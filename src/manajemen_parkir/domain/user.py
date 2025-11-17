from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID, uuid4

@dataclass
class Vehicle:
    id: UUID
    plate: str
    vehicle_type: Optional[str] = None

    @staticmethod
    def create(plate: str, vehicle_type: Optional[str] = None) -> "Vehicle":
        return Vehicle(id=uuid4(), plate=plate, vehicle_type=vehicle_type)


@dataclass
class User:
    id: UUID
    name: str
    email: Optional[str] = None
    vehicles: List[Vehicle] = field(default_factory=list)

    @staticmethod
    def create(name: str, email: Optional[str] = None) -> "User":
        return User(id=uuid4(), name=name, email=email)
