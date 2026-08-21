import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

from app.core.db import engine, get_db
from app.main import app

TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture()
def db_session():
    """Each test runs inside its own outer transaction, rolled back afterwards
    so tests never see each other's data. The app calls `db.commit()` as part
    of normal request handling, so we run the session on a SAVEPOINT that gets
    restarted after each commit (the standard SQLAlchemy test-isolation
    recipe), keeping the outer transaction alive until the final rollback.

    Schema/extensions are set up by `alembic upgrade head` before the test
    run, not by this fixture.
    """
    connection = engine.connect()
    outer_transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    outer_transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    def _signup(email: str, password: str = "secret123") -> dict:
        response = client.post(
            "/users/signup",
            json={"name": "Test", "last_name": "User", "email": email, "password": password},
        )
        assert response.status_code == 201, response.text
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _signup
