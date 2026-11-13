"use client";

import React, { useState } from "react";
import { useA11y } from "../../context/A11yContext";
import { Filter, MapPin, DollarSign, X, Check, Navigation } from "lucide-react";

interface EventFiltersBarProps {
  selectedCity: string;
  onCityChange: (city: string) => void;
  costFilter: "all" | "free" | "paid";
  onCostChange: (cost: "all" | "free" | "paid") => void;
  postalCode: string;
  onPostalCodeChange: (postal: string) => void;
  maxDistanceKm: number | null;
  onMaxDistanceChange: (km: number | null) => void;
  onClearAll: () => void;
  activeFilterCount: number;
}

export function EventFiltersBar({
  selectedCity,
  onCityChange,
  costFilter,
  onCostChange,
  postalCode,
  onPostalCodeChange,
  maxDistanceKm,
  onMaxDistanceChange,
  onClearAll,
  activeFilterCount,
}: EventFiltersBarProps) {
  const { language, t } = useA11y();
  const [showFilters, setShowFilters] = useState(false);
  const [localPostal, setLocalPostal] = useState(postalCode);

  const cities = [
    { key: "all", label: t.municipalities.all },
    { key: "brampton", label: t.municipalities.brampton },
    { key: "toronto", label: t.municipalities.toronto },
    { key: "mississauga", label: t.municipalities.mississauga },
    { key: "markham", label: t.municipalities.markham },
    { key: "vaughan", label: t.municipalities.vaughan },
    { key: "richmond_hill", label: t.municipalities.richmond_hill },
    { key: "oakville", label: t.municipalities.oakville },
    { key: "burlington", label: t.municipalities.burlington },
    { key: "hamilton", label: t.municipalities.hamilton },
  ];

  const handlePostalSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onPostalCodeChange(localPostal.trim().toUpperCase());
  };

  const isPostalValid =
    !postalCode ||
    /^[ML][0-9][A-Z] ?[0-9][A-Z][0-9]$/i.test(postalCode) ||
    /^[ML][0-9]/i.test(postalCode);

  return (
    <div className="mb-6 p-4 rounded-2xl bg-white dark:bg-[#1E1E1E] border-2 border-clearly-birch dark:border-[#383838] shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-clearly-baltic dark:text-blue-400" aria-hidden="true" />
          <span className="text-sm font-bold text-clearly-obsidian dark:text-white">
            {t.filtersTitle}
          </span>
          {activeFilterCount > 0 && (
            <span className="px-2 py-0.5 rounded-full text-xs font-black bg-clearly-baltic text-white">
              {activeFilterCount}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {activeFilterCount > 0 && (
            <button
              type="button"
              onClick={onClearAll}
              className="text-xs font-bold text-clearly-danger dark:text-red-400 hover:underline"
            >
              {t.clearFilters}
            </button>
          )}

          <button
            type="button"
            onClick={() => setShowFilters((prev) => !prev)}
            aria-expanded={showFilters}
            className="px-3 py-1.5 rounded-lg text-xs font-bold border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-[#252525] text-clearly-obsidian dark:text-gray-200"
          >
            {showFilters ? "Ocultar filtros" : "Ajustar filtros"}
          </button>
        </div>
      </div>

      {/* Expandable Filter Controls */}
      {showFilters && (
        <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-800 space-y-4">
          {/* City selector */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-2">
              {t.filterCity} (Gran Toronto - GTA)
            </label>
            <div className="flex flex-wrap gap-1.5">
              {cities.map((c) => (
                <button
                  key={c.key}
                  type="button"
                  onClick={() => onCityChange(c.key)}
                  aria-pressed={selectedCity === c.key}
                  className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                    selectedCity === c.key
                      ? "bg-clearly-baltic text-white shadow-sm"
                      : "bg-gray-100 dark:bg-[#2A2A2A] text-clearly-obsidian dark:text-gray-300 hover:bg-gray-200"
                  }`}
                >
                  {c.label}
                </button>
              ))}
            </div>
          </div>

          {/* Cost filter */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-2">
              {t.filterCost}
            </label>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => onCostChange("all")}
                aria-pressed={costFilter === "all"}
                className={`px-3 py-1 rounded-lg text-xs font-bold ${
                  costFilter === "all"
                    ? "bg-clearly-baltic text-white"
                    : "bg-gray-100 dark:bg-[#2A2A2A] text-clearly-obsidian dark:text-gray-300"
                }`}
              >
                {t.filterCostAll}
              </button>
              <button
                type="button"
                onClick={() => onCostChange("free")}
                aria-pressed={costFilter === "free"}
                className={`px-3 py-1 rounded-lg text-xs font-bold ${
                  costFilter === "free"
                    ? "bg-green-700 text-white"
                    : "bg-gray-100 dark:bg-[#2A2A2A] text-clearly-obsidian dark:text-gray-300"
                }`}
              >
                {t.filterCostFree}
              </button>
              <button
                type="button"
                onClick={() => onCostChange("paid")}
                aria-pressed={costFilter === "paid"}
                className={`px-3 py-1 rounded-lg text-xs font-bold ${
                  costFilter === "paid"
                    ? "bg-clearly-royal text-white"
                    : "bg-gray-100 dark:bg-[#2A2A2A] text-clearly-obsidian dark:text-gray-300"
                }`}
              >
                {t.filterCostPaid}
              </button>
            </div>
          </div>

          {/* Postal Code & Distance Radius */}
          <div>
            <label
              htmlFor="postal-filter-input"
              className="block text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-2"
            >
              {t.filterPostal} ({t.filterDistance})
            </label>
            <div className="flex flex-wrap items-center gap-2">
              <form onSubmit={handlePostalSubmit} className="flex items-center gap-2">
                <input
                  id="postal-filter-input"
                  type="text"
                  value={localPostal}
                  onChange={(e) => setLocalPostal(e.target.value.toUpperCase())}
                  placeholder={t.filterPostalPlaceholder}
                  maxLength={7}
                  className="w-32 px-3 py-1.5 rounded-lg border text-xs font-mono uppercase bg-gray-50 dark:bg-[#2A2A2A] text-clearly-obsidian dark:text-white border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-clearly-baltic"
                />
                <button
                  type="submit"
                  className="px-3 py-1.5 rounded-lg text-xs font-bold bg-clearly-baltic text-white hover:bg-clearly-baltic/90"
                >
                  {t.applyFilters}
                </button>
              </form>

              {/* Radius pills */}
              <div className="flex items-center gap-1">
                {[5, 10, 25].map((km) => (
                  <button
                    key={km}
                    type="button"
                    onClick={() => onMaxDistanceChange(km)}
                    className={`px-2.5 py-1 rounded-md text-xs font-bold ${
                      maxDistanceKm === km
                        ? "bg-clearly-royal text-white"
                        : "bg-gray-100 dark:bg-[#2A2A2A] text-gray-700 dark:text-gray-300"
                    }`}
                  >
                    {t.filterWithin(km)}
                  </button>
                ))}
                {maxDistanceKm !== null && (
                  <button
                    type="button"
                    onClick={() => onMaxDistanceChange(null)}
                    className="p-1 text-gray-400 hover:text-gray-600"
                    title={t.filterDistanceAny}
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
            {!isPostalValid && postalCode && (
              <p className="mt-1 text-xs text-amber-600 dark:text-amber-400 font-semibold">
                {t.filterPostalUnknown}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

