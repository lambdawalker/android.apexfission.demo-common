$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$config = Get-Content -LiteralPath (Join-Path $project '.project/setup/config.yaml') -Raw
$match = [regex]::Match($config, '(?m)^tooling_ref: [''" ]*(v\d+\.\d+\.\d+|[0-9a-f]{40})[''" ]*\r?$')
if (-not $match.Success) { throw 'Invalid tooling_ref in .project/setup/config.yaml' }
$reference = $match.Groups[1].Value
$destination = Join-Path (Join-Path $project 'bin') $reference
if ($reference.StartsWith('v')) {
    $executable = Join-Path $destination 'android-repo-setup.exe'
    if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
        & (Join-Path $PSScriptRoot 'install-setup-cli.ps1') -Version $reference
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
} else {
    $executable = Join-Path $destination 'bin/android-repo-setup.exe'
    if (-not (Test-Path -LiteralPath $executable -PathType Leaf)) {
        & cargo install --locked --root $destination --git https://github.com/lambdawalker/gradle.android-repo-setup.git --rev $reference android-repo-setup
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
}
& $executable --project $project @args
exit $LASTEXITCODE
