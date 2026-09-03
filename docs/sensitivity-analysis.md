# Sensitivity Analysis Methodology & Architecture (Phase 5)

> ⚠️ **EDUCATIONAL DISCLAIMER**
> **All calculations and estimations are simulation models created for educational purposes. They do not represent official AWS billing or performance metrics.**

---

## 1. Overview & Purpose

**Phase 5** introduces interactive **Sensitivity Analysis** to the Serverless Cost & Performance Rightsizing Simulator.

Sensitivity analysis enables engineering teams and students to explore how rightsizing recommendations respond when core workload parameters and target SLOs change:

- *"How does our recommended memory tier scale if request volume doubles?"*
- *"Will our serverless function violate its latency SLO if CPU load increases from 40% to 75%?"*
- *"How sensitive is our monthly cost to AWS pricing changes?"*

---

## 2. Supported Sensitivity Variables

| Key | Label | Unit | Valid Range | Scenario Field |
|---|---|---|---|---|
| `request_volume` | Request Volume | requests/month | $\ge 0$ | `request_volume` |
| `cpu_utilization` | CPU Utilization | % | $0 - 100\%$ | `cpu_utilization` |
| `baseline_latency_ms` | Baseline Latency | ms | $> 0$ | `baseline_latency_ms` |
| `latency_target_ms` | Latency Target SLO | ms | $> 0$ | `latency_target_ms` |
| `availability_target_percent` | Availability Target SLO | % | $90.0 - 100.0\%$ | `availability_target_percent` |
| `current_price` | Pricing Rate | $/GB-sec | $\ge 0$ | `current_price` |

---

## 3. Sensitivity Engine Workflow

To guarantee mathematical consistency and prevent logic drift, the **Sensitivity Engine (`backend/app/services/sensitivity_engine.py`)** does **NOT** duplicate any rightsizing formulas.

Instead, it reuses the existing Phase 2 **Simulation Engine (`run_simulation`)** as the single source of truth:

```
                            User Selects Scenario + Variable + Values
                                               │
                                               ▼
                              POST /api/sensitivity/analyze
                                               │
                                               ▼
                                  Load Scenario Data (SQLite/DynamoDB)
                                               │
               ┌───────────────────────────────┴───────────────────────────────┐
               │  Iterate over each test point (value_1, value_2, ..., value_N) │
               └───────────────────────────────┬───────────────────────────────┘
                                               │
                                               ▼
                            Copy scenario params & overwrite target variable
                                               │
                                               ▼
                            Construct SimulationRequest(params)
                                               │
                                               ▼
                            Invoke EXISTING run_simulation(sim_req)
                                               │
                                               ▼
                                Record SensitivityPoint Result
                                               │
                                               ▼
                             Generate Automated Insight Summary
```

---

## 4. API Specification

### A. List Variables: `GET /api/sensitivity/variables`
Returns metadata for all supported variables.

### B. Run Analysis: `POST /api/sensitivity/analyze`
**Request Payload**:
```json
{
  "scenario_id": "preset-normal-traffic",
  "variable": "request_volume",
  "values": [500000, 1000000, 2000000, 3000000, 5000000]
}
```

**Response Payload**:
```json
{
  "scenario_id": "preset-normal-traffic",
  "scenario_name": "Normal Traffic Profile",
  "variable": "request_volume",
  "variable_label": "Request Volume",
  "baseline_value": 2000000,
  "points": [
    {
      "input_value": 500000,
      "recommended_memory_mb": 512.0,
      "recommended_cost": 2.85,
      "recommended_latency_ms": 172.5,
      "recommended_availability_percent": 99.95,
      "savings_percent": 43.0,
      "simulation_status": "Recommended"
    }
  ],
  "insight_summary": "Varying Request Volume causes the recommended memory configuration to shift from 512 MB to 1024 MB.",
  "disclaimer": "Simulation Estimate: Sensitivity analysis results are educational models and not guaranteed AWS performance or cost metrics."
}
```

---

## 5. Input Validation Rules

The API enforces strict validation rules and returns HTTP 400/404 errors:
1. **Scenario Existence**: Returns `404 Not Found` if `scenario_id` does not exist.
2. **Variable Support**: Returns `400 Bad Request` if `variable` key is unsupported.
3. **Point Count**: Enforces $1 \le \text{points} \le 20$.
4. **Numeric Ranges**: Validates min/max bounds (e.g. CPU $\in [0, 100]$, latency $> 0$, availability $\in [90, 100]$).

---

## 6. Frontend Visualizations & Features

The **Sensitivity Analysis page (`src/pages/Sensitivity.jsx`)** provides:
1. **Scenario & Variable Selectors**: Populated dynamically from API endpoints.
2. **Preset Value Chips**: Convenient preset points (-50%, -25%, Baseline, +25%, +50%) and custom input tag editor.
3. **3 Interactive Recharts**:
   - **Recommended Memory (MB)** vs Variable (Bar Chart)
   - **Estimated Monthly Cost ($)** vs Variable (Line Chart)
   - **Estimated Latency (ms)** vs Variable (Line Chart)
4. **Results Table**: Displays all evaluated points with the **BASELINE** row highlighted.
5. **Insight Summary Banner**: Highlights executive conclusions generated by the backend.
