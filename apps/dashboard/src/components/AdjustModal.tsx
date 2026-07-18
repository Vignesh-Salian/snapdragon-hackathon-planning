import { useState } from "react";
import { Minus, Plus, X } from "lucide-react";
import { ACCENT } from "../types";
import { updateInventory } from "../services/api";
import Glass from "./Glass";

export interface AdjustModalProps {
  onClose: () => void;
  onSuccess?: () => void;
}

const BLOOD_TYPES = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"];

/**
 * Modal to adjust blood stock levels.
 */
export default function AdjustModal({ onClose, onSuccess }: AdjustModalProps) {
  const [bloodType, setBloodType] = useState("O+");
  const [units, setUnits] = useState(5);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await updateInventory("KMC-MANIPAL", bloodType, units);
      window.dispatchEvent(new Event("inventory-updated"));
      onSuccess?.();
      onClose();
    } catch (err: any) {
      console.error(err);
      alert(`Adjustment failed: ${err.message || "Failed to contact gateway"}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(5,4,6,0.7)", backdropFilter: "blur(4px)" }}>
      <Glass className="w-full max-w-sm p-6">
        <div className="mb-4 flex items-start justify-between">
          <h3 className="text-sm font-semibold text-white">Adjust Inventory</h3>
          <button className="cursor-pointer" onClick={onClose}><X size={16} style={{ color: "#8A97A6" }} /></button>
        </div>
        
        <label className="mb-1.5 block text-xs" style={{ color: "#8A97A6" }}>Select Blood Type</label>
        <select 
          value={bloodType} 
          onChange={(e) => setBloodType(e.target.value)}
          className="mb-4 w-full bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.1)] rounded-lg px-3 py-2 text-sm text-white outline-none"
        >
          {BLOOD_TYPES.map(t => <option key={t} value={t} style={{ background: "#131820" }}>{t}</option>)}
        </select>

        <label className="mb-1.5 block text-xs" style={{ color: "#8A97A6" }}>Units to add/remove (signed delta)</label>
        <div className="mb-6 flex items-center gap-3">
          <button onClick={() => setUnits(units - 1)} className="flex h-8 w-8 items-center justify-center rounded-lg border cursor-pointer" style={{ borderColor: "rgba(255,255,255,0.1)" }}><Minus size={13} style={{ color: "#8A97A6" }} /></button>
          <span className="w-16 text-center text-lg font-semibold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>{units > 0 ? `+${units}` : units}</span>
          <button onClick={() => setUnits(units + 1)} className="flex h-8 w-8 items-center justify-center rounded-lg border cursor-pointer" style={{ borderColor: "rgba(255,255,255,0.1)" }}><Plus size={13} style={{ color: "#8A97A6" }} /></button>
        </div>
        
        <button 
          onClick={handleSubmit} 
          disabled={loading}
          className="w-full rounded-lg py-2.5 text-xs font-semibold text-black cursor-pointer hover:opacity-90 disabled:opacity-50" 
          style={{ background: ACCENT }}
        >
          {loading ? "Saving..." : "Submit adjustment"}
        </button>
      </Glass>
    </div>
  );
}
