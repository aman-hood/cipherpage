# CipherPage AWS Cloud Infrastructure & IaC Runbook
**SRS v2.2 Compliance: OPS-05, OPS-06, OPS-07, OPS-08, OPS-11, OPS-12, AC-08**

This runbook guides engineers and DevOps practitioners on deploying, validating, securing, and destroying cloud infrastructure for **CipherPage** using **Terraform** and **AWS CloudFormation**.

---

## 1. Architecture & Network Topology

CipherPage deploys a zero-trust multi-tier architecture on AWS:

```
                            [ Internet Client ]
                                     |
                                     v  (HTTP / HTTPS)
                    +----------------------------------+
                    |  Application Load Balancer (ALB) |
                    |      (Public Subnets 1 & 2)      |
                    +----------------+-----------------+
                                     |
                +--------------------+--------------------+
                |                                         |
                | (Path: /api/*, /health)                 | (Default: /*)
                v                                         v
   +--------------------------+              +--------------------------+
   |   FastAPI Backend Tasks  |              |   Next.js Frontend Tasks |
   |  (ECS Fargate - Priv. 1) |              |  (ECS Fargate - Priv. 2) |
   +------------+-------------+              +--------------------------+
                |
                +----------------------------+
                |                            |
                v (Port 5432)                v (S3 SDK)
   +--------------------------+  +--------------------------------------+
   |  RDS PostgreSQL 15 +     |  |   Encrypted S3 Course Assets Bucket  |
   |   pgvector Extension     |  |     (Server-side AES256, No Public)  |
   +--------------------------+  +--------------------------------------+
```

---

## 2. Infrastructure as Code Options

| Tool | Directory | Primary Use Case |
| :--- | :--- | :--- |
| **Terraform** | `infra/terraform/` | Modular, multi-cloud ready, declarative IaC for staging & production. |
| **CloudFormation** | `infra/cloudformation/` | Native AWS single-click repeatable stack deployment without state storage. |
| **Serverless Lambda**| `infra/serverless/` | Event-driven S3 media processing and pre-signed upload authorization. |

---

## 3. Terraform Staging Deployment Guide (OPS-05, OPS-11)

### Prerequisites
* AWS CLI v2 configured with valid credentials (`aws configure`)
* Terraform CLI (v1.5+)

### Step 1: Pre-Deployment Validation (AC-08)
Verify that your Terraform templates are structurally and syntactically sound without spending any cloud budget:
```bash
cd infra/terraform

# Format validation
terraform fmt -check

# Validate provider schema and configuration
terraform init -backend=false
terraform validate
```

### Step 2: Configure Environment Variables
Copy the sanitized template:
```bash
cp terraform.tfvars.example terraform.tfvars
```
Update `terraform.tfvars` with your environment parameters. For zero-cost staging, keep `enable_nat_gateway = false`.

### Step 3: Review Execution Plan
```bash
terraform plan -out=staging.tfplan
```
Inspect the proposed resources to ensure IAM permissions and network boundaries strictly match requirements.

### Step 4: Apply Changes
```bash
terraform apply staging.tfplan
```

### Outputs
Upon successful completion, Terraform displays:
* `alb_dns_name`: Public address for the web portal and API.
* `rds_endpoint`: PostgreSQL endpoint.
* `s3_course_assets_bucket`: Storage bucket name for lecture materials.

---

## 4. CloudFormation Alternative Deployment (OPS-06)

To deploy using AWS CloudFormation:
```bash
aws cloudformation deploy \
  --template-file infra/cloudformation/cipherpage-staging-stack.yaml \
  --stack-name cipherpage-staging \
  --parameter-overrides Environment=staging \
  --capabilities CAPABILITY_IAM
```

---

## 5. Security & IAM Least-Privilege Controls (OPS-07, SEC-06)

1. **No SSH into Production (`OPS-07`)**:
   Compute is deployed on **AWS ECS Fargate**, eliminating bastion hosts and open SSH port 22 vulnerabilities.
2. **Task Execution vs. Task Role Separation**:
   * `ecs-execution-role`: Limited exclusively to pulling container images from ECR and emitting CloudWatch logs.
   * `ecs-task-role`: Application container role granting least-privilege `s3:GetObject` and `s3:PutObject` permissions strictly scoped to `cipherpage-assets-*`.
3. **Network Boundary Isolation**:
   * RDS PostgreSQL is placed inside isolated database subnets with `publicly_accessible = false`.
   * Security groups allow port 5432 ingress **only** from the ECS Security Group.
4. **Encryption at Rest & In Transit**:
   * All S3 objects use AES256 server-side encryption with public access blocked.
   * Internal database connections enforce SSL.

---

## 6. Cost Control & Safe Resource Cleanup (OPS-11)

### AWS Budgets & Alarm Thresholds
Terraform automatically creates an `aws_budgets_budget` monitoring actual spending:
* **Monthly Cap**: \$15 USD.
* **Alert Trigger**: Sends email notification when actual spend crosses 80% (\$12 USD).

### Safe Shutdown & Destruction
To completely dismantle demo or staging resources and eliminate billable charges:
```bash
cd infra/terraform
terraform destroy -auto-approve
```
*Note: S3 buckets have `force_destroy = true` enabled in staging to facilitate frictionless teardown.*

---

## 7. Disaster Recovery & Rollback Procedures

### ECS Service Rollback
If a newly deployed container version fails health checks:
```bash
# Roll back ECS service to previous task revision
aws ecs update-service \
  --cluster cipherpage-staging-cluster \
  --service cipherpage-staging-backend-service \
  --task-definition cipherpage-staging-backend:<PREVIOUS_REVISION>
```

### RDS Point-In-Time Recovery
To recover from database corruption:
```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier cipherpage-staging-pg \
  --target-db-instance-identifier cipherpage-staging-pg-restored \
  --restore-time 2026-10-11T12:00:00Z
```
