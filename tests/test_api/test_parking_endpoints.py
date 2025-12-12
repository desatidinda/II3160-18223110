import pytest
from fastapi.testclient import TestClient

from src.main import app


def get_petugas_token(api_client):
    import uuid
    username = f"petugas_{uuid.uuid4().hex[:8]}"
    
    api_client.post("/auth/register", json={
        "username": username,
        "password": "petugaspass",
        "peran": "PETUGAS"
    })
    
    login_response = api_client.post("/auth/login", json={
        "username": username,
        "password": "petugaspass"
    })
    return login_response.json()["access_token"]


def get_pengguna_token_and_data(api_client):
    import uuid
    username = f"parking_user_{uuid.uuid4().hex[:8]}"
    
    register_response = api_client.post("/auth/register", json={
        "username": username,
        "password": "testpass",
        "peran": "PENGGUNA"
    })
    
    register_data = register_response.json()
    user_id = register_data["user_id"]
    
    login_response = api_client.post("/auth/login", json={
        "username": username,
        "password": "testpass"
    })
    token = login_response.json()["access_token"]
    
    # Add vehicle
    vehicle_response = api_client.post(
        "/users/vehicle",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_id": user_id,
            "plate": "B1234XYZ",
            "vehicle_type": "Motor"
        }
    )
    
    vehicle_id = vehicle_response.json()["vehicle_id"]
    
    return token, user_id, vehicle_id


def create_available_slot(api_client):
    petugas_token = get_petugas_token(api_client)
    slot_response = api_client.post(
        "/slots/",
        headers={"Authorization": f"Bearer {petugas_token}"},
        json={
            "lantai": 1,
            "posisi_x": 10.0,
            "posisi_y": 20.0
        }
    )
    return slot_response.json()["id"]


class TestParkingEndpoints:
    def test_check_in_success(self, api_client):
        token, user_id, vehicle_id = get_pengguna_token_and_data(api_client)
        slot_id = create_available_slot(api_client)
        
        response = api_client.post(
            "/parking/check-in",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vehicle_id": vehicle_id,
                "slot_id": slot_id
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["plate"] == "B1234XYZ"
        assert data["vehicle_id"] == vehicle_id
        assert data["status"] == "AKTIF"
        assert data["checkin_time"] is not None
        assert data["checkout_time"] is None
    
    def test_check_in_without_slot(self, api_client):
        token, user_id, vehicle_id = get_pengguna_token_and_data(api_client)
        
        response = api_client.post(
            "/parking/check-in",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vehicle_id": vehicle_id
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["vehicle_id"] == vehicle_id
        assert data["status"] == "AKTIF"
    
    def test_check_in_vehicle_not_found(self, api_client):
        import uuid
        token, user_id, vehicle_id = get_pengguna_token_and_data(api_client)
        
        response = api_client.post(
            "/parking/check-in",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vehicle_id": str(uuid.uuid4())
            }
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_check_in_slot_not_found(self, api_client):
        import uuid
        token, user_id, vehicle_id = get_pengguna_token_and_data(api_client)
        
        response = api_client.post(
            "/parking/check-in",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vehicle_id": vehicle_id,
                "slot_id": str(uuid.uuid4())
            }
        )
        
        assert response.status_code == 404
        assert "Slot" in response.json()["detail"]
    
    def test_check_in_slot_not_available(self, api_client):
        token, user_id, vehicle_id = get_pengguna_token_and_data(api_client)
        slot_id = create_available_slot(api_client)
        
        petugas_token = get_petugas_token(api_client)
        api_client.patch(
            f"/slots/{slot_id}/status",
            headers={"Authorization": f"Bearer {petugas_token}"},
            json={"status": "TERISI"}
        )
        
        response = api_client.post(
            "/parking/check-in",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vehicle_id": vehicle_id,
                "slot_id": slot_id
            }
        )
        
        assert response.status_code == 400
        assert "tidak tersedia" in response.json()["detail"]
    
    def test_check_out_success(self, api_client):
        token, user_id, vehicle_id = get_pengguna_token_and_data(api_client)
        slot_id = create_available_slot(api_client)
        
        # Check in
        checkin_response = api_client.post(
            "/parking/check-in",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vehicle_id": vehicle_id,
                "slot_id": slot_id
            }
        )
        session_id = checkin_response.json()["id"]
        
        # Check out
        response = api_client.post(
            f"/parking/check-out/{session_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SELESAI"
        assert data["checkout_time"] is not None
        assert data["final_fee"] is not None
    
    def test_check_out_with_slot_id(self, api_client):
        token, user_id, vehicle_id = get_pengguna_token_and_data(api_client)
        slot_id = create_available_slot(api_client)
        
        # Check in
        checkin_response = api_client.post(
            "/parking/check-in",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vehicle_id": vehicle_id,
                "slot_id": slot_id
            }
        )
        session_id = checkin_response.json()["id"]
        
        # Check out with slot_id
        response = api_client.post(
            f"/parking/check-out/{session_id}?slot_id={slot_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SELESAI"
    
    def test_check_out_session_not_found(self, api_client):
        import uuid
        token, user_id, vehicle_id = get_pengguna_token_and_data(api_client)
        
        response = api_client.post(
            f"/parking/check-out/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
    
    def test_get_session(self, api_client):
        token, user_id, vehicle_id = get_pengguna_token_and_data(api_client)
        
        # Check in
        checkin_response = api_client.post(
            "/parking/check-in",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "vehicle_id": vehicle_id
            }
        )
        session_id = checkin_response.json()["id"]
        
        # Get session
        response = api_client.get(
            f"/parking/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["vehicle_id"] == vehicle_id
    
    def test_get_session_not_found(self, api_client):
        import uuid
        token, user_id, vehicle_id = get_pengguna_token_and_data(api_client)
        
        response = api_client.get(
            f"/parking/sessions/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
    
    def test_list_sessions(self, api_client):
        token, user_id, vehicle_id = get_pengguna_token_and_data(api_client)
        
        # Create multiple sessions
        for i in range(3):
            api_client.post(
                "/parking/check-in",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "vehicle_id": vehicle_id
                }
            )
        
        # List sessions
        response = api_client.get(
            "/parking/sessions",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
    
    def test_check_in_without_auth(self, api_client):
        response = api_client.post(
            "/parking/check-in",
            json={
                "vehicle_id": "fb46d318-5a6a-4be9-8769-2cb904cc7fbf"
            }
        )
        
        assert response.status_code in [401, 403]


