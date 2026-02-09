"""Pytest fixtures for API testing."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.repositories.unit_of_work import UnitOfWork, get_unit_of_work
from rest_server import app


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Enable foreign keys for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_unit_of_work():
    """Override UnitOfWork dependency for testing."""
    session = TestingSessionLocal()
    uow = UnitOfWork(session=session)
    return uow


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database."""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_unit_of_work] = override_get_unit_of_work
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_book_data():
    """Sample book data for testing."""
    return {
        "title": "Test Book",
        "author": "Test Author",
        "isbn": "978-0-123456-78-9",
        "publishedYear": 2024,
        "genre": "Fiction",
        "totalCopies": 5
    }


@pytest.fixture
def sample_member_data():
    """Sample member data for testing."""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "555-0100",
        "address": "123 Test Street"
    }


@pytest.fixture
def created_book(client, sample_book_data):
    """Create a book and return it."""
    response = client.post("/api/books", json=sample_book_data)
    return response.json()


@pytest.fixture
def created_member(client, sample_member_data):
    """Create a member and return it."""
    response = client.post("/api/members", json=sample_member_data)
    return response.json()
