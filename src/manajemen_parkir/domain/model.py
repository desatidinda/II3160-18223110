from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from decimal import Decimal

from .value_objects import NomorPlat, Durasi, BiayaFinal


class StatusSesi(str, Enum):
    AKTIF = "AKTIF"
    SELESAI = "SELESAI"
    DIBATALKAN = "DIBATALKAN"


@dataclass
class SesiParkir:
    nomor_plat: NomorPlat
    id_sesi: UUID = field(default_factory=uuid4)
    waktu_masuk: datetime = field(default_factory=datetime.utcnow)
    waktu_keluar: Optional[datetime] = None
    status: StatusSesi = StatusSesi.AKTIF
    durasi: Optional[Durasi] = None
    biaya_final: Optional[BiayaFinal] = None
    owner_id: Optional[UUID] = None
    vehicle_id: Optional[UUID] = None
    slot_id: Optional[UUID] = None

    def check_out(self, tarif):
        if self.status != StatusSesi.AKTIF:
            raise ValueError("Sesi sudah berakhir atau dibatalkan.")
        self.waktu_keluar = datetime.utcnow()
        selisih = self.waktu_keluar - self.waktu_masuk
        total_menit = int(selisih.total_seconds() / 60)
        self.durasi = Durasi(total_menit=total_menit)
        jumlah = tarif.calculate(self.waktu_masuk, self.waktu_keluar)
        self.biaya_final = BiayaFinal(jumlah=Decimal(jumlah))
        self.status = StatusSesi.SELESAI


@dataclass
class Transaksi:
    id_transaksi: UUID = field(default_factory=uuid4)
    id_sesi: UUID | None = None
    metode_pembayaran: Optional[str] = None
    status_pembayaran: Optional[str] = None
    waktu_pembayaran: Optional[datetime] = None
