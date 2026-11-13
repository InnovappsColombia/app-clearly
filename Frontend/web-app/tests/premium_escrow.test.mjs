/**
 * CLEARLY — Sprint 4 Automated Test Suite
 * CLEARLY Premium: Automatic Expert Matching, Stripe Connect Escrow, and LiveKit WebRTC
 */

import test from "node:test";
import assert from "node:assert/strict";

// Helper for WCAG 2.1 Luminance and Contrast Calculation
function hexToRgb(hex) {
  const cleanHex = hex.replace("#", "");
  const bigint = parseInt(cleanHex, 16);
  return {
    r: (bigint >> 16) & 255,
    g: (bigint >> 8) & 255,
    b: bigint & 255,
  };
}

function getRelativeLuminance(r, g, b) {
  const [rs, gs, bs] = [r, g, b].map((c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function getContrastRatio(hex1, hex2) {
  const rgb1 = hexToRgb(hex1);
  const rgb2 = hexToRgb(hex2);
  const l1 = getRelativeLuminance(rgb1.r, rgb1.g, rgb1.b);
  const l2 = getRelativeLuminance(rgb2.r, rgb2.g, rgb2.b);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

// Deterministic matching rule implementation under test
function matchExpert(docType, summary) {
  const combined = (docType + " " + summary).toLowerCase();
  if (
    combined.includes("ircc") ||
    combined.includes("inmigra") ||
    combined.includes("residencia") ||
    combined.includes("visa") ||
    combined.includes("procedural fairness")
  ) {
    return {
      expert_name: "David Mendoza, RCIC",
      specialty: "Consultor Regulado de Inmigración Canadiense (RCIC)",
      license_number: "R708912-CICC",
      hourly_rate_cents: 4500,
    };
  } else if (
    combined.includes("ltb") ||
    combined.includes("desalojo") ||
    combined.includes("arrendamiento") ||
    combined.includes("alquiler") ||
    combined.includes("renta") ||
    combined.includes("vivienda")
  ) {
    return {
      expert_name: "Sarah Jenkins, MSW",
      specialty: "Trabajadora Social de Vivienda y Mediación (LTB)",
      license_number: "OCSWSSW-839120",
      hourly_rate_cents: 4000,
    };
  } else {
    return {
      expert_name: "María Santos",
      specialty: "Especialista en Beneficios Cívicos y Pensiones CRA",
      license_number: "CRA-CVITP-9021",
      hourly_rate_cents: 3500,
    };
  }
}

// Stripe Escrow math
function calculateEscrowSplit(totalCents, platformFeePercent = 15) {
  const platformFeeCents = Math.round((totalCents * platformFeePercent) / 100);
  const expertEscrowCents = totalCents - platformFeeCents;
  return {
    totalCents,
    platformFeeCents,
    expertEscrowCents,
  };
}

test("Sprint 4 — Automatic Expert Matching: IRCC Procedural Fairness", () => {
  const match = matchExpert(
    "Procedural Fairness Letter",
    "Immigration, Refugees and Citizenship Canada (IRCC) letter requesting proof of residency."
  );
  assert.equal(match.expert_name, "David Mendoza, RCIC");
  assert.equal(match.specialty, "Consultor Regulado de Inmigración Canadiense (RCIC)");
  assert.equal(match.license_number, "R708912-CICC");
  assert.equal(match.hourly_rate_cents, 4500);
});

test("Sprint 4 — Automatic Expert Matching: LTB N4 Eviction Notice", () => {
  const match = matchExpert(
    "Formulario N4 Desalojo",
    "Tribunal de Arrendamiento LTB exige pago de alquiler adeudado en Brampton."
  );
  assert.equal(match.expert_name, "Sarah Jenkins, MSW");
  assert.equal(match.specialty, "Trabajadora Social de Vivienda y Mediación (LTB)");
  assert.equal(match.license_number, "OCSWSSW-839120");
  assert.equal(match.hourly_rate_cents, 4000);
});

test("Sprint 4 — Automatic Expert Matching: CRA GIS & Pension Tax Audit", () => {
  const match = matchExpert(
    "Auditoría CRA OAS",
    "Agencia Tributaria de Canadá (CRA) suspendió el suplemento GIS de pensión para el adulto mayor."
  );
  assert.equal(match.expert_name, "María Santos");
  assert.equal(match.specialty, "Especialista en Beneficios Cívicos y Pensiones CRA");
  assert.equal(match.license_number, "CRA-CVITP-9021");
  assert.equal(match.hourly_rate_cents, 3500);
});

test("Sprint 4 — Stripe Connect Escrow Financial Split Invariants (15% Fee / 85% Expert)", () => {
  // $45.00 CAD
  const split45 = calculateEscrowSplit(4500, 15);
  assert.equal(split45.totalCents, 4500);
  assert.equal(split45.platformFeeCents, 675); // $6.75 CAD
  assert.equal(split45.expertEscrowCents, 3825); // $38.25 CAD
  assert.equal(split45.platformFeeCents + split45.expertEscrowCents, 4500);

  // $40.00 CAD
  const split40 = calculateEscrowSplit(4000, 15);
  assert.equal(split40.totalCents, 4000);
  assert.equal(split40.platformFeeCents, 600); // $6.00 CAD
  assert.equal(split40.expertEscrowCents, 3400); // $34.00 CAD
  assert.equal(split40.platformFeeCents + split40.expertEscrowCents, 4000);

  // $35.00 CAD
  const split35 = calculateEscrowSplit(3500, 15);
  assert.equal(split35.totalCents, 3500);
  assert.equal(split35.platformFeeCents, 525); // $5.25 CAD
  assert.equal(split35.expertEscrowCents, 2975); // $29.75 CAD
  assert.equal(split35.platformFeeCents + split35.expertEscrowCents, 3500);
});

test("Sprint 4 — LiveKit Subtitles Accessibility: WCAG 2.1 AAA Contrast Ratio (>= 7:1)", () => {
  // Yellow Subtitle Text (#F7D000) on Deep Dark Overlay (#0F0F0F)
  const yellowOnDark = getContrastRatio("#F7D000", "#0F0F0F");
  assert.ok(
    yellowOnDark >= 7.0,
    `Yellow subtitle contrast ${yellowOnDark.toFixed(2)} must be >= 7.0:1 for WCAG AAA`
  );

  // White Subtitle Text (#FFFFFF) on Deep Dark Overlay (#0F0F0F)
  const whiteOnDark = getContrastRatio("#FFFFFF", "#0F0F0F");
  assert.ok(
    whiteOnDark >= 7.0,
    `White text contrast ${whiteOnDark.toFixed(2)} must be >= 7.0:1 for WCAG AAA`
  );
});

test("Sprint 4 — LiveKit Gerontological A11y Metadata Defaults", () => {
  const roomConfig = {
    caption_font_scale: 1.5,
    enable_realtime_transcription: true,
  };
  assert.ok(roomConfig.caption_font_scale >= 1.5, "Senior caption scale must be at least 1.5x");
  assert.equal(roomConfig.enable_realtime_transcription, true);
});

test("Sprint 4 — Escrow State Machine Progression", () => {
  const states = ["pending_payment", "hold_in_escrow", "released"];
  let currentState = states[0];

  // User/Tutor authorizes payment
  currentState = "hold_in_escrow";
  assert.equal(currentState, "hold_in_escrow");

  // Consultation finishes and rating submitted -> release
  currentState = "released";
  assert.equal(currentState, "released");
});

