from typing import Dict, List, Optional
from uuid import UUID

from manajemen_parkir.domain.model import SesiParkir


class InMemorySesiParkirRepository:
    def __init__(self) -> None:
        self._store: Dict[UUID, SesiParkir] = {}

    def get_by_id(self, id_sesi: UUID) -> Optional[SesiParkir]:
        return self._store.get(id_sesi)

    def save(self, sesi: SesiParkir) -> None:
        self._store[sesi.id_sesi] = sesi

    def list(self) -> List[SesiParkir]:
        return list(self._store.values())
