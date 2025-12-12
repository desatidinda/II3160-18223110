import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from src.manajemen_parkir.domain.auth import Akun, Kredensial, Peran, TokenAkses


class TestKredensial:
    def test_create_valid_kredensial(self):
        kredensial = Kredensial(username="testuser", password_hash="hashed_pwd")
        assert kredensial.username == "testuser"
        assert kredensial.password_hash == "hashed_pwd"
    
    def test_kredensial_empty_username(self):
        with pytest.raises(ValueError, match="Username tidak boleh kosong"):
            Kredensial(username="", password_hash="hashed_pwd")
    
    def test_kredensial_whitespace_username(self):
        with pytest.raises(ValueError, match="Username tidak boleh kosong"):
            Kredensial(username="   ", password_hash="hashed_pwd")
    
    def test_kredensial_empty_password_hash(self):
        with pytest.raises(ValueError, match="Password hash tidak boleh kosong"):
            Kredensial(username="testuser", password_hash="")
    
    def test_kredensial_immutable(self):
        kredensial = Kredensial(username="testuser", password_hash="hashed_pwd")
        with pytest.raises(Exception):
            kredensial.username = "newuser"


class TestPeran:
    def test_peran_values(self):
        assert Peran.ADMIN.value == "ADMIN"
        assert Peran.PETUGAS.value == "PETUGAS"
        assert Peran.PENGGUNA.value == "PENGGUNA"
    
    def test_peran_from_string(self):
        assert Peran("ADMIN") == Peran.ADMIN
        assert Peran("PETUGAS") == Peran.PETUGAS
        assert Peran("PENGGUNA") == Peran.PENGGUNA
    
    def test_peran_invalid(self):
        with pytest.raises(ValueError):
            Peran("INVALID_ROLE")


class TestTokenAkses:
    def test_create_token(self):
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        token = TokenAkses(token="abc123", expires_at=expires_at)
        assert token.token == "abc123"
        assert token.token_type == "bearer"
        assert token.expires_at == expires_at
    
    def test_token_not_expired(self):
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        token = TokenAkses(token="abc123", expires_at=expires_at)
        assert not token.is_expired()
    
    def test_token_expired(self):
        expires_at = datetime.utcnow() - timedelta(minutes=1)
        token = TokenAkses(token="abc123", expires_at=expires_at)
        assert token.is_expired()
    
    def test_token_custom_type(self):
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        token = TokenAkses(token="abc123", expires_at=expires_at, token_type="custom")
        assert token.token_type == "custom"
    
    def test_token_immutable(self):
        expires_at = datetime.utcnow() + timedelta(minutes=30)
        token = TokenAkses(token="abc123", expires_at=expires_at)
        with pytest.raises(Exception):
            token.token = "new_token"


class TestAkun:
    def test_create_akun_factory(self):
        akun = Akun.create(
            username="testuser",
            password_hash="hashed_pwd",
            peran=Peran.PENGGUNA,
            email="test@example.com"
        )
        assert akun.kredensial.username == "testuser"
        assert akun.peran == Peran.PENGGUNA
        assert akun.email == "test@example.com"
        assert akun.is_active is True
        assert akun.current_token is None
    
    def test_create_akun_default_values(self):
        akun = Akun.create(
            username="testuser",
            password_hash="hashed_pwd",
            peran=Peran.ADMIN
        )
        assert akun.email is None
        assert akun.is_active is True
        assert isinstance(akun.created_at, datetime)
    
    def test_issue_token(self):
        akun = Akun.create(
            username="testuser",
            password_hash="hashed_pwd",
            peran=Peran.PENGGUNA
        )
        token = akun.issue_token("jwt_token_string", expires_in_minutes=30)
        
        assert token.token == "jwt_token_string"
        assert token.token_type == "bearer"
        assert akun.current_token == token
        assert not token.is_expired()
    
    def test_revoke_token(self):
        akun = Akun.create(
            username="testuser",
            password_hash="hashed_pwd",
            peran=Peran.PENGGUNA
        )
        akun.issue_token("jwt_token_string", expires_in_minutes=30)
        assert akun.current_token is not None
        
        akun.revoke_token()
        assert akun.current_token is None
    
    def test_deactivate_akun(self):
        akun = Akun.create(
            username="testuser",
            password_hash="hashed_pwd",
            peran=Peran.PENGGUNA
        )
        assert akun.is_active is True
        
        akun.deactivate()
        assert akun.is_active is False
    
    def test_activate_akun(self):
        akun = Akun.create(
            username="testuser",
            password_hash="hashed_pwd",
            peran=Peran.PENGGUNA
        )
        akun.deactivate()
        assert akun.is_active is False
        
        akun.activate()
        assert akun.is_active is True
    
    def test_akun_has_unique_id(self):
        akun1 = Akun.create(username="user1", password_hash="hash1", peran=Peran.PENGGUNA)
        akun2 = Akun.create(username="user2", password_hash="hash2", peran=Peran.PENGGUNA)
        assert akun1.id != akun2.id
    
    def test_akun_different_roles(self):
        admin = Akun.create(username="admin", password_hash="hash", peran=Peran.ADMIN)
        petugas = Akun.create(username="petugas", password_hash="hash", peran=Peran.PETUGAS)
        pengguna = Akun.create(username="pengguna", password_hash="hash", peran=Peran.PENGGUNA)
        
        assert admin.peran == Peran.ADMIN
        assert petugas.peran == Peran.PETUGAS
        assert pengguna.peran == Peran.PENGGUNA
