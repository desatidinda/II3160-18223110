from typing import List, Optional
from uuid import UUID

from manajemen_parkir.domain.alokasi_slot import (
    SlotParkir, Sensor, TipeSensor, StatusSlot
)
from manajemen_parkir.infrastructure.slot_repository import InMemorySlotParkirRepository


class SlotParkirService:
    
    def __init__(self, repository: InMemorySlotParkirRepository):
        self.repository = repository
    
    def buat_slot(
        self,
        lantai: int,
        posisi_x: float,
        posisi_y: float,
        kapasitas: int = 1,
        keterangan: Optional[str] = None,
        tipe_sensor: Optional[str] = None
    ) -> SlotParkir:
        sensor = None
        if tipe_sensor:
            try:
                tipe = TipeSensor[tipe_sensor.upper()]
                sensor = Sensor.create(tipe=tipe)
            except KeyError:
                raise ValueError(f"Tipe sensor tidak valid: {tipe_sensor}")
        
        slot = SlotParkir.create(
            lantai=lantai,
            posisi_x=posisi_x,
            posisi_y=posisi_y,
            kapasitas=kapasitas,
            sensor=sensor,
            keterangan=keterangan
        )
        
        return self.repository.save(slot)
    
    def update_status_slot(self, slot_id: UUID, status: str) -> SlotParkir:
        slot = self.repository.get_by_id(slot_id)
        if not slot:
            raise ValueError("Slot parkir tidak ditemukan")
        
        status_upper = status.upper()
        if status_upper == "TERSEDIA":
            slot.tandai_tersedia()
        elif status_upper == "TERISI":
            slot.tandai_terisi()
        elif status_upper == "RUSAK":
            slot.tandai_rusak()
        else:
            raise ValueError(f"Status tidak valid: {status}")
        
        return self.repository.save(slot)
    
    def pasang_sensor_ke_slot(
        self,
        slot_id: UUID,
        tipe_sensor: str
    ) -> SlotParkir:
        slot = self.repository.get_by_id(slot_id)
        if not slot:
            raise ValueError("Slot parkir tidak ditemukan")
        
        try:
            tipe = TipeSensor[tipe_sensor.upper()]
        except KeyError:
            raise ValueError(f"Tipe sensor tidak valid: {tipe_sensor}")
        
        sensor = Sensor.create(tipe=tipe)
        slot.pasang_sensor(sensor)
        
        return self.repository.save(slot)
    
    def lepas_sensor_dari_slot(self, slot_id: UUID) -> SlotParkir:
        slot = self.repository.get_by_id(slot_id)
        if not slot:
            raise ValueError("Slot parkir tidak ditemukan")
        
        slot.lepas_sensor()
        return self.repository.save(slot)
    
    def update_kondisi_sensor(
        self,
        slot_id: UUID,
        kondisi: str
    ) -> SlotParkir:
        slot = self.repository.get_by_id(slot_id)
        if not slot:
            raise ValueError("Slot parkir tidak ditemukan")
        
        if not slot.sensor:
            raise ValueError("Slot tidak memiliki sensor")
        
        slot.sensor.update_kondisi(kondisi)
        return self.repository.save(slot)
    
    def get_slot_tersedia(self, lantai: Optional[int] = None) -> List[SlotParkir]:
        if lantai is not None:
            slots = self.repository.list_by_lantai(lantai)
            return [slot for slot in slots if slot.is_tersedia()]
        return self.repository.list_tersedia()
    
    def get_statistik_slot(self) -> dict:
        total = self.repository.count_total()
        tersedia = self.repository.count_tersedia()
        terisi = self.repository.count_terisi()
        rusak = self.repository.count_rusak()
        
        return {
            "total": total,
            "tersedia": tersedia,
            "terisi": terisi,
            "rusak": rusak,
            "persentase_okupansi": round((terisi / total * 100) if total > 0 else 0, 2)
        }
    
    def get_statistik_per_lantai(self) -> dict:
        all_slots = self.repository.list_all()
        lantai_stats = {}
        
        for slot in all_slots:
            lantai = slot.koordinat.lantai
            if lantai not in lantai_stats:
                lantai_stats[lantai] = {
                    "total": 0,
                    "tersedia": 0,
                    "terisi": 0,
                    "rusak": 0
                }
            
            lantai_stats[lantai]["total"] += 1
            status = slot.status_ketersediaan.status
            
            if status == StatusSlot.TERSEDIA:
                lantai_stats[lantai]["tersedia"] += 1
            elif status == StatusSlot.TERISI:
                lantai_stats[lantai]["terisi"] += 1
            elif status == StatusSlot.RUSAK:
                lantai_stats[lantai]["rusak"] += 1
        
        for lantai, stats in lantai_stats.items():
            total = stats["total"]
            terisi = stats["terisi"]
            stats["persentase_okupansi"] = round((terisi / total * 100) if total > 0 else 0, 2)
        
        return lantai_stats
