# Invoked from Secret-backed Sysprep media during specialise. No credentials.
$ErrorActionPreference = 'Stop'
$media = Get-PSDrive -PSProvider FileSystem | Where-Object {
    Test-Path ($_.Root + 'guest-agent\qemu-ga-x86_64.msi')
} | Select-Object -First 1
if (-not $media) { throw 'Pinned VirtIO driver media is missing' }
foreach ($driver in @('viostor', 'NetKVM', 'vioserial', 'Balloon')) {
    $path = $media.Root + $driver + '\w11\amd64\'
    $files = @(Get-ChildItem -LiteralPath $path -Filter '*.inf')
    if (-not $files.Count) { throw "Pinned driver INF is missing: $driver" }
    & pnputil.exe /add-driver ($path + '*.inf') /install
    $result = $LASTEXITCODE
    if ($result -eq 259) {
        # ERROR_NO_MORE_ITEMS also means every matching package/device is
        # already up-to-date. Verify the supplied packages are in DriverStore;
        # do not confuse that idempotent result with an absent driver.
        $installed = @((Get-WindowsDriver -Online).OriginalFileName | ForEach-Object {
            [IO.Path]::GetFileName($_)
        })
        foreach ($file in $files) {
            if ($file.Name -notin $installed) {
                throw "Driver was not installed: $($file.Name)"
            }
        }
    } elseif ($result -notin @(0, 3010)) {
        throw "Driver installation failed: $driver (exit $result)"
    }
}
$installer = Start-Process msiexec.exe -ArgumentList @(
    '/i', ($media.Root + 'guest-agent\qemu-ga-x86_64.msi'), '/qn', '/norestart'
) -Wait -PassThru
if ($installer.ExitCode -notin @(0, 3010)) {
    throw "Guest agent installation failed (exit $($installer.ExitCode))"
}
Start-Service QEMU-GA
