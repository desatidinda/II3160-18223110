import pytest
from uuid import uuid4


def get_token(api_client):
    username = f"user_{uuid4().hex[:8]}"
    
    api_client.post("/auth/register", json={
        "username": username,
        "password": "testpass",
        "peran": "PENGGUNA"
    })
    
    login_response = api_client.post("/auth/login", json={
        "username": username,
        "password": "testpass"
    })
    return login_response.json()["access_token"]


class TestUserCoverageImprovements:
    
    def test_add_vehicle_user_not_found(self, api_client):
        token = get_token(api_client)
        fake_user_id = str(uuid4())
        
        response = api_client.post(
            "/users/vehicle",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_id": fake_user_id,
                "plate": "B1234XYZ",
                "vehicle_type": "MOBIL"
            }
        )
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_get_user_not_found(self, api_client):
        token = get_token(api_client)
        fake_user_id = str(uuid4())
        
        response = api_client.get(
            f"/users/{fake_user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_delete_user_not_found(self, api_client):
        token = get_token(api_client)
        fake_user_id = str(uuid4())
        
        response = api_client.delete(
            f"/users/{fake_user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_delete_user_success(self, api_client):
        username = f"user_{uuid4().hex[:8]}"
        register_response = api_client.post("/auth/register", json={
            "username": username,
            "password": "testpass",
            "peran": "PENGGUNA"
        })
        user_id = register_response.json()["user_id"]
        
        token = get_token(api_client)
        
        response = api_client.delete(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"
    
    def test_get_user_with_vehicles(self, api_client):
        # Register user
        username = f"user_{uuid4().hex[:8]}"
        register_response = api_client.post("/auth/register", json={
            "username": username,
            "password": "testpass",
            "peran": "PENGGUNA"
        })
        user_id = register_response.json()["user_id"]
        
        login_response = api_client.post("/auth/login", json={
            "username": username,
            "password": "testpass"
        })
        token = login_response.json()["access_token"]
        
        api_client.post(
            "/users/vehicle",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_id": user_id,
                "plate": "B1234XYZ",
                "vehicle_type": "MOBIL"
            }
        )
        
        response = api_client.get(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["vehicles"]) == 1
        assert data["vehicles"][0]["plate"] == "B1234XYZ"
        assert "vehicle_type" in data["vehicles"][0]
