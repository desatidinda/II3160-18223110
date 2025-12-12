"""
Repository untuk BC Alokasi Slot
"""
from typing import List, Optional
from uuid import UUID

from manajemen_parkir.domain.alokasi_slot import SlotParkir


class InMemorySlotParkirRepository:
    def __init__(self):
        self._slots: dict[UUID, SlotParkir] = {}
    
    def save(self, slot: SlotParkir) -> SlotParkir:
        self._slots[slot.id] = slot
        return slot
    
    def get_by_id(self, slot_id: UUID) -> Optional[SlotParkir]:
        return self._slots.get(slot_id)
    
    def find_by_id(self, slot_id: UUID) -> Optional[SlotParkir]:
        """Alias for get_by_id for compatibility"""
        return self.get_by_id(slot_id)
    
    def list_all(self) -> List[SlotParkir]:
        return list(self._slots.values())
    
    def list_by_lantai(self, lantai: int) -> List[SlotParkir]:
        return [slot for slot in self._slots.values() if slot.koordinat.lantai == lantai]
    
    def list_tersedia(self) -> List[SlotParkir]:
        return [slot for slot in self._slots.values() if slot.is_tersedia()]
    
    def delete(self, slot_id: UUID) -> bool:
        if slot_id in self._slots:
            del self._slots[slot_id]
            return True
        return False
    
    def count_total(self) -> int:
        return len(self._slots)
    
    def count_tersedia(self) -> int:
        return len(self.list_tersedia())
    
    def count_terisi(self) -> int:
        from manajemen_parkir.domain.alokasi_slot import StatusSlot
        return len([slot for slot in self._slots.values() 
                   if slot.status_ketersediaan.status == StatusSlot.TERISI])
    
    def count_rusak(self) -> int:
        from manajemen_parkir.domain.alokasi_slot import StatusSlot
        return len([slot for slot in self._slots.values() 
                   if slot.status_ketersediaan.status == StatusSlot.RUSAK])
