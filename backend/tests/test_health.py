def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["ok", "degraded"]
    assert data["is_simulated"] is True
    assert data["emergency_services_integrated"] is False
    assert "database" in data
    assert "uptime_seconds" in data
    assert "simulation_disclaimer" in data


def test_v1_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert data["is_simulated"] is True
    assert data["emergency_services_integrated"] is False


def test_version_endpoint(client):
    response = client.get("/api/version")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0-phase1"
    assert data["api_version"] == "v1"
    assert data["is_simulated"] is True


def test_v1_version_endpoint(client):
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0-phase1"
    assert data["is_simulated"] is True
