import { redirect } from "next/navigation";

export default function ChartsRedirect({
  searchParams,
}: {
  searchParams: { city?: string; area?: string; postcode?: string };
}) {
  const params = new URLSearchParams({ tab: "charts" });
  if (searchParams.city) params.set("city", searchParams.city);
  if (searchParams.area) params.set("area", searchParams.area);
  if (searchParams.postcode) params.set("postcode", searchParams.postcode);
  redirect(`/?${params.toString()}`);
}
