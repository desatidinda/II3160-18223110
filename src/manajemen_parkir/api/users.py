from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from manajemen_parkir.domain.user import User, Vehicle
from manajemen_parkir.domain.auth import Akun
from manajemen_parkir.api.dependencies import (
    _shared_user_repo,
    verify_token_dependency,
)

router = APIRouter(prefix="/users", tags=["Users & Vehicles"])


class CreateVehicleRequest(BaseModel):
    user_id: UUID
    plate: str
    vehicle_type: Optional[str] = None


@router.post("/vehicle", status_code=201)
def add_vehicle(
    req: CreateVehicleRequest,
    current_akun: Akun = Depends(verify_token_dependency),
):
    user = _shared_user_repo.get_by_id(req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    v = Vehicle.create_legacy(plate=req.plate, vehicle_type=req.vehicle_type)
    user.vehicles.append(v)
    _shared_user_repo.save(user)
    return {"vehicle_id": str(v.id), "plate": v.plate}


@router.get("/{user_id}")
def get_user(
    user_id: UUID,
    current_akun: Akun = Depends(verify_token_dependency),
):
    user = _shared_user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "vehicles": [
            {"id": str(v.id), "plate": v.plate, "vehicle_type": v.vehicle_type}
            for v in user.vehicles
        ],
    }


@router.get("/")
def list_users(current_akun: Akun = Depends(verify_token_dependency)):
    users = _shared_user_repo.list()
    return [
        {
            "id": str(u.id),
            "name": u.name,
            "email": u.email,
            "vehicles": [{"id": str(v.id), "plate": v.plate} for v in u.vehicles],
        }
        for u in users
    ]


@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    current_akun: Akun = Depends(verify_token_dependency),
):
    existed = _shared_user_repo.delete(user_id)
    if not existed:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "deleted"}
