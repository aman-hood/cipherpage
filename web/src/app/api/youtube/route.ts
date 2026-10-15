import { NextResponse } from 'next/server';
import { 
  CHANNEL_DATA, 
  getPlaylistForMonth, 
  getPOTDVideosForMonth, 
  getVideoForDate, 
  MONTH_NAMES 
} from '@/lib/youtubeData';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const monthParam = searchParams.get('month');
  const yearParam = searchParams.get('year');
  const dayParam = searchParams.get('day');

  // If specific date is requested
  if (yearParam && monthParam !== null && dayParam) {
    const year = parseInt(yearParam, 10);
    const month = parseInt(monthParam, 10);
    const day = parseInt(dayParam, 10);

    const video = getVideoForDate(year, month, day);
    const playlist = getPlaylistForMonth(month, year);

    return NextResponse.json({
      channel: {
        title: CHANNEL_DATA.title,
        url: CHANNEL_DATA.url,
        handle: CHANNEL_DATA.handle,
      },
      date: { year, month: MONTH_NAMES[month], day },
      playlistName: playlist?.playlistTitle || `Leetcode ${MONTH_NAMES[month]} ${year}`,
      hasPlaylist: !!playlist,
      video: video || null,
    });
  }

  // If month & year is requested
  if (yearParam && monthParam !== null) {
    const year = parseInt(yearParam, 10);
    const month = parseInt(monthParam, 10);

    const playlist = getPlaylistForMonth(month, year);
    const videos = getPOTDVideosForMonth(month, year);

    return NextResponse.json({
      channel: {
        title: CHANNEL_DATA.title,
        url: CHANNEL_DATA.url,
        handle: CHANNEL_DATA.handle,
      },
      month: MONTH_NAMES[month],
      year,
      playlist: playlist || null,
      videos,
    });
  }

  // Otherwise return full channel info
  return NextResponse.json(CHANNEL_DATA);
}
