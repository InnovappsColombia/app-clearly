/**
 * CLEARLY — Document & A11y Types
 * Fulfills Sprint 2 frontend contracts and matches FastAPI Backend v1 models.
 */

export type UrgencyLevel = "low" | "medium" | "high" | "critical";

export interface ActionItem {
  id: string;
  document_id: string;
  task_description: string;
  required_document: string | null;
  deadline: string | null;
  is_completed: boolean;
  completed_at: string | null;
  created_at: string;
}

export interface DocumentAnalysisResult {
  id: string;
  user_id: string;
  document_type: string;
  issuing_entity: string;
  plain_summary: string;
  detected_language: string;
  fernandez_huerta_score: number;
  readability_category: string;
  urgency: UrgencyLevel;
  critical_deadline: string | null;
  days_remaining: number | null;
  tutor_alert_triggered: boolean;
  requires_human_expert: boolean;
  actions_required: ActionItem[];
  ambiguities_flagged: string[];
  recommended_questions: string[];
  storage_path?: string;
  file_sha256?: string;
  created_at: string;
  original_extracted_text?: string;
}

export interface ReadabilityAuditResult {
  score: number;
  is_acceptable: boolean;
  category: string;
  reading_level: string;
  num_words: number;
  num_sentences: number;
  total_syllables: number;
  syllables_per_word: number;
  words_per_sentence: number;
  recommendations: string[];
}

export interface CommunityEvent {
  id: string;
  title: string;
  what: string;
  when_where: string;
  cost: string;
  how_to_register: string;
  is_free: boolean;
  is_wheelchair_accessible: boolean;
  is_senior_friendly: boolean;
  transport_tip: string;
  organizer: string;
  date_label: string;
}

