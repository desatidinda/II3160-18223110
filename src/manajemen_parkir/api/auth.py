from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional

from manajemen_parkir.application.services import AuthService
from manajemen_parkir.domain.auth import Peran
from manajemen_parkir.api.dependencies import (
    get_auth_service,
    security,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    peran: Optional[str] = "PENGGUNA"


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_at: str


@router.post("/register", status_code=201)
def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        if len(request.password.encode('utf-8')) > 72:
            raise HTTPException(
                status_code=400,
                detail="Password terlalu panjang. Maksimal 72 karakter.",
            )
        
        try:
            peran = Peran(request.peran.upper())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Peran tidak valid. Pilih: ADMIN, PETUGAS, atau PENGGUNA",
            )

        akun, user = auth_service.register(
            username=request.username,
            password=request.password,
            email=request.email,
            peran=peran,
        )

        return {
            "akun_id": str(akun.id),
            "user_id": str(user.id) if user else None,
            "username": akun.kredensial.username,
            "email": akun.email,
            "peran": akun.peran.value,
            "message": "Registrasi berhasil. User profile otomatis dibuat.",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        if len(request.password.encode('utf-8')) > 72:
            raise HTTPException(
                status_code=400,
                detail="Password terlalu panjang. Maksimal 72 karakter.",
            )
        
        token_akses = auth_service.login(
            username=request.username,
            password=request.password,
        )

        return {
            "access_token": token_akses.token,
            "token_type": token_akses.token_type,
            "expires_at": token_akses.expires_at.isoformat(),
        }

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me")
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        token = credentials.credentials
        akun = auth_service.verify_token(token)

        return {
            "id": str(akun.id),
            "username": akun.kredensial.username,
            "email": akun.email,
            "peran": akun.peran.value,
            "is_active": akun.is_active,
            "created_at": akun.created_at.isoformat(),
        }

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
