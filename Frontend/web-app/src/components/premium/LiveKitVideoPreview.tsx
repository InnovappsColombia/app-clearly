"use client";

import React, { useState, useEffect } from "react";
import {
  Mic,
  MicOff,
  Video,
  VideoOff,
  PhoneOff,
  Users,
  ShieldCheck,
  Subtitles,
  Volume2,
  CheckCircle2,
  Star,
  Lock,
} from "lucide-react";
import { ExpertProfile, LiveKitRoomDetails, PremiumBooking } from "@/types/premium";

interface LiveKitVideoPreviewProps {
  expert: ExpertProfile;
  booking: PremiumBooking;
  roomDetails: LiveKitRoomDetails;
  onClose: () => void;
  onReleaseEscrow: (rating: number, feedback: string) => void;
}

export default function LiveKitVideoPreview({
  expert,
  booking,
  roomDetails,
  onClose,
  onReleaseEscrow,
}: LiveKitVideoPreviewProps) {
  // A/V controls
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  const [tutorJoined, setTutorJoined] = useState(false);

  // Subtitle accessibility options
  const [subtitlesEnabled, setSubtitlesEnabled] = useState(true);
  const [captionScale, setCaptionScale] = useState(roomDetails.caption_font_scale || 1.5);

  // Simulated live captions
  const [activeCaption, setActiveCaption] = useState<string>(
    `${expert.full_name}: "Buenas tardes Elena. Ya he cargado y revisado los documentos de su caso. Vamos a resolver esto juntos paso a paso."`
  );

  // Completion & Escrow Release Flow
  const [isCallEnded, setIsCallEnded] = useState(false);
  const [rating, setRating] = useState(5);
  const [feedback, setFeedback] = useState("Excelente asesoría, muy clara y humana.");
  const [isEscrowReleased, setIsEscrowReleased] = useState(false);

  // Periodic captions rotation to simulate natural dialogue
  useEffect(() => {
    if (isCallEnded) return;

    const speechScript = [
      `${expert.full_name}: "Buenas tardes Elena. Ya he cargado y revisado los documentos de su caso. Vamos a resolver esto juntos paso a paso."`,
      `Elena Gómez (Tú): "Muchas gracias. Estaba un poco angustiada con la fecha límite de la carta."`,
      `${expert.full_name}: "La entiendo perfectamente. Verifiqué que tenemos plazo hasta el próximo mes. Solo necesitamos adjuntar dos comprobantes de residencia."`,
      tutorJoined
        ? `Carlos Gómez (Tutor): "Hola David, estoy aquí con mi mamá apoyándola. Yo tengo esos dos recibos en PDF."`
        : `${expert.full_name}: "La plataforma CLEARLY protege su sesión con encriptación médica y legal. ¿Desea que sumemos a su hijo Carlos a la sala?"`,
      `${expert.full_name}: "Excelente, redactaré la respuesta formal con mi número de licencia oficial y se la compartiré en la plataforma."`,
    ];

    let index = 0;
    const interval = setInterval(() => {
      index = (index + 1) % speechScript.length;
      setActiveCaption(speechScript[index]);
    }, 6000);

    return () => clearInterval(interval);
  }, [expert.full_name, isCallEnded, tutorJoined]);

  const handleEndCall = () => {
    setIsCallEnded(true);
  };

  const handleConfirmEscrowRelease = () => {
    setIsEscrowReleased(true);
    onReleaseEscrow(rating, feedback);
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Consulta por Video en Vivo con Profesional Verificado"
      className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/80 backdrop-blur-md"
    >
      <div className="relative w-full max-w-4xl bg-clearly-obsidian text-white rounded-3xl shadow-2xl border-2 border-clearly-baltic overflow-hidden flex flex-col max-h-[92vh]">
        {/* Header */}
        <header className="p-4 bg-[#141414] border-b border-gray-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="w-3 h-3 rounded-full bg-green-500 animate-pulse" aria-hidden="true" />
            <div>
              <h2 className="text-base sm:text-lg font-black text-white flex items-center gap-2">
                Consulta Segura LiveKit WebRTC
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-900/60 text-blue-200 border border-blue-700">
                  Cifrado E2E
                </span>
              </h2>
              <p className="text-xs text-gray-300">
                Con: <strong className="text-white">{expert.full_name}</strong> ({expert.specialty})
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs bg-yellow-900/50 text-clearly-lemon px-2.5 py-1 rounded-full font-bold flex items-center gap-1 border border-yellow-700/60">
              <Lock className="w-3.5 h-3.5" aria-hidden="true" />
              Escrow Activo: ${(booking.hourly_rate_cents / 100).toFixed(2)} CAD
            </span>
          </div>
        </header>

        {/* Video Stage */}
        <div className="relative flex-1 bg-black p-4 min-h-[380px] flex flex-col justify-between">
          {/* Remote Video Feed (Expert) */}
          <div className="absolute inset-0 bg-gradient-to-b from-[#1A233A] via-[#101422] to-black flex items-center justify-center">
            <div className="text-center p-6">
              <div className="w-28 h-28 sm:w-36 sm:h-36 mx-auto rounded-full bg-clearly-baltic/40 border-4 border-clearly-baltic flex items-center justify-center shadow-xl mb-4">
                <span className="text-3xl sm:text-4xl font-black text-white">
                  {expert.full_name.charAt(0)}
                </span>
              </div>
              <h3 className="text-xl sm:text-2xl font-black text-white">{expert.full_name}</h3>
              <p className="text-sm font-semibold text-blue-300 mt-1">
                Licencia Verificada: {expert.license_number}
              </p>
              <span className="inline-block mt-2 px-3 py-1 rounded-full bg-green-950 text-green-300 border border-green-700 text-xs font-bold">
                Conexión Estable de Audio y Video HD
              </span>
            </div>
          </div>

          {/* Self-view Picture-in-Picture (Senior / User) */}
          <div className="relative z-10 self-end w-32 sm:w-44 h-24 sm:h-32 rounded-2xl bg-gray-900 border-2 border-white/40 shadow-2xl overflow-hidden flex items-center justify-center">
            {isVideoOff ? (
              <div className="text-center text-xs text-gray-400 p-2">
                <VideoOff className="w-6 h-6 mx-auto mb-1 text-gray-500" />
                Cámara Apagada
              </div>
            ) : (
              <div className="w-full h-full bg-gradient-to-tr from-gray-800 to-gray-700 flex flex-col items-center justify-center text-center p-1">
                <span className="text-xs font-bold text-gray-200">Elena Gómez</span>
                <span className="text-[10px] text-green-400 font-semibold">(Tú - Vista local)</span>
              </div>
            )}
          </div>

          {/* Tutor In-Call Participant Badge */}
          {tutorJoined && (
            <div className="relative z-10 self-start bg-blue-950/90 border border-blue-500 px-3 py-1.5 rounded-xl shadow-lg flex items-center gap-2">
              <Users className="w-4 h-4 text-blue-300" aria-hidden="true" />
              <span className="text-xs font-bold text-white">Carlos Gómez (Tutor Conectado)</span>
            </div>
          )}

          {/* REAL-TIME GERONTOLOGICAL SUBTITLES OVERLAY */}
          {subtitlesEnabled && !isCallEnded && (
            <section
              aria-live="polite"
              aria-label="Subtítulos accesibles en tiempo real"
              className="relative z-20 mt-auto mx-auto max-w-3xl w-full"
            >
              <div
                style={{ fontSize: `${captionScale * 1.1}rem`, lineHeight: 1.4 }}
                className="p-4 rounded-2xl bg-[#0F0F0F]/95 text-clearly-lemon border-2 border-clearly-lemon/80 font-bold shadow-2xl tracking-wide text-center"
              >
                {activeCaption}
              </div>
            </section>
          )}
        </div>

        {/* Accessibility & Video Call Controls */}
        {!isCallEnded ? (
          <footer className="p-4 bg-[#141414] border-t border-gray-800 flex flex-wrap items-center justify-between gap-3">
            {/* Audio/Video Media Toggles */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setIsMuted((prev) => !prev)}
                className={`p-3.5 rounded-2xl font-bold flex items-center gap-2 text-sm shadow-md transition-colors ${
                  isMuted
                    ? "bg-red-600 hover:bg-red-700 text-white"
                    : "bg-gray-800 hover:bg-gray-700 text-white border border-gray-600"
                }`}
                aria-label={isMuted ? "Reactivar micrófono" : "Silenciar micrófono"}
              >
                {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                <span className="hidden sm:inline">{isMuted ? "Mutado" : "Micrófono"}</span>
              </button>

              <button
                type="button"
                onClick={() => setIsVideoOff((prev) => !prev)}
                className={`p-3.5 rounded-2xl font-bold flex items-center gap-2 text-sm shadow-md transition-colors ${
                  isVideoOff
                    ? "bg-red-600 hover:bg-red-700 text-white"
                    : "bg-gray-800 hover:bg-gray-700 text-white border border-gray-600"
                }`}
                aria-label={isVideoOff ? "Encender cámara" : "Apagar cámara"}
              >
                {isVideoOff ? <VideoOff className="w-5 h-5" /> : <Video className="w-5 h-5" />}
                <span className="hidden sm:inline">{isVideoOff ? "Sin Video" : "Cámara"}</span>
              </button>
            </div>

            {/* Gerontological Accessibility Controls */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setSubtitlesEnabled((prev) => !prev)}
                className={`px-3 py-2 rounded-xl text-xs sm:text-sm font-bold flex items-center gap-1.5 ${
                  subtitlesEnabled
                    ? "bg-clearly-lemon text-clearly-obsidian"
                    : "bg-gray-800 text-gray-300"
                }`}
                aria-pressed={subtitlesEnabled}
              >
                <Subtitles className="w-4 h-4" />
                <span>Subtítulos {subtitlesEnabled ? "Activos" : "Pausados"}</span>
              </button>

              {subtitlesEnabled && (
                <button
                  type="button"
                  onClick={() =>
                    setCaptionScale((prev) => (prev >= 2.0 ? 1.25 : prev + 0.25))
                  }
                  className="px-2.5 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-xs font-bold text-white border border-gray-700"
                  title="Cambiar tamaño de subtítulos"
                >
                  Tamaño {captionScale.toFixed(2)}x
                </button>
              )}

              {/* Invite Tutor Carlos button */}
              {!tutorJoined && (
                <button
                  type="button"
                  onClick={() => setTutorJoined(true)}
                  className="px-3 py-2 rounded-xl bg-blue-900/80 hover:bg-blue-800 text-blue-200 text-xs sm:text-sm font-bold flex items-center gap-1.5 border border-blue-600"
                >
                  <Users className="w-4 h-4" />
                  <span>Sumar a Carlos (Tutor)</span>
                </button>
              )}
            </div>

            {/* End Call Button */}
            <div>
              <button
                type="button"
                onClick={handleEndCall}
                className="px-5 py-3 rounded-2xl bg-red-600 hover:bg-red-700 text-white font-black text-sm flex items-center gap-2 shadow-lg"
              >
                <PhoneOff className="w-5 h-5" />
                <span>Finalizar y Evaluar</span>
              </button>
            </div>
          </footer>
        ) : (
          /* Escrow Release & Satisfaction Review Step */
          <div className="p-6 bg-[#161616] text-white">
            {!isEscrowReleased ? (
              <div className="max-w-xl mx-auto space-y-4">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-2xl bg-green-900/60 text-green-300">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-lg font-black">Consulta con {expert.full_name} Finalizada</h3>
                    <p className="text-xs text-gray-400">
                      Verifique su satisfacción para autorizar la liberación del pago en garantía (Stripe Escrow).
                    </p>
                  </div>
                </div>

                {/* Escrow Financial Transparency Breakdown */}
                <div className="p-4 rounded-2xl bg-[#202020] border border-gray-700 space-y-2 text-sm">
                  <div className="flex justify-between text-gray-300">
                    <span>Monto total retenido en Escrow:</span>
                    <strong className="text-white">${(booking.hourly_rate_cents / 100).toFixed(2)} CAD</strong>
                  </div>
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>85% Payout al profesional verificado:</span>
                    <span>${(booking.expert_escrow_cents / 100).toFixed(2)} CAD</span>
                  </div>
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>15% Tarifa de plataforma y soporte CLEARLY:</span>
                    <span>${(booking.platform_fee_cents / 100).toFixed(2)} CAD</span>
                  </div>
                </div>

                {/* Rating Stars */}
                <div>
                  <label className="block text-sm font-bold text-gray-200 mb-2">
                    ¿Cómo califica la claridad y trato del profesional?
                  </label>
                  <div className="flex items-center gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onClick={() => setRating(star)}
                        className={`p-2 rounded-xl transition-transform hover:scale-110 ${
                          rating >= star ? "text-clearly-lemon" : "text-gray-600"
                        }`}
                        aria-label={`${star} estrellas`}
                      >
                        <Star className="w-7 h-7 fill-current" />
                      </button>
                    ))}
                    <span className="ml-2 font-bold text-sm text-clearly-lemon">
                      {rating} de 5 estrellas
                    </span>
                  </div>
                </div>

                {/* Feedback note */}
                <div>
                  <label htmlFor="call-feedback" className="block text-xs font-bold text-gray-300 mb-1">
                    Comentarios sobre la consulta (opcional):
                  </label>
                  <input
                    id="call-feedback"
                    type="text"
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-gray-900 border border-gray-700 text-sm text-white focus:outline-none focus:ring-2 focus:ring-clearly-lemon"
                  />
                </div>

                {/* Action buttons */}
                <div className="flex items-center justify-end gap-3 pt-2">
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-4 py-2 font-bold text-sm text-gray-400 hover:text-white"
                  >
                    Cerrar sin liberar
                  </button>
                  <button
                    type="button"
                    onClick={handleConfirmEscrowRelease}
                    className="px-6 py-3 font-bold text-sm rounded-2xl bg-green-600 hover:bg-green-700 text-white shadow-xl flex items-center gap-2"
                  >
                    <ShieldCheck className="w-5 h-5" />
                    <span>Liberar Pago Escrow ($45.00 CAD)</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="max-w-md mx-auto text-center py-6 space-y-3">
                <div className="w-16 h-16 mx-auto rounded-full bg-green-900/60 text-green-300 flex items-center justify-center">
                  <CheckCircle2 className="w-10 h-10" />
                </div>
                <h3 className="text-xl font-black text-white">¡Pago Escrow Liberado con Éxito!</h3>
                <p className="text-sm text-gray-300">
                  Se ha transferido ${(booking.expert_escrow_cents / 100).toFixed(2)} CAD a {expert.full_name} a través de Stripe Connect.
                  Su calificación de {rating} estrellas ha sido registrada.
                </p>
                <div className="pt-4">
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-6 py-2.5 rounded-xl bg-clearly-baltic text-white font-bold text-sm hover:bg-clearly-baltic/90 shadow-md"
                  >
                    Volver al Documento
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
