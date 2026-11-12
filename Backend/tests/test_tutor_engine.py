"""
CLEARLY — Test Suite for Tutor Hub & Handshake Engine
Validates Ephemeral Pairing Codes, PASETO Attenuated Tokens, Real-time Collaborative Checklists,
and Silent Duress PIN Protection (FMEA FM-04).
Runs with deterministic synchronous async execution (safe across all sandboxes).
"""

from datetime import date, timedelta
import unittest
import sys
from pathlib import Path
from uuid import UUID

# Add Backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api.v1.tutors import (
    create_pairing_code,
    pair_tutor,
    get_tutor_dashboard,
    toggle_checklist_action,
    trigger_duress_pin,
)
from app.schemas.tutor import (
    ChecklistToggleRequest,
    DuressTriggerRequest,
    PairingCodeRequest,
    PairTutorRequest,
)
from app.db.repository import repository
from tests.async_helper import run_sync

ELENA_ID = UUID("11111111-1111-1111-1111-111111111111")
CARLOS_ID = UUID("22222222-2222-2222-2222-222222222222")


class TestTutorEngine(unittest.TestCase):
    def setUp(self):
        repository._load_seed_data()
    def test_ephemeral_pairing_code_generation(self):
        """Tests generating a 6-digit ephemeral pairing code and Curve25519 QR handshake payload."""
        req = PairingCodeRequest(senior_id=ELENA_ID)
        data = run_sync(create_pairing_code(req))

        self.assertEqual(len(data.pairing_code), 6)
        self.assertTrue(data.pairing_code.isdigit())
        self.assertEqual(data.senior_id, ELENA_ID)
        self.assertEqual(data.senior_name, "Elena Pabla")
        self.assertIn("clearly://handshake?code=", data.qr_payload)
        self.assertIn("&key=", data.qr_payload)

    def test_tutor_handshake_and_paseto_capability_token(self):
        """
        Tests tutor redeeming the pairing code.
        Validates issuance of attenuated capability token (FMEA Spec 4.2).
        """
        # 1. Senior generates pairing code
        gen_req = PairingCodeRequest(senior_id=ELENA_ID)
        gen_data = run_sync(create_pairing_code(gen_req))
        code = gen_data.pairing_code

        # 2. Tutor Carlos redeems the code
        pair_req = PairTutorRequest(pairing_code=code, tutor_id=CARLOS_ID)
        pair_data = run_sync(pair_tutor(pair_req))

        self.assertEqual(pair_data.status, "paired")
        self.assertEqual(pair_data.senior_profile["full_name"], "Elena Pabla")
        self.assertTrue(pair_data.granted_permissions["can_view_critical_alerts"])

        # Verify attenuated capability token restricts permissions
        token = pair_data.capability_token
        self.assertIn("pasv4.public", token)
        self.assertIn("action = read_only", token)
        self.assertIn("prohibit_actions = [financial_transfer", token)

    def test_tutor_hub_dashboard(self):
        """Tests Tutor Hub aggregated dashboard for Carlos supervising Elena."""
        dash = run_sync(get_tutor_dashboard(senior_id=ELENA_ID, tutor_id=CARLOS_ID))

        self.assertEqual(dash.senior["full_name"], "Elena Pabla")
        self.assertFalse(dash.is_quarantine_mode)

        # Check critical deadlines & collaborative checklist
        checklist = dash.collaborative_checklist
        self.assertGreater(len(checklist), 0)
        self.assertIsNotNone(checklist[0].task_description)
        self.assertIsInstance(checklist[0].is_completed, bool)

    def test_collaborative_checklist_toggle(self):
        """Tests checking and unchecking a task in the collaborative checklist."""
        dash = run_sync(get_tutor_dashboard(senior_id=ELENA_ID, tutor_id=CARLOS_ID))
        checklist = dash.collaborative_checklist
        self.assertTrue(len(checklist) > 0)

        action_id = checklist[0].id
        initial_status = checklist[0].is_completed

        # Toggle the action
        toggle_req = ChecklistToggleRequest(completed_by_user_id=CARLOS_ID)
        updated = run_sync(toggle_checklist_action(action_id=action_id, req=toggle_req))

        self.assertEqual(updated.is_completed, not initial_status)
        self.assertEqual(updated.completed_by_user_id, CARLOS_ID)
        self.assertEqual(updated.completed_by_name, "Carlos Pabla")
        self.assertIsNotNone(updated.completed_at)

    def test_duress_pin_silent_protection_fm04(self):
        """
        FMEA FM-04 Benchmark: Coercion / Elder Abuse Protection.
        When Senior enters Duress PIN:
          1. UI returns identical innocent confirmation.
          2. Backend quietly activates quarantine mode.
          3. Dashboard hides sensitive documents from tutor view.
        """
        duress_req = DuressTriggerRequest(senior_id=ELENA_ID, entered_pin="9876")
        res = run_sync(trigger_duress_pin(duress_req))
        self.assertEqual(res.status, "success")
        self.assertIn("actualizadas correctamente", res.message)

        # Check Tutor Hub dashboard now returns quarantined neutral view
        dash_data = run_sync(get_tutor_dashboard(senior_id=ELENA_ID, tutor_id=CARLOS_ID))
        self.assertTrue(dash_data.is_quarantine_mode)
        self.assertEqual(len(dash_data.critical_deadlines), 0)
        self.assertEqual(len(dash_data.recent_documents), 0)


if __name__ == "__main__":
    unittest.main()
