from fastapi import APIRouter

from app.schemas.api import PlaceAreaOption, PlaceOption
from app.services.places import grid_region_for, list_areas, list_places

router = APIRouter(prefix="/v1", tags=["locations"])


@router.get("/locations", response_model=list[PlaceOption])
async def locations() -> list[PlaceOption]:
    options: list[PlaceOption] = []
    for place in list_places():
        options.append(
            PlaceOption(
                id=place.id,
                name=place.name,
                postcode=place.outward_postcode,
                areas=[
                    PlaceAreaOption(
                        id=area.id.removeprefix(f"{place.id}-"),
                        name=area.name,
                        postcode=area.outward_postcode,
                        grid_region=grid_region_for(area),
                    )
                    for area in list_areas(place.id)
                ],
            )
        )
    return options