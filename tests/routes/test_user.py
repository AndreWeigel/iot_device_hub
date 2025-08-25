
# Test 1: create a user, log in, and read the current user profile
def test_register_login_and_get_user(client, create_user, auth_header):
    """
    - Create a new user via the API.
    - Log in to obtain a JWT token.
    - Use the token to fetch the current user profile.
    - Verify username and email match the created user.
    """
    u = create_user(client, username="alice", email="alice@example.com", password="secret123")

    # Login to get token
    headers = auth_header(client, u["username"], u["password"])

    # Check current user endpoint
    resp = client.get("/user", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"


# Test 2: update the user’s username/email, then re-login with the new username and delete the account
def test_update_and_delete_user(client, create_user, auth_header, get_user_token):
    """
    - Create a new user.
    - Log in and update username and email.
    - Re-login with the new username (since JWT subject is username).
    - Delete the user with the new token.
    """
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


