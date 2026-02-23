import type { NewsTodayResponse } from '$lib/types/news';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
	const resp = await fetch('/api/news/today');

	if (!resp.ok) {
		return { articles: [], date: '', total: 0, audioReadyCount: 0 };
	}

	const data: NewsTodayResponse = await resp.json();
	return {
		articles: data.articles,
		date: data.date,
		total: data.total,
		audioReadyCount: data.audio_ready_count
	};
};
