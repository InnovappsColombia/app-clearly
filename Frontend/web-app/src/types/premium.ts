/**
 * CLEARLY — Premium & Escrow Types
 * Matches FastAPI Backend v1 schemas and entities for human-in-the-loop escalation.
 */

export type EscrowStatus = "pending_payment" | "hold_in_escrow" | "released" | "disputed" | "refunded";

export interface ExpertProfile {
  id: string;
  user_id: string;
  full_name: string;
  specialty: string;
  license_number: string;
  id_verification_status: "verified" | "pending" | "suspended";
  hourly_rate_cents: number;
  bio_plain_text: string;
  languages_spoken: string[];
  service_modalities: string[];
  average_rating: number;
  total_reviews: number;
  is_available: boolean;
}

export interface ExpertMatchResult {
  matched_expert: ExpertProfile;
  detected_specialty: string;
  match_score: number;
  plain_language_reasoning: string;
  alternative_experts: ExpertProfile[];
}

export interface PremiumBooking {
  id: string;
  senior_id: string;
  expert_id: string;
  expert_name: string;
  specialty: string;
  hourly_rate_cents: number;
  platform_fee_cents: number;
  expert_escrow_cents: number;
  currency: string;
  status: EscrowStatus;
  paid_by_user_id: string;
  paid_by_role: "senior" | "tutor";
  stripe_payment_intent_id?: string;
  livekit_room_name: string;
  scheduled_at: string;
  completed_at?: string;
  client_rating?: number;
  client_feedback?: string;
}

export interface LiveKitRoomDetails {
  room_name: string;
  token: string;
  livekit_url: string;
  participant_identity: string;
  participant_name: string;
  caption_font_scale: number;
  enable_realtime_transcription: boolean;
}
