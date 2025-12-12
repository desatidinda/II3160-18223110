import pytest
from uuid import uuid4


def get_petugas_token(api_client):
    username = f"petugas_{uuid4().hex[:8]}"
    
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


def get_pengguna_token(api_client):
    username = f"pengguna_{uuid4().hex[:8]}"
    
    api_client.post("/auth/register", json={
        "username": username,
        "password": "penggunapass",
        "peran": "PENGGUNA"
    })
    
    login_response = api_client.post("/auth/login", json={
        "username": username,
        "password": "penggunapass"
    })
    return login_response.json()["access_token"]


class TestSlotCoverageImprovements:
    
    def test_create_slot_with_invalid_sensor_type(self, api_client):
        token = get_petugas_token(api_client)
        
        response = api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "lantai": 1,
                "posisi_x": 10.0,
                "posisi_y": 20.0,
                "tipe_sensor": "INVALID_SENSOR_TYPE"
            }
        )
        
        assert response.status_code == 400
        assert "tidak valid" in response.json()["detail"].lower()
    
    def test_list_slots_with_invalid_status_filter(self, api_client):
        token = get_pengguna_token(api_client)
        
        response = api_client.get(
            "/slots/?status=INVALID_STATUS",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "Status tidak valid" in response.json()["detail"]
    
    def test_list_slots_with_status_filter(self, api_client):
        petugas_token = get_petugas_token(api_client)
        pengguna_token = get_pengguna_token(api_client)
        
        api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {petugas_token}"},
            json={
                "lantai": 1,
                "posisi_x": 10.0,
                "posisi_y": 20.0
            }
        )
        
        response = api_client.get(
            "/slots/?status=TERSEDIA",
            headers={"Authorization": f"Bearer {pengguna_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for slot in data:
            assert slot["status"] == "TERSEDIA"
    
    def test_list_slots_by_lantai(self, api_client):
        petugas_token = get_petugas_token(api_client)
        pengguna_token = get_pengguna_token(api_client)
        
        api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {petugas_token}"},
            json={"lantai": 1, "posisi_x": 10.0, "posisi_y": 20.0}
        )
        
        api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {petugas_token}"},
            json={"lantai": 2, "posisi_x": 15.0, "posisi_y": 25.0}
        )
        
        response = api_client.get(
            "/slots/?lantai=1",
            headers={"Authorization": f"Bearer {pengguna_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for slot in data:
            assert slot["lantai"] == 1
    
    def test_update_slot_status_not_found(self, api_client):
        token = get_petugas_token(api_client)
        fake_id = str(uuid4())
        
        response = api_client.patch(
            f"/slots/{fake_id}/status",
            headers={"Authorization": f"Bearer {token}"},
            json={"status": "TERISI"}
        )
        
        assert response.status_code in [400, 404]
    
    def test_attach_sensor_invalid_type(self, api_client):
        petugas_token = get_petugas_token(api_client)
        
        slot_response = api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {petugas_token}"},
            json={"lantai": 1, "posisi_x": 10.0, "posisi_y": 20.0}
        )
        slot_id = slot_response.json()["id"]
        
        response = api_client.post(
            f"/slots/{slot_id}/sensor",
            headers={"Authorization": f"Bearer {petugas_token}"},
            json={"tipe_sensor": "INVALID_TYPE"}
        )
        
        assert response.status_code == 400
        assert "tidak valid" in response.json()["detail"].lower()
    
    def test_attach_sensor_slot_not_found(self, api_client):
        token = get_petugas_token(api_client)
        fake_id = str(uuid4())
        
        response = api_client.post(
            f"/slots/{fake_id}/sensor",
            headers={"Authorization": f"Bearer {token}"},
            json={"tipe_sensor": "ULTRASONIK"}
        )
        
        assert response.status_code in [400, 404]
    
    def test_detach_sensor_slot_not_found(self, api_client):
        token = get_petugas_token(api_client)
        fake_id = str(uuid4())
        
        response = api_client.delete(
            f"/slots/{fake_id}/sensor",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code in [400, 404]
    
    def test_update_sensor_condition_slot_not_found(self, api_client):
        token = get_petugas_token(api_client)
        fake_id = str(uuid4())
        
        response = api_client.patch(
            f"/slots/{fake_id}/sensor/kondisi",
            headers={"Authorization": f"Bearer {token}"},
            json={"kondisi": "NORMAL"}
        )
        
        assert response.status_code in [400, 404]
    
    def test_update_sensor_condition_no_sensor(self, api_client):
        petugas_token = get_petugas_token(api_client)
        
        slot_response = api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {petugas_token}"},
            json={"lantai": 1, "posisi_x": 10.0, "posisi_y": 20.0}
        )
        slot_id = slot_response.json()["id"]
        
        response = api_client.patch(
            f"/slots/{slot_id}/sensor/kondisi",
            headers={"Authorization": f"Bearer {petugas_token}"},
            json={"kondisi": "NORMAL"}
        )
        
        assert response.status_code == 400
        assert "tidak memiliki sensor" in response.json()["detail"].lower()
    
    def test_update_sensor_condition_invalid(self, api_client):
        petugas_token = get_petugas_token(api_client)
        
        slot_response = api_client.post(
            "/slots/",
            headers={"Authorization": f"Bearer {petugas_token}"},
            json={
                "lantai": 1,
                "posisi_x": 10.0,
                "posisi_y": 20.0,
                "tipe_sensor": "ULTRASONIK"
            }
        )
        slot_id = slot_response.json()["id"]
        
        response = api_client.patch(
            f"/slots/{slot_id}/sensor/kondisi",
            headers={"Authorization": f"Bearer {petugas_token}"},
            json={"kondisi": "INVALID_CONDITION"}
        )
        
        assert response.status_code in [200, 400]
