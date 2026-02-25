# update-wsl-portproxy.ps1
# Forward Windows port 3000 to WSL2 NAT IP for Tailscale Funnel access.
# Must run as Administrator (netsh requires elevation).

$ErrorActionPreference = "Stop"

# Get WSL2 IP
$wslIp = (wsl hostname -I).Trim().Split(" ")[0]
if (-not $wslIp) {
    Write-Error "Could not determine WSL2 IP. Is WSL running?"
    exit 1
}
Write-Host "WSL2 IP: $wslIp"

# Update port forwarding for frontend (port 3000)
netsh interface portproxy delete v4tov4 listenport=3000 listenaddress=0.0.0.0 2>$null
netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=$wslIp
Write-Host "Port 3000 -> WSL2 ($wslIp):3000"

# Create firewall rule if it doesn't exist yet
if (-not (Get-NetFirewallRule -DisplayName "WSL2 Frontend 3000" -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName "WSL2 Frontend 3000" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 3000 | Out-Null
    Write-Host "Firewall rule created: WSL2 Frontend 3000"
} else {
    Write-Host "Firewall rule already exists: WSL2 Frontend 3000"
}

# Show current portproxy rules
Write-Host ""
Write-Host "Active port forwarding rules:"
netsh interface portproxy show v4tov4

Write-Host ""
Write-Host "Done. Tailscale Funnel should now reach the frontend."
