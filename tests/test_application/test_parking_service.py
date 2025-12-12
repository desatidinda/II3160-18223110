import pytest
from datetime import datetime
from uuid import uuid4

from manajemen_parkir.domain.auth import Peran
from manajemen_parkir.domain.alokasi_slot import StatusSlot
from manajemen_parkir.infrastructure.auth_repository import InMemoryAuthRepository
from manajemen_parkir.infrastructure.user_repository import InMemoryUserRepository
from manajemen_parkir.infrastructure.slot_repository import InMemorySlotParkirRepository
from manajemen_parkir.infrastructure.repository import InMemorySesiParkirRepository
from manajemen_parkir.application.services import ParkingService, AuthService
from manajemen_parkir.application.slot_service import SlotParkirService


class TestParkingService:
    def setup_method(self):
        self.auth_repo = InMemoryAuthRepository()
        self.user_repo = InMemoryUserRepository()
        self.slot_repo = InMemorySlotParkirRepository()
        self.sesi_repo = InMemorySesiParkirRepository()
        
        self.auth_service = AuthService(self.auth_repo, self.user_repo)
        self.slot_service = SlotParkirService(self.slot_repo)
        self.parking_service = ParkingService(
            self.sesi_repo,
            self.user_repo,
            self.slot_repo
        )
        
        self.akun, self.user = self.auth_service.register(
            "testuser",
            "password",
            peran=Peran.PENGGUNA
        )
        self.user.add_vehicle("B1234XYZ", "Motor", "Yamaha", "NMAX")
        self.user_repo.save(self.user)
        
        self.slot = self.slot_service.buat_slot(lantai=1, posisi_x=10.0, posisi_y=20.0)
    
    def test_start_parking_success(self):
        sesi = self.parking_service.start_parking(
            user_id=self.user.id,
            vehicle_id=self.user.vehicles[0].id,
            slot_id=self.slot.id
        )
        
        assert sesi.owner_id == self.user.id
        assert sesi.vehicle_id == self.user.vehicles[0].id
        assert sesi.slot_id == self.slot.id
        assert sesi.waktu_masuk is not None
        assert sesi.waktu_keluar is None
        
        updated_slot = self.slot_repo.find_by_id(self.slot.id)
        assert updated_slot.status_ketersediaan.status == StatusSlot.TERISI
    
    def test_start_parking_user_not_found(self):
        with pytest.raises(ValueError, match="User tidak ditemukan"):
            self.parking_service.start_parking(
                user_id=uuid4(),
                vehicle_id=self.user.vehicles[0].id,
                slot_id=self.slot.id
            )
    
    def test_start_parking_vehicle_not_found(self):
        with pytest.raises(ValueError, match="Kendaraan tidak ditemukan"):
            self.parking_service.start_parking(
                user_id=self.user.id,
                vehicle_id=uuid4(),
                slot_id=self.slot.id
            )
    
    def test_start_parking_slot_not_found(self):
        with pytest.raises(ValueError, match="Slot parkir tidak ditemukan"):
            self.parking_service.start_parking(
                user_id=self.user.id,
                vehicle_id=self.user.vehicles[0].id,
                slot_id=uuid4()
            )
    
    def test_start_parking_slot_not_available(self):
        self.slot_service.update_status_slot(self.slot.id, "RUSAK")
        
        with pytest.raises(ValueError, match="Slot parkir tidak tersedia"):
            self.parking_service.start_parking(
                user_id=self.user.id,
                vehicle_id=self.user.vehicles[0].id,
                slot_id=self.slot.id
            )
    
    def test_end_parking_success(self):
        sesi = self.parking_service.start_parking(
            user_id=self.user.id,
            vehicle_id=self.user.vehicles[0].id,
            slot_id=self.slot.id
        )
        
        updated_sesi = self.parking_service.end_parking(sesi.id_sesi)
        
        assert updated_sesi.waktu_keluar is not None
        assert updated_sesi.durasi is not None
        assert updated_sesi.biaya_final is not None
        
        updated_slot = self.slot_repo.find_by_id(self.slot.id)
        assert updated_slot.status_ketersediaan.status == StatusSlot.TERSEDIA
    
    def test_end_parking_sesi_not_found(self):
        with pytest.raises(ValueError, match="Sesi parkir tidak ditemukan"):
            self.parking_service.end_parking(uuid4())
    
    def test_end_parking_already_ended(self):
        sesi = self.parking_service.start_parking(
            user_id=self.user.id,
            vehicle_id=self.user.vehicles[0].id,
            slot_id=self.slot.id
        )
        self.parking_service.end_parking(sesi.id_sesi)
        
        with pytest.raises(ValueError, match="Sesi parkir sudah selesai"):
            self.parking_service.end_parking(sesi.id_sesi)
    
    def test_get_active_sessions_by_user(self):
        sesi1 = self.parking_service.start_parking(
            user_id=self.user.id,
            vehicle_id=self.user.vehicles[0].id,
            slot_id=self.slot.id
        )
        
        slot2 = self.slot_service.buat_slot(lantai=1, posisi_x=15.0, posisi_y=20.0)
        self.user.add_vehicle("D5678ABC", "Mobil", "Toyota", "Avanza")
        self.user_repo.save(self.user)
        
        sesi2 = self.parking_service.start_parking(
            user_id=self.user.id,
            vehicle_id=self.user.vehicles[1].id,
            slot_id=slot2.id
        )
        
        active = self.parking_service.get_active_sessions_by_user(self.user.id)
        assert len(active) == 2
    
    def test_get_session_history_by_user(self):
        sesi = self.parking_service.start_parking(
            user_id=self.user.id,
            vehicle_id=self.user.vehicles[0].id,
            slot_id=self.slot.id
        )
        self.parking_service.end_parking(sesi.id_sesi)
        
        history = self.parking_service.get_session_history_by_user(self.user.id)
        assert len(history) == 1
        assert history[0].waktu_keluar is not None
    
    def test_calculate_parking_fee(self):
        sesi = self.parking_service.start_parking(
            user_id=self.user.id,
            vehicle_id=self.user.vehicles[0].id,
            slot_id=self.slot.id
        )
        
        fee = self.parking_service.calculate_parking_fee(sesi.id_sesi)
        assert fee >= 0
