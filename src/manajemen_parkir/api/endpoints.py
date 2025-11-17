from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from manajemen_parkir.application.services import ParkingService

router = APIRouter(prefix="/parking", tags=["Parking Management"])


class CheckInRequest(BaseModel):
    kode_plat: str
    tipe_kendaraan: Optional[str] = None
    user_id: Optional[UUID] = None
    vehicle_id: Optional[UUID] = None


_shared_parking_service = ParkingService()


def get_parking_service():
    return _shared_parking_service


class SessionResponse(BaseModel):
    id: UUID
    plate: str
    vehicle_type: Optional[str] = None
    owner_id: Optional[UUID] = None
    vehicle_id: Optional[UUID] = None
    checkin_time: datetime
    checkout_time: Optional[datetime] = None
    status: str
    biaya_final: Optional[Decimal] = None


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
def check_in(request: CheckInRequest, service: ParkingService = Depends(get_parking_service)):
    vehicle_plate = request.kode_plat
    vehicle_type = request.tipe_kendaraan
    sesi = service.start_parking(vehicle_plate, vehicle_type, user_id=request.user_id, vehicle_id=request.vehicle_id)
    return _serialize_sesi(sesi)


@router.post("/check-out/{id_sesi}")
def check_out(id_sesi: UUID, service: ParkingService = Depends(get_parking_service)):
    try:
        sesi = service.end_parking(id_sesi)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _serialize_sesi(sesi)


@router.get("/sessions/{id_sesi}")
def get_session(id_sesi: UUID, service: ParkingService = Depends(get_parking_service)):
    sesi = service.get(id_sesi)
    if not sesi:
        raise HTTPException(status_code=404, detail="Session not found")
    return _serialize_sesi(sesi)


@router.get("/sessions")
def list_sessions(service: ParkingService = Depends(get_parking_service)):
    res = []
    for s in service.list():
        res.append(_serialize_sesi(s))
    return res
