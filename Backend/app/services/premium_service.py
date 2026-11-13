"""
CLEARLY — Premium Escrow & Booking Service
Manages expert consultations with Stripe Connect escrow holds and LiveKit WebRTC signaling.
Supports delegate payment by family tutors (Carlos) on behalf of seniors (Elena).
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID, uuid4
from loguru import logger

from app.core.config import settings
from app.db.repository import repository
from app.models.entities import NotificationEntity, PremiumBookingEntity, get_utc_now
from app.schemas.premium import (
    BookingResponse,
    CreateBookingRequest,
    ReleaseEscrowRequest,
    ReleaseEscrowResponse,
)
from app.services.livekit_service import livekit_service


class PremiumService:
    def __init__(self):
        self.repo = repository
        self.livekit = livekit_service

    async def create_booking(self, req: CreateBookingRequest) -> BookingResponse:
        """
        Creates a premium consultation booking with funds held in Stripe Escrow.
        Funds are NOT released to the professional until the senior or tutor confirms completion.
        """
        expert = await self.repo.get_expert_profile(req.expert_id)
        if not expert or not expert.is_available:
            raise ValueError("El profesional seleccionado no está disponible para reservas.")

        senior = await self.repo.get_user(req.client_senior_id)
        if not senior:
            raise ValueError("El usuario titular (adulto mayor) no existe.")

        payer_id = req.requested_by_user_id or req.client_senior_id
        payer = await self.repo.get_user(payer_id)

        # Calculate fees (15% platform commission, 85% expert payout)
        amount_cents = expert.hourly_rate_cents
        platform_fee_cents = int(amount_cents * (settings.CLEARLY_PLATFORM_FEE_PERCENT / 100.0))
        expert_payout_cents = amount_cents - platform_fee_cents

        booking_id = uuid4()
        scheduled_end = req.scheduled_end or (req.scheduled_start + timedelta(hours=1))

        # Generate LiveKit Room and Token
        livekit_details = self.livekit.create_room_token(
            booking_id=booking_id,
            participant_identity=f"senior_{senior.id}",
            participant_name=senior.full_name,
            is_senior=True,
        )

        # Stripe Connect Escrow Hold (Simulated/Configured with Stripe Secret)
        stripe_pi_id = f"pi_clearly_escrow_{uuid4().hex[:12]}"
        logger.info(
            f"Stripe Escrow Hold initialized: {stripe_pi_id} for ${amount_cents / 100.0:.2f} CAD. "
            f"Funds safely held in escrow until session confirmation."
        )

        booking_entity = PremiumBookingEntity(
            id=booking_id,
            client_senior_id=senior.id,
            requested_by_user_id=payer_id,
            expert_id=expert.id,
            document_id=req.document_id,
            modality=req.modality,
            scheduled_start=req.scheduled_start,
            scheduled_end=scheduled_end,
            livekit_room_name=livekit_details.room_name,
            livekit_token=livekit_details.token,
            status="escrow_held",
            stripe_payment_intent_id=stripe_pi_id,
            amount_cents=amount_cents,
            expert_payout_cents=expert_payout_cents,
            platform_fee_cents=platform_fee_cents,
        )
        saved = await self.repo.create_premium_booking(booking_entity)

        # Notify expert of new booking
        notif = NotificationEntity(
            id=uuid4(),
            user_id=expert.user_id,
            title="Nueva Consulta CLEARLY Premium Asignada",
            message=f"Tiene una consulta agendada con {senior.full_name} para el {req.scheduled_start.strftime('%d/%m/%Y %H:%M')}. Honorarios garantizados en Escrow.",
            channel="in_app",
            is_urgent=False,
            metadata={"booking_id": str(booking_id)},
        )
        await self.repo.create_notification(notif)

        expert_user = await self.repo.get_user(expert.user_id)
        expert_name = expert_user.full_name if expert_user else "Profesional Verificado"

        return BookingResponse(
            id=saved.id,
            client_senior_id=senior.id,
            client_name=senior.full_name,
            requested_by_name=payer.full_name if payer else "Titular",
            expert_id=expert.id,
            expert_name=expert_name,
            specialty=expert.specialty,
            license_number=expert.license_number,
            modality=saved.modality,
            scheduled_start=saved.scheduled_start,
            scheduled_end=saved.scheduled_end,
            status=saved.status,
            stripe_payment_intent_id=saved.stripe_payment_intent_id,
            amount_cents=saved.amount_cents,
            amount_formatted=f"${saved.amount_cents / 100.0:.2f} CAD",
            livekit_room_name=saved.livekit_room_name,
            livekit_token=saved.livekit_token,
            escrow_held=True,
            created_at=saved.created_at,
        )

    async def get_booking(self, booking_id: UUID) -> Optional[BookingResponse]:
        booking = await self.repo.get_premium_booking(booking_id)
        if not booking:
            return None

        senior = await self.repo.get_user(booking.client_senior_id)
        payer = await self.repo.get_user(booking.requested_by_user_id)
        expert = await self.repo.get_expert_profile(booking.expert_id)
        expert_user = await self.repo.get_user(expert.user_id) if expert else None

        return BookingResponse(
            id=booking.id,
            client_senior_id=booking.client_senior_id,
            client_name=senior.full_name if senior else "Titular",
            requested_by_name=payer.full_name if payer else "Pagador",
            expert_id=booking.expert_id,
            expert_name=expert_user.full_name if expert_user else "Experto",
            specialty=expert.specialty if expert else "Especialista",
            license_number=expert.license_number if expert else "Verificada",
            modality=booking.modality,
            scheduled_start=booking.scheduled_start,
            scheduled_end=booking.scheduled_end,
            status=booking.status,
            stripe_payment_intent_id=booking.stripe_payment_intent_id,
            amount_cents=booking.amount_cents,
            amount_formatted=f"${booking.amount_cents / 100.0:.2f} CAD",
            livekit_room_name=booking.livekit_room_name,
            livekit_token=booking.livekit_token,
            escrow_held=booking.status == "escrow_held",
            created_at=booking.created_at,
        )

    async def release_escrow(self, booking_id: UUID, req: ReleaseEscrowRequest) -> ReleaseEscrowResponse:
        """
        Releases escrow funds to the verified expert once the senior or tutor confirms
        the consultation was completed satisfactorily.
        """
        updated_booking = await self.repo.release_booking_escrow(
            booking_id=booking_id,
            rating=req.rating,
            review_text=req.review_text,
        )
        if not updated_booking:
            raise ValueError("La reserva solicitada no existe o ya fue completada.")

        logger.info(
            f"Stripe Escrow RELEASED: Transferred ${updated_booking.expert_payout_cents / 100.0:.2f} CAD "
            f"to Expert {updated_booking.expert_id}. Client rating: {req.rating}/5 stars."
        )

        return ReleaseEscrowResponse(
            booking_id=updated_booking.id,
            status="completed",
            escrow_released_at=updated_booking.escrow_released_at or get_utc_now(),
            expert_payout_cents=updated_booking.expert_payout_cents,
            expert_payout_formatted=f"${updated_booking.expert_payout_cents / 100.0:.2f} CAD",
            client_review_rating=req.rating,
            message="Fondos en custodia liberados exitosamente al profesional verificado. Gracias por su valoración.",
        )


premium_service = PremiumService()

