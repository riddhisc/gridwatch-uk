from app.db.models import CarbonSnapshot, PriceSnapshot


def test_snapshot_table_names() -> None:
    assert CarbonSnapshot.__tablename__ == "carbon_snapshots"
    assert PriceSnapshot.__tablename__ == "price_snapshots"
    carbon_constraints = {item.name for item in CarbonSnapshot.__table__.constraints if item.name}
    price_constraints = {item.name for item in PriceSnapshot.__table__.constraints if item.name}
    assert "uq_carbon_period_region" in carbon_constraints
    assert "uq_price_period_tariff" in price_constraints
