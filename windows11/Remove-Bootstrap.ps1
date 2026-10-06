# Run elevated after confirmed OOBE, before detaching Secret-backed Sysprep media.
# Removes only the native setup pointer and cached/backup answer files.
$ErrorActionPreference = 'Stop'
$state = (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Setup\State').ImageState
if ($state -ne 'IMAGE_STATE_COMPLETE') {
    throw 'Windows Setup has not completed; do not remove its bootstrap files'
}
Remove-ItemProperty 'HKLM:\SYSTEM\Setup' -Name UnattendFile -ErrorAction SilentlyContinue
$removed = @()
foreach ($base in @('C:\Windows\Panther', 'C:\Windows\System32\Sysprep')) {
    foreach ($file in (Get-ChildItem $base -Recurse -File -Filter '*unattend*.xml')) {
        $removed += $file.FullName
        Remove-Item -LiteralPath $file.FullName -Force
    }
}
@{ imageState = $state; removedPaths = $removed;
   pointerRemoved = $null -eq (Get-ItemProperty 'HKLM:\SYSTEM\Setup' -Name UnattendFile -ErrorAction SilentlyContinue).UnattendFile } |
    ConvertTo-Json -Compress
