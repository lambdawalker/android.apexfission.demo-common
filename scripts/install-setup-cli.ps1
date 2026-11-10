param(
    [Parameter(Mandatory)]
    [ValidatePattern('\Av[0-9]+\.[0-9]+\.[0-9]+\z')]
    [string]$Version
)

$ErrorActionPreference = 'Stop'
$bin = Join-Path (Split-Path -Parent $PSScriptRoot) 'bin'
$destination = Join-Path $bin $Version
$executable = Join-Path $destination 'android-repo-setup.exe'
$archive = 'android-repo-setup-x86_64-pc-windows-msvc.zip'
$url = "https://github.com/lambdawalker/gradle.android-repo-setup/releases/download/$Version"
$stage = Join-Path $bin ('.download-' + [guid]::NewGuid().ToString('N'))

try {
    New-Item -ItemType Directory -Path $stage -Force | Out-Null
    $zip = Join-Path $stage $archive
    $checksum = "$zip.sha256"
    # Windows PowerShell 5.1 may otherwise default to an older TLS protocol.
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Write-Host "Downloading Android Repository Setup $Version..."
    Invoke-WebRequest -UseBasicParsing -Uri "$url/$archive" -OutFile $zip -TimeoutSec 90
    Invoke-WebRequest -UseBasicParsing -Uri "$url/$archive.sha256" -OutFile $checksum -TimeoutSec 30
    $line = (Get-Content -LiteralPath $checksum -Raw).Trim()
    $match = [regex]::Match($line, '\A([a-fA-F0-9]{64}) [ *]' + [regex]::Escape($archive) + '\z')
    if (-not $match.Success) {
        throw 'The release checksum has an unexpected format.'
    }
    $hasher = [Security.Cryptography.SHA256]::Create()
    $stream = [IO.File]::OpenRead($zip)
    try {
        $actualHash = [BitConverter]::ToString($hasher.ComputeHash($stream)).Replace('-', '')
    } finally {
        $stream.Dispose()
        $hasher.Dispose()
    }
    if ($actualHash -ne $match.Groups[1].Value) {
        throw 'The downloaded CLI archive failed SHA-256 verification.'
    }

    $payload = Join-Path $stage 'payload'
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [IO.Compression.ZipFile]::ExtractToDirectory($zip, $payload)
    $stagedExe = Join-Path $payload 'android-repo-setup.exe'
    $reportedVersion = & $stagedExe --version
    if ($LASTEXITCODE -ne 0 -or $reportedVersion -ne "android-repo-setup $($Version.Substring(1))") {
        throw 'The downloaded CLI reported an unexpected version.'
    }

    try {
        [IO.Directory]::Move($payload, $destination)
    } catch {
        # A concurrent launcher may already have installed this version.
        if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) { throw }
    }
} catch {
    [Console]::Error.WriteLine("Could not install Android Repository Setup $Version. $($_.Exception.Message)")
    exit 1
} finally {
    if (Test-Path -LiteralPath $stage) {
        Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
    }
}
