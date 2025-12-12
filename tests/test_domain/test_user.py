import pytest
from uuid import uuid4

from src.manajemen_parkir.domain.user import User, Vehicle, MetodePembayaran
from src.manajemen_parkir.domain.value_objects import NomorPlat


class TestNomorPlat:
    def test_create_nomor_plat(self):
        nomor_plat = NomorPlat(kode="B1234XYZ", tipe_kendaraan="MOBIL")
        assert nomor_plat.kode == "B1234XYZ"
        assert nomor_plat.tipe_kendaraan == "MOBIL"
    
    def test_nomor_plat_without_type(self):
        nomor_plat = NomorPlat(kode="B1234XYZ")
        assert nomor_plat.kode == "B1234XYZ"
        assert nomor_plat.tipe_kendaraan is None
    
    def test_nomor_plat_immutable(self):
        nomor_plat = NomorPlat(kode="B1234XYZ", tipe_kendaraan="MOBIL")
        with pytest.raises(Exception):
            nomor_plat.kode = "B5678ABC"


class TestVehicle:
    def test_create_vehicle_legacy(self):
        vehicle = Vehicle.create_legacy(plate="B1234XYZ", vehicle_type="MOBIL")
        assert vehicle.plate == "B1234XYZ"
        assert vehicle.vehicle_type == "MOBIL"
        assert vehicle.id is not None
    
    def test_create_vehicle_with_nomor_plat_value_object(self):
        nomor_plat = NomorPlat(kode="B1234XYZ", tipe_kendaraan="MOTOR")
        vehicle = Vehicle(
            id=uuid4(),
            nomor_plat=nomor_plat,
            plate="B1234XYZ",
            vehicle_type="MOTOR"
        )
        assert vehicle.nomor_plat == nomor_plat
        assert vehicle.plate == "B1234XYZ"
        assert vehicle.vehicle_type == "MOTOR"
    
    def test_vehicle_unique_id(self):
        vehicle1 = Vehicle.create_legacy(plate="B1234XYZ")
        vehicle2 = Vehicle.create_legacy(plate="B5678ABC")
        assert vehicle1.id != vehicle2.id
    
    def test_vehicle_no_type(self):
        vehicle = Vehicle.create_legacy(plate="B1234XYZ")
        assert vehicle.vehicle_type is None or vehicle.vehicle_type in ["MOTOR", "MOBIL"]
    
    def test_vehicle_optional_fields(self):
        vehicle = Vehicle.create_legacy(plate="B1234XYZ")
        assert vehicle.tahun is None
        assert vehicle.warna is None


class TestUser:
    def test_create_user(self):
        akun_id = uuid4()
        user = User.create(name="John Doe", email="john@example.com", akun_id=akun_id)
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.akun_id == akun_id
        assert user.vehicles == []
        assert user.id is not None
    
    def test_user_without_email(self):
        user = User.create(name="John Doe", akun_id=uuid4())
        assert user.email is None
    
    def test_add_vehicle_to_user(self):
        user = User.create(name="John Doe", email="john@example.com", akun_id=uuid4())
        vehicle = Vehicle.create_legacy(plate="B1234XYZ", vehicle_type="MOBIL")
        
        user.vehicles.append(vehicle)
        assert len(user.vehicles) == 1
        assert user.vehicles[0] == vehicle
    
    def test_add_multiple_vehicles(self):
        user = User.create(name="John Doe", email="john@example.com", akun_id=uuid4())
        vehicle1 = Vehicle.create_legacy(plate="B1234XYZ", vehicle_type="MOBIL")
        vehicle2 = Vehicle.create_legacy(plate="B5678ABC", vehicle_type="MOTOR")
        
        user.vehicles.extend([vehicle1, vehicle2])
        assert len(user.vehicles) == 2
    
    def test_user_unique_id(self):
        user1 = User.create(name="User 1", akun_id=uuid4())
        user2 = User.create(name="User 2", akun_id=uuid4())
        assert user1.id != user2.id
    
    def test_user_vehicle_relationship(self):
        user = User.create(name="John Doe", email="john@example.com", akun_id=uuid4())
        assert hasattr(user, 'vehicles')
        assert isinstance(user.vehicles, list)


class TestMetodePembayaran:
    def test_create_metode_pembayaran(self):
        metode = MetodePembayaran.create(
            tipe="KARTU_KREDIT",
            token_eksternal="tok_123456",
            nama_penyedia="Visa",
            is_default=True
        )
        assert metode.tipe == "KARTU_KREDIT"
        assert metode.token_eksternal == "tok_123456"
        assert metode.nama_penyedia == "Visa"
        assert metode.is_default is True
        assert metode.id is not None
    
    def test_create_metode_pembayaran_minimal(self):
        metode = MetodePembayaran.create(tipe="TUNAI")
        assert metode.tipe == "TUNAI"
        assert metode.token_eksternal is None
        assert metode.nama_penyedia is None
        assert metode.is_default is False
    
    def test_tambah_metode_pembayaran(self):
        user = User.create(name="John Doe", akun_id=uuid4())
        metode = MetodePembayaran.create(tipe="KARTU_KREDIT")
        
        user.tambah_metode_pembayaran(metode)
        
        assert len(user.metode_pembayaran) == 1
        assert user.metode_pembayaran[0] == metode
    
    def test_tambah_metode_pembayaran_set_default(self):
        user = User.create(name="John Doe", akun_id=uuid4())
        metode1 = MetodePembayaran.create(tipe="TUNAI", is_default=True)
        metode2 = MetodePembayaran.create(tipe="KARTU_KREDIT", is_default=True)
        
        user.tambah_metode_pembayaran(metode1)
        user.tambah_metode_pembayaran(metode2)
        
        assert metode1.is_default is False
        assert metode2.is_default is True
    
    def test_set_metode_pembayaran_default(self):
        user = User.create(name="John Doe", akun_id=uuid4())
        metode1 = MetodePembayaran.create(tipe="TUNAI", is_default=True)
        metode2 = MetodePembayaran.create(tipe="KARTU_KREDIT")
        
        user.tambah_metode_pembayaran(metode1)
        user.tambah_metode_pembayaran(metode2)
        
        user.set_metode_pembayaran_default(metode2.id)
        
        assert metode1.is_default is False
        assert metode2.is_default is True
    
    def test_set_metode_pembayaran_default_not_found(self):
        user = User.create(name="John Doe", akun_id=uuid4())
        
        with pytest.raises(ValueError, match="tidak ditemukan"):
            user.set_metode_pembayaran_default(uuid4())
    
    def test_get_metode_pembayaran_default(self):
        user = User.create(name="John Doe", akun_id=uuid4())
        metode1 = MetodePembayaran.create(tipe="TUNAI")
        metode2 = MetodePembayaran.create(tipe="KARTU_KREDIT", is_default=True)
        
        user.tambah_metode_pembayaran(metode1)
        user.tambah_metode_pembayaran(metode2)
        
        default = user.get_metode_pembayaran_default()
        assert default == metode2
    
    def test_get_metode_pembayaran_default_none(self):
        user = User.create(name="John Doe", akun_id=uuid4())
        metode = MetodePembayaran.create(tipe="TUNAI", is_default=False)
        user.tambah_metode_pembayaran(metode)
        
        default = user.get_metode_pembayaran_default()
        assert default is None
