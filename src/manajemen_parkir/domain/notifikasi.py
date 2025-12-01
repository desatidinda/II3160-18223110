from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class TipePesan(Enum):
    EMAIL = "EMAIL"
    PUSH = "PUSH"
    SMS = "SMS"


class StatusPengirimanEnum(Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"



@dataclass(frozen=True)
class TujuanKomunikasi:
    tipe: TipePesan
    alamat: str
    
    def __post_init__(self):
        if not self.alamat:
            raise ValueError("Alamat tujuan tidak boleh kosong")
        
        if self.tipe == TipePesan.EMAIL and "@" not in self.alamat:
            raise ValueError("Format email tidak valid")
        if self.tipe == TipePesan.SMS and not self.alamat.startswith("+"):
            raise ValueError("Nomor telepon harus dimulai dengan +")


@dataclass(frozen=True)
class KontenPesan:
    subjek: str
    badan_pesan: str
    template_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.badan_pesan:
            raise ValueError("Badan pesan tidak boleh kosong")


@dataclass(frozen=True)
class StatusPengiriman:
    status: StatusPengirimanEnum
    waktu_kirim: Optional[datetime]
    kode_status_eksternal: Optional[str] = None
    pesan_error: Optional[str] = None
    
    @staticmethod
    def pending():
        return StatusPengiriman(
            status=StatusPengirimanEnum.PENDING,
            waktu_kirim=None
        )
    
    @staticmethod
    def sent(waktu_kirim: datetime, kode_status: Optional[str] = None):
        return StatusPengiriman(
            status=StatusPengirimanEnum.SENT,
            waktu_kirim=waktu_kirim,
            kode_status_eksternal=kode_status
        )
    
    @staticmethod
    def delivered(waktu_kirim: datetime, kode_status: Optional[str] = None):
        return StatusPengiriman(
            status=StatusPengirimanEnum.DELIVERED,
            waktu_kirim=waktu_kirim,
            kode_status_eksternal=kode_status
        )
    
    @staticmethod
    def failed(pesan_error: str):
        return StatusPengiriman(
            status=StatusPengirimanEnum.FAILED,
            waktu_kirim=None,
            pesan_error=pesan_error
        )


# Aggregate Root
@dataclass
class Pesan:
    id: UUID
    tipe: TipePesan
    tujuan: TujuanKomunikasi
    konten: KontenPesan
    status_pengiriman: StatusPengiriman
    prioritas: int = 0 
    retry_count: int = 0
    max_retry: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @staticmethod
    def create(
        tipe: TipePesan,
        alamat_tujuan: str,
        subjek: str,
        badan_pesan: str,
        template_id: Optional[str] = None,
        prioritas: int = 0
    ) -> 'Pesan':
        tujuan = TujuanKomunikasi(tipe=tipe, alamat=alamat_tujuan)
        konten = KontenPesan(
            subjek=subjek,
            badan_pesan=badan_pesan,
            template_id=template_id
        )
        return Pesan(
            id=uuid4(),
            tipe=tipe,
            tujuan=tujuan,
            konten=konten,
            status_pengiriman=StatusPengiriman.pending(),
            prioritas=prioritas
        )
    
    def tandai_terkirim(self, kode_status: Optional[str] = None):
        self.status_pengiriman = StatusPengiriman.sent(
            waktu_kirim=datetime.now(),
            kode_status=kode_status
        )
        self.updated_at = datetime.now()
    
    def tandai_delivered(self, kode_status: Optional[str] = None):
        self.status_pengiriman = StatusPengiriman.delivered(
            waktu_kirim=datetime.now(),
            kode_status=kode_status
        )
        self.updated_at = datetime.now()
    
    def tandai_gagal(self, pesan_error: str):
        self.status_pengiriman = StatusPengiriman.failed(pesan_error)
        self.updated_at = datetime.now()
    
    def retry(self) -> bool:
        if self.retry_count >= self.max_retry:
            return False
        self.retry_count += 1
        self.status_pengiriman = StatusPengiriman.pending()
        self.updated_at = datetime.now()
        return True
    
    def can_retry(self) -> bool:
        return self.retry_count < self.max_retry
