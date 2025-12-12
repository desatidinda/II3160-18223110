import pytest
from datetime import datetime

from src.manajemen_parkir.domain.alokasi_slot import (
    Koordinat, StatusKetersediaan, StatusSlot, TipeSensor, Sensor, SlotParkir
)


class TestKoordinat:
    def test_create_koordinat(self):
        koordinat = Koordinat(lantai=1, posisi_x=10.5, posisi_y=20.3)
        assert koordinat.lantai == 1
        assert koordinat.posisi_x == 10.5
        assert koordinat.posisi_y == 20.3
    
    def test_koordinat_negative_lantai(self):
        with pytest.raises(ValueError, match="Lantai tidak boleh negatif"):
            Koordinat(lantai=-1, posisi_x=10.0, posisi_y=20.0)
    
    def test_koordinat_zero_lantai(self):
        koordinat = Koordinat(lantai=0, posisi_x=10.0, posisi_y=20.0)
        assert koordinat.lantai == 0
    
    def test_koordinat_immutable(self):
        koordinat = Koordinat(lantai=1, posisi_x=10.0, posisi_y=20.0)
        with pytest.raises(Exception):
            koordinat.lantai = 2


class TestStatusKetersediaan:
    def test_create_tersedia(self):
        status = StatusKetersediaan.tersedia()
        assert status.status == StatusSlot.TERSEDIA
        assert isinstance(status.waktu_update, datetime)
    
    def test_create_terisi(self):
        status = StatusKetersediaan.terisi()
        assert status.status == StatusSlot.TERISI
        assert isinstance(status.waktu_update, datetime)
    
    def test_create_rusak(self):
        status = StatusKetersediaan.rusak()
        assert status.status == StatusSlot.RUSAK
        assert isinstance(status.waktu_update, datetime)
    
    def test_status_immutable(self):
        status = StatusKetersediaan.tersedia()
        with pytest.raises(Exception):
            status.status = StatusSlot.TERISI


class TestTipeSensor:
    def test_tipe_sensor_values(self):
        assert TipeSensor.KAMERA.value == "KAMERA"
        assert TipeSensor.ULTRASONIK.value == "ULTRASONIK"
        assert TipeSensor.INFRARED.value == "INFRARED"
    
    def test_tipe_sensor_from_string(self):
        assert TipeSensor["KAMERA"] == TipeSensor.KAMERA
        assert TipeSensor["ULTRASONIK"] == TipeSensor.ULTRASONIK
        assert TipeSensor["INFRARED"] == TipeSensor.INFRARED


class TestSensor:
    def test_create_sensor(self):
        sensor = Sensor.create(tipe=TipeSensor.KAMERA, kondisi="Normal")
        assert sensor.tipe == TipeSensor.KAMERA
        assert sensor.kondisi == "Normal"
        assert sensor.is_active is True
        assert sensor.id is not None
    
    def test_sensor_default_kondisi(self):
        sensor = Sensor.create(tipe=TipeSensor.ULTRASONIK)
        assert sensor.kondisi == "Normal"
    
    def test_update_kondisi_sensor(self):
        sensor = Sensor.create(tipe=TipeSensor.KAMERA)
        sensor.update_kondisi("Error")
        assert sensor.kondisi == "Error"
    
    def test_activate_sensor(self):
        sensor = Sensor.create(tipe=TipeSensor.INFRARED)
        sensor.is_active = False
        sensor.activate()
        assert sensor.is_active is True
    
    def test_deactivate_sensor(self):
        sensor = Sensor.create(tipe=TipeSensor.KAMERA)
        sensor.deactivate()
        assert sensor.is_active is False
    
    def test_sensor_unique_id(self):
        sensor1 = Sensor.create(tipe=TipeSensor.KAMERA)
        sensor2 = Sensor.create(tipe=TipeSensor.KAMERA)
        assert sensor1.id != sensor2.id


class TestSlotParkir:
    def test_create_slot_basic(self):
        slot = SlotParkir.create(lantai=1, posisi_x=10.0, posisi_y=20.0)
        assert slot.koordinat.lantai == 1
        assert slot.koordinat.posisi_x == 10.0
        assert slot.koordinat.posisi_y == 20.0
        assert slot.kapasitas == 1
        assert slot.status_ketersediaan.status == StatusSlot.TERSEDIA
        assert slot.sensor is None
    
    def test_create_slot_with_sensor(self):
        sensor = Sensor.create(tipe=TipeSensor.KAMERA)
        slot = SlotParkir.create(
            lantai=1,
            posisi_x=10.0,
            posisi_y=20.0,
            sensor=sensor
        )
        assert slot.sensor == sensor
    
    def test_create_slot_with_keterangan(self):
        slot = SlotParkir.create(
            lantai=1,
            posisi_x=10.0,
            posisi_y=20.0,
            keterangan="Dekat pintu masuk"
        )
        assert slot.keterangan == "Dekat pintu masuk"
    
    def test_tandai_tersedia(self):
        slot = SlotParkir.create(lantai=1, posisi_x=10.0, posisi_y=20.0)
        old_update = slot.status_ketersediaan.waktu_update
        
        slot.tandai_tersedia()
        assert slot.status_ketersediaan.status == StatusSlot.TERSEDIA
        assert slot.updated_at >= old_update
    
    def test_tandai_terisi(self):
        slot = SlotParkir.create(lantai=1, posisi_x=10.0, posisi_y=20.0)
        slot.tandai_terisi()
        assert slot.status_ketersediaan.status == StatusSlot.TERISI
    
    def test_tandai_terisi_when_rusak(self):
        slot = SlotParkir.create(lantai=1, posisi_x=10.0, posisi_y=20.0)
        slot.tandai_rusak()
        
        with pytest.raises(ValueError, match="Slot rusak tidak bisa diisi"):
            slot.tandai_terisi()
    
    def test_tandai_rusak(self):
        slot = SlotParkir.create(lantai=1, posisi_x=10.0, posisi_y=20.0)
        slot.tandai_rusak()
        assert slot.status_ketersediaan.status == StatusSlot.RUSAK
    
    def test_pasang_sensor(self):
        slot = SlotParkir.create(lantai=1, posisi_x=10.0, posisi_y=20.0)
        sensor = Sensor.create(tipe=TipeSensor.ULTRASONIK)
        
        slot.pasang_sensor(sensor)
        assert slot.sensor == sensor
    
    def test_lepas_sensor(self):
        sensor = Sensor.create(tipe=TipeSensor.KAMERA)
        slot = SlotParkir.create(
            lantai=1,
            posisi_x=10.0,
            posisi_y=20.0,
            sensor=sensor
        )
        
        slot.lepas_sensor()
        assert slot.sensor is None
    
    def test_is_tersedia_true(self):
        slot = SlotParkir.create(lantai=1, posisi_x=10.0, posisi_y=20.0)
        assert slot.is_tersedia() is True
    
    def test_is_tersedia_false_when_terisi(self):
        slot = SlotParkir.create(lantai=1, posisi_x=10.0, posisi_y=20.0)
        slot.tandai_terisi()
        assert slot.is_tersedia() is False
    
    def test_is_tersedia_false_when_rusak(self):
        slot = SlotParkir.create(lantai=1, posisi_x=10.0, posisi_y=20.0)
        slot.tandai_rusak()
        assert slot.is_tersedia() is False
    
    def test_slot_unique_id(self):
        slot1 = SlotParkir.create(lantai=1, posisi_x=10.0, posisi_y=20.0)
        slot2 = SlotParkir.create(lantai=1, posisi_x=15.0, posisi_y=20.0)
        assert slot1.id != slot2.id
    
    def test_slot_custom_kapasitas(self):
        slot = SlotParkir.create(
            lantai=1,
            posisi_x=10.0,
            posisi_y=20.0,
            kapasitas=2
        )
        assert slot.kapasitas == 2
