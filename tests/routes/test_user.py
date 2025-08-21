def test_register_login_and_get_user(client, create_user, auth_header):
    u = create_user(client, username="alice", email="alice@example.com", password="secret123")

    # Login to get token
    headers = auth_header(client, u["username"], u["password"])

    # Check current user endpoint
    resp = client.get("/user", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"


def test_update_and_delete_user(client, create_user, auth_header, get_user_token):
    create_user(client, username="bob", email="bob@example.com", password="secret123")
    headers = auth_header(client, "bob", "secret123")

    # Update username and email
    resp = client.put("/user", json={"username": "bobby", "email": "bobby@example.com"}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "bobby"
    assert data["email"] == "bobby@example.com"

    # Token subject is username, so re-login after username change
    new_headers = {"Authorization": f"Bearer {get_user_token(client, "bobby", "secret123")}"}

    # Delete user
    resp = client.delete("/user", headers=new_headers)
    assert resp.status_code == 204


