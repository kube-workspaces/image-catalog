# Create the root-enumerated devnode; pnputil only stages/binds driver packages.
#Requires -RunAsAdministrator
param([Parameter(Mandatory = $true)][string]$InfPath)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $InfPath)) { throw "Missing INF: $InfPath" }
$existing = @(Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -like 'ROOT\MTTVDD\*' })
if (-not $existing.Count) {
    Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Text;
public static class RootDisplayDevice {
    [StructLayout(LayoutKind.Sequential)]
    struct DeviceInfo { public uint cbSize; public Guid ClassGuid; public uint DevInst; public IntPtr Reserved; }
    [DllImport("setupapi.dll", SetLastError=true)]
    static extern IntPtr SetupDiCreateDeviceInfoList(ref Guid guid, IntPtr hwnd);
    [DllImport("setupapi.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    static extern bool SetupDiCreateDeviceInfoW(IntPtr set, string name, ref Guid guid, string description, IntPtr hwnd, uint flags, ref DeviceInfo data);
    [DllImport("setupapi.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    static extern bool SetupDiSetDeviceRegistryPropertyW(IntPtr set, ref DeviceInfo data, uint property, byte[] buffer, uint length);
    [DllImport("setupapi.dll", SetLastError=true)]
    static extern bool SetupDiCallClassInstaller(uint function, IntPtr set, ref DeviceInfo data);
    [DllImport("setupapi.dll", SetLastError=true)]
    static extern bool SetupDiDestroyDeviceInfoList(IntPtr set);
    [DllImport("newdev.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    static extern bool UpdateDriverForPlugAndPlayDevicesW(IntPtr hwnd, string hardwareId, string inf, uint flags, out bool reboot);
    static void Check(bool ok, string operation) {
        if (!ok) throw new Win32Exception(Marshal.GetLastWin32Error(), operation);
    }
    public static bool Install(string inf) {
        Guid guid = new Guid("4d36e968-e325-11ce-bfc1-08002be10318");
        IntPtr set = SetupDiCreateDeviceInfoList(ref guid, IntPtr.Zero);
        if (set == new IntPtr(-1)) throw new Win32Exception(Marshal.GetLastWin32Error());
        try {
            DeviceInfo data = new DeviceInfo(); data.cbSize = (uint)Marshal.SizeOf(typeof(DeviceInfo));
            Check(SetupDiCreateDeviceInfoW(set, @"ROOT\MTTVDD\0000", ref guid, "Virtual Display Driver", IntPtr.Zero, 0, ref data), "Create root display devnode");
            byte[] hardware = Encoding.Unicode.GetBytes("Root\\MttVDD\0\0");
            Check(SetupDiSetDeviceRegistryPropertyW(set, ref data, 1, hardware, (uint)hardware.Length), "Set hardware ID");
            Check(SetupDiCallClassInstaller(0x19, set, ref data), "Register root display devnode");
        } finally { SetupDiDestroyDeviceInfoList(set); }
        bool reboot;
        Check(UpdateDriverForPlugAndPlayDevicesW(IntPtr.Zero, @"Root\MttVDD", inf, 1, out reboot), "Bind staged display driver");
        return reboot;
    }
}
'@
    $reboot = [RootDisplayDevice]::Install((Resolve-Path -LiteralPath $InfPath).Path)
    Write-Output "Root display installed; reboot required: $reboot"
    if ($reboot) { throw 'Display device requires a reboot before validation' }
}
$device = @(Get-PnpDevice -PresentOnly -Class Display | Where-Object { $_.InstanceId -like 'ROOT\MTTVDD\*' })
if (-not $device.Count -or @($device | Where-Object { $_.Status -ne 'OK' }).Count) {
    throw 'Root display device is missing or unhealthy'
}
$device | Format-Table Status,FriendlyName,InstanceId -AutoSize
