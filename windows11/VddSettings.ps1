# Shared premium virtual-display (IDD) configuration, dot-sourced by the
# install recipe and the seal gate.
#
# The pinned Virtual Display Driver ("Virtual Display Driver", Root\MttVDD)
# advertises a bounded mode list read from
#   C:\VirtualDisplayDriver\vdd_settings.xml
# (directory override: HKLM\SOFTWARE\MikeTheTech\VirtualDisplayDriver\VDDPATH).
# The emulated Basic Display VGA is a single fixed mode, so the streamed output
# must be the virtual display: workspace-agent prefers it by default and every
# guest resolution change is a CDS mode change on that adapter.
#
# Keep $VddPremiumResolutions in step with the frontend's fixed guest-resolution
# presets (frontend/src/lib/agent-protocol.ts, fixedResolutionPresets) so every
# advertised choice is actually available. The driver fails to initialise when
# the resolution/refresh combination count gets large (observed near 96); this
# list stays far below that.

$VddConfigDir = 'C:\VirtualDisplayDriver'
$VddConfigPath = Join-Path $VddConfigDir 'vdd_settings.xml'
$VddRefreshRate = 60

$VddPremiumResolutions = @(
    [pscustomobject]@{ Width = 800;  Height = 600  }
    [pscustomobject]@{ Width = 1024; Height = 768  }
    [pscustomobject]@{ Width = 1280; Height = 720  }
    [pscustomobject]@{ Width = 1280; Height = 800  }
    [pscustomobject]@{ Width = 1280; Height = 960  }
    [pscustomobject]@{ Width = 1280; Height = 1024 }
    [pscustomobject]@{ Width = 1366; Height = 768  }
    [pscustomobject]@{ Width = 1440; Height = 900  }
    [pscustomobject]@{ Width = 1600; Height = 900  }
    [pscustomobject]@{ Width = 1600; Height = 1200 }
    [pscustomobject]@{ Width = 1680; Height = 1050 }
    [pscustomobject]@{ Width = 1920; Height = 1080 }
    [pscustomobject]@{ Width = 1920; Height = 1200 }
    [pscustomobject]@{ Width = 2048; Height = 1152 }
    [pscustomobject]@{ Width = 2560; Height = 1440 }
    [pscustomobject]@{ Width = 2560; Height = 1600 }
    [pscustomobject]@{ Width = 3440; Height = 1440 }
    [pscustomobject]@{ Width = 3840; Height = 2160 }
)

# Render the vdd_settings.xml document for the given modes. Single monitor,
# RGB SDR, hardware cursor, no custom EDID; only the resolution list varies.
function Get-VddSettingsXml {
    param(
        [Parameter(Mandatory = $true)][object[]]$Resolutions,
        [int]$RefreshRate = 60
    )
    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add('<?xml version="1.0" encoding="utf-8"?>')
    $lines.Add('<vdd_settings>')
    $lines.Add('  <monitors>')
    $lines.Add('    <count>1</count>')
    $lines.Add('  </monitors>')
    $lines.Add('  <gpu>')
    $lines.Add('    <friendlyname>default</friendlyname>')
    $lines.Add('  </gpu>')
    $lines.Add('  <resolutions>')
    foreach ($mode in $Resolutions) {
        $lines.Add('    <resolution>')
        $lines.Add("      <width>$($mode.Width)</width>")
        $lines.Add("      <height>$($mode.Height)</height>")
        $lines.Add("      <refresh_rate>$RefreshRate</refresh_rate>")
        $lines.Add('    </resolution>')
    }
    $lines.Add('  </resolutions>')
    $lines.Add('  <logging>')
    $lines.Add('    <logging>false</logging>')
    $lines.Add('    <debuglogging>false</debuglogging>')
    $lines.Add('    <SendLogsThroughPipe>false</SendLogsThroughPipe>')
    $lines.Add('  </logging>')
    $lines.Add('  <colour>')
    $lines.Add('    <SDR10bit>false</SDR10bit>')
    $lines.Add('    <HDRPlus>false</HDRPlus>')
    $lines.Add('    <ColourFormat>RGB</ColourFormat>')
    $lines.Add('  </colour>')
    $lines.Add('  <cursor>')
    $lines.Add('    <HardwareCursor>true</HardwareCursor>')
    $lines.Add('  </cursor>')
    $lines.Add('  <edid>')
    $lines.Add('    <CustomEdid>false</CustomEdid>')
    $lines.Add('  </edid>')
    $lines.Add('</vdd_settings>')
    return ($lines -join [Environment]::NewLine)
}

# Write the standard premium mode list to the driver's config path. Call before
# the driver first starts (or reload afterwards) so it is read at start-up.
function Write-VddSettings {
    param(
        [string]$Path = $VddConfigPath,
        [object[]]$Resolutions = $VddPremiumResolutions,
        [int]$RefreshRate = $VddRefreshRate
    )
    $dir = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    $xml = Get-VddSettingsXml -Resolutions $Resolutions -RefreshRate $RefreshRate
    Set-Content -LiteralPath $Path -Value $xml -Encoding UTF8
    return $Path
}

# Read back the resolutions advertised by a vdd_settings.xml file.
function Get-VddSettingsResolutions {
    param([Parameter(Mandatory = $true)][string]$Path)
    $doc = New-Object System.Xml.XmlDocument
    $doc.Load($Path)
    return @($doc.vdd_settings.resolutions.resolution | ForEach-Object {
        [pscustomobject]@{ Width = [int]$_.width; Height = [int]$_.height }
    })
}

# Ask the running driver to reload its configuration over the control pipe
# (\\.\pipe\MTTVirtualDisplayPipe, command as UTF-16LE). Best-effort: a fresh
# driver start already reads the config, so a failure is only fatal on re-runs,
# where the caller decides whether to retry or require a reboot.
function Invoke-VddDriverReload {
    [CmdletBinding()]
    param(
        [string]$PipeName = 'MTTVirtualDisplayPipe',
        [int]$TimeoutMs = 2000,
        [int]$Attempts = 1
    )
    for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
        $client = $null
        try {
            $client = New-Object System.IO.Pipes.NamedPipeClientStream(
                '.', $PipeName, [System.IO.Pipes.PipeDirection]::InOut)
            $client.Connect($TimeoutMs)
            $payload = [System.Text.Encoding]::Unicode.GetBytes('RELOAD_DRIVER')
            $client.Write($payload, 0, $payload.Length)
            $client.Flush()
            return $true
        } catch {
            if ($attempt -eq $Attempts) {
                Write-Warning "virtual display reload unavailable: $($_.Exception.Message)"
                return $false
            }
            Start-Sleep -Seconds 1
        } finally {
            if ($null -ne $client) { $client.Dispose() }
        }
    }
    return $false
}
