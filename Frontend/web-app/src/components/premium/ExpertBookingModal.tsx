"use client";

import React, { useState } from "react";
import {
  UserCheck,
  ShieldCheck,
  Star,
  Lock,
  Video,
  CreditCard,
  User,
  Users,
  CheckCircle2,
  Calendar,
  X,
  Sparkles,
  Info,
} from "lucide-react";
import { DocumentAnalysisResult } from "@/types/document";
import { ExpertProfile, PremiumBooking, LiveKitRoomDetails } from "@/types/premium";
import { matchExpertLocally } from "@/data/sampleExperts";
import LiveKitVideoPreview from "./LiveKitVideoPreview";

interface ExpertBookingModalProps {
  doc: DocumentAnalysisResult;
  isOpen: boolean;
  onClose: () => void;
  onBookingConfirmed?: (booking: PremiumBooking) => void;
}

export default function ExpertBookingModal({
  doc,
  isOpen,
  onClose,
  onBookingConfirmed,
}: ExpertBookingModalProps) {
  // 1. Automatic matching based on document type & issue
  const matchResult = matchExpertLocally(doc.document_type, doc.plain_summary);
  const [selectedExpert, setSelectedExpert] = useState<ExpertProfile>(matchResult.matched_expert);

  // Booking step states: 'details' -> 'booked' -> 'video_call'
  const [step, setStep] = useState<"details" | "booked" | "video_call">("details");
  const [payerRole, setPayerRole] = useState<"senior" | "tutor">("senior");
  const [isProcessingEscrow, setIsProcessingEscrow] = useState(false);
  const [createdBooking, setCreatedBooking] = useState<PremiumBooking | null>(null);

  if (!isOpen) return null;

  const totalCents = selectedExpert.hourly_rate_cents;
  const platformFeeCents = Math.round(totalCents * 0.15);
  const escrowCents = totalCents - platformFeeCents;

  const handleCreateEscrowBooking = async () => {
    setIsProcessingEscrow(true);

    // Simulate creation of Stripe Payment Intent and Escrow Hold
    const newBooking: PremiumBooking = {
      id: `bk-${Date.now()}`,
      senior_id: doc.user_id || "11111111-1111-1111-1111-111111111111",
      expert_id: selectedExpert.id,
      expert_name: selectedExpert.full_name,
      specialty: selectedExpert.specialty,
      hourly_rate_cents: totalCents,
      platform_fee_cents: platformFeeCents,
      expert_escrow_cents: escrowCents,
      currency: "cad",
      status: "hold_in_escrow",
      paid_by_user_id:
        payerRole === "senior"
          ? "11111111-1111-1111-1111-111111111111"
          : "22222222-2222-2222-2222-222222222222",
      paid_by_role: payerRole,
      stripe_payment_intent_id: `pi_clearly_escrow_${Date.now()}`,
      livekit_room_name: `clearly-room-${doc.id.slice(0, 8)}`,
      scheduled_at: new Date(Date.now() + 15 * 60 * 1000).toISOString(),
    };

    setTimeout(() => {
      setCreatedBooking(newBooking);
      setIsProcessingEscrow(false);
      setStep("booked");
      if (onBookingConfirmed) {
        onBookingConfirmed(newBooking);
      }
    }, 800);
  };

  const handleReleaseEscrow = (rating: number, feedback: string) => {
    if (createdBooking) {
      setCreatedBooking({
        ...createdBooking,
        status: "released",
        client_rating: rating,
        client_feedback: feedback,
        completed_at: new Date().toISOString(),
      });
    }
  };

  // LiveKit room details with accessible senior defaults
  const liveKitRoomDetails: LiveKitRoomDetails = {
    room_name: createdBooking?.livekit_room_name || `clearly-${doc.id.slice(0, 8)}`,
    token: "mock-livekit-jwt-senior-accessible-token",
    livekit_url: "wss://livekit.clearly.ca",
    participant_identity: "senior_elena",
    participant_name: "Elena Gómez",
    caption_font_scale: 1.5,
    enable_realtime_transcription: true,
  };

  if (step === "video_call" && createdBooking) {
    return (
      <LiveKitVideoPreview
        expert={selectedExpert}
        booking={createdBooking}
        roomDetails={liveKitRoomDetails}
        onClose={() => {
          setStep("booked");
          onClose();
        }}
        onReleaseEscrow={handleReleaseEscrow}
      />
    );
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="booking-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/70 backdrop-blur-sm"
    >
      <div className="relative w-full max-w-2xl bg-white dark:bg-[#1E1E1E] text-clearly-obsidian dark:text-white rounded-3xl shadow-2xl border-2 border-clearly-baltic overflow-hidden flex flex-col max-h-[92vh]">
        {/* Modal Header */}
        <header className="p-4 sm:p-5 bg-clearly-baltic text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-2xl bg-white/20">
              <Sparkles className="w-6 h-6 text-clearly-lemon" aria-hidden="true" />
            </div>
            <div>
              <h2 id="booking-modal-title" className="text-lg sm:text-xl font-black">
                CLEARLY Premium — Consulta con Profesional Verificado
              </h2>
              <p className="text-xs text-blue-100 font-medium">
                Escalamiento asistido con protección y garantía Stripe Escrow
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-xl text-white/80 hover:text-white hover:bg-white/10"
            aria-label="Cerrar ventana de reserva"
          >
            <X className="w-5 h-5" />
          </button>
        </header>

        {/* Modal Body */}
        <div className="p-4 sm:p-6 overflow-y-auto space-y-5">
          {step === "details" && (
            <>
              {/* Match Banner with Plain Language Rationale */}
              <section className="p-4 rounded-2xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800">
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-xl bg-clearly-baltic text-white mt-0.5">
                    <UserCheck className="w-5 h-5" aria-hidden="true" />
                  </div>
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-clearly-baltic dark:text-blue-300">
                      Asignación Automática Inteligente
                    </span>
                    <h3 className="text-base font-black text-clearly-obsidian dark:text-white mt-0.5">
                      {selectedExpert.specialty}
                    </h3>
                    <p className="text-xs sm:text-sm text-gray-700 dark:text-gray-300 mt-2 leading-relaxed">
                      {matchResult.plain_language_reasoning}
                    </p>
                  </div>
                </div>
              </section>

              {/* Expert Profile Card */}
              <section className="p-4 sm:p-5 rounded-2xl border-2 border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-[#252525]">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-gray-200 dark:border-gray-700">
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-lg font-black text-clearly-obsidian dark:text-white">
                        {selectedExpert.full_name}
                      </h4>
                      <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full bg-green-100 text-green-800 dark:bg-green-900/60 dark:text-green-300 border border-green-300 dark:border-green-700">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        Verificado
                      </span>
                    </div>
                    <p className="text-xs text-clearly-baltic dark:text-blue-400 font-bold mt-0.5">
                      Licencia Oficial: {selectedExpert.license_number}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="flex items-center text-amber-500 font-bold text-sm">
                      <Star className="w-4 h-4 fill-current mr-1" />
                      <span>{selectedExpert.average_rating}</span>
                    </div>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      ({selectedExpert.total_reviews} consultas)
                    </span>
                  </div>
                </div>

                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300 mt-3 leading-relaxed">
                  {selectedExpert.bio_plain_text}
                </p>

                <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
                  <span className="px-2.5 py-1 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 font-semibold text-gray-700 dark:text-gray-300">
                    Idiomas: {selectedExpert.languages_spoken.map((l) => l.toUpperCase()).join(", ")}
                  </span>
                  <span className="px-2.5 py-1 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 font-semibold text-gray-700 dark:text-gray-300">
                    Modalidad: Video LiveKit WebRTC / Presencial
                  </span>
                </div>
              </section>

              {/* Stripe Connect Escrow Financial Breakdown */}
              <section className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800">
                <div className="flex items-start gap-2.5">
                  <Lock className="w-5 h-5 text-amber-700 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                  <div className="w-full">
                    <h4 className="text-sm font-black text-amber-900 dark:text-amber-200">
                      Garantía de Protección CLEARLY Escrow (Stripe Connect)
                    </h4>
                    <p className="text-xs text-amber-800 dark:text-amber-300 mt-1 leading-relaxed">
                      El dinero se congela de manera segura en Escrow. El profesional sólo recibe el
                      pago tras finalizar la consulta y contar con su aprobación o la de su tutor.
                    </p>

                    <div className="mt-3 pt-2 border-t border-amber-200 dark:border-amber-900/60 grid grid-cols-3 gap-2 text-center text-xs">
                      <div>
                        <span className="text-gray-500 dark:text-gray-400 block">Tarifa Total</span>
                        <strong className="text-sm font-black text-clearly-obsidian dark:text-white">
                          ${(totalCents / 100).toFixed(2)} CAD
                        </strong>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400 block">Retenido Escrow (85%)</span>
                        <strong className="text-sm font-black text-green-700 dark:text-green-400">
                          ${(escrowCents / 100).toFixed(2)} CAD
                        </strong>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400 block">CLEARLY Fee (15%)</span>
                        <strong className="text-sm font-black text-blue-700 dark:text-blue-300">
                          ${(platformFeeCents / 100).toFixed(2)} CAD
                        </strong>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              {/* Payer Selection (Senior vs Tutor Delegation) */}
              <section>
                <label className="block text-xs font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-2">
                  ¿Quién autoriza y paga la consulta?
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setPayerRole("senior")}
                    className={`p-3.5 rounded-2xl border-2 text-left flex items-center gap-3 transition-all ${
                      payerRole === "senior"
                        ? "border-clearly-baltic bg-blue-50 dark:bg-blue-950/40 text-clearly-obsidian dark:text-white shadow-sm"
                        : "border-gray-200 dark:border-gray-800 hover:border-gray-300"
                    }`}
                  >
                    <div
                      className={`p-2 rounded-xl ${
                        payerRole === "senior"
                          ? "bg-clearly-baltic text-white"
                          : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
                      }`}
                    >
                      <User className="w-5 h-5" />
                    </div>
                    <div>
                      <strong className="text-sm block">Pagar yo (Elena Gómez)</strong>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        Tarjeta de crédito o débito personal
                      </span>
                    </div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setPayerRole("tutor")}
                    className={`p-3.5 rounded-2xl border-2 text-left flex items-center gap-3 transition-all ${
                      payerRole === "tutor"
                        ? "border-clearly-baltic bg-blue-50 dark:bg-blue-950/40 text-clearly-obsidian dark:text-white shadow-sm"
                        : "border-gray-200 dark:border-gray-800 hover:border-gray-300"
                    }`}
                  >
                    <div
                      className={`p-2 rounded-xl ${
                        payerRole === "tutor"
                          ? "bg-clearly-baltic text-white"
                          : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
                      }`}
                    >
                      <Users className="w-5 h-5" />
                    </div>
                    <div>
                      <strong className="text-sm block">Delegar a Carlos (Tutor)</strong>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        Notificar al tutor para autorizar el cargo
                      </span>
                    </div>
                  </button>
                </div>
              </section>
            </>
          )}

          {step === "booked" && createdBooking && (
            <div className="space-y-5 text-center py-4">
              <div className="w-16 h-16 mx-auto rounded-full bg-green-100 dark:bg-green-950/60 text-green-700 dark:text-green-300 flex items-center justify-center">
                <CheckCircle2 className="w-10 h-10" />
              </div>

              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-green-700 dark:text-green-400">
                  Garantía Escrow Confirmada
                </span>
                <h3 className="text-xl font-black text-clearly-obsidian dark:text-white mt-1">
                  Consulta Reservada con {selectedExpert.full_name}
                </h3>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300 mt-2 max-w-md mx-auto">
                  Se ha retenido ${(createdBooking.hourly_rate_cents / 100).toFixed(2)} CAD en Stripe Escrow.
                  La sala segura de video LiveKit está lista para su ingreso con subtítulos en tamaño gigante.
                </p>
              </div>

              <div className="p-4 rounded-2xl bg-gray-50 dark:bg-[#252525] border border-gray-200 dark:border-gray-700 max-w-md mx-auto text-left text-xs space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Especialista:</span>
                  <strong className="text-clearly-obsidian dark:text-white">{selectedExpert.full_name}</strong>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Número de Licencia:</span>
                  <span className="font-mono text-clearly-baltic dark:text-blue-400">{selectedExpert.license_number}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Sala LiveKit WebRTC:</span>
                  <span className="font-mono text-gray-700 dark:text-gray-300">{createdBooking.livekit_room_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500 dark:text-gray-400">Estado de Pago:</span>
                  <span className="font-bold text-amber-700 dark:text-amber-400">Retenido en Escrow</span>
                </div>
              </div>

              <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
                <button
                  type="button"
                  onClick={() => setStep("video_call")}
                  className="w-full sm:w-auto px-6 py-3.5 rounded-2xl bg-clearly-baltic hover:bg-clearly-baltic/90 text-white font-black text-sm flex items-center justify-center gap-2 shadow-xl"
                >
                  <Video className="w-5 h-5 text-clearly-lemon" />
                  <span>Entrar a la Sala de Video LiveKit</span>
                </button>

                <button
                  type="button"
                  onClick={onClose}
                  className="w-full sm:w-auto px-4 py-3 rounded-2xl text-gray-500 hover:text-black dark:text-gray-400 dark:hover:text-white font-bold text-sm"
                >
                  Volver al documento
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer (for details step) */}
        {step === "details" && (
          <footer className="p-4 sm:p-5 bg-gray-50 dark:bg-[#161616] border-t border-gray-200 dark:border-gray-800 flex items-center justify-between">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-bold text-gray-600 dark:text-gray-400 hover:text-black dark:hover:text-white"
            >
              Cancelar
            </button>

            <button
              type="button"
              disabled={isProcessingEscrow}
              onClick={handleCreateEscrowBooking}
              className="px-6 py-3 rounded-2xl bg-clearly-baltic hover:bg-clearly-baltic/90 disabled:opacity-50 text-white font-black text-sm shadow-xl flex items-center gap-2"
            >
              <CreditCard className="w-4 h-4 text-clearly-lemon" />
              <span>
                {isProcessingEscrow
                  ? "Creando Garantía Escrow..."
                  : `Autorizar Escrow ($${(totalCents / 100).toFixed(2)} CAD)`}
              </span>
            </button>
          </footer>
        )}
      </div>
    </div>
  );
}

