import asyncio
import os
import pathlib
import pytest


# Ensure an event loop exists for async tests (pytest-asyncio default mode is auto in recent versions)
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db_url(tmp_path_factory):
    # Use a file-based SQLite DB to persist across connections during tests
    db_dir = tmp_path_factory.mktemp("db")
    db_path = db_dir / "test_iot_device_hub.db"
    return f"sqlite+aiosqlite:///{db_path}"


@pytest.fixture(scope="session", autouse=True)
def set_test_env(test_db_url):
    # Minimal secrets for JWT
    os.environ["API_SECRET_KEY"] = "test-secret-key"
    os.environ["API_ALGORITHM"] = "HS256"
    # Point the app's DB to our sqlite test database
    os.environ["DATABASE_URL"] = test_db_url
    # Keep MQTT off localhost connection attempts where possible
    os.environ["MQTT_BROKER_URL"] = "localhost"


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


@pytest.fixture()
def client(app_instance):
    # Use FastAPI's TestClient to handle startup/shutdown automatically
    from fastapi.testclient import TestClient

    with TestClient(app_instance) as c:
        yield c


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


@pytest.fixture()
def create_user():
    # Helper to create a user via the API to ensure consistent hashing and side-effects
    def _create(client, username="alice", email="alice@example.com", password="secret123"):
        payload = {"username": username, "email": email, "password": password}
        resp = client.post("/user", json=payload)
        assert resp.status_code == 201, resp.text
        return {"username": username, "email": email, "password": password, "user": resp.json()}

    return _create


@pytest.fixture()
def get_user_token():
    def _login(client, username: str, password: str) -> str:
        # OAuth2PasswordRequestForm requires form-encoded body
        resp = client.post("/token", data={"username": username, "password": password})
        assert resp.status_code == 200, resp.text
        token = resp.json()["access_token"]
        return token

    return _login


@pytest.fixture()
def auth_header(get_user_token):
    def _hdr(client, username: str, password: str):
        token = get_user_token(client, username, password)
        return {"Authorization": f"Bearer {token}"}

    return _hdr


@pytest.fixture()
def register_device():
    def _register(client, auth_header, name="sensor-1", device_type="thermometer"):
        resp = client.post("/device", json={"name": name, "device_type": device_type}, headers=auth_header)
        assert resp.status_code == 201, resp.text
        return resp.json()  # contains device_key

    return _register


