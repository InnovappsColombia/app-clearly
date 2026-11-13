import { ExpertProfile, ExpertMatchResult } from "@/types/premium";

export const SEED_EXPERTS: ExpertProfile[] = [
  {
    id: "66666666-6666-6666-6666-666666666666",
    user_id: "33333333-3333-3333-3333-333333333333",
    full_name: "David Mendoza, RCIC",
    specialty: "Consultor Regulado de Inmigración Canadiense (RCIC)",
    license_number: "R708912-CICC",
    id_verification_status: "verified",
    hourly_rate_cents: 4500,
    bio_plain_text:
      "Especialista con 12 años guiando a adultos mayores y familias hispanas en residencia permanente, visas y cartas de IRCC.",
    languages_spoken: ["es", "en"],
    service_modalities: ["virtual", "in_person"],
    average_rating: 4.95,
    total_reviews: 38,
    is_available: true,
  },
  {
    id: "66666666-6666-6666-6666-666666666667",
    user_id: "44444444-4444-4444-4444-444444444444",
    full_name: "Sarah Jenkins, MSW",
    specialty: "Trabajadora Social de Vivienda y Mediación (LTB)",
    license_number: "OCSWSSW-839120",
    id_verification_status: "verified",
    hourly_rate_cents: 4000,
    bio_plain_text:
      "Trabajadora social bilingüe especializada en mediación de desalojos del tribunal LTB y acuerdos justos de alquiler.",
    languages_spoken: ["es", "en"],
    service_modalities: ["virtual", "in_person"],
    average_rating: 4.98,
    total_reviews: 52,
    is_available: true,
  },
  {
    id: "66666666-6666-6666-6666-666666666668",
    user_id: "55555555-5555-5555-5555-555555555555",
    full_name: "María Santos",
    specialty: "Especialista en Beneficios Cívicos y Pensiones CRA",
    license_number: "CRA-CVITP-9021",
    id_verification_status: "verified",
    hourly_rate_cents: 3500,
    bio_plain_text:
      "Experta comunitaria en Ontario Trillium Benefit, GIS, OAS y regularización de impuestos atrasados para seniors.",
    languages_spoken: ["es", "en"],
    service_modalities: ["virtual", "in_person"],
    average_rating: 4.9,
    total_reviews: 29,
    is_available: true,
  },
];

/**
 * Deterministic matching function mirroring Backend app.services.premium_matching
 */
export function matchExpertLocally(docType: string, summary: string): ExpertMatchResult {
  const combined = (docType + " " + summary).toLowerCase();

  let targetSpecialty = "Trabajadora Social de Vivienda y Mediación (LTB)";
  let reasoning =
    "Hemos elegido a esta trabajadora social porque su carta es del tribunal de alquileres. Tiene amplia experiencia en mediación de vivienda en Brampton. Le acompañará para lograr un acuerdo justo con su propietario.";

  if (
    combined.includes("ircc") ||
    combined.includes("inmigra") ||
    combined.includes("residencia") ||
    combined.includes("visa") ||
    combined.includes("refugio") ||
    combined.includes("procedural fairness")
  ) {
    targetSpecialty = "Consultor Regulado de Inmigración Canadiense (RCIC)";
    reasoning =
      "Hemos elegido a este especialista porque su carta es de Inmigración Canadá. Cuenta con licencia oficial CICC y habla español. Le ayudará a responder los requisitos a tiempo y sin errores.";
  } else if (
    combined.includes("cra") ||
    combined.includes("pension") ||
    combined.includes("gis") ||
    combined.includes("oas") ||
    combined.includes("impuesto") ||
    combined.includes("jubila")
  ) {
    targetSpecialty = "Especialista en Beneficios Cívicos y Pensiones CRA";
    reasoning =
      "Hemos elegido a este profesional porque conoce muy bien las pensiones y subsidios de Ontario. Habla su idioma y le explicará cómo asegurar sus pagos mensuales de forma sencilla.";
  }

  const matched =
    SEED_EXPERTS.find((e) => e.specialty === targetSpecialty) || SEED_EXPERTS[0];
  const alternatives = SEED_EXPERTS.filter((e) => e.id !== matched.id);

  return {
    matched_expert: matched,
    detected_specialty: targetSpecialty,
    match_score: 99.8,
    plain_language_reasoning: reasoning,
    alternative_experts: alternatives,
  };
}
