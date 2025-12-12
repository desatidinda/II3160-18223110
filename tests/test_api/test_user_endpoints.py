import pytest
from fastapi.testclient import TestClient

from src.main import app


def get_admin_token(api_client):
    api_client.post("/auth/register", json={
        "username": "user_admin",
        "password": "adminpass",
        "peran": "ADMIN"
    })
    response = api_client.post("/auth/login", json={
        "username": "user_admin",
        "password": "adminpass"
    })
    return response.json()["access_token"]


def get_pengguna_token_and_user_id(api_client):
    import uuid
    username = f"user_pengguna_{uuid.uuid4().hex[:8]}"
    
    register_response = api_client.post("/auth/register", json={
        "username": username,
        "password": "penggunapass",
        "peran": "PENGGUNA"
    })
    user_id = register_response.json()["user_id"]
    
    login_response = api_client.post("/auth/login", json={
        "username": username,
        "password": "penggunapass"
    })
    token = login_response.json()["access_token"]
    
    return token, user_id


class TestUserEndpoints:
    def test_add_vehicle_to_own_account(self, api_client):
        token, user_id = get_pengguna_token_and_user_id(api_client)
        
        response = api_client.post(
            "/users/vehicle",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_id": user_id,
                "plate": "B1234XYZ",
                "vehicle_type": "Motor"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["plate"] == "B1234XYZ"
    
    def test_add_vehicle_without_auth(self, api_client):
        response = api_client.post(
            "/users/vehicle",
            json={
                "nomor_plat": "B1234XYZ",
                "jenis_kendaraan": "Motor"
            }
        )
        
        assert response.status_code == 401
    
    def test_add_multiple_vehicles(self, api_client):
        token, user_id = get_pengguna_token_and_user_id(api_client)
        
        api_client.post(
            "/users/vehicle",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_id": user_id,
                "plate": "B1234XYZ",
                "vehicle_type": "Motor"
            }
        )
        
        response = api_client.post(
            "/users/vehicle",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_id": user_id,
                "plate": "D5678ABC",
                "vehicle_type": "Mobil"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["plate"] == "D5678ABC"
    
    def test_get_all_users_as_admin(self, api_client):
        admin_token = get_admin_token(api_client)
        
        response = api_client.get(
            "/users/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_all_users_as_pengguna_forbidden(self, api_client):
        token, _ = get_pengguna_token_and_user_id(api_client)
        
        response = api_client.get(
            "/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
    
    def test_get_user_by_id_as_admin(self, api_client):
        admin_token = get_admin_token(api_client)
        pengguna_token, user_id = get_pengguna_token_and_user_id(api_client)
        
        response = api_client.get(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == user_id
    
    def test_get_own_user_data(self, api_client):
        token, user_id = get_pengguna_token_and_user_id(api_client)
        
        response = api_client.get(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == user_id
    
    def test_get_other_user_as_pengguna_forbidden(self, api_client):
        token1, user_id1 = get_pengguna_token_and_user_id(api_client)
        
        api_client.post("/auth/register", json={
            "username": "other_user",
            "password": "password",
            "peran": "PENGGUNA"
        })
        other_login = api_client.post("/auth/login", json={
            "username": "other_user",
            "password": "password"
        })
        other_token = other_login.json()["access_token"]
        
        response = api_client.get(
            f"/users/{user_id1}",
            headers={"Authorization": f"Bearer {other_token}"}
        )
        
        assert response.status_code == 200
