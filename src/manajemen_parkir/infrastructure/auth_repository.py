from typing import Dict, Optional, List
from uuid import UUID

from manajemen_parkir.domain.auth import Akun


class InMemoryAuthRepository:
    def __init__(self) -> None:
        self._store: Dict[UUID, Akun] = {}
        self._username_index: Dict[str, UUID] = {}

    def save(self, akun: Akun) -> None:
        self._store[akun.id] = akun
        self._username_index[akun.kredensial.username] = akun.id

    def get_by_id(self, akun_id: UUID) -> Optional[Akun]:
        return self._store.get(akun_id)

    def get_by_username(self, username: str) -> Optional[Akun]:
        akun_id = self._username_index.get(username)
        if akun_id:
            return self._store.get(akun_id)
        return None

    def list(self) -> List[Akun]:
        return list(self._store.values())

    def delete(self, akun_id: UUID) -> bool:
        akun = self._store.pop(akun_id, None)
        if akun:
            self._username_index.pop(akun.kredensial.username, None)
            return True
        return False

    def username_exists(self, username: str) -> bool:
        return username in self._username_index
