# Phase 6 — Authentication & Organizations Documentation

## 1. Overview
Phase 6 introduces a secure, local-first authentication and authorization layer (`AUTH_MODE=local`) designed for multi-tenant workspace environments.

```
+-------------------------------------------------------------------------+
|                               Client Request                            |
|                     (Header: Authorization: Bearer <JWT>)               |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                    FastAPI Dependency: get_current_user                 |
|       - Decodes JWT access token with HS256 algorithm                   |
|       - Verifies expiration and signature                               |
|       - Fetches user record from local SQLite repository                |
|       - Validates account active status (is_active == 1)                |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                      Multi-Tenant Organization Filter                   |
|       - Injects authenticated organization_id into repo queries         |
|       - Guarantees strict cross-organization data isolation            |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                       Role-Based Access Control (RBAC)                  |
|       - require_admin: Administrator only                               |
|       - require_analyst_or_admin: Admin & Analyst                       |
|       - require_authenticated_user: Admin, Analyst, Viewer              |
+-------------------------------------------------------------------------+
```

---

## 2. Password Security & Cryptography
- **Password Hashing**: Direct `bcrypt` algorithm with automated salt generation.
- **Security Invariants**:
  - Passwords are **never** stored in plain text.
  - Passwords are **never** logged to stdout/stderr.
  - Password hashes are **never** returned in API responses.
  - Passwords are **never** cached in browser localStorage.

---

## 3. JWT Token Mechanics
- **Signature Algorithm**: `HS256`
- **Secret Key Configuration**: Controlled via `JWT_SECRET_KEY` in `backend/.env`.
- **Expiration Policy**: Controlled via `JWT_EXPIRE_MINUTES=60`.
- **Payload Claims**:
  ```json
  {
    "user_id": "93b2a5a1-79ec-45f8-8bb0-a9314c44238e",
    "organization_id": "5f65ada2-429c-4444-93de-994fc425f746",
    "role": "admin",
    "exp": 1788349200,
    "iat": 1788345600
  }
  ```

---

## 4. Multi-Tenant Organization Isolation
Every scenario, simulation history record, and user profile is bound to an `organization_id`.
- The backend API **never trusts** an `organization_id` provided in the HTTP request body.
- The `organization_id` is always derived directly from the authenticated JWT user profile.
- If User $A$ from Organization $1$ attempts to read, edit, or delete a scenario belonging to Organization $2$, the API immediately returns `404 Not Found` to prevent metadata leakage.

---

## 5. API Endpoints

### Authentication Router (`/api/auth`)
| Method | Path | Access | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | Public | Registers a new user & workspace (first user = Admin) |
| `POST` | `/api/auth/login` | Public | Authenticates credentials and issues JWT token |
| `GET` | `/api/auth/me` | Authenticated | Returns current authenticated user profile |

### Organization Router (`/api/organizations`)
| Method | Path | Access | Description |
|---|---|---|---|
| `GET` | `/api/organizations/me` | Authenticated | Retrieves current user's organization metadata |
| `PUT` | `/api/organizations/me` | Admin Only | Updates organization name & description |

### User Management Router (`/api/users`)
| Method | Path | Access | Description |
|---|---|---|---|
| `GET` | `/api/users` | Admin / Analyst | Lists team members in current organization |
| `GET` | `/api/users/{id}` | Admin / Analyst | Fetches detailed profile of a member |
| `POST` | `/api/users` | Admin Only | Creates and invites a new member |
| `PUT` | `/api/users/{id}/role` | Admin Only | Updates member role (with final admin safety guard) |
| `PUT` | `/api/users/{id}/status` | Admin Only | Activates/deactivates user (with final admin guard) |

---

## 6. Development Demo Accounts
For rapid local testing and demonstrations, run:
```bash
py scripts/seed_demo_users.py
```

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Admin** | `admin@example.com` | `AdminPass123!` | Full permissions: Scenarios, Simulations, Team & Role Management |
| **Analyst** | `analyst@example.com` | `AnalystPass123!` | Create/Edit Scenarios, Run Simulations, Sensitivity Analysis |
| **Viewer** | `viewer@example.com` | `ViewerPass123!` | Read-only: Dashboard, View Scenarios, View History |

---

## 7. Future AWS Cognito Migration Roadmap
The authentication layer is decoupled behind `AuthService` and `UserRepository`. In future AWS production deployments (`AUTH_MODE=cognito`):
1. Replace `AuthService.decode_access_token` with AWS Cognito JWKS public key verification.
2. Map Cognito User Pool Groups (`admins`, `analysts`, `viewers`) directly to application roles.
3. No rightsizing simulation formulas, scenario repositories, or business controllers require refactoring.
