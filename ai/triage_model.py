"""
AI Disaster Resource Allocation & Triage Prioritization Engine.
DISCLAIMER: All algorithmic predictions and optimization outputs are simulated 
for synthetic scenarios and must not be used for real emergency medical or life-safety operations.
"""
from typing import Dict, Any, List
import numpy as np

class DisasterTriageModel:
    """
    Simulated predictive triage and priority scoring for evacuation sectors.
    Uses multi-criteria decision analysis (hazard proximity, vulnerable population density, route congestion).
    """

    def __init__(self, version: str = "1.0.0-sim"):
        self.version = version
        self.is_simulated = True

    def calculate_sector_urgency(
        self,
        hazard_distance_km: float,
        population_count: int,
        vulnerability_ratio: float,
        route_capacity_ratio: float,
    ) -> Dict[str, Any]:
        """
        Computes composite evacuation urgency score between 0.0 and 1.0.
        """
        # Distance decay factor
        distance_factor = float(np.exp(-0.15 * max(0.1, hazard_distance_km)))
        # Population vulnerability factor
        vuln_factor = float(np.clip(vulnerability_ratio, 0.0, 1.0))
        # Congestion bottleneck factor
        bottleneck_factor = float(np.clip(1.0 - route_capacity_ratio, 0.0, 1.0))

        # Weighted priority formula (simulated heuristic)
        raw_score = (0.45 * distance_factor) + (0.35 * vuln_factor) + (0.20 * bottleneck_factor)
        urgency_score = float(np.clip(raw_score, 0.0, 1.0))

        if urgency_score >= 0.75:
            priority_tier = "CRITICAL_EVACUATE_IMMEDIATELY"
        elif urgency_score >= 0.50:
            priority_tier = "HIGH_PRIORITY"
        elif urgency_score >= 0.25:
            priority_tier = "ELEVATED_WATCH"
        else:
            priority_tier = "ROUTINE_MONITORING"

        return {
            "urgency_score": round(urgency_score, 4),
            "priority_tier": priority_tier,
            "is_simulated": True,
            "model_version": self.version,
            "metadata": {
                "distance_factor": round(distance_factor, 4),
                "vulnerability_factor": round(vuln_factor, 4),
                "bottleneck_factor": round(bottleneck_factor, 4),
            }
        }
