export interface POTDVideo {
  videoId: string;
  title: string;
  url: string;
  problemNumber?: string;
  problemTitle?: string;
  difficulty?: 'Easy' | 'Medium' | 'Hard';
  day: number;
  month: string;
  year: number;
  playlistTitle: string;
  playlistId: string;
}

export interface ChannelPlaylist {
  playlistTitle: string;
  playlistId: string;
  month: string;
  year: number;
  videos: {
    videoId: string;
    title: string;
    url: string;
  }[];
}

export interface ChannelInfo {
  title: string;
  url: string;
  handle: string;
  playlists: ChannelPlaylist[];
}

export const CHANNEL_DATA: ChannelInfo = {
  title: 'CipherPage',
  url: 'https://youtube.com/@cipherpage',
  handle: '@cipherpage',
  playlists: [
    {
      playlistTitle: 'Leetcode August 2026',
      playlistId: 'PLEzi4Fs64RUY',
      month: 'August',
      year: 2026,
      videos: [
        {
          videoId: 'AdG8y5RwzpU',
          title: 'Leetcode 486 | Predict the Winner | Medium | POTD August 1, 2026',
          url: 'https://www.youtube.com/watch?v=AdG8y5RwzpU',
        },
        {
          videoId: 'hRNW-YOEmlA',
          title: 'Leetcode 877 | Stone Game | Medium | POTD August 2, 2026',
          url: 'https://www.youtube.com/watch?v=hRNW-YOEmlA',
        },
        {
          videoId: 'wENy24037dc',
          title: 'Leetcode 1406 | Stone Game III | Hard | POTD August 3, 2026',
          url: 'https://www.youtube.com/watch?v=wENy24037dc',
        },
        {
          videoId: 'urHnY9shvXk',
          title: 'Leetcode 3731 | Find Missing Elements | Easy | POTD August 4, 2026',
          url: 'https://www.youtube.com/watch?v=urHnY9shvXk',
        },
        {
          videoId: 'w9JtDI-M0kk',
          title: 'Leetcode 3310 | Remove Methods From Project | Medium | POTD August 5, 2026',
          url: 'https://www.youtube.com/watch?v=w9JtDI-M0kk',
        },
        {
          videoId: 'ymwTZ4XxxgY',
          title: 'Leetcode 3345 | Smallest Divisible Digit Product I | Easy | POTD August 6, 2026',
          url: 'https://www.youtube.com/watch?v=ymwTZ4XxxgY',
        },
        {
          videoId: 'JSSoUPwsHro',
          title: 'Leetcode 2958 | Length of Longest Subarray With at Most K Frequency | Medium | POTD August 12, 2026',
          url: 'https://www.youtube.com/watch?v=JSSoUPwsHro',
        },
        {
          videoId: '97z3WHbfcSM',
          title: 'Leetcode 3090 | Maximum Length Substring With Two Occurrences | Easy | POTD August 14, 2026',
          url: 'https://www.youtube.com/watch?v=97z3WHbfcSM',
        },
        {
          videoId: '9Bs9UZFdG3U',
          title: 'Leetcode 3702 | Longest Subsequence With Non-Zero Bitwise XOR | Medium | POTD August 15, 2026',
          url: 'https://www.youtube.com/watch?v=9Bs9UZFdG3U',
        },
      ],
    },
    {
      playlistTitle: 'Leetcode July 2026',
      playlistId: 'PLJrqTlGoOkzc',
      month: 'July',
      year: 2026,
      videos: [
        {
          videoId: 'UoxKmaWJNBU',
          title: 'Leetcode 2812 | Find the Safest Path in a Grid | Medium | POTD July 1, 2026',
          url: 'https://www.youtube.com/watch?v=UoxKmaWJNBU',
        },
        {
          videoId: '5hv1sJjHDIo',
          title: 'Leetcode 3286 | Find a Safe Walk Through a Grid | Medium | POTD July 2, 2026',
          url: 'https://www.youtube.com/watch?v=5hv1sJjHDIo',
        },
        {
          videoId: 'mkmp44gYJgY',
          title: 'Leetcode 3620 | Network Recovery Pathways | Hard | POTD July 3, 2026',
          url: 'https://www.youtube.com/watch?v=mkmp44gYJgY',
        },
        {
          videoId: 'a8HrmQwc72Q',
          title: 'Leetcode 2492 | Minimum Score of a Path Between Two Cities | Medium | POTD July 4, 2026',
          url: 'https://www.youtube.com/watch?v=a8HrmQwc72Q',
        },
        {
          videoId: 'E8X_23qc0y0',
          title: 'Leetcode 1301 | Number of Paths with Max Score | Hard | POTD July 5, 2026',
          url: 'https://www.youtube.com/watch?v=E8X_23qc0y0',
        },
        {
          videoId: 'mzuLNQTXNfY',
          title: 'Leetcode 1288 | Remove Covered Intervals | Medium | POTD July 6, 2026',
          url: 'https://www.youtube.com/watch?v=mzuLNQTXNfY',
        },
        {
          videoId: 'gIUElGsg9u8',
          title: 'Leetcode 3754 | Concatenate Non-Zero Digits and Multiply by Sum I | Easy | POTD July 7, 2026',
          url: 'https://www.youtube.com/watch?v=gIUElGsg9u8',
        },
        {
          videoId: '3j0jOEyDVIk',
          title: 'Leetcode 3756 | Concatenate Non-Zero Digits and Multiply by Sum II | Medium | POTD July 8, 2026',
          url: 'https://www.youtube.com/watch?v=3j0jOEyDVIk',
        },
        {
          videoId: '98dMkF02fNc',
          title: 'Leetcode 3532 | Path Existence Queries in a Graph I | Medium | POTD July 9, 2026',
          url: 'https://www.youtube.com/watch?v=98dMkF02fNc',
        },
        {
          videoId: 'Ye32NSc2jtw',
          title: 'Leetcode 3534 | Path Existence Queries in a Graph II | Hard | POTD July 10, 2026',
          url: 'https://www.youtube.com/watch?v=Ye32NSc2jtw',
        },
        {
          videoId: 'LHEnxQfVCxY',
          title: 'Leetcode 2685 | Count the Number of Complete Components | Medium | POTD July 11, 2026',
          url: 'https://www.youtube.com/watch?v=LHEnxQfVCxY',
        },
        {
          videoId: 'lgbT7kwRQO4',
          title: 'Leetcode 1331 | Rank Transform of an Array | Easy | POTD July 12, 2026',
          url: 'https://www.youtube.com/watch?v=lgbT7kwRQO4',
        },
        {
          videoId: 'dqIhC6gXVVk',
          title: 'Leetcode 1291 | Sequential Digits | Medium | POTD July 13, 2026',
          url: 'https://www.youtube.com/watch?v=dqIhC6gXVVk',
        },
        {
          videoId: 'q6VtfCD2o5M',
          title: 'Leetcode 3336 | Find the Number of Subsequences With Equal GCD | Hard | POTD July 14, 2026',
          url: 'https://www.youtube.com/watch?v=q6VtfCD2o5M',
        },
        {
          videoId: 'xWjOoJn3WmY',
          title: 'Leetcode 3658 | GCD of Odd and Even Sums | Easy | POTD July 15, 2026',
          url: 'https://www.youtube.com/watch?v=xWjOoJn3WmY',
        },
        {
          videoId: 'nKNYnVYejQg',
          title: 'Leetcode 3867 | Sum of GCD of Formed Pairs | Medium | POTD July 16, 2026',
          url: 'https://www.youtube.com/watch?v=nKNYnVYejQg',
        },
        {
          videoId: 'pO3xDPsFKyU',
          title: 'Leetcode 3312 | Sorted GCD Pair Queries | Hard | POTD July 17, 2026',
          url: 'https://www.youtube.com/watch?v=pO3xDPsFKyU',
        },
        {
          videoId: 'wXqb_Rhwlhk',
          title: 'Leetcode 1979 | Find Greatest Common Divisor of Array | Easy | POTD July 18, 2026',
          url: 'https://www.youtube.com/watch?v=wXqb_Rhwlhk',
        },
        {
          videoId: 'd6xTrXre_sY',
          title: 'Leetcode 1081 | Smallest Subsequence of Distinct Characters | Medium | POTD July 19, 2026',
          url: 'https://www.youtube.com/watch?v=d6xTrXre_sY',
        },
        {
          videoId: 'WNXhkY08tNs',
          title: 'Leetcode 1260 | Shift 2D Grid | Easy | POTD July 20, 2026',
          url: 'https://www.youtube.com/watch?v=WNXhkY08tNs',
        },
        {
          videoId: 'jONhypS9lMM',
          title: 'Leetcode 3499 | Maximize Active Section with Trade I | Medium | POTD July 21, 2026',
          url: 'https://www.youtube.com/watch?v=jONhypS9lMM',
        },
      ],
    },
  ],
};

export const MONTH_NAMES = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
];

/**
 * Parses video metadata from title following the format:
 * "Leetcode <number> | <title> | <difficulty> | POTD <month> <day>, <year>"
 */
export function parsePOTDTitle(title: string, playlistTitle: string, playlistId: string, videoId: string): POTDVideo | null {
  // Regex to match "Leetcode <probNum> | <probName> | <difficulty> | POTD <month> <day>, <year>"
  const regex = /(?:Leetcode\s+(\d+)\s*\|\s*)?([^|]+?)\s*\|\s*(Easy|Medium|Hard)\s*\|\s*POTD\s+([A-Za-z]+)\s+(\d{1,2}),?\s*(\d{4})?/i;
  const match = title.match(regex);

  if (match) {
    return {
      videoId,
      title,
      url: `https://www.youtube.com/watch?v=${videoId}`,
      problemNumber: match[1] || undefined,
      problemTitle: match[2]?.trim(),
      difficulty: (match[3].charAt(0).toUpperCase() + match[3].slice(1).toLowerCase()) as 'Easy' | 'Medium' | 'Hard',
      month: match[4].charAt(0).toUpperCase() + match[4].slice(1).toLowerCase(),
      day: parseInt(match[5], 10),
      year: match[6] ? parseInt(match[6], 10) : 2026,
      playlistTitle,
      playlistId,
    };
  }

  // Fallback for simple "POTD <month> <day>"
  const potdSimple = /POTD\s+([A-Za-z]+)\s+(\d{1,2})/i.exec(title);
  if (potdSimple) {
    return {
      videoId,
      title,
      url: `https://www.youtube.com/watch?v=${videoId}`,
      month: potdSimple[1].charAt(0).toUpperCase() + potdSimple[1].slice(1).toLowerCase(),
      day: parseInt(potdSimple[2], 10),
      year: 2026,
      playlistTitle,
      playlistId,
    };
  }

  return null;
}

/**
 * Finds the playlist for a given month and year.
 * Only playlists strictly named "Leetcode <MonthName> <Year>" are matched.
 */
export function getPlaylistForMonth(monthIndex: number, year: number): ChannelPlaylist | null {
  const monthName = MONTH_NAMES[monthIndex];
  if (!monthName) return null;

  const targetName = `leetcode ${monthName} ${year}`.toLowerCase();

  return (
    CHANNEL_DATA.playlists.find(
      (p) => p.playlistTitle.toLowerCase().trim() === targetName
    ) || null
  );
}

/**
 * Gets all parsed POTD videos for a given month & year from its playlist.
 */
export function getPOTDVideosForMonth(monthIndex: number, year: number): POTDVideo[] {
  const playlist = getPlaylistForMonth(monthIndex, year);
  if (!playlist) return [];

  const parsedList: POTDVideo[] = [];
  for (const v of playlist.videos) {
    const parsed = parsePOTDTitle(v.title, playlist.playlistTitle, playlist.playlistId, v.videoId);
    if (parsed) {
      parsedList.push(parsed);
    }
  }

  return parsedList;
}

/**
 * Gets the POTD video published for a specific date (year, monthIndex, day).
 * Strictly requires the video to belong to the "Leetcode <Month> <Year>" playlist!
 */
export function getVideoForDate(year: number, monthIndex: number, day: number): POTDVideo | null {
  const monthVideos = getPOTDVideosForMonth(monthIndex, year);
  return monthVideos.find((v) => v.day === day) || null;
}

/**
 * Returns a Set of day numbers that have POTD videos for the given month and year.
 */
export function getPOTDDaysSet(year: number, monthIndex: number): Set<number> {
  const monthVideos = getPOTDVideosForMonth(monthIndex, year);
  return new Set(monthVideos.map((v) => v.day));
}
