from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from manajemen_parkir.application.services import ParkingService
from manajemen_parkir.domain.auth import Akun
from manajemen_parkir.api.dependencies import (
    get_user_repository,
    get_slot_repository,
    get_sesi_repository,
    get_slot_service,
    verify_token_dependency,
)

router = APIRouter(prefix="/parking", tags=["Parking Management"])


class CheckInRequest(BaseModel):
    vehicle_id: UUID
    slot_id: Optional[UUID] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "vehicle_id": "fb46d318-5a6a-4be9-8769-2cb904cc7fbf",
                "slot_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


def get_parking_service(
    sesi_repo = Depends(get_sesi_repository),
    user_repo = Depends(get_user_repository),
    slot_repo = Depends(get_slot_repository),
):
    return ParkingService(sesi_repo, user_repo, slot_repo)


class SessionResponse(BaseModel):
    id: UUID
    plate: str
    vehicle_type: Optional[str] = None
    owner_id: Optional[UUID] = None
    vehicle_id: Optional[UUID] = None
    checkin_time: datetime
    checkout_time: Optional[datetime] = None
    status: str
    final_fee: Optional[Decimal] = None


def _serialize_sesi(sesi) -> dict:
    sid = getattr(sesi, "id_sesi", None)
    np = getattr(sesi, "nomor_plat", None)
    plate = None
    vehicle_type = None
    if np is not None:
        plate = getattr(np, "kode", None)
        vehicle_type = getattr(np, "tipe_kendaraan", None)
    plate = plate or getattr(sesi, "plate", None)
    vehicle_type = vehicle_type or getattr(sesi, "vehicle_type", None)

    biaya = getattr(sesi, "biaya_final", None)
    biaya_val = None
    if biaya is not None:
        raw = getattr(biaya, "jumlah", biaya)
        try:
            biaya_val = float(raw)
        except Exception:
            biaya_val = raw

    return {
        "id": str(sid) if sid is not None else None,
        "plate": plate,
        "vehicle_type": vehicle_type,
        "owner_id": getattr(sesi, "owner_id", None),
        "vehicle_id": getattr(sesi, "vehicle_id", None),
        "checkin_time": getattr(sesi, "waktu_masuk", None),
        "checkout_time": getattr(sesi, "waktu_keluar", None),
        "status": getattr(sesi, "status", None).value if getattr(sesi, "status", None) is not None else None,
        "final_fee": biaya_val,
    }


@router.post("/check-in")
def check_in(
    request: CheckInRequest,
    service: ParkingService = Depends(get_parking_service),
    user_repo = Depends(get_user_repository),
    slot_repo = Depends(get_slot_repository),
    current_akun: Akun = Depends(verify_token_dependency),
):
    try:
        vehicle = None
        owner = None
        for user in user_repo.list():
            for v in user.vehicles:
                if v.id == request.vehicle_id:
                    vehicle = v
                    owner = user
                    break
            if vehicle:
                break
        
        if not vehicle:
            raise HTTPException(status_code=404, detail=f"Vehicle with ID {request.vehicle_id} not found")
        
        if request.slot_id:
            from manajemen_parkir.domain.alokasi_slot import StatusSlot
            slot = slot_repo.get_by_id(request.slot_id)
            if not slot:
                raise HTTPException(status_code=404, detail=f"Slot with ID {request.slot_id} not found")
            if slot.status_ketersediaan.status != StatusSlot.TERSEDIA:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Slot {request.slot_id} tidak tersedia (status: {slot.status_ketersediaan.status.value})"
                )
        
        sesi = service.start_parking(
            user_id=owner.id,
            vehicle_id=vehicle.id,
            slot_id=request.slot_id,
        )
        return _serialize_sesi(sesi)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/check-out/{id_sesi}")
def check_out(
    id_sesi: UUID,
    slot_id: Optional[UUID] = None,
    service: ParkingService = Depends(get_parking_service),
    current_akun: Akun = Depends(verify_token_dependency),
):
    try:
        sesi = service.end_parking(id_sesi)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _serialize_sesi(sesi)


@router.get("/sessions/{id_sesi}")
def get_session(
    id_sesi: UUID,
    service: ParkingService = Depends(get_parking_service),
    current_akun: Akun = Depends(verify_token_dependency),
):
    sesi = service.get(id_sesi)
    if not sesi:
        raise HTTPException(status_code=404, detail="Session not found")
    return _serialize_sesi(sesi)


@router.get("/sessions")
def list_sessions(
    service: ParkingService = Depends(get_parking_service),
    current_akun: Akun = Depends(verify_token_dependency),
):
    res = []
    for s in service.list():
        res.append(_serialize_sesi(s))
    return res
