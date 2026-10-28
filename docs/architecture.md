# Architecture Document

## Project: AI Disaster Evacuation & Resource Allocation Command Center

### 1. Overview
The platform provides tactical decision support, evacuation routing simulations, and dynamic shelter resource balancing during synthesized humanitarian disaster scenarios.

> **CRITICAL DISCLAIMER**:
> All sensor feeds, GIS layers, road closures, casualty models, and AI dispatch predictions are purely simulated for research, tabletop exercises, and algorithmic evaluation. The system contains **no integration** with real-world municipal 911 dispatch, civil defense, or emergency services.

---

### 2. Layered Architecture

```
[ Frontend Client (React + TS + Vite + Tailwind) ]
         │
   HTTP / REST (Axios)       WebSocket (/ws)
         │                         │
         ▼                         ▼
[ FastAPI Backend (Python 3.11+ / 3.13) ]
  ├── core/            (Config, Logging, Error Handlers, DB engine)
  ├── api/v1/          (Health, Version, Resource, Evac endpoints)
  ├── models/          (SQLAlchemy Declarative Models)
  ├── schemas/         (Pydantic Data Validation & Serialization)
  ├── services/        (Business Logic & Routing Algorithms)
  ├── repositories/    (Data Access Layer)
  └── websocket/       (Real-Time Telemetry Streaming Manager)
         │
         ├── SQLAlchemy ORM
         ▼
[ PostgreSQL / SQLite Fallback Database ]
```

---

### 3. AI & Simulation Subsystems
- **`simulation/`**: Synthetic hazard expansion engine based on numerical dispersion equations (perimeter spread velocity, severity index calculation).
- **`ai/`**: Multi-criteria decision analysis triage model (`triage_model.py`) using NumPy & Scikit-learn to determine sector urgency tiers without deceptive AI claims.

---

### 4. Security & Safety Guardrails
- Role-based authorization: Incident Commander, Logistics Coordinator, Field Dispatcher, Simulation Analyst.
- Explicit simulation tags across all API responses (`is_simulated: true`, `emergency_services_integrated: false`).
- Hardened CORS configuration and structured request logging.
