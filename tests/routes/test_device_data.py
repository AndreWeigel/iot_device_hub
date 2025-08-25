from datetime import datetime, timedelta, timezone


def test_ingest_and_query_device_data(client, create_user, auth_header):
    """
    - Create a user and register a device.
    - Obtain a device token using device_id + device_key.
    - Ingest three telemetry points with different timestamps.
    - Query the latest 2 points.
    - Query a time range covering all 3 points.
    """
    # Create user and login
    create_user(client, username="dave", email="dave@example.com", password="secret123")
    headers = auth_header(client, "dave", "secret123")

    # Register a device for user
    resp = client.post("/device", json={"name": "sensor-2", "device_type": "thermometer"}, headers=headers)
    assert resp.status_code == 201
    dev = resp.json()
    device_id = dev["id"]

    # Device obtains a device token via /device/token
    resp = client.post(
        "/device/token",
        data={"device_id": device_id, "device_key": dev["device_key"]},
    )
    assert resp.status_code == 200
    device_token = resp.json()["access_token"]

    # Ingest data using device token
    now = datetime.now(timezone.utc)
    payloads = [
        {"reading_type": "temp", "value": 21.5, "timestamp": (now - timedelta(minutes=2)).isoformat()},
        {"reading_type": "temp", "value": 22.1, "timestamp": (now - timedelta(minutes=1)).isoformat()},
        {"reading_type": "temp", "value": 22.8, "timestamp": now.isoformat()},
    ]

    for p in payloads:
        resp = client.post(
            "/devices/data",
            json=p,
            headers={"Authorization": f"Bearer {device_token}"},
        )
        assert resp.status_code == 200, resp.text

    # Query last data points
    resp = client.get(f"/devices/{device_id}/data/last", params={"limit": 2}, headers=headers)
    assert resp.status_code == 200
    last = resp.json()
    assert len(last) == 2

    # Query range
    start = (now - timedelta(minutes=3)).isoformat()
    end = (now + timedelta(seconds=1)).isoformat()
    resp = client.get(
        f"/devices/{device_id}/data/range",
        params={"start": start, "end": end},
        headers=headers,
    )
    assert resp.status_code == 200
    rng = resp.json()
    assert len(rng) == 3


def test_ingest_invalid_payload(client, create_user, auth_header):
    create_user(client, "a2", "a2@e.com", "pw")
    h = auth_header(client, "a2", "pw")
    dev = client.post("/device", json={"name":"s","device_type":"t"}, headers=h).json()
    tok = client.post("/device/token", data={"device_id":dev["id"],"device_key":dev["device_key"]}).json()["access_token"]
    # Missing timestamp
    r = client.post("/devices/data", json={"reading_type":"temp"},
                    headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 422


def test_range_start_after_end(client, create_user, auth_header):
    create_user(client, "a3", "a3@e.com", "pw")
    h = auth_header(client, "a3", "pw")
    dev = client.post("/device", json={"name":"s","device_type":"t"}, headers=h).json()
    r = client.get(f"/devices/{dev['id']}/data/range",
                   params={"start":"2025-01-02T00:00:00Z","end":"2025-01-01T00:00:00Z"},
                   headers=h)
    assert r.status_code == 400