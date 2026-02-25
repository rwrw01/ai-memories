# register-portproxy-task.ps1
# Register a Windows Task Scheduler task that updates WSL2 port forwarding at login.
# Must run as Administrator. Only needs to run once.

$ErrorActionPreference = "Stop"
$taskName = "WSL2 Port Forward 3000"
$scriptPath = Join-Path $PSScriptRoot "update-wsl-portproxy.ps1"

if (-not (Test-Path $scriptPath)) {
    Write-Error "Script not found: $scriptPath"
    exit 1
}

# Remove existing task if present
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Removed existing task: $taskName"
}

# Action: run the portproxy update script
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`""

# Trigger: at user logon, with 30s delay to let WSL2 start
$trigger = New-ScheduledTaskTrigger -AtLogOn
$trigger.Delay = "PT30S"

# Settings: run with highest privileges, allow on battery, don't stop if on battery
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

# Principal: run as current user with admin rights
$principal = New-ScheduledTaskPrincipal `
    -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) `
    -RunLevel Highest `
    -LogonType Interactive

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Update netsh portproxy to forward port 3000 to WSL2 NAT IP for Tailscale Funnel" | Out-Null

Write-Host "Scheduled task '$taskName' registered."
Write-Host "  Trigger: at logon (30s delay)"
Write-Host "  Script:  $scriptPath"
Write-Host "  Runs as: Admin (no UAC prompt)"
