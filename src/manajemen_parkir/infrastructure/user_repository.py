from typing import Dict, Optional, List
from uuid import UUID

from manajemen_parkir.domain.user import User, Vehicle


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._store: Dict[UUID, User] = {}

    def save(self, user: User) -> None:
        self._store[user.id] = user

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self._store.get(user_id)

    def find_by_plate(self, plate: str) -> Optional[Vehicle]:
        for user in self._store.values():
            for v in user.vehicles:
                if v.plate == plate:
                    return v
        return None

    def list(self) -> List[User]:
        return list(self._store.values())

    def delete(self, user_id: UUID) -> bool:
        return self._store.pop(user_id, None) is not None
