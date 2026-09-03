# Serverless Cost & Performance Rightsizing Simulator

> **Student Project — Phase 6 Complete (Authentication, Organizations & RBAC)**
> A full-stack simulator that helps startups understand the relationship between serverless cost and application performance.

---

## Problem Statement

Startups running serverless applications on AWS often over-provision Lambda memory and CPU, resulting in:
- **Unnecessarily high cloud bills** from idle compute capacity
- **Poor performance visibility** — no clear link between configuration and latency
- **Guesswork-based scaling** — without data-driven rightsizing recommendations

There is no easy tool for students and small engineering teams to explore the cost-performance trade-off space interactively.

---

## Main Features

| Feature | Phase | Status |
|---|---|---|
| Dashboard with summary metrics | Phase 1 | ✅ Built |
| Synthetic dataset (CSV, 2,880 rows) | Phase 1 | ✅ Built |
| FastAPI backend with health/info/metrics endpoints | Phase 1 | ✅ Built |
| Rightsizing simulation engine service (`simulation_engine.py`) | Phase 2 | ✅ Built |
| Interactive Simulator Page & Recharts | Phase 2 | ✅ Built |
| Dynamic RecommendationCard ("Why this configuration?") | Phase 2 | ✅ Built |
| Persistent Scenario Management (CRUD + Presets) | Phase 3 | ✅ Built |
| Simulation History & Run Comparison | Phase 3 | ✅ Built |
| AWS DynamoDB Cloud Persistence (`serverless-rightsizing-scenarios`, `serverless-rightsizing-history`) | Phase 4 | ✅ Built |
| Amazon S3 Artifact Export (`simulations/{scenario_id}/{history_id}.json`) | Phase 4 | ✅ Built |
| Storage Selector Pattern (`STORAGE_MODE=local` vs `STORAGE_MODE=aws`) | Phase 4 | ✅ Built |
| Storage Status API (`GET /api/storage/status`) | Phase 4 | ✅ Built |
| Interactive Sensitivity Analysis Engine (`sensitivity_engine.py`) | Phase 5 | ✅ Built |
| Sensitivity Endpoints (`POST /api/sensitivity/analyze`, `GET /api/sensitivity/variables`) | Phase 5 | ✅ Built |
| Sensitivity Analysis Workbench UI (Scenario/Variable Selectors, Presets, 3 Recharts, Table) | Phase 5 | ✅ Built |
| Automated Sensitivity Insight Summary Generator | Phase 5 | ✅ Built |
| Local JWT Authentication & Bcrypt Password Hashing | Phase 6 | ✅ Built |
| Multi-Tenant Organization Isolation (`organization_id` partitioning) | Phase 6 | ✅ Built |
| Role-Based Access Control (Admin, Analyst, Viewer) | Phase 6 | ✅ Built |
| Organization & Team Management Page (`Organizations.jsx`) | Phase 6 | ✅ Built |
| Protected Routes & React `AuthContext` with Bearer Interceptors | Phase 6 | ✅ Built |
| Complete Unit Test Suite (62/62 passing with 100% success rate) | Phase 6 | ✅ Built |

---

## Technology Stack

### Frontend
- **React 18** — component-based UI
- **AuthContext** — JWT session state store & Axios Bearer token interceptor
- **Vite** — fast development server and build tool
- **Tailwind CSS** — utility-first styling
- **Recharts** — charting library (bar, line charts)
- **Lucide React** — icon library
- **Axios** — HTTP client for backend communication

### Backend
- **Python 3.13** — primary language
- **FastAPI** — modern async web framework
- **PyJWT & Bcrypt** — JWT token generation and password hashing
- **SQLite & Amazon DynamoDB** — dual persistence options
- **Amazon S3 & Boto3** — cloud artifact export & AWS SDK
- **Pandas & NumPy** — data processing
- **Pydantic** — data validation & schemas
- **Pytest** — unit test suite (62 tests passing)
- **Uvicorn** — ASGI server

---

## How to Run

### Start the Backend

```bash
cd serverless-rightsizing-simulator/backend
py -m pip install -r requirements.txt
py scripts/seed_demo_users.py
py -m uvicorn app.main:app --reload
```

- **API Base:** `http://localhost:8000`
- **Swagger Docs:** `http://localhost:8000/docs`
- **Storage Status API:** `http://localhost:8000/api/storage/status`
- **Run Unit Tests:** `py -m pytest tests/ -v`

### Demo Login Accounts (Development)
- **Admin**: `admin@example.com` / `AdminPass123!`
- **Analyst**: `analyst@example.com` / `AnalystPass123!`
- **Viewer**: `viewer@example.com` / `ViewerPass123!`

---

### Start the Frontend

In a **new terminal**:

```bash
cd serverless-rightsizing-simulator/frontend
npm install
npm run dev
```

- **App:** `http://localhost:5173`

---

## API Endpoints Reference

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/auth/register` | Public | Register new user & workspace (first user = Admin) |
| POST | `/api/auth/login` | Public | Authenticate email/password, return access token |
| GET | `/api/auth/me` | Authenticated | Current user profile |
| GET | `/api/organizations/me` | Authenticated | Organization details and member count |
| PUT | `/api/organizations/me` | Admin | Update organization profile |
| GET | `/api/users` | Admin / Analyst | List organization members |
| POST | `/api/users` | Admin | Invite/create user in organization |
| PUT | `/api/users/{id}/role` | Admin | Change member role (with final admin protection) |
| PUT | `/api/users/{id}/status` | Admin | Activate/deactivate member account |
| GET | `/api/scenarios` | Authenticated | List scenarios (organization-scoped) |
| POST | `/api/scenarios` | Admin / Analyst | Create scenario |
| GET | `/api/scenarios/{id}` | Authenticated | Get single scenario by ID |
| PUT | `/api/scenarios/{id}` | Admin / Analyst | Update scenario parameters |
| DELETE | `/api/scenarios/{id}` | Admin | Delete scenario |
| POST | `/api/scenarios/{id}/simulate` | Admin / Analyst | Run simulation on scenario, save to history |
| GET | `/api/history` | Authenticated | List simulation history (organization-scoped) |
| GET | `/api/history/{id}` | Authenticated | Get history detail with full simulation JSON |
| DELETE | `/api/history/{id}` | Admin | Delete history entry |
| GET | `/api/history/compare/{id1}/{id2}` | Authenticated | Compare two simulation runs side-by-side |
| GET | `/api/sensitivity/variables` | Authenticated | List supported sensitivity variables |
| POST | `/api/sensitivity/analyze` | Admin / Analyst | Run sensitivity analysis for scenario & variable |
| GET | `/api/storage/status` | Public | Active storage provider, database type, and AWS health |
| GET | `/health` | Public | Service liveness check |
| GET | `/api/info` | Public | Project metadata |
| GET | `/api/metrics/summary` | Public | Aggregated statistics from CSV dataset |
| POST | `/api/simulate` | Public | Evaluates workload parameters directly |

---

*Built as a student project to demonstrate full-stack serverless architecture design.*
