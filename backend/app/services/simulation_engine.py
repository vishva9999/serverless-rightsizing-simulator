"""
Simulation Engine Service — Phase 2 Rightsizing Simulation Engine.

Provides transparent, mathematically consistent simulation models for:
  - Estimated Monthly Cost
  - Estimated Latency
  - Estimated Availability
  - Constraint validation against SLO targets
  - Rightsizing Recommendation

NOTE: This is an educational simulation model and not an official AWS pricing or performance model.
"""

from typing import List, Optional
from app.models.response_models import (
    SimulationRequest,
    SimulationResponse,
    BaselineResult,
    CandidateConfigResult,
    RecommendationResult,
)

# Standard candidate memory configurations to evaluate (in MB)
CANDIDATE_MEMORY_TIERS = [512, 1024, 1536, 2048, 3072]


def calculate_cost(
    request_volume: int,
    memory_mb: float,
    latency_ms: float,
    unit_price: float
) -> float:
    """
    Calculate estimated monthly cost.
    Formula: request_volume * (memory_mb / 1024.0) * (latency_ms / 1000.0) * unit_price
    """
    if request_volume <= 0 or unit_price <= 0 or memory_mb <= 0 or latency_ms <= 0:
        return 0.0

    memory_gb = memory_mb / 1024.0
    duration_sec = latency_ms / 1000.0
    total_cost = request_volume * memory_gb * duration_sec * unit_price
    return round(float(total_cost), 4)


def calculate_latency(
    baseline_latency_ms: float,
    baseline_memory_mb: float,
    candidate_memory_mb: float,
    cpu_utilization: float = 0.0
) -> float:
    """
    Calculate estimated latency for a candidate memory configuration.
    
    Formula:
    estimated_latency = baseline_latency_ms * (baseline_memory_mb / candidate_memory_mb)^0.65
    
    Guarantees baseline consistency: when candidate_memory_mb == baseline_memory_mb,
    the estimated latency is exactly equal to baseline_latency_ms.
    """
    if baseline_latency_ms <= 0 or candidate_memory_mb <= 0:
        return 0.0

    memory_ratio = baseline_memory_mb / candidate_memory_mb
    estimated_latency = baseline_latency_ms * (memory_ratio ** 0.65)
    return round(float(max(5.0, estimated_latency)), 2)


def calculate_availability(
    cpu_utilization: float,
    baseline_memory_mb: float,
    candidate_memory_mb: float
) -> float:
    """
    Calculate estimated availability percentage (90.0 - 100.0).
    
    Formula:
    Resource load ratio S = (cpu_utilization / 100.0) * (baseline_memory_mb / candidate_memory_mb)
    
    If S > 1.0: penalty = 3.5 * (S - 1.0)^1.4; availability = 99.95 - penalty
    If S <= 1.0: bonus = 0.04 * (1.0 - S); availability = 99.95 + bonus
    
    Result is bounded within [90.0, 100.0].
    """
    load_ratio = (cpu_utilization / 100.0) * (baseline_memory_mb / candidate_memory_mb)

    if load_ratio > 1.0:
        penalty = 3.5 * ((load_ratio - 1.0) ** 1.4)
        est_avail = 99.95 - penalty
    else:
        bonus = 0.04 * (1.0 - load_ratio)
        est_avail = 99.95 + bonus

    bounded_avail = max(90.0, min(100.0, est_avail))
    return round(float(bounded_avail), 2)


def calculate_cost_savings(baseline_cost: float, candidate_cost: float) -> float:
    """
    Calculate cost savings percentage compared to baseline.
    Formula: ((baseline_cost - candidate_cost) / baseline_cost) * 100
    
    Guarantees baseline consistency: if candidate_cost == baseline_cost, returns 0.0%.
    """
    if baseline_cost <= 0.0:
        return 0.0
    if abs(baseline_cost - candidate_cost) < 1e-6:
        return 0.0
    savings = ((baseline_cost - candidate_cost) / baseline_cost) * 100.0
    return round(float(savings), 2)


def generate_explanation(
    request: SimulationRequest,
    baseline: BaselineResult,
    candidates: List[CandidateConfigResult],
    recommendation: Optional[RecommendationResult]
) -> str:
    """Generate human-readable explanation of the simulation recommendation."""
    if not recommendation:
        failed_reasons = []
        for c in candidates:
            reasons = []
            if not c.latency_target_met:
                reasons.append(f"latency ({c.estimated_latency_ms} ms > target {request.latency_target_ms} ms)")
            if not c.availability_target_met:
                reasons.append(f"availability ({c.estimated_availability}% < target {request.availability_target}%)")
            failed_reasons.append(f"{int(c.memory_mb)} MB violates " + " and ".join(reasons))

        return (
            "No configuration satisfies the required performance and availability targets. "
            f"Evaluated tiers: {', '.join(failed_reasons)}. "
            "Consider relaxing the latency or availability targets to find a feasible rightsizing configuration."
        )

    rec_mem = int(recommendation.memory_mb)
    rec_cost = recommendation.estimated_monthly_cost
    rec_savings = recommendation.cost_savings_percentage

    # If the recommended tier is the baseline configuration
    if rec_mem == int(baseline.memory_mb):
        cheaper_rejected = [c for c in candidates if c.estimated_monthly_cost < rec_cost and not c.feasible]
        explanation_parts = []

        if cheaper_rejected:
            for c in cheaper_rejected:
                reasons = []
                if not c.latency_target_met:
                    reasons.append(f"estimated latency ({c.estimated_latency_ms} ms) exceeds target ({request.latency_target_ms} ms)")
                if not c.availability_target_met:
                    reasons.append(f"estimated availability ({c.estimated_availability}%) falls below target ({request.availability_target}%)")
                explanation_parts.append(
                    f"{int(c.memory_mb)} MB has a lower estimated cost (${c.estimated_monthly_cost}), but its " + " and ".join(reasons) + "."
                )

        explanation_parts.append(
            f"Current configuration ({rec_mem} MB) is already near-optimal. "
            f"It satisfies both latency (≤ {request.latency_target_ms} ms) and availability (≥ {request.availability_target}%) requirements while maintaining the best cost balance."
        )
        return "\n\n".join(explanation_parts)

    # If another tier is recommended
    cheaper_rejected = [c for c in candidates if c.estimated_monthly_cost < rec_cost and not c.feasible]
    explanation_parts = []

    if cheaper_rejected:
        for c in cheaper_rejected:
            reasons = []
            if not c.latency_target_met:
                reasons.append(f"estimated latency ({c.estimated_latency_ms} ms) exceeds target ({request.latency_target_ms} ms)")
            if not c.availability_target_met:
                reasons.append(f"estimated availability ({c.estimated_availability}%) falls below target ({request.availability_target}%)")
            explanation_parts.append(
                f"{int(c.memory_mb)} MB has a lower estimated cost (${c.estimated_monthly_cost}), but its " + " and ".join(reasons) + "."
            )

    if rec_savings > 0:
        savings_text = f"reduces cost by {rec_savings}% (saving ${round(baseline.estimated_monthly_cost - rec_cost, 4)}/mo)"
    else:
        savings_text = f"increases cost by {abs(rec_savings)}% to satisfy performance targets"

    explanation_parts.append(
        f"{rec_mem} MB satisfies both latency (≤ {request.latency_target_ms} ms) and availability (≥ {request.availability_target}%) requirements, and {savings_text}."
    )
    explanation_parts.append(f"Therefore, {rec_mem} MB is recommended as the optimal rightsizing configuration.")

    return "\n\n".join(explanation_parts)


def run_simulation(request: SimulationRequest) -> SimulationResponse:
    """
    Main engine runner. Evaluates baseline and all candidate tiers, checks constraints,
    determines feasibility, selects recommendation, and generates explanation.
    """
    memory_tiers = sorted(list(set(CANDIDATE_MEMORY_TIERS + [int(request.memory_mb)])))

    # 1. Evaluate Baseline
    baseline_cost = calculate_cost(
        request_volume=request.request_volume,
        memory_mb=request.memory_mb,
        latency_ms=request.baseline_latency_ms,
        unit_price=request.current_price
    )
    baseline_avail = calculate_availability(
        cpu_utilization=request.cpu_utilization,
        baseline_memory_mb=request.memory_mb,
        candidate_memory_mb=request.memory_mb
    )

    baseline = BaselineResult(
        memory_mb=request.memory_mb,
        estimated_monthly_cost=baseline_cost,
        latency_ms=request.baseline_latency_ms,
        availability=baseline_avail
    )

    # 2. Evaluate Candidate Configurations
    candidates: List[CandidateConfigResult] = []

    for mem in memory_tiers:
        est_lat = calculate_latency(
            baseline_latency_ms=request.baseline_latency_ms,
            baseline_memory_mb=request.memory_mb,
            candidate_memory_mb=mem,
            cpu_utilization=request.cpu_utilization
        )

        est_cost = calculate_cost(
            request_volume=request.request_volume,
            memory_mb=mem,
            latency_ms=est_lat,
            unit_price=request.current_price
        )

        est_avail = calculate_availability(
            cpu_utilization=request.cpu_utilization,
            baseline_memory_mb=request.memory_mb,
            candidate_memory_mb=mem
        )

        savings_pct = calculate_cost_savings(baseline_cost, est_cost)

        lat_met = est_lat <= request.latency_target_ms
        avail_met = est_avail >= request.availability_target
        feasible = lat_met and avail_met

        candidates.append(
            CandidateConfigResult(
                memory_mb=float(mem),
                estimated_monthly_cost=est_cost,
                estimated_latency_ms=est_lat,
                estimated_availability=est_avail,
                cost_savings_percentage=savings_pct,
                latency_target_met=lat_met,
                availability_target_met=avail_met,
                feasible=feasible
            )
        )

    # 3. Select Best Recommendation
    feasible_configs = [c for c in candidates if c.feasible]

    if not feasible_configs:
        simulation_status = "no_feasible_configuration"
        recommendation = None
    else:
        simulation_status = "success"
        feasible_configs.sort(key=lambda c: (c.estimated_monthly_cost, c.estimated_latency_ms))
        best = feasible_configs[0]

        recommendation = RecommendationResult(
            memory_mb=best.memory_mb,
            estimated_monthly_cost=best.estimated_monthly_cost,
            estimated_latency_ms=best.estimated_latency_ms,
            estimated_availability=best.estimated_availability,
            cost_savings_percentage=best.cost_savings_percentage
        )

    # 4. Generate Explanation
    explanation = generate_explanation(request, baseline, candidates, recommendation)

    return SimulationResponse(
        simulation_status=simulation_status,
        scenario_name=request.scenario_name,
        baseline=baseline,
        configurations=candidates,
        recommendation=recommendation,
        explanation=explanation
    )
