import { createClient } from '@/lib/supabase/client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export interface BackendChallenge {
  id: number;
  title: string;
  slug: string;
  description?: string;
  difficulty: string;
  category: string;
  time_limit?: number;
  memory_limit?: number;
  starter_code?: Record<string, string>;
  constraints?: string[];
  examples?: Array<{ input: string; output: string; explanation?: string }>;
  hints?: string[];
  is_active?: boolean;
}

// In-memory cache of backend challenges
let cachedChallenges: BackendChallenge[] | null = null;
let fetchPromise: Promise<BackendChallenge[]> | null = null;

// Fallback hardcoded dictionary for instant synchronous resolution
const KNOWN_ID_MAP: Record<string, number> = {
  '486': 1,
  'predict-the-winner': 1,
  '1': 2,
  'two-sum': 2,
};

function normalize(str: string): string {
  return str.toLowerCase().replace(/[^a-z0-9]/g, '');
}

/**
 * Fetches all challenges from the backend API.
 */
export async function fetchBackendChallenges(token?: string, forceRefresh = false): Promise<BackendChallenge[]> {
  if (cachedChallenges && !forceRefresh) {
    return cachedChallenges;
  }

  if (fetchPromise && !forceRefresh) {
    return fetchPromise;
  }

  fetchPromise = (async () => {
    try {
      const headers: Record<string, string> = { 'Accept': 'application/json' };
      let authToken = token;
      if (!authToken) {
        try {
          const supabase = createClient();
          const { data: { session } } = await supabase.auth.getSession();
          if (session?.access_token) authToken = session.access_token;
        } catch (e) {}
      }
      if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
      }

      const res = await fetch(`${API_BASE_URL}/api/v1/challenges/`, { headers });
      if (!res.ok) {
        console.warn('Failed to fetch challenges from backend:', res.statusText);
        return cachedChallenges || [];
      }
      const data = await res.json();
      cachedChallenges = data;
      return data;
    } catch (err) {
      console.warn('Error fetching backend challenges:', err);
      return cachedChallenges || [];
    } finally {
      fetchPromise = null;
    }
  })();

  return fetchPromise;
}

/**
 * Synchronous resolver for instant initial state before network returns.
 */
export function getKnownBackendChallengeId(problemNumberOrId: string | number, title?: string): number {
  const strId = String(problemNumberOrId).trim();
  if (KNOWN_ID_MAP[strId]) return KNOWN_ID_MAP[strId];

  if (title) {
    const normTitle = normalize(title);
    if (normTitle.includes('predictthewinner')) return 1;
    if (normTitle.includes('twosum')) return 2;
  }

  const num = parseInt(strId, 10);
  // If already a small integer (1, 2, ... <= 50), it is likely a direct sequence ID
  if (!isNaN(num) && num > 0 && num <= 50) {
    return num;
  }

  // Fallback default: Predict the Winner is Challenge 1
  return 1;
}

/**
 * Dynamic asynchronous resolver querying live backend challenges.
 */
export async function resolveBackendChallengeId(
  problemNumberOrId: string | number,
  title?: string,
  token?: string
): Promise<number> {
  const challenges = await fetchBackendChallenges(token);

  if (challenges && challenges.length > 0) {
    const strId = String(problemNumberOrId).trim();
    const numId = parseInt(strId, 10);

    // 1. Direct ID match if numeric and matches existing DB ID
    const exactIdMatch = challenges.find((c) => c.id === numId);
    if (exactIdMatch && numId <= 50) {
      return exactIdMatch.id;
    }

    // 2. Title match
    if (title) {
      const normTitle = normalize(title);
      const titleMatch = challenges.find((c) => {
        const cNorm = normalize(c.title);
        return cNorm === normTitle || cNorm.includes(normTitle) || normTitle.includes(cNorm);
      });
      if (titleMatch) return titleMatch.id;
    }

    // 3. Slug match
    const slugMatch = challenges.find((c) => {
      const cSlug = normalize(c.slug);
      return cSlug === normalize(strId) || (title && cSlug === normalize(title));
    });
    if (slugMatch) return slugMatch.id;
  }

  // Fallback to known mapping
  return getKnownBackendChallengeId(problemNumberOrId, title);
}
