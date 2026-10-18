import { getFirebaseIdToken } from '@/lib/firebase/client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

async function resolveAuthToken(explicitToken?: string): Promise<string> {
  const token = explicitToken || await getFirebaseIdToken();
  if (!token) throw new Error('Sign in is required to submit code.');
  return token;
}

export interface SubmissionPayload {
  challenge_id: number;
  code: string;
  language: string;
}

export interface SubmissionResultDetail {
  id: number;
  test_case_id: number;
  passed: boolean;
  stdout?: string;
  stderr?: string;
  execution_time: number;
  memory_usage: number;
}

export interface EvaluationResult {
  submission_id: string;
  challenge_id: number;
  status: string;
  score: number;
  tests_passed: number;
  total_tests: number;
  execution_time: number;
  memory_usage: number;
  error_message?: string;
  created_at: string;
  results?: SubmissionResultDetail[];
}

export interface SubmissionStatus {
  submission_id: string;
  status: string;
  tests_passed: number;
  total_tests: number;
  score: number;
}

export async function submitCode(
  payload: { challenge_id: number; code: string; language: string },
  token?: string
): Promise<EvaluationResult> {
  const authToken = await resolveAuthToken(token);
  const res = await fetch(`${API_BASE_URL}/api/v1/submissions/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to submit code' }));
    throw new Error(err.detail || 'Submission failed');
  }

  return res.json();
}

export async function getSubmissionStatus(submissionId: string, token?: string): Promise<SubmissionStatus> {
  const authToken = await resolveAuthToken(token);
  const res = await fetch(`${API_BASE_URL}/api/v1/submissions/${submissionId}/status`, {
    headers: authToken ? { 'Authorization': `Bearer ${authToken}` } : {},
  });
  if (!res.ok) {
    throw new Error('Failed to fetch status');
  }
  return res.json();
}

export async function getSubmissionResult(submissionId: string, token?: string): Promise<EvaluationResult> {
  const authToken = await resolveAuthToken(token);
  const res = await fetch(`${API_BASE_URL}/api/v1/submissions/${submissionId}`, {
    headers: authToken ? { 'Authorization': `Bearer ${authToken}` } : {},
  });
  if (!res.ok) {
    throw new Error('Failed to fetch submission details');
  }
  return res.json();
}

export async function getSubmissionHistory(
  challengeId: number,
  token?: string
): Promise<EvaluationResult[]> {
  const authToken = await resolveAuthToken(token);
  const res = await fetch(`${API_BASE_URL}/api/v1/submissions/history/${challengeId}`, {
    headers: {
      'Authorization': `Bearer ${authToken}`,
    },
  });
  if (!res.ok) {
    return [];
  }
  return res.json();
}

export async function pollSubmissionResult(
  submissionId: string,
  onStatusChange?: (status: SubmissionStatus) => void,
  token?: string,
  maxAttempts: number = 30,
  intervalMs: number = 400
): Promise<EvaluationResult> {
  for (let i = 0; i < maxAttempts; i++) {
    const statusData = await getSubmissionStatus(submissionId, token);
    onStatusChange?.(statusData);

    if (['PASSED', 'FAILED', 'COMPILE_ERROR', 'RUNTIME_ERROR', 'TIME_LIMIT_EXCEEDED', 'SYSTEM_ERROR'].includes(statusData.status)) {
      return await getSubmissionResult(submissionId, token);
    }

    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }

  // Final fallback attempt
  return await getSubmissionResult(submissionId, token);
}
