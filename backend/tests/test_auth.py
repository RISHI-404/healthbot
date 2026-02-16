"""
Tests for authentication endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Test successful user registration."""
    response = await client.post("/api/auth/register", json={
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "securepass123",
        "role": "PATIENT",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert data["role"] == "PATIENT"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test that duplicate email registration fails."""
    payload = {
        "email": "dupe@example.com",
        "full_name": "User One",
        "password": "securepass123",
        "role": "PATIENT",
    }
    await client.post("/api/auth/register", json=payload)
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login returns tokens."""
    await client.post("/api/auth/register", json={
        "email": "login@example.com",
        "full_name": "Login User",
        "password": "securepass123",
        "role": "PATIENT",
    })
    response = await client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "securepass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Test login with wrong password fails."""
    await client.post("/api/auth/register", json={
        "email": "wrong@example.com",
        "full_name": "Wrong User",
        "password": "securepass123",
        "role": "PATIENT",
    })
    response = await client.post("/api/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile(client: AsyncClient):
    """Test getting user profile with valid token."""
    await client.post("/api/auth/register", json={
        "email": "profile@example.com",
        "full_name": "Profile User",
        "password": "securepass123",
        "role": "PATIENT",
    })
    login_res = await client.post("/api/auth/login", json={
        "email": "profile@example.com",
        "password": "securepass123",
    })
    token = login_res.json()["access_token"]
    response = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "profile@example.com"


@pytest.mark.asyncio
async def test_get_profile_no_token(client: AsyncClient):
    """Test that profile endpoint requires auth."""
    response = await client.get("/api/auth/me")
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_consent(client: AsyncClient):
    """Test accepting consent."""
    await client.post("/api/auth/register", json={
        "email": "consent@example.com",
        "full_name": "Consent User",
        "password": "securepass123",
        "role": "PATIENT",
    })
    login_res = await client.post("/api/auth/login", json={
        "email": "consent@example.com",
        "password": "securepass123",
    })
    token = login_res.json()["access_token"]
    response = await client.post(
        "/api/auth/consent",
        json={"accepted": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
