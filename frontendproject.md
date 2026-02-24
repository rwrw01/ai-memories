# Frontend Offline PWA — Projectplan

## Context

De Herinneringen PWA toont een **blanco scherm** wanneer er geen verbinding is. De huidige service worker (`generateSW`) cachet alleen statische bestanden maar heeft geen `navigateFallback` — navigatieverzoeken falen dus compleet offline.

Daarnaast:
- Audio-opnames gaan verloren bij verbindingsverlies
- Nieuws-audio (Phase 5) kan niet offline beluisterd worden

Dit plan lost alle drie problemen op in **4 onafhankelijke fases**, elk met eigen branch en verificatie.

---

## Fase A: App-shell offline beschikbaar (blanco scherm fix)

**Branch:** `feature/offline-shell`
**Doel:** Na eerste bezoek werkt de app offline — geen blanco scherm meer.

### Wat verandert

| Actie | Bestand | Doel |
|-------|---------|------|
| **Nieuw** | `src/service-worker.ts` | Custom SW met precaching + navigatie-caching |
| **Wijzig** | `vite.config.ts` | `generateSW` → `injectManifest` |

### Stappen

1. Maak `src/service-worker.ts` met:
   - `precacheAndRoute(self.__WB_MANIFEST)` — cache alle statische assets
   - `cleanupOutdatedCaches()` — opruimen bij SW-update
   - `NetworkFirst` strategie voor navigatie-requests (SvelteKit pagina's)
   - `SKIP_WAITING` message handler voor soepele updates
2. Wijzig `vite.config.ts`:
   - `strategies: 'generateSW'` → `'injectManifest'`
   - `workbox: { ... }` → `injectManifest: { globPatterns: [...] }`
   - Voeg `srcDir: 'src'` en `filename: 'service-worker.ts'` toe

### Verificatie

1. `bun run build` — succesvol
2. Start app, laad pagina (SW registreert)
3. DevTools → Network → "Offline" aan → herlaad → **app-shell zichtbaar** (niet blanco)
4. DevTools → Application → Cache Storage → precache entries aanwezig

---

## Fase B: Offline audio-opname met auto-retry

**Branch:** `feature/offline-recording`
**Doel:** Audio-opnames overleven verbindingsverlies. Worden automatisch verstuurd bij reconnect.
**Vereist:** Fase A (custom service worker)

### Wat verandert

| Actie | Bestand | Doel |
|-------|---------|------|
| **Nieuw** | `src/lib/offline-queue.ts` | IndexedDB wrapper voor wachtende uploads |
| **Nieuw** | `src/lib/stores/connection.svelte.ts` | Online/offline state + iOS retry fallback |
| **Wijzig** | `src/service-worker.ts` | Background Sync toevoegen voor `/api/stt` |
| **Wijzig** | `src/routes/+page.svelte` | `verstuurAudio()` queued offline opnames |
| **Wijzig** | `package.json` | `idb-keyval` dependency |

### Stappen

1. `bun add idb-keyval`
2. Maak `src/lib/offline-queue.ts`:
   - `enqueueUpload(blob, mimeType)` — Blob → ArrayBuffer → IndexedDB
   - `getAllPendingUploads()` — voor retry
   - `removeUpload(id)` — na succesvolle upload
   - `getPendingCount()` — voor UI
   - Prefix `pending-stt-`, max 5 retries, 24-uur TTL
3. Maak `src/lib/stores/connection.svelte.ts`:
   - Reactieve `online` state via `$state()`
   - `window.addEventListener('online'/'offline')`
   - iOS fallback: `visibilitychange` event → retry wachtende uploads
   - Exporteert `initConnectionWatcher()` met cleanup
4. Voeg `BackgroundSyncPlugin` toe aan `src/service-worker.ts`:
   - Queue `stt-upload-queue`, 24 uur retentie
   - Registreer op `POST /api/stt` met `NetworkFirst` + sync plugin
5. Wijzig `verstuurAudio()` in `+page.svelte`:
   - Check `navigator.onLine` vóór fetch
   - Offline → `enqueueUpload()` → toon "Opname opgeslagen — wordt verstuurd bij verbinding"
   - Fetch-fout → alsnog queuen in IndexedDB
   - Status wordt `idle` (niet `fout`) bij offline opslaan

### Verificatie

1. Offline aan → opnemen → "Opname opgeslagen" melding
2. DevTools → Application → IndexedDB → entry zichtbaar
3. Online aan → upload wordt automatisch verstuurd
4. iPhone: vliegtuigmodus aan → opnemen → uit → terug naar app → upload verstuurd

---

## Fase C: Offline UI indicator

**Branch:** `feature/offline-indicator`
**Doel:** Gebruiker ziet duidelijk wanneer de app offline is en hoeveel opnames wachten.
**Vereist:** Fase B (connection store + offline queue)

### Wat verandert

| Actie | Bestand | Doel |
|-------|---------|------|
| **Nieuw** | `src/lib/components/OfflineIndicator.svelte` | "Geen verbinding" banner |
| **Wijzig** | `src/routes/+layout.svelte` | Component invoegen + watcher init |

### Stappen

1. Maak `src/lib/components/OfflineIndicator.svelte`:
   - Rode banner bovenaan wanneer offline
   - Tekst: "Geen verbinding"
   - Badge met wachtende uploads: "2 wachtend"
   - Knipperende rode dot (animatie)
   - Dark theme: `#2a1020` achtergrond, `#e94560` accent
2. Wijzig `src/routes/+layout.svelte`:
   - Import `OfflineIndicator` + `initConnectionWatcher`
   - Component plaatsen tussen header en main
   - `initConnectionWatcher()` aanroepen in `onMount`

### Verificatie

1. Online: geen banner zichtbaar
2. Offline: rode "Geen verbinding" banner verschijnt
3. Offline + opname queued: badge toont "1 wachtend"
4. Terug online: banner verdwijnt

---

## Fase D: Nieuws-audio pre-caching (Phase 5 infra)

**Branch:** `feature/news-cache-infra`
**Doel:** Infrastructuur voor offline nieuws-playback. Wordt aangesloten wanneer Phase 5 (News Briefing) gebouwd wordt.
**Vereist:** Fase A (custom service worker)

### Wat verandert

| Actie | Bestand | Doel |
|-------|---------|------|
| **Nieuw** | `src/lib/news-cache.ts` | Pre-cache helper voor nieuws-audio |
| **Wijzig** | `src/service-worker.ts` | Runtime caching routes voor news API |

### Stappen

1. Voeg runtime caching routes toe aan `src/service-worker.ts`:
   - `NetworkFirst` voor `GET /api/news/today` (manifest)
   - `CacheFirst` voor `GET /api/news/{id}/audio` (immutable audio)
   - Cache: `news-audio`, max 30 entries, 7 dagen TTL, `purgeOnQuotaError: true`
   - Message handler voor `PRECACHE_NEWS_AUDIO` → SW downloadt URL-lijst
2. Maak `src/lib/news-cache.ts`:
   - `precacheNewsForToday()` — fetch manifest → postMessage naar SW
   - `getCachedNewsManifest()` — lees manifest uit cache voor offline
   - Vangt 404 stilzwijgend op (endpoints bestaan nog niet)

### Verificatie

1. Build succesvol
2. SW registreert zonder fouten
3. `precacheNewsForToday()` aanroepen → geen errors (404 wordt stilzwijgend genegeerd)
4. Handmatig testen zodra Phase 5 endpoints bestaan

---

## Volgorde en afhankelijkheden

```
Fase A (shell)  ←── verplicht eerst
  ├── Fase B (recording) ←── vereist A
  │     └── Fase C (indicator) ←── vereist B
  └── Fase D (news infra) ←── vereist A, onafhankelijk van B/C
```

Aanbevolen volgorde: **A → B → C → D**

Fase D kan ook parallel aan B+C of later bij Phase 5.

---

## Bestanden totaaloverzicht

| Bestand | Fase | Actie |
|---------|------|-------|
| `src/service-worker.ts` | A + B + D | Nieuw (A), uitbreiden (B, D) |
| `vite.config.ts` | A | Wijzigen |
| `src/lib/offline-queue.ts` | B | Nieuw |
| `src/lib/stores/connection.svelte.ts` | B | Nieuw |
| `src/routes/+page.svelte` | B | Wijzigen |
| `package.json` | B | Wijzigen (idb-keyval) |
| `src/lib/components/OfflineIndicator.svelte` | C | Nieuw |
| `src/routes/+layout.svelte` | C | Wijzigen |
| `src/lib/news-cache.ts` | D | Nieuw |
