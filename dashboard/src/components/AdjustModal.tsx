import React, { useState } from "react";
import { Minus, Plus, X } from "lucide-react";
import { ACCENT } from "../types";
import Glass from "./Glass";

export interface AdjustModalProps {
  onClose: () => void;
}

/**
 * Modal to adjust blood stock levels.
 */
export default function AdjustModal({ onClose }: AdjustModalProps) {
  const [units, setUnits] = useState(12);
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(5,4,6,0.7)", backdropFilter: "blur(4px)" }}>
      <Glass className="w-full max-w-sm p-6">
        <div className="mb-4 flex items-start justify-between">
          <h3 className="text-sm font-semibold text-white">Adjust Inventory</h3>
          <button className="cursor-pointer" onClick={onClose}><X size={16} style={{ color: "#8A97A6" }} /></button>
        </div>
        <label className="mb-1.5 block text-xs" style={{ color: "#8A97A6" }}>Blood type</label>
        <div className="mb-4 rounded-lg border px-3 py-2 text-sm text-white" style={{ borderColor: "rgba(255,255,255,0.1)" }}>O-  (breach — 18 units)</div>
        <label className="mb-1.5 block text-xs" style={{ color: "#8A97A6" }}>Units to add</label>
        <div className="mb-6 flex items-center gap-3">
          <button onClick={() => setUnits(Math.max(0, units - 1))} className="flex h-8 w-8 items-center justify-center rounded-lg border cursor-pointer" style={{ borderColor: "rgba(255,255,255,0.1)" }}><Minus size={13} style={{ color: "#8A97A6" }} /></button>
          <span className="w-12 text-center text-lg font-semibold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>{units}</span>
          <button onClick={() => setUnits(units + 1)} className="flex h-8 w-8 items-center justify-center rounded-lg border cursor-pointer" style={{ borderColor: "rgba(255,255,255,0.1)" }}><Plus size={13} style={{ color: "#8A97A6" }} /></button>
        </div>
        <button onClick={onClose} className="w-full rounded-lg py-2.5 text-xs font-semibold text-black cursor-pointer" style={{ background: ACCENT }}>Submit adjustment</button>
      </Glass>
    </div>
  );
}
