"use client";

import React from "react";
import { useA11y } from "../../context/A11yContext";
import { X, ShieldCheck, Eye, Keyboard, Type, CheckCircle2 } from "lucide-react";

interface AccessibilityStatementModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AccessibilityStatementModal({
  isOpen,
  onClose,
}: AccessibilityStatementModalProps) {
  const { language } = useA11y();

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="a11y-modal-title"
      className="fixed inset-0 z-50 overflow-y-auto bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6"
    >
      <div className="relative w-full max-w-2xl rounded-3xl bg-white dark:bg-[#1C1C1C] text-clearly-obsidian dark:text-white border-2 border-clearly-birch dark:border-[#383838] shadow-2xl p-6 sm:p-8 max-h-[90vh] overflow-y-auto">
        <button
          type="button"
          onClick={onClose}
          aria-label="Cerrar declaración de accesibilidad"
          className="absolute top-5 right-5 p-2 rounded-full text-gray-400 hover:text-clearly-obsidian dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <X className="w-6 h-6" aria-hidden="true" />
        </button>

        <div className="border-b border-clearly-birch/60 dark:border-gray-800 pb-4 pr-10">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-green-100 text-green-900 dark:bg-green-950 dark:text-green-300 mb-2">
            <ShieldCheck className="w-3.5 h-3.5" aria-hidden="true" />
            Certificación WCAG 2.1 AAA
          </span>
          <h2 id="a11y-modal-title" className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Declaración de Accesibilidad Universal
          </h2>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
            CLEARLY está concebido desde su arquitectura base para garantizar autonomía plena a personas con baja visión, adultos mayores y dificultades cognitivas o de lenguaje.
          </p>
        </div>

        <div className="mt-6 space-y-6 text-sm">
          <section className="space-y-2">
            <h3 className="text-base font-bold flex items-center gap-2 text-clearly-baltic dark:text-blue-400">
              <Type className="w-5 h-5" aria-hidden="true" />
              1. Tipografía Atkinson Hyperlegible
            </h3>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Diseñada por el <em>Braille Institute</em> de Estados Unidos, diferencia de forma inequívoca letras homólogas (como la 'I' mayúscula, la 'l' minúscula y el número '1') reduciendo el error de lectura hasta en un 80% en pacientes con degeneración macular senil o cataratas.
            </p>
          </section>

          <section className="space-y-2">
            <h3 className="text-base font-bold flex items-center gap-2 text-clearly-baltic dark:text-blue-400">
              <Eye className="w-5 h-5" aria-hidden="true" />
              2. Contraste Superior WCAG 2.1 Nivel AAA
            </h3>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Superamos el ratio estándar de 4.5:1 exigido por WCAG AA, manteniendo un contraste cromático estricto $\ge 7:1$ en texto estándar y disponiendo de un modo ultra contraste amarillo sobre negro (#FFFF00 / #000000) con ratio superior a 19:1.
            </p>
          </section>

          <section className="space-y-2">
            <h3 className="text-base font-bold flex items-center gap-2 text-clearly-baltic dark:text-blue-400">
              <Keyboard className="w-5 h-5" aria-hidden="true" />
              3. Atajos de Teclado y Compatibilidad con Lectores de Pantalla
            </h3>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs pt-1">
              <li className="p-2.5 rounded-lg bg-gray-50 dark:bg-[#252525] border border-gray-200 dark:border-gray-700">
                <kbd className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-800 rounded font-mono font-bold">Alt + +</kbd>: Aumentar tamaño de letra
              </li>
              <li className="p-2.5 rounded-lg bg-gray-50 dark:bg-[#252525] border border-gray-200 dark:border-gray-700">
                <kbd className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-800 rounded font-mono font-bold">Alt + -</kbd>: Reducir tamaño de letra
              </li>
              <li className="p-2.5 rounded-lg bg-gray-50 dark:bg-[#252525] border border-gray-200 dark:border-gray-700">
                <kbd className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-800 rounded font-mono font-bold">Alt + C</kbd>: Cambiar contraste / tema
              </li>
              <li className="p-2.5 rounded-lg bg-gray-50 dark:bg-[#252525] border border-gray-200 dark:border-gray-700">
                <kbd className="px-1.5 py-0.5 bg-gray-200 dark:bg-gray-800 rounded font-mono font-bold">Alt + V</kbd>: Activar / pausar voz en off
              </li>
            </ul>
          </section>
        </div>

        <div className="mt-8 pt-4 border-t border-clearly-birch/60 dark:border-gray-800 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 rounded-xl text-sm font-bold bg-clearly-baltic text-white hover:bg-clearly-baltic/90 shadow-md"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}

