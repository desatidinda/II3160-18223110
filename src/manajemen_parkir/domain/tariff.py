from datetime import datetime
from math import ceil


class ParkingTariff:
    def __init__(self, price_per_hour: float = 3000.0, max_daily: float | None = None, tariff_type: str = "regular"):
        self.price_per_hour = float(price_per_hour)
        self.max_daily = float(max_daily) if max_daily is not None else None
        self.tariff_type = tariff_type

    def calculate(self, checkin: datetime, checkout: datetime) -> float:
        seconds = (checkout - checkin).total_seconds()
        hours = max(1, ceil(seconds / 3600))
        fee = hours * self.price_per_hour
        if self.max_daily is not None:
            days = max(1, (checkout.date() - checkin.date()).days + 1)
            fee = min(fee, days * self.max_daily)
        return float(fee)
