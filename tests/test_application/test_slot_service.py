import pytest
from uuid import uuid4

from manajemen_parkir.domain.alokasi_slot import TipeSensor, StatusSlot
from manajemen_parkir.infrastructure.slot_repository import InMemorySlotParkirRepository
from manajemen_parkir.application.slot_service import SlotParkirService


class TestSlotParkirService:
    def test_buat_slot_basic(self):
        repo = InMemorySlotParkirRepository()
        service = SlotParkirService(repo)
        
        slot = service.buat_slot(lantai=1, posisi_x=10.0, posisi_y=20.0)
        
        assert slot.koordinat.lantai == 1
        assert slot.koordinat.posisi_x == 10.0
        assert slot.status_ketersediaan.status == StatusSlot.TERSEDIA
    
    def test_buat_slot_with_sensor(self):
        repo = InMemorySlotParkirRepository()
        service = SlotParkirService(repo)
        
        slot = service.buat_slot(
            lantai=1,
            posisi_x=10.0,
            posisi_y=20.0,
            tipe_sensor="KAMERA"
        )
        
        assert slot.sensor is not None
        assert slot.sensor.tipe == TipeSensor.KAMERA
    
    def test_buat_slot_invalid_sensor(self):
        repo = InMemorySlotParkirRepository()
        service = SlotParkirService(repo)
        
        with pytest.raises(ValueError, match="Tipe sensor tidak valid"):
            service.buat_slot(
                lantai=1,
                posisi_x=10.0,
                posisi_y=20.0,
                tipe_sensor="INVALID"
            )
    
    def test_update_status_slot_to_terisi(self):
        repo = InMemorySlotParkirRepository()
        service = SlotParkirService(repo)
        
        slot = service.buat_slot(lantai=1, posisi_x=10.0, posisi_y=20.0)
        updated = service.update_status_slot(slot.id, "TERISI")
        
        assert updated.status_ketersediaan.status == StatusSlot.TERISI
    
    def test_update_status_slot_to_rusak(self):
        repo = InMemorySlotParkirRepository()
        service = SlotParkirService(repo)
        
        slot = service.buat_slot(lantai=1, posisi_x=10.0, posisi_y=20.0)
        updated = service.update_status_slot(slot.id, "RUSAK")
        
        assert updated.status_ketersediaan.status == StatusSlot.RUSAK
    
    def test_update_status_slot_not_found(self):
        repo = InMemorySlotParkirRepository()
        service = SlotParkirService(repo)
        
        with pytest.raises(ValueError, match="Slot parkir tidak ditemukan"):
            service.update_status_slot(uuid4(), "TERISI")
    
    def test_update_status_invalid(self):
        repo = InMemorySlotParkirRepository()
        service = SlotParkirService(repo)
        
        slot = service.buat_slot(lantai=1, posisi_x=10.0, posisi_y=20.0)
        
        with pytest.raises(ValueError, match="Status tidak valid"):
            service.update_status_slot(slot.id, "INVALID")
    
    def test_pasang_sensor_ke_slot(self):
        repo = InMemorySlotParkirRepository()
        service = SlotParkirService(repo)
        
        slot = service.buat_slot(lantai=1, posisi_x=10.0, posisi_y=20.0)
        updated = service.pasang_sensor_ke_slot(slot.id, "ULTRASONIK")
        
        assert updated.sensor is not None
        assert updated.sensor.tipe == TipeSensor.ULTRASONIK
    
    def test_lepas_sensor_dari_slot(self):
        repo = InMemorySlotParkirRepository()
        service = SlotParkirService(repo)
        
        slot = service.buat_slot(
            lantai=1,
            posisi_x=10.0,
            posisi_y=20.0,
            tipe_sensor="KAMERA"
        )
        updated = service.lepas_sensor_dari_slot(slot.id)
        
        assert updated.sensor is None
    
    def test_update_kondisi_sensor(self):
        repo = InMemorySlotParkirRepository()
        service = SlotParkirService(repo)
        
        slot = service.buat_slot(
            lantai=1,
            posisi_x=10.0,
            posisi_y=20.0,
            tipe_sensor="KAMERA"
        )
        updated = service.update_kondisi_sensor(slot.id, "Error")
        
        assert updated.sensor.kondisi == "Error"
    
    def test_update_kondisi_sensor_no_sensor(self):
        repo = InMemorySlotParkirRepository()
        service = SlotParkirService(repo)
        
        slot = service.buat_slot(lantai=1, posisi_x=10.0, posisi_y=20.0)
        
        with pytest.raises(ValueError, match="Slot tidak memiliki sensor"):
            service.update_kondisi_sensor(slot.id, "Error")
    
    def test_get_slot_tersedia(self):
        repo = InMemorySlotParkirRepository()
        service = SlotParkirService(repo)
        
        service.buat_slot(lantai=1, posisi_x=10.0, posisi_y=20.0)
        service.buat_slot(lantai=1, posisi_x=15.0, posisi_y=20.0)
        
        slots = service.get_slot_tersedia()
        assert len(slots) == 2
    
    def test_get_slot_tersedia_filter_lantai(self):
        repo = InMemorySlotParkirRepository()
        service = SlotParkirService(repo)
        
        service.buat_slot(lantai=1, posisi_x=10.0, posisi_y=20.0)
        service.buat_slot(lantai=2, posisi_x=10.0, posisi_y=20.0)
        
        slots = service.get_slot_tersedia(lantai=1)
        assert len(slots) == 1
        assert slots[0].koordinat.lantai == 1
    
    def test_get_statistik_slot(self):
        repo = InMemorySlotParkirRepository()
        service = SlotParkirService(repo)
        
        slot1 = service.buat_slot(lantai=1, posisi_x=10.0, posisi_y=20.0)
        service.buat_slot(lantai=1, posisi_x=15.0, posisi_y=20.0)
        service.update_status_slot(slot1.id, "TERISI")
        
        stats = service.get_statistik_slot()
        assert stats["total"] == 2
        assert stats["tersedia"] == 1
        assert stats["terisi"] == 1
        assert stats["rusak"] == 0
        assert stats["persentase_okupansi"] == 50.0
    
    def test_get_statistik_per_lantai(self):
        repo = InMemorySlotParkirRepository()
        service = SlotParkirService(repo)
        
        service.buat_slot(lantai=1, posisi_x=10.0, posisi_y=20.0)
        service.buat_slot(lantai=1, posisi_x=15.0, posisi_y=20.0)
        service.buat_slot(lantai=2, posisi_x=10.0, posisi_y=20.0)
        
        stats = service.get_statistik_per_lantai()
        assert 1 in stats
        assert 2 in stats
        assert stats[1]["total"] == 2
        assert stats[2]["total"] == 1
