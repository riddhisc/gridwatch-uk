from app.services.places import display_name, get_area, list_areas, normalize_postcode, resolve_query


def test_city_resolves_to_outward_postcode() -> None:
    place = resolve_query(city="manchester")
    assert place.outward_postcode == "M1"
    assert place.lookup_postcode == "M11AE"


def test_london_uses_full_outward_postcode() -> None:
    # NESO rejects truncated SW1; the district is SW1A.
    place = resolve_query(city="london")
    assert place.outward_postcode == "SW1A"
    assert place.lookup_postcode == "SW1A1AA"


def test_london_area_uses_local_postcode() -> None:
    place = resolve_query(city="london", area="croydon")
    assert place.outward_postcode == "CR0"
    assert place.parent_id == "london"
    assert display_name(place) == "London · Croydon"
    assert get_area("london", "ealing") is not None
    assert any(area.outward_postcode == "RM1" for area in list_areas("london"))


def test_unit_postcode_becomes_outward() -> None:
    assert normalize_postcode("sw1a 1aa") == "SW1A"
    place = resolve_query(postcode="EH1 1YZ")
    assert place.outward_postcode == "EH1"
