# Installs the premium workspace-agent stack into the build guest BEFORE
# sealing: the pinned kw-agent MSI plus the approved virtual-display
# driver package. Operator supplies both on local media; the repository
# distributes no Windows binaries.
#
# The install must leave the guest UNENROLLED: no identity.json, no
# enrollment-token.json, no account credentials. Enrollment happens per
# clone at first boot through the controller-staged token (clone-only
# enrollment). Run Test-SealedRoot.ps1 afterwards to prove it.
#
# From elevated PowerShell:
#   .\Install-PremiumAgent.ps1 -AgentMsi C:\media\workspace-agent-v0.3.3-windows-amd64.msi `
#     -IddDriverDir C:\media\vdd-25.7.23 -AgentVersion 0.3.3
#Requires -Version 5.1
#Requires -RunAsAdministrator
param(
    [Parameter(Mandatory = $true)][string]$AgentMsi,
    [Parameter(Mandatory = $true)][string]$IddDriverDir,
    [Parameter(Mandatory = $true)][string]$AgentVersion
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $AgentMsi -PathType Leaf)) { throw "Agent MSI missing: $AgentMsi" }
if (-not (Test-Path -LiteralPath $IddDriverDir -PathType Container)) { throw "IDD driver dir missing: $IddDriverDir" }
$infs = @(Get-ChildItem -LiteralPath $IddDriverDir -Filter '*.inf' -Recurse)
if (-not $infs.Count) { throw "No IDD INF in $IddDriverDir" }

$dataDir = Join-Path $env:PROGRAMDATA 'workspace-agent'
foreach ($secret in @('identity.json', 'enrollment-token.json')) {
    if (Test-Path -LiteralPath (Join-Path $dataDir $secret)) {
        throw "Build guest already enrolled ($secret present): start from a clean root, never seal an identity"
    }
}

& pnputil.exe /add-driver (Join-Path $IddDriverDir '*.inf') /install
$result = $LASTEXITCODE
if ($result -notin @(0, 3010)) { throw "IDD driver installation failed (exit $result)" }

$installer = Start-Process msiexec.exe -ArgumentList @('/i', $AgentMsi, '/qn', '/norestart') -Wait -PassThru
if ($installer.ExitCode -notin @(0, 3010)) { throw "Agent MSI installation failed (exit $($installer.ExitCode))" }

$service = Get-Service -Name 'workspace-agent' -ErrorAction SilentlyContinue
if ($null -eq $service) { throw 'workspace-agent service missing after MSI install' }

$reported = (& "$env:ProgramFiles\workspace-agent\kw-agent.exe" --version 2>$null)
if ($reported -notmatch [regex]::Escape($AgentVersion)) {
    throw "Agent version mismatch: expected $AgentVersion, got: $reported"
}

$idd = @(Get-PnpDevice -Class Display -ErrorAction SilentlyContinue | Where-Object { $_.FriendlyName -match 'Virtual|Indirect' })
if (-not $idd.Count) { throw 'No virtual/indirect display device after IDD install' }

foreach ($secret in @('identity.json', 'enrollment-token.json')) {
    if (Test-Path -LiteralPath (Join-Path $dataDir $secret)) {
        throw "Install enrolled the guest ($secret present): the seal must stay identity-free"
    }
}

Write-Output "premium agent $AgentVersion installed, IDD present, guest unenrolled"
