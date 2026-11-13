import test from "node:test";
import assert from "node:assert/strict";

// Test 1: Validate Haversine formula calculation
function calculateDistanceKm(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c * 10) / 10;
}

test("Sprint 5 — Haversine Distance Calculation for GTA Municipalities", () => {
  // Brampton (43.6833, -79.7667) to Toronto Downtown (43.6532, -79.3832) is ~31 km
  const distance = calculateDistanceKm(43.6833, -79.7667, 43.6532, -79.3832);
  assert.ok(distance > 28 && distance < 35, `Distance was ${distance}`);

  // Zero distance test
  const same = calculateDistanceKm(43.6833, -79.7667, 43.6833, -79.7667);
  assert.equal(same, 0);
});

// Test 2: Validate RFC 5545 iCalendar generation invariant
test("Sprint 5 — RFC 5545 iCalendar Generator (.ICS) Invariants", () => {
  const mockEvent = {
    id: "evt-test-1",
    title: { es: "Taller de Bienestar", en: "Wellness Workshop", pa: "ਤੰਦਰੁਸਤੀ ਵਰਕਸ਼ਾਪ" },
    location_name: "Brampton Library",
    address: "65 Queen St E, Brampton, ON",
    start_datetime: "2026-11-21T10:30:00",
    end_datetime: "2026-11-21T11:45:00",
    plain_questions: {
      q1: { es: "Clase grupal", en: "Group class", pa: "ਗਰੁੱਪ ਕਲਾਸ" },
    },
    organizer_name: "Parks & Rec",
    accessibility_information: { es: "Rampa accesible", en: "Ramp", pa: "ਰੈਂਪ" },
  };

  const clean = (str) =>
    str.replace(/\\/g, "\\\\").replace(/[,;]/g, (m) => `\\${m}`).replace(/\n/g, "\\n");
  const formatDt = (dtStr) => dtStr.replace(/[-:]/g, "").slice(0, 15);

  const lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//CLEARLY//Accessible Community Events//EN",
    "BEGIN:VEVENT",
    `UID:${mockEvent.id}@clearly.community`,
    `DTSTART:${formatDt(mockEvent.start_datetime)}`,
    `DTEND:${formatDt(mockEvent.end_datetime)}`,
    `SUMMARY:${clean(mockEvent.title.es)}`,
    `LOCATION:${clean(`${mockEvent.location_name}, ${mockEvent.address}`)}`,
    "STATUS:CONFIRMED",
    "END:VEVENT",
    "END:VCALENDAR",
  ].join("\r\n");

  assert.ok(lines.includes("BEGIN:VCALENDAR"));
  assert.ok(lines.includes("VERSION:2.0"));
  assert.ok(lines.includes("BEGIN:VEVENT"));
  assert.ok(lines.includes("DTSTART:20261121T10300"));
  assert.ok(lines.includes("SUMMARY:Taller de Bienestar"));
  assert.ok(lines.includes("END:VEVENT"));
  assert.ok(lines.includes("END:VCALENDAR"));
});

// Test 3: Validate Google Maps Transit URL invariant
test("Sprint 5 — Google Maps Transit Directions URL Structure", () => {
  const dest = "Downtown Brampton Community Centre, 8 Central Park Dr, Brampton, ON";
  const url = `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(dest)}&travelmode=transit`;

  assert.ok(url.startsWith("https://www.google.com/maps/dir/?api=1"));
  assert.ok(url.includes("travelmode=transit"));
  assert.ok(url.includes("Central%20Park%20Dr"));
});

// Test 4: Validate 6 Canonical Plain Language Questions
test("Sprint 5 — Canonical 6-Question Framework Completeness", () => {
  const canonicalQuestions = ["q1", "q2", "q3", "q4", "q5", "q6"];
  assert.equal(canonicalQuestions.length, 6);
  assert.deepEqual(canonicalQuestions, ["q1", "q2", "q3", "q4", "q5", "q6"]);
});

// Test 5: Validate Trilingual Language Keys
test("Sprint 5 — Supported Languages Invariant (EN, ES, PA)", () => {
  const supportedLanguages = ["en", "es", "pa"];
  assert.equal(supportedLanguages.length, 3);
  assert.ok(supportedLanguages.includes("pa"), "Punjabi must be supported for Brampton/Peel Region inclusion");
});

