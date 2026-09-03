# Role-Based Access Control (RBAC) Specification

## 1. Role Hierarchy & Permission Matrix

The application implements three explicit permission roles:

| Feature / Action | Admin | Analyst | Viewer | Backend Enforcer |
|---|---|---|---|---|
| **View Dashboard & Metrics** | ✅ YES | ✅ YES | ✅ YES | `get_current_user` |
| **View Scenarios** | ✅ YES | ✅ YES | ✅ YES | `get_current_user` |
| **Create Scenario** | ✅ YES | ✅ YES | ❌ NO (403) | `require_analyst_or_admin` |
| **Edit Scenario** | ✅ YES | ✅ YES | ❌ NO (403) | `require_analyst_or_admin` |
| **Delete Scenario** | ✅ YES | ❌ NO (403) | ❌ NO (403) | `require_admin` |
| **Run Simulation** | ✅ YES | ✅ YES | ❌ NO (403) | `require_analyst_or_admin` |
| **View History & Compare** | ✅ YES | ✅ YES | ✅ YES | `get_current_user` |
| **Delete History Entry** | ✅ YES | ❌ NO (403) | ❌ NO (403) | `require_admin` |
| **Sensitivity Analysis** | ✅ YES | ✅ YES | ❌ NO (403) | `require_analyst_or_admin` |
| **View Organization Users** | ✅ YES | ✅ YES | ❌ NO (403) | `require_analyst_or_admin` |
| **Create / Invite Users** | ✅ YES | ❌ NO (403) | ❌ NO (403) | `require_admin` |
| **Change User Roles** | ✅ YES | ❌ NO (403) | ❌ NO (403) | `require_admin` |
| **Activate / Deactivate Users** | ✅ YES | ❌ NO (403) | ❌ NO (403) | `require_admin` |
| **Update Organization Profile** | ✅ YES | ❌ NO (403) | ❌ NO (403) | `require_admin` |

---

## 2. Administrator Safety Invariant

To ensure an organization is never left without administrative oversight, the API enforces a strict guard in `backend/app/api/users.py`:
- An Admin **cannot** demote or deactivate the last remaining active Administrator in an organization.
- Any such attempt returns `400 Bad Request: Cannot demote/deactivate the final active administrator in an organization. Assign another admin first.`

---

## 3. UI Layer Adaptation vs Backend Enforcement

- **UI Navigation**: The sidebar dynamically filters options based on the authenticated role (`Viewer` does not see interactive execution tools).
- **Backend Guard**: UI hiding is strictly for user experience. Every API route enforces cryptographic JWT validation and role verification, rejecting unauthorized requests with `HTTP 403 Forbidden` or `HTTP 401 Unauthorized`.
