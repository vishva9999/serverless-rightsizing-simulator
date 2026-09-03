# Amazon Cognito Authentication & RBAC Integration

## 1. Architecture Overview
Phase 7 integrates Amazon Cognito for cloud identity authentication (`AUTH_MODE=cognito`) while maintaining full backward compatibility with local JWT authentication (`AUTH_MODE=local`).

```
                              ┌─────────────────────────────────┐
                              │     React / Vite Application    │
                              └────────────────┬────────────────┘
                                               │
                        ┌──────────────────────┴──────────────────────┐
                        │                                             │
               if AUTH_MODE=local                             if AUTH_MODE=cognito
                        ▼                                             ▼
             ┌─────────────────────┐                       ┌─────────────────────┐
             │ Local JWT Auth      │                       │ Amazon Cognito      │
             │ - HS256 algorithm   │                       │ - RS256 algorithm   │
             │ - Local secret key  │                       │ - JWKS endpoint     │
             │ - SQLite user store │                       │ - Public SPA client │
             └─────────────────────┘                       └─────────────────────┘
```

---

## 2. Cognito User Pool Configuration
- **User Pool Name**: `serverless-rightsizing-simulator-user-pool-prod`
- **Username Attributes**: Email-based sign-in.
- **Auto-Verified Attributes**: Email verification.
- **Password Policy**: Minimum 8 characters, uppercase, lowercase, numbers.
- **Account Recovery**: Verified email.

---

## 3. Cognito User Pool App Client
- **Client Type**: Public Single-Page Application (SPA) Client.
- **Client Secret**: `None` (Public clients in browsers must not hold client secrets).
- **Explicit Auth Flows**:
  - `ALLOW_USER_PASSWORD_AUTH`
  - `ALLOW_USER_SRP_AUTH`
  - `ALLOW_REFRESH_TOKEN_AUTH`
- **Prevent User Existence Errors**: `ENABLED`.

---

## 4. Backend JWT Validation & JWKS Caching
In `backend/app/services/cognito_service.py`:
1. **JWKS Fetching & Caching**: Public RSA keys are retrieved from `https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json` and cached in-memory for 24 hours.
2. **Signature Verification**: Validates the RS256 digital signature against the public key matching `kid` in the token header.
3. **Claim Verification**:
   - `iss`: Ensures token was issued by the configured User Pool.
   - `exp`: Ensures token has not expired.
   - `client_id` / `aud`: Ensures token was created for the authorized application client.

---

## 5. Identity & Organization Mapping
- **Identity Key**: Uses Cognito `sub` (UUID) as the stable unique identifier.
- **Role Assignment**: Cognito groups (`admin`, `analyst`) map directly to application RBAC roles.
- **Organization Partitioning**: Authenticated requests derive `organization_id` strictly from backend application state—never from user-controlled headers.
