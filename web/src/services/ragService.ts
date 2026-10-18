import { getFirebaseIdToken } from '@/lib/firebase/client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

async function resolveAuthToken(explicitToken?: string): Promise<string> {
  const token = explicitToken || await getFirebaseIdToken();
  if (!token) throw new Error('Sign in is required to access course materials.');
  return token;
}

export interface Citation {
  document_id: number;
  document_title: string;
  section_title: string;
  page_number?: number;
  excerpt: string;
}

export interface RAGQueryPayload {
  question: string;
  course_id?: number;
}

export interface RAGQueryResponse {
  question: string;
  answer: string;
  citations: Citation[];
  sources_found: boolean;
  confidence: number;
}

export interface DocumentSummary {
  id: number;
  title: string;
  course_id?: number;
  status: string;
  chunks_count: number;
  created_at: string;
}

export async function askLearningAssistant(
  payload: RAGQueryPayload,
  token?: string
): Promise<RAGQueryResponse> {
  const authToken = await resolveAuthToken(token);
  const res = await fetch(`${API_BASE_URL}/api/v1/ai/learning-assistant`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`,
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to consult Learning Assistant' }));
    throw new Error(err.detail || 'Learning Assistant request failed');
  }

  return res.json();
}

export async function fetchCourseDocuments(
  courseId?: number,
  token?: string
): Promise<DocumentSummary[]> {
  const authToken = await resolveAuthToken(token);
  const url = courseId 
    ? `${API_BASE_URL}/api/v1/ai/documents?course_id=${courseId}`
    : `${API_BASE_URL}/api/v1/ai/documents`;

  const res = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${authToken}`,
    },
  });

  if (!res.ok) {
    return [];
  }

  return res.json();
}
