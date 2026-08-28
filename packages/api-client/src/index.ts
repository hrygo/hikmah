import {
  HealthResponse,
  ExpertSeat,
  SidecarRuleProfile,
  KnowledgeCandidate,
  CorrelationRecord,
} from './types';

export * from './types';

export class HikmahApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000/api/v1') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.error?.message || `HTTP ${res.status}: ${res.statusText}`);
    }

    return res.json() as Promise<T>;
  }

  // Health
  getHealth(): Promise<HealthResponse> {
    return this.request<HealthResponse>('/health');
  }

  // Expert Seats
  listSeats(isPersonal?: boolean): Promise<ExpertSeat[]> {
    const query = isPersonal !== undefined ? `?is_personal=${isPersonal}` : '';
    return this.request<ExpertSeat[]>(`/seats${query}`);
  }

  getSeat(seatId: string, userId?: string): Promise<ExpertSeat> {
    const query = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
    return this.request<ExpertSeat>(`/seats/${seatId}${query}`);
  }

  // Sidecar Rules
  listRules(): Promise<SidecarRuleProfile[]> {
    return this.request<SidecarRuleProfile[]>('/rules');
  }

  getRuleByChannel(channelId: string): Promise<SidecarRuleProfile> {
    return this.request<SidecarRuleProfile>(`/rules/channel/${channelId}`);
  }

  // Knowledge Candidates
  listKnowledge(status?: string, channelId?: string): Promise<KnowledgeCandidate[]> {
    const params = new URLSearchParams();
    if (status) params.set('status_filter', status);
    if (channelId) params.set('channel_id', channelId);
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request<KnowledgeCandidate[]>(`/knowledge${query}`);
  }

  // Correlation Traces
  listTraces(traceId?: string, channelId?: string): Promise<CorrelationRecord[]> {
    const params = new URLSearchParams();
    if (traceId) params.set('trace_id', traceId);
    if (channelId) params.set('channel_id', channelId);
    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request<CorrelationRecord[]>(`/traces${query}`);
  }
}
