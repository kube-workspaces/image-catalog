# Installs the premium workspace-agent stack into the build guest BEFORE
# sealing: the pinned kw-agent MSI plus the approved virtual-display
# driver package and writes a standard vdd_settings.xml (modes aligned
# to the frontend presets). Operator supplies both on local media; the
# repository distributes no Windows binaries.
#
# The install must leave the guest UNENROLLED: no identity.json, no
# enrollment-token.json, no account credentials. Enrollment happens per
# clone at first boot through the controller-staged token (clone-only
# enrollment). Run Test-SealedRoot.ps1 afterwards to prove it.
#
# From elevated PowerShell:
#   .\Install-PremiumAgent.ps1 -AgentMsi C:\media\workspace-agent-v0.3.3-windows-amd64.msi `
#     -IddDriverDir C:\media\vdd-25.7.23 -AgentVersion 0.3.3 `
#     -VcRedistPath C:\media\vc_redist.x64.exe
#Requires -Version 5.1
#Requires -RunAsAdministrator
param(
    [Parameter(Mandatory = $true)][string]$AgentMsi,
    [Parameter(Mandatory = $true)][string]$IddDriverDir,
    [Parameter(Mandatory = $true)][string]$AgentVersion,
    [string]$VcRedistPath = (Join-Path $PSScriptRoot 'vc_redist.x64.exe'),
    [string]$InstallLogPath = (Join-Path $env:TEMP 'workspace-agent-install.log'),
    [string]$IddPublisherThumbprint = '3CF8CF26D8BA266C3A483AB7D26D4A818E317D76'
)

. (Join-Path $PSScriptRoot 'VddSettings.ps1')

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $AgentMsi -PathType Leaf)) { throw "Agent MSI missing: $AgentMsi" }
if (-not (Test-Path -LiteralPath $IddDriverDir -PathType Container)) { throw "IDD driver dir missing: $IddDriverDir" }
$infs = @(Get-ChildItem -LiteralPath $IddDriverDir -Filter '*.inf' -Recurse)
if ($infs.Count -ne 1) { throw 'Expected exactly one approved IDD INF' }

$dataDir = Join-Path $env:PROGRAMDATA 'workspace-agent'
foreach ($secret in @('identity.json', 'enrollment-token.json')) {
    if (Test-Path -LiteralPath (Join-Path $dataDir $secret)) {
        throw "Build guest already enrolled ($secret present): start from a clean root, never seal an identity"
    }
}

# A native agent needs the x64 Visual C++ runtime. Stage it with the other
# operator-pinned inputs rather than downloading from the build guest.
$runtimeDlls = @('vcruntime140.dll', 'vcruntime140_1.dll')
$missingRuntime = @($runtimeDlls | Where-Object { -not (Test-Path (Join-Path "$env:WINDIR\System32" $_)) })
if ($missingRuntime.Count) {
    if (-not (Test-Path -LiteralPath $VcRedistPath -PathType Leaf)) { throw 'VC++ runtime installer missing' }
    $runtime = Start-Process -FilePath $VcRedistPath -ArgumentList @('/install', '/quiet', '/norestart') -Wait -PassThru
    if ($runtime.ExitCode -notin @(0, 3010, 1638)) { throw "VC++ runtime install failed: $($runtime.ExitCode)" }
    foreach ($dll in $runtimeDlls) {
        if (-not (Test-Path (Join-Path "$env:WINDIR\System32" $dll))) { throw "VC++ runtime DLL missing after installation: $dll" }
    }
    Write-Output "VC++ runtime installed (exit $($runtime.ExitCode))"
}

# Trust only the explicitly pinned publisher of the approved, signed catalog.
$catalogs = @(Get-ChildItem -LiteralPath $IddDriverDir -Filter '*.cat' -Recurse)
if ($catalogs.Count -ne 1) { throw 'Expected exactly one approved IDD catalog' }
$signature = Get-AuthenticodeSignature $catalogs[0].FullName
if ($signature.Status -ne 'Valid' -or $null -eq $signature.SignerCertificate -or
    $signature.SignerCertificate.Thumbprint -ne $IddPublisherThumbprint) {
    throw 'IDD catalog signature or publisher pin does not match'
}
$store = [System.Security.Cryptography.X509Certificates.X509Store]::new('TrustedPublisher', 'LocalMachine')
$store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
try { $store.Add($signature.SignerCertificate) } finally { $store.Close() }

# Write the aligned mode list before starting/reloading the display driver.
Write-VddSettings
& pnputil.exe /add-driver $infs[0].FullName /install
# 259 is an already-current package; devnode health is checked independently.
if ($LASTEXITCODE -notin @(0, 259, 3010)) { throw "IDD package staging failed: $LASTEXITCODE" }
& (Join-Path $PSScriptRoot 'Install-RootDisplayDevice.ps1') -InfPath $infs[0].FullName

# Reload the virtual display driver so it reads the updated mode list (best-effort).
[void](Invoke-VddDriverReload -Attempts 3)

# Verify the configured mode list was written.
if (-not (Test-Path -LiteralPath $VddConfigPath)) { throw "Virtual display config missing: $VddConfigPath" }
$cur = Get-VddSettingsResolutions -Path $VddConfigPath
if ($cur.Count -ne $VddPremiumResolutions.Count) {
    throw "Virtual display mode count mismatch: expected $($VddPremiumResolutions.Count), got $($cur.Count)"
}

$logDirectory = Split-Path -Parent $InstallLogPath
if ($logDirectory) { New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null }
$installer = Start-Process msiexec.exe -ArgumentList @('/i', ('"{0}"' -f $AgentMsi), '/qn', '/norestart', '/L*v', ('"{0}"' -f $InstallLogPath)) -Wait -PassThru
if ($installer.ExitCode -notin @(0, 3010)) {
    if (Test-Path -LiteralPath $InstallLogPath) {
        Write-Warning (Get-Content -LiteralPath $InstallLogPath -Tail 50 | Out-String)
    }
    throw "Agent MSI installation failed (exit $($installer.ExitCode))"
}

$service = Get-Service -Name 'KubeWorkspacesAgent' -ErrorAction SilentlyContinue
if ($null -eq $service) { throw 'KubeWorkspacesAgent service missing after MSI install' }

$reported = (& "$env:ProgramFiles\workspace-agent\kw-agent.exe" --version 2>$null)
if ($reported -notmatch [regex]::Escape($AgentVersion)) {
    throw "Agent version mismatch: expected $AgentVersion, got: $reported"
}

$idd = @(Get-PnpDevice -PresentOnly -Class Display -ErrorAction SilentlyContinue | Where-Object { $_.InstanceId -like 'ROOT\MTTVDD\*' -and $_.Status -eq 'OK' })
if (-not $idd.Count) { throw 'No virtual/indirect display device after IDD install' }

foreach ($secret in @('identity.json', 'enrollment-token.json')) {
    if (Test-Path -LiteralPath (Join-Path $dataDir $secret)) {
        throw "Install enrolled the guest ($secret present): the seal must stay identity-free"
    }
}

Write-Output "premium agent $AgentVersion installed, IDD present, guest unenrolled"
