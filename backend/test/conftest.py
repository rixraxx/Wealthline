import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Alias app to avoid package shadowing
from app.main import app as fastapi_app
from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash

# Import models package to register all ORM models with Base.metadata
import app.models
from app.models.user import User

# In-memory SQLite DB for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Create all database tables before each test and tear down after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    """Provides an isolated database session per test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def override_get_db(db):
    """Override FastAPI's get_db dependency to point to the test SQLite database."""
    def _override():
        try:
            yield db
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = _override
    yield
    fastapi_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db) -> User:
    """Inserts a default active user into the test database."""
    user = User(
        email="testuser@wealthline.io",
        hashed_password=get_password_hash("TestPassword123!"),
        full_name="Test User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user: User) -> dict:
    """Generates a valid Bearer JWT header for authenticated API tests."""
    access_token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(scope="function")
def client(override_get_db) -> TestClient:
    """FastAPI TestClient fixture."""
    return TestClient(app=fastapi_app)