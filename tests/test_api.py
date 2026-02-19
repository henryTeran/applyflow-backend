"""
Comprehensive test suite for ApplyFlow API.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base
from app.api.deps import get_db

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create test client with fresh database."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_headers(client):
    """Create authenticated user and return auth headers."""
    # Register user
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword123"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Login
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# Authentication Tests
# ============================================================================

def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "name": "New User",
            "password": "securepassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["name"] == "New User"
    assert "id" in data


def test_register_duplicate_email(client):
    """Test that duplicate email registration fails."""
    user_data = {
        "email": "duplicate@example.com",
        "name": "User One",
        "password": "password123"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Try to register same email again
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client):
    """Test successful login."""
    # Register user
    user_data = {
        "email": "login@example.com",
        "name": "Login User",
        "password": "loginpass123"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """Test login with wrong password."""
    # Register user
    user_data = {
        "email": "wrongpass@example.com",
        "name": "Wrong Pass",
        "password": "correctpass"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Try login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": user_data["email"],
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_get_current_user(client, auth_headers):
    """Test getting current user info."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"


# ============================================================================
# Job Offer Tests
# ============================================================================

def test_create_job_offer(client, auth_headers):
    """Test creating a job offer."""
    job_data = {
        "title": "Senior Python Developer",
        "company": "TechCorp",
        "location": "Geneva, Switzerland",
        "source": "LinkedIn",
        "url": "https://linkedin.com/jobs/123",
        "application_type": "email",
        "raw_description": "We are looking for a Senior Python Developer..."
    }
    response = client.post(
        "/api/v1/job-offers/",
        json=job_data,
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == job_data["title"]
    assert data["company"] == job_data["company"]
    assert "id" in data


def test_list_job_offers(client, auth_headers):
    """Test listing job offers."""
    # Create a few job offers
    for i in range(3):
        client.post(
            "/api/v1/job-offers/",
            json={
                "title": f"Job {i}",
                "company": f"Company {i}",
                "location": "Remote",
                "source": "LinkedIn",
                "raw_description": "Description"
            },
            headers=auth_headers
        )
    
    response = client.get("/api/v1/job-offers/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_get_job_offer(client, auth_headers):
    """Test getting a specific job offer."""
    # Create job offer
    create_response = client.post(
        "/api/v1/job-offers/",
        json={
            "title": "Backend Developer",
            "company": "StartupCo",
            "location": "Zurich",
            "source": "Website",
            "raw_description": "Backend role"
        },
        headers=auth_headers
    )
    job_id = create_response.json()["id"]
    
    # Get job offer
    response = client.get(f"/api/v1/job-offers/{job_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job_id
    assert data["title"] == "Backend Developer"


def test_update_job_offer(client, auth_headers):
    """Test updating a job offer."""
    # Create job offer
    create_response = client.post(
        "/api/v1/job-offers/",
        json={
            "title": "DevOps Engineer",
            "company": "CloudCo",
            "location": "Remote",
            "source": "LinkedIn",
            "raw_description": "DevOps role"
        },
        headers=auth_headers
    )
    job_id = create_response.json()["id"]
    
    # Update job offer
    response = client.patch(
        f"/api/v1/job-offers/{job_id}",
        json={"title": "Senior DevOps Engineer"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Senior DevOps Engineer"


def test_delete_job_offer(client, auth_headers):
    """Test deleting a job offer."""
    # Create job offer
    create_response = client.post(
        "/api/v1/job-offers/",
        json={
            "title": "Test Job",
            "company": "TestCo",
            "location": "Remote",
            "source": "LinkedIn",
            "raw_description": "Test"
        },
        headers=auth_headers
    )
    job_id = create_response.json()["id"]
    
    # Delete job offer
    response = client.delete(f"/api/v1/job-offers/{job_id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/v1/job-offers/{job_id}", headers=auth_headers)
    assert get_response.status_code == 404


# ============================================================================
# Application Tests
# ============================================================================

def test_create_application(client, auth_headers):
    """Test creating an application."""
    # First create a job offer
    job_response = client.post(
        "/api/v1/job-offers/",
        json={
            "title": "Frontend Developer",
            "company": "WebCo",
            "location": "Lausanne",
            "source": "Indeed",
            "raw_description": "Frontend role"
        },
        headers=auth_headers
    )
    job_id = job_response.json()["id"]
    
    # Create application
    app_data = {
        "job_offer_id": job_id,
        "channel": "email",
        "submitted_by": "manual",
        "status": "sent"
    }
    response = client.post(
        "/api/v1/applications/",
        json=app_data,
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["job_offer_id"] == job_id
    assert data["status"] == "sent"


def test_update_application_status(client, auth_headers):
    """Test updating application status."""
    # Create job offer and application
    job_response = client.post(
        "/api/v1/job-offers/",
        json={
            "title": "Data Scientist",
            "company": "DataCo",
            "location": "Basel",
            "source": "LinkedIn",
            "raw_description": "Data science role"
        },
        headers=auth_headers
    )
    job_id = job_response.json()["id"]
    
    app_response = client.post(
        "/api/v1/applications/",
        json={
            "job_offer_id": job_id,
            "channel": "portal",
            "submitted_by": "manual",
            "status": "sent"
        },
        headers=auth_headers
    )
    app_id = app_response.json()["id"]
    
    # Update status
    response = client.patch(
        f"/api/v1/applications/{app_id}/status",
        json={"status": "interview"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "interview"


# ============================================================================
# Health Check Tests
# ============================================================================

def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_ping_endpoint(client):
    """Test ping health check."""
    response = client.get("/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "pong"


def test_health_endpoint(client):
    """Test detailed health check."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app" in data
    assert "version" in data
