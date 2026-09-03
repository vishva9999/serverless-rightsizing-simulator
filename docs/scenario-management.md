# Scenario Management & Simulation History — Technical Specification

## 1. Overview

Phase 3 introduces persistent scenario management, execution history tracking, and side-by-side simulation comparison. This elevates the application from a one-off calculator to an interactive simulation workbench product.

---

## 2. Architecture & Repository Pattern

Storage operations are abstracted behind dedicated repository interfaces (`ScenarioRepository`, `HistoryRepository`). In Phase 3, these repositories store data in a local **SQLite database** (`simulator.db`).

### Future DynamoDB Migration Path (Phase 4 Target)
Because the database access layer is decoupled behind repository classes, migrating to AWS DynamoDB in Phase 4 requires only swapping the repository implementation without altering FastAPI routers, models, or simulation services.

```
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI Routers                       │
│    (/api/scenarios, /api/scenarios/{id}/simulate, /api/history) │
└──────────────────────────────┬──────────────────────────────┘
                               │ Calls methods on
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     Repository Layer                        │
│         ScenarioRepository   │   HistoryRepository          │
└──────────────────────────────┬──────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼ (Phase 3)                     ▼ (Phase 4 Target)
┌──────────────────────────────┐ ┌─────────────────────────────┐
│  SQLite Database             │ │  AWS DynamoDB               │
│  (simulator.db)              │ │  - Scenarios Table          │
│  - scenarios                 │ │  - SimulationHistory Table  │
│  - simulation_history        │ │                             │
└──────────────────────────────┘ └─────────────────────────────┘
```

---

## 3. Data Schemas

### Scenario Table Schema (`scenarios`)

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | TEXT | PRIMARY KEY | Unique UUID identifier |
| `name` | TEXT | NOT NULL | Scenario title |
| `description` | TEXT | | Scenario description / notes |
| `workload_type` | TEXT | NOT NULL | Low Traffic, Normal Traffic, High Traffic, Custom |
| `request_volume` | INTEGER | NOT NULL (ge=0) | Monthly invocation volume |
| `baseline_memory_mb` | REAL | NOT NULL (gt=0) | Baseline allocated memory in MB |
| `baseline_latency_ms` | REAL | NOT NULL (gt=0) | Baseline latency in ms |
| `cpu_utilization` | REAL | NOT NULL (0–100) | Peak CPU load percentage |
| `current_price` | REAL | NOT NULL (ge=0) | Compute rate $/GB-sec |
| `latency_target_ms` | REAL | NOT NULL (gt=0) | Maximum allowed latency target (ms) |
| `availability_target_percent` | REAL | NOT NULL (90–100) | Minimum allowed availability target (%) |
| `created_at` | TEXT | NOT NULL | ISO 8601 creation timestamp |
| `updated_at` | TEXT | NOT NULL | ISO 8601 update timestamp |

---

### Simulation History Table Schema (`simulation_history`)

| Column | Type | Description |
|---|---|---|
| `id` | TEXT PRIMARY KEY | Unique simulation run ID |
| `scenario_id` | TEXT NOT NULL | Foreign reference to scenario ID |
| `scenario_name` | TEXT NOT NULL | Scenario name snapshot |
| `created_at` | TEXT NOT NULL | Execution ISO timestamp |
| `recommended_memory_mb` | REAL | Recommended memory tier |
| `recommended_cost` | REAL | Recommended monthly cost |
| `recommended_latency_ms` | REAL | Recommended latency |
| `recommended_availability_percent` | REAL | Recommended availability % |
| `savings_percent` | REAL | Cost savings % |
| `status` | TEXT NOT NULL | Recommended, Near Optimal, No Feasible Configuration |
| `full_simulation_json` | TEXT NOT NULL | Complete serialized JSON simulation output |

---

## 4. API Endpoints

### Scenario CRUD

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/scenarios` | Create a new scenario |
| `GET` | `/api/scenarios` | List all scenarios |
| `GET` | `/api/scenarios/{id}` | Get single scenario by ID |
| `PUT` | `/api/scenarios/{id}` | Update scenario parameters |
| `DELETE` | `/api/scenarios/{id}` | Delete scenario by ID |

### Simulation Execution

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/scenarios/{id}/simulate` | Executes existing Phase 2 simulation engine for scenario, saves output to history, and returns result |

### Simulation History & Comparison

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/history` | List history runs (optional `?scenario_id=` query filter) |
| `GET` | `/api/history/{id}` | Get full history run detail with full JSON simulation output |
| `DELETE` | `/api/history/{id}` | Delete history record |
| `GET` | `/api/history/compare/{id1}/{id2}` | Side-by-side run comparison of two historical runs |

---

## 5. Preset Scenarios

When initialized, the database seeds 3 default preset scenarios if empty:
1. **Low Traffic**: Off-peak night workload (100k req/mo, 20% CPU, 110ms latency).
2. **Normal Traffic**: Standard business workload (2M req/mo, 65% CPU, 150ms latency).
3. **High Traffic**: Peak traffic surge (8M req/mo, 90% CPU, 220ms latency).

---

## 6. Simulation Workflow

```
Dashboard View
  │
  ├──► Create Scenario Modal  ──► Save to DB (POST /api/scenarios)
  │
  ├──► Open Scenario View      ──► Display parameters & "Run Simulation" button
  │                                    │
  │                                    ▼
  │                           POST /api/scenarios/{id}/simulate
  │                                    │
  │                                    ├─► Runs simulation_engine.py
  │                                    ├─► Saves run to simulation_history DB
  │                                    └─► Renders recommendation, table & Recharts
  │
  └──► Simulation History      ──► List past runs (GET /api/history)
        │                              │
        └─► Select 2 Runs              └─► Compare Side-by-Side (GET /api/history/compare/{id1}/{id2})
```

---

## 7. Educational Disclaimer

> **Simulation Estimate**: All cost, latency, and availability values are derived from mathematical simulation models for learning and demonstration purposes. They do not represent official AWS billing or performance metrics.
