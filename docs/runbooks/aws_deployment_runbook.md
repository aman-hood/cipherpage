# CipherPage AWS Deployment & Infrastructure Runbook

## 1. Architecture

CipherPage runs FastAPI and Next.js on AWS ECS behind an Application Load Balancer. Course assets remain in S3. Application records live in Neon PostgreSQL, and user authentication is provided by Firebase Authentication.

AWS does not host the application database or Firebase identity store. ECS tasks need outbound HTTPS access to Neon and Firebase. Database traffic must use TLS. Keep the Neon URL and Firebase Admin credentials in AWS Secrets Manager; only the backend and worker receive them. The frontend receives public Firebase client configuration at image build time.

The CloudFormation template provisions VPC, subnets, security groups, S3, ECS cluster, and ALB. Terraform provisions ECS and supporting AWS resources and references owner-managed Neon and Firebase secrets by Secrets Manager ARN.

## 2. Terraform prerequisites and validation

- Terraform 1.7 or newer is required by the state-safe removed blocks.
- AWS CLI credentials and account/region must be confirmed before planning.
- Supply non-production values in the local ignored tfvars file; the example contains placeholders.
- Configure the owner-managed Secrets Manager ARNs for DATABASE_URL and Firebase Admin credentials, and the Firebase project ID.
- Set exact HTTPS frontend origin(s) in allowed_origins; Terraform rejects an empty list or a non-HTTPS origin.

Run terraform fmt -check and terraform validate after initializing the required provider plugins. Review the complete plan, especially removed blocks and any legacy resources, before any apply. Never use an automatic approval flag.

## 3. Neon and Firebase configuration

Set the DATABASE_URL secret to the project owner’s Neon PostgreSQL connection URL. Select the pooled endpoint for the application runtime when required by Neon’s connection mode, retain TLS, and ensure the connection pool fits the Neon plan limits.

Set FIREBASE_SERVICE_ACCOUNT_JSON from a trusted backend-only identity or secret. Set FIREBASE_PROJECT_ID to the matching Firebase project. The backend validates Firebase ID tokens; a public Firebase API key is not a server-side trust credential.

Build the web image with NEXT_PUBLIC_API_URL and the owner-supplied NEXT_PUBLIC_FIREBASE_* client values. These are public browser configuration values and must not contain a service-account key or database credential.

## 4. Existing RDS resources

The application configuration no longer creates or uses RDS. Terraform removed blocks for the old database and related networking use destroy=false, so a normal apply detaches those old resources from Terraform state rather than deleting them. Existing AWS resources can therefore remain running but unmanaged.

Before retiring legacy RDS, export and verify any required data, confirm the Neon migration, and obtain a separately approved cloud change. Do not remove the removed blocks or delete the old database until retention, export, and recovery requirements are satisfied. No production apply or database migration is part of source verification.

## 5. Safe infrastructure changes

For a non-production infrastructure change:

1. Confirm the AWS account, region, Terraform workspace, and secret ARNs.
2. Validate formatting and provider configuration.
3. Generate and review a plan without applying it.
4. Verify no resource replacement, data destruction, or secret exposure is proposed.
5. Apply only after a separate authorized review.

Avoid terraform destroy for shared or production environments. The S3 assets bucket and other stateful resources require explicit backup and retention decisions before any teardown.

## 6. Recovery

Use Neon’s approved point-in-time recovery or branch restore procedure for database recovery. Validate the recovery target separately before directing application traffic to it. Do not use RDS restore commands for the application database.

ECS service rollback can use a previously approved task definition revision. Verify backend health, database connectivity, Firebase token verification, and frontend readiness in a non-production environment before promoting a release.
