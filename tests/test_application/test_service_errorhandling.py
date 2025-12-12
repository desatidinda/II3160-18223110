import pytest
from uuid import uuid4, UUID
from manajemen_parkir.application.services import AuthService, ParkingService
from manajemen_parkir.infrastructure.auth_repository import InMemoryAuthRepository
from manajemen_parkir.infrastructure.user_repository import InMemoryUserRepository
from manajemen_parkir.infrastructure.repository import InMemorySesiParkirRepository
from manajemen_parkir.infrastructure.slot_repository import InMemorySlotParkirRepository
from manajemen_parkir.domain.value_objects import NomorPlat
from manajemen_parkir.domain.alokasi_slot import SlotParkir


class TestAuthServiceErrorPaths:
    
    def test_verify_token_with_invalid_token_format(self):
        auth_repo = InMemoryAuthRepository()
        user_repo = InMemoryUserRepository()
        service = AuthService(auth_repo, user_repo)
        
        with pytest.raises(ValueError, match="Token tidak valid"):
            service.verify_token("invalid_token_format")


class TestParkingServiceErrorPaths:
    
    def test_start_parking_user_not_found(self):
        sesi_repo = InMemorySesiParkirRepository()
        user_repo = InMemoryUserRepository()
        slot_repo = InMemorySlotParkirRepository()
        
        service = ParkingService(sesi_repo, user_repo, slot_repo)
        
        fake_user_id = uuid4()
        fake_vehicle_id = uuid4()
        
        with pytest.raises(ValueError, match="User tidak ditemukan"):
            service.start_parking(fake_user_id, fake_vehicle_id, None)
    
    def test_start_parking_without_repos(self):
        sesi_repo = InMemorySesiParkirRepository()
        service = ParkingService(sesi_repo, None, None)
        
        fake_user_id = uuid4()
        fake_vehicle_id = uuid4()
        
        sesi = service.start_parking(fake_user_id, fake_vehicle_id, None)
        
        assert sesi is not None
        assert sesi.owner_id == fake_user_id
        assert sesi.vehicle_id == fake_vehicle_id
        assert sesi.nomor_plat.kode == "TEMP"
    
    def test_end_parking_session_not_found(self):
        sesi_repo = InMemorySesiParkirRepository()
        service = ParkingService(sesi_repo, None, None)
        
        fake_sesi_id = uuid4()
        
        with pytest.raises(ValueError, match="Sesi parkir tidak ditemukan"):
            service.end_parking(fake_sesi_id)
    
    def test_calculate_parking_fee_session_not_found(self):
        sesi_repo = InMemorySesiParkirRepository()
        service = ParkingService(sesi_repo, None, None)
        
        fake_sesi_id = uuid4()
        
        with pytest.raises(ValueError, match="Sesi parkir tidak ditemukan"):
            service.calculate_parking_fee(fake_sesi_id)
    
    def test_start_parking_slot_not_found(self):
        sesi_repo = InMemorySesiParkirRepository()
        slot_repo = InMemorySlotParkirRepository()
        
        service = ParkingService(sesi_repo, None, slot_repo)
        
        fake_user_id = uuid4()
        fake_vehicle_id = uuid4()
        fake_slot_id = uuid4()
        
        with pytest.raises(ValueError, match="Slot parkir tidak ditemukan"):
            service.start_parking(fake_user_id, fake_vehicle_id, fake_slot_id)
    
    def test_start_parking_slot_not_available(self):
        sesi_repo = InMemorySesiParkirRepository()
        slot_repo = InMemorySlotParkirRepository()
        
        slot = SlotParkir.create(
            lantai=1,
            posisi_x=10.0,
            posisi_y=20.0,
            kapasitas=1
        )
        slot.tandai_terisi()
        slot_repo.save(slot)
        
        service = ParkingService(sesi_repo, None, slot_repo)
        
        fake_user_id = uuid4()
        fake_vehicle_id = uuid4()
        
        with pytest.raises(ValueError, match="Slot parkir tidak tersedia"):
            service.start_parking(fake_user_id, fake_vehicle_id, slot.id)

