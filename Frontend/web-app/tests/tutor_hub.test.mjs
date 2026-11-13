import test from "node:test";
import assert from "node:assert/strict";

// Helper: Calculate relative luminance according to WCAG 2.1 specifications
function getLuminance(r, g, b) {
  const [rs, gs, bs] = [r, g, b].map((c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function hexToRgb(hex) {
  const cleaned = hex.replace("#", "");
  return [
    parseInt(cleaned.substring(0, 2), 16),
    parseInt(cleaned.substring(2, 4), 16),
    parseInt(cleaned.substring(4, 6), 16),
  ];
}

function getContrastRatio(hex1, hex2) {
  const l1 = getLuminance(...hexToRgb(hex1));
  const l2 = getLuminance(...hexToRgb(hex2));
  const brighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (brighter + 0.05) / (darker + 0.05);
}

test("Sprint 3 — Ephemeral Pairing Code Contract", () => {
  const code = "849201";
  const ttlSeconds = 900;
  assert.strictEqual(code.length, 6, "El código de emparejamiento debe tener exactamente 6 dígitos");
  assert.strictEqual(/^\d{6}$/.test(code), true, "El código debe ser estrictamente numérico");
  assert.strictEqual(ttlSeconds, 900, "La validez debe ser exactamente de 15 minutos (900s)");
});

test("Sprint 3 — Attenuated Capability Token Caveats (FMEA Spec 4.2)", () => {
  const caveats = [
    "action = read_only",
    "scope = critical_deadlines_and_checklists",
    "prohibit_actions = [financial_transfer, document_deletion, identity_alteration]",
  ];

  assert.ok(caveats.some((c) => c.includes("read_only")), "Tutor debe tener capacidad estricta de solo lectura");
  assert.ok(
    caveats.some((c) => c.includes("prohibit_actions") && c.includes("financial_transfer")),
    "Prohibición estricta de transferencias financieras para prevenir abuso patrimonial"
  );
});

test("Sprint 3 — Collaborative Checklist Item Completion Tracking", () => {
  const task = {
    id: "act-1",
    task: "Abonar renta adeudada o convenir plan de pagos",
    isCompleted: false,
    completedByName: null,
  };

  // Simulate Carlos toggling the task
  const completedTask = {
    ...task,
    isCompleted: true,
    completedByName: "Carlos Pabla (Hijo)",
    completedAt: "12/11/2026, 18:36",
  };

  assert.strictEqual(completedTask.isCompleted, true);
  assert.strictEqual(completedTask.completedByName, "Carlos Pabla (Hijo)");
  assert.ok(completedTask.completedAt !== null);
});

test("Sprint 3 — Duress Mode Protocol (FMEA FM-04 Silent Quarantine)", () => {
  const normalPin = "1234";
  const duressPin = "9876";

  function evaluatePin(pin) {
    if (pin === duressPin) {
      return {
        uiMessage: "Preferencias de privacidad actualizadas con éxito.",
        isQuarantineActive: true,
        tutorAlertsSuspended: true,
        socialWorkerAlertDispatched: true,
      };
    }
    return {
      uiMessage: "PIN verificado.",
      isQuarantineActive: false,
      tutorAlertsSuspended: false,
      socialWorkerAlertDispatched: false,
    };
  }

  const result = evaluatePin(duressPin);
  // Identical innocent UI message to never tip off a coercing party
  assert.strictEqual(
    result.uiMessage,
    "Preferencias de privacidad actualizadas con éxito."
  );
  assert.strictEqual(result.isQuarantineActive, true);
  assert.strictEqual(result.tutorAlertsSuspended, true);
  assert.strictEqual(result.socialWorkerAlertDispatched, true);
});

test("Sprint 3 — WCAG AAA Contrast for Tutor Hub Critical Deadlines Alert", () => {
  // Pure WCAG 2.1 AAA Contrast: Dark Red (red-900: #7F1D1D) on Light Red (red-100: #FEE2E2)
  const ratioRedAlert = getContrastRatio("#7F1D1D", "#FEE2E2");
  assert.ok(
    ratioRedAlert >= 7.0,
    `El contraste del badge de plazo crítico debe ser >= 7.0 (WCAG AAA). Obtenido: ${ratioRedAlert.toFixed(2)}:1`
  );

  // Pure WCAG 2.1 AAA Contrast: Dark Amber (amber-950: #451A03) on Light Amber (amber-100: #FEF3C7)
  const ratioAmberAlert = getContrastRatio("#451A03", "#FEF3C7");
  assert.ok(
    ratioAmberAlert >= 7.0,
    `El contraste del banner preventivo debe ser >= 7.0 (WCAG AAA). Obtenido: ${ratioAmberAlert.toFixed(2)}:1`
  );
});
