export type FeedEntry = {
	url: string;
	label: string;
	category: string;
};

export type Provider = {
	id: string;
	name: string;
	lang: 'nl' | 'en';
	feeds: FeedEntry[];
};

export const FEED_CATALOG: Provider[] = [
	{
		id: 'nos',
		name: 'NOS',
		lang: 'nl',
		feeds: [
			{ url: 'https://feeds.nos.nl/nosnieuwsalgemeen', label: 'Algemeen', category: 'algemeen' },
			{ url: 'https://feeds.nos.nl/nosnieuwseconomie', label: 'Economie', category: 'economie' },
			{
				url: 'https://feeds.nos.nl/nosnieuwsbuitenland',
				label: 'Buitenland',
				category: 'internationaal'
			},
			{ url: 'https://feeds.nos.nl/nosnieuwstech', label: 'Tech', category: 'tech' },
			{ url: 'https://feeds.nos.nl/nossportalgemeen', label: 'Sport', category: 'sport' }
		]
	},
	{
		id: 'nunl',
		name: 'NU.nl',
		lang: 'nl',
		feeds: [
			{ url: 'https://www.nu.nl/rss/Algemeen', label: 'Algemeen', category: 'algemeen' },
			{ url: 'https://www.nu.nl/rss/Economie', label: 'Economie', category: 'economie' },
			{ url: 'https://www.nu.nl/rss/Internet', label: 'Tech', category: 'tech' }
		]
	},
	{
		id: 'tweakers',
		name: 'Tweakers',
		lang: 'nl',
		feeds: [
			{ url: 'https://feeds.tweakers.net/mixed.xml', label: 'Algemeen', category: 'tech' }
		]
	},
	{
		id: 'rtl',
		name: 'RTL Nieuws',
		lang: 'nl',
		feeds: [
			{ url: 'https://www.rtlnieuws.nl/rss.xml', label: 'Algemeen', category: 'algemeen' }
		]
	},
	{
		id: 'knmi',
		name: 'KNMI',
		lang: 'nl',
		feeds: [
			{
				url: 'https://cdn.knmi.nl/knmi/xml/rss/rss_KNMIverwachtingen.xml',
				label: 'Weerbericht',
				category: 'weer'
			}
		]
	},
	{
		id: 'bbc',
		name: 'BBC News',
		lang: 'en',
		feeds: [
			{ url: 'https://feeds.bbci.co.uk/news/rss.xml', label: 'World', category: 'internationaal' },
			{
				url: 'https://feeds.bbci.co.uk/news/technology/rss.xml',
				label: 'Tech',
				category: 'tech'
			},
			{
				url: 'https://feeds.bbci.co.uk/news/business/rss.xml',
				label: 'Business',
				category: 'economie'
			}
		]
	},
	{
		id: 'arstechnica',
		name: 'Ars Technica',
		lang: 'en',
		feeds: [
			{
				url: 'https://feeds.arstechnica.com/arstechnica/index/',
				label: 'Algemeen',
				category: 'tech'
			}
		]
	},
	{
		id: 'theverge',
		name: 'The Verge',
		lang: 'en',
		feeds: [
			{ url: 'https://www.theverge.com/rss/index.xml', label: 'Algemeen', category: 'tech' }
		]
	},
	{
		id: 'hackernews',
		name: 'Hacker News',
		lang: 'en',
		feeds: [{ url: 'https://hnrss.org/frontpage', label: 'Front Page', category: 'tech' }]
	}
];
