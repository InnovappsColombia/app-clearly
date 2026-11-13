"use client";

import React from "react";
import { useA11y } from "../../context/A11yContext";
import { X, Heart, Users, MapPin, Sparkles } from "lucide-react";

interface AboutClearlyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AboutClearlyModal({ isOpen, onClose }: AboutClearlyModalProps) {
  const { language } = useA11y();

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="about-modal-title"
      className="fixed inset-0 z-50 overflow-y-auto bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6"
    >
      <div className="relative w-full max-w-2xl rounded-3xl bg-white dark:bg-[#1C1C1C] text-clearly-obsidian dark:text-white border-2 border-clearly-birch dark:border-[#383838] shadow-2xl p-6 sm:p-8 max-h-[90vh] overflow-y-auto">
        <button
          type="button"
          onClick={onClose}
          aria-label="Cerrar ventana sobre CLEARLY"
          className="absolute top-5 right-5 p-2 rounded-full text-gray-400 hover:text-clearly-obsidian dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <X className="w-6 h-6" aria-hidden="true" />
        </button>

        <div className="border-b border-clearly-birch/60 dark:border-gray-800 pb-4 pr-10">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-purple-100 text-purple-900 dark:bg-purple-950 dark:text-purple-300 mb-2">
            <Heart className="w-3.5 h-3.5 text-purple-600 dark:text-purple-400" aria-hidden="true" />
            Nuestra Misión Cívica
          </span>
          <h2 id="about-modal-title" className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            CLEARLY — Tu comunidad. Más clara.
          </h2>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
            Derribando la barrera del lenguaje burocrático y el aislamiento digital en el Gran Toronto.
          </p>
        </div>

        <div className="mt-6 space-y-6 text-sm">
          <section className="space-y-2">
            <h3 className="text-base font-bold flex items-center gap-2 text-clearly-baltic dark:text-blue-400">
              <Users className="w-5 h-5" aria-hidden="true" />
              ¿Por qué nació CLEARLY?
            </h3>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              En Canadá, miles de adultos mayores inmigrantes y personas recién llegadas reciben cartas intimidantes de desalojo (Tribunal LTB), revisiones migratorias (IRCC) o deducciones de pensión (CRA). El lenguaje legal complejo genera angustia y parálisis burocrática. CLEARLY transforma esos textos en 3 capas claras de comprensión y acción.
            </p>
          </section>

          <section className="space-y-2">
            <h3 className="text-base font-bold flex items-center gap-2 text-clearly-baltic dark:text-blue-400">
              <MapPin className="w-5 h-5" aria-hidden="true" />
              Compromiso Local en el Gran Toronto (GTA)
            </h3>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Nacimos con foco especial en Brampton, Mississauga, Toronto, Markham, Vaughan, Richmond Hill, Oakville, Burlington y Hamilton. Ofrecemos soporte trilingüe en <strong>Español, Inglés y Punjabi (ਪੰਜਾਬੀ)</strong> para conectar a las familias con actividades cívicas reales, bibliotecas y talleres de salud gratuitos.
            </p>
          </section>

          <section className="space-y-2">
            <h3 className="text-base font-bold flex items-center gap-2 text-clearly-baltic dark:text-blue-400">
              <Sparkles className="w-5 h-5" aria-hidden="true" />
              Enlace Intergeneracional (Modo Tutor)
            </h3>
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              Permite a los hijos y cuidadores familiares (*la generación sándwich*) mantenerse informados sin invadir la autonomía del adulto mayor, previniendo fraudes y acompañándolos en cada paso cívico y de salud.
            </p>
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

