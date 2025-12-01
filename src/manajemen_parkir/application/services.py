from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from manajemen_parkir.domain.model import SesiParkir
from manajemen_parkir.infrastructure.repository import InMemorySesiParkirRepository
from manajemen_parkir.domain.tariff import ParkingTariff
from manajemen_parkir.domain.auth import Akun, Kredensial, Peran, TokenAkses
from manajemen_parkir.infrastructure.auth_repository import InMemoryAuthRepository


class AuthService:
    
    SECRET_KEY = "your-secret-key-change-in-production"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    def __init__(self, repo: Optional[InMemoryAuthRepository] = None, user_repo=None):
        self.repo = repo or InMemoryAuthRepository()
        self.user_repo = user_repo

    def register(
        self, username: str, password: str, email: Optional[str] = None, peran: Peran = Peran.PENGGUNA
    ) -> tuple[Akun, Optional[any]]:
        if self.repo.username_exists(username):
            raise ValueError(f"Username '{username}' sudah terdaftar")
        
        password_hash = self._hash_password(password)
        
        akun = Akun.create(
            username=username,
            password_hash=password_hash,
            peran=peran,
            email=email,
        )
        
        self.repo.save(akun)
        
        user = None
        if self.user_repo:
            from manajemen_parkir.domain.user import User
            user = User.create(name=username, email=email, akun_id=akun.id)
            self.user_repo.save(user)
        
        return akun, user

    def login(self, username: str, password: str) -> TokenAkses:
        akun = self.repo.get_by_username(username)
        
        if not akun:
            raise ValueError("Username atau password salah")
        
        if not akun.is_active:
            raise ValueError("Akun tidak aktif")
        
        if not self._verify_password(password, akun.kredensial.password_hash):
            raise ValueError("Username atau password salah")
        
        token = self._create_access_token(
            data={"sub": username, "akun_id": str(akun.id), "peran": akun.peran.value}
        )
        
        token_akses = akun.issue_token(token, self.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.repo.save(akun)
        
        return token_akses

    def verify_token(self, token: str) -> Akun:
        try:
            payload = self._decode_token(token)
            username: str = payload.get("sub")
            if username is None:
                raise ValueError("Token tidak valid")
            
            akun = self.repo.get_by_username(username)
            if akun is None:
                raise ValueError("Akun tidak ditemukan")
            
            if not akun.is_active:
                raise ValueError("Akun tidak aktif")
            
            return akun
            
        except Exception as e:
            raise ValueError(f"Token tidak valid: {str(e)}")

    def _hash_password(self, password: str) -> str:
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password = password[:72]
        
        try:
            import bcrypt
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        except ImportError:
            try:
                from passlib.context import CryptContext
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                return pwd_context.hash(password)
            except Exception:
                import hashlib
                return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            plain_password = plain_password[:72]
        
        try:
            import bcrypt
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except ImportError:
            try:
                from passlib.context import CryptContext
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                return pwd_context.verify(plain_password, hashed_password)
            except Exception:
                import hashlib
                return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

    def _create_access_token(self, data: dict) -> str:
        try:
            from jose import jwt
            to_encode = data.copy()
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
            return encoded_jwt
        except ImportError:
            import json
            import base64
            return base64.b64encode(json.dumps(data).encode()).decode()

    def _decode_token(self, token: str) -> dict:
        try:
            from jose import jwt, JWTError
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except ImportError:
            # Fallback sederhana
            import json
            import base64
            return json.loads(base64.b64decode(token.encode()).decode())


class ParkingService:
    def __init__(self, repo: Optional[InMemorySesiParkirRepository] = None, slot_service=None):
        self.repo = repo or InMemorySesiParkirRepository()
        self.tarif = ParkingTariff(price_per_hour=3000.0, max_daily=50000.0)
        self.slot_service = slot_service 

    def start_parking(
        self,
        kode_plat: str,
        tipe_kendaraan: Optional[str] = None,
        user_id: Optional[UUID] = None,
        vehicle_id: Optional[UUID] = None,
        slot_id: Optional[UUID] = None,
    ) -> SesiParkir:
        from manajemen_parkir.domain.value_objects import NomorPlat

        nomor = NomorPlat(kode=kode_plat, tipe_kendaraan=tipe_kendaraan)
        sesi = SesiParkir(nomor_plat=nomor, owner_id=user_id, vehicle_id=vehicle_id)
        self.repo.save(sesi)
        
        if slot_id and self.slot_service:
            try:
                self.slot_service.update_status_slot(slot_id, "TERISI")
            except ValueError:
                pass
        
        return sesi

    def end_parking(self, id_sesi: UUID, slot_id: Optional[UUID] = None) -> SesiParkir:
        sesi = self.repo.get_by_id(id_sesi)
        if not sesi:
            raise ValueError("Sesi parkir tidak ditemukan")
        sesi.check_out(self.tarif)
        self.repo.save(sesi)
        
        if slot_id and self.slot_service:
            try:
                self.slot_service.update_status_slot(slot_id, "TERSEDIA")
            except ValueError:
                pass
        
        return sesi

    def get(self, id_sesi: UUID) -> Optional[SesiParkir]:
        return self.repo.get_by_id(id_sesi)

    def list(self):
        return self.repo.list()
