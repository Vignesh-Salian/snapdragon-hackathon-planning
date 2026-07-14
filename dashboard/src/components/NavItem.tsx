import React from "react";
import { ACCENT } from "../types";

export interface NavItemProps {
  icon: React.ComponentType<{ size?: number; strokeWidth?: number }>;
  label: string;
  active: boolean;
  onClick: () => void;
}

/**
 * Sidebar navigation item button.
 */
export default function NavItem({ icon: Icon, label, active, onClick }: NavItemProps) {
  return (
    <button
      onClick={onClick}
      className="flex w-full items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm transition-colors cursor-pointer"
      style={{
        color: active ? "#E7FBF8" : "#8A97A6",
        background: active ? "rgba(47,217,196,0.10)" : "transparent",
        borderLeft: active ? `2px solid ${ACCENT}` : "2px solid transparent",
      }}
    >
      <Icon size={17} strokeWidth={2} />
      <span className="font-medium">{label}</span>
    </button>
  );
}
