"""
Unit tests for Phase 2 Rightsizing Simulation Engine.

Verifies:
  1. Baseline consistency (candidate matching baseline memory produces equal cost, equal latency, and 0.0% savings)
  2. Availability formula calculation matching documentation exactly
  3. Normal workload
  4. Low traffic
  5. High traffic
  6. High CPU
  7. High baseline latency
  8. Tight latency target
  9. Tight availability target
 10. Zero request volume
 11. No feasible configuration
 12. Invalid input (validation error)
"""

import pytest
from pydantic import ValidationError
from app.models.response_models import SimulationRequest
from app.services.simulation_engine import (
    run_simulation,
    calculate_cost,
    calculate_latency,
    calculate_availability,
    calculate_cost_savings
)


def test_baseline_consistency():
    """Verify that when candidate memory equals baseline memory, cost, latency, and savings are 100% consistent."""
    req = SimulationRequest(
        scenario_name="Baseline Consistency Test",
        cpu_utilization=65.0,
        memory_mb=1024.0,
        baseline_latency_ms=150.0,
        request_volume=2000000,
        current_price=0.00001667,
        latency_target_ms=200.0,
        availability_target=99.9
    )
    res = run_simulation(req)
    assert res.simulation_status == "success"

    # Find the candidate matching baseline memory (1024 MB)
    candidate_1024 = next(c for c in res.configurations if c.memory_mb == 1024.0)

    # 1. Latency must equal baseline latency
    assert candidate_1024.estimated_latency_ms == res.baseline.latency_ms
    assert candidate_1024.estimated_latency_ms == 150.0

    # 2. Monthly cost must equal baseline cost
    assert candidate_1024.estimated_monthly_cost == res.baseline.estimated_monthly_cost
    assert candidate_1024.estimated_monthly_cost == 5.001

    # 3. Cost savings percentage must be 0.0%
    assert candidate_1024.cost_savings_percentage == 0.0

    # 4. Availability must match baseline availability
    assert candidate_1024.estimated_availability == res.baseline.availability


def test_availability_formula_matches_documentation():
    """Verify that calculate_availability matches documented formulas exactly."""
    # Case A: Well provisioned (load_ratio <= 1.0)
    # CPU = 50%, Baseline = 1024MB, Candidate = 1024MB -> load_ratio = 0.5
    # bonus = 0.04 * (1.0 - 0.5) = 0.02 -> availability = 99.95 + 0.02 = 99.97%
    avail_a = calculate_availability(50.0, 1024.0, 1024.0)
    assert avail_a == 99.97

    # Case B: Overloaded (load_ratio > 1.0)
    # CPU = 80%, Baseline = 1024MB, Candidate = 512MB -> load_ratio = 1.6
    # penalty = 3.5 * (1.6 - 1.0)^1.4 = 3.5 * (0.6)^1.4 = 3.5 * 0.4876 = 1.7067
    # availability = 99.95 - 1.7067 = 98.2433 -> rounded to 98.24%
    avail_b = calculate_availability(80.0, 1024.0, 512.0)
    assert avail_b == 98.24


def test_normal_workload():
    req = SimulationRequest(
        scenario_name="Normal Workload",
        cpu_utilization=45.0,
        memory_mb=1024.0,
        baseline_latency_ms=150.0,
        request_volume=2000000,
        current_price=0.00001667,
        latency_target_ms=200.0,
        availability_target=99.9
    )
    res = run_simulation(req)
    assert res.simulation_status == "success"
    assert res.recommendation is not None
    assert res.recommendation.estimated_latency_ms <= 200.0
    assert res.recommendation.estimated_availability >= 99.9
    # 1024 MB is recommended as near-optimal
    assert res.recommendation.memory_mb == 1024.0
    assert res.recommendation.cost_savings_percentage == 0.0
    assert "near-optimal" in res.explanation


def test_low_traffic():
    req = SimulationRequest(
        scenario_name="Low Traffic",
        cpu_utilization=15.0,
        memory_mb=1024.0,
        baseline_latency_ms=100.0,
        request_volume=50000,
        current_price=0.00001667,
        latency_target_ms=250.0,
        availability_target=99.5
    )
    res = run_simulation(req)
    assert res.simulation_status == "success"
    assert res.recommendation is not None
    # 512 MB is selected as it saves cost while staying well within latency target
    assert res.recommendation.memory_mb == 512.0
    assert res.recommendation.cost_savings_percentage > 0.0


def test_high_traffic():
    req = SimulationRequest(
        scenario_name="High Traffic",
        cpu_utilization=85.0,
        memory_mb=1024.0,
        baseline_latency_ms=220.0,
        request_volume=10000000,
        current_price=0.00001667,
        latency_target_ms=180.0,
        availability_target=99.9
    )
    res = run_simulation(req)
    assert res.simulation_status == "success"
    assert res.recommendation is not None
    # Needs higher memory tier to meet the 180ms latency target
    assert res.recommendation.memory_mb >= 1536.0


def test_high_cpu():
    req = SimulationRequest(
        scenario_name="High CPU Load",
        cpu_utilization=98.0,
        memory_mb=1024.0,
        baseline_latency_ms=180.0,
        request_volume=3000000,
        current_price=0.00001667,
        latency_target_ms=200.0,
        availability_target=99.0
    )
    res = run_simulation(req)
    # High CPU overload on 512MB causes availability penalty
    c_512 = next(c for c in res.configurations if c.memory_mb == 512.0)
    assert c_512.estimated_availability < 99.0 or not c_512.latency_target_met


def test_high_baseline_latency():
    req = SimulationRequest(
        scenario_name="Legacy Slow Service",
        cpu_utilization=50.0,
        memory_mb=512.0,
        baseline_latency_ms=800.0,
        request_volume=1000000,
        current_price=0.00001667,
        latency_target_ms=500.0,
        availability_target=99.5
    )
    res = run_simulation(req)
    assert res.simulation_status == "success"
    # To reduce 800ms down to <=500ms, higher memory is required
    assert res.recommendation.memory_mb > 512.0


def test_tight_latency_target():
    req = SimulationRequest(
        scenario_name="Strict Latency SLO",
        cpu_utilization=40.0,
        memory_mb=1024.0,
        baseline_latency_ms=150.0,
        request_volume=1000000,
        current_price=0.00001667,
        latency_target_ms=90.0,
        availability_target=99.0
    )
    res = run_simulation(req)
    assert res.simulation_status == "success"
    # 90ms target requires 2048 MB or 3072 MB
    assert res.recommendation.memory_mb >= 2048.0


def test_tight_availability_target():
    req = SimulationRequest(
        scenario_name="Strict Availability SLO",
        cpu_utilization=70.0,
        memory_mb=512.0,
        baseline_latency_ms=100.0,
        request_volume=1000000,
        current_price=0.00001667,
        latency_target_ms=200.0,
        availability_target=99.98
    )
    res = run_simulation(req)
    if res.recommendation:
        assert res.recommendation.estimated_availability >= 99.98


def test_zero_request_volume():
    req = SimulationRequest(
        scenario_name="Zero Requests Idle Service",
        cpu_utilization=0.0,
        memory_mb=1024.0,
        baseline_latency_ms=100.0,
        request_volume=0,
        current_price=0.00001667,
        latency_target_ms=200.0,
        availability_target=99.0
    )
    res = run_simulation(req)
    assert res.simulation_status == "success"
    assert res.baseline.estimated_monthly_cost == 0.0
    assert res.recommendation.estimated_monthly_cost == 0.0


def test_no_feasible_configuration():
    req = SimulationRequest(
        scenario_name="Impossible Targets",
        cpu_utilization=90.0,
        memory_mb=512.0,
        baseline_latency_ms=500.0,
        request_volume=1000000,
        current_price=0.00001667,
        latency_target_ms=10.0,
        availability_target=99.999
    )
    res = run_simulation(req)
    assert res.simulation_status == "no_feasible_configuration"
    assert res.recommendation is None
    assert "No configuration satisfies" in res.explanation


def test_invalid_input_validation():
    with pytest.raises(ValidationError):
        SimulationRequest(
            scenario_name="Invalid CPU",
            cpu_utilization=150.0,
            memory_mb=1024.0,
            baseline_latency_ms=100.0,
            request_volume=100000,
            current_price=0.00001667,
            latency_target_ms=200.0,
            availability_target=99.0
        )
