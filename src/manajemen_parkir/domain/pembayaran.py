from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4
from decimal import Decimal


class StatusPembayaran(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class KodeMataUang(Enum):
    IDR = "IDR"
    USD = "USD"
    EUR = "EUR"


@dataclass(frozen=True)
class Invoice:
    id_invoice: UUID
    id_sesi_parkir: UUID
    deskripsi: str
    
    def __post_init__(self):
        if not self.deskripsi:
            raise ValueError("Deskripsi invoice tidak boleh kosong")


@dataclass(frozen=True)
class JumlahTagihan:
    jumlah: Decimal
    kode_mata_uang: KodeMataUang
    
    def __post_init__(self):
        if self.jumlah < 0:
            raise ValueError("Jumlah tagihan tidak boleh negatif")
    
    def format_rupiah(self) -> str:
        if self.kode_mata_uang != KodeMataUang.IDR:
            raise ValueError("Hanya support format Rupiah")
        return f"Rp {self.jumlah:,.2f}"


@dataclass(frozen=True)
class CallbackData:
    waktu_callback: datetime
    kode_respon: str
    pesan: str
    external_transaction_id: Optional[str] = None


@dataclass
class Pembayaran:
    id: UUID
    id_transaksi: UUID  # dari BC Manajemen Parkir
    invoice: Invoice
    jumlah_tagihan: JumlahTagihan
    status: StatusPembayaran
    metode_pembayaran: str
    callback_data: Optional[CallbackData] = None
    external_payment_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @staticmethod
    def create(
        id_transaksi: UUID,
        id_sesi_parkir: UUID,
        jumlah: Decimal,
        deskripsi: str,
        metode_pembayaran: str,
        kode_mata_uang: KodeMataUang = KodeMataUang.IDR
    ) -> 'Pembayaran':
        invoice = Invoice(
            id_invoice=uuid4(),
            id_sesi_parkir=id_sesi_parkir,
            deskripsi=deskripsi
        )
        jumlah_tagihan = JumlahTagihan(
            jumlah=jumlah,
            kode_mata_uang=kode_mata_uang
        )
        return Pembayaran(
            id=uuid4(),
            id_transaksi=id_transaksi,
            invoice=invoice,
            jumlah_tagihan=jumlah_tagihan,
            status=StatusPembayaran.PENDING,
            metode_pembayaran=metode_pembayaran
        )
    
    def tandai_sukses(self, callback_data: CallbackData):
        if self.status == StatusPembayaran.SUCCESS:
            raise ValueError("Pembayaran sudah sukses")
        self.status = StatusPembayaran.SUCCESS
        self.callback_data = callback_data
        self.updated_at = datetime.now()
    
    def tandai_gagal(self, callback_data: CallbackData):
        if self.status == StatusPembayaran.SUCCESS:
            raise ValueError("Pembayaran sudah sukses, tidak bisa digagalkan")
        self.status = StatusPembayaran.FAILED
        self.callback_data = callback_data
        self.updated_at = datetime.now()
    
    def batalkan(self):
        if self.status == StatusPembayaran.SUCCESS:
            raise ValueError("Pembayaran sudah sukses, tidak bisa dibatalkan")
        self.status = StatusPembayaran.CANCELLED
        self.updated_at = datetime.now()
    
    def set_external_payment_id(self, external_id: str):
        self.external_payment_id = external_id
        self.updated_at = datetime.now()
