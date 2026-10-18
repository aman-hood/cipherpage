# Neon PostgreSQL and Firebase Authentication Migration

## Runtime architecture

- Next.js web and Flutter clients authenticate with Firebase Authentication.
- Clients send Firebase ID tokens as bearer tokens to FastAPI.
- FastAPI verifies ID tokens with Firebase Admin, requires a verified email, and derives identity only from the verified Firebase UID.
- FastAPI and Celery connect to Neon PostgreSQL through SQLAlchemy. PostgreSQL and pgvector remain the database engine and vector extension.
- The web and mobile Firebase configuration values are public client configuration. Firebase Admin credentials and the Neon URL are backend-only secrets.

## Required environment values

Backend, in backend/.env or the deployment secret manager:

- DATABASE_URL: the exact Neon PostgreSQL URL supplied by the project owner. Use the pooled endpoint for the web and worker runtime where the supplied Neon configuration calls for pooling. Keep TLS enabled.
- MIGRATION_DATABASE_URL: optional separate owner-managed Neon URL for Alembic DDL operations. Give the runtime DATABASE_URL role only the privileges needed by the application; never inject the migration URL into backend or worker tasks.
- ALLOWED_ORIGINS: comma-separated, exact HTTPS frontend origins for staging and production. Remote settings reject localhost, wildcard, and non-HTTPS origins.
- FIREBASE_PROJECT_ID: the owner’s Firebase project ID.
- FIREBASE_SERVICE_ACCOUNT_JSON: optional backend-only service-account JSON when Application Default Credentials are not available. Prefer the deployment identity or secret manager where supported.
- FIREBASE_CHECK_REVOKED: defaults to true; leave token revocation checks enabled unless the security owner approves a documented exception.
- DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT, DB_POOL_RECYCLE, and DB_CONNECT_TIMEOUT: tune only after checking Neon connection limits and application concurrency.
- Existing Redis, AI-provider, and payment variables remain necessary only for the corresponding enabled application features.

Web, in web/.env and as build-time variables for a production bundle:

- NEXT_PUBLIC_API_URL
- NEXT_PUBLIC_FIREBASE_API_KEY
- NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
- NEXT_PUBLIC_FIREBASE_PROJECT_ID
- NEXT_PUBLIC_FIREBASE_APP_ID
- NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID and NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET when supplied by the Firebase project

Mobile, in mobile/.env:

- API_BASE_URL
- FIREBASE_API_KEY, FIREBASE_AUTH_DOMAIN, FIREBASE_PROJECT_ID, FIREBASE_APP_ID, FIREBASE_MESSAGING_SENDER_ID, and FIREBASE_STORAGE_BUCKET
- GOOGLE_SIGN_IN_CLIENT_ID and GOOGLE_SIGN_IN_SERVER_CLIENT_ID for the configured Google sign-in platform flow

All examples contain empty placeholders. Never commit local .env files, Neon URLs, Firebase Admin credentials, or service-account key files. Public Firebase client values must still be provided by the project owner; do not guess a Firebase project.

## Schema and identity migration

The new Alembic migration is forward-only for safety. It keeps users.id and all existing application foreign keys, renames the old provider identifier to nullable legacy_auth_uid, adds a unique nullable firebase_uid, and creates an identity_mappings audit table. No profile, role, course, enrollment, progress, submission, or document row is discarded.

The existing Supabase-auth Alembic revision is retained as historical migration history because deployed databases may have it recorded. The new forward migration consumes its column and preserves the legacy value. This historical revision is not an active Supabase runtime dependency.

Do not auto-link users by email. Build an operator-reviewed CSV that maps each `legacy_auth_uid` to a Firebase UID only after the owner has verified account control through an approved process. The import script requires verification method, reviewer, and evidence reference; it is dry-run by default, checks that the Firebase account exists, is enabled, and has a verified email, and does not require Neon credentials for CSV-only validation. Unmapped users and their data remain intact for manual resolution. Duplicate Firebase UID mappings or conflicting profiles must stop the import and be investigated.

Run the Alembic migration only after a verified backup or Neon restore point exists and the SQL has been reviewed on a non-production branch. Run the identity import only after Firebase accounts exist and ownership evidence has been reviewed. The import does not create Firebase accounts or transfer passwords.

Supabase passwords are not automatically portable. Users must reauthenticate through a trusted account recovery or password reset process. Do not claim ownership based only on an email match, and do not remove legacy mapping values until an explicit retention decision is approved.

## Legacy database provider retirement

Local Docker Compose no longer creates a PostgreSQL server or persistent database volume. Terraform no longer declares an AWS RDS PostgreSQL instance. Terraform removed blocks use destroy=false so a Terraform apply detaches the previous RDS resources from state instead of destroying them. This leaves any existing RDS resources in AWS unmanaged; export and verify their data, then decommission separately through an approved cloud change.

CloudFormation in this repository provisions networking, ECS, ALB, and S3 only; it does not create an RDS database. Do not perform a CloudFormation or Terraform production apply as part of code verification.

The Terraform ECS task reads DATABASE_URL and FIREBASE_SERVICE_ACCOUNT_JSON from owner-provided Secrets Manager ARNs. The frontend receives only public Firebase client configuration at image build time. Keep database credentials and Admin credentials out of frontend builds.

## Verification status and remaining prerequisites

Source-level tests mock Firebase and the database; they do not prove connectivity. Do not report Neon or Firebase connectivity as verified until the owner supplies project configuration and an authorized non-production smoke test succeeds.

Before deploying:

1. Supply a Neon URL and confirm pooled/direct connection selection, TLS, and connection limits.
2. Supply the Firebase project ID and web/mobile client configuration; enable the required Firebase sign-in providers.
3. Configure Firebase Admin through a trusted runtime identity or a backend-only secret.
4. Configure Google OAuth client IDs, authorized domains, Android signing fingerprints, and iOS URL schemes for the supported clients.
5. Create non-production CI credentials and build-time NEXT_PUBLIC variables.
6. Back up Neon, review the Alembic SQL, apply schema changes in staging, verify user/profile mappings, then schedule production migration and recovery.
7. Export and verify any legacy RDS data before separately decommissioning the now-unmanaged RDS resources.
8. Set the exact HTTPS ALLOWED_ORIGINS value for each remote backend deployment.
