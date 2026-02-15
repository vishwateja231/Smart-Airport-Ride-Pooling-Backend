class PricingService:
    def __init__(self, rate_per_km: float):
        self.rate_per_km = rate_per_km

    def calculate(self, distance_km: float, passengers: int, cab_capacity: int) -> float:
        base_price = distance_km * self.rate_per_km
        shared_discount = passengers / cab_capacity
        final_price = base_price * (1 - shared_discount * 0.3)
        return round(max(final_price, 0), 2)
