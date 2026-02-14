import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Add project root to sys.path so that "src" can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models import Base
from src.database import get_db
from src.dependencies import get_current_user


# Test database URL (matches docker-compose.test.yml)
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/shopping_test"


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine for the entire test session."""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create a new database session for each test function."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    yield session
    
    # Rollback any changes and close session
    session.rollback()
    session.close()
    
    # Clean up all data after each test
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
        session.commit()


@pytest.fixture(scope="function")
def mock_user():
    """Mock authenticated user data."""
    return {"sub": "test-user-123", "email": "test@example.com"}


@pytest.fixture(scope="function")
def client(db_session, mock_user):
    """Create a FastAPI TestClient with dependency overrides."""
    from src.main import app
    
    # Override database dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Override authentication dependency
    def override_get_current_user():
        return mock_user
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def unauthenticated_client(db_session):
    """Create a FastAPI TestClient without authentication."""
    from src.main import app
    
    # Override database dependency only
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear overrides
    app.dependency_overrides.clear()

