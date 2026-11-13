"use client";

import React, { useState } from "react";
import { DocumentAnalysisResult } from "../types/document";
import { SAMPLE_DOCUMENTS } from "../data/sampleDocuments";
import { TutorStatusBanner } from "../components/tutor/TutorStatusBanner";
import { TutorHubDashboard } from "../components/tutor/TutorHubDashboard";
import { DocumentUploader } from "../components/documents/DocumentUploader";
import { ThreeLayerDocumentView } from "../components/documents/ThreeLayerDocumentView";
import { MadeClearEventsShowcase } from "../components/events/MadeClearEventsShowcase";
import {
  FileText,
  ShieldCheck,
  HeartHandshake,
  PhoneCall,
  Lock,
  Sparkles,
  BookOpen,
} from "lucide-react";

export default function HomePage() {
  // Initial demo document: Formulario N4 LTB (Hero feature active by default)
  const [activeDocument, setActiveDocument] = useState<DocumentAnalysisResult>(
    SAMPLE_DOCUMENTS.n4_eviction
  );
  const [isProcessing, setIsProcessing] = useState(false);

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
      {/* Hero Welcome Announcement */}
      <section
        role="region"
        aria-label="Presentación de CLEARLY"
        className="mb-8 p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-clearly-baltic to-[#2A3B7A] text-white shadow-xl"
      >
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-white/20 backdrop-blur-sm mb-3">
            <Sparkles className="w-4 h-4 text-yellow-300" aria-hidden="true" />
            Accesibilidad Gerontológica • WCAG 2.1 AAA
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight leading-tight">
            Tu comunidad. Más clara.
          </h1>

          <p className="mt-3 text-base sm:text-xl font-medium text-blue-100 leading-relaxed">
            Eliminamos las barreras del lenguaje burocrático y los formularios complejos. Sube una
            carta para entenderla en 3 pasos sencillos, mantén informado a tu tutor familiar y
            descubre eventos comunitarios gratuitos.
          </p>

          <div className="mt-6 flex flex-wrap items-center gap-4 text-xs sm:text-sm font-semibold text-blue-200">
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-green-400" aria-hidden="true" />
              100% Soberano y Privado (Local-First)
            </span>
            <span className="flex items-center gap-1.5">
              <BookOpen className="w-4 h-4 text-yellow-300" aria-hidden="true" />
              Tipografía Oficial Atkinson Hyperlegible
            </span>
            <span className="flex items-center gap-1.5">
              <HeartHandshake className="w-4 h-4 text-blue-300" aria-hidden="true" />
              Supervisión Pasiva con Modo Tutor
            </span>
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

      {/* Community Events Marketplace Showcase ("Made Clear" Format) */}
      <MadeClearEventsShowcase />

      {/* Accessible Footer */}
      <footer
        role="contentinfo"
        aria-label="Pie de página informativo de CLEARLY"
        className="mt-16 pt-8 pb-12 border-t-2 border-clearly-birch dark:border-gray-800 text-sm text-gray-600 dark:text-gray-400"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center space-x-2">
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-white text-base bg-clearly-baltic dark:bg-clearly-royal"
                aria-hidden="true"
              >
                C
              </div>
              <span className="text-lg font-bold text-clearly-obsidian dark:text-white">
                CLEARLY
              </span>
            </div>
            <p className="mt-2 text-xs leading-relaxed">
              Iniciativa ciudadana de inclusión digital gerontológica fundada por{" "}
              <strong>Navreet Pabla</strong> en Brampton, Ontario. Diseñada bajo la tipografía oficial{" "}
              <strong>Atkinson Hyperlegible</strong> creada por el <em>Braille Institute</em>.
            </p>
          </div>

          <div>
            <h3 className="font-bold text-xs uppercase tracking-wider text-clearly-obsidian dark:text-white mb-2">
              Privacidad y Soberanía Local-First
            </h3>
            <p className="text-xs leading-relaxed">
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
                <PhoneCall className="w-3.5 h-3.5 text-clearly-royal" aria-hidden="true" />
                <span>Servicios Sociales de Ontario: Marca <strong>211</strong> (Gratis, 24/7)</span>
              </li>
              <li className="flex items-center gap-1.5">
                <PhoneCall className="w-3.5 h-3.5 text-clearly-royal" aria-hidden="true" />
                <span>Servicios Municipales de Brampton: Marca <strong>311</strong></span>
              </li>
              <li className="flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5 text-green-600" aria-hidden="true" />
                <span>Almacenamiento Cifrado MinIO AES-256</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-4 border-t border-gray-200 dark:border-gray-800 text-center text-xs text-gray-500">
          © 2026 CLEARLY — Tu comunidad. Más clara. WCAG 2.1 AAA Compliant.
        </div>
      </footer>
    </div>
  );
}

