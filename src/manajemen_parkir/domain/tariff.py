from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from math import ceil
from typing import Optional
from uuid import UUID, uuid4


class JenisTarif(Enum):
    REGULER = "REGULER"
    PREMIUM = "PREMIUM"
    PROMO = "PROMO"


class TipeKendaraan(Enum):
    MOTOR = "MOTOR"
    MOBIL = "MOBIL"


@dataclass(frozen=True)
class Durasi:
    total_jam: int
    total_menit: int
    
    @staticmethod
    def hitung_dari_waktu(waktu_masuk: datetime, waktu_keluar: datetime) -> 'Durasi':
        if waktu_keluar < waktu_masuk:
            raise ValueError("Waktu keluar tidak boleh lebih awal dari waktu masuk")
        
        delta = waktu_keluar - waktu_masuk
        total_menit = int(delta.total_seconds() / 60)
        total_jam = total_menit // 60
        sisa_menit = total_menit % 60
        
        return Durasi(total_jam=total_jam, total_menit=sisa_menit)
    
    def ke_jam_penuh(self) -> int:
        if self.total_menit > 0:
            return self.total_jam + 1
        return self.total_jam
    
    def __str__(self) -> str:
        return f"{self.total_jam} jam {self.total_menit} menit"


@dataclass(frozen=True)
class BiayaFinal:
    jumlah: Decimal
    keterangan: Optional[str] = None
    
    def __post_init__(self):
        if self.jumlah < 0:
            raise ValueError("BiayaFinal tidak boleh negatif")
    
    def format_rupiah(self) -> str:
        return f"Rp {self.jumlah:,.2f}"
    
    def __str__(self) -> str:
        return self.format_rupiah()


@dataclass
class TarifParkir:
    id: UUID
    nama: str
    jenis_tarif: JenisTarif
    tipe_kendaraan: TipeKendaraan
    harga_per_jam: Decimal
    harga_maksimum_harian: Optional[Decimal] = None
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.now())
        if self.updated_at is None:
            object.__setattr__(self, 'updated_at', datetime.now())
    
    @staticmethod
    def create(
        nama: str,
        tipe_kendaraan: TipeKendaraan,
        harga_per_jam: Decimal,
        jenis_tarif: JenisTarif = JenisTarif.REGULER,
        harga_maksimum_harian: Optional[Decimal] = None
    ) -> 'TarifParkir':
        if harga_per_jam < 0:
            raise ValueError("Harga per jam tidak boleh negatif")
        if harga_maksimum_harian and harga_maksimum_harian < harga_per_jam:
            raise ValueError("Harga maksimum harian harus lebih besar dari harga per jam")
        
        return TarifParkir(
            id=uuid4(),
            nama=nama,
            jenis_tarif=jenis_tarif,
            tipe_kendaraan=tipe_kendaraan,
            harga_per_jam=harga_per_jam,
            harga_maksimum_harian=harga_maksimum_harian
        )
    
    def hitung_biaya(self, durasi: Durasi) -> BiayaFinal:
        jam_penuh = durasi.ke_jam_penuh()
        biaya = self.harga_per_jam * jam_penuh
        
        if self.harga_maksimum_harian and biaya > self.harga_maksimum_harian:
            biaya = self.harga_maksimum_harian
            keterangan = f"Tarif maksimum harian diterapkan ({durasi})"
        else:
            keterangan = f"Tarif {self.jenis_tarif.value} - {durasi}"
        
        return BiayaFinal(jumlah=biaya, keterangan=keterangan)
    
    def update_harga(self, harga_per_jam: Decimal, harga_maksimum_harian: Optional[Decimal] = None):
        if harga_per_jam < 0:
            raise ValueError("Harga per jam tidak boleh negatif")
        self.harga_per_jam = harga_per_jam
        self.harga_maksimum_harian = harga_maksimum_harian
        self.updated_at = datetime.now()
    
    def nonaktifkan(self):
        self.is_active = False
        self.updated_at = datetime.now()
    
    def aktifkan(self):
        self.is_active = True
        self.updated_at = datetime.now()


class ParkingTariff:
    def __init__(self, price_per_hour: float = 3000.0, max_daily: float | None = None, tariff_type: str = "regular"):
        self.price_per_hour = float(price_per_hour)
        self.max_daily = float(max_daily) if max_daily is not None else None
        self.tariff_type = tariff_type

    def calculate(self, checkin: datetime, checkout: datetime) -> float:
        seconds = (checkout - checkin).total_seconds()
        hours = max(1, ceil(seconds / 3600))
        fee = hours * self.price_per_hour
        if self.max_daily is not None:
            days = max(1, (checkout.date() - checkin.date()).days + 1)
            fee = min(fee, days * self.max_daily)
        return float(fee)

