import { HomeViews } from "@/components/HomeViews";
import { fetchOverview, fetchPlaces } from "@/lib/overview";

export const dynamic = "force-dynamic";

export default async function HomePage({
  searchParams,
}: {
  searchParams: { city?: string; area?: string; postcode?: string; tab?: string };
}) {
  try {
    const [data, places] = await Promise.all([
      fetchOverview({
        city: searchParams.city,
        area: searchParams.area,
        postcode: searchParams.postcode,
      }),
      fetchPlaces(),
    ]);
    return (
      <HomeViews
        data={data}
        places={places}
        initialTab={searchParams.tab === "charts" ? "charts" : "dashboard"}
      />
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to load live grid data";
    return (
      <section className="rounded-xl border border-red-200 bg-red-50 p-6 sm:p-8">
        <h2 className="text-2xl font-semibold text-red-900">Live data is unavailable</h2>
        <p className="mt-2 text-slate-800">{message}</p>
        <p className="mt-2 text-sm text-slate-600">
          The dashboard needs the API at port 8000. Carbon and price charts will return when NESO and Octopus
          respond.
        </p>
      </section>
    );
  }
}
