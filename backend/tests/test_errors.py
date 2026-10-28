def test_404_error_format(client):
    response = client.get("/api/nonexistent-route-for-testing")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert data["is_simulated"] is True
    assert data["error"]["type"] == "HTTPException"
