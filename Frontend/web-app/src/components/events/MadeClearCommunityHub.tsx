"use client";

import React, { useState, useEffect, useMemo } from "react";
import { GTA_COMMUNITY_EVENTS, GTAEvent, GTA_POSTAL_COORDS, calculateDistanceKm } from "../../data/communityEventsData";
import { useA11y } from "../../context/A11yContext";
import { AskClearlyHero } from "./AskClearlyHero";
import { EventFiltersBar } from "./EventFiltersBar";
import { EventCardInteractive } from "./EventCardInteractive";
import {
  Calendar,
  Sparkles,
  Bookmark,
  CheckCircle2,
  Inbox,
  Search,
} from "lucide-react";

export function MadeClearCommunityHub() {
  const { language, t, announce } = useA11y();

  // Navigation tab for events: all | recommended | my-events | saved
  const [activeHubTab, setActiveHubTab] = useState<"all" | "recommended" | "my-events" | "saved">("all");

  // Search and filter state
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCity, setSelectedCity] = useState("all");
  const [costFilter, setCostFilter] = useState<"all" | "free" | "paid">("all");
  const [postalCode, setPostalCode] = useState("");
  const [maxDistanceKm, setMaxDistanceKm] = useState<number | null>(null);

  // User engagement bookmarks (persisted in localStorage)
  const [goingEvents, setGoingEvents] = useState<string[]>([]);
  const [savedEvents, setSavedEvents] = useState<string[]>([]);

  // Load saved events from localStorage on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      try {
        const storedGoing = localStorage.getItem("clearly_going_events");
        if (storedGoing) setGoingEvents(JSON.parse(storedGoing));
        const storedSaved = localStorage.getItem("clearly_saved_events");
        if (storedSaved) setSavedEvents(JSON.parse(storedSaved));
      } catch {
        // Ignore
      }
    }
  }, []);

  const handleToggleGoing = (id: string) => {
    setGoingEvents((prev) => {
      const next = prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id];
      try {
        localStorage.setItem("clearly_going_events", JSON.stringify(next));
      } catch {}
      announce(
        next.includes(id)
          ? language === "es"
            ? "Agregado a Mis Eventos"
            : "Added to My Events"
          : language === "es"
          ? "Eliminado de Mis Eventos"
          : "Removed from My Events"
      );
      return next;
    });
  };

  const handleToggleSaved = (id: string) => {
    setSavedEvents((prev) => {
      const next = prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id];
      try {
        localStorage.setItem("clearly_saved_events", JSON.stringify(next));
      } catch {}
      announce(
        next.includes(id)
          ? language === "es"
            ? "Evento guardado"
            : "Event saved"
          : language === "es"
          ? "Evento eliminado de guardados"
          : "Event removed from saved"
      );
      return next;
    });
  };

  // Determine user coordinates if postal code is provided
  const userCoords = useMemo(() => {
    if (!postalCode) return null;
    const clean = postalCode.replace(/\s+/g, "").toUpperCase();
    // Try matching 3 chars, then 2 chars, then 1 char
    for (const len of [3, 2, 1]) {
      const prefix = clean.slice(0, len);
      if (GTA_POSTAL_COORDS[prefix]) {
        return GTA_POSTAL_COORDS[prefix];
      }
    }
    return null;
  }, [postalCode]);

  // Filter and score events
  const filteredEvents = useMemo(() => {
    return GTA_COMMUNITY_EVENTS.map((evt) => {
      // Calculate distance if coordinates available
      let distanceKm: number | undefined = undefined;
      if (userCoords) {
        distanceKm = calculateDistanceKm(userCoords.lat, userCoords.lng, evt.lat, evt.lng);
      }

      // Check match with search query
      let isSearchMatch = false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const titleMatch = evt.title[language].toLowerCase().includes(q);
        const cityMatch = evt.municipality.toLowerCase().includes(q);
        const whatMatch = evt.plain_questions.q1[language].toLowerCase().includes(q);
        const orgMatch = evt.organizer_name.toLowerCase().includes(q);
        const whyMatch = evt.why_recommended[language].toLowerCase().includes(q);
        isSearchMatch = titleMatch || cityMatch || whatMatch || orgMatch || whyMatch;
      }

      return {
        ...evt,
        distanceKm,
        isSearchMatch,
      };
    }).filter((evt) => {
      // Tab filter
      if (activeHubTab === "my-events" && !goingEvents.includes(evt.id)) return false;
      if (activeHubTab === "saved" && !savedEvents.includes(evt.id)) return false;
      if (activeHubTab === "recommended" && searchQuery && !evt.isSearchMatch) return false;

      // City filter
      if (selectedCity !== "all" && evt.municipality !== selectedCity) return false;

      // Cost filter
      if (costFilter === "free" && !evt.is_free) return false;
      if (costFilter === "paid" && evt.is_free) return false;

      // Distance filter
      if (maxDistanceKm !== null && evt.distanceKm !== undefined) {
        if (evt.distanceKm > maxDistanceKm) return false;
      }

      // Search filter if actively searching and in "all" tab
      if (searchQuery && activeHubTab === "all" && !evt.isSearchMatch) {
        // If there's an explicit search query, show matches first
        return true;
      }

      return true;
    }).sort((a, b) => {
      // Sort matches higher if search is active
      if (searchQuery) {
        if (a.isSearchMatch && !b.isSearchMatch) return -1;
        if (!a.isSearchMatch && b.isSearchMatch) return 1;
      }
      // Sort by distance if available
      if (a.distanceKm !== undefined && b.distanceKm !== undefined) {
        return a.distanceKm - b.distanceKm;
      }
      return 0;
    });
  }, [
    activeHubTab,
    searchQuery,
    selectedCity,
    costFilter,
    maxDistanceKm,
    userCoords,
    goingEvents,
    savedEvents,
    language,
  ]);

  const activeFilterCount =
    (selectedCity !== "all" ? 1 : 0) +
    (costFilter !== "all" ? 1 : 0) +
    (maxDistanceKm !== null ? 1 : 0) +
    (postalCode ? 1 : 0);

  const handleClearFilters = () => {
    setSelectedCity("all");
    setCostFilter("all");
    setPostalCode("");
    setMaxDistanceKm(null);
    setSearchQuery("");
  };

  return (
    <section
      role="region"
      aria-labelledby="community-hub-heading"
      className="mt-12 mb-16 scroll-mt-20"
    >
      {/* Section Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between pb-6 border-b-2 border-clearly-birch dark:border-[#383838] gap-4 mb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-clearly-baltic/10 text-clearly-baltic dark:bg-blue-900/40 dark:text-blue-300 mb-2">
            <Calendar className="w-3.5 h-3.5" aria-hidden="true" />
            Marketplace Comunitario GTA • Formato "Made Clear"
          </div>
          <h2
            id="community-hub-heading"
            className="text-3xl sm:text-4xl font-black tracking-tight text-clearly-obsidian dark:text-white"
          >
            {t.allEventsTitle}
          </h2>
          <p className="mt-1 text-base text-gray-600 dark:text-gray-300 font-medium max-w-2xl">
            {t.heroSubtitle}
          </p>
        </div>

        {/* Navigation Tabs (All, Recommended, My Events, Saved) */}
        <div
          role="tablist"
          aria-label="Vistas del hub comunitario"
          className="flex flex-wrap items-center gap-1.5 p-1 rounded-2xl bg-gray-100 dark:bg-[#1E1E1E] border border-clearly-birch dark:border-[#383838]"
        >
          <button
            type="button"
            role="tab"
            aria-selected={activeHubTab === "all"}
            onClick={() => setActiveHubTab("all")}
            className={`px-3.5 py-2 text-xs font-bold rounded-xl transition-all ${
              activeHubTab === "all"
                ? "bg-white dark:bg-[#2C2C2C] text-clearly-obsidian dark:text-white shadow-sm"
                : "text-gray-600 dark:text-gray-400 hover:text-clearly-obsidian"
            }`}
          >
            {language === "es" ? "Todos los eventos" : language === "en" ? "All Events" : "ਸਾਰੇ ਸਮਾਗਮ"} ({GTA_COMMUNITY_EVENTS.length})
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={activeHubTab === "recommended"}
            onClick={() => setActiveHubTab("recommended")}
            className={`px-3.5 py-2 text-xs font-bold rounded-xl flex items-center gap-1.5 transition-all ${
              activeHubTab === "recommended"
                ? "bg-clearly-baltic text-white shadow-sm"
                : "text-gray-600 dark:text-gray-400 hover:text-clearly-baltic"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-yellow-300" aria-hidden="true" />
            <span>{t.recommendedTitle}</span>
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={activeHubTab === "my-events"}
            onClick={() => setActiveHubTab("my-events")}
            className={`px-3.5 py-2 text-xs font-bold rounded-xl flex items-center gap-1.5 transition-all ${
              activeHubTab === "my-events"
                ? "bg-green-700 text-white shadow-sm"
                : "text-gray-600 dark:text-gray-400 hover:text-green-700"
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" />
            <span>{t.myEventsTitle}</span>
            {goingEvents.length > 0 && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] font-black bg-white text-green-800">
                {goingEvents.length}
              </span>
            )}
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={activeHubTab === "saved"}
            onClick={() => setActiveHubTab("saved")}
            className={`px-3.5 py-2 text-xs font-bold rounded-xl flex items-center gap-1.5 transition-all ${
              activeHubTab === "saved"
                ? "bg-clearly-royal text-white shadow-sm"
                : "text-gray-600 dark:text-gray-400 hover:text-clearly-royal"
            }`}
          >
            <Bookmark className="w-3.5 h-3.5" aria-hidden="true" />
            <span>{t.savedTitle}</span>
            {savedEvents.length > 0 && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] font-black bg-white text-clearly-royal">
                {savedEvents.length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Ask Clearly Hero (Natural language search & quick chips) */}
      <AskClearlyHero
        searchQuery={searchQuery}
        onSearchChange={(q) => {
          setSearchQuery(q);
          if (q) setActiveHubTab("all");
        }}
        onChipSelect={(chip) => {
          setSearchQuery(chip);
          setActiveHubTab("all");
        }}
        onClearSearch={() => setSearchQuery("")}
        hasResults={filteredEvents.length > 0}
        resultsCount={filteredEvents.length}
      />

      {/* Filter controls bar */}
      <EventFiltersBar
        selectedCity={selectedCity}
        onCityChange={setSelectedCity}
        costFilter={costFilter}
        onCostChange={setCostFilter}
        postalCode={postalCode}
        onPostalCodeChange={setPostalCode}
        maxDistanceKm={maxDistanceKm}
        onMaxDistanceChange={setMaxDistanceKm}
        onClearAll={handleClearFilters}
        activeFilterCount={activeFilterCount}
      />

      {/* Results Count & Search Feedback */}
      <div className="flex items-center justify-between mb-4 px-1">
        <span className="text-sm font-bold text-gray-700 dark:text-gray-300">
          {t.resultsCount(filteredEvents.length)}
          {searchQuery && (
            <span className="ml-2 font-normal text-xs text-clearly-baltic dark:text-blue-300">
              (filtrado por: "{searchQuery}")
            </span>
          )}
        </span>

        {activeHubTab === "recommended" && (
          <span className="inline-flex items-center gap-1.5 text-xs text-amber-700 dark:text-amber-400 font-semibold bg-amber-50 dark:bg-amber-950/40 px-2.5 py-1 rounded-full">
            <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
            {t.agentAiLabel}
          </span>
        )}
      </div>

      {/* Events Grid or Empty State */}
      {filteredEvents.length === 0 ? (
        <div className="p-12 text-center rounded-3xl bg-gray-50 dark:bg-[#1E1E1E] border-2 border-dashed border-clearly-birch dark:border-[#383838]">
          <Inbox className="w-12 h-12 text-gray-400 mx-auto mb-3" aria-hidden="true" />
          <h3 className="text-xl font-bold text-clearly-obsidian dark:text-white">
            {activeHubTab === "my-events"
              ? t.myEventsEmpty
              : activeHubTab === "saved"
              ? t.savedEmpty
              : t.noRecommendations}
          </h3>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 max-w-md mx-auto">
            {activeHubTab === "all" || activeHubTab === "recommended"
              ? "Prueba cambiando de ciudad o retirando filtros de costo para ver más actividades en el GTA."
              : "Explora la pestaña 'Todos los eventos' y haz clic en 'Voy a asistir' o 'Guardar'."}
          </p>
          <div className="mt-4">
            <button
              type="button"
              onClick={handleClearFilters}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-clearly-baltic text-white hover:bg-clearly-baltic/90 shadow-sm"
            >
              {t.clearFilters}
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredEvents.map((evt) => (
            <EventCardInteractive
              key={evt.id}
              event={evt}
              distanceKm={evt.distanceKm}
              isGoing={goingEvents.includes(evt.id)}
              isSaved={savedEvents.includes(evt.id)}
              onToggleGoing={handleToggleGoing}
              onToggleSaved={handleToggleSaved}
              isRecommendedMatch={Boolean(searchQuery && evt.isSearchMatch)}
            />
          ))}
        </div>
      )}
    </section>
  );
}

