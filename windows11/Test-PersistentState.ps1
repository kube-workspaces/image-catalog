# Run elevated on a disposable guest. Public-key metadata only; no TPM secrets.
# Create before graceful Stop/Start; Verify after a different VMI UID; Remove
# before sealing a build guest. Never recreate a missing key during verification.
param(
    [ValidateSet('Create', 'Verify', 'Remove')]
    [string]$Action = 'Verify',
    [string]$KeyName = 'KubeWorkspacesPersistenceProof',
    [string]$RecordPath = 'C:\ProgramData\KubeWorkspaces\PersistenceProof.json'
)

$ErrorActionPreference = 'Stop'
$provider = [System.Security.Cryptography.CngProvider]::new('Microsoft Platform Crypto Provider')
$options = [System.Security.Cryptography.CngKeyOpenOptions]::MachineKey
$exists = [System.Security.Cryptography.CngKey]::Exists($KeyName, $provider, $options)

if ($Action -eq 'Remove') {
    if ($exists) {
        $key = [System.Security.Cryptography.CngKey]::Open($KeyName, $provider, $options)
        try { $key.Delete() } finally { $key.Dispose() }
    }
    Remove-Item -LiteralPath $RecordPath -ErrorAction SilentlyContinue
    Write-Output 'Persistence proof key and record removed'
    exit 0
}

if ($Action -eq 'Create') {
    if ($exists -or (Test-Path -LiteralPath $RecordPath)) {
        throw 'Proof key/record already exists; choose another name or explicitly remove it'
    }
    $parameters = [System.Security.Cryptography.CngKeyCreationParameters]::new()
    $parameters.Provider = $provider
    $parameters.KeyCreationOptions = [System.Security.Cryptography.CngKeyCreationOptions]::MachineKey
    $parameters.KeyUsage = [System.Security.Cryptography.CngKeyUsages]::Signing
    $parameters.ExportPolicy = [System.Security.Cryptography.CngExportPolicies]::None
    $key = [System.Security.Cryptography.CngKey]::Create(
        [System.Security.Cryptography.CngAlgorithm]::Rsa, $KeyName, $parameters)
} else {
    if (!$exists -or !(Test-Path -LiteralPath $RecordPath)) {
        throw 'Existing TPM key or root record is missing; persistence is not proven'
    }
    $key = [System.Security.Cryptography.CngKey]::Open($KeyName, $provider, $options)
}

try {
    if (!$key.IsMachineKey -or $key.Provider.Provider -ne $provider.Provider) {
        throw 'Proof key is not a machine key in the TPM provider'
    }
    $hash = [System.Security.Cryptography.SHA256]::Create()
    try {
        $publicHash = ([BitConverter]::ToString($hash.ComputeHash(
            $key.Export([System.Security.Cryptography.CngKeyBlobFormat]::GenericPublicBlob)))).Replace('-', '')
    } finally { $hash.Dispose() }
    if ($Action -eq 'Create') {
        $record = @{ marker = [guid]::NewGuid().ToString(); publicKeySHA256 = $publicHash }
        New-Item -ItemType Directory -Path (Split-Path -Parent $RecordPath) -Force | Out-Null
        $record | ConvertTo-Json | Set-Content -LiteralPath $RecordPath -Encoding UTF8
    } else {
        $record = Get-Content -LiteralPath $RecordPath -Raw | ConvertFrom-Json
        if ($record.publicKeySHA256 -ne $publicHash) { throw 'TPM public key changed across restart' }
    }
    $rsa = [System.Security.Cryptography.RSACng]::new($key)
    try {
        $nonce = [guid]::NewGuid().ToByteArray()
        $algorithm = [System.Security.Cryptography.HashAlgorithmName]::SHA256
        $padding = [System.Security.Cryptography.RSASignaturePadding]::Pkcs1
        $signature = $rsa.SignData($nonce, $algorithm, $padding)
        if (!$rsa.VerifyData($nonce, $signature, $algorithm, $padding)) {
            throw 'TPM-backed signature verification failed'
        }
    } finally { $rsa.Dispose() }
    @{ action = $Action; marker = $record.marker; publicKeySHA256 = $publicHash;
       provider = $provider.Provider; signatureVerified = $true } | ConvertTo-Json -Compress
} finally { $key.Dispose() }
