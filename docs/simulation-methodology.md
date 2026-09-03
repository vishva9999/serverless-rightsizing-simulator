# Simulation Methodology — Serverless Rightsizing Engine

> ⚠️ **EDUCATIONAL DISCLAIMER**
> **This is an educational simulation model and not an official AWS pricing or performance model.**

---

## 1. Purpose

The objective of the Rightsizing Simulation Engine is to evaluate how allocating different memory resource tiers to a serverless function impacts estimated monthly cost, latency, and service availability. 

By systematically testing candidate memory configurations against user-defined Service Level Objectives (SLOs) for latency and availability, the engine identifies the most cost-effective configuration that satisfies all operational constraints.

---

## 2. Inputs

The simulation accepts a `SimulationRequest` object containing:

| Input Parameter | Validation Constraints | Description |
|---|---|---|
| `scenario_name` | String | Identifier for the workload scenario |
| `cpu_utilization` | $0.0 \le C \le 100.0$ (%) | Average CPU load during peak execution |
| `memory_mb` | $M_0 > 0.0$ (MB) | Baseline allocated memory |
| `baseline_latency_ms` | $L_0 > 0.0$ (ms) | Baseline p95 execution duration |
| `request_volume` | $V \ge 0$ (requests/mo) | Monthly invocation volume |
| `current_price` | $P \ge 0.0$ ($/GB-sec) | Price per GB-second compute |
| `latency_target_ms` | $L_{\text{target}} > 0.0$ (ms) | Maximum allowable p95 latency |
| `availability_target` | $90.0 \le A_{\text{target}} \le 100.0$ (%) | Minimum allowable availability percentage |
| `pricing_history` | Optional | Custom historical pricing structure |

---

## 3. Baseline & Candidate Configurations

### Baseline Configuration
The user's current operational setup ($M_0, L_0$) serves as the baseline for evaluating cost savings and performance deltas.

### Candidate Tiers
The simulation engine evaluates the following standardized memory tiers:
$$\mathcal{M} = \{512, 1024, 1536, 2048, 3072\} \text{ MB}$$

---

## 4. Cost Model

Serverless execution cost is modelled as a function of total compute time and allocated memory:

$$\text{Monthly Cost} = V \times \left(\frac{M}{1024}\right) \times \left(\frac{L}{1000}\right) \times P$$

Where:
- $V$ = Request volume
- $M$ = Memory size in MB
- $L$ = Estimated latency in milliseconds
- $P$ = Unit price per GB-second

### Cost Savings Percentage
Cost savings compared to the baseline configuration is calculated as:

$$\text{Savings \%} = \begin{cases} 
0.0, & \text{if } \text{Cost}_{\text{baseline}} = 0 \text{ or } \text{Cost}_{\text{candidate}} = \text{Cost}_{\text{baseline}} \\
\left( \frac{\text{Cost}_{\text{baseline}} - \text{Cost}_{\text{candidate}}}{\text{Cost}_{\text{baseline}}} \right) \times 100, & \text{otherwise}
\end{cases}$$

### Baseline Consistency Guarantee
When a candidate memory configuration equals the baseline memory configuration ($M_{\text{candidate}} = M_0$), the candidate latency equals baseline latency ($L = L_0$), candidate cost equals baseline cost, and cost savings is exactly $0.0\%$.

---

## 5. Latency Model

In serverless architectures, memory allocation dictates allocated CPU capacity. Increasing memory decreases execution latency up to the point of diminishing returns.

The candidate latency $L_{\text{candidate}}$ is estimated using a power-law scaling relationship:

$$L_{\text{candidate}} = L_0 \times \left( \frac{M_0}{M_{\text{candidate}}} \right)^{0.65}$$

### Properties:
1. **Baseline Consistency**: If $M_{\text{candidate}} = M_0$, $L_{\text{candidate}} = L_0$.
2. **Under-provisioning Penalty**: Halving memory ($1024 \to 512$ MB) increases latency by factor $(2.0)^{0.65} \approx 1.57\times$.
3. **Diminishing Returns**: Doubling memory ($1024 \to 2048$ MB) reduces latency to $(0.5)^{0.65} \approx 63.7\%$ of baseline. However, allocating double memory doubles the cost rate per second, so over-provisioning memory increases total monthly cost.

---

## 6. Availability Model

Availability measures the percentage of requests processed without memory throttling or timeout errors ($90.0\% - 100.0\%$).

Resource Load Ratio $S$:
$$S = \left(\frac{C}{100}\right) \times \left(\frac{M_0}{M_{\text{candidate}}}\right)$$

Estimated Availability:
$$A_{\text{candidate}} = \begin{cases}
99.95 - 3.5 \times (S - 1.0)^{1.4}, & \text{if } S > 1.0 \text{ (overload resource risk)} \\
\min\left(100.0, \, 99.95 + 0.04 \times (1.0 - S)\right), & \text{if } S \le 1.0 \text{ (well provisioned)}
\end{cases}$$

Bounded within $[90.0, 100.0]\%$.

---

## 7. Recommendation Logic

The engine selects a recommendation using a two-stage filter:

### Stage 1: Constraint Verification (Feasibility Check)
A candidate tier $M$ is marked **Feasible** if and only if BOTH conditions are met:
1. $L_{\text{candidate}} \le L_{\text{target}}$ (`latency_target_met`)
2. $A_{\text{candidate}} \ge A_{\text{target}}$ (`availability_target_met`)

### Stage 2: Cost-Performance Balance Selection
From all feasible tiers $\mathcal{F}$:
- Primary criterion: Select configuration with the **lowest estimated monthly cost**.
- Secondary criterion: If two feasible configurations have identical monthly cost, select the one with lower estimated latency.

### Near-Optimal Current Configuration
If the recommended configuration tier matches the user's current baseline memory ($M_{\text{recommendation}} = M_0$), the system reports:
> *"Current configuration is already near-optimal"*

### No Feasible Configuration Case
If $\mathcal{F} = \emptyset$:
- Returns `simulation_status = "no_feasible_configuration"`
- Returns `recommendation = null`
- Generates an explanation detailing which targets were violated by each candidate tier.

---

## 8. Assumptions & Limitations

1. **Educational Simulation Model**: This is an educational simulation model and not an official AWS pricing or performance model.
2. **Fixed Code Efficiency**: Assumes application logic execution scales with CPU availability.
3. **No Cold Start Simulation**: Cold start latency spikes are omitted from average monthly estimations in Phase 2.
