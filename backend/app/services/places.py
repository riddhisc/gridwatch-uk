from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Place:
    id: str
    name: str
    outward_postcode: str
    lookup_postcode: str
    parent_id: str | None = None


def _area(city: str, slug: str, name: str, outward: str, lookup: str) -> Place:
    return Place(f"{city}-{slug}", name, outward, lookup, parent_id=city)


# Outward codes for NESO; compact postcodes for Octopus GSP lookup.
PLACES: tuple[Place, ...] = (
    Place("gb", "Great Britain (national)", "", ""),
    Place("london", "London", "SW1A", "SW1A1AA"),
    Place("manchester", "Manchester", "M1", "M11AE"),
    Place("birmingham", "Birmingham", "B1", "B11AA"),
    Place("leeds", "Leeds", "LS1", "LS11BA"),
    Place("liverpool", "Liverpool", "L1", "L11AA"),
    Place("newcastle", "Newcastle", "NE1", "NE11EB"),
    Place("sheffield", "Sheffield", "S1", "S11DA"),
    Place("nottingham", "Nottingham", "NG1", "NG11AA"),
    Place("bristol", "Bristol", "BS1", "BS11EA"),
    Place("cardiff", "Cardiff", "CF10", "CF101EP"),
    Place("swansea", "Swansea", "SA1", "SA13SN"),
    Place("glasgow", "Glasgow", "G1", "G11DA"),
    Place("edinburgh", "Edinburgh", "EH1", "EH11YZ"),
    Place("aberdeen", "Aberdeen", "AB10", "AB101AA"),
    Place("inverness", "Inverness", "IV1", "IV11AA"),
    Place("southampton", "Southampton", "SO14", "SO141AA"),
    Place("brighton", "Brighton", "BN1", "BN11GE"),
    Place("oxford", "Oxford", "OX1", "OX11BP"),
    Place("cambridge", "Cambridge", "CB2", "CB21TN"),
    Place("norwich", "Norwich", "NR1", "NR13JU"),
    Place("exeter", "Exeter", "EX1", "EX11GE"),
    Place("plymouth", "Plymouth", "PL1", "PL11AA"),
    Place("belfast", "Belfast", "BT1", "BT11AA"),
)

# Districts use NESO-valid outward codes. Greater London edges sit on different grid regions.
AREAS: tuple[Place, ...] = (
    _area("london", "westminster", "Westminster", "SW1A", "SW1A1AA"),
    _area("london", "city", "City of London", "EC1A", "EC1A1BB"),
    _area("london", "camden", "Camden", "NW1", "NW11DA"),
    _area("london", "islington", "Islington", "N1", "N10QH"),
    _area("london", "hackney", "Hackney", "E8", "E81BP"),
    _area("london", "tower-hamlets", "Tower Hamlets", "E1", "E11AA"),
    _area("london", "southwark", "Southwark", "SE1", "SE11GE"),
    _area("london", "lambeth", "Lambeth", "SW2", "SW21AA"),
    _area("london", "wandsworth", "Wandsworth", "SW18", "SW182PR"),
    _area("london", "kensington", "Kensington & Chelsea", "W8", "W85SA"),
    _area("london", "hammersmith", "Hammersmith", "W6", "W60NZ"),
    _area("london", "greenwich", "Greenwich", "SE10", "SE100AX"),
    _area("london", "lewisham", "Lewisham", "SE13", "SE136AA"),
    _area("london", "newham", "Newham / Stratford", "E15", "E151AA"),
    _area("london", "waltham-forest", "Waltham Forest", "E17", "E173AA"),
    _area("london", "bromley", "Bromley", "BR1", "BR11AA"),
    _area("london", "ealing", "Ealing", "W5", "W52PA"),
    _area("london", "hounslow", "Hounslow", "TW3", "TW31LZ"),
    _area("london", "hillingdon", "Hillingdon / Uxbridge", "UB8", "UB81AA"),
    _area("london", "barnet", "Barnet", "N12", "N120AA"),
    _area("london", "enfield", "Enfield", "EN1", "EN11AA"),
    _area("london", "havering", "Havering / Romford", "RM1", "RM11AA"),
    _area("london", "croydon", "Croydon", "CR0", "CR01AA"),
    _area("london", "richmond", "Richmond", "TW9", "TW91AA"),
    _area("london", "kingston", "Kingston", "KT1", "KT11AA"),
    _area("manchester", "centre", "City centre", "M1", "M11AE"),
    _area("manchester", "salford", "Salford", "M3", "M35AN"),
    _area("manchester", "fallowfield", "Fallowfield", "M14", "M147RR"),
    _area("manchester", "didsbury", "Didsbury", "M20", "M206RQ"),
    _area("manchester", "oldham", "Oldham", "OL1", "OL11AA"),
    _area("manchester", "stockport", "Stockport", "SK1", "SK13AA"),
    _area("birmingham", "centre", "City centre", "B1", "B11AA"),
    _area("birmingham", "digbeth", "Digbeth", "B5", "B55TH"),
    _area("birmingham", "edgbaston", "Edgbaston", "B15", "B152TT"),
    _area("birmingham", "selly-oak", "Selly Oak", "B29", "B296AA"),
    _area("leeds", "centre", "City centre", "LS1", "LS11BA"),
    _area("leeds", "holbeck", "Holbeck", "LS2", "LS27HY"),
    _area("leeds", "headingley", "Headingley", "LS6", "LS63AA"),
    _area("liverpool", "centre", "City centre", "L1", "L11AA"),
    _area("liverpool", "waterfront", "Waterfront", "L3", "L31DS"),
    _area("liverpool", "toxteth", "Toxteth", "L8", "L80AA"),
    _area("newcastle", "centre", "City centre", "NE1", "NE11EB"),
    _area("newcastle", "jesmond", "Jesmond", "NE2", "NE21AA"),
    _area("sheffield", "centre", "City centre", "S1", "S11DA"),
    _area("sheffield", "park-hill", "Park Hill", "S2", "S25SY"),
    _area("sheffield", "nether-edge", "Nether Edge", "S8", "S89FL"),
    _area("nottingham", "centre", "City centre", "NG1", "NG11AA"),
    _area("nottingham", "lenton", "Lenton", "NG7", "NG72NR"),
    _area("bristol", "centre", "City centre", "BS1", "BS11EA"),
    _area("bristol", "southville", "Southville", "BS3", "BS31AA"),
    _area("bristol", "clifton", "Clifton", "BS8", "BS81TH"),
    _area("cardiff", "centre", "City centre", "CF10", "CF101EP"),
    _area("cardiff", "cardiff-bay", "Cardiff Bay", "CF11", "CF110SN"),
    _area("cardiff", "cathays", "Cathays", "CF24", "CF244AY"),
    _area("swansea", "centre", "City centre", "SA1", "SA13SN"),
    _area("glasgow", "centre", "City centre", "G1", "G11DA"),
    _area("glasgow", "merchant-city", "Merchant City", "G2", "G21DU"),
    _area("glasgow", "anderston", "Anderston", "G3", "G36AB"),
    _area("glasgow", "partick", "Partick", "G11", "G116BP"),
    _area("edinburgh", "centre", "Old Town", "EH1", "EH11YZ"),
    _area("edinburgh", "new-town", "New Town", "EH3", "EH36SS"),
    _area("edinburgh", "southside", "Southside", "EH8", "EH89YL"),
    _area("aberdeen", "centre", "City centre", "AB10", "AB101AA"),
    _area("aberdeen", "harbour", "Harbour", "AB11", "AB115RG"),
    _area("aberdeen", "west-end", "West End", "AB15", "AB156XL"),
    _area("inverness", "centre", "City centre", "IV1", "IV11AA"),
    _area("inverness", "crown", "Crown", "IV2", "IV23AA"),
    _area("southampton", "centre", "City centre", "SO14", "SO141AA"),
    _area("southampton", "ocean-village", "Ocean Village", "SO15", "SO151AB"),
    _area("southampton", "portswood", "Portswood", "SO17", "SO172AA"),
    _area("brighton", "centre", "City centre", "BN1", "BN11GE"),
    _area("brighton", "kemptown", "Kemptown", "BN2", "BN21AA"),
    _area("brighton", "hove", "Hove", "BN3", "BN32AA"),
    _area("oxford", "centre", "City centre", "OX1", "OX11BP"),
    _area("oxford", "jericho", "Jericho", "OX2", "OX26AA"),
    _area("oxford", "cowley", "Cowley", "OX4", "OX41AA"),
    _area("cambridge", "centre", "City centre", "CB2", "CB21TN"),
    _area("cambridge", "station", "Station / CB1", "CB1", "CB12JW"),
    _area("cambridge", "chesterton", "Chesterton", "CB4", "CB41AA"),
    _area("norwich", "centre", "City centre", "NR1", "NR13JU"),
    _area("norwich", "west", "West Norwich", "NR2", "NR21AA"),
    _area("norwich", "north", "North Norwich", "NR3", "NR31AA"),
    _area("exeter", "centre", "City centre", "EX1", "EX11GE"),
    _area("exeter", "st-thomas", "St Thomas", "EX2", "EX24AA"),
    _area("exeter", "st-davids", "St David's", "EX4", "EX43AA"),
    _area("plymouth", "centre", "City centre", "PL1", "PL11AA"),
    _area("plymouth", "sutton", "Sutton", "PL4", "PL40AA"),
    _area("plymouth", "plymstock", "Plymstock", "PL9", "PL97AA"),
)


# NESO has 14 GB regions. Boroughs only differ when their outward code maps to another region.
NESO_GRID_BY_OUTWARD = {
    "SW1A": "London",
    "EC1A": "London",
    "NW1": "London",
    "N1": "London",
    "E8": "London",
    "E1": "London",
    "SE1": "London",
    "SW2": "London",
    "SW18": "London",
    "W8": "London",
    "W6": "London",
    "SE10": "London",
    "SE13": "London",
    "E15": "London",
    "E17": "London",
    "BR1": "London",
    "W5": "South England",
    "TW3": "South England",
    "UB8": "South England",
    "CR0": "South East England",
    "TW9": "South East England",
    "KT1": "South East England",
    "N12": "East England",
    "EN1": "East England",
    "RM1": "East England",
    "M1": "North West England",
    "M2": "North West England",
    "M3": "North West England",
    "M14": "North West England",
    "M20": "North West England",
    "OL1": "North West England",
    "SK1": "North West England",
    "B1": "West Midlands",
    "B5": "West Midlands",
    "B15": "West Midlands",
    "B29": "West Midlands",
    "LS1": "Yorkshire",
    "LS2": "Yorkshire",
    "LS6": "Yorkshire",
    "L1": "North Wales & Merseyside",
    "L3": "North Wales & Merseyside",
    "L8": "North Wales & Merseyside",
    "NE1": "North East England",
    "NE2": "North East England",
    "S1": "Yorkshire",
    "S2": "Yorkshire",
    "S8": "Yorkshire",
    "NG1": "East Midlands",
    "NG7": "East Midlands",
    "BS1": "South West England",
    "BS3": "South West England",
    "BS8": "South West England",
    "CF10": "South Wales",
    "CF11": "South Wales",
    "CF24": "South Wales",
    "SA1": "South Wales",
    "G1": "South Scotland",
    "G2": "South Scotland",
    "G3": "South Scotland",
    "G11": "South Scotland",
    "EH1": "South Scotland",
    "EH3": "South Scotland",
    "EH8": "South Scotland",
    "AB10": "North Scotland",
    "AB11": "North Scotland",
    "AB15": "North Scotland",
    "IV1": "North Scotland",
    "IV2": "North Scotland",
    "SO14": "South England",
    "SO15": "South England",
    "SO17": "South England",
    "BN1": "South East England",
    "BN2": "South East England",
    "BN3": "South East England",
    "OX1": "South England",
    "OX2": "South England",
    "OX4": "South England",
    "CB2": "East England",
    "CB1": "East England",
    "CB4": "East England",
    "NR1": "East England",
    "NR2": "East England",
    "NR3": "East England",
    "EX1": "South West England",
    "EX2": "South West England",
    "EX4": "South West England",
    "PL1": "South West England",
    "PL4": "South West England",
    "PL9": "South West England",
}


GSP_NAMES = {
    "A": "Eastern England",
    "B": "East Midlands",
    "C": "London",
    "D": "Merseyside & North Wales",
    "E": "West Midlands",
    "F": "North East England",
    "G": "North West England",
    "H": "Southern England",
    "J": "South East England",
    "K": "South Wales",
    "L": "South West England",
    "M": "Yorkshire",
    "N": "South Scotland",
    "P": "North Scotland",
}


def list_places() -> list[Place]:
    return [place for place in PLACES if place.id != "belfast"]


def list_areas(city_id: str | None) -> list[Place]:
    if not city_id:
        return []
    key = city_id.strip().lower()
    return [place for place in AREAS if place.parent_id == key]


def all_named_places() -> tuple[Place, ...]:
    return PLACES + AREAS


def normalize_postcode(value: str) -> str:
    compact = "".join(value.split()).upper()
    if len(compact) >= 5:
        return compact[:-3]  # outward from a unit postcode
    return compact


def get_place(place_id: str | None) -> Place | None:
    if not place_id:
        return None
    key = place_id.strip().lower()
    for place in all_named_places():
        if place.id == key:
            return place
    return None


def get_area(city_id: str | None, area_id: str | None) -> Place | None:
    if not city_id or not area_id:
        return None
    city = city_id.strip().lower()
    key = area_id.strip().lower()
    for place in AREAS:
        if place.parent_id != city:
            continue
        slug = place.id.removeprefix(f"{city}-")
        if place.id == key or slug == key:
            return place
    return None


def display_name(place: Place) -> str:
    if not place.parent_id:
        return place.name
    parent = get_place(place.parent_id)
    city = parent.name if parent else place.parent_id.title()
    return f"{city} · {place.name}"


def grid_region_for(place: Place) -> str | None:
    return NESO_GRID_BY_OUTWARD.get(place.outward_postcode)


def shared_area_names(place: Place, neso_region: str | None) -> list[str]:
    city_id = place.parent_id or place.id
    region = neso_region or grid_region_for(place)
    if not region:
        return []
    names = [
        area.name
        for area in list_areas(city_id)
        if grid_region_for(area) == region
    ]
    return names


def grid_note_for(place: Place, neso_region: str | None) -> str | None:
    region = neso_region or grid_region_for(place)
    names = shared_area_names(place, region)
    if not region or len(names) < 2:
        if region:
            return (
                f"NESO publishes carbon for 14 GB regions, not street-level. "
                f"This postcode is on the {region} grid."
            )
        return None
    listed = ", ".join(names[:8])
    extra = f" (+{len(names) - 8} more)" if len(names) > 8 else ""
    return (
        f"NESO publishes one carbon figure for the whole {region} region. "
        f"{listed}{extra} share these numbers. Switch to an area in another group "
        f"to see different carbon intensity."
    )


def resolve_query(
    *, city: str | None = None, area: str | None = None, postcode: str | None = None
) -> Place:
    if postcode and postcode.strip():
        outward = normalize_postcode(postcode)
        lookup = "".join(postcode.split()).upper()
        named = (get_area(city, area) or get_place(city)) if city else None
        return Place(
            id=named.id if named else "postcode",
            name=named.name if named else f"Postcode {outward}",
            outward_postcode=outward,
            lookup_postcode=lookup or outward,
            parent_id=named.parent_id if named else None,
        )
    found = get_area(city, area)
    if found:
        return found
    place = get_place(city)
    if place:
        return place
    return PLACES[0]
