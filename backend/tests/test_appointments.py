"""
Tests for appointment CRUD endpoints.
"""
import pytest
from httpx import AsyncClient


async def get_patient_token(client: AsyncClient) -> str:
    """Helper: register + login + consent → return token."""
    await client.post("/api/auth/register", json={
        "email": "appt@example.com",
        "full_name": "Appt User",
        "password": "securepass123",
        "role": "PATIENT",
    })
    login = await client.post("/api/auth/login", json={
        "email": "appt@example.com",
        "password": "securepass123",
    })
    token = login.json()["access_token"]
    await client.post(
        "/api/auth/consent",
        json={"accepted": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    return token


@pytest.mark.asyncio
async def test_create_appointment(client: AsyncClient):
    token = await get_patient_token(client)
    response = await client.post(
        "/api/appointments/",
        json={
            "title": "Checkup",
            "doctor_name": "Dr. Smith",
            "scheduled_at": "2025-06-15T10:00:00",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Checkup"
    assert data["doctor_name"] == "Dr. Smith"


@pytest.mark.asyncio
async def test_list_appointments(client: AsyncClient):
    token = await get_patient_token(client)
    # Create one appointment
    await client.post(
        "/api/appointments/",
        json={"title": "Visit", "scheduled_at": "2025-07-01T09:00:00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    response = await client.get(
        "/api/appointments/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_delete_appointment(client: AsyncClient):
    token = await get_patient_token(client)
    create_res = await client.post(
        "/api/appointments/",
        json={"title": "Delete Me", "scheduled_at": "2025-08-01T09:00:00"},
        headers={"Authorization": f"Bearer {token}"},
    )
    appt_id = create_res.json()["id"]
    delete_res = await client.delete(
        f"/api/appointments/{appt_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_res.status_code == 200


@pytest.mark.asyncio
async def test_appointments_require_auth(client: AsyncClient):
    response = await client.get("/api/appointments/")
    assert response.status_code in [401, 403]
