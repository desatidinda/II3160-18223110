from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class Peran(str, Enum):
    ADMIN = "ADMIN"
    PETUGAS = "PETUGAS"
    PENGGUNA = "PENGGUNA"


@dataclass(frozen=True)
class Kredensial:
    username: str
    password_hash: str

    def __post_init__(self):
        if not self.username or len(self.username.strip()) == 0:
            raise ValueError("Username tidak boleh kosong")
        if not self.password_hash:
            raise ValueError("Password hash tidak boleh kosong")


@dataclass(frozen=True)
class TokenAkses:
    token: str
    expires_at: datetime
    token_type: str = "bearer"

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at


@dataclass
class Akun:
    kredensial: Kredensial
    peran: Peran
    id: UUID = field(default_factory=uuid4)
    email: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    current_token: Optional[TokenAkses] = None

    @staticmethod
    def create(
        username: str,
        password_hash: str,
        peran: Peran = Peran.PENGGUNA,
        email: Optional[str] = None,
    ) -> Akun:
        kredensial = Kredensial(username=username, password_hash=password_hash)
        return Akun(
            kredensial=kredensial,
            peran=peran,
            email=email,
        )

    def issue_token(self, token: str, expires_in_minutes: int = 30) -> TokenAkses:
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        token_akses = TokenAkses(token=token, expires_at=expires_at)
        self.current_token = token_akses
        return token_akses

    def revoke_token(self) -> None:
        self.current_token = None

    def deactivate(self) -> None:
        self.is_active = False
        self.revoke_token()

    def activate(self) -> None:
        self.is_active = True
