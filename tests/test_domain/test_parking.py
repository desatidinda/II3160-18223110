import pytest
from datetime import datetime
from decimal import Decimal

from src.manajemen_parkir.domain.model import SesiParkir, StatusSesi
from src.manajemen_parkir.domain.value_objects import NomorPlat, Durasi, BiayaFinal
from src.manajemen_parkir.domain.tariff import ParkingTariff


class TestDurasi:
    def test_create_durasi(self):
        durasi = Durasi(total_menit=90)
        assert durasi.total_menit == 90
    
    def test_durasi_total_jam(self):
        durasi = Durasi(total_menit=90)
        assert durasi.total_jam == 2
    
    def test_durasi_total_jam_round_up(self):
        durasi = Durasi(total_menit=61)
        assert durasi.total_jam == 2
    
    def test_durasi_total_jam_exact(self):
        durasi = Durasi(total_menit=60)
        assert durasi.total_jam == 1
    
    def test_durasi_zero_minutes(self):
        durasi = Durasi(total_menit=0)
        assert durasi.total_jam == 1
    
    def test_durasi_immutable(self):
        durasi = Durasi(total_menit=90)
        with pytest.raises(Exception):
            durasi.total_menit = 120


class TestBiayaFinal:
    def test_create_biaya_final(self):
        biaya = BiayaFinal(jumlah=Decimal("15000"))
        assert biaya.jumlah == Decimal("15000")
        assert biaya.mata_uang == "IDR"
    
    def test_biaya_final_custom_currency(self):
        biaya = BiayaFinal(jumlah=Decimal("100"), mata_uang="USD")
        assert biaya.mata_uang == "USD"
    
    def test_biaya_final_immutable(self):
        biaya = BiayaFinal(jumlah=Decimal("15000"))
        with pytest.raises(Exception):
            biaya.jumlah = Decimal("20000")


class TestSesiParkir:
    def test_create_sesi_parkir(self):
        nomor_plat = NomorPlat(kode="B1234XYZ", tipe_kendaraan="MOBIL")
        sesi = SesiParkir(nomor_plat=nomor_plat)
        
        assert sesi.nomor_plat == nomor_plat
        assert sesi.status == StatusSesi.AKTIF
        assert sesi.waktu_keluar is None
        assert sesi.durasi is None
        assert sesi.biaya_final is None
        assert isinstance(sesi.waktu_masuk, datetime)
    
    def test_checkout_success(self):
        nomor_plat = NomorPlat(kode="B1234XYZ")
        sesi = SesiParkir(nomor_plat=nomor_plat)
        tarif = ParkingTariff(price_per_hour=5000.0)
        
        sesi.check_out(tarif)
        
        assert sesi.status == StatusSesi.SELESAI
        assert sesi.waktu_keluar is not None
        assert sesi.durasi is not None
        assert sesi.biaya_final is not None
        assert isinstance(sesi.biaya_final.jumlah, Decimal)
    
    def test_checkout_already_finished(self):
        nomor_plat = NomorPlat(kode="B1234XYZ")
        sesi = SesiParkir(nomor_plat=nomor_plat)
        tarif = ParkingTariff(price_per_hour=5000.0)
        
        sesi.check_out(tarif)
        
        with pytest.raises(ValueError, match="Sesi sudah berakhir atau dibatalkan"):
            sesi.check_out(tarif)
    
    def test_sesi_with_owner_vehicle(self):
        nomor_plat = NomorPlat(kode="B1234XYZ")
        from uuid import uuid4
        owner_id = uuid4()
        vehicle_id = uuid4()
        
        sesi = SesiParkir(
            nomor_plat=nomor_plat,
            owner_id=owner_id,
            vehicle_id=vehicle_id
        )
        
        assert sesi.owner_id == owner_id
        assert sesi.vehicle_id == vehicle_id


class TestStatusSesi:
    def test_status_sesi_values(self):
        assert StatusSesi.AKTIF == "AKTIF"
        assert StatusSesi.SELESAI == "SELESAI"
        assert StatusSesi.DIBATALKAN == "DIBATALKAN"
