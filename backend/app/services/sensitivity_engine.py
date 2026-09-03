"""
Sensitivity Engine — Phase 5 Rightsizing Parameter Sensitivity Service.

Performs parameter sensitivity analysis by varying a single workload parameter across multiple test points
and executing the EXISTING Phase 2 simulation engine for each point.

CRITICAL: Does NOT duplicate rightsizing formulas. Reuses run_simulation() as single source of truth.
"""

from typing import List, Dict, Any
from app.models.response_models import (
    SimulationRequest,
    SensitivityPoint,
    SensitivityResponse,
    SensitivityVariable
)
from app.services.simulation_engine import run_simulation


SUPPORTED_VARIABLES: Dict[str, Dict[str, Any]] = {
    "request_volume": {
        "label": "Request Volume",
        "unit": "requests/month",
        "description": "Varies monthly workload request volume",
        "scenario_field": "request_volume",
        "min_val": 0.0,
        "max_val": None,
        "is_int": True
    },
    "cpu_utilization": {
        "label": "CPU Utilization",
        "unit": "%",
        "description": "Varies average CPU utilization percentage",
        "scenario_field": "cpu_utilization",
        "min_val": 0.0,
        "max_val": 100.0,
        "is_int": False
    },
    "baseline_latency_ms": {
        "label": "Baseline Latency",
        "unit": "ms",
        "description": "Varies baseline function execution latency",
        "scenario_field": "baseline_latency_ms",
        "min_val": 0.0001,
        "max_val": None,
        "is_int": False
    },
    "latency_target_ms": {
        "label": "Latency Target SLO",
        "unit": "ms",
        "description": "Varies target maximum latency SLA requirement",
        "scenario_field": "latency_target_ms",
        "min_val": 0.0001,
        "max_val": None,
        "is_int": False
    },
    "availability_target_percent": {
        "label": "Availability Target SLO",
        "unit": "%",
        "description": "Varies target availability percentage requirement",
        "scenario_field": "availability_target_percent",
        "min_val": 90.0,
        "max_val": 100.0,
        "is_int": False
    },
    "current_price": {
        "label": "Pricing Rate",
        "unit": "$/GB-sec",
        "description": "Varies compute pricing rate per GB-sec",
        "scenario_field": "current_price",
        "min_val": 0.0,
        "max_val": None,
        "is_int": False
    }
}


def get_supported_variables_metadata() -> List[SensitivityVariable]:
    """Returns metadata for all supported sensitivity analysis variables."""
    return [
        SensitivityVariable(
            key=k,
            label=v["label"],
            unit=v["unit"],
            description=v["description"]
        )
        for k, v in SUPPORTED_VARIABLES.items()
    ]


def run_sensitivity_analysis(
    scenario: Dict[str, Any],
    variable_key: str,
    test_values: List[float]
) -> SensitivityResponse:
    """
    Executes sensitivity analysis across test values for a scenario.
    Reuses existing run_simulation() without repeating formulas.
    """
    var_meta = SUPPORTED_VARIABLES[variable_key]
    field_name = var_meta["scenario_field"]
    baseline_val = float(scenario[field_name])

    points: List[SensitivityPoint] = []
    recommended_memories = []

    for val in test_values:
        # 1. Create a copy of base scenario parameters
        scenario_params = {
            "scenario_name": scenario["name"],
            "cpu_utilization": float(scenario["cpu_utilization"]),
            "memory_mb": float(scenario["baseline_memory_mb"]),
            "baseline_latency_ms": float(scenario["baseline_latency_ms"]),
            "request_volume": int(scenario["request_volume"]),
            "current_price": float(scenario["current_price"]),
            "latency_target_ms": float(scenario["latency_target_ms"]),
            "availability_target": float(scenario["availability_target_percent"])
        }

        # 2. Overwrite ONLY the selected sensitivity variable
        if field_name == "availability_target_percent":
            scenario_params["availability_target"] = val
        elif field_name == "request_volume":
            scenario_params["request_volume"] = int(val)
        else:
            scenario_params[field_name] = val

        # 3. Construct SimulationRequest & call EXISTING simulation engine
        sim_request = SimulationRequest(**scenario_params)
        sim_result = run_simulation(sim_request)

        # 4. Format SensitivityPoint
        rec = sim_result.recommendation
        if rec:
            recommended_memories.append(rec.memory_mb)
            point = SensitivityPoint(
                input_value=val,
                recommended_memory_mb=rec.memory_mb,
                recommended_cost=rec.estimated_monthly_cost,
                recommended_latency_ms=rec.estimated_latency_ms,
                recommended_availability_percent=rec.estimated_availability,
                savings_percent=rec.cost_savings_percentage,
                simulation_status="Recommended"
            )
        else:
            recommended_memories.append(None)
            point = SensitivityPoint(
                input_value=val,
                recommended_memory_mb=None,
                recommended_cost=None,
                recommended_latency_ms=None,
                recommended_availability_percent=None,
                savings_percent=None,
                simulation_status="No Feasible Configuration"
            )

        points.append(point)

    # 5. Generate human-readable insight summary
    insight_summary = _generate_insight_summary(
        var_label=var_meta["label"],
        var_unit=var_meta["unit"],
        points=points,
        recommended_memories=recommended_memories
    )

    return SensitivityResponse(
        scenario_id=scenario.get("id", scenario.get("scenario_id", "")),
        scenario_name=scenario["name"],
        variable=variable_key,
        variable_label=var_meta["label"],
        baseline_value=baseline_val,
        points=points,
        insight_summary=insight_summary
    )


def _generate_insight_summary(
    var_label: str,
    var_unit: str,
    points: List[SensitivityPoint],
    recommended_memories: List[Any]
) -> str:
    """Generates a clear human-readable explanation of sensitivity results."""
    valid_mems = [m for m in recommended_memories if m is not None]

    if not valid_mems:
        return f"No feasible serverless configuration exists across any tested {var_label} levels under current target SLO constraints."

    unique_mems = list(dict.fromkeys(valid_mems))

    if len(unique_mems) == 1:
        return (
            f"The recommended configuration remains optimal at {unique_mems[0]} MB across all tested {var_label} levels. "
            f"Cost scales smoothly without requiring a memory tier change."
        )

    first_mem = unique_mems[0]
    last_mem = unique_mems[-1]

    if None in recommended_memories:
        return (
            f"As {var_label} changes, the recommended memory scales from {first_mem} MB to {last_mem} MB. "
            f"At extreme points, no feasible configuration satisfies the required latency/availability targets."
        )

    return (
        f"Varying {var_label} causes the recommended memory configuration to shift from {first_mem} MB to {last_mem} MB. "
        f"Increasing compute memory offsets performance bottlenecks as workload demands change."
    )
