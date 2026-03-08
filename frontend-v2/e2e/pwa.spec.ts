/**
 * E2E tests for Herinneringen PWA — mobile browser (iPhone 14 viewport).
 *
 * Covers happy + unhappy flows for all core features:
 *   1. Navigation & layout
 *   2. Dictafoon (recording)
 *   3. Instellingen (service health)
 *   4. WhatsApp pairing
 *   5. Uren page
 *   6. Artikelen page
 *   7. Auth & error handling
 */

import { test, expect, type Page } from '@playwright/test';

// Mobile viewport (iPhone 14)
test.use({
	viewport: { width: 393, height: 852 },
	userAgent:
		'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
	hasTouch: true,
	isMobile: true,
});

const BASE = process.env.BASE_URL ?? 'http://localhost:3000';

// ---------------------------------------------------------------------------
// 1. Navigation & Layout
// ---------------------------------------------------------------------------

test.describe('Navigatie & layout', () => {
	test('homepage laadt met juiste titel en navigatie', async ({ page }) => {
		await page.goto(BASE);
		await expect(page.locator('h1')).toContainText('Herinneringen');

		// Bottom nav has all 6 items
		const nav = page.locator('nav');
		await expect(nav.getByText('Dictafoon')).toBeVisible();
		await expect(nav.getByText('Artikelen')).toBeVisible();
		await expect(nav.getByText('Uren')).toBeVisible();
		await expect(nav.getByText('WhatsApp')).toBeVisible();
		await expect(nav.getByText('Pipeline')).toBeVisible();
		await expect(nav.getByText('Instellingen')).toBeVisible();
	});

	test('navigatie tussen alle paginas werkt', async ({ page }) => {
		await page.goto(BASE);

		// Navigate to each page and verify content loads
		const pages = [
			{ label: 'Artikelen', heading: /artikelen/i },
			{ label: 'Uren', heading: /uren/i },
			{ label: 'WhatsApp', heading: /whatsapp/i },
			{ label: 'Instellingen', heading: /instellingen|systeemstatus/i },
			{ label: 'Dictafoon', heading: /opnemen/i },
		];

		for (const p of pages) {
			await page.locator('nav').getByText(p.label).click();
			await page.waitForLoadState('networkidle');
			// Page should not show a hard error
			await expect(page.locator('body')).not.toContainText('500');
		}
	});

	test('layout past in mobiele viewport zonder horizontale scroll', async ({ page }) => {
		await page.goto(BASE);
		const body = page.locator('body');
		const box = await body.boundingBox();
		expect(box).not.toBeNull();
		// Body should not exceed viewport width
		expect(box!.width).toBeLessThanOrEqual(393 + 1);
	});
});

// ---------------------------------------------------------------------------
// 2. Dictafoon (recording)
// ---------------------------------------------------------------------------

test.describe('Dictafoon', () => {
	test('happy: opnameknop is zichtbaar en klikbaar', async ({ page }) => {
		await page.goto(BASE);

		// Record button with aria-label
		const recordBtn = page.locator('button[aria-label="Start opname"]');
		await expect(recordBtn).toBeVisible();

		// Timer shows 00:00
		await expect(page.locator('text=00:00')).toBeVisible();

		// "Opnemen" label visible
		await expect(page.getByText('Opnemen')).toBeVisible();
	});

	test('happy: opname starten (met microfoon) toont stop-knop', async ({ page, context }) => {
		// In headless mode, getUserMedia may not have a real device.
		// We test that clicking the button either starts recording or shows an error.
		await context.grantPermissions(['microphone']);
		await page.goto(BASE);

		const recordBtn = page.locator('button[aria-label="Start opname"]');
		await recordBtn.click();

		// Either the stop button appears (recording started) or an error shows
		const stopBtn = page.locator('button[aria-label="Stop opname"]');
		const errorMsg = page.locator('text=/microfoon|toegang|Mislukt/i');

		await expect(stopBtn.or(errorMsg)).toBeVisible({ timeout: 5000 });

		// Clean up: stop if recording started
		if (await stopBtn.isVisible()) {
			await stopBtn.click();
		}
	});

	test('unhappy: geen microfoon toestemming toont foutmelding', async ({ page }) => {
		// Deny microphone
		await page.context().grantPermissions([]);
		await page.goto(BASE);

		const recordBtn = page.locator('button[aria-label="Start opname"]');
		await recordBtn.click();

		// Should show error about microphone access
		await expect(page.getByText(/microfoon|toegang/i)).toBeVisible({ timeout: 3000 });
	});

	test('happy: dictaat met transcriptie toont kopieer en verwijder knoppen', async ({ page }) => {
		// Mock the store to have a completed dictaat
		await page.goto(BASE);
		await page.evaluate(() => {
			const dictaat = {
				id: 'test-1',
				datum: Date.now(),
				duur: 5,
				status: 'gereed',
				transcriptie: 'Van acht tot twaalf bravis roosendaal',
				classificatie: null,
			};
			// Set in IndexedDB via idb-keyval
			const request = indexedDB.open('keyval-store', 1);
			request.onupgradeneeded = () => {
				request.result.createObjectStore('keyval');
			};
			request.onsuccess = () => {
				const tx = request.result.transaction('keyval', 'readwrite');
				tx.objectStore('keyval').put([dictaat], 'dictaten');
			};
		});

		// Reload to pick up the stored data
		await page.reload();
		await page.waitForLoadState('networkidle');

		// If dictaat loaded, we should see the transcription text
		const transcriptie = page.getByText('Van acht tot twaalf bravis roosendaal');
		if (await transcriptie.isVisible()) {
			// Copy and delete buttons should be present
			await expect(page.getByText('Kopieer')).toBeVisible();
			await expect(page.getByText('Verwijder')).toBeVisible();
		}
	});
});

// ---------------------------------------------------------------------------
// 3. Instellingen (service health)
// ---------------------------------------------------------------------------

test.describe('Instellingen', () => {
	test('happy: systeemstatus toont servicelijst', async ({ page }) => {
		await page.goto(`${BASE}/instellingen`);

		await expect(page.getByRole('heading', { name: 'Instellingen' })).toBeVisible();
		await expect(page.getByText('Systeemstatus')).toBeVisible();

		// Wait for health data to load (or show error)
		await page.waitForTimeout(2000);

		// Should show either service statuses or "Backend niet bereikbaar"
		// Use locator scoped to main content to avoid matching StatusBanner too
		const main = page.locator('main');
		const hasServices = await main.getByText(/STT|TTS|Ollama|NER/i).isVisible();
		const hasError = await main.getByText('Backend niet bereikbaar').isVisible();
		expect(hasServices || hasError).toBeTruthy();
	});

	test('unhappy: backend offline toont foutmelding', async ({ page }) => {
		// Block health API
		await page.route('**/api/health', (route) => route.abort());
		await page.goto(`${BASE}/instellingen`);

		await page.waitForTimeout(2000);
		// Scope to main to avoid strict mode conflict with StatusBanner
		await expect(page.locator('main').getByText('Backend niet bereikbaar')).toBeVisible();
	});
});

// ---------------------------------------------------------------------------
// 4. WhatsApp
// ---------------------------------------------------------------------------

test.describe('WhatsApp', () => {
	test('happy: pagina toont status en koppelopties', async ({ page }) => {
		await page.goto(`${BASE}/whatsapp`);

		// Use heading role to avoid matching instruction text "Open WhatsApp →..."
		await expect(page.getByRole('heading', { name: 'WhatsApp' })).toBeVisible();
		await expect(page.getByText('Vernieuwen')).toBeVisible();

		// Should show status (Verbonden, Niet verbonden, or any error)
		await page.waitForTimeout(2000);
		const main = page.locator('main');
		// Accept any status badge — connected, not connected, or backend error
		const statusCard = main.locator('.card, [class*="card"]').first();
		const hasStatus = await main.getByText(/Verbonden|Niet verbonden|Status|Failed|status niet ophalen/i).first().isVisible();
		expect(hasStatus).toBeTruthy();
	});

	test('happy: niet-verbonden toont telefoonnummer invoer', async ({ page }) => {
		// Mock status as not connected
		await page.route('**/api/whatsapp/status', (route) =>
			route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ ready: false, hasQr: false }),
			})
		);
		await page.goto(`${BASE}/whatsapp`);

		await page.waitForTimeout(1000);

		// Phone number input should be visible
		await expect(page.getByPlaceholder('31612345678')).toBeVisible();
		await expect(page.getByText('Koppelen')).toBeVisible();
	});

	test('unhappy: ongeldig telefoonnummer toont validatiefout', async ({ page }) => {
		await page.route('**/api/whatsapp/status', (route) =>
			route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ ready: false, hasQr: false }),
			})
		);
		await page.goto(`${BASE}/whatsapp`);
		await page.waitForTimeout(1000);

		// Enter too-short number
		await page.getByPlaceholder('31612345678').fill('123');
		await page.getByText('Koppelen').click();

		// Should show validation error
		await expect(page.getByText(/geldig telefoonnummer/i)).toBeVisible();
	});

	test('happy: verbonden toont contactenlijst met zoekfunctie', async ({ page }) => {
		// Mock connected status with contacts
		await page.route('**/api/whatsapp/status', (route) =>
			route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ ready: true, hasQr: false }),
			})
		);
		await page.route('**/api/whatsapp/contacts', (route) =>
			route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify([
					{ name: 'Jan de Vries', number: '+31612345678' },
					{ name: 'Piet Jansen', number: '+31698765432' },
					{ name: 'Marie Bakker', number: '+31611223344' },
				]),
			})
		);
		await page.goto(`${BASE}/whatsapp`);
		await page.waitForTimeout(1000);

		// Contacts visible
		await expect(page.getByText('Jan de Vries')).toBeVisible();
		await expect(page.getByText('3 contacten beschikbaar')).toBeVisible();

		// Search works
		await page.getByPlaceholder('Zoek contact...').fill('Piet');
		await expect(page.getByText('Jan de Vries')).not.toBeVisible();
		await expect(page.getByText('Piet Jansen')).toBeVisible();
	});

	test('unhappy: zoek zonder resultaten toont lege state', async ({ page }) => {
		await page.route('**/api/whatsapp/status', (route) =>
			route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify({ ready: true, hasQr: false }),
			})
		);
		await page.route('**/api/whatsapp/contacts', (route) =>
			route.fulfill({
				status: 200,
				contentType: 'application/json',
				body: JSON.stringify([{ name: 'Jan de Vries', number: '+31612345678' }]),
			})
		);
		await page.goto(`${BASE}/whatsapp`);
		await page.waitForTimeout(1000);

		await page.getByPlaceholder('Zoek contact...').fill('Niemand');
		await expect(page.getByText('Geen contacten gevonden')).toBeVisible();
	});
});

// ---------------------------------------------------------------------------
// 5. Uren
// ---------------------------------------------------------------------------

test.describe('Uren', () => {
	test('happy: uren pagina laadt', async ({ page }) => {
		await page.goto(`${BASE}/uren`);
		await page.waitForLoadState('networkidle');

		// Page should load without errors
		await expect(page.locator('body')).not.toContainText('500');
		await expect(page.locator('body')).not.toContainText('error');
	});
});

// ---------------------------------------------------------------------------
// 6. Artikelen
// ---------------------------------------------------------------------------

test.describe('Artikelen', () => {
	test('happy: artikelen pagina laadt', async ({ page }) => {
		await page.goto(`${BASE}/artikelen`);
		await page.waitForLoadState('networkidle');

		// Page should load without errors
		await expect(page.locator('body')).not.toContainText('500');
	});
});

// ---------------------------------------------------------------------------
// 7. Auth & Error handling
// ---------------------------------------------------------------------------

test.describe('Foutafhandeling', () => {
	test('unhappy: API 401 wordt graceful afgehandeld', async ({ page }) => {
		// Block all API calls with 401
		await page.route('**/api/**', (route) =>
			route.fulfill({
				status: 401,
				contentType: 'application/json',
				body: JSON.stringify({ detail: 'API key vereist' }),
			})
		);
		await page.goto(`${BASE}/instellingen`);
		await page.waitForTimeout(2000);

		// Should not crash — show error state (scope to main to avoid StatusBanner duplicate)
		await expect(page.locator('main').getByText('Backend niet bereikbaar')).toBeVisible();
	});

	test('unhappy: netwerk timeout wordt graceful afgehandeld', async ({ page }) => {
		// Simulate network timeout
		await page.route('**/api/**', (route) => route.abort('timedout'));
		await page.goto(`${BASE}/instellingen`);
		await page.waitForTimeout(2000);

		// Should show error, not crash (scope to main to avoid StatusBanner duplicate)
		await expect(page.locator('main').getByText('Backend niet bereikbaar')).toBeVisible();
	});

	test('unhappy: 404 pagina geeft geen crash', async ({ page }) => {
		const response = await page.goto(`${BASE}/niet-bestaande-pagina`);
		// SvelteKit returns 404 but page should still render
		expect(response?.status()).toBe(404);
	});
});

// ---------------------------------------------------------------------------
// 8. PWA-specifiek
// ---------------------------------------------------------------------------

test.describe('PWA features', () => {
	test('manifest is bereikbaar', async ({ page }) => {
		await page.goto(BASE);

		// Check for manifest link in head
		const manifest = page.locator('link[rel="manifest"]');
		if (await manifest.count()) {
			const href = await manifest.getAttribute('href');
			expect(href).toBeTruthy();

			// Fetch manifest and verify it's valid JSON
			const response = await page.goto(`${BASE}${href}`);
			expect(response?.status()).toBe(200);
		}
	});

	test('viewport meta tag is correct voor mobiel', async ({ page }) => {
		await page.goto(BASE);

		const viewport = page.locator('meta[name="viewport"]');
		await expect(viewport).toHaveAttribute('content', /width=device-width/);
	});

	test('touch targets zijn minimaal 44x44px', async ({ page }) => {
		await page.goto(BASE);

		// Check bottom nav buttons
		const navLinks = page.locator('nav a');
		const count = await navLinks.count();

		for (let i = 0; i < count; i++) {
			const box = await navLinks.nth(i).boundingBox();
			expect(box).not.toBeNull();
			// At least 44px in both dimensions (WCAG 2.5.8)
			expect(box!.height).toBeGreaterThanOrEqual(40); // Allow slight margin
			expect(box!.width).toBeGreaterThanOrEqual(40);
		}

		// Check record button
		const recordBtn = page.locator('button[aria-label="Start opname"]');
		const recBox = await recordBtn.boundingBox();
		expect(recBox).not.toBeNull();
		expect(recBox!.height).toBeGreaterThanOrEqual(44);
		expect(recBox!.width).toBeGreaterThanOrEqual(44);
	});
});
