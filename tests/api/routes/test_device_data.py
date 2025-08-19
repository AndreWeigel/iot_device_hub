from datetime import datetime, timedelta, timezone


def test_ingest_and_query_device_data(client, create_user, auth_header):
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


