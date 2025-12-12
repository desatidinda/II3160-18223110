from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from manajemen_parkir.domain.auth import Akun
from manajemen_parkir.api.dependencies import (
    verify_token_dependency,
    get_slot_service,
)

router = APIRouter(prefix="/slots", tags=["Alokasi Slot"])


# Request Models
class CreateSlotRequest(BaseModel):
    lantai: int
    posisi_x: float
    posisi_y: float
    kapasitas: int = 1
    keterangan: Optional[str] = None
    tipe_sensor: Optional[str] = None  # "KAMERA", "ULTRASONIK", "INFRARED"
    
    class Config:
        json_schema_extra = {
            "example": {
                "lantai": 1,
                "posisi_x": 10.5,
                "posisi_y": 20.3,
                "kapasitas": 1,
                "keterangan": "Slot dekat pintu masuk",
                "tipe_sensor": "KAMERA"
            }
        }


class UpdateStatusRequest(BaseModel):
    status: str  # "TERSEDIA", "TERISI", "RUSAK"
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "TERISI"
            }
        }


class PasangSensorRequest(BaseModel):
    tipe_sensor: str  # "KAMERA", "ULTRASONIK", "INFRARED"
    
    class Config:
        json_schema_extra = {
            "example": {
                "tipe_sensor": "ULTRASONIK"
            }
        }


class UpdateKondisiSensorRequest(BaseModel):
    kondisi: str  # "Normal", "Error", "Maintenance"
    
    class Config:
        json_schema_extra = {
            "example": {
                "kondisi": "Normal"
            }
        }


# Response Models
class SensorResponse(BaseModel):
    id: str
    tipe: str
    kondisi: str
    is_active: bool
    created_at: datetime


class SlotParkirResponse(BaseModel):
    id: str
    lantai: int
    posisi_x: float
    posisi_y: float
    kapasitas: int
    status: str
    waktu_update: datetime
    sensor: Optional[SensorResponse] = None
    keterangan: Optional[str] = None


# Endpoints
@router.post("/", status_code=201)
def create_slot(
    req: CreateSlotRequest,
    service = Depends(get_slot_service),
    current_akun: Akun = Depends(verify_token_dependency),
):
    try:
        slot = service.buat_slot(
            lantai=req.lantai,
            posisi_x=req.posisi_x,
            posisi_y=req.posisi_y,
            kapasitas=req.kapasitas,
            keterangan=req.keterangan,
            tipe_sensor=req.tipe_sensor
        )
        
        return {
            "id": str(slot.id),
            "lantai": slot.koordinat.lantai,
            "posisi_x": slot.koordinat.posisi_x,
            "posisi_y": slot.koordinat.posisi_y,
            "status": slot.status_ketersediaan.status.value,
            "message": "Slot parkir berhasil dibuat"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
def list_slots(
    lantai: Optional[int] = Query(None, description="Filter berdasarkan lantai"),
    status: Optional[str] = Query(None, description="Filter berdasarkan status (TERSEDIA/TERISI/RUSAK)"),
    current_akun: Akun = Depends(verify_token_dependency),
    service = Depends(get_slot_service),
):
    
    if lantai is not None:
        slots = service.repository.list_by_lantai(lantai)
    else:
        slots = service.repository.list_all()
    
    if status:
        status_upper = status.upper()
        from manajemen_parkir.domain.alokasi_slot import StatusSlot
        try:
            status_enum = StatusSlot[status_upper]
            slots = [s for s in slots if s.status_ketersediaan.status == status_enum]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Status tidak valid: {status}")
    
    return [
        {
            "id": str(slot.id),
            "lantai": slot.koordinat.lantai,
            "posisi_x": slot.koordinat.posisi_x,
            "posisi_y": slot.koordinat.posisi_y,
            "kapasitas": slot.kapasitas,
            "status": slot.status_ketersediaan.status.value,
            "waktu_update": slot.status_ketersediaan.waktu_update.isoformat(),
            "sensor": {
                "id": str(slot.sensor.id),
                "tipe": slot.sensor.tipe.value,
                "kondisi": slot.sensor.kondisi,
                "is_active": slot.sensor.is_active
            } if slot.sensor else None,
            "keterangan": slot.keterangan
        }
        for slot in slots
    ]


@router.get("/tersedia")
def list_available_slots(
    lantai: Optional[int] = Query(None, description="Filter berdasarkan lantai"),
    current_akun: Akun = Depends(verify_token_dependency),
    service = Depends(get_slot_service),
):
    slots = service.get_slot_tersedia(lantai=lantai)
    
    return [
        {
            "id": str(slot.id),
            "lantai": slot.koordinat.lantai,
            "posisi_x": slot.koordinat.posisi_x,
            "posisi_y": slot.koordinat.posisi_y,
            "status": slot.status_ketersediaan.status.value
        }
        for slot in slots
    ]


@router.get("/statistik")
def get_statistics(
    current_akun: Akun = Depends(verify_token_dependency),
    service = Depends(get_slot_service),
):
    return service.get_statistik_slot()


@router.get("/statistik/lantai")
def get_statistics_per_floor(
    current_akun: Akun = Depends(verify_token_dependency),
    service = Depends(get_slot_service),
):
    return service.get_statistik_per_lantai()


@router.get("/{slot_id}")
def get_slot(
    slot_id: UUID,
    current_akun: Akun = Depends(verify_token_dependency),
    service = Depends(get_slot_service),
):
    slot = service.repository.get_by_id(slot_id)
    
    if not slot:
        raise HTTPException(status_code=404, detail="Slot parkir tidak ditemukan")
    
    return {
        "id": str(slot.id),
        "lantai": slot.koordinat.lantai,
        "posisi_x": slot.koordinat.posisi_x,
        "posisi_y": slot.koordinat.posisi_y,
        "kapasitas": slot.kapasitas,
        "status": slot.status_ketersediaan.status.value,
        "waktu_update": slot.status_ketersediaan.waktu_update.isoformat(),
        "sensor": {
            "id": str(slot.sensor.id),
            "tipe": slot.sensor.tipe.value,
            "kondisi": slot.sensor.kondisi,
            "is_active": slot.sensor.is_active,
            "created_at": slot.sensor.created_at.isoformat()
        } if slot.sensor else None,
        "keterangan": slot.keterangan,
        "created_at": slot.created_at.isoformat(),
        "updated_at": slot.updated_at.isoformat()
    }


@router.patch("/{slot_id}/status")
def update_slot_status(
    slot_id: UUID,
    req: UpdateStatusRequest,
    service = Depends(get_slot_service),
    current_akun: Akun = Depends(verify_token_dependency),
):
    try:
        slot = service.update_status_slot(slot_id, req.status)
        return {
            "id": str(slot.id),
            "status": slot.status_ketersediaan.status.value,
            "waktu_update": slot.status_ketersediaan.waktu_update.isoformat(),
            "message": f"Status slot berhasil diupdate menjadi {req.status}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{slot_id}/sensor")
def attach_sensor(
    slot_id: UUID,
    req: PasangSensorRequest,
    service = Depends(get_slot_service),
    current_akun: Akun = Depends(verify_token_dependency),
):
    try:
        slot = service.pasang_sensor_ke_slot(slot_id, req.tipe_sensor)
        return {
            "id": str(slot.id),
            "sensor": {
                "id": str(slot.sensor.id),
                "tipe": slot.sensor.tipe.value,
                "kondisi": slot.sensor.kondisi
            },
            "message": f"Sensor {req.tipe_sensor} berhasil dipasang"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{slot_id}/sensor")
def detach_sensor(
    slot_id: UUID,
    service = Depends(get_slot_service),
    current_akun: Akun = Depends(verify_token_dependency),
):
    try:
        slot = service.lepas_sensor_dari_slot(slot_id)
        return {
            "id": str(slot.id),
            "message": "Sensor berhasil dilepas dari slot"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{slot_id}/sensor/kondisi")
def update_sensor_condition(
    slot_id: UUID,
    req: UpdateKondisiSensorRequest,
    service = Depends(get_slot_service),
    current_akun: Akun = Depends(verify_token_dependency),
):
    try:
        slot = service.update_kondisi_sensor(slot_id, req.kondisi)
        return {
            "id": str(slot.id),
            "sensor": {
                "id": str(slot.sensor.id),
                "kondisi": slot.sensor.kondisi
            },
            "message": f"Kondisi sensor berhasil diupdate menjadi {req.kondisi}"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{slot_id}")
def delete_slot(
    slot_id: UUID,
    service = Depends(get_slot_service),
    current_akun: Akun = Depends(verify_token_dependency),
):
    deleted = service.repository.delete(slot_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Slot parkir tidak ditemukan")
    
    return {"message": "Slot parkir berhasil dihapus"}
