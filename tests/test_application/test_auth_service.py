import pytest
from uuid import uuid4

from manajemen_parkir.domain.auth import Akun, Peran
from manajemen_parkir.infrastructure.auth_repository import InMemoryAuthRepository
from manajemen_parkir.infrastructure.user_repository import InMemoryUserRepository
from manajemen_parkir.application.services import AuthService


class TestAuthService:
    def test_register_success(self):
        auth_repo = InMemoryAuthRepository()
        user_repo = InMemoryUserRepository()
        service = AuthService(auth_repo, user_repo)
        
        akun, user = service.register(
            username="testuser",
            password="password123",
            email="test@example.com",
            peran=Peran.PENGGUNA
        )
        
        assert akun.kredensial.username == "testuser"
        assert akun.email == "test@example.com"
        assert akun.peran == Peran.PENGGUNA
        assert user is not None
        assert user.name == "testuser"
    
    def test_register_duplicate_username(self):
        auth_repo = InMemoryAuthRepository()
        user_repo = InMemoryUserRepository()
        service = AuthService(auth_repo, user_repo)
        
        service.register("testuser", "password123", peran=Peran.PENGGUNA)
        
        with pytest.raises(ValueError, match="sudah terdaftar"):
            service.register("testuser", "newpassword", peran=Peran.PENGGUNA)
    
    def test_register_different_roles(self):
        auth_repo = InMemoryAuthRepository()
        user_repo = InMemoryUserRepository()
        service = AuthService(auth_repo, user_repo)
        
        admin, _ = service.register("admin", "pass", peran=Peran.ADMIN)
        petugas, _ = service.register("petugas", "pass", peran=Peran.PETUGAS)
        pengguna, _ = service.register("pengguna", "pass", peran=Peran.PENGGUNA)
        
        assert admin.peran == Peran.ADMIN
        assert petugas.peran == Peran.PETUGAS
        assert pengguna.peran == Peran.PENGGUNA
    
    def test_login_success(self):
        auth_repo = InMemoryAuthRepository()
        user_repo = InMemoryUserRepository()
        service = AuthService(auth_repo, user_repo)
        
        service.register("testuser", "password123", peran=Peran.PENGGUNA)
        token = service.login("testuser", "password123")
        
        assert token.token is not None
        assert token.token_type == "bearer"
        assert not token.is_expired()
    
    def test_login_wrong_username(self):
        auth_repo = InMemoryAuthRepository()
        user_repo = InMemoryUserRepository()
        service = AuthService(auth_repo, user_repo)
        
        service.register("testuser", "password123", peran=Peran.PENGGUNA)
        
        with pytest.raises(ValueError, match="Username atau password salah"):
            service.login("wronguser", "password123")
    
    def test_login_wrong_password(self):
        auth_repo = InMemoryAuthRepository()
        user_repo = InMemoryUserRepository()
        service = AuthService(auth_repo, user_repo)
        
        service.register("testuser", "password123", peran=Peran.PENGGUNA)
        
        with pytest.raises(ValueError, match="Username atau password salah"):
            service.login("testuser", "wrongpassword")
    
    def test_login_inactive_account(self):
        auth_repo = InMemoryAuthRepository()
        user_repo = InMemoryUserRepository()
        service = AuthService(auth_repo, user_repo)
        
        akun, _ = service.register("testuser", "password123", peran=Peran.PENGGUNA)
        akun.deactivate()
        auth_repo.save(akun)
        
        with pytest.raises(ValueError, match="Akun tidak aktif"):
            service.login("testuser", "password123")
    
    def test_verify_token_success(self):
        auth_repo = InMemoryAuthRepository()
        user_repo = InMemoryUserRepository()
        service = AuthService(auth_repo, user_repo)
        
        service.register("testuser", "password123", peran=Peran.PENGGUNA)
        token = service.login("testuser", "password123")
        
        akun = service.verify_token(token.token)
        assert akun.kredensial.username == "testuser"
    
    def test_verify_token_invalid(self):
        auth_repo = InMemoryAuthRepository()
        user_repo = InMemoryUserRepository()
        service = AuthService(auth_repo, user_repo)
        
        with pytest.raises(ValueError, match="Token tidak valid"):
            service.verify_token("invalid_token")
    
    def test_hash_password_consistency(self):
        auth_repo = InMemoryAuthRepository()
        user_repo = InMemoryUserRepository()
        service = AuthService(auth_repo, user_repo)
        
        hash1 = service._hash_password("password123")
        hash2 = service._hash_password("password123")
        
        assert hash1 != hash2
        assert service._verify_password("password123", hash1)
        assert service._verify_password("password123", hash2)
    
    def test_password_verification(self):
        auth_repo = InMemoryAuthRepository()
        user_repo = InMemoryUserRepository()
        service = AuthService(auth_repo, user_repo)
        
        hashed = service._hash_password("password123")
        assert service._verify_password("password123", hashed)
        assert not service._verify_password("wrongpassword", hashed)
