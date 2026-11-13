"use client";

import React from "react";
import { useA11y } from "../../context/A11yContext";
import { Users, ShieldCheck, Volume2 } from "lucide-react";

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
      className="w-full mb-6 p-4 sm:p-5 border-2 border-clearly-obsidian dark:border-white bg-white dark:bg-[#1A1A1A] shadow-[3px_3px_0_#1B1B1B] dark:shadow-[3px_3px_0_#FFFF00]"
    >
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        {/* Tutor Info Badge */}
        <div className="flex items-start space-x-3.5">
          <div
            className="p-3 border-2 border-clearly-obsidian dark:border-white bg-blue-50 dark:bg-black text-clearly-baltic dark:text-yellow-400"
            aria-hidden="true"
          >
            <Users className="w-6 h-6 stroke-[2.5]" />
          </div>

          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="label-technical text-clearly-baltic dark:text-blue-300">
                Enlace Familiar / Modo Tutor
              </span>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold border border-green-700 bg-green-50 text-green-900 dark:bg-green-950 dark:text-green-300">
                <ShieldCheck className="w-3.5 h-3.5" aria-hidden="true" />
                Vínculo Activo y Protegido
              </span>
            </div>

            <p className="mt-1 text-sm sm:text-base font-bold text-clearly-obsidian dark:text-gray-100">
              Familiar registrado: <strong>Carlos Ramos (Hijo)</strong> • Tel: ***-***-8492
            </p>

            <p className="text-xs sm:text-sm text-gray-700 dark:text-gray-300 mt-0.5">
              Supervisión de plazos críticos activada vía WhatsApp. Tu familiar tiene acceso de{" "}
              <strong>solo lectura</strong> y no puede realizar trámites sin tu consentimiento.
            </p>
          </div>
        </div>

        {/* Action Buttons: Tutor Hub & Listen to Status */}
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto justify-end">
          <a
            href="#tutor-hub"
            className="btn-tactile btn-primary flex-row items-center gap-2 px-4 py-2.5 text-xs font-bold w-auto"
            aria-label="Ir al panel de Tutor Hub en tiempo real"
          >
            <Users className="w-4 h-4" aria-hidden="true" />
            <span>Abrir Tutor Hub</span>
          </a>

          <button
            type="button"
            onClick={handleSpeakTutor}
            aria-label="Escuchar explicación del modo tutor en voz alta"
            className="btn-tactile flex-row items-center gap-2 px-4 py-2.5 text-xs font-bold w-auto border-2 border-clearly-obsidian dark:border-white"
          >
            <Volume2 className="w-4 h-4 text-clearly-baltic dark:text-yellow-400" aria-hidden="true" />
            <span>Escuchar Estado</span>
          </button>
        </div>
      </div>
    </section>
  );
}
