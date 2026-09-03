# Architecture — Serverless Cost & Performance Rightsizing Simulator

## Overview

This document describes the full-stack architecture for the Serverless Cost & Performance Rightsizing Simulator.
**Phase 6 is complete.** Local JWT Authentication, Multi-Tenant Organization Isolation, and Role-Based Access Control (Admin, Analyst, Viewer) are active across all endpoints and UI views.

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER BROWSER                           │
│                                                                 │
│  React + Vite + Tailwind CSS + Recharts                         │
│  - AuthContext (JWT tokens, role verification, session state)   │
│  - ProtectedRoute (Admin / Analyst / Viewer route guards)       │
│  - Login & Register Views (one-click demo login buttons)        │
│  - Organization & Team Management Workbench                     │
│  - Dashboard (user welcome banner, live metrics feed)           │
│  - Scenarios & Rightsizing Simulator Workbench                  │
│  - Sensitivity Analysis (presets, Recharts, insights)           │
│  - Simulation History & Side-by-Side Comparison                 │
│  - System Settings (Storage Mode & Security Provider Status)    │
└────────────────────────────────┬────────────────────────────────┘
                                 │  HTTP/HTTPS (Authorization: Bearer <JWT>)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND API LAYER                          │
│                                                                 │
│  FastAPI (Python)                                               │
│  - POST /api/auth/register, /api/auth/login, GET /api/auth/me   │
│  - GET/PUT /api/organizations/me                                │
│  - GET/POST /api/users, PUT /api/users/{id}/role, /status       │
│  - GET/POST/PUT/DELETE /api/scenarios (Multi-Tenant Isolated)   │
│  - POST /api/scenarios/{id}/simulate (Multi-Tenant Isolated)    │
│  - GET/DELETE /api/history (Multi-Tenant Isolated)              │
│  - GET /api/history/compare/{id1}/{id2}                         │
│  - GET /api/storage/status                                      │
│  - GET /api/sensitivity/variables                               │
│  - POST /api/sensitivity/analyze (Multi-Tenant Isolated)        │
│  - GET /health, GET /api/info, GET /api/metrics/summary         │
└────────────────────────────────┬────────────────────────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            ▼                    ▼                    ▼
┌───────────────────────┐ ┌──────────────┐ ┌──────────────────────┐
│  SENSITIVITY ENGINE   │ │ AUTH SERVICE │ │ STORAGE SELECTOR     │
│ (sensitivity_engine)  │ │ (bcrypt/JWT) │ │ (get_scenario_repo   │
│ - Reuses run_sim      │ └──────────────┘ │  get_history_repo)   │
│ - No duplicate math   │                  └──────────┬───────────┘
└───────────────────────┘                             │
                           ┌──────────────────────────┴───────────┐
                           │                                      │
                   if STORAGE_MODE=local                  if STORAGE_MODE=aws
                           ▼                                      ▼
                 ┌───────────────────┐                  ┌───────────────────┐
                 │ SQLite Database   │                  │ Amazon DynamoDB   │
                 │ (simulator.db)    │                  │ - Scenarios Table │
                 │ - users           │                  │ - History Table   │
                 │ - organizations   │                  │                   │
                 │ - scenarios       │                  │ Amazon S3 Bucket  │
                 │ - history         │                  │ - Artifact Exports│
                 └───────────────────┘                  └───────────────────┘
```

---

## Component Details

### Frontend (React + Vite)

| Technology | Role |
|---|---|
| React 18 | Component-based UI framework |
| AuthContext | JWT state store, session persistence, automatic token attachment |
| ProtectedRoute | Declarative role-based routing guard |
| Vite | Fast dev server + production bundler |
| Tailwind CSS | Utility-first responsive styling |
| Recharts | Interactive SVG charting library |
| Lucide React | Modern iconography |
| Axios | HTTP client with automatic 401 interceptor |

---

### Backend (FastAPI)

| Component | Role |
|---|---|
| `app/main.py` | App entry point, CORS configuration, SQLite schema init, router registration |
| `app/api/auth.py` | `/api/auth/register`, `/api/auth/login`, `/api/auth/me` |
| `app/api/organizations.py` | `/api/organizations/me` (Profile and description management) |
| `app/api/users.py` | `/api/users` (Team member CRUD, role changes, activation status with final admin guard) |
| `app/api/scenarios.py` | Multi-tenant Scenario CRUD & execution |
| `app/api/history.py` | Multi-tenant Simulation History & comparison |
| `app/api/sensitivity.py` | Multi-tenant Sensitivity Analysis endpoints |
| `app/api/storage.py` | Storage provider status endpoint |
| `app/services/auth_service.py` | Bcrypt password hashing & JWT encoding/decoding |
| `app/services/simulation_engine.py` | Pure mathematical rightsizing engine |
| `app/services/sensitivity_engine.py` | Multi-point parameter trade-off explorer |
| `app/core/dependencies.py` | `get_current_user`, `require_admin`, `require_analyst_or_admin` |
| `app/repositories/` | SQLite & DynamoDB repositories for Users, Organizations, Scenarios, and History |

---

## Phase Roadmap

| Phase | Goal | Status |
|---|---|---|
| Phase 1 | Project foundation — local stack, synthetic CSV metrics, basic APIs | ✅ Complete |
| Phase 2 | Simulation engine — cost, latency, availability, recommendation math | ✅ Complete |
| Phase 3 | Scenario management & simulation history — SQLite persistence | ✅ Complete |
| Phase 4 | AWS cloud persistence — DynamoDB, S3, Repository Selector, SAM template | ✅ Complete |
| Phase 5 | Interactive Sensitivity Analysis — parameter trade-off exploration | ✅ Complete |
| Phase 6 | Authentication, Organizations, and Role-Based Access Control (RBAC) | ✅ Complete |
| Phase 7 | Future Cloud Deployments (AWS Lambda, Cognito Production, CloudWatch) | 🔲 Planned |
