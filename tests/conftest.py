import asyncio
import os
import pathlib
import pytest


# ---------------------------
# EVENT LOOP FOR ASYNC TESTS
# ---------------------------
# Pytest-asyncio usually provides a loop automatically, but here you create
# one shared loop for the whole test session. Anything that needs the loop
# (e.g., async DB setup/teardown) can reuse it.@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()   # create a new event loop object
    yield loop                        # make it available to tests/fixtures
    loop.close()                      # teardown: close the event loop once all tests are done



# ---------------------------
# DATABASE URL (TEST)
# ---------------------------
# Build a *file-based* SQLite URL in a tmp directory. File-based (not in-memory)
# is important because multiple async connections will see the same DB and state.
@pytest.fixture(scope="session")
def test_db_url(tmp_path_factory):
    # Use a file-based SQLite DB to persist across connections during tests
    db_dir = tmp_path_factory.mktemp("db")
    db_path = db_dir / "test_iot_device_hub.db"
    return f"sqlite+aiosqlite:///{db_path}"


# ---------------------------
# TEST ENVIRONMENT VARIABLES
# ---------------------------
# autouse=True -> runs for the entire test session even if no test explicitly requests it.
# You set secrets and point the app’s DB to the test DB *before* the app imports/initializes.
@pytest.fixture(scope="session", autouse=True)
def set_test_env(test_db_url):
    # Minimal secrets for JWT
    os.environ["API_SECRET_KEY"] = "test-secret-key"
    os.environ["API_ALGORITHM"] = "HS256"
    # Point the app's DB to our sqlite test database
    os.environ["DATABASE_URL"] = test_db_url
    # Keep MQTT off localhost connection attempts where possible
    os.environ["MQTT_BROKER_URL"] = "localhost"


# ---------------------------
# FASTAPI APP INSTANCE
# ---------------------------
# This fixture imports your FastAPI app *after* env vars are set, ensuring the DB engine
# binds to the test DB. It also patches MQTT-related functions to avoid real network calls.
@pytest.fixture(scope="session")
def app_instance(set_test_env):
    # Import app after env is set so the engine binds to the test DB
    # Resolve path to main.py explicitly to avoid import path issues
    import importlib.util
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[1]
    main_path = project_root / "main.py"

    # Ensure project root is on sys.path so absolute imports like `app.*` resolve
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    spec = importlib.util.spec_from_file_location("main", str(main_path))
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    fastapi_app = module.app

    # Patch MQTT functions at their import sites to avoid actual network calls
    try:
        import app.lifespan as lifespan_mod
        import app.routes.device as device_routes

        async def _noop(*args, **kwargs):
            return None

        # Functions referenced inside lifespan
        lifespan_mod.initialize_all_mqtt_subscriptions = _noop
        lifespan_mod.disconnect_all_mqtt_subscriptions = _noop

        # Function referenced in device route during device creation
        device_routes.initialize_single_mqtt_subscription = _noop
    except Exception:
        pass

    return fastapi_app


# ---------------------------
# HTTP CLIENT (SYNC)
# ---------------------------
# FastAPI's TestClient wraps the ASGI app and automatically runs lifespan
# (startup/shutdown) within the context manager. Each test gets a fresh client.
@pytest.fixture()
def client(app_instance):
    # Use FastAPI's TestClient to handle startup/shutdown automatically
    from fastapi.testclient import TestClient

    with TestClient(app_instance) as c:
        yield c



# ---------------------------
# DIRECT DB SESSION ACCESS (OPTIONAL)
# ---------------------------
# For tests that want to do DB setup/inspection without going through HTTP.
# Returns a small wrapper that runs an async coroutine from a sync test using anyio.
@pytest.fixture()
def db_session():
    # Yield a real AsyncSession bound to the test engine for setup/teardown use in tests
    import anyio
    from app.db.session import async_session

    async def _get_session():
        async with async_session() as session:
            yield session

    # Provide a simple sync wrapper for tests that want to do quick setup
    class _SessionWrapper:
        def run(self, coro):
            return anyio.from_thread.run(asyncio.ensure_future, coro)

    return _SessionWrapper()


# ---------------------------
# HELPERS: CREATE USER VIA API
# ---------------------------
# Calls POST /user with a typical payload and asserts a 201 Created response.
@pytest.fixture()
def create_user():
    # Helper to create a user via the API to ensure consistent hashing and side-effects
    def _create(client, username="alice", email="alice@example.com", password="secret123"):
        payload = {"username": username, "email": email, "password": password}
        resp = client.post("/user", json=payload)
        assert resp.status_code == 201, resp.text
        return {"username": username, "email": email, "password": password, "user": resp.json()}

    return _create


# ---------------------------
# HELPERS: LOGIN TO GET JWT
# ---------------------------
# Posts form-encoded credentials to /token (OAuth2PasswordRequestForm convention).
@pytest.fixture()
def get_user_token():
    def _login(client, username: str, password: str) -> str:
        # OAuth2PasswordRequestForm requires form-encoded body
        resp = client.post("/token", data={"username": username, "password": password})
        assert resp.status_code == 200, resp.text
        token = resp.json()["access_token"]
        return token

    return _login


# ---------------------------
# HELPERS: AUTHORIZATION HEADER
# ---------------------------
# Convenience: obtain a Bearer token and build the Authorization header.
@pytest.fixture()
def auth_header(get_user_token):
    def _hdr(client, username: str, password: str):
        token = get_user_token(client, username, password)
        return {"Authorization": f"Bearer {token}"}

    return _hdr


# ---------------------------
# HELPERS: REGISTER DEVICE VIA API
# ---------------------------
# Calls POST /device with auth, expects a 201 and returns the response JSON (e.g. device_key).
@pytest.fixture()
def register_device():
    def _register(client, auth_header, name="sensor-1", device_type="thermometer"):
        resp = client.post("/device", json={"name": name, "device_type": device_type}, headers=auth_header)
        assert resp.status_code == 201, resp.text
        return resp.json()  # contains device_key

    return _register


