from app.ml.inference import get_forecast, get_recommendations


def test_ml_layer_stays_unavailable_until_phase_6() -> None:
    recs = get_recommendations()
    forecast = get_forecast()
    assert recs.available is False
    assert forecast.available is False
    assert recs.feature == "recommendations"
