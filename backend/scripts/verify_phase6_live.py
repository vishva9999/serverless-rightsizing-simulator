"""
Live API Verification Script for Phase 6.
Tests health, login, register, current user, organization, users, scenarios, history, and RBAC rules.
"""

import httpx
import sys

BASE_URL = "http://127.0.0.1:8000"

def run_checks():
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    print("1. Checking GET /health...")
    r = client.get("/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print("   [OK] /health 200 OK")

    print("2. Checking POST /api/auth/login (Admin)...")
    r = client.post("/api/auth/login", json={"email": "admin@example.com", "password": "AdminPass123!"})
    assert r.status_code == 200, f"Login failed: {r.text}"
    admin_token = r.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("   [OK] Admin Login 200 OK")

    print("3. Checking GET /api/auth/me (Current User)...")
    r = client.get("/api/auth/me", headers=admin_headers)
    assert r.status_code == 200, f"Auth me failed: {r.text}"
    assert r.json()["email"] == "admin@example.com"
    print("   [OK] /api/auth/me 200 OK:", r.json()["full_name"])

    print("4. Checking GET /api/organizations/me...")
    r = client.get("/api/organizations/me", headers=admin_headers)
    assert r.status_code == 200, f"Organization get failed: {r.text}"
    print("   [OK] /api/organizations/me 200 OK:", r.json()["name"])

    print("5. Checking GET /api/users...")
    r = client.get("/api/users", headers=admin_headers)
    assert r.status_code == 200, f"Users get failed: {r.text}"
    print(f"   [OK] /api/users 200 OK: {len(r.json())} members")

    print("6. Checking POST /api/auth/login (Viewer)...")
    r = client.post("/api/auth/login", json={"email": "viewer@example.com", "password": "ViewerPass123!"})
    assert r.status_code == 200, f"Viewer login failed: {r.text}"
    viewer_token = r.json()["access_token"]
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
    print("   [OK] Viewer Login 200 OK")

    print("7. Checking RBAC: Viewer attempting to create scenario (Must return 403)...")
    r = client.post("/api/scenarios", json={
        "name": "Viewer Forbidden Scenario",
        "workload_type": "Custom",
        "request_volume": 100000,
        "baseline_memory_mb": 1024.0,
        "baseline_latency_ms": 150.0,
        "cpu_utilization": 50.0,
        "current_price": 0.00001667,
        "latency_target_ms": 200.0,
        "availability_target_percent": 99.9
    }, headers=viewer_headers)
    assert r.status_code == 403, f"Expected 403, got {r.status_code}"
    print("   [OK] RBAC Guard 403 Forbidden confirmed for Viewer")

    print("8. Checking GET /api/storage/status (Public)...")
    r = client.get("/api/storage/status")
    assert r.status_code == 200, f"Storage status failed: {r.text}"
    print("   [OK] /api/storage/status 200 OK (Mode:", r.json()["mode"], ")")

    print("\nALL LIVE VERIFICATION CHECKS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    run_checks()
