import { defineConfig } from '@playwright/test';

export default defineConfig({
	testDir: './e2e',
	timeout: 30_000,
	retries: 1,
	use: {
		baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
		trace: 'on-first-retry',
		screenshot: 'only-on-failure',
	},
	projects: [
		{
			name: 'mobile-chrome',
			use: {
				browserName: 'chromium',
				viewport: { width: 393, height: 852 },
				isMobile: true,
				hasTouch: true,
				userAgent:
					'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
			},
		},
	],
	webServer: {
		command: 'npm run preview',
		port: 3000,
		reuseExistingServer: true,
		timeout: 15_000,
	},
});
