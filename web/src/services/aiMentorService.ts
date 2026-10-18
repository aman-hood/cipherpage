import { getFirebaseIdToken } from '@/lib/firebase/client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

async function resolveAuthToken(explicitToken?: string): Promise<string> {
  const token = explicitToken || await getFirebaseIdToken();
  if (!token) throw new Error('Sign in is required to use the AI mentor.');
  return token;
}

export type AIMentorMode = 'HINT' | 'DEBUG' | 'EXPLAIN' | 'COMPLEXITY';

export interface AIMentorRequestPayload {
  challenge_id?: number;
  mode: AIMentorMode;
  code: string;
  language: string;
  error_output?: string;
  request_full_solution?: boolean;
}

export interface AIMentorResponseData {
  mode: string;
  content: string;
  tokens_used: number;
  disclaimer: string;
  remaining_quota: number;
}

export interface AIQuotaData {
  daily_requests_used: number;
  daily_limit: number;
  remaining_quota: number;
}

export async function fetchAIMentorGuidance(
  payload: AIMentorRequestPayload,
  token?: string
): Promise<AIMentorResponseData> {
  const authToken = await resolveAuthToken(token);
  const res = await fetch(`${API_BASE_URL}/api/v1/ai/mentor`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to consult AI Mentor' }));
    throw new Error(err.detail || 'AI Mentor request failed');
  }

  return res.json();
}

export async function fetchAIQuota(token?: string): Promise<AIQuotaData> {
  const authToken = await resolveAuthToken(token);
  const res = await fetch(`${API_BASE_URL}/api/v1/ai/quota`, {
    headers: {
      'Authorization': `Bearer ${authToken}`,
    },
  });

  if (!res.ok) {
    return { daily_requests_used: 0, daily_limit: 50, remaining_quota: 50 };
  }

  return res.json();
}
