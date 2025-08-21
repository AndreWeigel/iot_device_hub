def test_device_crud_flow(client, create_user, auth_header):
    create_user(client, username="carol", email="carol@example.com", password="secret123")
    headers = auth_header(client, "carol", "secret123")

    # Initially no devices
    resp = client.get("/device", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []

    # Register a device
    resp = client.post("/device", json={"name": "sensor-1", "device_type": "thermometer"}, headers=headers)
    assert resp.status_code == 201
    device = resp.json()
    assert "device_key" in device
    device_id = device["id"]

    # Update device
    resp = client.put(f"/devices/{device_id}", json={"name": "sensor-1b"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "sensor-1b"

    # Toggle MQTT enabled
    resp = client.put(f"/devices/{device_id}/mqtt", params={"mqtt_enabled": False}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["mqtt_enabled"] is False

    # Delete device
    resp = client.delete(f"/devices/{device_id}", headers=headers)
    assert resp.status_code == 204


