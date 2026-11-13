"use client";

import React, { useState } from "react";
import { useA11y } from "../../context/A11yContext";
import { Search, ArrowRight, Sparkles, X, MessageSquareQuote } from "lucide-react";

interface AskClearlyHeroProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onChipSelect: (chipText: string) => void;
  onClearSearch: () => void;
  hasResults: boolean;
  resultsCount: number;
}

export function AskClearlyHero({
  searchQuery,
  onSearchChange,
  onChipSelect,
  onClearSearch,
  hasResults,
  resultsCount,
}: AskClearlyHeroProps) {
  const { language, t, announce } = useA11y();
  const [localInput, setLocalInput] = useState(searchQuery);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const query = localInput.trim();
    onSearchChange(query);
    if (query) {
      announce(language === "es" ? `Buscando eventos para: ${query}` : `Searching events for: ${query}`);
    }
  };

  const handleChipClick = (chip: string) => {
    setLocalInput(chip);
    onChipSelect(chip);
    announce(language === "es" ? `Filtro rápido seleccionado: ${chip}` : `Quick filter selected: ${chip}`);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const chips = [t.chip1, t.chip2, t.chip3, t.chip4];

  return (
    <section
      role="search"
      aria-label={t.askLabel}
      className="p-6 sm:p-8 rounded-3xl bg-gradient-to-br from-[#1C2C5E] via-clearly-baltic to-[#263773] text-white shadow-xl mb-8"
    >
      <div className="max-w-3xl space-y-4">
        {/* Subtitle / Intro */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-white/20 backdrop-blur-md">
          <Sparkles className="w-3.5 h-3.5 text-yellow-300" aria-hidden="true" />
          <span>{t.homeHint}</span>
        </div>

        <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight leading-tight">
          <span className="block">{t.heroTitle1}</span>
          <span className="block text-yellow-300">{t.heroTitle2}</span>
        </h2>

        <p className="text-base sm:text-lg text-blue-100 font-medium leading-relaxed">
          {t.heroSubtitle}
        </p>

        {/* Multiline "Ask CLEARLY" input */}
        <form onSubmit={handleSubmit} className="pt-2">
          <label htmlFor="ask-clearly-input" className="sr-only">
            {t.askLabel}
          </label>
          <div className="flex items-center gap-3 rounded-2xl bg-white text-clearly-obsidian p-3 pl-4 shadow-2xl focus-within:ring-4 focus-within:ring-yellow-300">
            <Search className="w-6 h-6 text-clearly-baltic shrink-0" aria-hidden="true" />
            <textarea
              id="ask-clearly-input"
              rows={2}
              value={localInput}
              onChange={(e) => setLocalInput(e.target.value)}
              onKeyDown={handleKeyDown}
              maxLength={300}
              placeholder={t.askPlaceholder}
              className="w-full resize-none bg-transparent text-sm sm:text-base font-medium text-clearly-obsidian outline-none placeholder:text-gray-400 focus:outline-none"
            />
            {localInput ? (
              <button
                type="button"
                onClick={() => {
                  setLocalInput("");
                  onClearSearch();
                }}
                aria-label={t.clearFilters}
                className="p-2 rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100"
              >
                <X className="w-5 h-5" aria-hidden="true" />
              </button>
            ) : null}
            <button
              type="submit"
              aria-label={t.ask}
              className="grid size-11 shrink-0 cursor-pointer place-items-center rounded-xl bg-clearly-baltic text-white hover:bg-clearly-baltic/90 shadow-md transition-transform active:scale-95"
            >
              <ArrowRight className="w-5 h-5" aria-hidden="true" />
            </button>
          </div>
        </form>

        {/* Quick Suggestion Chips */}
        <div className="pt-2 space-y-2">
          <span className="text-xs font-bold uppercase tracking-wider text-blue-200">
            {t.tryLabel}
          </span>
          <div className="flex flex-wrap gap-2">
            {chips.map((chip, index) => (
              <button
                key={index}
                type="button"
                onClick={() => handleChipClick(chip)}
                className="px-3.5 py-1.5 rounded-full text-xs sm:text-sm font-semibold bg-white/10 hover:bg-white/20 border border-white/20 text-white backdrop-blur-sm transition-all hover:scale-105"
              >
                {chip}
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

