import random
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.logging import logger
from app.models.simulation_scenario import SimulationScenario, ScenarioStatusEnum
from app.models.simulation_result import SimulationResult
from app.models.disaster_zone import DisasterZone
from app.schemas.simulation import (
    DisasterTypeEnum,
    RiskLevelEnum,
    DamageLevelEnum,
    EvacuationPriorityEnum,
    SimulationInputParams,
    SimulationOutputData,
    ZoneSimulationImpact,
    SimulationScenarioCreate,
)


class DisasterSimulationEngine:
    """
    Deterministic Disaster Simulation Engine.
    Simulates physical hazard dynamics, infrastructure degradation,
    affected population, and evacuation urgency for tactical decision exercises.
    ALL GENERATED DATA IS STRICTLY SYNTHETIC/SIMULATED.
    """

    MUNICIPAL_ZONES = [
        {"id": 1, "name": "Zone 1 - Gandhipuram Central", "base_pop": 24500, "vuln": 0.65},
        {"id": 2, "name": "Zone 2 - RS Puram West", "base_pop": 18200, "vuln": 0.40},
        {"id": 3, "name": "Zone 3 - Singanallur Industrial", "base_pop": 31000, "vuln": 0.80},
        {"id": 4, "name": "Zone 4 - Peelamedu North", "base_pop": 22000, "vuln": 0.50},
        {"id": 5, "name": "Zone 5 - Ukkadam Lake Basin", "base_pop": 28400, "vuln": 0.90},
        {"id": 6, "name": "Zone 6 - Town Hall Heritage Area", "base_pop": 16800, "vuln": 0.70},
    ]

    @staticmethod
    def calculate_simulation(params: SimulationInputParams) -> SimulationOutputData:
        """
        Pure deterministic calculation of disaster metrics based on input parameters and random seed.
        """
        seed = params.random_seed if params.random_seed is not None else 42
        rng = random.Random(seed)

        dtype = params.disaster_type.value if hasattr(params.disaster_type, "value") else str(params.disaster_type)

        # 1. Base hazard severity (0 - 100)
        if dtype == DisasterTypeEnum.FLOOD.value:
            base_severity = (params.rainfall / 300.0) * 50.0 + (params.water_level / 10.0) * 50.0
        elif dtype == DisasterTypeEnum.CYCLONE.value:
            base_severity = (params.wind_speed / 220.0) * 60.0 + (params.rainfall / 300.0) * 40.0
        elif dtype == DisasterTypeEnum.EARTHQUAKE.value:
            base_severity = (params.earthquake_intensity / 9.0) * 100.0
        elif dtype == DisasterTypeEnum.URBAN_FIRE.value:
            temp_norm = max(0.0, (params.temperature - 20.0) / 30.0) * 35.0
            wind_norm = (params.wind_speed / 100.0) * 35.0
            bldg_norm = (params.building_density / 3000.0) * 30.0
            base_severity = temp_norm + wind_norm + bldg_norm
        elif dtype == DisasterTypeEnum.LANDSLIDE.value:
            rain_norm = (params.rainfall / 250.0) * 60.0
            hist_norm = params.historical_risk * 40.0
            base_severity = rain_norm + hist_norm
        else:
            base_severity = 50.0

        base_severity = max(0.0, min(100.0, base_severity))

        # 2. Exposure modifier
        pop_factor = min(1.0, params.population_density / 8000.0)
        bldg_factor = min(1.0, params.building_density / 3000.0)
        exposure = (pop_factor * 0.4) + (bldg_factor * 0.3) + (params.historical_risk * 0.3)
        time_mult = 1.12 if str(params.time_of_day).lower() in ["night", "22", "23", "0", "1", "2", "3", "4"] else 1.0

        # 3. Deterministic stochastic jitter
        jitter = rng.uniform(-2.5, 2.5)

        # 4. Final Composite Risk Score (0.0 to 100.0)
        raw_risk = (base_severity * 0.65) + (exposure * 35.0 * time_mult) + jitter
        risk_score = round(max(0.0, min(100.0, raw_risk)), 2)

        # 5. Risk Level classification
        if risk_score < 25.0:
            risk_level = RiskLevelEnum.LOW
        elif risk_score < 50.0:
            risk_level = RiskLevelEnum.MEDIUM
        elif risk_score < 75.0:
            risk_level = RiskLevelEnum.HIGH
        else:
            risk_level = RiskLevelEnum.CRITICAL

        # 6. Road Accessibility percentage (0.0 to 100.0)
        road_degradation = (risk_score * 0.60) + (1.0 - params.road_condition) * 40.0
        road_accessibility = round(max(5.0, min(100.0, 100.0 - road_degradation)), 2)

        # 7. Affected population
        affected_ratio = (risk_score / 100.0) ** 1.25
        total_baseline_pop = int(params.population_density * 8.5)
        affected_population = int(total_baseline_pop * affected_ratio * (0.95 + rng.uniform(0.0, 0.1)))
        population_at_risk = int(affected_population * 1.3)

        # 8. Estimated Damage Level
        if risk_score < 30.0:
            damage_level = DamageLevelEnum.MINOR
        elif risk_score < 55.0:
            damage_level = DamageLevelEnum.MODERATE
        elif risk_score < 80.0:
            damage_level = DamageLevelEnum.SEVERE
        else:
            damage_level = DamageLevelEnum.CATASTROPHIC

        # 9. Evacuation Priority
        if risk_score < 30.0:
            evac_priority = EvacuationPriorityEnum.LOW
        elif risk_score < 55.0:
            evac_priority = EvacuationPriorityEnum.MEDIUM
        elif risk_score < 75.0:
            evac_priority = EvacuationPriorityEnum.HIGH
        else:
            evac_priority = EvacuationPriorityEnum.IMMEDIATE

        # 10. Estimated Evacuation Time (in hours)
        speed_factor = max(0.1, road_accessibility / 100.0)
        estimated_evac_time = round(max(0.5, (affected_population / 2500.0) / speed_factor), 2)

        # 11. Resource shortages & shelter utilization
        shelter_utilization = round(min(100.0, (affected_population / max(1, total_baseline_pop * 0.7)) * 100.0), 2)
        resource_shortages = max(0, int((risk_score - 40.0) / 10.0)) if risk_score > 40.0 else 0

        # 12. Zone impacts
        zone_impacts: List[ZoneSimulationImpact] = []
        for z in DisasterSimulationEngine.MUNICIPAL_ZONES:
            zone_vuln = z["vuln"]
            z_risk = round(min(100.0, max(0.0, risk_score * (0.8 + zone_vuln * 0.4) + rng.uniform(-3, 3))), 2)
            z_level = (
                RiskLevelEnum.CRITICAL if z_risk >= 75
                else RiskLevelEnum.HIGH if z_risk >= 50
                else RiskLevelEnum.MEDIUM if z_risk >= 25
                else RiskLevelEnum.LOW
            )
            z_priority = (
                EvacuationPriorityEnum.IMMEDIATE if z_risk >= 75
                else EvacuationPriorityEnum.HIGH if z_risk >= 50
                else EvacuationPriorityEnum.MEDIUM if z_risk >= 25
                else EvacuationPriorityEnum.LOW
            )
            z_affected = int(z["base_pop"] * (z_risk / 100.0) ** 1.2)
            z_road = round(max(5.0, min(100.0, 100.0 - (z_risk * 0.65))), 2)

            zone_impacts.append(
                ZoneSimulationImpact(
                    zone_id=z["id"],
                    zone_name=z["name"],
                    risk_score=z_risk,
                    risk_level=z_level,
                    affected_population=z_affected,
                    evacuation_priority=z_priority,
                    road_accessibility_percent=z_road,
                )
            )

        return SimulationOutputData(
            risk_score=risk_score,
            risk_level=risk_level,
            affected_population=affected_population,
            population_at_risk=population_at_risk,
            road_accessibility=road_accessibility,
            estimated_damage_level=damage_level,
            evacuation_priority=evac_priority,
            estimated_evacuation_time=estimated_evac_time,
            resource_shortage_count=resource_shortages,
            shelter_utilization=shelter_utilization,
            zone_impacts=zone_impacts,
            is_simulated=True,
            disclaimer="SYNTHETIC SIMULATION DATA ONLY. NOT CONNECTED TO REAL EMERGENCY SERVICES.",
        )

    @classmethod
    def create_scenario(
        cls, db: Session, scenario_in: SimulationScenarioCreate, user_id: int
    ) -> SimulationScenario:
        """Create a new simulation scenario record in the database."""
        params_dict = scenario_in.parameters_json or {}
        if scenario_in.parameters:
            params_dict = scenario_in.parameters.model_dump()
        elif not params_dict:
            # Default parameters for disaster type
            default_params = SimulationInputParams(
                disaster_type=scenario_in.disaster_type,
                random_seed=scenario_in.random_seed or 42,
            )
            params_dict = default_params.model_dump()

        scenario = SimulationScenario(
            name=scenario_in.name,
            disaster_type=scenario_in.disaster_type.value if hasattr(scenario_in.disaster_type, "value") else str(scenario_in.disaster_type),
            description=scenario_in.description,
            random_seed=scenario_in.random_seed or 42,
            parameters_json=params_dict,
            status=ScenarioStatusEnum.CREATED.value,
            created_by=user_id,
        )
        db.add(scenario)
        db.commit()
        db.refresh(scenario)
        return scenario

    @classmethod
    def run_scenario(cls, db: Session, scenario_id: int) -> tuple[SimulationScenario, SimulationResult, SimulationOutputData]:
        """Execute a deterministic simulation run for a stored scenario and record the result."""
        scenario = db.get(SimulationScenario, scenario_id)
        if not scenario:
            raise ValueError(f"Simulation scenario with id {scenario_id} not found")

        scenario.status = ScenarioStatusEnum.RUNNING.value
        db.commit()

        try:
            # Parse parameters
            params_dict = scenario.parameters_json or {}
            params_dict["disaster_type"] = scenario.disaster_type
            params_dict["random_seed"] = scenario.random_seed or 42

            input_params = SimulationInputParams(**params_dict)
            outputs = cls.calculate_simulation(input_params)

            # Persist result
            sim_result = SimulationResult(
                scenario_id=scenario.id,
                affected_population=outputs.affected_population,
                population_at_risk=outputs.population_at_risk,
                average_risk_score=outputs.risk_score,
                estimated_evacuation_time=outputs.estimated_evacuation_time,
                resource_shortage_count=outputs.resource_shortage_count,
                shelter_utilization=outputs.shelter_utilization,
                result_json=outputs.model_dump(),
                created_at=datetime.now(timezone.utc),
            )
            db.add(sim_result)
            scenario.status = ScenarioStatusEnum.COMPLETED.value
            db.commit()
            db.refresh(scenario)
            db.refresh(sim_result)

            return scenario, sim_result, outputs
        except Exception as e:
            scenario.status = ScenarioStatusEnum.FAILED.value
            db.commit()
            logger.error(f"Error executing simulation scenario {scenario_id}: {e}")
            raise

    @classmethod
    def get_or_create_demo_scenario(cls, db: Session, admin_user_id: int) -> SimulationScenario:
        """Seed or retrieve the canonical demo scenario: 'Coimbatore Flood Simulation - DEMO'."""
        stmt = select(SimulationScenario).where(
            SimulationScenario.name == "Coimbatore Flood Simulation - DEMO"
        )
        scenario = db.scalars(stmt).first()
        if not scenario:
            demo_in = SimulationScenarioCreate(
                name="Coimbatore Flood Simulation - DEMO",
                disaster_type=DisasterTypeEnum.FLOOD,
                description="Controlled synthetic flood simulation along Noyyal river basin in Coimbatore.",
                random_seed=42,
                parameters=SimulationInputParams(
                    disaster_type=DisasterTypeEnum.FLOOD,
                    rainfall=210.0,
                    water_level=4.8,
                    wind_speed=45.0,
                    earthquake_intensity=0.0,
                    temperature=26.5,
                    road_condition=0.7,
                    population_density=3200.0,
                    building_density=950.0,
                    historical_risk=0.75,
                    time_of_day="day",
                    random_seed=42,
                ),
            )
            scenario = cls.create_scenario(db, demo_in, admin_user_id)
            # Run the scenario once to produce initial demo results
            cls.run_scenario(db, scenario.id)
            db.refresh(scenario)

        return scenario
