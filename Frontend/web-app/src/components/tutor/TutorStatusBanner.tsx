"use client";

import React from "react";
import { useA11y } from "../../context/A11yContext";
import { Users, ShieldCheck, BellRing, Volume2, Info } from "lucide-react";

export function TutorStatusBanner() {
  const { speak, isSpeaking, stopSpeech, announce } = useA11y();

  const tutorInfoText =
    "Modo Tutor Activo. Tu familiar Carlos Ramos está enlazado a tu cuenta con permisos de solo lectura. Si recibes una carta con un plazo urgente de menos de 15 días, CLEARLY le envía una copia de tus recordatorios para ayudarte a tiempo sin quitarte tu privacidad.";

  const handleSpeakTutor = () => {
    if (isSpeaking) {
      stopSpeech();
    } else {
      announce("Leyendo información del modo tutor");
      speak(tutorInfoText);
    }
  };

  return (
    <section
      role="region"
      aria-label="Estado del Enlace Familiar y Modo Tutor"
      className="w-full mb-6 p-4 sm:p-5 rounded-2xl border transition-all duration-200 bg-white dark:bg-[#1C1C1C] border-clearly-baltic/30 dark:border-clearly-royal/40 shadow-sm"
    >
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Tutor Info Badge */}
        <div className="flex items-start space-x-3.5">
          <div
            className="p-3 rounded-xl bg-blue-50 dark:bg-blue-950/60 text-clearly-baltic dark:text-blue-400 border border-blue-200 dark:border-blue-800"
            aria-hidden="true"
          >
            <Users className="w-6 h-6" />
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-sm font-bold uppercase tracking-wider text-clearly-baltic dark:text-blue-400">
                Enlace Familiar / Modo Tutor
              </span>
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300 border border-green-300 dark:border-green-800">
                <ShieldCheck className="w-3.5 h-3.5" aria-hidden="true" />
                Vínculo Activo y Protegido
              </span>
            </div>

            <p className="mt-1 text-sm sm:text-base font-medium text-clearly-obsidian dark:text-gray-200">
              Familiar registrado: <strong>Carlos Ramos (Hijo)</strong> • Tel: ***-***-8492
            </p>

            <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-0.5">
              Supervisión de plazos críticos activada vía WhatsApp. Tu familiar tiene acceso de{" "}
              <strong>solo lectura</strong> y no puede realizar trámites sin tu consentimiento.
            </p>
          </div>
        </div>

        {/* Action Button: Listen to Tutor Status */}
        <div className="flex items-center gap-2 w-full md:w-auto justify-end">
          <button
            type="button"
            onClick={handleSpeakTutor}
            aria-label="Escuchar explicación del modo tutor en voz alta"
            className="px-3.5 py-2 text-xs sm:text-sm font-bold rounded-lg flex items-center gap-2 text-clearly-baltic dark:text-blue-300 bg-blue-50 dark:bg-blue-950/60 hover:bg-blue-100 dark:hover:bg-blue-900/60 border border-blue-200 dark:border-blue-800 transition-colors"
          >
            <Volume2 className="w-4 h-4" aria-hidden="true" />
            <span>Escuchar estado</span>
          </button>
        </div>
      </div>
    </section>
  );
}
