# AWS Storage Architecture & Cloud Persistence (Phase 4)

> ⚠️ **EDUCATIONAL DISCLAIMER**
> **All calculations and estimations are simulation models created for educational purposes. They do not represent official AWS billing or performance metrics.**

---

## 1. Overview & Repository Pattern Architecture

Phase 4 introduces cloud persistence capability via **Amazon DynamoDB** and **Amazon S3** while preserving 100% local development functionality (`STORAGE_MODE=local`).

The Repository Selector Pattern decouples API controllers from underlying storage implementations.

```
                         GET /api/scenarios, POST /api/scenarios/{id}/simulate, etc.
                                                     │
                                                     ▼
                                        get_scenario_repository()
                                        get_history_repository()
                                                     │
                             ┌───────────────────────┴───────────────────────┐
                             │                                               │
             if STORAGE_MODE == 'local'                      if STORAGE_MODE == 'aws'
                             ▼                                               ▼
                  ScenarioRepository (SQLite)                   DynamoDBScenarioRepository
                   HistoryRepository (SQLite)                   DynamoDBHistoryRepository
```

---

## 2. Storage Mode Configuration

Controlled via environment variable `STORAGE_MODE` in `.env`:

| Setting | Mode | Database Provider | S3 Artifact Export | AWS Credentials |
|---|---|---|---|---|
| `STORAGE_MODE=local` *(default)* | Local Mode | SQLite (`simulator.db`) | Disabled | Not required |
| `STORAGE_MODE=aws` | AWS Mode | Amazon DynamoDB | Enabled (`simulations/...`) | Standard Boto3 Resolution |

---

## 3. DynamoDB Table Design

### A. Scenarios Table (`serverless-rightsizing-scenarios`)
- **Partition Key**: `scenario_id` (String)
- **Billing Mode**: `PAY_PER_REQUEST` (On-Demand)

| Attribute | Type | Description |
|---|---|---|
| `scenario_id` | String | Unique UUID identifier |
| `name` | String | Scenario title |
| `description` | String | Scenario description |
| `workload_type` | String | Low Traffic, Normal Traffic, High Traffic, Custom |
| `request_volume` | Number | Monthly request volume |
| `baseline_memory_mb` | Number | Baseline memory allocation in MB |
| `baseline_latency_ms` | Number | Baseline execution duration in ms |
| `cpu_utilization` | Number | Peak CPU load percentage (0–100) |
| `current_price` | Number | Rate $/GB-sec |
| `latency_target_ms` | Number | Maximum allowable latency (ms) |
| `availability_target_percent` | Number | Minimum allowable availability (%) |
| `created_at` | String | ISO 8601 creation timestamp |
| `updated_at` | String | ISO 8601 update timestamp |

---

### B. Simulation History Table (`serverless-rightsizing-history`)
- **Partition Key**: `history_id` (String)
- **Global Secondary Index**: `scenario_id-index` (HASH: `scenario_id`)
- **Billing Mode**: `PAY_PER_REQUEST` (On-Demand)

| Attribute | Type | Description |
|---|---|---|
| `history_id` | String | Unique simulation run UUID |
| `scenario_id` | String | Foreign reference scenario ID |
| `scenario_name` | String | Scenario name snapshot |
| `created_at` | String | ISO 8601 execution timestamp |
| `recommended_memory_mb` | Number | Recommended memory tier |
| `recommended_cost` | Number | Recommended monthly cost |
| `recommended_latency_ms` | Number | Recommended latency |
| `recommended_availability_percent` | Number | Recommended availability % |
| `savings_percent` | Number | Cost savings % |
| `status` | String | Recommended, Near Optimal, No Feasible Configuration |
| `full_simulation_json` | String | Serialized full simulation output |

---

## 4. S3 Artifact Storage Design

When `STORAGE_MODE=aws`, executing `POST /api/scenarios/{id}/simulate` automatically exports the full simulation JSON result to S3.

- **Bucket**: `serverless-rightsizing-artifacts`
- **Object Key Structure**: `simulations/{scenario_id}/{history_id}.json`
- **Content-Type**: `application/json`

---

## 5. Environment Variables (`.env`)

```ini
STORAGE_MODE=local
AWS_REGION=ap-south-1
SCENARIOS_TABLE=serverless-rightsizing-scenarios
HISTORY_TABLE=serverless-rightsizing-history
S3_BUCKET=serverless-rightsizing-artifacts
```

> **Security Rule**: AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) must NEVER be hardcoded or committed to git. Use standard AWS CLI or IAM role resolution.

---

## 6. SAM Infrastructure Resources (`infrastructure/template.yaml`)

Defines AWS CloudFormation / SAM resources:
1. `ScenariosTable` (DynamoDB Table)
2. `HistoryTable` (DynamoDB Table with `scenario_id-index` GSI)
3. `SimulationArtifactsBucket` (S3 Bucket with public access blocked)
4. `SimulatorAppRole` (Least privilege IAM policy for DynamoDB & S3 operations)

---

## 7. Data Migration Utility (`scripts/migrate_sqlite_to_dynamodb.py`)

Migrates local SQLite scenarios and history records to Amazon DynamoDB:

```bash
cd serverless-rightsizing-simulator/backend
py scripts/migrate_sqlite_to_dynamodb.py
```

Prints summary statistics:
```
Scenarios found: 3
Scenarios migrated: 3
History records found: 10
History records migrated: 10
```

---

## 8. Local Development Without AWS

Local development (`STORAGE_MODE=local`) runs entirely without AWS credentials, an AWS account, or internet connectivity. All persistent data is managed automatically via SQLite (`simulator.db`).
