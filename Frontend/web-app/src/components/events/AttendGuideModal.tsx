"use client";

import React from "react";
import { GTAEvent, downloadEventICS, getTransitDirectionsUrl } from "../../data/communityEventsData";
import { useA11y } from "../../context/A11yContext";
import {
  X,
  Calendar,
  MapPin,
  ClipboardList,
  CalendarPlus,
  Bookmark,
  BookmarkCheck,
  ExternalLink,
  ShieldAlert,
  Clock,
  Navigation,
  CheckCircle2,
  Phone,
} from "lucide-react";

interface AttendGuideModalProps {
  event: GTAEvent;
  isOpen: boolean;
  onClose: () => void;
  isGoing: boolean;
  isSaved: boolean;
  onToggleGoing: () => void;
  onToggleSaved: () => void;
}

export function AttendGuideModal({
  event,
  isOpen,
  onClose,
  isGoing,
  isSaved,
  onToggleGoing,
  onToggleSaved,
}: AttendGuideModalProps) {
  const { language, t, announce } = useA11y();

  if (!isOpen) return null;

  const handleDownloadCalendar = () => {
    downloadEventICS(event, language);
    announce(language === "es" ? "Archivo de calendario descargado" : language === "en" ? "Calendar file downloaded" : "ਕੈਲੰਡਰ ਫ਼ਾਈਲ ਡਾਊਨਲੋਡ ਹੋ ਗਈ");
  };

  const transitUrl = getTransitDirectionsUrl(event);

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="attend-guide-title"
      className="fixed inset-0 z-50 overflow-y-auto bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6"
    >
      <div className="relative w-full max-w-2xl rounded-3xl bg-white dark:bg-[#1C1C1C] text-clearly-obsidian dark:text-white border-2 border-clearly-birch dark:border-[#383838] shadow-2xl p-6 sm:p-8 max-h-[90vh] overflow-y-auto">
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          aria-label={language === "es" ? "Cerrar guía de asistencia" : "Close attendance guide"}
          className="absolute top-5 right-5 p-2 rounded-full text-gray-400 hover:text-clearly-obsidian dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 transition-all"
        >
          <X className="w-6 h-6" aria-hidden="true" />
        </button>

        {/* Modal Header */}
        <div className="border-b border-clearly-birch/60 dark:border-gray-800 pb-4 pr-10">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-clearly-baltic/10 text-clearly-baltic dark:bg-blue-900/40 dark:text-blue-300 mb-2">
            <ClipboardList className="w-3.5 h-3.5" aria-hidden="true" />
            {t.attendTitle}
          </span>
          <h2 id="attend-guide-title" className="text-2xl sm:text-3xl font-extrabold tracking-tight leading-snug">
            {event.title[language]}
          </h2>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300 font-medium">
            {t.attendIntro}
          </p>
        </div>

        {/* 5-Step Attendance Checklist */}
        <ol className="mt-6 space-y-6">
          {/* Step 1: Register */}
          <li className="flex gap-4 p-4 rounded-2xl bg-gray-50 dark:bg-[#252525] border border-clearly-birch/40 dark:border-gray-700">
            <span
              aria-hidden="true"
              className="grid size-9 shrink-0 place-items-center rounded-full bg-clearly-baltic text-white font-black text-sm"
            >
              1
            </span>
            <div className="min-w-0 flex-1 space-y-2">
              <h3 className="text-lg font-bold flex items-center gap-2">
                <ClipboardList className="w-5 h-5 text-clearly-baltic dark:text-blue-400" aria-hidden="true" />
                {t.attendRegisterT}
              </h3>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-200">
                {event.registration_required ? t.attendRegNeeded : t.attendRegNotNeeded}
              </p>
              {event.registration_instructions && (
                <p className="text-xs text-gray-600 dark:text-gray-400 bg-white dark:bg-[#1A1A1A] p-2.5 rounded-lg border border-gray-200 dark:border-gray-700">
                  {event.registration_instructions[language]}
                </p>
              )}
              {event.registration_url && (
                <a
                  href={event.registration_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-clearly-royal dark:text-blue-300 hover:underline pt-1"
                >
                  <span>{language === "es" ? "Completar registro oficial" : "Complete official registration"}</span>
                  <ExternalLink className="w-3.5 h-3.5" aria-hidden="true" />
                </a>
              )}
            </div>
          </li>

          {/* Step 2: Get there (Transit Directions) */}
          <li className="flex gap-4 p-4 rounded-2xl bg-gray-50 dark:bg-[#252525] border border-clearly-birch/40 dark:border-gray-700">
            <span
              aria-hidden="true"
              className="grid size-9 shrink-0 place-items-center rounded-full bg-clearly-baltic text-white font-black text-sm"
            >
              2
            </span>
            <div className="min-w-0 flex-1 space-y-2">
              <h3 className="text-lg font-bold flex items-center gap-2">
                <MapPin className="w-5 h-5 text-clearly-baltic dark:text-blue-400" aria-hidden="true" />
                {t.attendGetThereT}
              </h3>
              <p className="text-sm font-medium text-gray-700 dark:text-gray-200">
                {t.attendGetThereText(event.location_name)}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {event.address}
              </p>
              <div className="pt-1 flex flex-wrap gap-2">
                <a
                  href={transitUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold bg-clearly-baltic text-white hover:bg-clearly-baltic/90 shadow-sm"
                >
                  <Navigation className="w-4 h-4" aria-hidden="true" />
                  <span>{t.directions}</span>
                  <ExternalLink className="w-3.5 h-3.5" aria-hidden="true" />
                </a>
              </div>
              <p className="text-xs text-amber-700 dark:text-amber-400 font-semibold flex items-center gap-1.5 pt-1">
                <Clock className="w-3.5 h-3.5" aria-hidden="true" />
                {t.arriveEarly}
              </p>
            </div>
          </li>

          {/* Step 3: Add to Calendar (.ICS) */}
          <li className="flex gap-4 p-4 rounded-2xl bg-gray-50 dark:bg-[#252525] border border-clearly-birch/40 dark:border-gray-700">
            <span
              aria-hidden="true"
              className="grid size-9 shrink-0 place-items-center rounded-full bg-clearly-baltic text-white font-black text-sm"
            >
              3
            </span>
            <div className="min-w-0 flex-1 space-y-2">
              <h3 className="text-lg font-bold flex items-center gap-2">
                <CalendarPlus className="w-5 h-5 text-clearly-baltic dark:text-blue-400" aria-hidden="true" />
                {t.attendCalendarT}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                {language === "es"
                  ? "Descarga el recordatorio para tu teléfono o computadora (compatible con Apple Calendar, Google Calendar y Outlook)."
                  : "Download an offline reminder for your phone or computer (works with Google, Apple & Outlook)."}
              </p>
              <button
                type="button"
                onClick={handleDownloadCalendar}
                className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold border-2 border-clearly-baltic text-clearly-baltic dark:border-blue-400 dark:text-blue-300 hover:bg-clearly-baltic hover:text-white dark:hover:bg-blue-400 dark:hover:text-black transition-all"
              >
                <Calendar className="w-4 h-4" aria-hidden="true" />
                <span>{t.addCalendar}</span>
              </button>
            </div>
          </li>

          {/* Step 4: Keep in My Events & Saved */}
          <li className="flex gap-4 p-4 rounded-2xl bg-gray-50 dark:bg-[#252525] border border-clearly-birch/40 dark:border-gray-700">
            <span
              aria-hidden="true"
              className="grid size-9 shrink-0 place-items-center rounded-full bg-clearly-baltic text-white font-black text-sm"
            >
              4
            </span>
            <div className="min-w-0 flex-1 space-y-3">
              <h3 className="text-lg font-bold flex items-center gap-2">
                <Bookmark className="w-5 h-5 text-clearly-baltic dark:text-blue-400" aria-hidden="true" />
                {t.attendSaveT}
              </h3>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={onToggleGoing}
                  aria-pressed={isGoing}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
                    isGoing
                      ? "bg-green-700 text-white"
                      : "bg-white dark:bg-[#1F1F1F] text-clearly-obsidian dark:text-white border border-gray-300 dark:border-gray-600"
                  }`}
                >
                  <CheckCircle2 className="w-4 h-4" aria-hidden="true" />
                  <span>{isGoing ? t.goingDone : t.going}</span>
                </button>

                <button
                  type="button"
                  onClick={onToggleSaved}
                  aria-pressed={isSaved}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
                    isSaved
                      ? "bg-clearly-royal text-white"
                      : "bg-white dark:bg-[#1F1F1F] text-clearly-obsidian dark:text-white border border-gray-300 dark:border-gray-600"
                  }`}
                >
                  {isSaved ? (
                    <BookmarkCheck className="w-4 h-4" aria-hidden="true" />
                  ) : (
                    <Bookmark className="w-4 h-4" aria-hidden="true" />
                  )}
                  <span>{isSaved ? t.savedDone : t.save}</span>
                </button>
              </div>
            </div>
          </li>

          {/* Step 5: Before you go */}
          <li className="flex gap-4 p-4 rounded-2xl bg-gray-50 dark:bg-[#252525] border border-clearly-birch/40 dark:border-gray-700">
            <span
              aria-hidden="true"
              className="grid size-9 shrink-0 place-items-center rounded-full bg-clearly-baltic text-white font-black text-sm"
            >
              5
            </span>
            <div className="min-w-0 flex-1 space-y-2">
              <h3 className="text-lg font-bold flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-clearly-baltic dark:text-blue-400" aria-hidden="true" />
                {t.attendBeforeT}
              </h3>
              <p className="text-sm text-gray-700 dark:text-gray-200">
                {t.attendBeforeText}
              </p>
              <div className="text-xs bg-white dark:bg-[#1A1A1A] p-3 rounded-lg border border-gray-200 dark:border-gray-700 space-y-1">
                <strong>{t.accessibilityInfo}:</strong>
                <p className="text-gray-600 dark:text-gray-300">{event.accessibility_information[language]}</p>
              </div>
            </div>
          </li>
        </ol>

        {/* Footer */}
        <div className="mt-8 pt-4 border-t border-clearly-birch/60 dark:border-gray-800 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 rounded-xl text-sm font-bold bg-clearly-baltic text-white hover:bg-clearly-baltic/90 shadow-md"
          >
            {language === "es" ? "Entendido, cerrar guía" : language === "en" ? "Got it, close guide" : "ਸਮਝ ਆ ਗਿਆ, ਬੰਦ ਕਰੋ"}
          </button>
        </div>
      </div>
    </div>
  );
}

