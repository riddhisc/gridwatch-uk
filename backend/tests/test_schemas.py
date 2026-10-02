from datetime import UTC, datetime

from app.schemas.carbon import GenerationResponse, IntensityResponse


def test_intensity_response_parses_official_payload() -> None:
    payload = {
        "data": [
            {
                "from": "2018-01-20T12:00Z",
                "to": "2018-01-20T12:30Z",
                "intensity": {"forecast": 266, "actual": 263, "index": "moderate"},
            }
        ]
    }
    parsed = IntensityResponse.model_validate(payload)
    period = parsed.data[0]
    assert period.intensity.forecast == 266
    assert period.intensity.actual == 263
    assert period.from_ == datetime(2018, 1, 20, 12, 0, tzinfo=UTC)


def test_generation_response_accepts_object_or_list() -> None:
    as_object = {
        "data": {
            "from": "2026-09-19T08:00Z",
            "to": "2026-09-19T08:30Z",
            "generationmix": [{"fuel": "wind", "perc": 62.2}],
        }
    }
    parsed = GenerationResponse.model_validate(as_object)
    assert parsed.data[0].generationmix[0].fuel == "wind"
