# CipherPage Backup, Disaster Recovery & Data Retention Runbook
**SRS v2.2 Compliance: NFR-04, SEC-08, SEC-09**

This runbook guides operations teams on scheduled backups, point-in-time database restoration, disaster recovery drills, and regulatory data retention / purging policies for **CipherPage**.

---

## 1. Backup Architecture & Cadence

CipherPage maintains multi-layered backups across database state, queue persistence, and media storage:

| Component | Target Storage | Backup Type | Frequency | Retention Period |
| :--- | :--- | :--- | :--- | :--- |
| **PostgreSQL 15 (DB)** | Encrypted S3 / EBS | `pg_dump` Logical + WAL Archive | Hourly WAL / Daily Dump | 30 Days (Production) |
| **Redis Cache** | EBS Volume | RDB Snapshot + AOF | Every 6 Hours | 7 Days |
| **Course Assets (S3)** | S3 Multi-AZ | S3 Versioning & Replication | Continuous Versioning | Indefinite (Course Notes) |
| **CloudWatch Logs** | CloudWatch Logs | Log Stream Export | Continuous | 14 Days (Staging) / 90 Days (Prod) |

---

## 2. Automated PostgreSQL Backup Procedures (NFR-04)

### Manual Snapshot (Prior to Deployments or Migrations)
To generate an immediate database backup before applying schema changes:
```bash
docker exec cipherpage-db pg_dump \
  -U cipheruser \
  -d cipherpagedb \
  -F c \
  -b \
  -v \
  -f /var/lib/postgresql/data/cipherpage_pre_migration_$(date +%Y%m%d_%H%M%S).dump
```

### Complete Database Restoration
To restore a logical dump file into PostgreSQL:
```bash
# 1. Terminate existing client connections
docker exec -i cipherpage-db psql -U cipheruser -d postgres -c "
  SELECT pg_terminate_backend(pid) 
  FROM pg_stat_activity 
  WHERE datname = 'cipherpagedb' AND pid <> pg_backend_pid();
"

# 2. Re-create clean database
docker exec -i cipherpage-db psql -U cipheruser -d postgres -c "DROP DATABASE cipherpagedb;"
docker exec -i cipherpage-db psql -U cipheruser -d postgres -c "CREATE DATABASE cipherpagedb OWNER cipheruser;"

# 3. Restore dump archive
docker exec -i cipherpage-db pg_restore \
  -U cipheruser \
  -d cipherpagedb \
  -v \
  /var/lib/postgresql/data/<BACKUP_FILE>.dump
```

---

## 3. Data Retention & Privacy Deletion Policies (SEC-08)

To comply with data privacy standards and reduce storage overhead:

### 1. Ephemeral Submissions & Code Outputs
* Raw runner standard output and execution logs are archived for **90 days**.
* Aggregated metrics (`verdict`, `score`, `language`, `execution_time_ms`) are retained indefinitely for learner transcripts.

### 2. GenAI Mentor Conversations & Usage Records
* `ai_usage_records` are retained for **180 days** for quota tracking and cost auditing.
* Conversation prompt strings older than **90 days** are purged via scheduled job.

### 3. Student Account Deletion Requests
When an authorized user requests account deletion (`DELETE /api/v1/auth/me`):
* User record email and personal details are pseudonymized.
* Auth sessions and tokens are immediately revoked.
* Course progress and certifications are anonymized.

---

## 4. Disaster Recovery Validation Drill (NFR-04)

Run this quarterly recovery validation drill in an isolated staging environment:
1. Spin up ephemeral PostgreSQL and Redis instances.
2. Restore the latest daily dump.
3. Validate vector embeddings: `SELECT count(*) FROM document_chunks WHERE embedding IS NOT NULL;`.
4. Run backend automated verification suite: `python -m unittest discover -s tests`.
5. Verify that all 29 unit and integration tests pass without error.
