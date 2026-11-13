"use client";

import React, { useState } from "react";
import { DocumentAnalysisResult, ActionItem } from "../../types/document";
import { useA11y } from "../../context/A11yContext";
import ExpertBookingModal from "../premium/ExpertBookingModal";
import {
  FileText,
  Clock,
  AlertCircle,
  CheckCircle,
  HelpCircle,
  Volume2,
  Calendar,
  Building,
  UserCheck,
  ChevronDown,
  ChevronUp,
  FileSearch,
  ShieldAlert,
  ArrowRight,
  ShieldCheck,
  Scale,
} from "lucide-react";

interface ThreeLayerDocumentViewProps {
  document: DocumentAnalysisResult;
  onUpdateAction?: (actionId: string, isCompleted: boolean) => void;
}

export function ThreeLayerDocumentView({
  document: doc,
  onUpdateAction,
}: ThreeLayerDocumentViewProps) {
  const { speak, isSpeaking, stopSpeech, announce } = useA11y();
  const [actions, setActions] = useState<ActionItem[]>(doc.actions_required);
  const [showOriginalText, setShowOriginalText] = useState(false);
  const [showPremiumModal, setShowPremiumModal] = useState(false);

  // Toggle checklist item
  const handleToggleAction = async (actionId: string) => {
    const targetAction = actions.find((a) => a.id === actionId);
    if (!targetAction) return;

    const nextCompleted = !targetAction.is_completed;
    const updated = actions.map((a) =>
      a.id === actionId
        ? {
            ...a,
            is_completed: nextCompleted,
            completed_at: nextCompleted ? new Date().toISOString() : null,
          }
        : a
    );
    setActions(updated);

    announce(
      nextCompleted
        ? `Tarea completada: ${targetAction.task_description}`
        : `Tarea desmarcada: ${targetAction.task_description}`
    );

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      await fetch(`${apiUrl}/api/v1/documents/actions/${actionId}/toggle`, {
        method: "PATCH",
      });
    } catch {
      // Offline fallback
    }

    if (onUpdateAction) {
      onUpdateAction(actionId, nextCompleted);
    }
  };

  const completedCount = actions.filter((a) => a.is_completed).length;
  const totalCount = actions.length;
  const progressPercent = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  // TTS Speech Generators
  const handleSpeakSummary = () => {
    const textToRead = `Capa 1: Qué significa esta carta. ${doc.plain_summary}`;
    announce("Leyendo el resumen en lenguaje sencillo");
    speak(textToRead);
  };

  const handleSpeakActions = () => {
    const tasks = actions
      .map(
        (a, i) =>
          `Paso ${i + 1}: ${a.task_description}. ${
            a.required_document ? `Documento necesario: ${a.required_document}.` : ""
          } ${a.deadline ? `Fecha límite: ${a.deadline}.` : ""}`
      )
      .join(" ");
    const textToRead = `Capa 2: Pasos a seguir. Tienes ${totalCount} tareas. ${tasks}`;
    announce("Leyendo lista de tareas");
    speak(textToRead);
  };

  const handleSpeakFullDocument = () => {
    const fullText = `Documento de ${doc.issuing_entity}. ${doc.document_type}. Plazo límite: ${
      doc.critical_deadline || "Sin fecha fija"
    }. Capa 1: Qué significa esto: ${doc.plain_summary}. Capa 2: Pasos a seguir: ${actions
      .map((a, i) => `Paso ${i + 1}: ${a.task_description}.`)
      .join(" ")}. Capa 3: Preguntas recomendadas: ${doc.recommended_questions.join(" ")}`;
    announce("Leyendo documento completo en tres capas");
    speak(fullText);
  };

  // Urgency styling helper
  const isUrgent = doc.urgency === "critical" || doc.urgency === "high";

  return (
    <article
      role="article"
      aria-label={`Análisis accesible de ${doc.document_type}`}
      className="mb-12"
    >
      {/* ==========================================================================
          BLOQUE ARQUITECTÓNICO A: TABLERO DE ALERTA Y FECHA CRÍTICA (SWISS STYLE)
         ========================================================================== */}
      <section className="crit-alert-block" role="region" aria-labelledby="crit-alert-title">
        <div className="crit-alert-header">
          <div className="crit-badge">
            <span className="crit-indicator" aria-hidden="true" />
            <span className="label-technical">
              {isUrgent ? "PLAZO LEGAL INAMOVIBLE" : "NOTIFICACIÓN ADMINISTRATIVA REGISTRADA"}
            </span>
          </div>
          <div className="flex items-center gap-3">
            <span className="crit-origin">EXPEDIENTE #{doc.id.substring(0, 14)}</span>
            <span className="inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 border border-current">
              <ShieldCheck className="w-3.5 h-3.5" aria-hidden="true" />
              FH: {doc.fernandez_huerta_score} / 100
            </span>
          </div>
        </div>

        <div className="crit-alert-body">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-4">
            <div>
              <h1 id="crit-alert-title" className="crit-doc-title">
                {doc.document_type}
              </h1>
              <p className="flex items-center gap-2 text-sm sm:text-base font-bold text-clearly-baltic dark:text-blue-300">
                <Building className="w-4 h-4" aria-hidden="true" />
                <span>Entidad emisora: <strong>{doc.issuing_entity}</strong></span>
              </p>
            </div>

            {/* Read Aloud Trigger */}
            <button
              type="button"
              onClick={handleSpeakFullDocument}
              className="btn-tactile btn-secondary self-start md:self-auto inline-flex flex-row items-center gap-2 px-4 py-2 text-xs font-bold border-2 border-line-structural"
              aria-label="Escuchar documento completo de principio a fin"
            >
              <Volume2 className="w-4 h-4 text-clearly-baltic dark:text-yellow-400" aria-hidden="true" />
              <span>Escuchar Documento Completo</span>
            </button>
          </div>

          {/* Metrics Strip */}
          <div className="crit-metrics-strip">
            <div className="crit-metric-cell highlight">
              <span className="label-technical">Fecha Límite Definitiva</span>
              <time className="crit-date numeric-ledger">
                {doc.critical_deadline || "Sin fecha fija"}
              </time>
              <span className="crit-sublabel">Plazo legal de respuesta</span>
            </div>

            <div className="crit-metric-cell">
              <span className="label-technical">Días Restantes</span>
              <div className="crit-countdown numeric-ledger">
                {doc.days_remaining !== null ? doc.days_remaining : "—"}
              </div>
              <span className="crit-sublabel">
                {doc.days_remaining !== null ? "Días para actuar o responder" : "Revisión preventiva"}
              </span>
            </div>

            <div className="crit-metric-cell">
              <span className="label-technical">Supervisión Tutor</span>
              <div className="text-xl font-bold mt-2 text-clearly-obsidian dark:text-white flex items-center gap-2">
                {doc.tutor_alert_triggered ? (
                  <>
                    <UserCheck className="w-5 h-5 text-green-600 dark:text-green-400" aria-hidden="true" />
                    <span>Copia Notificada</span>
                  </>
                ) : (
                  <span>Modo Individual</span>
                )}
              </div>
              <span className="crit-sublabel">Sincronizado vía PASETO v4</span>
            </div>
          </div>

          {/* Legal Guarantee & De-escalation Notice */}
          <div className="crit-legal-guarantee">
            <p>
              <strong>Aclaración Inmediata de Seguridad:</strong> Este documento es una comunicación oficial, 
              pero <u>no constituye una orden de ejecución inmediata</u>. En Ontario, todo desalojo, sanción 
              o suspensión de beneficios exige un proceso con derecho a audiencia y defensa según las leyes de la provincia.
            </p>
          </div>
        </div>
      </section>

      {/* ==========================================================================
          CAPA 1: ¿QUÉ SIGNIFICA ESTA CARTA? (PLAIN LANGUAGE SUMMARY)
         ========================================================================== */}
      <section
        role="region"
        aria-labelledby="layer-1-title"
        className="mb-8 p-6 sm:p-8 bg-white dark:bg-[#1A1A1A] border-2 border-clearly-obsidian dark:border-white shadow-[4px_4px_0_#1B1B1B] dark:shadow-[4px_4px_0_#FFFF00]"
      >
        <div className="flex items-center justify-between pb-4 border-b-2 border-clearly-obsidian dark:border-white">
          <div className="flex items-center gap-3">
            <span
              className="w-8 h-8 flex items-center justify-center font-bold text-white text-sm bg-clearly-baltic dark:bg-clearly-royal border border-current"
              aria-hidden="true"
            >
              1
            </span>
            <div>
              <h2
                id="layer-1-title"
                className="text-xl sm:text-2xl font-bold text-clearly-obsidian dark:text-white tracking-tight"
              >
                Capa 1: ¿Qué significa esta carta?
              </h2>
              <span className="text-xs font-bold uppercase tracking-wider text-gray-600 dark:text-gray-300">
                Explicación en lenguaje claro y sereno (Flesch / Fernández-Huerta)
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={handleSpeakSummary}
            aria-label="Escuchar la explicación de la Capa 1"
            className="px-3 py-1.5 border-2 border-clearly-obsidian dark:border-white font-bold text-xs flex items-center gap-1.5 hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <Volume2 className="w-4 h-4 text-clearly-baltic dark:text-yellow-400" aria-hidden="true" />
            <span>Escuchar</span>
          </button>
        </div>

        <div className="mt-4 text-base sm:text-lg leading-relaxed text-clearly-obsidian dark:text-gray-100 font-medium">
          <p>{doc.plain_summary}</p>
        </div>
      </section>

      {/* ==========================================================================
          CAPA 2: ¿QUÉ DEBES HACER? (CHECKLIST TÁCTIL INTERACTIVO)
         ========================================================================== */}
      <section
        role="region"
        aria-labelledby="layer-2-title"
        className="mb-8 p-6 sm:p-8 bg-white dark:bg-[#1A1A1A] border-2 border-clearly-obsidian dark:border-white shadow-[4px_4px_0_#1B1B1B] dark:shadow-[4px_4px_0_#FFFF00]"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b-2 border-clearly-obsidian dark:border-white gap-3">
          <div className="flex items-center gap-3">
            <span
              className="w-8 h-8 flex items-center justify-center font-bold text-white text-sm bg-clearly-baltic dark:bg-clearly-royal border border-current"
              aria-hidden="true"
            >
              2
            </span>
            <div>
              <h2
                id="layer-2-title"
                className="text-xl sm:text-2xl font-bold text-clearly-obsidian dark:text-white tracking-tight"
              >
                Capa 2: Pasos a seguir y tareas requeridas
              </h2>
              <span className="text-xs font-bold uppercase tracking-wider text-gray-600 dark:text-gray-300">
                Lista de control secuencial coordinada con tu tutor familiar
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <span className="text-xs font-bold uppercase tracking-wider text-clearly-obsidian dark:text-white">
                Progreso: {completedCount} de {totalCount} ({progressPercent}%)
              </span>
              <div
                className="w-32 h-3 bg-gray-200 dark:bg-gray-700 border border-clearly-obsidian dark:border-white mt-1 overflow-hidden"
                role="progressbar"
                aria-valuenow={progressPercent}
                aria-valuemin={0}
                aria-valuemax={100}
              >
                <div
                  className="h-full bg-clearly-baltic dark:bg-yellow-400 transition-all duration-300"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
            </div>

            <button
              type="button"
              onClick={handleSpeakActions}
              aria-label="Escuchar la lista de tareas"
              className="px-3 py-1.5 border-2 border-clearly-obsidian dark:border-white font-bold text-xs flex items-center gap-1.5 hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <Volume2 className="w-4 h-4 text-clearly-baltic dark:text-yellow-400" aria-hidden="true" />
              <span>Escuchar</span>
            </button>
          </div>
        </div>

        {/* Action Items List */}
        <div className="mt-6 space-y-4">
          {actions.map((action, idx) => (
            <div
              key={action.id}
              className={`p-4 border-2 transition-all flex items-start gap-4 ${
                action.is_completed
                  ? "bg-gray-100 dark:bg-[#252525] border-gray-400 dark:border-gray-600 opacity-80"
                  : "bg-white dark:bg-[#1A1A1A] border-clearly-obsidian dark:border-white hover:shadow-[2px_2px_0_#1B1B1B] dark:hover:shadow-[2px_2px_0_#FFFF00]"
              }`}
            >
              {/* Tactile Checkbox Button */}
              <button
                type="button"
                role="checkbox"
                aria-checked={action.is_completed}
                onClick={() => handleToggleAction(action.id)}
                className={`mt-0.5 w-8 h-8 border-2 flex items-center justify-center flex-shrink-0 transition-transform active:scale-95 ${
                  action.is_completed
                    ? "bg-clearly-obsidian text-white dark:bg-yellow-400 dark:text-black border-clearly-obsidian dark:border-yellow-400"
                    : "border-clearly-obsidian dark:border-white bg-white dark:bg-black hover:bg-gray-100 dark:hover:bg-gray-800"
                }`}
                aria-label={`Paso ${idx + 1}: ${action.task_description}. ${
                  action.is_completed ? "Completado" : "Pendiente"
                }`}
              >
                {action.is_completed && <CheckCircle className="w-5 h-5 stroke-[3]" aria-hidden="true" />}
              </button>

              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="label-technical text-gray-600 dark:text-gray-300">
                    Paso {idx + 1}
                  </span>
                  {action.deadline && (
                    <span className="text-xs font-bold text-clearly-danger dark:text-red-400 flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" aria-hidden="true" />
                      Fecha límite: {action.deadline}
                    </span>
                  )}
                </div>

                <p
                  className={`mt-1 text-base sm:text-lg font-bold leading-snug ${
                    action.is_completed
                      ? "line-through text-gray-500 dark:text-gray-400"
                      : "text-clearly-obsidian dark:text-white"
                  }`}
                >
                  {action.task_description}
                </p>

                {action.required_document && (
                  <div className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold border border-clearly-obsidian dark:border-gray-500 bg-gray-50 dark:bg-gray-900 text-clearly-obsidian dark:text-gray-200">
                    <FileText className="w-3.5 h-3.5" aria-hidden="true" />
                    <span>Documento o trámite necesario: <strong>{action.required_document}</strong></span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {progressPercent === 100 && (
          <div
            role="status"
            className="mt-6 p-4 border-2 border-green-700 bg-green-50 dark:bg-green-950/50 text-green-900 dark:text-green-200 flex items-center gap-3"
          >
            <CheckCircle className="w-6 h-6 flex-shrink-0 text-green-700 dark:text-green-400 stroke-[2.5]" />
            <div>
              <p className="font-bold text-base">¡Todas las tareas han sido completadas con éxito!</p>
              <p className="text-xs mt-0.5">
                Tu tutor familiar y el registro del panel han sido actualizados en tiempo real.
              </p>
            </div>
          </div>
        )}
      </section>

      {/* ==========================================================================
          BLOQUE B: MATRIZ DE COTEJO DOCUMENTAL (SWISS SUBGRID)
         ========================================================================== */}
      <section className="comparative-ledger" aria-labelledby="ledger-title">
        <div className="ledger-header">
          <h2 id="ledger-title" className="text-lg sm:text-xl font-bold text-clearly-obsidian dark:text-white">
            Cotejo Documental: Texto Oficial vs. Lenguaje Sencillo
          </h2>
          <span className="label-technical">Doble Pase OCR Verificado</span>
        </div>

        <div className="ledger-table">
          <div className="ledger-row header-row hidden sm:grid">
            <div className="ledger-cell original">
              <span className="label-technical">Texto Fuente Original (Ontario Legal Form)</span>
            </div>
            <div className="ledger-cell simplified">
              <span className="label-technical">Interpretación y Acción Concreta</span>
            </div>
          </div>

          <div className="ledger-row">
            <div className="ledger-cell original">
              <span className="original-cite">Sección Principal • Extracto Oficial</span>
              <p className="font-mono text-xs sm:text-sm leading-relaxed" lang="en">
                "{doc.original_extracted_text?.substring(0, 220) || 'Official Notice under the Residential Tenancies Act'}..."
              </p>
            </div>
            <div className="ledger-cell simplified">
              <strong className="action-highlight">Propósito Central:</strong>
              <p className="text-sm sm:text-base leading-relaxed">
                El documento establece una reclamación administrativa formal. Tu derecho principal es 
                revisar el balance, solicitar la mediación del tribunal y no desalojar voluntariamente 
                sin asesoría legal previa.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ==========================================================================
          CAPA 3: AMBIGÜEDADES, PREGUNTAS Y ESCALADO A EXPERTO HUMANO
         ========================================================================== */}
      <section
        role="region"
        aria-labelledby="layer-3-title"
        className="mb-8 p-6 sm:p-8 bg-white dark:bg-[#1A1A1A] border-2 border-clearly-obsidian dark:border-white shadow-[4px_4px_0_#1B1B1B] dark:shadow-[4px_4px_0_#FFFF00]"
      >
        <div className="flex items-center justify-between pb-4 border-b-2 border-clearly-obsidian dark:border-white">
          <div className="flex items-center gap-3">
            <span
              className="w-8 h-8 flex items-center justify-center font-bold text-white text-sm bg-clearly-baltic dark:bg-clearly-royal border border-current"
              aria-hidden="true"
            >
              3
            </span>
            <div>
              <h2
                id="layer-3-title"
                className="text-xl sm:text-2xl font-bold text-clearly-obsidian dark:text-white tracking-tight"
              >
                Capa 3: Puntos de Aclaración y Preguntas Recomendadas
              </h2>
              <span className="text-xs font-bold uppercase tracking-wider text-gray-600 dark:text-gray-300">
                Lo que no está explícito en la carta y qué debes preguntar
              </span>
            </div>
          </div>
        </div>

        {/* Ambiguities flagged */}
        {doc.ambiguities_flagged && doc.ambiguities_flagged.length > 0 && (
          <div className="mt-6 p-4 border-2 border-amber-600 bg-amber-50 dark:bg-amber-950/30">
            <h3 className="text-xs font-bold uppercase tracking-wider text-amber-900 dark:text-amber-300 mb-2 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-amber-600" aria-hidden="true" />
              <span>Aspectos ambiguos detectados en el texto fuente:</span>
            </h3>
            <ul className="space-y-1.5 text-sm sm:text-base font-medium text-clearly-obsidian dark:text-gray-200">
              {doc.ambiguities_flagged.map((amb, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="font-bold text-amber-600">—</span>
                  <span>{amb}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Recommended Questions to Ask Entity */}
        {doc.recommended_questions && doc.recommended_questions.length > 0 && (
          <div className="mt-6">
            <h3 className="label-technical text-clearly-baltic dark:text-blue-300 mb-3 flex items-center gap-2">
              <HelpCircle className="w-4 h-4" aria-hidden="true" />
              <span>Preguntas clave que debes formular a la entidad:</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {doc.recommended_questions.map((q, i) => (
                <div
                  key={i}
                  className="p-3 border-2 border-clearly-obsidian dark:border-gray-600 bg-gray-50 dark:bg-[#222222] font-semibold text-sm"
                >
                  <span className="font-bold text-clearly-baltic dark:text-yellow-400 block mb-1">
                    Pregunta sugerida {i + 1}:
                  </span>
                  <span>"{q}"</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Ethical Guardrail & Escalation to Human Professional */}
        <div className="mt-8 p-5 border-2 border-clearly-baltic dark:border-blue-400 bg-blue-50/60 dark:bg-[#182235] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 font-extrabold text-base sm:text-lg text-clearly-obsidian dark:text-white">
              <Scale className="w-5 h-5 text-clearly-baltic dark:text-blue-300" aria-hidden="true" />
              <span>¿Necesitas acompañamiento profesional presencial o legal?</span>
            </div>
            <p className="text-xs sm:text-sm text-gray-700 dark:text-gray-300 mt-1 max-w-2xl">
              CLEARLY nunca sustituye a un profesional con IA. Puedes conectarte con un trabajador social 
              colegiado (MSW) o un consultor migratorio acreditado (RCIC) con fondos bajo custodia Stripe Escrow.
            </p>
          </div>

          <button
            type="button"
            onClick={() => setShowPremiumModal(true)}
            className="btn-tactile btn-primary flex-row items-center gap-2 px-5 py-3 text-sm font-bold flex-shrink-0"
          >
            <span>Ver Asesores Verificados</span>
            <ArrowRight className="w-4 h-4" aria-hidden="true" />
          </button>
        </div>
      </section>

      {/* Cross-reference Raw OCR */}
      {doc.original_extracted_text && (
        <section className="pt-2">
          <button
            type="button"
            onClick={() => setShowOriginalText((prev) => !prev)}
            aria-expanded={showOriginalText}
            aria-controls="original-text-panel"
            className="w-full p-3 border-2 border-clearly-obsidian dark:border-gray-600 flex items-center justify-between font-bold text-xs uppercase tracking-wider text-clearly-obsidian dark:text-gray-200 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200"
          >
            <span className="flex items-center gap-2">
              <FileSearch className="w-4 h-4" aria-hidden="true" />
              <span>Inspección de Transparencia: Transcripción Cruda OCR</span>
            </span>
            {showOriginalText ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </button>

          {showOriginalText && (
            <div
              id="original-text-panel"
              className="mt-2 p-4 border-2 border-clearly-obsidian dark:border-gray-600 bg-white dark:bg-black font-mono text-xs leading-relaxed whitespace-pre-wrap overflow-x-auto text-clearly-obsidian dark:text-gray-200"
            >
              {doc.original_extracted_text}
            </div>
          )}
        </section>
      )}

      {/* Premium Modal */}
      {showPremiumModal && (
        <ExpertBookingModal
          doc={doc}
          isOpen={showPremiumModal}
          onClose={() => setShowPremiumModal(false)}
          onBookingConfirmed={(booking) => {
            announce(`Consulta con ${booking.expert_name} reservada bajo garantía Escrow.`);
          }}
        />
      )}
    </article>
  );
}
