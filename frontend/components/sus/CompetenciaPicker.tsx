"use client";
import React from "react";

type Props = {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
};

export function CompetenciaPicker({ value, onChange, disabled }: Props) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/\D/g, "").slice(0, 6);
    onChange(raw);
  };

  const isValid = /^\d{6}$/.test(value);

  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs text-slate-400">Competência (AAAAMM)</label>
      <input
        value={value}
        onChange={handleChange}
        maxLength={6}
        disabled={disabled}
        className={`bg-slate-900 border rounded px-3 py-2 text-sm outline-none ${
          isValid ? "border-slate-700" : "border-amber-500"
        }`}
        placeholder="202501"
      />
      {!isValid && <span className="text-amber-400 text-xs">Informe 6 dígitos (AAAAMM).</span>}
    </div>
  );
}
