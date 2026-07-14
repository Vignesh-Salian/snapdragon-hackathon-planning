import { Brain, Tag } from "lucide-react";
import { type PredictionResponse, STATE, ACCENT, alertLevelToState } from "../types";
import Glass from "./Glass";
import StatePill from "./StatePill";

export interface PredictionPanelProps {
  data: PredictionResponse;
}

/**
 * Explainable AI (XAI) Prediction Panel showing demand forecasting and top contributing factors.
 */
export default function PredictionPanel({ data }: PredictionPanelProps) {
  const s = STATE[alertLevelToState(data.prediction.alert_level)];
  return (
    <Glass className="p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-white">
          <Brain size={15} style={{ color: ACCENT }} /> Demand Forecast
        </h2>
        <StatePill state={alertLevelToState(data.prediction.alert_level)} />
      </div>

      <div className="mb-4 grid grid-cols-3 gap-3">
        <div>
          <span className="text-[11px]" style={{ color: "#8A97A6" }}>Expected Demand</span>
          <div className="text-xl font-semibold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
            {data.prediction.expected_demand_units}
          </div>
        </div>
        <div>
          <span className="text-[11px]" style={{ color: "#8A97A6" }}>Recommended Stock</span>
          <div className="text-xl font-semibold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
            {data.prediction.recommended_inventory}
          </div>
        </div>
        <div>
          <span className="text-[11px]" style={{ color: "#8A97A6" }}>Health Score</span>
          <div className="text-xl font-semibold" style={{ color: s.text, fontFamily: "'JetBrains Mono', monospace" }}>
            {data.prediction.inventory_health_score}
          </div>
        </div>
      </div>

      {data.top_contributors && data.top_contributors.length > 0 && (
        <div>
          <div className="mb-2 flex items-center gap-1.5">
            <Tag size={11} style={{ color: "#8A97A6" }} />
            <span className="text-[11px]" style={{ color: "#8A97A6" }}>Top contributing factors</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {data.top_contributors.map((c) => (
              <span
                key={c}
                className="rounded-full border px-2.5 py-1 text-[11px]"
                style={{ borderColor: "rgba(255,255,255,0.1)", color: "#C7D0DA", background: "rgba(255,255,255,0.03)" }}
              >
                {c}
              </span>
            ))}
          </div>
        </div>
      )}
      <p className="mt-3 text-[10px]" style={{ color: "#5B6572" }}>Source: AI Engine — /api/v1/predict/demand (via backend proxy)</p>
    </Glass>
  );
}
