# CipherPage Observability & Monitoring Runbook
**SRS v2.2 Compliance: OPS-09, NFR-04, NFR-06, AC-09**

This runbook guides engineers and site reliability engineers (SREs) on operating, querying, and diagnosing the **Prometheus** and **Grafana** observability stack for CipherPage.

---

## 1. Observability Architecture

```
                                  [ Scrape: /metrics ]
  +--------------------------+  <---------------------+  +------------------------+
  |    CipherPage FastAPI    |                        |  |       Prometheus       |
  |     Backend (:8000)      |  --------------------->+  |         (:9090)        |
  +--------------------------+     (Exposition Text)     +-----------+------------+
               |                                                     |
               v (Health Probe)                                      v (PromQL)
  +--------------------------+                           +------------------------+
  |  PostgreSQL & Redis DBs  |                           |        Grafana         |
  |  (Database Status Gauge) |                           |  Dashboards & Alerts   |
  +--------------------------+                           |         (:3001)        |
                                                         +------------------------+
```

---

## 2. Quickstart: Launching the Monitoring Stack (OPS-09)

Ensure the core CipherPage stack is active (`docker compose up -d`), then spin up Prometheus and Grafana:

```bash
docker compose -f deploy/docker/docker-compose.monitoring.yml up -d
```

### Accessing UIs
* **Prometheus Targets & Expression Browser**: `http://localhost:9090`
  * Verify target health: Visit `http://localhost:9090/targets` (Status must be `UP`).
* **Grafana Dashboards**: `http://localhost:3001`
  * Default Credentials: Username `admin`, Password `cipheradmin`.
  * Pre-loaded Dashboard: **CipherPage - Platform Observability Dashboard**.

---

## 3. Metrics Dictionary (NFR-06, AC-09)

All metrics are exposed in standard Prometheus format on `/metrics` with zero leakage of database credentials, learner source code, or cloud secrets.

| Metric Name | Type | Description | Labels |
| :--- | :--- | :--- | :--- |
| `cipherpage_http_requests_total` | Counter | Total volume of HTTP requests | `method`, `endpoint`, `status_code` |
| `cipherpage_http_request_duration_seconds` | Histogram | Latency distribution across percentiles | `method`, `endpoint` |
| `cipherpage_active_requests` | Gauge | Number of requests currently executing | None |
| `cipherpage_code_submissions_total` | Counter | Code submissions processed by runner | `language`, `verdict` |
| `cipherpage_runner_execution_duration_seconds`| Histogram | Runtime duration inside runner sandbox | `language` |
| `cipherpage_ai_mentor_requests_total` | Counter | Invocations of GenAI Coding Mentor | `mode`, `status` |
| `cipherpage_rag_queries_total` | Counter | Invocations of RAG Learning Assistant | `course_id`, `sources_found` |
| `cipherpage_database_health_status` | Gauge | PostgreSQL pool availability (1/0) | None |
| `cipherpage_redis_health_status` | Gauge | Redis queue availability (1/0) | None |

---

## 4. Useful PromQL Queries

### Current Traffic Throughput (Requests per Second)
```promql
sum(rate(cipherpage_http_requests_total[1m]))
```

### 95th Percentile Latency across Endpoints (Seconds)
```promql
histogram_quantile(0.95, sum(rate(cipherpage_http_request_duration_seconds_bucket[5m])) by (le))
```

### HTTP 5xx Error Percentage
```promql
(sum(rate(cipherpage_http_requests_total{status_code=~"5.."}[5m])) / sum(rate(cipherpage_http_requests_total[5m]))) * 100
```

### Isolated Runner Verdict Distribution
```promql
sum by (verdict) (rate(cipherpage_code_submissions_total[5m]))
```

---

## 5. Automated Alerting Rules & Triage Runbook (OPS-09)

Alerts are defined in `monitoring/prometheus/alert.rules.yml`:

### 1. `CipherPageHighErrorRate` (Critical)
* **Condition**: > 5% of HTTP requests return 5xx errors over 5 minutes.
* **Triage**:
  1. Inspect backend logs: `docker compose logs -f backend`.
  2. Query `/health` endpoint to verify if database pool or Redis queue connection dropped.
  3. Check recent code releases or Celery worker capacity.

### 2. `CipherPageHighLatency` (Warning)
* **Condition**: p95 API response time exceeds 1.5 seconds.
* **Triage**:
  1. Check endpoint breakdown in Grafana to isolate the offending route.
  2. If `/api/v1/ai/*` or `/api/v1/submissions/*` is slow, check LLM provider quotas and runner process contention.
  3. Check PostgreSQL connection pool saturation and index health on `challenges` / `submissions`.

### 3. `CipherPageDatabaseDegraded` (Critical)
* **Condition**: `cipherpage_database_health_status == 0`.
* **Triage**:
  1. Verify PostgreSQL container status: `docker ps | grep cipherpage-db`.
  2. Inspect database logs: `docker logs cipherpage-db`.
  3. Ensure disk storage volume has not run out of capacity.
