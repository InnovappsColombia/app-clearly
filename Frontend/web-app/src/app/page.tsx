"use client";

import React, { useState } from "react";
import { DocumentAnalysisResult } from "../types/document";
import { SAMPLE_DOCUMENTS } from "../data/sampleDocuments";
import { TutorStatusBanner } from "../components/tutor/TutorStatusBanner";
import { TutorHubDashboard } from "../components/tutor/TutorHubDashboard";
import { DocumentUploader } from "../components/documents/DocumentUploader";
import { ThreeLayerDocumentView } from "../components/documents/ThreeLayerDocumentView";
import { MadeClearCommunityHub } from "../components/events/MadeClearCommunityHub";
import { AccessibilityStatementModal } from "../components/governance/AccessibilityStatementModal";
import { ResponsibleAIModal } from "../components/governance/ResponsibleAIModal";
import { AboutClearlyModal } from "../components/governance/AboutClearlyModal";
import {
  FileText,
  ShieldCheck,
  HeartHandshake,
  PhoneCall,
  Lock,
  BookOpen,
  Info,
  Scale,
} from "lucide-react";

export default function HomePage() {
  // Initial demo document: Formulario N4 LTB (Hero feature active by default)
  const [activeDocument, setActiveDocument] = useState<DocumentAnalysisResult>(
    SAMPLE_DOCUMENTS.n4_eviction
  );
  const [isProcessing, setIsProcessing] = useState(false);

  // Governance modals state
  const [showA11yModal, setShowA11yModal] = useState(false);
  const [showAIModal, setShowAIModal] = useState(false);
  const [showAboutModal, setShowAboutModal] = useState(false);

  return (
    <div className="clearly-viewport-canvas">
      {/* ==========================================================================
          HERO MANIFIESTO: MATERIALIDAD CÍVICA SOBERANA (SWISS STYLE)
         ========================================================================== */}
      <section
        role="region"
        aria-label="Presentación y Manifiesto de CLEARLY"
        className="mb-8 border-2 border-clearly-obsidian dark:border-white bg-clearly-baltic dark:bg-[#121927] text-white shadow-[4px_4px_0_#1B1B1B] dark:shadow-[4px_4px_0_#FFFF00]"
      >
        <div className="p-6 sm:p-10">
          <div className="flex flex-wrap items-center justify-between gap-3 pb-4 mb-6 border-b-2 border-white/30 dark:border-white/20">
            <div className="inline-flex items-center gap-2 px-3 py-1 bg-black text-yellow-300 border border-yellow-300 font-bold text-xs uppercase tracking-wider">
              <Scale className="w-4 h-4 text-yellow-300" aria-hidden="true" />
              <span>Plataforma Cívica Soberana • WCAG 2.1 AAA & AODA</span>
            </div>
            <div className="text-xs font-mono uppercase tracking-wider text-blue-200">
              Región de Peel & Gran Toronto (GTA)
            </div>
          </div>

          <div className="max-w-4xl">
            <h1 className="text-3xl sm:text-5xl font-black tracking-tight leading-tight">
              Tu comunidad. Más clara.
            </h1>

            <p className="mt-4 text-base sm:text-xl font-medium text-blue-100 leading-relaxed max-w-3xl">
              Eliminamos el lenguaje hostil de las notificaciones oficiales, cartas de desalojo y
              formularios burocráticos. Información desglosada en 3 capas accesibles, supervisión 
              familiar protegida y eventos comunitarios gratuitos sin publicidad.
            </p>

            <div className="mt-8 pt-6 border-t border-white/20 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs sm:text-sm font-bold text-blue-100">
              <div className="flex items-center gap-2 p-2 border border-white/20 bg-white/5">
                <ShieldCheck className="w-4 h-4 text-green-400 flex-shrink-0" aria-hidden="true" />
                <span>100% Soberano y Privado (Local-First)</span>
              </div>
              <div className="flex items-center gap-2 p-2 border border-white/20 bg-white/5">
                <BookOpen className="w-4 h-4 text-yellow-300 flex-shrink-0" aria-hidden="true" />
                <span>Tipografía Atkinson Hyperlegible</span>
              </div>
              <div className="flex items-center gap-2 p-2 border border-white/20 bg-white/5">
                <HeartHandshake className="w-4 h-4 text-blue-300 flex-shrink-0" aria-hidden="true" />
                <span>Supervisión Pasiva con Modo Tutor</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mode Tutor Status Banner */}
      <TutorStatusBanner />

      {/* Upload Component */}
      <DocumentUploader
        onDocumentProcessed={(doc) => setActiveDocument(doc)}
        isProcessing={isProcessing}
        setIsProcessing={setIsProcessing}
      />

      {/* Three-Layer Document View (Core Hero Feature) */}
      {activeDocument && <ThreeLayerDocumentView document={activeDocument} />}

      {/* Tutor Hub en Tiempo Real (Sprint 3 Hero Feature) */}
      <div id="tutor-hub" className="scroll-mt-24">
        <TutorHubDashboard />
      </div>

      {/* Community Events Marketplace Hub ("Made Clear" & Civic Directory) */}
      <MadeClearCommunityHub />

      {/* ==========================================================================
          ACCESSIBLE CITIZEN FOOTER (SWISS INK AESTHETIC)
         ========================================================================== */}
      <footer
        role="contentinfo"
        aria-label="Pie de página informativo de CLEARLY"
        className="mt-16 pt-8 pb-12 border-t-2 border-clearly-obsidian dark:border-white text-sm text-clearly-obsidian dark:text-gray-300"
      >
        {/* Governance & Policy Quick Buttons */}
        <div className="mb-8 p-4 bg-gray-100 dark:bg-[#1E1E1E] border-2 border-clearly-obsidian dark:border-white shadow-[2px_2px_0_#1B1B1B] dark:shadow-[2px_2px_0_#FFFF00] flex flex-wrap items-center justify-between gap-3">
          <span className="text-xs font-bold uppercase tracking-wider text-clearly-obsidian dark:text-white flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-green-700 dark:text-green-400" aria-hidden="true" />
            <span>Transparencia y Garantías Cívicas CLEARLY</span>
          </span>
          <div className="flex flex-wrap gap-2 text-xs">
            <button
              type="button"
              onClick={() => setShowA11yModal(true)}
              className="px-3 py-1.5 font-bold border-2 border-clearly-obsidian dark:border-white bg-white dark:bg-black text-clearly-obsidian dark:text-white hover:bg-gray-200 dark:hover:bg-gray-800 flex items-center gap-1.5 transition-transform active:translate-y-0.5"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-green-700 dark:text-green-400" aria-hidden="true" />
              <span>Accesibilidad WCAG 2.1 AAA</span>
            </button>

            <button
              type="button"
              onClick={() => setShowAIModal(true)}
              className="px-3 py-1.5 font-bold border-2 border-clearly-obsidian dark:border-white bg-white dark:bg-black text-clearly-obsidian dark:text-white hover:bg-gray-200 dark:hover:bg-gray-800 flex items-center gap-1.5 transition-transform active:translate-y-0.5"
            >
              <Scale className="w-3.5 h-3.5 text-clearly-baltic dark:text-yellow-400" aria-hidden="true" />
              <span>IA Responsable y Ética</span>
            </button>

            <button
              type="button"
              onClick={() => setShowAboutModal(true)}
              className="px-3 py-1.5 font-bold border-2 border-clearly-obsidian dark:border-white bg-white dark:bg-black text-clearly-obsidian dark:text-white hover:bg-gray-200 dark:hover:bg-gray-800 flex items-center gap-1.5 transition-transform active:translate-y-0.5"
            >
              <Info className="w-3.5 h-3.5 text-clearly-baltic dark:text-yellow-400" aria-hidden="true" />
              <span>Acerca de CLEARLY (GTA)</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center space-x-2">
              <div
                className="w-8 h-8 border-2 border-clearly-obsidian dark:border-white flex items-center justify-center font-bold text-white text-base bg-clearly-baltic dark:bg-clearly-royal"
                aria-hidden="true"
              >
                C
              </div>
              <span className="text-lg font-black tracking-tight text-clearly-obsidian dark:text-white">
                CLEARLY
              </span>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-gray-700 dark:text-gray-300">
              Iniciativa ciudadana de inclusión digital gerontológica en Brampton, Mississauga y el Gran Toronto (GTA). Diseñada bajo la tipografía oficial{" "}
              <strong>Atkinson Hyperlegible</strong> creada por el <em>Braille Institute</em>.
            </p>
          </div>

          <div>
            <h3 className="font-bold text-xs uppercase tracking-wider text-clearly-obsidian dark:text-white mb-2">
              Privacidad y Soberanía Local-First
            </h3>
            <p className="text-xs leading-relaxed text-gray-700 dark:text-gray-300">
              Cumplimiento estricto de la ley canadiense de privacidad <strong>PIPEDA</strong> y{" "}
              <strong>AODA</strong>. Ningún documento médico o migratorio se comparte con
              proveedores comerciales externos. Inferencia 100% en infraestructura soberana.
            </p>
          </div>

          <div>
            <h3 className="font-bold text-xs uppercase tracking-wider text-clearly-obsidian dark:text-white mb-2">
              Líneas de Ayuda Comunitaria
            </h3>
            <ul className="text-xs space-y-1.5 font-medium">
              <li className="flex items-center gap-1.5">
                <PhoneCall className="w-3.5 h-3.5 text-clearly-royal dark:text-yellow-400" aria-hidden="true" />
                <span>Servicios Sociales de Ontario: Marca <strong>211</strong> (Gratis, 24/7)</span>
              </li>
              <li className="flex items-center gap-1.5">
                <PhoneCall className="w-3.5 h-3.5 text-clearly-royal dark:text-yellow-400" aria-hidden="true" />
                <span>Servicios Municipales de Brampton: Marca <strong>311</strong></span>
              </li>
              <li className="flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5 text-green-700 dark:text-green-400" aria-hidden="true" />
                <span>Almacenamiento Cifrado MinIO AES-256</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-4 border-t-2 border-clearly-obsidian dark:border-white text-center text-xs font-bold text-gray-600 dark:text-gray-400">
          © 2026 CLEARLY — Tu comunidad. Más clara. WCAG 2.1 AAA Compliant. Trilingüe (Español • English • ਪੰਜਾਬੀ).
        </div>
      </footer>

      {/* Modales de Transparencia y Gobernanza */}
      <AccessibilityStatementModal
        isOpen={showA11yModal}
        onClose={() => setShowA11yModal(false)}
      />
      <ResponsibleAIModal
        isOpen={showAIModal}
        onClose={() => setShowAIModal(false)}
      />
      <AboutClearlyModal
        isOpen={showAboutModal}
        onClose={() => setShowAboutModal(false)}
      />
    </div>
  );
}
