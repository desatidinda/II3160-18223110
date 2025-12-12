import pytest
from fastapi.testclient import TestClient

from src.main import app


class TestAuthEndpoints:
    def test_register_pengguna(self, api_client):
        response = api_client.post(
            "/auth/register",
            json={
                "username": "pengguna1",
                "password": "password123",
                "email": "pengguna@example.com"
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["username"] == "pengguna1"
        assert data["email"] == "pengguna@example.com"
        assert data["peran"] == "PENGGUNA"
        assert "user_id" in data
    
    def test_register_duplicate_username(self, api_client):
        api_client.post(
            "/auth/register",
            json={
                "username": "duplicate",
                "password": "password123"
            }
        )
        
        response = api_client.post(
            "/auth/register",
            json={
                "username": "duplicate",
                "password": "password456"
            }
        )
        
        assert response.status_code == 400
        assert "sudah terdaftar" in response.json()["detail"]
    
    def test_register_admin(self, api_client):
        response = api_client.post(
            "/auth/register",
            json={
                "username": "admin1",
                "password": "adminpass",
                "email": "admin@example.com",
                "peran": "ADMIN"
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["peran"] == "ADMIN"
    
    def test_register_petugas(self, api_client):
        response = api_client.post(
            "/auth/register",
            json={
                "username": "petugas1",
                "password": "petugaspass",
                "email": "petugas@example.com",
                "peran": "PETUGAS"
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["peran"] == "PETUGAS"
    
    def test_login_success(self, api_client):
        api_client.post(
            "/auth/register",
            json={
                "username": "logintest",
                "password": "password123"
            }
        )
        
        response = api_client.post(
            "/auth/login",
            json={
                "username": "logintest",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_username(self, api_client):
        response = api_client.post(
            "/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
    
    def test_login_wrong_password(self, api_client):
        api_client.post(
            "/auth/register",
            json={
                "username": "wrongpass",
                "password": "correctpassword"
            }
        )
        
        response = api_client.post(
            "/auth/login",
            json={
                "username": "wrongpass",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
    
    def test_get_current_user_authenticated(self, api_client):
        api_client.post(
            "/auth/register",
            json={
                "username": "currentuser",
                "password": "password123"
            }
        )
        
        login_response = api_client.post(
            "/auth/login",
            json={
                "username": "currentuser",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        
        response = api_client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "currentuser"
    
    def test_get_current_user_unauthenticated(self, api_client):
        response = api_client.get("/auth/me")
        assert response.status_code == 403
    
    def test_get_current_user_invalid_token(self, api_client):
        response = api_client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


def get_admin_token(api_client):
    api_client.post(
        "/auth/register",
        json={
            "username": "admin_test",
            "password": "adminpass",
            "peran": "ADMIN"
        }
    )
    response = api_client.post(
        "/auth/login",
        json={
            "username": "admin_test",
            "password": "adminpass"
        }
    )
    return response.json()["access_token"]


def get_petugas_token(api_client):
    api_client.post(
        "/auth/register",
        json={
            "username": "petugas_test",
            "password": "petugaspass",
            "peran": "PETUGAS"
        }
    )
    response = api_client.post(
        "/auth/login",
        json={
            "username": "petugas_test",
            "password": "petugaspass"
        }
    )
    return response.json()["access_token"]


def get_pengguna_token(api_client):
    api_client.post(
        "/auth/register",
        json={
            "username": "pengguna_test",
            "password": "penggunapass",
            "peran": "PENGGUNA"
        }
    )
    response = api_client.post(
        "/auth/login",
        json={
            "username": "pengguna_test",
            "password": "penggunapass"
        }
    )
    return response.json()["access_token"]

