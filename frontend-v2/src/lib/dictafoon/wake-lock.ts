// Screen Wake Lock API wrapper — keeps screen on during recording.
// Supported in Safari 16.4+ (iOS 16.4+), Chrome 84+, Edge 84+.

let wakeLock: WakeLockSentinel | null = null;
let visibilityHandler: (() => void) | null = null;

export function isWakeLockSupported(): boolean {
	return 'wakeLock' in navigator;
}

export async function requestWakeLock(): Promise<boolean> {
	if (!isWakeLockSupported()) return false;

	try {
		wakeLock = await navigator.wakeLock.request('screen');

		// Re-acquire wake lock when page becomes visible again
		// (iOS releases it when switching apps or when page is hidden)
		visibilityHandler = async () => {
			if (document.visibilityState === 'visible' && wakeLock?.released) {
				try {
					wakeLock = await navigator.wakeLock.request('screen');
				} catch {
					// Failed to re-acquire — screen may turn off
				}
			}
		};
		document.addEventListener('visibilitychange', visibilityHandler);

		return true;
	} catch {
		return false;
	}
}

export async function releaseWakeLock(): Promise<void> {
	if (visibilityHandler) {
		document.removeEventListener('visibilitychange', visibilityHandler);
		visibilityHandler = null;
	}

	if (wakeLock && !wakeLock.released) {
		await wakeLock.release();
	}
	wakeLock = null;
}
