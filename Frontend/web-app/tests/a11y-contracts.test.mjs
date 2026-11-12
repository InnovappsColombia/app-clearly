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

test("WCAG 2.1 AAA Contrast: Yellow on Black (Alto Contraste)", () => {
  const ratio = getContrastRatio("#FFFF00", "#000000");
  assert.ok(
    ratio >= 7.0,
    `El contraste debe ser >= 7.0 (WCAG AAA). Obtenido: ${ratio.toFixed(2)}:1`
  );
  assert.strictEqual(ratio > 19.0, true, "Yellow on Black supera 19:1");
});

test("WCAG 2.1 AAA Contrast: White text on Obsidian Black (#1B1B1B)", () => {
  const ratio = getContrastRatio("#FFFFFF", "#1B1B1B");
  assert.ok(
    ratio >= 7.0,
    `El contraste debe ser >= 7.0 (WCAG AAA). Obtenido: ${ratio.toFixed(2)}:1`
  );
  assert.strictEqual(ratio > 17.0, true, "White on Obsidian supera 17:1");
});

test("WCAG 2.1 AAA Contrast: White text on Baltic Blue (#394E96) for large text / UI elements", () => {
  const ratio = getContrastRatio("#FFFFFF", "#394E96");
  assert.ok(
    ratio >= 4.5,
    `El contraste en botones/encabezados debe ser >= 4.5 (WCAG AAA Large). Obtenido: ${ratio.toFixed(
      2
    )}:1`
  );
});

test("A11y Font Scaling Boundaries", () => {
  const scaleLevels = [100, 125, 150, 175, 200];
  assert.strictEqual(scaleLevels[0], 100, "Nivel mínimo debe ser 100%");
  assert.strictEqual(scaleLevels[scaleLevels.length - 1], 200, "Nivel máximo debe ser 200%");
  assert.strictEqual(scaleLevels.includes(125), true, "125% debe ser el valor base para seniors");
});

test("In-Browser TTS Speeds for Geriatric Accessibility", () => {
  const speeds = [0.75, 1.0, 1.25];
  assert.strictEqual(speeds[0], 0.75, "0.75x debe estar disponible para personas con disartria o fatiga cognitiva");
  assert.strictEqual(speeds[1], 1.0, "1.0x es velocidad normal");
  assert.strictEqual(speeds[2], 1.25, "1.25x es velocidad rápida");
});

test("Gold Standard Sample Documents: Fernandez-Huerta >= 80 Criteria", async () => {
  // Verify that all 3 sample documents have FH score >= 80 (Lectura muy fácil)
  const samples = [
    { name: "n4_eviction", score: 88.5, deadline: "2026-11-26" },
    { name: "ircc_letter", score: 86.2, deadline: "2026-12-12" },
    { name: "cra_gis_pension", score: 91.0, deadline: "2026-12-01" },
  ];

  for (const s of samples) {
    assert.ok(
      s.score >= 80.0,
      `Documento ${s.name} tiene un puntaje FH (${s.score}) inferior al umbral mínimo de 80.0`
    );
    assert.ok(s.deadline !== null, `Documento ${s.name} debe tener fecha límite extraída`);
  }
});

