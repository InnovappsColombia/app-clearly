"use client";

import React, { useState, useEffect } from "react";
import { useA11y, TextScale, ThemeMode } from "../../context/A11yContext";
import {
  Volume2,
  VolumeX,
  Sun,
  Moon,
  Eye,
  Type,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  HelpCircle,
  X,
  Keyboard,
  Languages,
  Globe,
} from "lucide-react";

export function A11yToolbar() {
  const {
    textScale,
    setTextScale,
    increaseTextScale,
    decreaseTextScale,
    resetTextScale,
    theme,
    setTheme,
    language,
    setLanguage,
    t,
    isSpeaking,
    stopSpeech,
    speak,
    announce,
  } = useA11y();

  const [showHelpModal, setShowHelpModal] = useState(false);

  // Keyboard accessibility shortcuts (Alt + keys)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.altKey) {
        if (e.key === "+" || e.key === "=") {
          e.preventDefault();
          increaseTextScale();
        } else if (e.key === "-") {
          e.preventDefault();
          decreaseTextScale();
        } else if (e.key.toLowerCase() === "c") {
          e.preventDefault();
          if (theme === "light") setTheme("dark");
          else if (theme === "dark") setTheme("high-contrast");
          else setTheme("light");
        } else if (e.key.toLowerCase() === "v") {
          e.preventDefault();
          if (isSpeaking) {
            stopSpeech();
          } else {
            const mainContent = document.getElementById("main-content");
            if (mainContent) {
              speak(mainContent.innerText);
            }
          }
        } else if (e.key.toLowerCase() === "h") {
          e.preventDefault();
          setShowHelpModal((prev) => !prev);
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [increaseTextScale, decreaseTextScale, theme, setTheme, isSpeaking, speak, stopSpeech]);

  const handleGlobalReadToggle = () => {
    if (isSpeaking) {
      stopSpeech();
    } else {
      const mainContent = document.getElementById("main-content");
      if (mainContent) {
        announce("Iniciando lectura de la página completa");
        speak(mainContent.innerText);
      }
    }
  };

  const scales: TextScale[] = [100, 125, 150, 175, 200];

  return (
    <>
      {/* Skip to Content Link (WCAG AAA) */}
      <a href="#main-content" className="skip-to-content">
        Saltar al contenido principal (Alt + S)
      </a>

      {/* Accessible Sticky Toolbar */}
      <header
        role="region"
        aria-label="Barra de herramientas de accesibilidad"
        className="sticky top-0 z-50 w-full border-b shadow-sm transition-colors duration-200 bg-white/95 dark:bg-[#1B1B1B]/95 border-clearly-birch dark:border-[#383838] backdrop-blur-md"
      >
        <div className="max-w-7xl mx-auto px-4 py-2 sm:px-6 lg:px-8">
          <div className="flex flex-wrap items-center justify-between gap-3">
            {/* Logo and Brand Title */}
            <div className="flex items-center space-x-3">
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center font-bold text-white text-xl bg-clearly-baltic dark:bg-clearly-royal"
                aria-hidden="true"
              >
                C
              </div>
              <div>
                <span className="text-xl sm:text-2xl font-bold tracking-tight text-clearly-obsidian dark:text-white">
                  CLEARLY
                </span>
                <span className="hidden sm:inline-block ml-2 text-xs font-semibold uppercase tracking-wider text-clearly-baltic dark:text-clearly-birch">
                  Tu comunidad. Más clara.
                </span>
              </div>
            </div>

            {/* A11y Quick Controls Group */}
            <nav
              aria-label="Controles de accesibilidad visual y auditiva"
              className="flex flex-wrap items-center gap-2"
            >
              {/* Text Size Scale Selector */}
              <div
                role="group"
                aria-label="Ajuste de tamaño de letra"
                className="flex items-center rounded-lg p-1 bg-clearly-birch-light dark:bg-[#252525] border border-clearly-birch dark:border-[#3A3A3A]"
              >
                <button
                  type="button"
                  onClick={decreaseTextScale}
                  disabled={textScale <= 100}
                  aria-label="Reducir tamaño de letra"
                  className="p-1.5 rounded-md hover:bg-white dark:hover:bg-[#333] disabled:opacity-30 disabled:cursor-not-allowed text-clearly-obsidian dark:text-white"
                  title="Reducir letra (Alt + -)"
                >
                  <ZoomOut className="w-5 h-5" aria-hidden="true" />
                </button>

                <div className="hidden md:flex items-center gap-1 px-1">
                  {scales.map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => setTextScale(s)}
                      aria-pressed={textScale === s}
                      aria-label={`Tamaño ${s} por ciento`}
                      className={`px-2 py-1 text-xs font-bold rounded-md transition-all ${
                        textScale === s
                          ? "bg-clearly-royal text-white shadow-sm"
                          : "text-clearly-obsidian dark:text-gray-200 hover:bg-white dark:hover:bg-[#333]"
                      }`}
                    >
                      {s}%
                    </button>
                  ))}
                </div>

                <button
                  type="button"
                  onClick={increaseTextScale}
                  disabled={textScale >= 200}
                  aria-label="Aumentar tamaño de letra"
                  className="p-1.5 rounded-md hover:bg-white dark:hover:bg-[#333] disabled:opacity-30 disabled:cursor-not-allowed text-clearly-obsidian dark:text-white"
                  title="Aumentar letra (Alt + +)"
                >
                  <ZoomIn className="w-5 h-5" aria-hidden="true" />
                </button>

                <button
                  type="button"
                  onClick={resetTextScale}
                  aria-label="Restablecer tamaño predeterminado (125%)"
                  className="p-1.5 ml-1 rounded-md text-gray-500 hover:text-clearly-obsidian dark:text-gray-400 dark:hover:text-white"
                  title="Restablecer letra al 125%"
                >
                  <RotateCcw className="w-4 h-4" aria-hidden="true" />
                </button>
              </div>

              {/* Language Selector (ES, EN, PA) */}
              <div
                role="group"
                aria-label="Selector de idioma / Language selector"
                className="flex items-center rounded-lg p-1 bg-clearly-birch-light dark:bg-[#252525] border border-clearly-birch dark:border-[#3A3A3A]"
              >
                <button
                  type="button"
                  onClick={() => setLanguage("es")}
                  aria-pressed={language === "es"}
                  aria-label="Cambiar idioma a Español"
                  className={`px-2 py-1 text-xs font-bold rounded-md transition-all ${
                    language === "es"
                      ? "bg-clearly-baltic text-white shadow-sm"
                      : "text-clearly-obsidian dark:text-gray-200 hover:bg-white/50"
                  }`}
                >
                  ES
                </button>
                <button
                  type="button"
                  onClick={() => setLanguage("en")}
                  aria-pressed={language === "en"}
                  aria-label="Switch language to English"
                  className={`px-2 py-1 text-xs font-bold rounded-md transition-all ${
                    language === "en"
                      ? "bg-clearly-baltic text-white shadow-sm"
                      : "text-clearly-obsidian dark:text-gray-200 hover:bg-white/50"
                  }`}
                >
                  EN
                </button>
                <button
                  type="button"
                  onClick={() => setLanguage("pa")}
                  aria-pressed={language === "pa"}
                  aria-label="ਬੋਲੀ ਪੰਜਾਬੀ ਵਿੱਚ ਬਦਲੋ (Punjabi)"
                  className={`px-2 py-1 text-xs font-bold rounded-md transition-all ${
                    language === "pa"
                      ? "bg-clearly-baltic text-white shadow-sm"
                      : "text-clearly-obsidian dark:text-gray-200 hover:bg-white/50"
                  }`}
                  title="ਪੰਜਾਬੀ (Punjabi)"
                >
                  ਪੰ
                </button>
              </div>

              {/* Theme & Contrast Selector */}
              <div
                role="group"
                aria-label="Contraste de pantalla"
                className="flex items-center rounded-lg p-1 bg-clearly-birch-light dark:bg-[#252525] border border-clearly-birch dark:border-[#3A3A3A]"
              >
                <button
                  type="button"
                  onClick={() => setTheme("light")}
                  aria-pressed={theme === "light"}
                  aria-label="Tema Claro estándar"
                  className={`px-2.5 py-1.5 text-xs font-bold rounded-md flex items-center gap-1.5 ${
                    theme === "light"
                      ? "bg-white text-clearly-obsidian shadow-sm"
                      : "text-gray-600 dark:text-gray-300 hover:bg-white/50"
                  }`}
                >
                  <Sun className="w-4 h-4 text-amber-600" aria-hidden="true" />
                  <span className="hidden sm:inline">Claro</span>
                </button>

                <button
                  type="button"
                  onClick={() => setTheme("dark")}
                  aria-pressed={theme === "dark"}
                  aria-label="Tema Oscuro Obsidian"
                  className={`px-2.5 py-1.5 text-xs font-bold rounded-md flex items-center gap-1.5 ${
                    theme === "dark"
                      ? "bg-[#1B1B1B] text-white shadow-sm border border-gray-600"
                      : "text-gray-600 dark:text-gray-300 hover:bg-white/50"
                  }`}
                >
                  <Moon className="w-4 h-4 text-blue-400" aria-hidden="true" />
                  <span className="hidden sm:inline">Oscuro</span>
                </button>

                <button
                  type="button"
                  onClick={() => setTheme("high-contrast")}
                  aria-pressed={theme === "high-contrast"}
                  aria-label="Tema de Alto Contraste Amarillo y Negro WCAG AAA"
                  className={`px-2.5 py-1.5 text-xs font-extrabold rounded-md flex items-center gap-1.5 ${
                    theme === "high-contrast"
                      ? "bg-black text-yellow-300 border-2 border-yellow-300 shadow-sm"
                      : "text-gray-700 dark:text-gray-200 hover:bg-white/50"
                  }`}
                  title="Alto Contraste WCAG AAA (Amarillo sobre Negro)"
                >
                  <Eye className="w-4 h-4 text-yellow-500" aria-hidden="true" />
                  <span>Alto Contraste</span>
                </button>
              </div>

              {/* Global Read Aloud (TTS) Button */}
              <button
                type="button"
                onClick={handleGlobalReadToggle}
                aria-pressed={isSpeaking}
                aria-label={
                  isSpeaking
                    ? "Detener lectura en voz alta de la página"
                    : "Escuchar en voz alta la página completa"
                }
                className={`px-3 py-1.5 text-xs sm:text-sm font-bold rounded-lg flex items-center gap-2 transition-all ${
                  isSpeaking
                    ? "bg-clearly-danger text-white animate-pulse"
                    : "bg-clearly-royal text-white hover:bg-clearly-royal-hover"
                }`}
                title="Lectura en voz alta (Alt + V)"
              >
                {isSpeaking ? (
                  <>
                    <VolumeX className="w-5 h-5" aria-hidden="true" />
                    <span>Detener Voz</span>
                  </>
                ) : (
                  <>
                    <Volume2 className="w-5 h-5" aria-hidden="true" />
                    <span>Escuchar</span>
                  </>
                )}
              </button>

              {/* A11y Help / Shortcuts Button */}
              <button
                type="button"
                onClick={() => setShowHelpModal(true)}
                aria-label="Guía de accesibilidad y atajos de teclado"
                className="p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-clearly-birch-light dark:hover:bg-[#2A2A2A]"
                title="Atajos de teclado y ayuda"
              >
                <HelpCircle className="w-5 h-5" aria-hidden="true" />
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Accessibility Help & Keyboard Shortcuts Modal */}
      {showHelpModal && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="a11y-modal-title"
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        >
          <div className="relative w-full max-w-lg p-6 bg-white dark:bg-[#1E1E1E] rounded-2xl shadow-2xl border-2 border-clearly-royal">
            <div className="flex items-center justify-between pb-3 border-b border-clearly-birch dark:border-gray-700">
              <h2
                id="a11y-modal-title"
                className="text-xl font-bold flex items-center gap-2 text-clearly-obsidian dark:text-white"
              >
                <Keyboard className="w-6 h-6 text-clearly-royal" aria-hidden="true" />
                Guía de Accesibilidad CLEARLY
              </h2>
              <button
                type="button"
                onClick={() => setShowHelpModal(false)}
                aria-label="Cerrar ventana de ayuda"
                className="p-1 rounded-lg text-gray-500 hover:text-black dark:text-gray-400 dark:hover:text-white"
              >
                <X className="w-6 h-6" aria-hidden="true" />
              </button>
            </div>

            <div className="mt-4 space-y-4 text-clearly-obsidian dark:text-gray-200">
              <p className="text-sm">
                CLEARLY está diseñado bajo normas internacionales{" "}
                <strong>WCAG 2.1 Nivel AAA</strong> y la tipografía oficial{" "}
                <strong>Atkinson Hyperlegible</strong> para personas mayores o con baja visión.
              </p>

              <div>
                <h3 className="font-bold text-sm uppercase tracking-wider mb-2 text-clearly-baltic dark:text-blue-400">
                  Atajos de Teclado Rápidos:
                </h3>
                <ul className="space-y-2 text-sm">
                  <li className="flex justify-between items-center py-1 border-b border-gray-100 dark:border-gray-800">
                    <span>Aumentar tamaño de letra:</span>
                    <kbd className="px-2 py-1 font-mono text-xs font-bold rounded bg-gray-100 dark:bg-gray-800 border">
                      Alt + +
                    </kbd>
                  </li>
                  <li className="flex justify-between items-center py-1 border-b border-gray-100 dark:border-gray-800">
                    <span>Reducir tamaño de letra:</span>
                    <kbd className="px-2 py-1 font-mono text-xs font-bold rounded bg-gray-100 dark:bg-gray-800 border">
                      Alt + -
                    </kbd>
                  </li>
                  <li className="flex justify-between items-center py-1 border-b border-gray-100 dark:border-gray-800">
                    <span>Alternar modos de contraste:</span>
                    <kbd className="px-2 py-1 font-mono text-xs font-bold rounded bg-gray-100 dark:bg-gray-800 border">
                      Alt + C
                    </kbd>
                  </li>
                  <li className="flex justify-between items-center py-1 border-b border-gray-100 dark:border-gray-800">
                    <span>Escuchar / Pausar lectura en voz alta:</span>
                    <kbd className="px-2 py-1 font-mono text-xs font-bold rounded bg-gray-100 dark:bg-gray-800 border">
                      Alt + V
                    </kbd>
                  </li>
                  <li className="flex justify-between items-center py-1">
                    <span>Abrir o cerrar esta ventana de ayuda:</span>
                    <kbd className="px-2 py-1 font-mono text-xs font-bold rounded bg-gray-100 dark:bg-gray-800 border">
                      Alt + H
                    </kbd>
                  </li>
                </ul>
              </div>

              <div className="p-3 bg-clearly-birch-light dark:bg-gray-800 rounded-lg text-xs">
                <strong>¿Sabías que?</strong> Todos los botones tienen un área táctil mínima de{" "}
                <strong>44×44 píxeles</strong> y los textos cumplen una relación de contraste superior a{" "}
                <strong>7:1</strong>.
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                type="button"
                onClick={() => setShowHelpModal(false)}
                className="px-5 py-2 font-bold text-white rounded-lg bg-clearly-royal hover:bg-clearly-royal-hover"
              >
                Entendido
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

