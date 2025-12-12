from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID, uuid4
from manajemen_parkir.domain.value_objects import NomorPlat


# Entity
@dataclass
class Vehicle:
    id: UUID
    nomor_plat: NomorPlat  # Value Object
    tahun: Optional[int] = None
    warna: Optional[str] = None
    
    plate: Optional[str] = None
    vehicle_type: Optional[str] = None

    @staticmethod
    def create(
        kode_plat: str,
        tipe_kendaraan: str,
        tahun: Optional[int] = None,
        warna: Optional[str] = None
    ) -> "Vehicle":
        nomor_plat = NomorPlat(kode=kode_plat, tipe_kendaraan=tipe_kendaraan)
        return Vehicle(
            id=uuid4(),
            nomor_plat=nomor_plat,
            tahun=tahun,
            warna=warna,
            plate=kode_plat, 
            vehicle_type=tipe_kendaraan
        )
    
    @staticmethod
    def create_legacy(plate: str, vehicle_type: Optional[str] = None) -> "Vehicle":
        tipe = vehicle_type.upper() if vehicle_type else "MOBIL"
        return Vehicle.create(kode_plat=plate, tipe_kendaraan=tipe)


@dataclass
class MetodePembayaran:
    id: UUID
    tipe: str
    token_eksternal: Optional[str] = None
    nama_penyedia: Optional[str] = None
    is_default: bool = False
    is_active: bool = True
    
    @staticmethod
    def create(
        tipe: str,
        token_eksternal: Optional[str] = None,
        nama_penyedia: Optional[str] = None,
        is_default: bool = False
    ) -> "MetodePembayaran":
        return MetodePembayaran(
            id=uuid4(),
            tipe=tipe,
            token_eksternal=token_eksternal,
            nama_penyedia=nama_penyedia,
            is_default=is_default
        )


# Aggregate Root
@dataclass
class User:
    id: UUID
    name: str
    akun_id: Optional[UUID] = None
    email: Optional[str] = None
    vehicles: List[Vehicle] = field(default_factory=list)
    metode_pembayaran: List[MetodePembayaran] = field(default_factory=list)

    @staticmethod
    def create(name: str, email: Optional[str] = None, akun_id: Optional[UUID] = None) -> "User":
        return User(id=uuid4(), name=name, email=email, akun_id=akun_id)
    
    def tambah_kendaraan(self, vehicle: Vehicle):
        self.vehicles.append(vehicle)
    
    def add_vehicle(self, nomor_plat: str, jenis_kendaraan: str, merek: Optional[str] = None, model: Optional[str] = None):
        vehicle = Vehicle.create(kode_plat=nomor_plat, tipe_kendaraan=jenis_kendaraan)
        self.vehicles.append(vehicle)
    
    def tambah_metode_pembayaran(self, metode: MetodePembayaran):
        if metode.is_default:
            for m in self.metode_pembayaran:
                m.is_default = False
        self.metode_pembayaran.append(metode)
    
    def set_metode_pembayaran_default(self, metode_id: UUID):
        found = False
        for metode in self.metode_pembayaran:
            if metode.id == metode_id:
                metode.is_default = True
                found = True
            else:
                metode.is_default = False
        if not found:
            raise ValueError("Metode pembayaran tidak ditemukan")
    
    def get_metode_pembayaran_default(self) -> Optional[MetodePembayaran]:
        for metode in self.metode_pembayaran:
            if metode.is_default:
                return metode
        return None

