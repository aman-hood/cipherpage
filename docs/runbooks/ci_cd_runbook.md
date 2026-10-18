# CipherPage CI/CD & Docker Operations Runbook
**SRS v2.2 Compliance: OPS-01, OPS-02, OPS-03, OPS-04, OPS-10, AC-06, AC-07, SEC-06**

This runbook guides engineers and DevOps practitioners on configuring, executing, and troubleshooting the containerized delivery lifecycle for **CipherPage**.

---

## 1. Architecture Overview

CipherPage utilizes a multi-stage Docker strategy and a declarative Jenkins CI/CD pipeline ensuring zero secrets in version control, non-root isolated runtimes, automated vulnerability scanning, and immutable image tagging.

```
       +--------------------+
       |  Developer Push    |
       +---------+----------+
                 |
                 v
       +--------------------+
       |   GitHub Webhook   |
       +---------+----------+
                 |
                 v
+-----------------------------------------------------------+
|             Jenkins Declarative Pipeline                  |
|                                                           |
| 1. Secret & Leak Detection (git diff & entropy check)     |
| 2. Static Code Analysis (Python compileall, Next.js lint) |
| 3. Type Checking & Dependency Audit (tsc, npm audit)      |
| 4. Isolated Backend Regression Tests                     |
| 5. Multi-Stage Docker Builds (Target: production/runner)  |
| 6. Container Vulnerability Scan (Trivy CVE inspection)    |
| 7. Staging Smoke Test & Health Check (/health probe)      |
| 8. Immutable Release Tagging (${BUILD_NUMBER}-${COMMIT})  |
+-----------------------------------------------------------+
                 |
                 v
       +--------------------+
       |  Docker Registry   |
       +--------------------+
```

---

## 2. Local Docker Workflow (OPS-01)

### Development Environment (With Live Reloading)
To run the full stack locally with hot reloading enabled for both FastAPI and Next.js:
```bash
# Set backend/.env and web/.env from their sanitized examples first.
# DATABASE_URL must contain the owner-provided Neon PostgreSQL URL.
# Start the application services (Redis, backend, worker, frontend).
docker compose up -d

# View real-time aggregated logs
docker compose logs -f

# Verify service health status
docker compose ps
```

### Production Stack Emulation (docker-compose.prod.yml)
To test the hardened production environment locally:
```bash
# Build and run the multi-stage production images
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Verify health probes
curl http://localhost:8000/health
curl -I http://localhost:3000
```

---

## 3. Jenkins Controller Setup (OPS-02)

CipherPage includes an out-of-the-box Dockerized Jenkins controller preloaded with Docker CLI and Trivy security scanner:

```bash
# Spin up the local Jenkins controller
docker compose -f deploy/docker/docker-compose.jenkins.yml up -d

# Retrieve initial admin unlock key
docker exec cipherpage-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Open your browser to `http://localhost:8080` to complete the initial setup wizard and install the recommended plugins.

---

## 4. GitHub Webhook Configuration (OPS-03)

To trigger automated pipeline execution on every pull request and push to `main`:

1. In your GitHub repository, navigate to **Settings > Webhooks > Add webhook**.
2. **Payload URL**: `https://<YOUR_JENKINS_HOST>/github-webhook/`
3. **Content type**: `application/json`
4. **Secret**: Generate a high-entropy secret (e.g. `openssl rand -hex 24`) and paste it here.
5. **Which events would you like to trigger this webhook?**:
   - Select **Let me select individual events**:
     - [x] **Pushes**
     - [x] **Pull requests**
6. Click **Add webhook**.

---

## 5. Branch Protection Rules (OPS-03)

Ensure that unverified code cannot be merged into `main`:

1. Go to **Settings > Branches > Add branch protection rule**.
2. **Branch name pattern**: `main`
3. Check the following enforcement criteria:
   - [x] **Require a pull request before merging**
   - [x] **Require status checks to pass before merging**
     - Select: `continuous-integration/jenkins/branch`
   - [x] **Require branches to be up to date before merging**
   - [x] **Do not allow bypassing the above settings** (applies to administrators).

---

## 6. Jenkins Credentials Management (OPS-03, SEC-03)

Configure least-privilege credentials in **Jenkins > Manage Jenkins > Credentials > System > Global credentials**:

| Credential ID | Type | Description |
| :--- | :--- | :--- |
| `DOCKER_REGISTRY_CREDENTIALS` | Username with password | Registry robot account for pushing release images |
| `GIT_CREDENTIALS` | SSH Username with private key | Deploy key for cloning protected submodules |
| cipherpage-neon-test-url | Secret text | Dedicated non-production Neon URL used only to satisfy backend test configuration; tests must not connect to it |
| cipherpage-staging-backend-env-file | Secret file | Backend-only staging environment file used by the local Compose smoke stage; contains the staging Neon URL and Firebase Admin configuration |
| FIREBASE_PROJECT_ID | Jenkins environment value | Firebase project identifier used by backend token verification |
| NEXT_PUBLIC_API_URL | Jenkins environment value | Public backend API URL baked into the web bundle |
| NEXT_PUBLIC_FIREBASE_* | Jenkins environment values | Public Firebase web app configuration baked into the web bundle |

Do not use a production Neon URL for CI. The isolated unit tests mock database and Firebase calls; the DATABASE_URL credential is present only because backend settings require it at import time. Do not run live-service integration tests against production from CI.
The staging backend environment file must include the staging Neon URL, Firebase Admin configuration, Firebase project ID, and exact HTTPS ALLOWED_ORIGINS for the staging frontend.

---

## 7. Container Vulnerability Scanning & Release Tagging (OPS-04, OPS-10)

### Immutable Tagging Convention
Every image built in CI is labeled with an immutable tag:
```
cipherpage-backend:${BUILD_NUMBER}-${GIT_COMMIT_SHORT}
cipherpage-web:${BUILD_NUMBER}-${GIT_COMMIT_SHORT}
```
*Never overwrite tags in production.* The `latest` tag is updated simultaneously as a rolling pointer.

### Vulnerability Gates with Trivy
The pipeline enforces automatic CVE scanning:
```bash
trivy image --severity HIGH,CRITICAL --exit-code 0 <image_name>:<tag>
```
To fail the build on any critical vulnerability, update `--exit-code 1`.

---

## 8. Rollback Procedures

If an incident occurs in staging or production:

1. Identify the previous stable immutable tag (e.g., `42-a1b2c3d`).
2. Trigger the deployment pipeline with parameterized input:
   ```bash
   IMAGE_TAG=42-a1b2c3d docker compose -f docker-compose.prod.yml up -d
   ```
3. Run post-rollback health checks:
   ```bash
   curl -f http://localhost:8000/health
   ```
