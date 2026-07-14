import { useState } from "react";
import { useOutletContext } from "react-router-dom";
import { Search, SearchX, User, ShieldAlert } from "lucide-react";
import { STATE, CONFIDENCE_THRESHOLD } from "../types";
import { verificationQueue } from "../mocks/data";
import Glass from "../components/Glass";
import StatePill from "../components/StatePill";

export interface VerificationPageProps {
  openAlert?: () => void;
}

/**
 * Donor Verification page component showing the registration queues, match confidence levels,
 * and duplicate alert lockout reviews.
 */
export default function Verification({ openAlert }: VerificationPageProps) {
  const context = useOutletContext<{ openAlert: () => void }>();
  const activeOpenAlert = openAlert || context?.openAlert;

  const [query, setQuery] = useState("");
  const filtered = verificationQueue.filter((v) =>
    v.response.matched_donor.name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="space-y-6 p-6 animate-none">
      <Glass className="p-5 animate-none">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2 animate-none">
          <h2 className="text-sm font-semibold text-white">Verification Queue</h2>
          <div className="flex items-center gap-2 animate-none">
            <span
              className="rounded-full border px-2.5 py-1 text-[11px] border-solid"
              style={{ borderColor: "rgba(255,255,255,0.1)", color: "#8A97A6" }}
              title="Matches above this confidence are auto-flagged as potential duplicates"
            >
              Flag threshold: {CONFIDENCE_THRESHOLD}%
            </span>
            <div className="flex items-center gap-2 rounded-lg border px-2.5 py-1.5 text-xs border-solid" style={{ borderColor: "rgba(255,255,255,0.1)", color: "#8A97A6" }}>
              <Search size={12} />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search donor"
                className="w-28 bg-transparent text-white outline-none placeholder:text-[#5B6572] border-none"
              />
            </div>
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-2 py-10 text-center animate-none">
            <SearchX size={22} style={{ color: "#5B6572" }} />
            <p className="text-sm text-white">No matching donor found</p>
            <p className="text-[11px]" style={{ color: "#5B6572" }}>Check the spelling, or clear the search to see the full queue.</p>
          </div>
        ) : (
          <div className="space-y-2 animate-none">
            {filtered.map((v) => {
              const s = STATE[v.state];
              const { confidence, matched_donor } = v.response;
              const overThreshold = confidence >= CONFIDENCE_THRESHOLD;
              return (
                <div key={matched_donor.name} className="flex items-center justify-between rounded-lg border p-3 border-solid" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
                  <div className="flex items-center gap-3 animate-none">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full" style={{ background: s.bg }}>
                      <User size={14} style={{ color: s.text }} />
                    </div>
                    <div>
                      <p className="text-sm text-white">{matched_donor.name}</p>
                      <p className="text-[11px]" style={{ color: overThreshold ? s.text : "#5B6572" }}>
                        Confidence match: {confidence}%{overThreshold ? ` — above ${CONFIDENCE_THRESHOLD}% threshold` : ""}
                      </p>
                    </div>
                  </div>
                  {v.state === "breach" ? (
                    <button onClick={activeOpenAlert} className="flex items-center gap-1 rounded-lg border px-3 py-1.5 text-xs font-medium cursor-pointer border-solid" style={{ borderColor: s.border, color: s.text }}>
                      <ShieldAlert size={12} /> Review lockout
                    </button>
                  ) : (
                    <StatePill state={v.state} />
                  )}
                </div>
              );
            })}
          </div>
        )}
      </Glass>
    </div>
  );
}
