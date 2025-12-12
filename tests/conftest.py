import pytest
from uuid import uuid4
from datetime import datetime
from decimal import Decimal

from src.manajemen_parkir.domain.auth import Akun, Kredensial, Peran
from src.manajemen_parkir.domain.user import User, Vehicle
from src.manajemen_parkir.domain.alokasi_slot import SlotParkir, Sensor, TipeSensor
from src.manajemen_parkir.infrastructure.auth_repository import InMemoryAuthRepository
from src.manajemen_parkir.infrastructure.user_repository import InMemoryUserRepository
from src.manajemen_parkir.infrastructure.slot_repository import InMemorySlotParkirRepository
from src.manajemen_parkir.infrastructure.repository import InMemorySesiParkirRepository
from src.manajemen_parkir.application.services import AuthService, ParkingService
from src.manajemen_parkir.application.slot_service import SlotParkirService


# Shared repository instances for API tests
@pytest.fixture(scope="session")
def shared_auth_repo():
    return InMemoryAuthRepository()


@pytest.fixture(scope="session")
def shared_user_repo():
    return InMemoryUserRepository()


@pytest.fixture(scope="session")
def shared_slot_repo():
    return InMemorySlotParkirRepository()


@pytest.fixture(scope="session")
def shared_sesi_repo():
    return InMemorySesiParkirRepository()


# Per-test repository instances for domain/application tests
@pytest.fixture
def auth_repo():
    return InMemoryAuthRepository()


@pytest.fixture
def user_repo():
    return InMemoryUserRepository()


@pytest.fixture
def slot_repo():
    return InMemorySlotParkirRepository()


@pytest.fixture
def sesi_repo():
    return InMemorySesiParkirRepository()


@pytest.fixture
def auth_service(auth_repo, user_repo):
    return AuthService(auth_repo, user_repo)


@pytest.fixture
def slot_service(slot_repo):
    return SlotParkirService(slot_repo)


@pytest.fixture
def parking_service(slot_service):
    return ParkingService(slot_service=slot_service)


@pytest.fixture
def sample_akun():
    return Akun.create(
        username="testuser",
        password_hash="hashed_password",
        peran=Peran.PENGGUNA,
        email="test@example.com"
    )


@pytest.fixture
def sample_user():
    return User.create(
        name="Test User",
        email="test@example.com",
        akun_id=uuid4()
    )


@pytest.fixture
def sample_vehicle():
    return Vehicle.create_legacy(
        plate="B1234XYZ",
        vehicle_type="MOBIL"
    )


@pytest.fixture
def sample_slot():
    return SlotParkir.create(
        lantai=1,
        posisi_x=10.0,
        posisi_y=20.0,
        kapasitas=1
    )


@pytest.fixture
def sample_sensor():
    return Sensor.create(
        tipe=TipeSensor.KAMERA,
        kondisi="Normal"
    )
