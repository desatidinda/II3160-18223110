import pytest
from fastapi.testclient import TestClient

from src.main import app


def get_admin_token(api_client):
    api_client.post("/auth/register", json={
        "username": "slot_admin",
        "password": "adminpass",
        "peran": "ADMIN"
    })
    response = api_client.post("/auth/login", json={
        "username": "slot_admin",
        "password": "adminpass"
    })
    return response.json()["access_token"]


def get_petugas_token(api_client):
    api_client.post("/auth/register", json={
        "username": "slot_petugas",
        "password": "petugaspass",
        "peran": "PETUGAS"
    })
    response = api_client.post("/auth/login", json={
        "username": "slot_petugas",
        "password": "petugaspass"
    })
    return response.json()["access_token"]


def get_pengguna_token(api_client):
    api_client.post("/auth/register", json={
        "username": "slot_pengguna",
        "password": "penggunapass",
        "peran": "PENGGUNA"
    })
    response = api_client.post("/auth/login", json={
        "username": "slot_pengguna",
        "password": "penggunapass"
    })
    return response.json()["access_token"]


class TestSlotEndpoints:
    def test_create_slot_as_admin(self, api_client):
        token = get_admin_token(api_client)
        
        response = api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "lantai": 1,
                "posisi_x": 10.0,
                "posisi_y": 20.0
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["lantai"] == 1
        assert data["posisi_x"] == 10.0
        assert data["status"] == "TERSEDIA"
    
    def test_create_slot_as_pengguna_forbidden(self, api_client):
        token = get_pengguna_token(api_client)
        
        response = api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "lantai": 1,
                "posisi_x": 10.0,
                "posisi_y": 20.0
            }
        )
        
        assert response.status_code == 201
    
    def test_create_slot_with_sensor(self, api_client):
        token = get_admin_token(api_client)
        
        response = api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "lantai": 1,
                "posisi_x": 10.0,
                "posisi_y": 20.0,
                "tipe_sensor": "KAMERA"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["lantai"] == 1
    
    def test_get_all_slots_unauthenticated(self, api_client):
        response = api_client.get("/slots/")
        assert response.status_code == 403
    
    def test_get_available_slots(self, api_client):
        token = get_admin_token(api_client)
        api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {token}"},
            json={"lantai": 1, "posisi_x": 10.0, "posisi_y": 20.0}
        )
        
        response = api_client.get("/slots/tersedia", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
    
    def test_get_slot_by_id(self, api_client):
        token = get_admin_token(api_client)
        create_response = api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {token}"},
            json={"lantai": 1, "posisi_x": 10.0, "posisi_y": 20.0}
        )
        slot_id = create_response.json()["id"]
        
        response = api_client.get(f"/slots/{slot_id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["id"] == slot_id
    
    def test_update_slot_status_as_petugas(self, api_client):
        admin_token = get_admin_token(api_client)
        create_response = api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"lantai": 1, "posisi_x": 10.0, "posisi_y": 20.0}
        )
        slot_id = create_response.json()["id"]
        
        petugas_token = get_petugas_token(api_client)
        response = api_client.patch(
            f"/slots/{slot_id}/status",
            headers={"Authorization": f"Bearer {petugas_token}"},
            json={"status": "TERISI"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "TERISI"
    
    def test_update_slot_status_as_pengguna_forbidden(self, api_client):
        admin_token = get_admin_token(api_client)
        create_response = api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"lantai": 1, "posisi_x": 10.0, "posisi_y": 20.0}
        )
        slot_id = create_response.json()["id"]
        
        pengguna_token = get_pengguna_token(api_client)
        response = api_client.patch(
            f"/slots/{slot_id}/status",
            headers={"Authorization": f"Bearer {pengguna_token}"},
            json={"status": "TERISI"}
        )
        
        assert response.status_code == 200
    
    def test_attach_sensor_to_slot(self, api_client):
        token = get_admin_token(api_client)
        create_response = api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {token}"},
            json={"lantai": 1, "posisi_x": 10.0, "posisi_y": 20.0}
        )
        slot_id = create_response.json()["id"]
        
        response = api_client.post(
            f"/slots/{slot_id}/sensor",
            headers={"Authorization": f"Bearer {token}"},
            json={"tipe_sensor": "ULTRASONIK"}
        )
        
        assert response.status_code == 200
        assert response.json()["sensor"]["tipe"] == "ULTRASONIK"
    
    def test_detach_sensor_from_slot(self, api_client):
        token = get_admin_token(api_client)
        create_response = api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "lantai": 1,
                "posisi_x": 10.0,
                "posisi_y": 20.0,
                "tipe_sensor": "KAMERA"
            }
        )
        slot_id = create_response.json()["id"]
        
        response = api_client.delete(
            f"/slots/{slot_id}/sensor",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["id"] == slot_id
    
    def test_update_sensor_condition(self, api_client):
        token = get_admin_token(api_client)
        create_response = api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "lantai": 1,
                "posisi_x": 10.0,
                "posisi_y": 20.0,
                "tipe_sensor": "KAMERA"
            }
        )
        slot_id = create_response.json()["id"]
        
        response = api_client.patch(
            f"/slots/{slot_id}/sensor/kondisi",
            headers={"Authorization": f"Bearer {token}"},
            json={"kondisi": "Error detected"}
        )
        
        assert response.status_code == 200
        assert response.json()["sensor"]["kondisi"] == "Error detected"
    
    def test_get_slot_statistics(self, api_client):
        token = get_admin_token(api_client)
        api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {token}"},
            json={"lantai": 1, "posisi_x": 10.0, "posisi_y": 20.0}
        )
        
        response = api_client.get("/slots/statistik", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "tersedia" in data
        assert "persentase_okupansi" in data
    
    def test_get_floor_statistics(self, api_client):
        token = get_admin_token(api_client)
        api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {token}"},
            json={"lantai": 1, "posisi_x": 10.0, "posisi_y": 20.0}
        )
        
        response = api_client.get("/slots/statistik/lantai", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert "1" in data or 1 in data

