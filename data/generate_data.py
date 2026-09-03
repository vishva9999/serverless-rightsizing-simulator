"""
Synthetic Data Generator for Serverless Rightsizing Simulator
=============================================================
This script generates SYNTHETIC data for simulation and learning purposes only.
This is NOT real AWS billing data. All values are artificially constructed
to demonstrate realistic serverless workload patterns.

Author: Phase 1 Setup
"""

import csv
import random
import math
from datetime import datetime, timedelta

random.seed(42)  # Reproducible results

OUTPUT_FILE = "sample_serverless_metrics.csv"

# Simulation period: 30 days at 15-minute intervals
START_DATE = datetime(2026, 8, 1, 0, 0, 0)
INTERVAL_MINUTES = 15
TOTAL_RECORDS = 30 * 24 * 4  # 2880 records (15-min intervals over 30 days)

COLUMNS = [
    "timestamp",
    "cpu_utilization",
    "memory_mb",
    "latency_ms",
    "request_volume",
    "instance_price",
    "availability",
]


def hour_of_day(dt):
    return dt.hour + dt.minute / 60.0


def traffic_multiplier(dt):
    """
    Return a traffic multiplier based on time of day.
    - Low traffic:    00:00 – 06:00 (night)
    - Normal traffic: 06:00 – 10:00 and 18:00 – 22:00 (shoulder)
    - High traffic:   10:00 – 18:00 (business hours peak)
    """
    h = hour_of_day(dt)
    if 0 <= h < 6:
        return random.uniform(0.05, 0.20)   # Low
    elif 6 <= h < 10 or 18 <= h < 22:
        return random.uniform(0.35, 0.65)   # Normal
    elif 10 <= h < 18:
        return random.uniform(0.65, 1.00)   # High
    else:
        return random.uniform(0.10, 0.30)   # Late night


def generate_record(dt):
    multiplier = traffic_multiplier(dt)

    # Weekend dip: ~40% less traffic on Saturday/Sunday
    if dt.weekday() >= 5:
        multiplier *= 0.60

    # Occasional traffic spike (flash events ~2% chance)
    if random.random() < 0.02:
        multiplier = min(1.0, multiplier * random.uniform(1.8, 2.5))

    # CPU utilization (%) — correlated with traffic, 5–95%
    cpu = max(5.0, min(95.0, multiplier * 85 + random.gauss(0, 4)))

    # Memory usage in MB — baseline 256MB, scales with load
    memory = max(128, min(1024, 256 + multiplier * 512 + random.gauss(0, 20)))

    # Latency in ms — increases non-linearly under high load
    base_latency = 20 + multiplier * 180
    latency = max(10, base_latency + random.gauss(0, base_latency * 0.15))

    # Request volume per 15-min interval — 0 to ~5000
    requests = max(0, int(multiplier * 4800 + random.gauss(0, 150)))

    # Lambda pricing (simplified): $0.0000166667 per GB-second
    # Assume avg duration ~300ms, billed per 128MB increment
    memory_gb = memory / 1024.0
    duration_sec = latency / 1000.0
    instance_price = round(requests * memory_gb * duration_sec * 0.0000166667, 6)

    # Availability — high load slightly increases error risk
    base_availability = 99.95
    if multiplier > 0.85:
        base_availability -= random.uniform(0, 0.15)
    elif multiplier > 0.65:
        base_availability -= random.uniform(0, 0.05)
    availability = round(max(99.0, min(100.0, base_availability + random.gauss(0, 0.02))), 4)

    return {
        "timestamp": dt.strftime("%Y-%m-%dT%H:%M:%S"),
        "cpu_utilization": round(cpu, 2),
        "memory_mb": round(memory, 1),
        "latency_ms": round(latency, 2),
        "request_volume": requests,
        "instance_price": instance_price,
        "availability": availability,
    }


def main():
    records = []
    current_dt = START_DATE

    for _ in range(TOTAL_RECORDS):
        records.append(generate_record(current_dt))
        current_dt += timedelta(minutes=INTERVAL_MINUTES)

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(records)

    print(f"Generated {len(records)} records -> {OUTPUT_FILE}")
    print("NOTE: This is SYNTHETIC data for simulation purposes only.")
    print("      It does NOT represent real AWS billing or performance data.")


if __name__ == "__main__":
    main()
