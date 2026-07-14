import React from "react";
import SkeletonBlock from "./SkeletonBlock";

/**
 * Skeleton loader page structure matching the dashboard layout.
 */
export default function DashboardSkeleton() {
  return (
    <div className="space-y-6 p-6 animate-none">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4 animate-none">
        {Array.from({ length: 4 }).map((_, i) => <SkeletonBlock key={i} style={{ height: 92 }} />)}
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3 animate-none">
        <SkeletonBlock className="lg:col-span-2" style={{ height: 220 }} />
        <SkeletonBlock style={{ height: 220 }} />
      </div>
      <SkeletonBlock style={{ height: 160 }} />
    </div>
  );
}
