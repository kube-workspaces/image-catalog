# Run elevated in a disposable Windows proof guest. No credentials/recovery keys.
param([Parameter(Mandatory=$true)][string]$OutputPath)
$ErrorActionPreference = 'Stop'
$os = Get-CimInstance Win32_OperatingSystem
$system = Get-CimInstance Win32_ComputerSystem
$tpm = Get-Tpm
$tpmDevice = Get-CimInstance -Namespace root/CIMV2/Security/MicrosoftTpm -ClassName Win32_Tpm
$secureBoot = Confirm-SecureBootUEFI
$agent = Get-Service -Name QEMU-GA -ErrorAction SilentlyContinue
$evidence = [ordered]@{
    CollectedAtUTC = (Get-Date).ToUniversalTime().ToString('o')
    Edition = $os.Caption
    Version = $os.Version
    Build = $os.BuildNumber
    Hostname = $system.Name
    FirmwareUUID = (Get-CimInstance Win32_ComputerSystemProduct).UUID
    Processors = @(Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors)
    MemoryBytes = $system.TotalPhysicalMemory
    SecureBoot = $secureBoot
    TPM = [ordered]@{Present=$tpm.TpmPresent; Ready=$tpm.TpmReady; Enabled=$tpm.TpmEnabled; SpecVersion=$tpmDevice.SpecVersion}
    Agent = if ($agent) { $agent.Status.ToString() } else { 'NotInstalled' }
    Disks = @(Get-Disk | Select-Object Number, FriendlyName, SerialNumber, PartitionStyle, Size, OperationalStatus)
    Network = @(Get-NetAdapter | Select-Object Name, InterfaceDescription, Status, LinkSpeed)
    Display = @(Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, VideoModeDescription)
    VirtIODrivers = @(Get-CimInstance Win32_PnPSignedDriver | Where-Object {$_.DeviceName -match 'VirtIO|Red Hat|QEMU'} | Select-Object DeviceName, DriverVersion, IsSigned, Signer)
}
$evidence | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
if (-not $secureBoot -or -not $tpm.TpmPresent -or -not $tpm.TpmReady -or $tpmDevice.SpecVersion -notmatch '^2\.0') {
    throw 'Windows proof failed: Secure Boot and a ready TPM 2.0 are required. See the evidence file.'
}
Write-Output 'Evidence collected. Separately capture dxdiag, VNC usability and restart/TPM-bound persistence results.'
