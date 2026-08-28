/**
 * Typed OpenAPI Interfaces for Hikmah API.
 */

export interface HealthResponse {
  status: string;
  version: string;
  foundation: string;
  timestamp: string;
  environment: string;
}

export interface ExpertSeat {
  id: string;
  name: string;
  display_name: string;
  description: string;
  mattermost_user_id: string;
  mattermost_username: string;
  runtime_type: 'qwenpaw_shared' | 'qwenpaw_personal' | 'agentscope_sidecar';
  runtime_agent_id: string;
  runtime_config: Record<string, unknown>;
  owner_user_id?: string | null;
  is_personal: boolean;
  status: 'active' | 'disabled' | 'degraded';
  created_at: string;
  updated_at: string;
}

export interface SidecarRuleProfile {
  id: string;
  channel_id: string;
  channel_name: string;
  explicit_mention_silent: boolean;
  unmentioned_policy: 'silent' | 'single_responder' | 'moderator_only';
  confidence_threshold: number;
  default_responder_seat_id?: string | null;
  require_approval_for_write: boolean;
  require_approval_for_external: boolean;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeCandidate {
  id: string;
  title: string;
  summary: string;
  content: string;
  source_channel_id: string;
  source_thread_id?: string | null;
  source_post_ids: string[];
  proposer_user_id: string;
  status: 'proposed' | 'approved' | 'rejected' | 'revoked';
  scope: 'channel' | 'team';
  reviewer_user_id?: string | null;
  review_notes?: string | null;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface CorrelationRecord {
  id: string;
  trace_id: string;
  channel_id: string;
  thread_id?: string | null;
  post_id: string;
  user_id: string;
  expert_seat_id: string;
  runtime_session_id: string;
  action_type: string;
  tool_name?: string | null;
  approval_status?: string | null;
  duration_ms?: number | null;
  metadata_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}
