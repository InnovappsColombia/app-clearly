"use client";

import React, { useState, useEffect } from "react";
import { useA11y } from "../../context/A11yContext";
import {
  Users,
  ShieldCheck,
  BellRing,
  CheckCircle2,
  Circle,
  Calendar,
  AlertTriangle,
  QrCode,
  KeyRound,
  RefreshCw,
  Sparkles,
  ExternalLink,
  Volume2,
  Lock,
  UserCheck,
  Copy,
  Check,
  ShieldAlert,
} from "lucide-react";

interface TaskItem {
  id: string;
  documentTitle: string;
  task: string;
  requiredDoc?: string;
  deadline: string;
  daysRemaining: number;
  isCritical: boolean;
  isCompleted: boolean;
  completedByName?: string;
  completedAt?: string;
}

export function TutorHubDashboard() {
  const { speak, isSpeaking, stopSpeech, announce } = useA11y();

  // Current view role: 'tutor' (Carlos) or 'senior' (Elena)
  const [activeRole, setActiveRole] = useState<"tutor" | "senior">("tutor");

  // Pairing code state for Senior
  const [pairingCode, setPairingCode] = useState<string>("849201");
  const [codeTimeLeft, setCodeTimeLeft] = useState<number>(885); // 14m 45s
  const [copiedCode, setCopiedCode] = useState<boolean>(false);

  // Real-time synchronization state
  const [isLiveConnected, setIsLiveConnected] = useState<boolean>(true);
  const [lastSyncTime, setLastSyncTime] = useState<string>("En vivo");

  // Duress security mode (FMEA FM-04)
  const [isDuressActive, setIsDuressActive] = useState<boolean>(false);
  const [duressInputPin, setDuressInputPin] = useState<string>("");
  const [duressMessage, setDuressMessage] = useState<string | null>(null);

  // Collaborative tasks
  const [tasks, setTasks] = useState<TaskItem[]>([
    {
      id: "act-1",
      documentTitle: "Tribunal de Arrendamiento (LTB) — Formulario N4",
      task: "Abonar renta adeudada ($1,450 CAD) o convenir plan de pagos con el propietario.",
      requiredDoc: "Comprobante de transferencia bancaria o recibo firmado",
      deadline: "2026-11-26",
      daysRemaining: 14,
      isCritical: true,
      isCompleted: false,
    },
    {
      id: "act-2",
      documentTitle: "Inmigración Canadá (IRCC) — Procedural Fairness",
      task: "Reunir sellos del pasaporte y recibos de servicios del domicilio en Brampton.",
      requiredDoc: "Pasaportes vigentes y contrato de arrendamiento",
      deadline: "2026-12-12",
      daysRemaining: 30,
      isCritical: false,
      isCompleted: true,
      completedByName: "Carlos Pabla (Hijo)",
      completedAt: "Hoy a las 11:20 AM",
    },
    {
      id: "act-3",
      documentTitle: "Centro Cívico Flower City — Vacunación",
      task: "Llevar tarjeta OHIP y lista de medicamentos habituales a la clínica comunitaria.",
      requiredDoc: "Tarjeta de salud OHIP",
      deadline: "2026-11-27",
      daysRemaining: 15,
      isCritical: true,
      isCompleted: false,
    },
  ]);

  // Expiration timer for pairing code
  useEffect(() => {
    const timer = setInterval(() => {
      setCodeTimeLeft((prev) => (prev > 0 ? prev - 1 : 900));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatSeconds = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  const handleToggleTask = (taskId: string) => {
    setTasks((prev) =>
      prev.map((t) => {
        if (t.id === taskId) {
          const nextState = !t.isCompleted;
          const updated = {
            ...t,
            isCompleted: nextState,
            completedByName: nextState
              ? activeRole === "tutor"
                ? "Carlos Pabla (Tutor)"
                : "Elena Pabla (Titular)"
              : undefined,
            completedAt: nextState ? "Hace un momento" : undefined,
          };
          announce(
            nextState
              ? `Tarea marcada como completada: ${t.task}`
              : `Tarea desmarcada: ${t.task}`
          );
          return updated;
        }
        return t;
      })
    );
    setLastSyncTime(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
  };

  const handleCopyCode = () => {
    if (navigator?.clipboard) {
      navigator.clipboard.writeText(pairingCode);
      setCopiedCode(true);
      announce("Código de vinculación copiado al portapapeles");
      setTimeout(() => setCopiedCode(false), 3000);
    }
  };

  const handleGenerateNewCode = () => {
    const newCode = `${Math.floor(100000 + Math.random() * 900000)}`;
    setPairingCode(newCode);
    setCodeTimeLeft(900);
    announce(`Nuevo código de vinculación generado: ${newCode}`);
  };

  const handleTriggerDuress = () => {
    if (duressInputPin === "9876") {
      setIsDuressActive(true);
      setDuressMessage(
        "Modo de Coacción Silenciosa Activado (FMEA FM-04). Las alertas al tutor se desvincularon discretamente sin alertar a ningún coaccionador."
      );
      announce("Preferencias de privacidad actualizadas con éxito.");
    } else {
      setDuressMessage("Código no reconocido. Ingrese el PIN de prueba '9876'.");
    }
  };

  const handleSpeakDashboard = () => {
    if (isSpeaking) {
      stopSpeech();
    } else {
      const summaryText =
        activeRole === "tutor"
          ? `Panel Tutor Hub. Supervisando a Elena Pabla. Hay dos fechas límite urgentes de menos de quince días: el formulario de arrendamiento que vence en catorce días y la clínica de vacunación en quince días. Dos tareas pendientes por completar.`
          : `Modo Titular. Tu código de vinculación familiar es ${pairingCode}. Válido por ${Math.floor(
              codeTimeLeft / 60
            )} minutos. Carlos tiene permisos de solo lectura para cuidarte.`;
      speak(summaryText);
    }
  };

  return (
    <section
      role="region"
      aria-label="Tutor Hub y Sincronización Colaborativa en Tiempo Real"
      className="w-full my-8 p-6 sm:p-8 rounded-3xl border-2 transition-all duration-200 bg-white dark:bg-[#1C1C1C] border-clearly-baltic/40 dark:border-clearly-royal/60 shadow-lg"
    >
      {/* Header with Role Selector and Live Status */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 pb-6 border-b border-gray-200 dark:border-gray-800">
        <div>
          <div className="flex items-center gap-2.5 mb-2">
            <div
              className="p-2.5 rounded-xl bg-blue-100 text-clearly-baltic dark:bg-blue-950 dark:text-blue-300"
              aria-hidden="true"
            >
              <Users className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-2xl sm:text-3xl font-black text-clearly-obsidian dark:text-white tracking-tight">
                Tutor Hub en Tiempo Real
              </h2>
              <p className="text-xs sm:text-sm font-semibold text-gray-600 dark:text-gray-400">
                Canal colaborativo intergeneracional con sincronización instantánea y resguardo ético
              </p>
            </div>
          </div>
        </div>

        {/* Live sync pill & TTS voice reader */}
        <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto justify-start lg:justify-end">
          <div
            className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold bg-green-50 text-green-800 dark:bg-green-950/80 dark:text-green-300 border border-green-300 dark:border-green-800"
            role="status"
            aria-live="polite"
          >
            <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse" aria-hidden="true" />
            <span>Sincronizado {lastSyncTime}</span>
          </div>

          <button
            type="button"
            onClick={handleSpeakDashboard}
            aria-label="Escuchar resumen del panel en voz alta"
            className="px-4 py-2 text-xs sm:text-sm font-bold rounded-xl flex items-center gap-2 text-white bg-clearly-baltic dark:bg-clearly-royal hover:opacity-90 transition-opacity"
          >
            <Volume2 className="w-4 h-4" aria-hidden="true" />
            <span>{isSpeaking ? "Detener voz" : "Escuchar panel"}</span>
          </button>
        </div>
      </div>

      {/* Role Toggle Tabs */}
      <div className="mt-6 flex flex-wrap items-center gap-3" role="tablist" aria-label="Seleccionar rol de visualización">
        <button
          type="button"
          role="tab"
          aria-selected={activeRole === "tutor"}
          onClick={() => {
            setActiveRole("tutor");
            announce("Vista cambiada a Modo Tutor: Carlos Pabla");
          }}
          className={`px-5 py-3 rounded-2xl text-sm sm:text-base font-bold flex items-center gap-2.5 transition-all border-2 ${
            activeRole === "tutor"
              ? "bg-clearly-baltic text-white border-clearly-baltic shadow-md dark:bg-clearly-royal dark:border-clearly-royal"
              : "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-transparent hover:border-gray-300"
          }`}
        >
          <UserCheck className="w-5 h-5" aria-hidden="true" />
          <span>Vista Tutor: Carlos Pabla (Hijo)</span>
        </button>

        <button
          type="button"
          role="tab"
          aria-selected={activeRole === "senior"}
          onClick={() => {
            setActiveRole("senior");
            announce("Vista cambiada a Modo Titular: Elena Pabla");
          }}
          className={`px-5 py-3 rounded-2xl text-sm sm:text-base font-bold flex items-center gap-2.5 transition-all border-2 ${
            activeRole === "senior"
              ? "bg-clearly-baltic text-white border-clearly-baltic shadow-md dark:bg-clearly-royal dark:border-clearly-royal"
              : "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-transparent hover:border-gray-300"
          }`}
        >
          <ShieldCheck className="w-5 h-5" aria-hidden="true" />
          <span>Vista Titular: Elena Pabla (74 años)</span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* VISTA 1: TUTOR HUB (CARLOS PABLA) */}
      {/* ========================================================================= */}
      {activeRole === "tutor" && (
        <div className="mt-8 space-y-6">
          {/* Senior Profile Summary Header */}
          <div className="p-5 rounded-2xl bg-blue-50/70 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-3.5">
              <div
                className="w-12 h-12 rounded-full bg-clearly-baltic text-white dark:bg-blue-600 flex items-center justify-center font-black text-xl"
                aria-hidden="true"
              >
                EP
              </div>
              <div>
                <h3 className="text-lg font-bold text-clearly-obsidian dark:text-white">
                  Supervisando a: Elena Pabla (Madre)
                </h3>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300">
                  Brampton, ON • Teléfono: +1 (905) 555-0101 • Idioma: Español
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs font-bold text-clearly-baltic dark:text-blue-300 px-3 py-1.5 rounded-lg bg-white dark:bg-black/40 border border-blue-200 dark:border-blue-800">
              <Lock className="w-4 h-4" aria-hidden="true" />
              <span>Token de Capacidad: Solo Lectura + Checklist</span>
            </div>
          </div>

          {/* Critical Deadlines Priority Banner (< 15 days) */}
          <div
            role="alert"
            className="p-5 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border-2 border-amber-300 dark:border-amber-700/80 shadow-sm"
          >
            <div className="flex items-start gap-3.5">
              <AlertTriangle className="w-6 h-6 text-amber-700 dark:text-amber-400 flex-shrink-0 mt-0.5" aria-hidden="true" />
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="text-base sm:text-lg font-black text-amber-950 dark:text-amber-200">
                    Alerta Proactiva: 2 Plazos Críticos Requieren Atención
                  </h4>
                  <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-red-100 text-red-900 dark:bg-red-950 dark:text-red-300 border border-red-300 dark:border-red-800">
                    &lt; 15 días
                  </span>
                </div>
                <p className="mt-1 text-sm text-amber-900 dark:text-amber-300 font-medium leading-relaxed">
                  Elena recibió correspondencia con fechas límite estrictas. Como tutor, CLEARLY te
                  mantiene al tanto para evitar multas, pérdida de vivienda o trámites migratorios
                  caducados.
                </p>
              </div>
            </div>
          </div>

          {/* Collaborative Real-Time Checklist */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-xl font-black text-clearly-obsidian dark:text-white flex items-center gap-2">
                  <CheckCircle2 className="w-6 h-6 text-clearly-baltic dark:text-blue-400" aria-hidden="true" />
                  <span>Checklist Colaborativo Familiar</span>
                </h3>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                  Marca las tareas que ya realizaste junto a tu familiar. Se actualiza en tiempo real en ambos dispositivos.
                </p>
              </div>
            </div>

            <div className="space-y-3" role="list" aria-label="Lista de tareas colaborativas">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  role="listitem"
                  className={`p-4 sm:p-5 rounded-2xl border-2 transition-all ${
                    task.isCompleted
                      ? "bg-green-50/60 dark:bg-green-950/20 border-green-300 dark:border-green-800/80 opacity-90"
                      : task.isCritical
                      ? "bg-white dark:bg-gray-900 border-clearly-baltic/50 dark:border-clearly-royal/60 shadow-sm"
                      : "bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800"
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3.5">
                      <button
                        type="button"
                        onClick={() => handleToggleTask(task.id)}
                        aria-label={
                          task.isCompleted
                            ? `Marcar como no completada la tarea: ${task.task}`
                            : `Marcar como completada la tarea: ${task.task}`
                        }
                        className="mt-0.5 p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors focus:ring-2 focus:ring-clearly-baltic"
                      >
                        {task.isCompleted ? (
                          <CheckCircle2 className="w-7 h-7 text-green-600 dark:text-green-400" aria-hidden="true" />
                        ) : (
                          <Circle className="w-7 h-7 text-gray-400 hover:text-clearly-baltic dark:hover:text-blue-400" aria-hidden="true" />
                        )}
                      </button>

                      <div>
                        <span className="text-xs font-bold uppercase tracking-wider text-clearly-baltic dark:text-blue-400">
                          {task.documentTitle}
                        </span>

                        <p
                          className={`mt-0.5 text-base sm:text-lg font-bold ${
                            task.isCompleted
                              ? "line-through text-gray-500 dark:text-gray-400"
                              : "text-clearly-obsidian dark:text-white"
                          }`}
                        >
                          {task.task}
                        </p>

                        {task.requiredDoc && (
                          <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1">
                            📄 <strong>Documento necesario:</strong> {task.requiredDoc}
                          </p>
                        )}

                        {task.completedByName && (
                          <div className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300">
                            <Check className="w-3.5 h-3.5" aria-hidden="true" />
                            <span>Completado por: {task.completedByName} • {task.completedAt}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Deadline Pill */}
                    <div className="flex flex-col items-end flex-shrink-0">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-black ${
                          task.daysRemaining <= 15
                            ? "bg-red-100 text-red-900 dark:bg-red-950 dark:text-red-300 border border-red-300 dark:border-red-800"
                            : "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300"
                        }`}
                      >
                        {task.daysRemaining} días restantes
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Vence: {task.deadline}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Escalation to CLEARLY Premium Action */}
          <div className="mt-6 p-5 rounded-2xl bg-gradient-to-r from-blue-900 to-indigo-950 text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-yellow-300" aria-hidden="true" />
                <h4 className="font-black text-lg">¿El trámite legal es complejo?</h4>
              </div>
              <p className="mt-1 text-sm text-blue-100">
                Puedes contratar a un consultor de inmigración regulado (RCIC) o trabajador social
                verificado en CLEARLY Premium para acompañar a tu madre en Brampton.
              </p>
            </div>
            <button
              type="button"
              className="px-5 py-2.5 text-xs sm:text-sm font-black rounded-xl bg-yellow-400 text-black hover:bg-yellow-300 transition-colors whitespace-nowrap"
            >
              Consultar Profesionales ($45/hr)
            </button>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* VISTA 2: TITULAR (ELENA PABLA) */}
      {/* ========================================================================= */}
      {activeRole === "senior" && (
        <div className="mt-8 space-y-6">
          {/* Ephemeral Pairing Code Card */}
          <div className="p-6 sm:p-8 rounded-3xl bg-blue-50/80 dark:bg-blue-950/50 border-2 border-clearly-baltic/50 dark:border-blue-700">
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="max-w-xl text-center md:text-left">
                <span className="text-xs sm:text-sm font-bold uppercase tracking-wider text-clearly-baltic dark:text-blue-400">
                  Vincular a un Familiar de Confianza
                </span>
                <h3 className="text-2xl sm:text-3xl font-black text-clearly-obsidian dark:text-white mt-1">
                  Tu Código de Vinculación Familiar
                </h3>
                <p className="mt-2 text-sm sm:text-base text-gray-700 dark:text-gray-300 leading-relaxed font-medium">
                  Entrega este código a tu hijo o familiar para que se conecte a tu cuenta. Solo podrá
                  ver recordatorios y fechas urgentes. <strong>Nunca podrá ver tus contraseñas ni tocar tus cuentas.</strong>
                </p>

                {/* Big Pairing Code Display */}
                <div className="mt-6 flex flex-wrap items-center justify-center md:justify-start gap-4">
                  <div className="px-6 py-3 rounded-2xl bg-white dark:bg-black border-2 border-clearly-baltic text-clearly-baltic dark:text-yellow-400 font-mono font-black text-3xl sm:text-4xl tracking-widest shadow-inner">
                    {pairingCode}
                  </div>

                  <button
                    type="button"
                    onClick={handleCopyCode}
                    className="px-4 py-3 rounded-2xl text-sm font-bold flex items-center gap-2 bg-clearly-baltic text-white hover:opacity-90 transition-opacity"
                    aria-label="Copiar código de vinculación"
                  >
                    {copiedCode ? <Check className="w-5 h-5 text-green-300" /> : <Copy className="w-5 h-5" />}
                    <span>{copiedCode ? "Copiado" : "Copiar"}</span>
                  </button>

                  <button
                    type="button"
                    onClick={handleGenerateNewCode}
                    className="px-4 py-3 rounded-2xl text-sm font-bold flex items-center gap-2 bg-gray-200 text-gray-800 dark:bg-gray-800 dark:text-gray-200 hover:bg-gray-300 transition-colors"
                    aria-label="Generar nuevo código"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span>Renovar</span>
                  </button>
                </div>

                <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">
                  ⏰ Este código expira en: <strong>{formatSeconds(codeTimeLeft)}</strong> (Seguridad efímera Curve25519)
                </p>
              </div>

              {/* QR Code preview representation */}
              <div className="p-4 rounded-2xl bg-white dark:bg-black border-2 border-gray-300 dark:border-gray-700 text-center flex flex-col items-center">
                <QrCode className="w-32 h-32 text-clearly-obsidian dark:text-white" aria-hidden="true" />
                <span className="mt-2 text-xs font-bold text-gray-600 dark:text-gray-400">
                  Escanear con App Tutor
                </span>
              </div>
            </div>
          </div>

          {/* Duress Protection Card (FMEA FM-04) */}
          <div className="p-6 rounded-3xl bg-gray-50 dark:bg-gray-900 border-2 border-gray-200 dark:border-gray-800">
            <div className="flex items-start gap-4">
              <div
                className="p-3 rounded-2xl bg-gray-200 dark:bg-gray-800 text-clearly-obsidian dark:text-gray-200"
                aria-hidden="true"
              >
                <ShieldAlert className="w-6 h-6" />
              </div>
              <div className="w-full">
                <h4 className="text-lg font-black text-clearly-obsidian dark:text-white">
                  Protección de Coacción Silenciosa (Duress Mode — FMEA FM-04)
                </h4>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400 leading-relaxed font-medium">
                  Si alguna vez sientes presión indebida o abuso por parte de un familiar para que le
                  muestres tu aplicación o documentos, ingresa tu <strong>PIN de Emergencia (9876)</strong>.
                  La app mantendrá una apariencia normal, pero desconectará en silencio todas las alertas a ese tutor
                  y solicitará un chequeo cívico confidencial a trabajadores sociales comunitarios.
                </p>

                <div className="mt-4 flex flex-wrap items-center gap-3">
                  <input
                    type="password"
                    maxLength={4}
                    value={duressInputPin}
                    onChange={(e) => setDuressInputPin(e.target.value)}
                    placeholder="PIN (ej. 9876)"
                    className="px-4 py-2 text-base font-bold rounded-xl border border-gray-300 dark:border-gray-700 bg-white dark:bg-black text-clearly-obsidian dark:text-white w-36 text-center"
                    aria-label="Ingresar PIN de prueba para modo de coacción"
                  />
                  <button
                    type="button"
                    onClick={handleTriggerDuress}
                    className="px-4 py-2 text-sm font-bold rounded-xl bg-gray-800 text-white dark:bg-gray-700 hover:bg-gray-900 transition-colors"
                  >
                    Probar PIN de Seguridad
                  </button>
                </div>

                {duressMessage && (
                  <div
                    className="mt-3 p-3 rounded-xl bg-blue-100 text-blue-900 dark:bg-blue-950 dark:text-blue-300 text-xs sm:text-sm font-semibold"
                    role="status"
                    aria-live="polite"
                  >
                    {duressMessage}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
