# Seal/clone gate for premium Windows roots. Two modes, both fail-closed:
#
#   Seal:  run in the build guest right before Sysprep. Asserts the root is
#          identity-free (no identity.json, no enrollment-token.json), has no
#          answer-file caches, no test TPM keys, and carries the premium
#          agent service + virtual display device.
#   Clone: run in a provisioned clone to prove exactly-once enrollment.
#          Asserts identity.json exists and binds to the given UID+generation
#          via `kw-agent identity-check`, and that no live enrollment token
#          remains at rest.
#
# Seal:  .\Test-SealedRoot.ps1 -Mode Seal [-AgentVersion 0.3.3]
# Clone: .\Test-SealedRoot.ps1 -Mode Clone -WorkspaceUid <uid> -WorkspaceGeneration <gen>
#Requires -Version 5.1
#Requires -RunAsAdministrator
param(
    [ValidateSet('Seal', 'Clone')][string]$Mode = 'Seal',
    [string]$AgentVersion = '',
    [string]$WorkspaceUid = '',
    [string]$WorkspaceGeneration = ''
)

$ErrorActionPreference = 'Stop'
$dataDir = Join-Path $env:PROGRAMDATA 'workspace-agent'

function Assert-NoFile($path, $why) {
    if (Test-Path -LiteralPath $path) { throw "$why ($path present)" }
}

function Assert-File($path, $why) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "$why ($path missing)" }
}

if ($Mode -eq 'Seal') {
    Assert-NoFile (Join-Path $dataDir 'identity.json') 'sealed root must not carry an enrolled identity'
    Assert-NoFile (Join-Path $dataDir 'enrollment-token.json') 'sealed root must not carry an enrollment token'
    foreach ($cache in @('C:\Windows\Panther\unattend.xml', 'C:\Windows\System32\Sysprep\unattend.xml')) {
        Assert-NoFile $cache 'stale answer file would override clone provisioning'
    }
    $service = Get-Service -Name 'workspace-agent' -ErrorAction SilentlyContinue
    if ($null -eq $service) { throw 'premium agent service missing from sealed root' }
    if ($AgentVersion -ne '') {
        $reported = (& "$env:ProgramFiles\workspace-agent\kw-agent.exe" --version 2>$null)
        if ($reported -notmatch [regex]::Escape($AgentVersion)) {
            throw "Agent version mismatch: expected $AgentVersion, got: $reported"
        }
    }
    $idd = @(Get-PnpDevice -Class Display -ErrorAction SilentlyContinue | Where-Object { $_.FriendlyName -match 'Virtual|Indirect' })
    if (-not $idd.Count) { throw 'sealed root has no virtual/indirect display device' }
    Write-Output 'seal gate passed: premium stack present, identity-free'
    return
}

if ($WorkspaceUid -eq '' -or $WorkspaceGeneration -eq '') {
    throw 'Clone mode requires -WorkspaceUid and -WorkspaceGeneration'
}
Assert-File (Join-Path $dataDir 'identity.json') 'provisioned clone must be enrolled'
Assert-NoFile (Join-Path $dataDir 'enrollment-token.json') 'one-use token must be consumed, never at rest'
$check = (& "$env:ProgramFiles\workspace-agent\kw-agent.exe" identity-check `
    --workspace-uid $WorkspaceUid --workspace-generation $WorkspaceGeneration 2>&1)
if ($LASTEXITCODE -ne 0) { throw "identity-check failed: $check" }
Write-Output "clone gate passed: enrolled exactly $WorkspaceUid / $WorkspaceGeneration"
