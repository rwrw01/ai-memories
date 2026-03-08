"""Keyword-based intent classifier for Dutch voice commands.

Replaces the previous Ollama/Qwen3-8B LLM classifier with simple regex
keyword matching — instant (<1ms), no external dependencies, no network calls.
"""

import re

# Ordered from most specific to most generic.
# First match wins.  Each entry:
#   trigger  – compiled regex (IGNORECASE) that must appear in the text
#   intent   – canonical intent name
#   extract  – function(match, full_text) → params dict
_RULES: list[dict] = []


def _register(pattern: str, intent: str, extract):
    _RULES.append({
        "trigger": re.compile(pattern, re.IGNORECASE),
        "intent": intent,
        "extract": extract,
    })


# --- WhatsApp: "whatsapp naar Peter dat ik later kom" / "stuur een berichtje naar Maria" ---
def _extract_whatsapp(match: re.Match, text: str) -> dict:
    rest = text[match.end():].strip()
    # Try to split "naar <contact> <bericht>"
    m = re.match(r"(?:naar|aan)\s+(\w+)\s*(.*)", rest, re.IGNORECASE | re.DOTALL)
    if m:
        return {"contact": m.group(1), "bericht": m.group(2).strip() or rest}
    return {"contact": "", "bericht": rest or text}

_register(
    r"\bwhatsapp\b|\bstuur\s+(?:een\s+)?(?:bericht|berichtje)\b",
    "whatsapp",
    _extract_whatsapp,
)


# --- Artikel: "artikel over duurzame energie" ---
def _extract_artikel(match: re.Match, text: str) -> dict:
    rest = text[match.end():].strip()
    # Strip leading "over" if present
    rest = re.sub(r"^over\s+", "", rest, flags=re.IGNORECASE)
    return {"onderwerp": rest or text, "brontekst": text}

_register(r"\bartikel\b", "artikel", _extract_artikel)


# --- Uren: "uren 8 uur project alpha" ---
def _extract_uren(match: re.Match, text: str) -> dict:
    rest = text[match.end():].strip()
    return {"tekst": rest or text}

_register(r"\buren\b", "uren", _extract_uren)


# --- Aantekening / notitie: "notitie vergadering verzet" / "onthoud dat ..." ---
def _extract_notitie(match: re.Match, text: str) -> dict:
    rest = text[match.end():].strip()
    # Strip leading "dat" if present
    rest = re.sub(r"^dat\s+", "", rest, flags=re.IGNORECASE)
    return {"tekst": rest or text}

_register(
    r"\bnotitie\b|\bnotities\b|\baantekening\b|\bonthoud\b|\bschrijf\s+op\b",
    "aantekening",
    _extract_notitie,
)


async def classify(transcription: str) -> dict:
    """Classify a Dutch transcription into an intent with parameters.

    Pure keyword matching — no network calls, no external dependencies.
    Returns the same shape as the old LLM classifier for full compatibility.
    """
    text = transcription.strip()
    if not text:
        return _fallback(transcription)

    for rule in _RULES:
        match = rule["trigger"].search(text)
        if match:
            params = rule["extract"](match, text)
            return {
                "intent": rule["intent"],
                "params": params,
                "confidence": 1.0,
            }

    return _fallback(transcription)


def _fallback(transcription: str) -> dict:
    """No keyword matched — default to aantekening (text goes to PWA)."""
    return {
        "intent": "aantekening",
        "params": {"tekst": transcription},
        "confidence": 1.0,
    }
