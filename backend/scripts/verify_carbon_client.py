"""Live smoke check for the NESO Carbon Intensity client. Requires network."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.clients.carbon_intensity import CarbonIntensityClient
from app.clients.http import HttpClient
from app.config import get_settings


async def main() -> int:
    parser = argparse.ArgumentParser(description="Call NESO Carbon Intensity API via the typed client")
    parser.add_argument("--postcode", default="", help="Optional outward postcode, e.g. SW1")
    args = parser.parse_args()

    settings = get_settings()
    http = HttpClient(base_url=str(settings.carbon_intensity_base_url))
    client = CarbonIntensityClient(http)
    try:
        current = await client.get_current_intensity()
        generation = await client.get_generation_mix()
        period = current.data[0]
        mix = generation.data[0]
        payload = {
            "from": period.from_.isoformat(),
            "to": period.to.isoformat(),
            "forecast": period.intensity.forecast,
            "actual": period.intensity.actual,
            "index": period.intensity.index,
            "generation_fuels": [item.fuel for item in mix.generationmix],
        }
        if args.postcode:
            regional = await client.get_regional_by_postcode(args.postcode)
            location = regional.data[0]
            payload["region"] = {
                "id": location.regionid,
                "name": location.shortname,
                "postcode": location.postcode,
            }
        print(json.dumps(payload, indent=2))
        return 0
    finally:
        await http.aclose()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
