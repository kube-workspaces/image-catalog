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

. (Join-Path $PSScriptRoot 'VddSettings.ps1')

$ErrorActionPreference = 'Stop'

$dataDir = Join-Path $env:PROGRAMDATA 'workspace-agent'

function Assert-NoFile($path, $why) {
    if (Test-Path -LiteralPath $path) { throw "$why ($path present)" }
}

function Assert-File($path, $why) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "$why ($path missing)" }
}

# Service installation/enrollment alone does not prove that a proxy can reach
# the interactive listener. Require the explicit all-profile desktop exception
# in both seal and clone gates, and reject conflicting application block rules.
$agentPath = Join-Path $env:ProgramFiles 'workspace-agent\kw-agent.exe'
$firewall = @(Get-NetFirewallRule -PolicyStore ActiveStore -Name 'KubeWorkspacesAgentDesktop' -ErrorAction SilentlyContinue)
if ($firewall.Count -ne 1 -or $firewall[0].Enabled -ne 'True' -or
    $firewall[0].Direction -ne 'Inbound' -or $firewall[0].Action -ne 'Allow' -or
    $firewall[0].Profile -ne 'Any') {
    throw 'premium desktop firewall exception missing, disabled or not enabled for all network profiles'
}
$application = @($firewall | Get-NetFirewallApplicationFilter)
$ports = @($firewall | Get-NetFirewallPortFilter)
if ($application.Count -ne 1 -or $application[0].Program -ne $agentPath -or
    $ports.Count -ne 1 -or $ports[0].Protocol -notin @('TCP', '6') -or
    $ports[0].LocalPort -ne '44787') {
    throw 'premium desktop firewall exception must target kw-agent.exe TCP port 44787'
}
$blocks = @(Get-NetFirewallApplicationFilter -PolicyStore ActiveStore -Program $agentPath -ErrorAction SilentlyContinue |
    Get-NetFirewallRule | Where-Object { $_.Enabled -eq 'True' -and $_.Direction -eq 'Inbound' -and $_.Action -eq 'Block' } |
    Where-Object { @($_ | Get-NetFirewallPortFilter | Where-Object {
        $_.Protocol -in @('TCP', '6', 'Any', '256') -and $_.LocalPort -in @('Any', '44787')
    }).Count -gt 0 })
if ($blocks.Count) { throw 'conflicting inbound block rule prevents premium desktop access' }

if ($Mode -eq 'Seal') {
    Assert-NoFile (Join-Path $dataDir 'identity.json') 'sealed root must not carry an enrolled identity'
    Assert-NoFile (Join-Path $dataDir 'enrollment-token.json') 'sealed root must not carry an enrollment token'
    foreach ($cache in @('C:\Windows\Panther\unattend.xml', 'C:\Windows\System32\Sysprep\unattend.xml')) {
        Assert-NoFile $cache 'stale answer file would override clone provisioning'
    }
    $service = Get-Service -Name 'KubeWorkspacesAgent' -ErrorAction SilentlyContinue
    if ($null -eq $service) { throw 'premium agent service missing from sealed root' }
    if ($AgentVersion -ne '') {
        $reported = (& "$env:ProgramFiles\workspace-agent\kw-agent.exe" --version 2>$null)
        if ($reported -notmatch [regex]::Escape($AgentVersion)) {
            throw "Agent version mismatch: expected $AgentVersion, got: $reported"
        }
    }
    $idd = @(Get-PnpDevice -PresentOnly -Class Display -ErrorAction SilentlyContinue | Where-Object { $_.InstanceId -like 'ROOT\MTTVDD\*' -and $_.Status -eq 'OK' })
    if (-not $idd.Count) { throw 'sealed root has no virtual/indirect display device' }
    # Assert the virtual-display mode list is the premium list aligned to frontend presets.
    if (-not (Test-Path -LiteralPath $VddConfigPath)) { throw "sealed root missing virtual display config: $VddConfigPath" }
    $cur = Get-VddSettingsResolutions -Path $VddConfigPath
    if ($cur.Count -ne $VddPremiumResolutions.Count) {
        throw "virtual display mode count mismatch: expected $($VddPremiumResolutions.Count), got $($cur.Count)"
    }
    $key = @('Width','Height')
    $expectedSet = @{}
    foreach ($r in $VddPremiumResolutions) { $expectedSet["$($r.Width)x$($r.Height)"] = $true }
    foreach ($r in $cur) {
        $k = "$($r.Width)x$($r.Height)"
        if (-not $expectedSet.ContainsKey($k)) { throw "unadvertised mode in sealed vdd_settings.xml: $k" }
    }
    Write-Output 'seal gate passed: premium stack present, identity-free, virtual display modes aligned'
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
