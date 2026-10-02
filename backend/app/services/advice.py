from __future__ import annotations

from app.schemas.api import Advice

LOW_INDEXES = {"very low", "low"}
HIGH_INDEXES = {"high", "very high"}


def build_advice(
    *,
    index: str | None,
    carbon: int | None,
    price_inc_vat: float | None,
) -> Advice:
    green = (index or "").lower() in LOW_INDEXES or (carbon is not None and carbon < 100)
    dirty = (index or "").lower() in HIGH_INDEXES or (carbon is not None and carbon >= 250)
    cheap = price_inc_vat is not None and price_inc_vat <= 5
    expensive = price_inc_vat is not None and price_inc_vat >= 25

    if green and cheap:
        return Advice(
            action="charge_now",
            headline="Now is an excellent time to use power",
            detail=(
                "The UK grid is relatively green and Agile electricity is cheap. "
                "Run the dishwasher, laundry, or plug in an EV."
            ),
        )
    if green:
        return Advice(
            action="use_now",
            headline="Now is a good time to use electricity",
            detail=(
                "Carbon intensity is low, so this is a greener window for appliances "
                "and charging even if price is average."
            ),
        )
    if dirty and expensive:
        return Advice(
            action="wait",
            headline="Wait if you can",
            detail=(
                "The grid is carbon-heavy and power is expensive. "
                "Shift EV charging and heavy appliances to a later window."
            ),
        )
    if dirty:
        return Advice(
            action="wait",
            headline="The grid is dirtier than usual",
            detail="Delay energy-heavy jobs if you can. A greener window should show up on the 48-hour forecast.",
        )
    return Advice(
        action="ok",
        headline="The grid is middling right now",
        detail="Fine for normal use. If you can wait, a cheaper or greener half-hour may be coming up.",
    )
