from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4


class TipeSensor(Enum):
    KAMERA = "KAMERA"
    ULTRASONIK = "ULTRASONIK"
    INFRARED = "INFRARED"


class StatusSlot(Enum):
    TERSEDIA = "TERSEDIA"
    TERISI = "TERISI"
    RUSAK = "RUSAK"


@dataclass(frozen=True)
class Koordinat:
    lantai: int
    posisi_x: float
    posisi_y: float
    
    def __post_init__(self):
        if self.lantai < 0:
            raise ValueError("Lantai tidak boleh negatif")


@dataclass(frozen=True)
class StatusKetersediaan:
    status: StatusSlot
    waktu_update: datetime
    
    @staticmethod
    def tersedia():
        return StatusKetersediaan(
            status=StatusSlot.TERSEDIA,
            waktu_update=datetime.now()
        )
    
    @staticmethod
    def terisi():
        return StatusKetersediaan(
            status=StatusSlot.TERISI,
            waktu_update=datetime.now()
        )
    
    @staticmethod
    def rusak():
        return StatusKetersediaan(
            status=StatusSlot.RUSAK,
            waktu_update=datetime.now()
        )


@dataclass
class Sensor:
    id: UUID
    tipe: TipeSensor
    kondisi: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    @staticmethod
    def create(tipe: TipeSensor, kondisi: str = "Normal") -> 'Sensor':
        return Sensor(
            id=uuid4(),
            tipe=tipe,
            kondisi=kondisi,
            is_active=True
        )
    
    def update_kondisi(self, kondisi_baru: str):
        self.kondisi = kondisi_baru
    
    def activate(self):
        self.is_active = True
    
    def deactivate(self):
        self.is_active = False


@dataclass
class SlotParkir:
    id: UUID
    kapasitas: int
    koordinat: Koordinat
    status_ketersediaan: StatusKetersediaan
    sensor: Optional[Sensor] = None
    keterangan: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @staticmethod
    def create(
        lantai: int,
        posisi_x: float,
        posisi_y: float,
        kapasitas: int = 1,
        sensor: Optional[Sensor] = None,
        keterangan: Optional[str] = None
    ) -> 'SlotParkir':
        koordinat = Koordinat(lantai=lantai, posisi_x=posisi_x, posisi_y=posisi_y)
        return SlotParkir(
            id=uuid4(),
            kapasitas=kapasitas,
            koordinat=koordinat,
            status_ketersediaan=StatusKetersediaan.tersedia(),
            sensor=sensor,
            keterangan=keterangan
        )
    
    def tandai_tersedia(self):
        self.status_ketersediaan = StatusKetersediaan.tersedia()
        self.updated_at = datetime.now()
    
    def tandai_terisi(self):
        if self.status_ketersediaan.status == StatusSlot.RUSAK:
            raise ValueError("Slot rusak tidak bisa diisi")
        self.status_ketersediaan = StatusKetersediaan.terisi()
        self.updated_at = datetime.now()
    
    def tandai_rusak(self):
        self.status_ketersediaan = StatusKetersediaan.rusak()
        self.updated_at = datetime.now()
    
    def pasang_sensor(self, sensor: Sensor):
        self.sensor = sensor
        self.updated_at = datetime.now()
    
    def lepas_sensor(self):
        self.sensor = None
        self.updated_at = datetime.now()
    
    def is_tersedia(self) -> bool:
        return self.status_ketersediaan.status == StatusSlot.TERSEDIA
