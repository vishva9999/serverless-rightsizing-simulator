# Amazon CloudWatch Observability & Logging

## 1. Overview
Amazon CloudWatch provides centralized telemetry, structured logging, error monitoring, and performance metrics for the Serverless Rightsizing Simulator in AWS.

---

## 2. CloudWatch Logs Configuration
- **Log Group**: `/aws/lambda/serverless-rightsizing-simulator-api-prod`
- **Retention Period**: `30 days` (balances compliance and cost efficiency).
- **Sensitive Data Safeguards**:
  - Passwords and password hashes are **never** logged.
  - JWT access/refresh tokens are **never** logged.
  - AWS access keys or secret session headers are **never** logged.

---

## 3. Serverless Metrics Monitored

| Metric | Source | Unit | Description |
|---|---|---|---|
| `Invocations` | AWS Lambda | Count | Total requests processed by FastAPI backend |
| `Duration` | AWS Lambda | Milliseconds | Execution duration per API call |
| `Errors` | AWS Lambda | Count | Unhandled exceptions and function crashes |
| `Throttles` | AWS Lambda | Count | Concurrency limit throttling |
| `4XXError` | API Gateway | Count | Client errors (401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Validation) |
| `5XXError` | API Gateway | Count | Server-side execution errors |
| `Latency` | API Gateway | Milliseconds | End-to-end client round-trip latency |

---

## 4. Application-Level Structured Logging
FastAPI utilizes standard Python `logging` streams formatted for automated CloudWatch ingestion:
- Request method, route path, status code, and latency are captured automatically by Uvicorn / Mangum.
- Audit events (user registration, scenario execution, role changes) are emitted with timestamps.
