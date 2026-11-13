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
  ExternalLink,
  ShieldAlert,
  ArrowRight,
  Sparkles,
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
        ? `Tarea marcada como completada: ${targetAction.task_description}`
        : `Tarea desmarcada: ${targetAction.task_description}`
    );

    // Call API if available
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
    const textToRead = `Capa 1: Qué significa esto. ${doc.plain_summary}`;
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
    const textToRead = `Capa 2: Qué debes hacer. Tienes ${totalCount} tareas. ${tasks}`;
    announce("Leyendo la lista de tareas requeridas");
    speak(textToRead);
  };

  const handleSpeakFullDocument = () => {
    const fullText = `Documento de ${doc.issuing_entity}. ${doc.document_type}. Plazo límite: ${
      doc.critical_deadline || "Sin fecha fija"
    }. Capa 1: Qué significa esto: ${doc.plain_summary}. Capa 2: Qué debes hacer: ${actions
      .map((a, i) => `Paso ${i + 1}: ${a.task_description}.`)
      .join(" ")}. Capa 3: Preguntas recomendadas: ${doc.recommended_questions.join(" ")}`;
    announce("Leyendo documento completo en tres capas");
    speak(fullText);
  };

  // Urgency styling helper
  const getUrgencyBadge = (urgency: string) => {
    switch (urgency) {
      case "critical":
        return {
          label: "Plazo Crítico Urgente",
          badgeClass:
            "badge-urgency-critical bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300 border-red-300 dark:border-red-800",
          icon: ShieldAlert,
        };
      case "high":
        return {
          label: "Atención Prioritaria",
          badgeClass:
            "badge-urgency-high bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border-amber-300 dark:border-amber-800",
          icon: Clock,
        };
      case "medium":
        return {
          label: "Plazo Regular",
          badgeClass:
            "badge-urgency-medium bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 border-blue-300 dark:border-blue-800",
          icon: Calendar,
        };
      default:
        return {
          label: "Informativo",
          badgeClass:
            "badge-urgency-low bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300 border-green-300 dark:border-green-800",
          icon: CheckCircle,
        };
    }
  };

  const urgencyMeta = getUrgencyBadge(doc.urgency);
  const UrgencyIcon = urgencyMeta.icon;

  return (
    <article
      role="article"
      aria-label={`Análisis accesible de ${doc.document_type}`}
      className="p-6 sm:p-8 rounded-3xl border-2 transition-all duration-200 bg-white dark:bg-[#1A1A1A] border-clearly-birch dark:border-[#383838] shadow-lg mb-12"
    >
      {/* ========================================================
          DOCUMENT HEADER: Entity, Deadlines, Readability score
         ======================================================== */}
      <header className="pb-6 border-b border-clearly-birch/60 dark:border-gray-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2 mb-2">
              {/* Urgency Badge */}
              <span
                className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${urgencyMeta.badgeClass}`}
              >
                <UrgencyIcon className="w-4 h-4" aria-hidden="true" />
                {urgencyMeta.label}
              </span>

              {/* Readability Score FH >= 80 Badge */}
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300 border border-green-300 dark:border-green-800">
                <CheckCircle className="w-4 h-4" aria-hidden="true" />
                Fernández-Huerta: {doc.fernandez_huerta_score} / 100 (Muy Fácil)
              </span>

              {/* Tutor Alert notification badge */}
              {doc.tutor_alert_triggered && (
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300 border border-purple-300 dark:border-purple-800">
                  <UserCheck className="w-4 h-4" aria-hidden="true" />
                  Alerta Copiada a Tutor
                </span>
              )}
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-clearly-obsidian dark:text-white tracking-tight">
              {doc.document_type}
            </h1>

            <p className="flex items-center gap-2 mt-1 text-sm sm:text-base font-semibold text-clearly-baltic dark:text-blue-400">
              <Building className="w-4 h-4" aria-hidden="true" />
              Entidad emisora: <span>{doc.issuing_entity}</span>
            </p>
          </div>

          {/* Critical Deadline Countdown Box */}
          <div className="flex flex-col items-start md:items-end justify-center p-4 rounded-2xl bg-clearly-birch-light/70 dark:bg-[#252525] border border-clearly-birch dark:border-gray-700">
            <span className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">
              Fecha Límite Fatal
            </span>
            <span className="text-xl sm:text-2xl font-black text-clearly-danger dark:text-red-400">
              {doc.critical_deadline || "Sin fecha fija"}
            </span>
            {doc.days_remaining !== null && (
              <span className="text-xs font-bold text-clearly-obsidian dark:text-gray-300 mt-0.5">
                Quedan <strong>{doc.days_remaining} días</strong> para responder
              </span>
            )}
          </div>
        </div>

        {/* Global Read Aloud for this Document */}
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-gray-100 dark:border-gray-800">
          <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
            Auditado bajo fórmula oficial de Flesch/Fernández-Huerta para adultos mayores.
          </p>
          <button
            type="button"
            onClick={handleSpeakFullDocument}
            className="px-4 py-2 font-bold text-xs sm:text-sm text-white rounded-xl shadow-sm bg-clearly-royal hover:bg-clearly-royal-hover flex items-center gap-2 transition-transform active:scale-95"
            aria-label="Escuchar documento completo de principio a fin"
          >
            <Volume2 className="w-4 h-4" aria-hidden="true" />
            <span>Escuchar Documento Completo</span>
          </button>
        </div>
      </header>

      {/* ========================================================
          CAPA 1: ¿QUÉ SIGNIFICA ESTO? (PLAIN LANGUAGE SUMMARY)
         ======================================================== */}
      <section
        role="region"
        aria-labelledby="layer-1-title"
        className="mt-6 p-6 rounded-2xl border-2 transition-colors bg-blue-50/50 dark:bg-[#1D2433] border-clearly-baltic/40 dark:border-blue-900/60"
      >
        <div className="flex items-center justify-between pb-3 border-b border-blue-200/60 dark:border-blue-900/40">
          <div className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center font-black text-white text-sm bg-clearly-baltic dark:bg-clearly-royal"
              aria-hidden="true"
            >
              1
            </div>
            <div>
              <h2
                id="layer-1-title"
                className="text-lg sm:text-xl font-bold text-clearly-obsidian dark:text-white"
              >
                Capa 1: ¿Qué significa esta carta?
              </h2>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                Explicación en lenguaje claro y tranquilizador
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={handleSpeakSummary}
            aria-label="Escuchar la explicación de la Capa 1"
            className="p-2 rounded-lg text-clearly-baltic dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-950 flex items-center gap-1.5 text-xs font-bold"
          >
            <Volume2 className="w-4 h-4" aria-hidden="true" />
            <span className="hidden sm:inline">Escuchar</span>
          </button>
        </div>

        <div className="mt-4 text-base sm:text-lg font-medium leading-relaxed text-clearly-obsidian dark:text-gray-100">
          <p>{doc.plain_summary}</p>
        </div>
      </section>

      {/* ========================================================
          CAPA 2: ¿QUÉ DEBES HACER? (INTERACTIVE CHECKLIST)
         ======================================================== */}
      <section
        role="region"
        aria-labelledby="layer-2-title"
        className="mt-6 p-6 rounded-2xl border-2 transition-colors bg-white dark:bg-[#202020] border-clearly-birch dark:border-gray-700"
      >
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-clearly-birch/60 dark:border-gray-800 gap-3">
          <div className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center font-black text-white text-sm bg-clearly-royal"
              aria-hidden="true"
            >
              2
            </div>
            <div>
              <h2
                id="layer-2-title"
                className="text-lg sm:text-xl font-bold text-clearly-obsidian dark:text-white"
              >
                Capa 2: ¿Qué debes hacer? (Checklist de Pasos)
              </h2>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                Marca cada tarea conforme la completes. Se sincroniza con tu tutor.
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Progress indicator */}
            <div className="text-right">
              <span className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                Progreso: {completedCount} de {totalCount} ({progressPercent}%)
              </span>
              <div
                className="w-32 h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full mt-1 overflow-hidden"
                role="progressbar"
                aria-valuenow={progressPercent}
                aria-valuemin={0}
                aria-valuemax={100}
              >
                <div
                  className="h-full bg-clearly-royal transition-all duration-300"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
            </div>

            <button
              type="button"
              onClick={handleSpeakActions}
              aria-label="Escuchar la lista de pasos a seguir"
              className="p-2 rounded-lg text-clearly-royal dark:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-950 flex items-center gap-1.5 text-xs font-bold"
            >
              <Volume2 className="w-4 h-4" aria-hidden="true" />
              <span className="hidden sm:inline">Escuchar</span>
            </button>
          </div>
        </div>

        {/* Action Items List */}
        <div className="mt-4 space-y-3">
          {actions.map((action, idx) => (
            <div
              key={action.id}
              className={`p-4 rounded-xl border-2 transition-all flex items-start gap-4 ${
                action.is_completed
                  ? "bg-green-50/70 dark:bg-green-950/30 border-green-300 dark:border-green-800"
                  : "bg-white dark:bg-[#252525] border-clearly-birch dark:border-gray-700 hover:border-clearly-royal"
              }`}
            >
              {/* Accessible Checkbox */}
              <button
                type="button"
                role="checkbox"
                aria-checked={action.is_completed}
                onClick={() => handleToggleAction(action.id)}
                className={`mt-1 w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 transition-colors border-2 ${
                  action.is_completed
                    ? "bg-green-600 border-green-600 text-white"
                    : "border-gray-400 dark:border-gray-500 hover:border-clearly-royal bg-white dark:bg-gray-800"
                }`}
                aria-label={`Paso ${idx + 1}: ${action.task_description}. ${
                  action.is_completed ? "Completado" : "Pendiente"
                }`}
              >
                {action.is_completed && <CheckCircle className="w-5 h-5" aria-hidden="true" />}
              </button>

              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                    Paso {idx + 1}
                  </span>
                  {action.deadline && (
                    <span className="text-xs font-bold text-red-600 dark:text-red-400 flex items-center gap-1">
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
                  <div className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-bold bg-amber-50 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                    <FileText className="w-3.5 h-3.5" aria-hidden="true" />
                    <span>Papel o trámite necesario: {action.required_document}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {progressPercent === 100 && (
          <div
            role="status"
            className="mt-4 p-4 rounded-xl flex items-center gap-3 bg-green-100 text-green-900 dark:bg-green-950 dark:text-green-200 border border-green-300 dark:border-green-800"
          >
            <CheckCircle className="w-6 h-6 flex-shrink-0 text-green-600 dark:text-green-400" />
            <div>
              <p className="font-bold">¡Excelente trabajo! Has completado todos los pasos.</p>
              <p className="text-xs mt-0.5">
                Tu tutor familiar ha sido notificado del cumplimiento de los requisitos.
              </p>
            </div>
          </div>
        )}
      </section>

      {/* ========================================================
          CAPA 3: PUNTOS DE ACLARACIÓN & PREGUNTAS RECOMENDADAS
         ======================================================== */}
      <section
        role="region"
        aria-labelledby="layer-3-title"
        className="mt-6 p-6 rounded-2xl border-2 transition-colors bg-amber-50/40 dark:bg-[#252219] border-amber-300 dark:border-amber-800/60"
      >
        <div className="flex items-center justify-between pb-3 border-b border-amber-200 dark:border-amber-900/60">
          <div className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center font-black text-white text-sm bg-amber-600"
              aria-hidden="true"
            >
              3
            </div>
            <div>
              <h2
                id="layer-3-title"
                className="text-lg sm:text-xl font-bold text-clearly-obsidian dark:text-white"
              >
                Capa 3: Puntos de Aclaración y Preguntas Sugeridas
              </h2>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                Lo que el texto no deja claro y las preguntas que debes hacer
              </span>
            </div>
          </div>
        </div>

        {/* Ambiguities flagged */}
        {doc.ambiguities_flagged && doc.ambiguities_flagged.length > 0 && (
          <div className="mt-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-amber-900 dark:text-amber-300 mb-2 flex items-center gap-1.5">
              <AlertCircle className="w-4 h-4 text-amber-600" aria-hidden="true" />
              Aspectos no aclarados en el documento original:
            </h3>
            <ul className="space-y-2 text-sm sm:text-base text-clearly-obsidian dark:text-gray-200">
              {doc.ambiguities_flagged.map((amb, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-amber-600 font-bold">•</span>
                  <span>{amb}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Recommended Questions to Ask Entity */}
        {doc.recommended_questions && doc.recommended_questions.length > 0 && (
          <div className="mt-5 pt-4 border-t border-amber-200/60 dark:border-amber-900/40">
            <h3 className="text-sm font-bold uppercase tracking-wider text-clearly-baltic dark:text-blue-400 mb-2 flex items-center gap-1.5">
              <HelpCircle className="w-4 h-4 text-clearly-baltic dark:text-blue-400" aria-hidden="true" />
              Preguntas recomendadas para la entidad emisora:
            </h3>
            <ul className="space-y-2 text-sm sm:text-base text-clearly-obsidian dark:text-gray-200">
              {doc.recommended_questions.map((q, i) => (
                <li
                  key={i}
                  className="p-3 bg-white dark:bg-[#2C271E] rounded-xl border border-amber-200 dark:border-amber-900/60 font-semibold flex items-start gap-2"
                >
                  <span className="text-clearly-royal font-bold">¿?</span>
                  <span>"{q}"</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Ethical Guardrail & Escalation to CLEARLY Premium */}
        <div className="mt-6 p-4 rounded-xl bg-white dark:bg-[#1E1E1E] border-2 border-clearly-royal/60 dark:border-clearly-royal/40 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-clearly-royal" aria-hidden="true" />
              <span className="font-extrabold text-sm sm:text-base text-clearly-obsidian dark:text-white">
                ¿Tu situación es compleja o necesitas acompañamiento en ventanilla?
              </span>
            </div>
            <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-0.5">
              CLEARLY nunca da asesoría legal por IA. Conéctate con un trabajador social o consultor
              de inmigración humano verificado.
            </p>
          </div>

          <button
            type="button"
            onClick={() => setShowPremiumModal(true)}
            className="px-4 py-2 font-bold text-xs sm:text-sm text-white rounded-xl shadow-md bg-clearly-baltic hover:bg-clearly-baltic/90 flex items-center gap-2 flex-shrink-0"
          >
            <span>Ver Expertos CLEARLY</span>
            <ArrowRight className="w-4 h-4" aria-hidden="true" />
          </button>
        </div>
      </section>

      {/* ========================================================
          CROSS-REFERENCE: ORIGINAL SCANNED TEXT (DUAL PASS)
         ======================================================== */}
      {doc.original_extracted_text && (
        <section className="mt-6 pt-4 border-t border-clearly-birch/60 dark:border-gray-800">
          <button
            type="button"
            onClick={() => setShowOriginalText((prev) => !prev)}
            aria-expanded={showOriginalText}
            aria-controls="original-text-panel"
            className="w-full p-3 rounded-xl flex items-center justify-between font-bold text-sm text-clearly-obsidian dark:text-gray-300 bg-clearly-birch-light/60 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700"
          >
            <span className="flex items-center gap-2">
              <FileSearch className="w-4 h-4 text-clearly-royal" aria-hidden="true" />
              Comparar con el texto original en inglés / escaneado (Transparencia Total)
            </span>
            {showOriginalText ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </button>

          {showOriginalText && (
            <div
              id="original-text-panel"
              className="mt-3 p-4 rounded-xl bg-gray-50 dark:bg-[#151515] border border-gray-200 dark:border-gray-800 font-mono text-xs sm:text-sm leading-relaxed text-gray-700 dark:text-gray-300 whitespace-pre-wrap overflow-x-auto"
            >
              {doc.original_extracted_text}
            </div>
          )}
        </section>
      )}

      {/* CLEARLY Premium Verified Expert Modal (Stripe Escrow & LiveKit WebRTC) */}
      {showPremiumModal && (
        <ExpertBookingModal
          doc={doc}
          isOpen={showPremiumModal}
          onClose={() => setShowPremiumModal(false)}
          onBookingConfirmed={(booking) => {
            announce(
              `Consulta con ${booking.expert_name} reservada con éxito bajo garantía Escrow.`
            );
          }}
        />
      )}
    </article>
  );
}

