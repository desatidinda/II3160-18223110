from decimal import Decimal
from typing import Optional
from uuid import UUID

from manajemen_parkir.domain.model import SesiParkir
from manajemen_parkir.infrastructure.repository import InMemorySesiParkirRepository
from manajemen_parkir.domain.tariff import ParkingTariff


class ParkingService:
    def __init__(self, repo: Optional[InMemorySesiParkirRepository] = None):
        self.repo = repo or InMemorySesiParkirRepository()
        self.tarif = ParkingTariff(price_per_hour=3000.0, max_daily=50000.0)

    def start_parking(
        self,
        kode_plat: str,
        tipe_kendaraan: Optional[str] = None,
        user_id: Optional[UUID] = None,
        vehicle_id: Optional[UUID] = None,
    ) -> SesiParkir:
        from manajemen_parkir.domain.value_objects import NomorPlat

        nomor = NomorPlat(kode=kode_plat, tipe_kendaraan=tipe_kendaraan)
        sesi = SesiParkir(nomor_plat=nomor, owner_id=user_id, vehicle_id=vehicle_id)
        self.repo.save(sesi)
        return sesi

    def end_parking(self, id_sesi: UUID) -> SesiParkir:
        sesi = self.repo.get_by_id(id_sesi)
        if not sesi:
            raise ValueError("Sesi parkir tidak ditemukan")
        sesi.check_out(self.tarif)
        self.repo.save(sesi)
        return sesi

    def get(self, id_sesi: UUID) -> Optional[SesiParkir]:
        return self.repo.get_by_id(id_sesi)

    def list(self):
        return self.repo.list()
