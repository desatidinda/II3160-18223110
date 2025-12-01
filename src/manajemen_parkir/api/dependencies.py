from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from manajemen_parkir.infrastructure.user_repository import InMemoryUserRepository
from manajemen_parkir.infrastructure.auth_repository import InMemoryAuthRepository
from manajemen_parkir.infrastructure.slot_repository import InMemorySlotParkirRepository
from manajemen_parkir.application.services import AuthService
from manajemen_parkir.application.slot_service import SlotParkirService

_shared_user_repo = InMemoryUserRepository()
_shared_auth_repo = InMemoryAuthRepository()
_shared_slot_repo = InMemorySlotParkirRepository()

_shared_auth_service = AuthService(_shared_auth_repo, _shared_user_repo)
_shared_slot_service = SlotParkirService(_shared_slot_repo)

security = HTTPBearer()


async def verify_token_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    akun = _shared_auth_service.verify_token(token)
    if not akun:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau sudah expired"
        )
    return akun
