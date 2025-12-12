import pytest
from datetime import datetime
from decimal import Decimal

from src.manajemen_parkir.domain.tariff import (
    Durasi, BiayaFinal, TarifParkir, JenisTarif, TipeKendaraan, ParkingTariff
)


class TestDurasiTariff:
    def test_hitung_dari_waktu(self):
        waktu_masuk = datetime(2024, 1, 1, 10, 0, 0)
        waktu_keluar = datetime(2024, 1, 1, 12, 30, 0)
        
        durasi = Durasi.hitung_dari_waktu(waktu_masuk, waktu_keluar)
        assert durasi.total_jam == 2
        assert durasi.total_menit == 30
    
    def test_hitung_dari_waktu_invalid(self):
        waktu_masuk = datetime(2024, 1, 1, 12, 0, 0)
        waktu_keluar = datetime(2024, 1, 1, 10, 0, 0)
        
        with pytest.raises(ValueError, match="Waktu keluar tidak boleh lebih awal"):
            Durasi.hitung_dari_waktu(waktu_masuk, waktu_keluar)
    
    def test_ke_jam_penuh_with_minutes(self):
        durasi = Durasi(total_jam=2, total_menit=30)
        assert durasi.ke_jam_penuh() == 3
    
    def test_ke_jam_penuh_without_minutes(self):
        durasi = Durasi(total_jam=2, total_menit=0)
        assert durasi.ke_jam_penuh() == 2
    
    def test_durasi_str(self):
        durasi = Durasi(total_jam=2, total_menit=30)
        assert str(durasi) == "2 jam 30 menit"


class TestBiayaFinalTariff:
    def test_create_biaya_final(self):
        biaya = BiayaFinal(jumlah=Decimal("15000"), keterangan="Tarif reguler")
        assert biaya.jumlah == Decimal("15000")
        assert biaya.keterangan == "Tarif reguler"
    
    def test_biaya_negative(self):
        with pytest.raises(ValueError, match="BiayaFinal tidak boleh negatif"):
            BiayaFinal(jumlah=Decimal("-1000"))
    
    def test_format_rupiah(self):
        biaya = BiayaFinal(jumlah=Decimal("15000"))
        assert "15,000" in biaya.format_rupiah()
        assert "Rp" in biaya.format_rupiah()
    
    def test_biaya_str(self):
        biaya = BiayaFinal(jumlah=Decimal("15000"))
        assert "Rp" in str(biaya)


class TestTarifParkir:
    def test_create_tarif(self):
        tarif = TarifParkir.create(
            nama="Tarif Reguler",
            tipe_kendaraan=TipeKendaraan.MOBIL,
            harga_per_jam=Decimal("5000")
        )
        assert tarif.nama == "Tarif Reguler"
        assert tarif.tipe_kendaraan == TipeKendaraan.MOBIL
        assert tarif.harga_per_jam == Decimal("5000")
        assert tarif.jenis_tarif == JenisTarif.REGULER
        assert tarif.is_active is True
    
    def test_create_tarif_with_max_daily(self):
        tarif = TarifParkir.create(
            nama="Tarif Premium",
            tipe_kendaraan=TipeKendaraan.MOBIL,
            harga_per_jam=Decimal("10000"),
            harga_maksimum_harian=Decimal("50000")
        )
        assert tarif.harga_maksimum_harian == Decimal("50000")
    
    def test_create_tarif_negative_price(self):
        with pytest.raises(ValueError, match="Harga per jam tidak boleh negatif"):
            TarifParkir.create(
                nama="Invalid",
                tipe_kendaraan=TipeKendaraan.MOBIL,
                harga_per_jam=Decimal("-5000")
            )
    
    def test_create_tarif_invalid_max_daily(self):
        with pytest.raises(ValueError, match="Harga maksimum harian harus lebih besar"):
            TarifParkir.create(
                nama="Invalid",
                tipe_kendaraan=TipeKendaraan.MOBIL,
                harga_per_jam=Decimal("10000"),
                harga_maksimum_harian=Decimal("5000")
            )
    
    def test_hitung_biaya_basic(self):
        tarif = TarifParkir.create(
            nama="Tarif Reguler",
            tipe_kendaraan=TipeKendaraan.MOBIL,
            harga_per_jam=Decimal("5000")
        )
        durasi = Durasi(total_jam=2, total_menit=30)
        
        biaya = tarif.hitung_biaya(durasi)
        assert biaya.jumlah == Decimal("15000")
    
    def test_hitung_biaya_with_max_daily(self):
        tarif = TarifParkir.create(
            nama="Tarif Premium",
            tipe_kendaraan=TipeKendaraan.MOBIL,
            harga_per_jam=Decimal("10000"),
            harga_maksimum_harian=Decimal("50000")
        )
        durasi = Durasi(total_jam=10, total_menit=0)
        
        biaya = tarif.hitung_biaya(durasi)
        assert biaya.jumlah == Decimal("50000")
        assert "maksimum harian" in biaya.keterangan.lower()
    
    def test_update_harga(self):
        tarif = TarifParkir.create(
            nama="Tarif Reguler",
            tipe_kendaraan=TipeKendaraan.MOBIL,
            harga_per_jam=Decimal("5000")
        )
        
        tarif.update_harga(Decimal("7000"), Decimal("50000"))
        assert tarif.harga_per_jam == Decimal("7000")
        assert tarif.harga_maksimum_harian == Decimal("50000")
    
    def test_update_harga_negative(self):
        tarif = TarifParkir.create(
            nama="Tarif Reguler",
            tipe_kendaraan=TipeKendaraan.MOBIL,
            harga_per_jam=Decimal("5000")
        )
        
        with pytest.raises(ValueError, match="Harga per jam tidak boleh negatif"):
            tarif.update_harga(Decimal("-1000"))
    
    def test_nonaktifkan_tarif(self):
        tarif = TarifParkir.create(
            nama="Tarif Reguler",
            tipe_kendaraan=TipeKendaraan.MOBIL,
            harga_per_jam=Decimal("5000")
        )
        
        tarif.nonaktifkan()
        assert tarif.is_active is False
    
    def test_aktifkan_tarif(self):
        tarif = TarifParkir.create(
            nama="Tarif Reguler",
            tipe_kendaraan=TipeKendaraan.MOBIL,
            harga_per_jam=Decimal("5000")
        )
        tarif.nonaktifkan()
        
        tarif.aktifkan()
        assert tarif.is_active is True


class TestParkingTariffLegacy:
    def test_calculate_basic(self):
        tariff = ParkingTariff(price_per_hour=5000.0)
        checkin = datetime(2024, 1, 1, 10, 0, 0)
        checkout = datetime(2024, 1, 1, 12, 30, 0)
        
        fee = tariff.calculate(checkin, checkout)
        assert fee == 15000.0
    
    def test_calculate_with_max_daily(self):
        tariff = ParkingTariff(price_per_hour=5000.0, max_daily=20000.0)
        checkin = datetime(2024, 1, 1, 10, 0, 0)
        checkout = datetime(2024, 1, 1, 22, 0, 0)
        
        fee = tariff.calculate(checkin, checkout)
        assert fee == 20000.0
