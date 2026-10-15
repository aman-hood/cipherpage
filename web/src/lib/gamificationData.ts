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
    unlocked: true,
    unlockedAt: 'August 1, 2026',
    progress: { current: 1, max: 1 },
  },
  {
    id: 'streak-7',
    name: 'Streak Warrior',
    description: 'Maintained a 7-day daily LeetCode POTD solving streak.',
    category: 'streak',
    tier: 'silver',
    icon: '🔥',
    unlocked: true,
    unlockedAt: 'August 7, 2026',
    progress: { current: 7, max: 7 },
  },
  {
    id: 'minimax-maestro',
    name: 'Minimax Maestro',
    description: 'Solved Game Theory & Minimax challenges (#486 and #877).',
    category: 'skills',
    tier: 'gold',
    icon: '👑',
    unlocked: true,
    unlockedAt: 'August 2, 2026',
    progress: { current: 2, max: 2 },
  },
  {
    id: 'ten-out-of-ten',
    name: 'Flawless Execution',
    description: 'Achieved 100% on all 10 testcases on your very first submission attempt.',
    category: 'speed',
    tier: 'silver',
    icon: '⚡',
    unlocked: true,
    unlockedAt: 'August 3, 2026',
    progress: { current: 1, max: 1 },
  },
  {
    id: 'dp-connoisseur',
    name: 'DP Connoisseur',
    description: 'Solve 5 Dynamic Programming challenges with optimal memoization.',
    category: 'skills',
    tier: 'gold',
    icon: '🧠',
    unlocked: false,
    progress: { current: 3, max: 5 },
  },
  {
    id: 'graph-explorer',
    name: 'Graph Explorer',
    description: 'Traverse multi-source BFS / Dijkstra in Safest Path #2812 and #3286.',
    category: 'skills',
    tier: 'gold',
    icon: '🌐',
    unlocked: true,
    unlockedAt: 'July 2, 2026',
    progress: { current: 2, max: 2 },
  },
  {
    id: 'streak-30',
    name: 'Monthly Legend',
    description: 'Complete all 30 POTD problems in a monthly playlist series.',
    category: 'streak',
    tier: 'diamond',
    icon: '💎',
    unlocked: false,
    progress: { current: 12, max: 30 },
  },
  {
    id: 'polyglot',
    name: 'Code Polyglot',
    description: 'Submit passing solutions in 3 different programming languages.',
    category: 'milestone',
    tier: 'silver',
    icon: '🚀',
    unlocked: false,
    progress: { current: 2, max: 3 },
  },
];

export const INITIAL_SKILLS: SkillMastery[] = [
  {
    name: 'Dynamic Programming & Memoization',
    level: 4,
    progressPercent: 82,
    solvedCount: 14,
    totalCount: 18,
    color: 'from-cyan-500 to-blue-500',
  },
  {
    name: 'Game Theory & Minimax Optimization',
    level: 5,
    progressPercent: 92,
    solvedCount: 6,
    totalCount: 7,
    color: 'from-purple-500 to-pink-500',
  },
  {
    name: 'Graph Traversal (BFS / Dijkstra)',
    level: 3,
    progressPercent: 68,
    solvedCount: 8,
    totalCount: 12,
    color: 'from-emerald-500 to-teal-500',
  },
  {
    name: 'Sliding Window & Two Pointers',
    level: 4,
    progressPercent: 88,
    solvedCount: 11,
    totalCount: 13,
    color: 'from-amber-500 to-orange-500',
  },
  {
    name: 'Bit Manipulation & Math',
    level: 2,
    progressPercent: 54,
    solvedCount: 5,
    totalCount: 10,
    color: 'from-rose-500 to-red-500',
  },
];

export const INITIAL_CERTIFICATES: Certificate[] = [
  {
    id: 'cert-algo-2026',
    title: 'Algorithmic Mastery: Dynamic Programming & Game Theory',
    issuer: 'CipherPage LAG Academy',
    issueDate: 'August 10, 2026',
    verificationCode: 'CP-LAG-2026-DP991',
    credentialUrl: 'https://verify.cipherpage.com/cert/CP-LAG-2026-DP991',
    skills: ['Dynamic Programming', 'Game Theory', 'State Compression', 'Minimax'],
  },
  {
    id: 'cert-potd-streak',
    title: 'LeetCode POTD Champion: July 2026 Series',
    issuer: 'CipherPage LAG Academy',
    issueDate: 'July 31, 2026',
    verificationCode: 'CP-LAG-2026-POTD7',
    credentialUrl: 'https://verify.cipherpage.com/cert/CP-LAG-2026-POTD7',
    skills: ['Daily Problem Solving', 'Graph Algorithms', 'Grid Traversal', 'Optimization'],
  },
];

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
 * Loads or initializes user progress data, factoring in solved problems from localStorage.
 */
export function getUserProgress(): UserProgressData {
  let solvedIds: string[] = [];
  try {
    const saved = localStorage.getItem('cipherpage_solved_potds');
    if (saved) {
      solvedIds = JSON.parse(saved);
    }
  } catch (e) {}

  // Base XP: 50 XP per solved problem + base XP
  const baseSolvedCount = Math.max(solvedIds.length, 6);
  const totalXp = 850 + baseSolvedCount * 50;
  const levelInfo = calculateLevel(totalXp);

  return {
    totalXp,
    level: levelInfo.level,
    levelTitle: levelInfo.title,
    currentStreak: 14,
    longestStreak: 21,
    totalSolved: baseSolvedCount,
    totalEasySolved: Math.ceil(baseSolvedCount * 0.35),
    totalMediumSolved: Math.ceil(baseSolvedCount * 0.5),
    totalHardSolved: Math.max(1, Math.floor(baseSolvedCount * 0.15)),
    rankPercentile: 94.5,
    skills: INITIAL_SKILLS,
    badges: INITIAL_BADGES,
    certificates: INITIAL_CERTIFICATES,
  };
}
