"use client";

import { useEffect, useState } from "react";
import { ChartsView } from "@/components/Charts";
import { Dashboard } from "@/components/Dashboard";
import type { OverviewResponse, PlaceOption } from "@/lib/overview";
import { subscribeViewTab, type ViewTab } from "@/lib/view-tab";

export function HomeViews({
  data,
  places,
  initialTab,
}: {
  data: OverviewResponse;
  places: PlaceOption[];
  initialTab: ViewTab;
}) {
  const [tab, setTab] = useState<ViewTab>(initialTab);

  useEffect(() => {
    setTab(initialTab);
    return subscribeViewTab(setTab);
  }, [initialTab]);

  if (tab === "charts") {
    return <ChartsView data={data} places={places} />;
  }
  return <Dashboard data={data} places={places} />;
}
