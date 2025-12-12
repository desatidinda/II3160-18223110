import pytest
from uuid import UUID, uuid4

from src.manajemen_parkir.infrastructure.auth_repository import InMemoryAuthRepository
from src.manajemen_parkir.infrastructure.user_repository import InMemoryUserRepository
from src.manajemen_parkir.infrastructure.slot_repository import InMemorySlotParkirRepository
from src.manajemen_parkir.infrastructure.repository import InMemorySesiParkirRepository
from src.manajemen_parkir.domain.auth import Akun, Kredensial, Peran
from src.manajemen_parkir.domain.user import User, Vehicle
from src.manajemen_parkir.domain.alokasi_slot import SlotParkir, Koordinat
from src.manajemen_parkir.domain.model import SesiParkir
from src.manajemen_parkir.domain.value_objects import NomorPlat


class TestAuthRepository:
    def test_save_and_get_by_id(self):
        repo = InMemoryAuthRepository()
        akun = Akun.create("testuser", "hash123", Peran.PENGGUNA)
        
        repo.save(akun)
        result = repo.get_by_id(akun.id)
        
        assert result is not None
        assert result.id == akun.id
        assert result.kredensial.username == "testuser"
    
    def test_get_by_id_not_found(self):
        repo = InMemoryAuthRepository()
        result = repo.get_by_id(uuid4())
        assert result is None
    
    def test_get_by_username(self):
        repo = InMemoryAuthRepository()
        akun = Akun.create("testuser", "hash123", Peran.PENGGUNA)
        repo.save(akun)
        
        result = repo.get_by_username("testuser")
        assert result is not None
        assert result.kredensial.username == "testuser"
    
    def test_get_by_username_not_found(self):
        repo = InMemoryAuthRepository()
        result = repo.get_by_username("nonexistent")
        assert result is None
    
    def test_username_exists(self):
        repo = InMemoryAuthRepository()
        akun = Akun.create("testuser", "hash123", Peran.PENGGUNA)
        repo.save(akun)
        
        assert repo.username_exists("testuser") is True
        assert repo.username_exists("other") is False
    
    def test_list_all(self):
        repo = InMemoryAuthRepository()
        akun1 = Akun.create("user1", "hash1", Peran.PENGGUNA)
        akun2 = Akun.create("user2", "hash2", Peran.ADMIN)
        
        repo.save(akun1)
        repo.save(akun2)
        
        result = repo.list()
        assert len(result) == 2
        assert akun1 in result
        assert akun2 in result
    
    def test_delete(self):
        repo = InMemoryAuthRepository()
        akun = Akun.create("testuser", "hash123", Peran.PENGGUNA)
        repo.save(akun)
        
        result = repo.delete(akun.id)
        assert result is True
        assert repo.get_by_id(akun.id) is None
    
    def test_delete_not_found(self):
        repo = InMemoryAuthRepository()
        result = repo.delete(uuid4())
        assert result is False


class TestUserRepository:
    def test_save_and_get_by_id(self):
        repo = InMemoryUserRepository()
        user = User.create("Test User", "test@example.com")
        
        repo.save(user)
        result = repo.get_by_id(user.id)
        
        assert result is not None
        assert result.id == user.id
        assert result.name == "Test User"
    
    def test_get_by_id_not_found(self):
        repo = InMemoryUserRepository()
        result = repo.get_by_id(uuid4())
        assert result is None
    
    def test_find_by_id_alias(self):
        repo = InMemoryUserRepository()
        user = User.create("Test User")
        repo.save(user)
        
        result = repo.find_by_id(user.id)
        assert result is not None
        assert result.id == user.id
    
    def test_find_by_plate(self):
        repo = InMemoryUserRepository()
        user = User.create("Test User")
        vehicle = Vehicle.create_legacy("B1234XYZ", "MOBIL")
        user.vehicles.append(vehicle)
        repo.save(user)
        
        result = repo.find_by_plate("B1234XYZ")
        assert result is not None
        assert result.id == vehicle.id
    
    def test_find_by_plate_not_found(self):
        repo = InMemoryUserRepository()
        result = repo.find_by_plate("NOTFOUND")
        assert result is None
    
    def test_list(self):
        repo = InMemoryUserRepository()
        user1 = User.create("User 1")
        user2 = User.create("User 2")
        
        repo.save(user1)
        repo.save(user2)
        
        result = repo.list()
        assert len(result) == 2
        assert user1 in result
        assert user2 in result
    
    def test_delete(self):
        repo = InMemoryUserRepository()
        user = User.create("Test User")
        repo.save(user)
        
        result = repo.delete(user.id)
        assert result is True
        assert repo.get_by_id(user.id) is None
    
    def test_delete_not_found(self):
        repo = InMemoryUserRepository()
        result = repo.delete(uuid4())
        assert result is False


class TestSlotRepository:
    def test_save_and_get_by_id(self):
        repo = InMemorySlotParkirRepository()
        slot = SlotParkir.create(lantai=1, posisi_x=10.0, posisi_y=20.0)
        
        repo.save(slot)
        result = repo.get_by_id(slot.id)
        
        assert result is not None
        assert result.id == slot.id
    
    def test_find_by_id_alias(self):
        repo = InMemorySlotParkirRepository()
        slot = SlotParkir.create(lantai=1, posisi_x=10.0, posisi_y=20.0)
        repo.save(slot)
        
        result = repo.find_by_id(slot.id)
        assert result is not None
        assert result.id == slot.id
    
    def test_list(self):
        repo = InMemorySlotParkirRepository()
        slot1 = SlotParkir.create(lantai=1, posisi_x=10.0, posisi_y=20.0)
        slot2 = SlotParkir.create(lantai=2, posisi_x=15.0, posisi_y=25.0)
        
        repo.save(slot1)
        repo.save(slot2)
        
        result = repo.list_all()
        assert len(result) == 2
        assert slot1 in result
        assert slot2 in result
    
    def test_get_by_lantai(self):
        repo = InMemorySlotParkirRepository()
        slot1 = SlotParkir.create(lantai=1, posisi_x=10.0, posisi_y=20.0)
        slot2 = SlotParkir.create(lantai=2, posisi_x=15.0, posisi_y=25.0)
        slot3 = SlotParkir.create(lantai=1, posisi_x=30.0, posisi_y=40.0)
        
        repo.save(slot1)
        repo.save(slot2)
        repo.save(slot3)
        
        result = repo.list_by_lantai(1)
        assert len(result) == 2
        assert slot1 in result
        assert slot3 in result
        assert slot2 not in result
    
    def test_delete(self):
        repo = InMemorySlotParkirRepository()
        slot = SlotParkir.create(lantai=1, posisi_x=10.0, posisi_y=20.0)
        repo.save(slot)
        
        result = repo.delete(slot.id)
        assert result is True
        assert repo.get_by_id(slot.id) is None
    
    def test_delete_not_found(self):
        repo = InMemorySlotParkirRepository()
        result = repo.delete(uuid4())
        assert result is False


class TestSesiRepository:
    def test_save_and_get_by_id(self):
        repo = InMemorySesiParkirRepository()
        nomor = NomorPlat("B1234XYZ", "MOBIL")
        sesi = SesiParkir(nomor_plat=nomor)
        
        repo.save(sesi)
        result = repo.get_by_id(sesi.id_sesi)
        
        assert result is not None
        assert result.id_sesi == sesi.id_sesi
    
    def test_get_by_id_not_found(self):
        repo = InMemorySesiParkirRepository()
        result = repo.get_by_id(uuid4())
        assert result is None
    
    def test_list(self):
        repo = InMemorySesiParkirRepository()
        sesi1 = SesiParkir(nomor_plat=NomorPlat("B1111", "MOBIL"))
        sesi2 = SesiParkir(nomor_plat=NomorPlat("B2222", "MOTOR"))
        
        repo.save(sesi1)
        repo.save(sesi2)
        
        result = repo.list()
        assert len(result) == 2
        assert sesi1 in result
        assert sesi2 in result
