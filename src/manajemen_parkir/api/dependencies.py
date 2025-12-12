from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from manajemen_parkir.infrastructure.user_repository import InMemoryUserRepository
from manajemen_parkir.infrastructure.auth_repository import InMemoryAuthRepository
from manajemen_parkir.infrastructure.slot_repository import InMemorySlotParkirRepository
from manajemen_parkir.infrastructure.repository import InMemorySesiParkirRepository
from manajemen_parkir.application.services import AuthService
from manajemen_parkir.application.slot_service import SlotParkirService

_shared_user_repo = InMemoryUserRepository()
_shared_auth_repo = InMemoryAuthRepository()
_shared_slot_repo = InMemorySlotParkirRepository()
_shared_sesi_repo = InMemorySesiParkirRepository()

_shared_slot_service = SlotParkirService(_shared_slot_repo)

security = HTTPBearer()


def get_user_repository():
    return _shared_user_repo


def get_slot_repository():
    return _shared_slot_repo


def get_sesi_repository():
    return _shared_sesi_repo


def get_slot_service(
    slot_repo = Depends(get_slot_repository),
):
    """Create SlotParkirService with current repository (allows test overrides)"""
    return SlotParkirService(slot_repo)


def get_auth_service(
    auth_repo = Depends(lambda: _shared_auth_repo),
    user_repo = Depends(get_user_repository),
):
    """Create AuthService with current repositories (allows test overrides)"""
    return AuthService(auth_repo, user_repo)


async def verify_token_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    token = credentials.credentials
    akun = auth_service.verify_token(token)
    if not akun:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau sudah expired"
        )
    return akun
