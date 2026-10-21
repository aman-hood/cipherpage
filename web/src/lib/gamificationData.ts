export interface Badge {
  id: string;
  name: string;
  description: string;
  category: 'streak' | 'skills' | 'speed' | 'milestone';
  tier: 'bronze' | 'silver' | 'gold' | 'diamond';
  icon: string;
  unlocked: boolean;
  unlockedAt?: string;
  progress?: { current: number; max: number };
}

export interface SkillMastery {
  name: string;
  level: number;
  progressPercent: number;
  solvedCount: number;
  totalCount: number;
  color: string;
}

export interface Certificate {
  id: string;
  title: string;
  issuer: string;
  issueDate: string;
  verificationCode: string;
  credentialUrl: string;
  skills: string[];
}

export interface UserProgressData {
  totalXp: number;
  level: number;
  levelTitle: string;
  currentStreak: number;
  longestStreak: number;
  totalSolved: number;
  totalEasySolved: number;
  totalMediumSolved: number;
  totalHardSolved: number;
  rankPercentile: number;
  skills: SkillMastery[];
  badges: Badge[];
  certificates: Certificate[];
}

export const INITIAL_BADGES: Badge[] = [
  {
    id: 'first-blood',
    name: 'First Blood',
    description: 'Passed your first 10-testcase problem in the Monaco editor.',
    category: 'milestone',
    tier: 'bronze',
    icon: '⚔️',
    unlocked: false,
    progress: { current: 0, max: 1 },
  },
  {
    id: 'streak-7',
    name: 'Streak Warrior',
    description: 'Maintain a 7-day daily LeetCode POTD solving streak.',
    category: 'streak',
    tier: 'silver',
    icon: '🔥',
    unlocked: false,
    progress: { current: 0, max: 7 },
  },
  {
    id: 'minimax-maestro',
    name: 'Minimax Maestro',
    description: 'Solve Game Theory & Minimax challenges (#486 and #877).',
    category: 'skills',
    tier: 'gold',
    icon: '👑',
    unlocked: false,
    progress: { current: 0, max: 2 },
  },
  {
    id: 'ten-out-of-ten',
    name: 'Flawless Execution',
    description: 'Achieve 100% on all 10 testcases on your very first submission attempt.',
    category: 'speed',
    tier: 'silver',
    icon: '⚡',
    unlocked: false,
    progress: { current: 0, max: 1 },
  },
  {
    id: 'dp-connoisseur',
    name: 'DP Connoisseur',
    description: 'Solve 5 Dynamic Programming challenges with optimal memoization.',
    category: 'skills',
    tier: 'gold',
    icon: '🧠',
    unlocked: false,
    progress: { current: 0, max: 5 },
  },
  {
    id: 'graph-explorer',
    name: 'Graph Explorer',
    description: 'Traverse multi-source BFS / Dijkstra in Safest Path #2812 and #3286.',
    category: 'skills',
    tier: 'gold',
    icon: '🌐',
    unlocked: false,
    progress: { current: 0, max: 2 },
  },
  {
    id: 'streak-30',
    name: 'Monthly Legend',
    description: 'Complete all 30 POTD problems in a monthly playlist series.',
    category: 'streak',
    tier: 'diamond',
    icon: '💎',
    unlocked: false,
    progress: { current: 0, max: 30 },
  },
  {
    id: 'polyglot',
    name: 'Code Polyglot',
    description: 'Submit passing solutions in 3 different programming languages.',
    category: 'milestone',
    tier: 'silver',
    icon: '🚀',
    unlocked: false,
    progress: { current: 0, max: 3 },
  },
];

export const INITIAL_SKILLS: SkillMastery[] = [
  {
    name: 'Dynamic Programming & Memoization',
    level: 1,
    progressPercent: 0,
    solvedCount: 0,
    totalCount: 18,
    color: 'from-cyan-500 to-blue-500',
  },
  {
    name: 'Game Theory & Minimax Optimization',
    level: 1,
    progressPercent: 0,
    solvedCount: 0,
    totalCount: 7,
    color: 'from-purple-500 to-pink-500',
  },
  {
    name: 'Graph Traversal (BFS / Dijkstra)',
    level: 1,
    progressPercent: 0,
    solvedCount: 0,
    totalCount: 12,
    color: 'from-emerald-500 to-teal-500',
  },
  {
    name: 'Sliding Window & Two Pointers',
    level: 1,
    progressPercent: 0,
    solvedCount: 0,
    totalCount: 13,
    color: 'from-amber-500 to-orange-500',
  },
  {
    name: 'Bit Manipulation & Math',
    level: 1,
    progressPercent: 0,
    solvedCount: 0,
    totalCount: 10,
    color: 'from-rose-500 to-red-500',
  },
];

export const INITIAL_CERTIFICATES: Certificate[] = [];

/**
 * Calculates user's level and title based on solved problems and total XP.
 */
export function calculateLevel(totalXp: number): { level: number; title: string; nextLevelXp: number; currentLevelFloor: number } {
  if (totalXp < 300) return { level: 1, title: 'Novice Coder', nextLevelXp: 300, currentLevelFloor: 0 };
  if (totalXp < 700) return { level: 2, title: 'Syntax Apprentice', nextLevelXp: 700, currentLevelFloor: 300 };
  if (totalXp < 1200) return { level: 3, title: 'Problem Solver', nextLevelXp: 1200, currentLevelFloor: 700 };
  if (totalXp < 2000) return { level: 4, title: 'Algorithm Specialist', nextLevelXp: 2000, currentLevelFloor: 1200 };
  return { level: 5, title: 'Code Grandmaster', nextLevelXp: 3000, currentLevelFloor: 2000 };
}

/**
 * Loads or initializes user progress data, factoring in solved problems from user-scoped localStorage.
 */
export function getUserProgress(userId?: string): UserProgressData {
  let solvedIds: string[] = [];
  let streak = 0;
  const storagePrefix = userId ? `cipherpage_${userId}` : 'cipherpage_guest';

  if (typeof window !== 'undefined') {
    try {
      const saved = localStorage.getItem(`${storagePrefix}_solved_potds`);
      if (saved) {
        solvedIds = JSON.parse(saved);
      }
      const savedStreak = localStorage.getItem(`${storagePrefix}_current_streak`);
      if (savedStreak) {
        streak = parseInt(savedStreak, 10) || 0;
      }
    } catch (e) {}
  }

  const solvedCount = solvedIds.length;
  const totalXp = solvedCount * 50;
  const levelInfo = calculateLevel(totalXp);

  return {
    totalXp,
    level: levelInfo.level,
    levelTitle: levelInfo.title,
    currentStreak: streak,
    longestStreak: streak,
    totalSolved: solvedCount,
    totalEasySolved: Math.ceil(solvedCount * 0.35),
    totalMediumSolved: Math.ceil(solvedCount * 0.5),
    totalHardSolved: Math.max(0, Math.floor(solvedCount * 0.15)),
    rankPercentile: solvedCount > 0 ? Math.min(99, 50 + solvedCount * 5) : 0,
    skills: INITIAL_SKILLS.map(s => ({
      ...s,
      solvedCount: Math.min(s.totalCount, Math.floor(solvedCount / 5)),
      progressPercent: Math.min(100, Math.round((Math.floor(solvedCount / 5) / s.totalCount) * 100)),
    })),
    badges: INITIAL_BADGES,
    certificates: INITIAL_CERTIFICATES,
  };
}

