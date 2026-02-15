from app.services.pricing_service import PricingService


def test_pricing_formula() -> None:
    service = PricingService(rate_per_km=2.0)
    result = service.calculate(distance_km=10, passengers=2, cab_capacity=4)
    assert result == 17.0
