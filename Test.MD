# Testing Knowledge — PWA Audio Recording App

## Testinfrastructuur

### Packages

```bash
bun add -d vitest @vitest/browser vitest-browser-svelte playwright fake-indexeddb @playwright/test
bunx playwright install chromium
```

### Vitest config

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
  plugins: [sveltekit()],
  test: {
    projects: [{
      name: 'browser',
      browser: {
        enabled: true,
        provider: 'playwright',
        instances: [{ browser: 'chromium' }],
      },
      include: ['src/**/*.{test,spec}.{ts,js}'],
      setupFiles: ['src/tests/setup.ts'],
    }],
  },
});
```

### Test setup (fake-indexeddb)

```typescript
// src/tests/setup.ts
import 'fake-indexeddb/auto';
// idb-keyval reads from globalThis.indexedDB — auto patches it
```

---

## MediaRecorder Mocking

### FakeMediaRecorder class

```typescript
class FakeMediaRecorder {
  static isTypeSupported = vi.fn(() => true);
  state: 'inactive' | 'recording' = 'inactive';
  ondataavailable: ((e: { data: Blob }) => void) | null = null;
  onstop: (() => void) | null = null;
  private intervalId: ReturnType<typeof setInterval> | null = null;

  constructor(public stream: MediaStream, public options?: { mimeType?: string }) {}

  start(timeslice?: number): void {
    this.state = 'recording';
    if (timeslice) {
      this.intervalId = setInterval(() => {
        this.ondataavailable?.({ data: new Blob(['chunk'], { type: 'audio/webm' }) });
      }, timeslice);
    }
  }

  stop(): void {
    if (this.intervalId) clearInterval(this.intervalId);
    this.ondataavailable?.({ data: new Blob(['final'], { type: 'audio/webm' }) });
    this.state = 'inactive';
    this.onstop?.();
  }

  requestData(): void {
    this.ondataavailable?.({ data: new Blob(['requested'], { type: 'audio/webm' }) });
  }
}
```

### Fake getUserMedia

```typescript
function makeFakeStream(): MediaStream {
  return { getTracks: () => [{ stop: vi.fn() }] } as unknown as MediaStream;
}

vi.stubGlobal('navigator', {
  mediaDevices: { getUserMedia: vi.fn(async () => makeFakeStream()) },
});
```

---

## IndexedDB Testing

### Pattern: reset between tests

```typescript
import { clear } from 'idb-keyval';
beforeEach(async () => await clear());
```

### Pattern: simulate QuotaExceededError

```typescript
import * as idbKeyval from 'idb-keyval';
vi.spyOn(idbKeyval, 'set').mockRejectedValueOnce(
  new DOMException('Quota exceeded', 'QuotaExceededError')
);
```

### Pattern: seed crash recovery chunks

```typescript
import { set } from 'idb-keyval';
await set('rec-meta', { mimeType: 'audio/webm', startedAt: Date.now() - 30000, chunkCount: 2 });
await set('rec-chunk-0', new Uint8Array([0x00]).buffer);
await set('rec-chunk-1', new Uint8Array([0x01]).buffer);
```

---

## E2E Testing met Playwright

### Config met fake microfoon

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    baseURL: 'http://localhost:5173',
    launchOptions: {
      args: [
        '--use-fake-device-for-media-stream',
        '--use-fake-ui-for-media-stream',
        '--use-file-for-fake-audio-capture=./e2e/fixtures/test-audio-48k.wav',
      ],
    },
    permissions: ['microphone'],
  },
});
```

WAV fixture vereisten: **mono, 48kHz, 16-bit PCM**.

### Offline testing

```typescript
await page.goto('/');
await page.waitForLoadState('networkidle');
await page.evaluate(() => navigator.serviceWorker.ready);
await context.setOffline(true);
await page.reload();
// App should render from SW cache
```

### Test audio generation

```bash
python scripts/generate_test_wav.py              # 1-5 min files
python scripts/generate_test_wav.py --duration 60 # custom duration
```

---

## Regressietests

### 1. Timer stacking

**Bug:** `startRecording()` called without `stopTimer()` causes multiple intervals.

```typescript
it('timer does not stack on double start', async () => {
  vi.useFakeTimers();
  await startRecording(s => ticks.push(s), vi.fn());
  await startRecording(s => ticks.push(s), vi.fn()); // second call
  vi.advanceTimersByTime(3000);
  expect(ticks.filter(t => t === 1)).toHaveLength(1); // no duplicate "1"
});
```

### 2. Blob completeness

**Bug:** `onstop` fires before IndexedDB writes complete.

```typescript
it('onstop blob contains all chunks', async () => {
  let result: Blob;
  await startRecording(vi.fn(), blob => { result = blob; });
  fakeRecorder.emitChunk(new Blob(['aaaa']));
  fakeRecorder.emitChunk(new Blob(['bbbb']));
  stopRecording();
  expect(result!.size).toBeGreaterThan(0);
});
```

### 3. Body size limit (>512KB)

**Bug:** SvelteKit adapter-node default BODY_SIZE_LIMIT = 512KB.

```typescript
test('upload >512KB succeeds', async ({ page }) => {
  let uploadSize = 0;
  await page.route('**/api/stt', async route => {
    uploadSize = (await route.request().postDataBuffer())?.length ?? 0;
    await route.fulfill({ json: { text: 'ok' } });
  });
  // Record 7+ seconds to exceed 512KB
  // ...
  expect(uploadSize).toBeGreaterThan(512 * 1024);
});
```

### 4. Error propagation

**Bug:** Catch block swallowed errors silently.

```typescript
it('transcription failure sets foutReden', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Network error')));
  const d = await saveDictaat(blob, 'audio/webm', 5);
  await transcribeDictaat(d);
  expect(getDictaten().find(x => x.id === d.id)?.foutReden).toBe('Network error');
});
```

### 5. Crash recovery order

```typescript
it('recovery preserves chunk order', async () => {
  await set('rec-chunk-2', new Uint8Array([0x02]).buffer);
  await set('rec-chunk-0', new Uint8Array([0x00]).buffer);
  await set('rec-chunk-1', new Uint8Array([0x01]).buffer);
  await set('rec-meta', { mimeType: 'audio/webm', startedAt: Date.now() - 5000, chunkCount: 3 });
  const result = await recoverInterruptedRecording();
  const arr = new Uint8Array(await result!.blob.arrayBuffer());
  expect([arr[0], arr[1], arr[2]]).toEqual([0x00, 0x01, 0x02]);
});
```

---

## Bekende iOS Safari Problemen

### Kritiek

| Probleem | Symptoom | Workaround |
|----------|----------|------------|
| `onstop` niet gevuurd op iPad | Blob nooit afgeleverd | Collect chunks in `ondataavailable`, gebruik `requestData()` voor stop |
| Timeslice genegeerd (iOS 14-15) | Slechts 1 ondataavailable event | Vertrouw niet op timeslice voor streaming; upload alles na stop |
| Pagina crash >60s opname | iOS herlaadt pagina (geheugen) | Flush chunks incrementeel naar IDB, vermijd grote Blobs in geheugen |
| `audio/mp4` ipv WebM | Backend rejects onbekend formaat | `isTypeSupported` cascade, stuur mimeType mee |
| Timer throttling achtergrond | `setInterval` bevriest | Gebruik `visibilitychange` om te detecteren; herstart timer |
| Wake Lock broken in PWA (iOS <18.4) | Scherm gaat uit ondanks lock | Speel stil audiobestand af als fallback |

### IndexedDB

| Probleem | Symptoom | Workaround |
|----------|----------|------------|
| 7-dagen evictie (Safari browser) | Data verdwijnt | Installeer als PWA + `navigator.storage.persist()` |
| ~50MB quotum (Safari browser) | `QuotaExceededError` | Check quota voor write, verwijder na upload |
| Stille write failure (geheugendruk) | Data lijkt geschreven maar verdwijnt | Read-back verificatie na put() |
| Transaction auto-close na await | `TransactionInactiveError` | Geen non-IDB awaits in transactie (idb-keyval doet dit goed) |

### MediaRecorder

| Probleem | Symptoom | Workaround |
|----------|----------|------------|
| Alleen eerste chunk heeft headers | Losse chunks niet speelbaar | Altijd concateneren tot 1 Blob |
| Lege blobs van ondataavailable | `size === 0` | Filter `e.data.size > 0` |
| Bad state na slaap/wakker | Recorder hangt of geeft lege data | Stop en herstart bij `visibilitychange` |
| WebM duration=Infinity | Audio player toont geen duur | Fix met `fix-webm-duration` library (niet relevant voor STT) |

---

## Incrementeel Testprotocol

Test-audiobestanden genereren:
```bash
cd memories && python3 scripts/generate_test_wav.py
```

Dit maakt bestanden in `scripts/test-audio/`:
- `test-1min.wav` — 5.5 MB
- `test-2min.wav` — 11.0 MB
- `test-3min.wav` — 16.5 MB
- `test-4min.wav` — 22.0 MB
- `test-5min.wav` — 27.5 MB

Per stap:
```bash
# 1. Upload naar STT backend
curl -X POST -F "audio=@scripts/test-audio/test-Xmin.wav" http://localhost:8000/api/stt

# 2. Check HTTP status (verwacht: 200)
# 3. Check response JSON: {"text": "..."}
# 4. Check response time (<60s voor 5min audio)
# 5. Check geheugen: docker stats --no-stream
```

### Verwachte resultaten

| Duur | Bestandsgrootte | Max response time | Status |
|------|----------------|-------------------|--------|
| 1 min | 5.5 MB | ~10s | 200 OK |
| 2 min | 11.0 MB | ~15s | 200 OK |
| 3 min | 16.5 MB | ~25s | 200 OK |
| 4 min | 22.0 MB | ~35s | 200 OK |
| 5 min | 27.5 MB | ~45s | 200 OK |

---

## CI/CD

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: bun install
        working-directory: frontend
      - run: bun run test
        working-directory: frontend

  e2e:
    runs-on: ubuntu-latest
    container:
      image: mcr.microsoft.com/playwright:v1.48.0-noble
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v2
      - run: bun install
        working-directory: frontend
      - run: bun run e2e/generate-fixtures.ts
        working-directory: frontend
      - run: bun run build
        working-directory: frontend
      - run: bunx playwright test
        working-directory: frontend
```

**Key:** Use `mcr.microsoft.com/playwright:v1.48.0-noble` (not Alpine — lacks audio codecs).
