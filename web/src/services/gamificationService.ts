import { getFirebaseIdToken } from '@/lib/firebase/client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

async function resolveAuthToken(explicitToken?: string): Promise<string> {
  if (explicitToken) return explicitToken;
  const token = await getFirebaseIdToken();
  if (!token) throw new Error('Sign in is required to load account data.');
  return token;
}

export interface BackendBadgeDetail {
  id: number;
  slug: string;
  name: string;
  description: string;
  category: 'streak' | 'skills' | 'speed' | 'milestone';
  tier: 'bronze' | 'silver' | 'gold' | 'diamond';
  icon: string;
  xp_reward: number;
  unlocked: boolean;
  unlocked_at?: string | null;
}

export interface UserStatsResponse {
  total_xp: number;
  level: number;
  current_streak: number;
  longest_streak: number;
  total_solved: number;
  easy_solved: number;
  medium_solved: number;
  hard_solved: number;
  badges: BackendBadgeDetail[];
}

export interface BackendCertificateDetail {
  id: string;
  title: string;
  issuer: string;
  issue_date: string;
  verification_code: string;
  credential_url: string;
  skills: string[];
}

/**
 * Fetches user stats including total XP, current rank level, streak days, and problem breakdown.
 */
export async function fetchLiveUserStats(token?: string): Promise<UserStatsResponse> {
  const authToken = await resolveAuthToken(token);
  const res = await fetch(`${API_BASE_URL}/api/v1/gamification/stats`, {
    headers: {
      'Authorization': `Bearer ${authToken}`,
      'Accept': 'application/json',
    },
  });

  if (!res.ok) {
    // Fallback attempt to un-prefixed /stats endpoint
    const fallbackRes = await fetch(`${API_BASE_URL}/api/v1/stats`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Accept': 'application/json',
      },
    });

    if (!fallbackRes.ok) {
      const err = await fallbackRes.json().catch(() => ({ detail: 'Failed to fetch user stats' }));
      throw new Error(err.detail || 'Failed to fetch user stats');
    }
    return fallbackRes.json();
  }

  return res.json();
}

/**
 * Fetches all platform badges along with user unlock statuses.
 */
export async function fetchLiveBadges(token?: string): Promise<BackendBadgeDetail[]> {
  const authToken = await resolveAuthToken(token);
  const res = await fetch(`${API_BASE_URL}/api/v1/gamification/badges`, {
    headers: {
      'Authorization': `Bearer ${authToken}`,
      'Accept': 'application/json',
    },
  });

  if (!res.ok) {
    const fallbackRes = await fetch(`${API_BASE_URL}/api/v1/badges`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Accept': 'application/json',
      },
    });
    if (!fallbackRes.ok) {
      return [];
    }
    return fallbackRes.json();
  }

  return res.json();
}

export interface UserActivityItem {
  id: number;
  activity_type: string;
  title: string;
  description?: string;
  action_label: string;
  created_at: string;
}

export interface UserActivityCreate {
  activity_type: string;
  title: string;
  description?: string;
  action_label: string;
}

export interface POTDCompletionRequest {
  video_id: string;
  problem_number?: string;
  title?: string;
  date_key: string;
  completed: boolean;
}

export interface POTDCompletionDetail {
  video_id: string;
  problem_number?: string;
  date_key: string;
  completed: boolean;
  created_at: string;
}

export interface UserDashboardResponse {
  stats: UserStatsResponse & { hours_learned?: number };
  recent_activity: UserActivityItem[];
  solved_potds: string[];
  hours_learned: number;
}

/**
 * Fetches comprehensive, fully personalized dashboard summary for the authenticated user.
 */
export async function fetchUserDashboard(token?: string): Promise<UserDashboardResponse> {
  const authToken = await resolveAuthToken(token);
  const res = await fetch(`${API_BASE_URL}/api/v1/gamification/dashboard`, {
    headers: {
      'Authorization': `Bearer ${authToken}`,
      'Accept': 'application/json',
    },
  });

  if (!res.ok) {
    const fallbackRes = await fetch(`${API_BASE_URL}/api/v1/dashboard`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Accept': 'application/json',
      },
    });

    if (!fallbackRes.ok) {
      throw new Error('Failed to fetch personalized dashboard');
    }
    return fallbackRes.json();
  }

  return res.json();
}

/**
 * Fetches recent audit activities strictly for the authenticated user.
 */
export async function fetchUserActivities(limit = 10, token?: string): Promise<UserActivityItem[]> {
  const authToken = await resolveAuthToken(token);
  const res = await fetch(`${API_BASE_URL}/api/v1/gamification/activity?limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${authToken}`,
      'Accept': 'application/json',
    },
  });

  if (!res.ok) {
    return [];
  }
  return res.json();
}

/**
 * Logs an activity record (e.g. video watched, problem solved) for the authenticated user.
 */
export async function recordUserActivity(
  activity: UserActivityCreate,
  token?: string
): Promise<UserActivityItem | null> {
  try {
    const authToken = await resolveAuthToken(token);
    const res = await fetch(`${API_BASE_URL}/api/v1/gamification/activity`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(activity),
    });

    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

/**
 * Fetches solved POTDs strictly for the authenticated user.
 */
export async function fetchUserPOTDs(token?: string): Promise<POTDCompletionDetail[]> {
  try {
    const authToken = await resolveAuthToken(token);
    const res = await fetch(`${API_BASE_URL}/api/v1/gamification/potd`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Accept': 'application/json',
      },
    });

    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

/**
 * Toggles a POTD completion state for the authenticated user in the backend database.
 */
export async function togglePOTDCompletion(
  req: POTDCompletionRequest,
  token?: string
): Promise<UserDashboardResponse | null> {
  try {
    const authToken = await resolveAuthToken(token);
    const res = await fetch(`${API_BASE_URL}/api/v1/gamification/potd`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(req),
    });

    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

/**
 * Fetches verifiable certificates earned by completing academy courses.
 */
export async function fetchLiveCertificates(token?: string): Promise<BackendCertificateDetail[]> {
  const authToken = await resolveAuthToken(token);
  const res = await fetch(`${API_BASE_URL}/api/v1/gamification/certificates`, {
    headers: {
      'Authorization': `Bearer ${authToken}`,
      'Accept': 'application/json',
    },
  });

  if (!res.ok) {
    const fallbackRes = await fetch(`${API_BASE_URL}/api/v1/certificates`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Accept': 'application/json',
      },
    });
    if (!fallbackRes.ok) {
      return [];
    }
    return fallbackRes.json();
  }

  return res.json();
}

