"""
CLEARLY — Test Suite for Stripe Connect Escrow & Premium Bookings (Sprint 4)
Validates escrow creation, delegate payer support (Tutor paying for Senior),
fee splits (15% platform / 85% payout), and escrow release upon session completion.
"""

from datetime import datetime, timedelta, timezone
import unittest
import sys
from pathlib import Path
from uuid import UUID

# Add Backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api.v1.premium import create_booking, get_booking_details, release_escrow
from app.db.repository import repository
from app.schemas.premium import CreateBookingRequest, ReleaseEscrowRequest
from tests.async_helper import run_sync

ELENA_ID = UUID("11111111-1111-1111-1111-111111111111")
CARLOS_ID = UUID("22222222-2222-2222-2222-222222222222")
DAVID_EXPERT_ID = UUID("66666666-6666-6666-6666-666666666666")


class TestPremiumEscrow(unittest.TestCase):
    def setUp(self):
        repository._load_seed_data()

    def test_create_booking_with_stripe_escrow_hold(self):
        """Validates booking creation with Stripe Escrow hold and delegate payment by Tutor."""
        now = datetime.now(timezone.utc)
        req = CreateBookingRequest(
            expert_id=DAVID_EXPERT_ID,
            client_senior_id=ELENA_ID,
            requested_by_user_id=CARLOS_ID,  # Carlos pays on behalf of his mother
            modality="virtual",
            scheduled_start=now + timedelta(days=2),
        )

        booking = run_sync(create_booking(req))

        self.assertEqual(booking.status, "escrow_held")
        self.assertTrue(booking.escrow_held)
        self.assertEqual(booking.client_name, "Elena Pabla")
        self.assertEqual(booking.requested_by_name, "Carlos Pabla")
        self.assertEqual(booking.expert_name, "David Mendoza, RCIC")
        self.assertEqual(booking.amount_cents, 4500)
        self.assertIn("clearly-consultation-", booking.livekit_room_name)
        self.assertIsNotNone(booking.livekit_token)

    def test_escrow_release_lifecycle(self):
        """
        Validates the full escrow lifecycle:
        1. Booking placed with funds in escrow hold.
        2. Consultation completed.
        3. Escrow released to expert with client 5-star review.
        4. Expert rating and review count updated.
        """
        now = datetime.now(timezone.utc)
        # 1. Place booking
        create_req = CreateBookingRequest(
            expert_id=DAVID_EXPERT_ID,
            client_senior_id=ELENA_ID,
            requested_by_user_id=CARLOS_ID,
            modality="virtual",
            scheduled_start=now + timedelta(days=1),
        )
        booking = run_sync(create_booking(create_req))
        self.assertEqual(booking.status, "escrow_held")

        initial_expert = run_sync(repository.get_expert_profile(DAVID_EXPERT_ID))
        initial_reviews = initial_expert.total_reviews

        # 2. Release escrow
        release_req = ReleaseEscrowRequest(
            rating=5,
            review_text="Excelente orientación. David nos explicó paso a paso la carta de IRCC con mucha paciencia.",
        )
        release_res = run_sync(release_escrow(booking.id, release_req))

        self.assertEqual(release_res.status, "completed")
        self.assertEqual(release_res.client_review_rating, 5)
        self.assertEqual(release_res.expert_payout_cents, 3825)  # 85% of $45.00 = $38.25 CAD
        self.assertEqual(release_res.expert_payout_formatted, "$38.25 CAD")

        # 3. Verify booking detail status updated
        updated_detail = run_sync(get_booking_details(booking.id))
        self.assertEqual(updated_detail.status, "completed")
        self.assertFalse(updated_detail.escrow_held)

        # 4. Verify expert total reviews incremented
        updated_expert = run_sync(repository.get_expert_profile(DAVID_EXPERT_ID))
        self.assertEqual(updated_expert.total_reviews, initial_reviews + 1)


if __name__ == "__main__":
    unittest.main()

