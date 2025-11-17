from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from manajemen_parkir.infrastructure.user_repository import InMemoryUserRepository
from manajemen_parkir.domain.user import User, Vehicle

router = APIRouter(prefix="/users", tags=["Users"])

_shared_user_repo = InMemoryUserRepository()


class CreateUserRequest(BaseModel):
    name: str
    email: Optional[str] = None


class CreateVehicleRequest(BaseModel):
    user_id: UUID
    plate: str
    vehicle_type: Optional[str] = None


@router.post("/", status_code=201)
def create_user(req: CreateUserRequest):
    user = User.create(name=req.name, email=req.email)
    _shared_user_repo.save(user)
    return {"id": str(user.id), "name": user.name, "email": user.email}


@router.post("/vehicle", status_code=201)
def add_vehicle(req: CreateVehicleRequest):
    user = _shared_user_repo.get_by_id(req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    v = Vehicle.create(plate=req.plate, vehicle_type=req.vehicle_type)
    user.vehicles.append(v)
    _shared_user_repo.save(user)
    return {"vehicle_id": str(v.id), "plate": v.plate}


@router.get("/{user_id}")
def get_user(user_id: UUID):
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
def list_users():
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
def delete_user(user_id: UUID):
    existed = _shared_user_repo.delete(user_id)
    if not existed:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "deleted"}
