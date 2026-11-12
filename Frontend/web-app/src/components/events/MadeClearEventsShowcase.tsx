"use client";

import React, { useState } from "react";
import { CommunityEvent } from "../../types/document";
import { SAMPLE_EVENTS } from "../../data/sampleDocuments";
import { useA11y } from "../../context/A11yContext";
import {
  Calendar,
  MapPin,
  Bus,
  Accessibility,
  Heart,
  Volume2,
  CheckCircle2,
  Share2,
  Filter,
} from "lucide-react";

export function MadeClearEventsShowcase() {
  const { speak, announce } = useA11y();
  const [filter, setFilter] = useState<"all" | "free" | "wheelchair" | "seniors">("all");
  const [familyNotified, setFamilyNotified] = useState<Record<string, boolean>>({});

  const filteredEvents = SAMPLE_EVENTS.filter((evt) => {
    if (filter === "free") return evt.is_free;
    if (filter === "wheelchair") return evt.is_wheelchair_accessible;
    if (filter === "seniors") return evt.is_senior_friendly;
    return true;
  });

  const handleSpeakEvent = (evt: CommunityEvent) => {
    const text = `Evento: ${evt.title}. Qué es: ${evt.what}. Cuándo y dónde: ${evt.when_where}. Costo: ${evt.cost}. Cómo registrarse: ${evt.how_to_register}. Transporte: ${evt.transport_tip}`;
    announce(`Leyendo evento: ${evt.title}`);
    speak(text);
  };

  const handleNotifyFamily = (evtId: string) => {
    setFamilyNotified((prev) => ({ ...prev, [evtId]: true }));
    announce("Evento enviado a tu familiar Carlos por WhatsApp para acompañarte.");
  };

  return (
    <section
      role="region"
      aria-labelledby="events-section-title"
      className="p-6 sm:p-8 rounded-3xl border-2 transition-all duration-200 bg-white dark:bg-[#1A1A1A] border-clearly-birch dark:border-[#383838] shadow-md mb-12"
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-clearly-birch/60 dark:border-gray-800 gap-4">
        <div>
          <h2
            id="events-section-title"
            className="text-2xl sm:text-3xl font-bold tracking-tight text-clearly-obsidian dark:text-white flex items-center gap-3"
          >
            <Calendar className="w-8 h-8 text-clearly-baltic dark:text-blue-400" aria-hidden="true" />
            Marketplace Comunitario — Formato "Made Clear"
          </h2>
          <p className="mt-1 text-sm sm:text-base text-gray-600 dark:text-gray-300">
            Actividades cívicas, de salud y talleres en Brampton y GTA reescritos en 4 preguntas
            claras para evitar confusiones.
          </p>
        </div>

        {/* Filter Pills */}
        <div
          role="group"
          aria-label="Filtros de accesibilidad de eventos"
          className="flex flex-wrap items-center gap-2"
        >
          <button
            type="button"
            onClick={() => setFilter("all")}
            aria-pressed={filter === "all"}
            className={`px-3 py-1.5 text-xs font-bold rounded-lg border-2 ${
              filter === "all"
                ? "bg-clearly-baltic text-white border-clearly-baltic"
                : "bg-white dark:bg-[#252525] text-clearly-obsidian dark:text-gray-300 border-clearly-birch dark:border-gray-700"
            }`}
          >
            Todos ({SAMPLE_EVENTS.length})
          </button>

          <button
            type="button"
            onClick={() => setFilter("free")}
            aria-pressed={filter === "free"}
            className={`px-3 py-1.5 text-xs font-bold rounded-lg border-2 ${
              filter === "free"
                ? "bg-green-700 text-white border-green-700"
                : "bg-white dark:bg-[#252525] text-clearly-obsidian dark:text-gray-300 border-clearly-birch dark:border-gray-700"
            }`}
          >
            100% Gratis
          </button>

          <button
            type="button"
            onClick={() => setFilter("wheelchair")}
            aria-pressed={filter === "wheelchair"}
            className={`px-3 py-1.5 text-xs font-bold rounded-lg border-2 ${
              filter === "wheelchair"
                ? "bg-clearly-royal text-white border-clearly-royal"
                : "bg-white dark:bg-[#252525] text-clearly-obsidian dark:text-gray-300 border-clearly-birch dark:border-gray-700"
            }`}
          >
            Acceso Rampa / Silla
          </button>
        </div>
      </div>

      {/* Events Grid */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {filteredEvents.map((evt) => (
          <article
            key={evt.id}
            role="article"
            aria-label={`Evento comunitario: ${evt.title}`}
            className="p-5 rounded-2xl border-2 flex flex-col justify-between transition-all bg-white dark:bg-[#222222] border-clearly-birch dark:border-gray-700 hover:border-clearly-royal dark:hover:border-clearly-royal shadow-sm"
          >
            <div>
              {/* Event Header */}
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="px-2.5 py-0.5 rounded-md text-xs font-extrabold uppercase tracking-wider bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300 border border-green-300 dark:border-green-800">
                  {evt.cost}
                </span>

                <span className="text-xs font-bold text-clearly-baltic dark:text-blue-400">
                  {evt.date_label}
                </span>
              </div>

              <h3 className="text-lg font-bold text-clearly-obsidian dark:text-white leading-snug">
                {evt.title}
              </h3>

              <span className="text-xs text-gray-500 dark:text-gray-400 block mt-0.5">
                Organiza: {evt.organizer}
              </span>

              {/* 4 Made Clear Canonical Questions */}
              <div className="mt-4 space-y-3 text-sm">
                <div>
                  <strong className="block text-xs font-bold uppercase tracking-wider text-clearly-baltic dark:text-blue-300">
                    1. ¿Qué es?
                  </strong>
                  <p className="mt-0.5 text-gray-700 dark:text-gray-300 font-medium">{evt.what}</p>
                </div>

                <div>
                  <strong className="block text-xs font-bold uppercase tracking-wider text-clearly-baltic dark:text-blue-300">
                    2. ¿Cuándo y dónde?
                  </strong>
                  <p className="mt-0.5 text-gray-700 dark:text-gray-300 font-medium">
                    {evt.when_where}
                  </p>
                </div>

                {evt.transport_tip && (
                  <div className="p-2.5 rounded-lg bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900/40 flex items-start gap-2 text-xs">
                    <Bus className="w-4 h-4 text-clearly-baltic dark:text-blue-400 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700 dark:text-gray-300">{evt.transport_tip}</span>
                  </div>
                )}

                <div>
                  <strong className="block text-xs font-bold uppercase tracking-wider text-clearly-baltic dark:text-blue-300">
                    3. ¿Cómo registrarse?
                  </strong>
                  <p className="mt-0.5 text-gray-700 dark:text-gray-300 font-medium">
                    {evt.how_to_register}
                  </p>
                </div>
              </div>
            </div>

            {/* Event Actions Footer */}
            <div className="mt-6 pt-4 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between gap-2">
              <button
                type="button"
                onClick={() => handleSpeakEvent(evt)}
                aria-label={`Escuchar detalles del evento ${evt.title}`}
                className="p-2 rounded-lg text-clearly-royal dark:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-950 flex items-center gap-1.5 text-xs font-bold"
              >
                <Volume2 className="w-4 h-4" aria-hidden="true" />
                <span>Escuchar</span>
              </button>

              <button
                type="button"
                onClick={() => handleNotifyFamily(evt.id)}
                aria-label={`Avisar a familiar para ir a ${evt.title}`}
                className={`px-3 py-1.5 text-xs font-bold rounded-lg flex items-center gap-1.5 transition-all ${
                  familyNotified[evt.id]
                    ? "bg-green-600 text-white"
                    : "bg-clearly-baltic text-white hover:bg-clearly-baltic/90"
                }`}
              >
                {familyNotified[evt.id] ? (
                  <>
                    <CheckCircle2 className="w-4 h-4" aria-hidden="true" />
                    <span>Avisado a Carlos</span>
                  </>
                ) : (
                  <>
                    <Heart className="w-4 h-4" aria-hidden="true" />
                    <span>Ir con mi familia</span>
                  </>
                )}
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
