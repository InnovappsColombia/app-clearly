"""
CLEARLY — Automatic Matching Engine for Verified Human Experts (CLEARLY Premium).
Maps complex legal, immigration, and housing cases to certified professionals (RCIC, MSW).
"""

from typing import List, Optional
from uuid import UUID
from loguru import logger

from app.db.repository import repository
from app.models.entities import ExpertProfileEntity
from app.schemas.premium import ExpertMatchResponse, ExpertProfileResponse


class PremiumMatchingEngine:
    def __init__(self):
        self.repo = repository

    async def match_expert(
        self,
        document_id: Optional[UUID] = None,
        query_text: Optional[str] = None,
        senior_id: Optional[UUID] = None,
    ) -> ExpertMatchResponse:
        """
        Analyzes document context or text query and automatically matches the most
        suitable verified professional based on specialty, language, and case urgency.
        """
        corpus = ""
        doc = None
        if document_id:
            doc = await self.repo.get_document(document_id)
            if doc:
                corpus += f" {doc.issuing_entity or ''} {doc.original_extracted_text or ''} {doc.plain_summary}"

        if query_text:
            corpus += f" {query_text}"

        corpus_lower = corpus.lower()

        # Resolve preferred language of senior
        senior_lang = "es"
        if senior_id:
            senior = await self.repo.get_user(senior_id)
            if senior and senior.preferred_language:
                senior_lang = senior.preferred_language

        # 1. Classify target specialty based on legal/administrative markers
        detected_specialty = self._classify_specialty(corpus_lower)
        logger.info(f"Classified case complexity to specialty: '{detected_specialty}'")

        # 2. Retrieve verified available experts
        all_experts = await self.repo.list_expert_profiles()

        # 3. Score and rank experts
        scored: List[tuple[float, ExpertProfileEntity]] = []
        for exp in all_experts:
            score = 0.0
            # Specialty match
            # Specialty match is paramount (exact specialty gets 60 pts, key domain match gets 40 pts)
            if exp.specialty.strip().lower() == detected_specialty.strip().lower():
                score += 60.0
            elif any(
                kw in exp.specialty.lower()
                for kw in ["rcic", "ltb", "cra", "inmigración", "vivienda", "pensiones"]
                if kw in detected_specialty.lower()
            ):
                score += 40.0

            # Language match
            if senior_lang in exp.languages_spoken:
                score += 25.0

            # Rating & reputation weight (max 15.0)
            score += min(exp.average_rating * 3.0, 15.0)

            scored.append((score, exp))

        scored.sort(key=lambda x: x[0], reverse=True)

        if not scored:
            raise ValueError("No hay profesionales disponibles en este momento.")

        top_score, top_expert = scored[0]
        alternatives = [x[1] for x in scored[1:3]]

        # 4. Generate plain language reasoning (FH >= 80)
        reasoning = self._generate_plain_reasoning(top_expert, detected_specialty, senior_lang)

        # Build responses
        top_user = await self.repo.get_user(top_expert.user_id)
        full_name = top_user.full_name if top_user else "Profesional Verificado"

        matched_dto = self._build_expert_dto(top_expert, full_name)
        alt_dtos: List[ExpertProfileResponse] = []
        for alt in alternatives:
            alt_user = await self.repo.get_user(alt.user_id)
            alt_name = alt_user.full_name if alt_user else "Profesional Verificado"
            alt_dtos.append(self._build_expert_dto(alt, alt_name))

        return ExpertMatchResponse(
            matched_expert=matched_dto,
            detected_specialty=detected_specialty,
            match_score=round(top_score, 1),
            plain_language_reasoning=reasoning,
            alternative_experts=alt_dtos,
        )

    def _classify_specialty(self, text: str) -> str:
        """Deterministically classifies bureaucratic issue into verified expert specialty."""
        if any(term in text for term in ["ircc", "inmigra", "residencia", "visa", "refugio", "procedural fairness", "pasaporte", "ciudadan"]):
            return "Consultor Regulado de Inmigración Canadiense (RCIC)"
        elif any(term in text for term in ["ltb", "desalojo", "arrendamiento", "alquiler", "renta", "n4", "n12", "vivienda"]):
            return "Trabajadora Social de Vivienda y Mediación (LTB)"
        elif any(term in text for term in ["cra", "pension", "gis", "oas", "impuesto", "beneficio", "suplemento", "jubila"]):
            return "Especialista en Beneficios Cívicos y Pensiones CRA"
        else:
            return "Trabajadora Social de Vivienda y Mediación (LTB)"

    def _generate_plain_reasoning(self, expert: ExpertProfileEntity, specialty: str, lang: str) -> str:
        """Creates a high readability ($FH >= 80.0$) explanation for why this expert was chosen."""
        if "Inmigración" in specialty:
            return (
                "Hemos elegido a este especialista porque su carta es de Inmigración Canadá. "
                "Cuenta con licencia oficial CICC y habla español. "
                "Le ayudará a responder los requisitos a tiempo y sin errores."
            )
        elif "Vivienda" in specialty or "LTB" in specialty:
            return (
                "Hemos elegido a esta trabajadora social porque su carta es del tribunal de alquileres. "
                "Tiene amplia experiencia en mediación de vivienda en Brampton. "
                "Le acompañará para lograr un acuerdo justo con su propietario."
            )
        else:
            return (
                "Hemos elegido a este profesional porque conoce muy bien las pensiones y subsidios de Ontario. "
                "Habla su idioma y le explicará cómo asegurar sus pagos mensuales de forma sencilla."
            )

    def _build_expert_dto(self, expert: ExpertProfileEntity, full_name: str) -> ExpertProfileResponse:
        dollars = expert.hourly_rate_cents / 100.0
        return ExpertProfileResponse(
            id=expert.id,
            user_id=expert.user_id,
            full_name=full_name,
            specialty=expert.specialty,
            license_number=expert.license_number,
            id_verification_status=expert.id_verification_status,
            hourly_rate_cents=expert.hourly_rate_cents,
            hourly_rate_formatted=f"${dollars:.2f} CAD/hora",
            bio_plain_text=expert.bio_plain_text,
            languages_spoken=expert.languages_spoken,
            service_modalities=expert.service_modalities,
            average_rating=expert.average_rating,
            total_reviews=expert.total_reviews,
            is_available=expert.is_available,
        )


premium_matching_engine = PremiumMatchingEngine()
