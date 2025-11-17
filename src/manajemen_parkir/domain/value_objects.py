from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class NomorPlat:
    kode: str
    tipe_kendaraan: Optional[str] = None


@dataclass(frozen=True)
class Durasi:
    total_menit: int

    @property
    def total_jam(self) -> int:
        return max(1, -(-self.total_menit // 60))


@dataclass(frozen=True)
class BiayaFinal:
    jumlah: Decimal
    mata_uang: str = "IDR"
