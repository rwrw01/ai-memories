#!/usr/bin/env bash
# Forward Windows port 3000 to WSL2 for Tailscale Funnel access.
# Launches the PowerShell script with admin elevation (UAC prompt).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PS_SCRIPT="$SCRIPT_DIR/update-wsl-portproxy.ps1"
POWERSHELL="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"

if [[ ! -f "$PS_SCRIPT" ]]; then
    echo "Error: $PS_SCRIPT not found"
    exit 1
fi

if [[ ! -f "$POWERSHELL" ]]; then
    echo "Error: powershell.exe not found at $POWERSHELL"
    exit 1
fi

WIN_SCRIPT=$(wslpath -w "$PS_SCRIPT")

echo "Launching port forwarding update (UAC prompt will appear on Windows)..."
"$POWERSHELL" -Command "Start-Process powershell -Verb RunAs -ArgumentList '-ExecutionPolicy Bypass -File \"$WIN_SCRIPT\"' -Wait"

echo ""
echo "Verifying..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
if [[ "$STATUS" == "200" ]]; then
    echo "OK: localhost:3000 returns HTTP 200"
else
    echo "WARNING: localhost:3000 returned HTTP $STATUS (frontend might not be running yet)"
fi
