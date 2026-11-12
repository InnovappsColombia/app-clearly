"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  ReactNode,
} from "react";

export type ThemeMode = "light" | "dark" | "high-contrast";
export type TextScale = 100 | 125 | 150 | 175 | 200;
export type TtsSpeed = 0.75 | 1.0 | 1.25;

interface A11yContextType {
  // Visual A11y
  textScale: TextScale;
  setTextScale: (scale: TextScale) => void;
  increaseTextScale: () => void;
  decreaseTextScale: () => void;
  resetTextScale: () => void;

  theme: ThemeMode;
  setTheme: (theme: ThemeMode) => void;
  toggleTheme: () => void;

  lineSpacing: "normal" | "relaxed" | "loose";
  setLineSpacing: (spacing: "normal" | "relaxed" | "loose") => void;

  // TTS Engine (In-Browser Web Speech API + SpeechSynthesis)
  isSpeaking: boolean;
  isPaused: boolean;
  ttsSpeed: TtsSpeed;
  setTtsSpeed: (speed: TtsSpeed) => void;
  currentSpeechText: string | null;
  speak: (text: string, onEnd?: () => void) => void;
  pauseSpeech: () => void;
  resumeSpeech: () => void;
  stopSpeech: () => void;

  // Live Screen Reader Announcement (WCAG AAA aria-live)
  announceMessage: string;
  announce: (message: string, priority?: "polite" | "assertive") => void;
}

const A11yContext = createContext<A11yContextType | undefined>(undefined);

const SCALE_LEVELS: TextScale[] = [100, 125, 150, 175, 200];

export function A11yProvider({ children }: { children: ReactNode }) {
  const [textScale, setTextScaleState] = useState<TextScale>(125); // Default 125% for seniors
  const [theme, setThemeState] = useState<ThemeMode>("light");
  const [lineSpacing, setLineSpacing] = useState<"normal" | "relaxed" | "loose">("relaxed");

  // TTS State
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [ttsSpeed, setTtsSpeed] = useState<TtsSpeed>(1.0);
  const [currentSpeechText, setCurrentSpeechText] = useState<string | null>(null);

  // Screen reader announcer state
  const [announceMessage, setAnnounceMessage] = useState("");
  const [announcePriority, setAnnouncePriority] = useState<"polite" | "assertive">("polite");

  // Load saved preferences
  useEffect(() => {
    if (typeof window !== "undefined") {
      try {
        const savedScale = localStorage.getItem("clearly_text_scale");
        if (savedScale && SCALE_LEVELS.includes(Number(savedScale) as TextScale)) {
          setTextScaleState(Number(savedScale) as TextScale);
        }
        const savedTheme = localStorage.getItem("clearly_theme") as ThemeMode;
        if (savedTheme && ["light", "dark", "high-contrast"].includes(savedTheme)) {
          setThemeState(savedTheme);
        }
        const savedSpeed = localStorage.getItem("clearly_tts_speed");
        if (savedSpeed) {
          setTtsSpeed(Number(savedSpeed) as TtsSpeed);
        }
      } catch {
        // Ignore localStorage errors
      }
    }
  }, []);

  // Apply theme & font scale to <html> element
  useEffect(() => {
    if (typeof document !== "undefined") {
      const root = document.documentElement;

      // Theme classes
      root.classList.remove("theme-light", "theme-dark", "theme-high-contrast", "dark");
      root.classList.add(`theme-${theme}`);
      if (theme === "dark" || theme === "high-contrast") {
        root.classList.add("dark");
      }

      // Font size root scaling
      root.style.fontSize = `${textScale}%`;

      // Persist
      try {
        localStorage.setItem("clearly_text_scale", String(textScale));
        localStorage.setItem("clearly_theme", theme);
      } catch {
        // Ignore
      }
    }
  }, [textScale, theme]);

  const setTextScale = useCallback((scale: TextScale) => {
    setTextScaleState(scale);
    announce(`Tamaño de letra cambiado al ${scale} por ciento`);
  }, []);

  const increaseTextScale = useCallback(() => {
    setTextScaleState((prev) => {
      const currentIndex = SCALE_LEVELS.indexOf(prev);
      if (currentIndex < SCALE_LEVELS.length - 1) {
        const next = SCALE_LEVELS[currentIndex + 1];
        announce(`Texto aumentado al ${next} por ciento`);
        return next;
      }
      announce("Tamaño de texto máximo alcanzado: 200 por ciento");
      return prev;
    });
  }, []);

  const decreaseTextScale = useCallback(() => {
    setTextScaleState((prev) => {
      const currentIndex = SCALE_LEVELS.indexOf(prev);
      if (currentIndex > 0) {
        const next = SCALE_LEVELS[currentIndex - 1];
        announce(`Texto reducido al ${next} por ciento`);
        return next;
      }
      announce("Tamaño de texto mínimo alcanzado: 100 por ciento");
      return prev;
    });
  }, []);

  const resetTextScale = useCallback(() => {
    setTextScaleState(125);
    announce("Tamaño de letra restablecido al valor predeterminado del 125 por ciento");
  }, []);

  const setTheme = useCallback((newTheme: ThemeMode) => {
    setThemeState(newTheme);
    const label =
      newTheme === "high-contrast"
        ? "Modo de Alto Contraste Amarillo y Negro activado"
        : newTheme === "dark"
        ? "Modo Oscuro activado"
        : "Modo Claro Predeterminado activado";
    announce(label);
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeState((prev) => {
      if (prev === "light") return "dark";
      if (prev === "dark") return "high-contrast";
      return "light";
    });
  }, []);

  // Screen reader announcer
  const announce = useCallback((message: string, priority: "polite" | "assertive" = "polite") => {
    setAnnouncePriority(priority);
    setAnnounceMessage(message);
    // Clear after delay so repeated messages trigger re-announcement
    setTimeout(() => {
      setAnnounceMessage("");
    }, 4000);
  }, []);

  // TTS Engine (Web Speech API)
  const speak = useCallback(
    (text: string, onEnd?: () => void) => {
      if (typeof window === "undefined" || !("speechSynthesis" in window)) {
        announce("La síntesis de voz no está disponible en este navegador", "assertive");
        return;
      }

      window.speechSynthesis.cancel();

      // Clean plain text for reading
      const cleanText = text
        .replace(/[#*_`]/g, "")
        .replace(/\n\s*\n/g, ". ")
        .replace(/\s+/g, " ")
        .trim();

      if (!cleanText) return;

      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.rate = ttsSpeed;
      utterance.pitch = 1.0;
      utterance.lang = "es-ES";

      // Select natural sounding voice if available
      const voices = window.speechSynthesis.getVoices();
      const spanishVoice = voices.find(
        (v) => v.lang.startsWith("es") || v.name.toLowerCase().includes("spanish")
      );
      if (spanishVoice) {
        utterance.voice = spanishVoice;
      }

      utterance.onstart = () => {
        setIsSpeaking(true);
        setIsPaused(false);
        setCurrentSpeechText(cleanText);
      };

      utterance.onend = () => {
        setIsSpeaking(false);
        setIsPaused(false);
        setCurrentSpeechText(null);
        if (onEnd) onEnd();
      };

      utterance.onerror = (e) => {
        if (e.error !== "canceled" && e.error !== "interrupted") {
          setIsSpeaking(false);
          setIsPaused(false);
          setCurrentSpeechText(null);
        }
      };

      window.speechSynthesis.speak(utterance);
    },
    [ttsSpeed, announce]
  );

  const pauseSpeech = useCallback(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.pause();
      setIsPaused(true);
      announce("Lectura en voz alta en pausa");
    }
  }, [announce]);

  const resumeSpeech = useCallback(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.resume();
      setIsPaused(false);
      announce("Reanudando lectura");
    }
  }, [announce]);

  const stopSpeech = useCallback(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      setIsPaused(false);
      setCurrentSpeechText(null);
      announce("Lectura detenida");
    }
  }, [announce]);

  // Cleanup TTS on unmount
  useEffect(() => {
    return () => {
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  return (
    <A11yContext.Provider
      value={{
        textScale,
        setTextScale,
        increaseTextScale,
        decreaseTextScale,
        resetTextScale,
        theme,
        setTheme,
        toggleTheme,
        lineSpacing,
        setLineSpacing,
        isSpeaking,
        isPaused,
        ttsSpeed,
        setTtsSpeed,
        currentSpeechText,
        speak,
        pauseSpeech,
        resumeSpeech,
        stopSpeech,
        announceMessage,
        announce,
      }}
    >
      {/* Invisible ARIA Live Regions for Screen Readers */}
      <div
        id="a11y-announcer-polite"
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {announcePriority === "polite" ? announceMessage : ""}
      </div>
      <div
        id="a11y-announcer-assertive"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
        className="sr-only"
      >
        {announcePriority === "assertive" ? announceMessage : ""}
      </div>
      {children}
    </A11yContext.Provider>
  );
}

export function useA11y() {
  const context = useContext(A11yContext);
  if (!context) {
    throw new Error("useA11y debe utilizarse dentro de un A11yProvider");
  }
  return context;
}

