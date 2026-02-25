export type NewsArticle = {
	id: string;
	source: string;
	title: string;
	url: string;
	description: string | null;
	audio_ready: boolean;
	audio_quality: 'parkiet' | 'piper' | null;
	published_at: string;
	rendered_at: string | null;
};

export type NewsTodayResponse = {
	date: string;
	articles: NewsArticle[];
	total: number;
	audio_ready_count: number;
};

export type NewsPreferences = {
	feeds: string[];
	max_articles: number;
	categories_exclude: string[];
};
