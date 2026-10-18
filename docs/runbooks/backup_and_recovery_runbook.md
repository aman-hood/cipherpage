# CipherPage Backup, Disaster Recovery & Data Retention Runbook

## 1. Backup ownership

Neon PostgreSQL is the authoritative application database. Backup and point-in-time restore retention depend on the owner’s Neon plan and project settings. Confirm the configured retention in Neon before each production schema migration and record the available recovery point.

Redis is a cache and task broker; do not treat it as the system of record. Course assets remain in S3. Firebase Authentication owns authentication identities; Neon stores CipherPage profiles, roles, and application data.

## 2. Pre-migration backup and recovery

Before a production schema migration:

1. Confirm Neon’s automated backup and point-in-time restore settings for the production project.
2. Create a Neon restore branch or point-in-time recovery target according to the owner’s approved operations procedure.
3. If a logical export is required, use the project owner’s approved secret-manager-backed export procedure. Do not put DATABASE_URL in shell history, logs, screenshots, command arguments, or this repository.
4. Verify that the recovery target can be reached and that the export is readable before approving a migration.
5. Apply migrations only to the intended target after reviewing the generated SQL and the restore point.

Never use a destructive in-place restore as a routine rollback. Validate recovery in an isolated Neon branch first, compare schema and record counts, then follow the separately approved production recovery procedure.

## 3. Identity migration recovery

The Firebase identity migration preserves the existing integer user primary keys and application foreign keys. Firebase UID mappings are recorded in the versioned identity mapping table. Existing Supabase identifiers remain in the nullable legacy column until each account mapping is verified.

The identity import script is dry-run by default and requires explicit evidence fields before applying a mapping. Do not match accounts by email alone. Keep unresolved records in the legacy state and resolve them with the account owner. Do not delete legacy identity values until the project owner approves a separate retention and cleanup plan.

Firebase accounts cannot inherit Supabase passwords through this migration. Users must authenticate through Firebase using the approved reauthentication or password-reset flow.

## 4. Data retention and privacy deletion

Confirm the retention requirements for submissions, AI usage records, conversations, course progress, and account deletion with the product owner before implementing scheduled deletion. Account deletion must coordinate Firebase identity deletion, token revocation, and application-data retention; the current backend does not expose a deletion endpoint.

## 5. Disaster recovery validation drill

Run quarterly against an isolated Neon restore branch:

1. Restore to a separate branch or approved non-production target.
2. Compare important table counts, constraints, indexes, and vector data with the recorded backup baseline.
3. Run the isolated backend regression tests: python -m unittest discover -s tests -p 'test_phase4_regressions.py' and python -m unittest discover -s tests -p 'test_phase8_hardening.py'.
4. Record the recovery point, branch used, results, and gaps. Never point this drill at the production branch.
