# github-mirror.ps1 - fetch a GitHub URL through the fastest healthy public mirror.
# Auto-detects codeload health; caches probe results to a local JSON file (TTL ~60s).
param(
  [Parameter(Mandatory=$true)][string]$Url,
  [string]$OutFile = "",
  [int]$CacheTtlSeconds = 60
)
$ErrorActionPreference = "Stop"
$probeTimeout = 6
$dlTimeout = 25
$cacheDir = Join-Path $env:USERPROFILE ".dsh\vendor\github-mirror"
$cacheFile = Join-Path $cacheDir "cache.json"
$zipMirrors = @(
  'https://gh.ddlc.top/https://github.com',
  'https://gh.jasonzeng.dev/https://github.com',
  'https://ghfast.top/https://github.com',
  'https://wget.la/https://github.com',
  'https://gh.zwy.one/https://github.com',
  'https://gh.chjina.com/https://github.com',
  'https://gh.idayer.com/https://github.com',
  'https://github.geekery.cn/https://github.com',
  'https://ghproxy.net/https://github.com'
)
$rawMirrors = @(
  'https://wget.la/https://raw.githubusercontent.com',
  'https://ghfast.top/https://raw.githubusercontent.com',
  'https://hk.gh-proxy.org/https://raw.githubusercontent.com',
  'https://fastly.jsdelivr.net/gh'
)
function MakeMirrorUrl($mirror, $targetUrl) {
  if ($mirror -match 'jsdelivr') {
    $m = [regex]::Match($targetUrl, 'raw\.githubusercontent\.com\/([^\/]+)\/([^\/]+)\/([^\/]+)\/(.*)')
    if ($m.Success) { return ($mirror + '/' + $m.Groups[1].Value + '/' + $m.Groups[2].Value + '@' + $m.Groups[3].Value + '/' + $m.Groups[4].Value) }
    return $null
  }
  if ($targetUrl -like 'https://raw.githubusercontent.com*') { return ($mirror + $targetUrl.Substring('https://raw.githubusercontent.com'.Length)) }
  if ($targetUrl -like 'https://github.com*') { return ($mirror + $targetUrl.Substring('https://github.com'.Length)) }
  if ($targetUrl -like 'https://api.github.com*') { return ($mirror + $targetUrl.Substring('https://api.github.com'.Length)) }
  return $null
}
function Probe($mirror, $targetUrl) {
  $mu = MakeMirrorUrl $mirror $targetUrl
  if (-not $mu) { return -1 }
  try {
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $r = Invoke-WebRequest -Uri $mu -Method Get -TimeoutSec $probeTimeout -UseBasicParsing -ErrorAction Stop
    $sw.Stop()
    if ($r.StatusCode -eq 200) { return $sw.ElapsedMilliseconds }
  } catch {}
  return -1
}
function ReadJson($path) {
  try {
    $raw = [IO.File]::ReadAllText($path).TrimStart([char]0xFEFF) # strip BOM
    return $raw | ConvertFrom-Json
  } catch { return $null }
}
function WriteJson($path, $obj) {
  try { New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null } catch {}
  try { $json = $obj | ConvertTo-Json -Depth 4; [IO.File]::WriteAllText($path, $json, (New-Object System.Text.UTF8Encoding $false)) } catch {}
}
function FreshProbe($targetUrl, $mirrors) {
  $h = @()
  foreach ($m in $mirrors) {
    $ms = Probe $m $targetUrl
    if ($ms -ge 0) { $h += ,@($ms, (MakeMirrorUrl $m $targetUrl)) }
  }
  return ($h | Sort-Object { $_[0] })
}
function TryDownload($entry, $outFile) {
  try {
    if ($outFile) {
      Invoke-WebRequest -Uri $entry[1] -Method Get -TimeoutSec $dlTimeout -OutFile $outFile -UseBasicParsing
      $size = (Get-Item $outFile).Length
      if ($size -gt 0) { Write-Output ('MIRROR=' + $entry[1]); Write-Output ('BYTES=' + $size); return $true }
    } else {
      $content = (Invoke-WebRequest -Uri $entry[1] -Method Get -TimeoutSec $dlTimeout -UseBasicParsing).Content
      Write-Output ('MIRROR=' + $entry[1]); Write-Output $content; return $true
    }
  } catch {}
  return $false
}
$targetUrl = $Url
$kind = if ($targetUrl -like '*raw.githubusercontent.com*') { 'raw' } else { 'zip' }
$mirrors = if ($kind -eq 'raw') { $rawMirrors } else { $zipMirrors }
$cache = ReadJson $cacheFile
$now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$cachedList = $null
if ($cache -and $cache.updatedAt -and ($now - [int64]$cache.updatedAt) -lt $CacheTtlSeconds) { $cachedList = if ($kind -eq 'raw') { $cache.raw } else { $cache.zip } }
$healthy = @()
$cacheHit = $false
if ($cachedList -is [array] -and $cachedList.Count -gt 0) { $healthy = @($cachedList | ForEach-Object { @([int64]$_.latency, $_.url) }); $cacheHit = $true }
if ($cacheHit) {
  $tried = 0
  foreach ($h in $healthy) { if ($tried -ge 3) { break }; $tried++; if (TryDownload $h $OutFile) { Write-Output ('CACHE=HIT (ttl=' + $CacheTtlSeconds + 's)'); exit 0 } }
  Write-Output 'CACHE=STALE_RETRY_FRESH'
  $healthy = FreshProbe $targetUrl $mirrors
  $tried = 0
  foreach ($h in $healthy) { if ($tried -ge 3) { break }; $tried++; if (TryDownload $h $OutFile) { exit 0 } }
} else {
  Write-Output 'CACHE=MISS (fresh probe)'
  $healthy = FreshProbe $targetUrl $mirrors
  $top = @($healthy | Select-Object -First 3 | ForEach-Object { @{ url = $_[1]; latency = $_[0] } })
  $cacheObj = if ($cache) { $cache } else { @{} }
  $cacheObj.updatedAt = $now
  if ($kind -eq 'raw') { $cacheObj.raw = $top } else { $cacheObj.zip = $top }
  WriteJson $cacheFile $cacheObj
  $tried = 0
  foreach ($h in $healthy) { if ($tried -ge 3) { break }; $tried++; if (TryDownload $h $OutFile) { exit 0 } }
}
Write-Output 'MIRROR=DIRECT_FALLBACK'
try {
  if ($OutFile) { Invoke-WebRequest -Uri $targetUrl -Method Get -TimeoutSec $dlTimeout -OutFile $OutFile -UseBasicParsing; Write-Output ('BYTES=' + (Get-Item $OutFile).Length) }
  else { (Invoke-WebRequest -Uri $targetUrl -Method Get -TimeoutSec $dlTimeout -UseBasicParsing).Content }
  exit 0
} catch { Write-Output ('ALL_FAILED: ' + $_.Exception.Message); exit 1 }