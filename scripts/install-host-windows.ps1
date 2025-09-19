[CmdletBinding()]
param(
    [ValidateSet("chrome", "edge")]
    [string]$Browser = "chrome"
)

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$manifestTemplatePath = Join-Path $repoRoot "native\com.yourorg.researchdownload.json"
$launcherPath = Join-Path $repoRoot "native\dist\researchdownload_host.cmd"

if (-not (Test-Path -Path $manifestTemplatePath)) {
    throw "Unable to find manifest template at $manifestTemplatePath"
}

if (-not (Test-Path -Path $launcherPath)) {
    throw "Unable to find launcher at $launcherPath. Ensure the .cmd shim exists."
}

$resolvedLauncherPath = (Resolve-Path -Path $launcherPath).Path
$manifestTemplate = Get-Content -Path $manifestTemplatePath -Raw | ConvertFrom-Json
$manifestTemplate.path = $resolvedLauncherPath

switch ($Browser) {
    "chrome" {
        $targetDir = Join-Path $env:LOCALAPPDATA "Google\Chrome\User Data\NativeMessagingHosts"
    }
    "edge" {
        $targetDir = Join-Path $env:LOCALAPPDATA "Microsoft\Edge\User Data\NativeMessagingHosts"
    }
}

New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
$targetManifestPath = Join-Path $targetDir "com.yourorg.researchdownload.json"
$manifestJson = $manifestTemplate | ConvertTo-Json -Depth 5
$manifestJson | Set-Content -Path $targetManifestPath -Encoding UTF8

Write-Host "Installed ResearchDownload host manifest to $targetManifestPath"
Write-Host "Host launcher path: $resolvedLauncherPath"
