"use client";

import React from "react";
import { useA11y, TtsSpeed } from "../../context/A11yContext";
import { Play, Pause, Square, Volume2, FastForward } from "lucide-react";

export function AccessibleTTSPlayer() {
  const {
    isSpeaking,
    isPaused,
    ttsSpeed,
    setTtsSpeed,
    currentSpeechText,
    pauseSpeech,
    resumeSpeech,
    stopSpeech,
    announce,
  } = useA11y();

  if (!isSpeaking && !isPaused) {
    return null;
  }

  const speeds: { value: TtsSpeed; label: string }[] = [
    { value: 0.75, label: "0.75× Lento" },
    { value: 1.0, label: "1.0× Normal" },
    { value: 1.25, label: "1.25× Rápido" },
  ];

  const handleSpeedChange = (newSpeed: TtsSpeed) => {
    setTtsSpeed(newSpeed);
    announce(`Velocidad de voz ajustada a ${newSpeed} veces`);
  };

  return (
    <div
      role="region"
      aria-label="Reproductor de lectura en voz alta"
      className="fixed bottom-4 left-4 right-4 max-w-4xl mx-auto z-40 p-4 rounded-2xl shadow-2xl border-2 transition-all duration-300 bg-white dark:bg-[#1C1C1C] border-clearly-royal dark:border-clearly-royal"
    >
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Left: Animated Status & Text snippet */}
        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center ${
              isSpeaking && !isPaused
                ? "bg-clearly-royal text-white animate-pulse"
                : "bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
            }`}
            aria-hidden="true"
          >
            <Volume2 className="w-5 h-5" />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-clearly-royal dark:text-blue-400">
                {isPaused ? "Lectura en Pausa" : "Leyendo en voz alta..."}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                (Síntesis local en navegador)
              </span>
            </div>
            {currentSpeechText && (
              <p className="text-sm font-medium truncate text-clearly-obsidian dark:text-white max-w-md">
                "{currentSpeechText}"
              </p>
            )}
          </div>
        </div>

        {/* Right: Controls & Speed */}
        <div className="flex flex-wrap items-center justify-end gap-3 w-full sm:w-auto">
          {/* Play / Pause Toggle */}
          {isPaused ? (
            <button
              type="button"
              onClick={resumeSpeech}
              aria-label="Reanudar lectura"
              className="px-4 py-2 font-bold text-sm text-white rounded-lg flex items-center gap-2 bg-clearly-royal hover:bg-clearly-royal-hover"
            >
              <Play className="w-4 h-4" aria-hidden="true" />
              <span>Reanudar</span>
            </button>
          ) : (
            <button
              type="button"
              onClick={pauseSpeech}
              aria-label="Pausar lectura"
              className="px-4 py-2 font-bold text-sm text-clearly-obsidian dark:text-white bg-clearly-birch-light dark:bg-gray-700 hover:bg-gray-200 rounded-lg flex items-center gap-2 border border-clearly-birch dark:border-gray-600"
            >
              <Pause className="w-4 h-4" aria-hidden="true" />
              <span>Pausar</span>
            </button>
          )}

          {/* Stop Button */}
          <button
            type="button"
            onClick={stopSpeech}
            aria-label="Detener lectura en voz alta"
            className="px-4 py-2 font-bold text-sm text-white bg-clearly-danger hover:bg-red-700 rounded-lg flex items-center gap-2"
          >
            <Square className="w-4 h-4" aria-hidden="true" />
            <span>Detener</span>
          </button>

          {/* Speed Selector */}
          <div
            role="group"
            aria-label="Velocidad de reproducción"
            className="flex items-center rounded-lg p-1 bg-clearly-birch-light dark:bg-gray-800 border border-clearly-birch dark:border-gray-700"
          >
            {speeds.map((s) => (
              <button
                key={s.value}
                type="button"
                onClick={() => handleSpeedChange(s.value)}
                aria-pressed={ttsSpeed === s.value}
                className={`px-2.5 py-1 text-xs font-bold rounded-md transition-all ${
                  ttsSpeed === s.value
                    ? "bg-clearly-royal text-white shadow-sm"
                    : "text-clearly-obsidian dark:text-gray-300 hover:bg-white/50"
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

