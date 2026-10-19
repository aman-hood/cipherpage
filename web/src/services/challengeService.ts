import { getFirebaseIdToken } from '@/lib/firebase/client';

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
let challengesCachedAt = 0;
const CHALLENGES_CACHE_TTL_MS = 15_000;

function normalize(str: string): string {
  return str.toLowerCase().replace(/[^a-z0-9]/g, '');
}

/**
 * Fetches all challenges from the backend API.
 */
export async function fetchBackendChallenges(token?: string, forceRefresh = false): Promise<BackendChallenge[]> {
  if (cachedChallenges !== null && !forceRefresh && Date.now() - challengesCachedAt < CHALLENGES_CACHE_TTL_MS) {
    return cachedChallenges;
  }

  if (fetchPromise && !forceRefresh) {
    return fetchPromise;
  }

  fetchPromise = (async () => {
    try {
      const headers: Record<string, string> = { 'Accept': 'application/json' };
      const authToken = token || await getFirebaseIdToken();
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
      challengesCachedAt = Date.now();
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
 * Dynamic asynchronous resolver querying live backend challenges.
 */
export async function resolveBackendChallengeId(
  problemNumberOrId: string | number,
  title?: string,
  token?: string
): Promise<number | null> {
  const challenges = await fetchBackendChallenges(token);

  if (challenges && challenges.length > 0) {
    const strId = String(problemNumberOrId).trim();
    const normalizedTitle = title ? normalize(title) : '';

    // Match user-facing problem identity before an internal numeric database ID.
    if (title) {
      const titleMatch = challenges.find((c) => {
        const normalizedChallengeTitle = normalize(c.title);
        return normalizedChallengeTitle === normalizedTitle ||
          normalizedTitle.includes(normalizedChallengeTitle);
      });
      if (titleMatch) return titleMatch.id;
    }

    // Slugs may include a problem number in addition to the title.
    const slugMatch = challenges.find((c) => {
      const normalizedSlug = normalize(c.slug);
      return normalizedSlug === normalize(strId) ||
        (normalizedTitle.length > 0 && (
          normalizedSlug.includes(normalizedTitle) || normalizedTitle.includes(normalizedSlug)
        ));
    });
    if (slugMatch) return slugMatch.id;

    // Accept a raw internal ID only when no display identity was provided.
    if (!title) {
      const numId = Number(strId);
      const exactIdMatch = challenges.find((c) => c.id === numId);
      if (exactIdMatch) return exactIdMatch.id;
    }
  }

  return null;
}
