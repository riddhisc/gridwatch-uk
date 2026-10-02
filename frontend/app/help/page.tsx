import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Help · Green Power Hours",
  description: "What the Green Power Hours numbers mean, where they come from, and how to use them.",
};

function SourceLink({ href, children }: { href: string; children: string }) {
  return (
    <a href={href} className="font-medium text-blue-800 underline-offset-2 hover:underline" target="_blank" rel="noreferrer">
      {children}
    </a>
  );
}

export default function HelpPage() {
  return (
    <article className="space-y-10 text-slate-800">
      <section className="card p-6 sm:p-8">
        <p className="text-sm font-medium text-blue-800">How to read Green Power Hours</p>
        <h2 className="mt-2 text-3xl font-semibold tracking-tight">Live GB electricity, not a sample dashboard</h2>
        <p className="mt-4 max-w-3xl text-slate-700">
          Green Power Hours reads two official feeds every time you load the page: carbon intensity from the{" "}
          <strong>National Energy System Operator (NESO)</strong> Carbon Intensity API, and unit rates from{" "}
          <strong>Octopus Energy</strong> Agile. Nothing on the dashboard is invented demo data. The half-hour you see
          is the settlement period the grid actually uses for generation and (if you are on Agile) for your unit rate.
        </p>
      </section>

      <section className="space-y-4">
        <h3 className="text-xl font-semibold">What the terms mean</h3>
        <dl className="grid gap-4 md:grid-cols-2">
          {[
            [
              "Carbon intensity (gCO₂/kWh)",
              "Grams of CO₂ released for each kilowatt-hour of electricity consumed on the grid. Lower is cleaner. NESO estimates this from the generation mix, interconnectors, and network losses.",
            ],
            [
              "Index (very low → very high)",
              "NESO’s own label on that half-hour. Green Power Hours displays the index the API returns. It is a relative “how clean is the GB system right now” tag, not a legal emissions factor for your bill.",
            ],
            [
              "Generation mix",
              "Share of the electricity being used in that NESO region from wind, solar, nuclear, gas, biomass, hydro, storage, and imports. More wind and nuclear usually means lower carbon.",
            ],
            [
              "Octopus Agile (p/kWh inc VAT)",
              "The published half-hourly unit rate for Octopus Agile in your Grid Supply Point (GSP) region. Negative rates mean Octopus pays you to use electricity. This is not the standard SVR cap rate.",
            ],
            [
              "GSP / DNO region",
              "Great Britain is split into 14 electricity regions. NESO carbon follows DNO/postcode regions. Agile prices follow GSP letters A–P. A London borough can sit on a neighbouring region.",
            ],
            [
              "Half-hour / settlement period",
              "Electricity in GB is settled in 30-minute blocks. Carbon, mix, and Agile rates all change on that clock, which is why the dashboard shows 10:30–11:00 rather than a daily average.",
            ],
            [
              "Forecast vs actual",
              "Forecast is NESO’s outlook for that half-hour. Actual is filled in after the period from metered generation. Future slots only have a forecast.",
            ],
            [
              "Best window",
              "Green Power Hours’ ranking of the next 24 hours using both carbon and Agile price. It is guidance for when to run flexible loads, not a dispatch instruction.",
            ],
          ].map(([term, meaning]) => (
            <div key={term} className="card p-5">
              <dt className="font-medium text-slate-900">{term}</dt>
              <dd className="mt-2 text-sm text-slate-600">{meaning}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="space-y-4">
        <h3 className="text-xl font-semibold">Best to worst range</h3>
        <p className="text-sm text-slate-600">
          NESO labels every half-hour. Green Power Hours also uses simple advice thresholds so the headline is readable: under{" "}
          <strong>100 gCO₂/kWh</strong> is treated as a green window; <strong>250 gCO₂/kWh</strong> and above is treated
          as a dirty window. Agile advice treats about <strong>5p/kWh or less</strong> as cheap and{" "}
          <strong>25p/kWh or more</strong> as expensive.
        </p>
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
          <table className="w-full min-w-[36rem] text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">Scale</th>
                <th className="px-4 py-3 font-medium">Best</th>
                <th className="px-4 py-3 font-medium">Typical</th>
                <th className="px-4 py-3 font-medium">Worst</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              <tr>
                <td className="px-4 py-3 text-slate-700">NESO carbon index</td>
                <td className="px-4 py-3 font-medium text-green-800">Very low / low</td>
                <td className="px-4 py-3">Moderate</td>
                <td className="px-4 py-3 font-medium text-red-800">High / very high</td>
              </tr>
              <tr>
                <td className="px-4 py-3 text-slate-700">Carbon (this app’s advice)</td>
                <td className="px-4 py-3 font-medium text-green-800">&lt; 100 gCO₂/kWh</td>
                <td className="px-4 py-3">100–249 gCO₂/kWh</td>
                <td className="px-4 py-3 font-medium text-red-800">≥ 250 gCO₂/kWh</td>
              </tr>
              <tr>
                <td className="px-4 py-3 text-slate-700">Agile unit rate inc VAT</td>
                <td className="px-4 py-3 font-medium text-green-800">≤ 5p, including negative</td>
                <td className="px-4 py-3">Around 5–25p</td>
                <td className="px-4 py-3 font-medium text-red-800">≥ 25p, evening spikes</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="grid gap-2 sm:grid-cols-5">
          {[
            ["Very low", "bg-green-800 text-white"],
            ["Low", "bg-green-600 text-white"],
            ["Moderate", "bg-amber-500 text-slate-900"],
            ["High", "bg-orange-600 text-white"],
            ["Very high", "bg-red-700 text-white"],
          ].map(([label, color]) => (
            <div key={label} className={`rounded-lg px-3 py-2 text-center text-xs font-semibold ${color}`}>
              {label}
            </div>
          ))}
        </div>
      </section>

      <section className="space-y-3">
        <h3 className="text-xl font-semibold">How this is helpful</h3>
        <ul className="list-disc space-y-2 pl-5 text-slate-700">
          <li>Shift washing, dishwashers, immersion heaters, and EV charging into green, cheap half-hours.</li>
          <li>Avoid the winter evening peak, when GB demand, gas generation, and Agile prices often rise together.</li>
          <li>See whether your postcode is on the London grid or a neighbour such as South East or East England.</li>
          <li>Use the 48-hour NESO forecast and the “best window” card to plan the next day, not just this hour.</li>
        </ul>
      </section>

      <section className="space-y-3">
        <h3 className="text-xl font-semibold">How much money you might save</h3>
        <p className="text-slate-700">
          Time-shifting does not cut the standing charge. It only changes what you pay on <em>unit rates</em>, and only
          if you are on a half-hourly tariff such as Octopus Agile (or you use the carbon view for climate, not cost).
        </p>
        <p className="text-sm text-slate-600">
          DESNZ NEED 2026 (2024 meter year): median household electricity use in England and Wales was{" "}
          <strong>2,500 kWh/year</strong>; the mean was <strong>3,300 kWh</strong>. DESNZ uses about{" "}
          <strong>3,400 kWh</strong> as an average for standard-electricity bill comparisons.
        </p>
        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full min-w-[40rem] text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">If you can move</th>
                <th className="px-4 py-3 font-medium">Example spread</th>
                <th className="px-4 py-3 font-medium">Illustrative saving</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              <tr>
                <td className="px-4 py-3">One 1.2 kWh wash cycle</td>
                <td className="px-4 py-3">28p peak → 8p overnight</td>
                <td className="px-4 py-3">About 24p per cycle; ~£35/year at 150 cycles</td>
              </tr>
              <tr>
                <td className="px-4 py-3">15% of a median 2,500 kWh home (375 kWh)</td>
                <td className="px-4 py-3">20p/kWh cheaper window</td>
                <td className="px-4 py-3">About £75/year</td>
              </tr>
              <tr>
                <td className="px-4 py-3">2,000 kWh of EV charging</td>
                <td className="px-4 py-3">32p evening → 8p overnight</td>
                <td className="px-4 py-3">About £480/year</td>
              </tr>
              <tr>
                <td className="px-4 py-3">Any kWh at a negative Agile rate</td>
                <td className="px-4 py-3">e.g. −2.9p/kWh</td>
                <td className="px-4 py-3">You are paid to consume; 10 kWh ≈ 29p credit</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-500">
          These are worked examples from live-style Agile spreads, not a personal quote. Your GSP, product code, and how
          much load you can actually move will change the result.
        </p>
      </section>

      <section className="space-y-3">
        <h3 className="text-xl font-semibold">How accurate this is</h3>
        <ul className="list-disc space-y-2 pl-5 text-slate-700">
          <li>
            <strong>Agile rates</strong> are the unit rates Octopus publishes for that product, tariff, and GSP. For
            Agile customers they are the rates that go on the bill (plus standing charge).
          </li>
          <li>
            <strong>Carbon forecast</strong> is NESO’s operational model (machine learning + power-flow), updated about
            every 30 minutes, with a 48-hour look-ahead on the endpoints Green Power Hours calls. It is an indicative grid
            figure, not a smart-meter reading of your home.
          </li>
          <li>
            <strong>Carbon actual</strong> is NESO’s estimate from metered generation after the half-hour. Forecast and
            actual often differ when wind, demand, or interconnectors change quickly.
          </li>
          <li>
            <strong>Geography</strong> is accurate to NESO’s 14 regions, not to a street. Westminster and Camden share
            the London figure; Croydon is on South East England.
          </li>
          <li>
            Green Power Hours caches carbon for about 60 seconds and prices for about 120 seconds so the live APIs are not
            hammered. Refresh to pick up the next half-hour.
          </li>
        </ul>
      </section>

      <section className="space-y-3">
        <h3 className="text-xl font-semibold">Where the data comes from</h3>
        <ul className="list-disc space-y-2 pl-5 text-slate-700">
          <li>
            Carbon, index, mix, regional postcode lookup: NESO Carbon Intensity API —{" "}
            <SourceLink href="https://api.carbonintensity.org.uk">api.carbonintensity.org.uk</SourceLink> ·{" "}
            <SourceLink href="https://carbonintensity.org.uk">carbonintensity.org.uk</SourceLink> ·{" "}
            <SourceLink href="https://carbon-intensity.github.io/api-definitions/">API definitions</SourceLink>
          </li>
          <li>
            Agile unit rates and GSP from postcode: Octopus Energy REST API —{" "}
            <SourceLink href="https://api.octopus.energy/v1">api.octopus.energy/v1</SourceLink>
          </li>
          <li>
            Operator context:{" "}
            <SourceLink href="https://www.neso.energy">National Energy System Operator (NESO)</SourceLink>
          </li>
          <li>
            Household consumption used in the savings examples: DESNZ{" "}
            <SourceLink href="https://www.gov.uk/government/statistics/national-energy-efficiency-data-framework-need-report-summary-of-analysis-2026">
              NEED report, June 2026 (2024 consumption)
            </SourceLink>
          </li>
        </ul>
      </section>

      <section className="space-y-3">
        <h3 className="text-xl font-semibold">What drives higher electricity use in the UK</h3>
        <p className="text-slate-700">
          GB demand is still peaked by people coming home, cooking, lighting, and heating. NESO has to match that with
          generation. When demand is high and wind is low, gas plant fills the gap — carbon intensity and often Agile
          prices rise together.
        </p>
        <ul className="list-disc space-y-2 pl-5 text-slate-700">
          <li>
            <strong>Winter evening peak (about 16:00–20:00)</strong> — lights, cooking, kettles, washing, heating pumps,
            and entertainment loads stack up after work.
          </li>
          <li>
            <strong>Cold weather</strong> — electric heating, heat pumps, and immersion heaters. Homes with no gas
            (including many flats) lean harder on electricity.
          </li>
          <li>
            <strong>Uncontrolled EV charging</strong> — plugging in at 18:00 adds a large extra load on the same peak.
          </li>
          <li>
            <strong>Industry, commercial cooling, and data centres</strong> — steady underlying demand on top of homes.
          </li>
          <li>
            <strong>Low renewable output</strong> — still nights mean more combined-cycle gas. That is why a “moderate”
            evening can jump to high even if your house is not using more than yesterday.
          </li>
        </ul>
        <p className="text-sm text-slate-600">
          Shifting flexible home loads off that peak is the practical bit Green Power Hours is for: it does not replace
          insulation or a better tariff, but it uses the same half-hour the system operator and Octopus already settle
          on.
        </p>
      </section>
    </article>
  );
}
