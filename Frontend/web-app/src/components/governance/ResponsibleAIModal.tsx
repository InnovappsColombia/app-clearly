"use client";

import React from "react";
import { useA11y } from "../../context/A11yContext";
import { X, Sparkles, ShieldCheck, Lock, UserCheck, AlertTriangle } from "lucide-react";

interface ResponsibleAIModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ResponsibleAIModal({ isOpen, onClose }: ResponsibleAIModalProps) {
  const { language } = useA11y();

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="responsible-ai-title"
      className="fixed inset-0 z-50 overflow-y-auto bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6"
    >
      <div className="relative w-full max-w-2xl rounded-3xl bg-white dark:bg-[#1C1C1C] text-clearly-obsidian dark:text-white border-2 border-clearly-birch dark:border-[#383838] shadow-2xl p-6 sm:p-8 max-h-[90vh] overflow-y-auto">
        <button
          type="button"
          onClick={onClose}
          aria-label="Cerrar manifiesto de IA Responsable"
          className="absolute top-5 right-5 p-2 rounded-full text-gray-400 hover:text-clearly-obsidian dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <X className="w-6 h-6" aria-hidden="true" />
        </button>

        <div className="border-b border-clearly-birch/60 dark:border-gray-800 pb-4 pr-10">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-blue-100 text-blue-900 dark:bg-blue-950 dark:text-blue-300 mb-2">
            <Sparkles className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" aria-hidden="true" />
            Transparencia & Ética Algorítmica
          </span>
          <h2 id="responsible-ai-title" className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Marco de Inteligencia Artificial Responsable
          </h2>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
            En CLEARLY protegemos a las poblaciones vulnerables de los riesgos de alucinación, sesgo algorítmico y fuga de datos privados.
          </p>
        </div>

        <div className="mt-6 space-y-6 text-sm">
          <section className="space-y-2">
            <h3 className="text-base font-bold flex items-center gap-2 text-clearly-baltic dark:text-blue-400">
              <Lock className="w-5 h-5" aria-hidden="true" />
              1. Privacidad Absoluta y Soberanía Local (Local-First)
            </h3>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Tus documentos médicos, migratorios (IRCC) o de desalojo (LTB) nunca se envían a corporaciones de IA comercial en la nube para entrenar modelos. La inferencia se ejecuta con modelos Open Source autohospedados bajo cifrado AES-256 en cumplimiento de PIPEDA y GDPR.
            </p>
          </section>

          <section className="space-y-2">
            <h3 className="text-base font-bold flex items-center gap-2 text-clearly-baltic dark:text-blue-400">
              <AlertTriangle className="w-5 h-5 text-amber-500" aria-hidden="true" />
              2. Guardrail Anti-Alucinación de Plazos Deterministas
            </h3>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Las fechas de desalojo o requerimientos legales nunca son "imaginadas" por un modelo de lenguaje. Son extraídas determinísticamente con expresiones regulares de estricto rigor y auditadas con la fórmula de legibilidad <em>Fernández-Huerta</em> ($\ge 80$).
            </p>
          </section>

          <section className="space-y-2">
            <h3 className="text-base font-bold flex items-center gap-2 text-clearly-baltic dark:text-blue-400">
              <UserCheck className="w-5 h-5 text-green-600" aria-hidden="true" />
              3. Deslinde Legal y Escalamiento Humano (Human-in-the-Loop)
            </h3>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              CLEARLY es un facilitador de comprensión lingüística y de inclusión comunitaria, no un abogado ni asesor legal. Ante casos críticos con riesgo legal inminente, el sistema bloquea la auto-asesoría y ofrece enlace directo con especialistas humanos acreditados (RCIC, Trabajadores Sociales MSW) bajo custodia Escrow.
            </p>
          </section>
        </div>

        <div className="mt-8 pt-4 border-t border-clearly-birch/60 dark:border-gray-800 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 rounded-xl text-sm font-bold bg-clearly-baltic text-white hover:bg-clearly-baltic/90 shadow-md"
          >
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
}

