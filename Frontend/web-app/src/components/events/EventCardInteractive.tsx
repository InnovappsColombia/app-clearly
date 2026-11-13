"use client";

import React, { useState } from "react";
import { GTAEvent } from "../../data/communityEventsData";
import { useA11y } from "../../context/A11yContext";
import { AttendGuideModal } from "./AttendGuideModal";
import {
  Calendar,
  MapPin,
  Clock,
  Volume2,
  VolumeX,
  Share2,
  Heart,
  CheckCircle2,
  Navigation,
  FileQuestion,
  HelpCircle,
  Sparkles,
  ExternalLink,
  ClipboardList,
  Bookmark,
  BookmarkCheck,
} from "lucide-react";

interface EventCardInteractiveProps {
  event: GTAEvent;
  distanceKm?: number;
  isGoing: boolean;
  isSaved: boolean;
  onToggleGoing: (id: string) => void;
  onToggleSaved: (id: string) => void;
  isRecommendedMatch?: boolean;
}

export function EventCardInteractive({
  event,
  distanceKm,
  isGoing,
  isSaved,
  onToggleGoing,
  onToggleSaved,
  isRecommendedMatch = false,
}: EventCardInteractiveProps) {
  const { language, t, speak, stopSpeech, isSpeaking, currentSpeechText, announce } = useA11y();
  const [activeTab, setActiveTab] = useState<"simple" | "clearly">("simple");
  const [isAttendModalOpen, setIsAttendModalOpen] = useState(false);
  const [familyNotified, setFamilyNotified] = useState(false);

  // Format date range nicely
  const formatDateRange = (startStr: string, endStr?: string) => {
    try {
      const start = new Date(startStr);
      const locale = language === "pa" ? "pa-IN" : language === "en" ? "en-US" : "es-ES";
      const dateFormatted = start.toLocaleDateString(locale, {
        weekday: "short",
        month: "short",
        day: "numeric",
      });
      const timeStart = start.toLocaleTimeString(locale, { hour: "numeric", minute: "2-digit" });
      if (endStr) {
        const end = new Date(endStr);
        const timeEnd = end.toLocaleTimeString(locale, { hour: "numeric", minute: "2-digit" });
        return `${dateFormatted}, ${timeStart} - ${timeEnd}`;
      }
      return `${dateFormatted}, ${timeStart}`;
    } catch {
      return startStr;
    }
  };

  const formattedDate = formatDateRange(event.start_datetime, event.end_datetime);

  const handleReadAloud = () => {
    const speechTarget =
      activeTab === "clearly"
        ? `${event.title[language]}. ${t.q1}: ${event.plain_questions.q1[language]}. ${t.q2}: ${event.plain_questions.q2[language]}. ${t.q3}: ${event.plain_questions.q3[language]}. ${t.q4}: ${event.plain_questions.q4[language]}.`
        : `${event.title[language]}. ${event.location_name}. ${formattedDate}. ${t.cost}: ${event.cost_amount ?? t.free}. ${event.plain_questions.q1[language]}`;

    if (isSpeaking && currentSpeechText === speechTarget) {
      stopSpeech();
    } else {
      announce(`${t.listen}: ${event.title[language]}`);
      speak(speechTarget);
    }
  };

  const handleNotifyCarlos = () => {
    setFamilyNotified(true);
    announce(t.notifiedFamily);
  };

  const isCurrentCardSpeaking = isSpeaking && currentSpeechText?.includes(event.title[language]);

  return (
    <>
      <article
        role="article"
        aria-label={`${event.title[language]} - ${t.municipalities[event.municipality]}`}
        className="card-surface relative flex flex-col justify-between rounded-3xl border-2 transition-all duration-200 bg-white dark:bg-[#202020] border-clearly-birch dark:border-[#3A3A3A] hover:border-clearly-royal dark:hover:border-clearly-royal shadow-md p-5 sm:p-6"
      >
        <div>
          {/* Header Badges */}
          <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-teal-50 text-teal-800 dark:bg-teal-950/60 dark:text-teal-300 border border-teal-200 dark:border-teal-800">
                {t.categories[event.category] ?? event.category}
              </span>
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-50 text-clearly-baltic dark:bg-blue-950/60 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
                {t.municipalities[event.municipality] ?? event.municipality}
              </span>
              {event.is_free && (
                <span className="px-2.5 py-1 rounded-full text-xs font-black uppercase tracking-wider bg-green-100 text-green-900 dark:bg-green-950/80 dark:text-green-300 border border-green-300 dark:border-green-800">
                  {t.free}
                </span>
              )}
            </div>

            {distanceKm !== undefined && (
              <span className="text-xs font-extrabold text-clearly-baltic dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 px-2 py-0.5 rounded-md">
                {t.distanceAway(distanceKm)}
              </span>
            )}
          </div>

          {/* Event Image if available */}
          {event.image && (
            <div className="aspect-[16/9] w-full rounded-2xl overflow-hidden mb-4 bg-gray-100 dark:bg-gray-800">
              <img
                src={event.image}
                alt=""
                loading="lazy"
                className="w-full h-full object-cover"
              />
            </div>
          )}

          {/* Title */}
          <h3 className="text-xl sm:text-2xl font-black text-clearly-obsidian dark:text-white leading-tight">
            {event.title[language]}
          </h3>

          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {t.organizer}: <strong className="text-gray-700 dark:text-gray-300">{event.organizer_name}</strong>
          </p>

          {/* "Why Recommended" AI Hook if Search match */}
          {isRecommendedMatch && event.why_recommended && (
            <div className="mt-3 p-3 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 text-xs text-amber-900 dark:text-amber-200 flex items-start gap-2">
              <Sparkles className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" aria-hidden="true" />
              <div>
                <strong>{t.whyRecommended}:</strong>{" "}
                <span>{event.why_recommended[language]}</span>
              </div>
            </div>
          )}

          {/* View Mode Tabs (Simple vs CLEARLY) */}
          <div
            role="tablist"
            aria-label={t.viewTabs}
            className="mt-4 flex rounded-xl p-1 bg-gray-100 dark:bg-[#1A1A1A] border border-clearly-birch/60 dark:border-gray-800"
          >
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "simple"}
              onClick={() => setActiveTab("simple")}
              className={`flex-1 py-1.5 text-xs font-extrabold rounded-lg transition-all ${
                activeTab === "simple"
                  ? "bg-white dark:bg-[#2C2C2C] text-clearly-obsidian dark:text-white shadow-sm"
                  : "text-gray-500 dark:text-gray-400 hover:text-clearly-obsidian"
              }`}
            >
              {t.tabSimple}
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "clearly"}
              onClick={() => setActiveTab("clearly")}
              className={`flex-1 py-1.5 text-xs font-black tracking-wide rounded-lg flex items-center justify-center gap-1.5 transition-all ${
                activeTab === "clearly"
                  ? "bg-clearly-baltic text-white shadow-sm"
                  : "text-gray-500 dark:text-gray-400 hover:text-clearly-baltic"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-yellow-300" aria-hidden="true" />
              {t.tabClearly} (6 Pistas)
            </button>
          </div>

          {/* Content based on Active Tab */}
          {activeTab === "simple" ? (
            <div className="mt-4 space-y-2.5 text-sm">
              <div className="flex items-start gap-2 text-gray-700 dark:text-gray-200">
                <Calendar className="w-4 h-4 text-clearly-baltic dark:text-blue-400 shrink-0 mt-0.5" aria-hidden="true" />
                <span className="font-semibold">{formattedDate}</span>
              </div>

              <div className="flex items-start gap-2 text-gray-700 dark:text-gray-200">
                <MapPin className="w-4 h-4 text-clearly-baltic dark:text-blue-400 shrink-0 mt-0.5" aria-hidden="true" />
                <span>
                  {event.location_name} <span className="text-xs text-gray-500">({event.address})</span>
                </span>
              </div>

              <p className="mt-2 text-sm text-gray-600 dark:text-gray-300 leading-relaxed font-medium">
                {event.plain_questions.q1[language]}
              </p>
            </div>
          ) : (
            /* CLEARLY View: The 6 Canonical Questions */
            <div className="mt-4 space-y-3 p-3.5 rounded-2xl bg-blue-50/70 dark:bg-blue-950/30 border border-blue-200/80 dark:border-blue-900/40 text-xs">
              <div>
                <strong className="block font-bold text-clearly-baltic dark:text-blue-300">{t.q1}</strong>
                <p className="mt-0.5 text-gray-800 dark:text-gray-200 font-medium">{event.plain_questions.q1[language]}</p>
              </div>

              <div>
                <strong className="block font-bold text-clearly-baltic dark:text-blue-300">{t.q2}</strong>
                <p className="mt-0.5 text-gray-800 dark:text-gray-200 font-medium">{event.plain_questions.q2[language]}</p>
              </div>

              <div>
                <strong className="block font-bold text-clearly-baltic dark:text-blue-300">{t.q3}</strong>
                <p className="mt-0.5 text-gray-800 dark:text-gray-200 font-medium">{event.plain_questions.q3[language]}</p>
              </div>

              <div>
                <strong className="block font-bold text-clearly-baltic dark:text-blue-300">{t.q4}</strong>
                <p className="mt-0.5 text-gray-800 dark:text-gray-200 font-medium">{event.plain_questions.q4[language]}</p>
              </div>

              <div>
                <strong className="block font-bold text-clearly-baltic dark:text-blue-300">{t.q5}</strong>
                <p className="mt-0.5 text-gray-800 dark:text-gray-200 font-medium">{event.plain_questions.q5[language]}</p>
              </div>

              <div>
                <strong className="block font-bold text-clearly-baltic dark:text-blue-300">{t.q6}</strong>
                <p className="mt-0.5 text-gray-800 dark:text-gray-200 font-medium">{event.plain_questions.q6[language]}</p>
              </div>
            </div>
          )}
        </div>

        {/* Card Actions Footer */}
        <div className="mt-6 pt-4 border-t border-clearly-birch/60 dark:border-gray-800 space-y-3">
          {/* Top action row: Attend Guide & TTS Read Aloud */}
          <div className="flex flex-wrap items-center justify-between gap-2">
            <button
              type="button"
              onClick={() => setIsAttendModalOpen(true)}
              className="px-3.5 py-2 rounded-xl text-xs font-bold bg-clearly-baltic text-white hover:bg-clearly-baltic/90 shadow-sm flex items-center gap-1.5"
            >
              <ClipboardList className="w-4 h-4 text-yellow-300" aria-hidden="true" />
              <span>{t.attendTitle}</span>
            </button>

            <button
              type="button"
              onClick={handleReadAloud}
              aria-pressed={isCurrentCardSpeaking}
              className={`p-2 rounded-xl text-xs font-bold flex items-center gap-1.5 border transition-all ${
                isCurrentCardSpeaking
                  ? "bg-clearly-danger text-white border-clearly-danger animate-pulse"
                  : "bg-gray-100 dark:bg-gray-800 text-clearly-obsidian dark:text-gray-200 border-gray-300 dark:border-gray-700 hover:bg-white"
              }`}
            >
              {isCurrentCardSpeaking ? (
                <>
                  <VolumeX className="w-4 h-4" aria-hidden="true" />
                  <span>{t.stopListen}</span>
                </>
              ) : (
                <>
                  <Volume2 className="w-4 h-4 text-clearly-royal dark:text-blue-400" aria-hidden="true" />
                  <span>{t.listen}</span>
                </>
              )}
            </button>
          </div>

          {/* Bottom action row: Going, Save, and Notify Carlos */}
          <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => onToggleGoing(event.id)}
                aria-pressed={isGoing}
                className={`px-2.5 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1 transition-all ${
                  isGoing
                    ? "bg-green-700 text-white"
                    : "bg-gray-50 dark:bg-[#1E1E1E] text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-700 hover:bg-white"
                }`}
                title={isGoing ? t.goingDone : t.going}
              >
                <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" />
                <span>{isGoing ? t.goingDone : t.going}</span>
              </button>

              <button
                type="button"
                onClick={() => onToggleSaved(event.id)}
                aria-pressed={isSaved}
                className={`p-1.5 rounded-lg text-xs font-bold flex items-center gap-1 transition-all ${
                  isSaved
                    ? "bg-clearly-royal text-white"
                    : "bg-gray-50 dark:bg-[#1E1E1E] text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-700 hover:bg-white"
                }`}
                title={isSaved ? t.savedDone : t.save}
              >
                {isSaved ? (
                  <BookmarkCheck className="w-4 h-4" aria-hidden="true" />
                ) : (
                  <Bookmark className="w-4 h-4" aria-hidden="true" />
                )}
              </button>
            </div>

            {/* Notify Tutor Carlos WhatsApp button */}
            <button
              type="button"
              onClick={handleNotifyCarlos}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
                familyNotified
                  ? "bg-green-600 text-white"
                  : "bg-blue-50 dark:bg-blue-950 text-clearly-baltic dark:text-blue-300 hover:bg-blue-100"
              }`}
            >
              {familyNotified ? (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5" aria-hidden="true" />
                  <span>Avisado a Carlos</span>
                </>
              ) : (
                <>
                  <Heart className="w-3.5 h-3.5 text-red-500" aria-hidden="true" />
                  <span>Avisar tutor</span>
                </>
              )}
            </button>
          </div>
        </div>
      </article>

      {/* Attend Guide Modal */}
      <AttendGuideModal
        event={event}
        isOpen={isAttendModalOpen}
        onClose={() => setIsAttendModalOpen(false)}
        isGoing={isGoing}
        isSaved={isSaved}
        onToggleGoing={() => onToggleGoing(event.id)}
        onToggleSaved={() => onToggleSaved(event.id)}
      />
    </>
  );
}

