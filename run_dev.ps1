param(
  [ValidateSet('lan','ngrok')]
  [string]$Mode = 'lan',
  [int]$Port = 8000,
  [string]$Host = '',            # LAN IPv4 override (e.g., 192.168.1.23)
  [string]$NgrokDomain = '',     # e.g., abc123.ngrok-free.app
  [string]$PythonPath = 'venv\Scripts\python.exe'
)

function Get-LocalIPv4 {
  try {
    $ip = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
      Where-Object { $_.IPAddress -match '^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[0-1])\.)' } |
      Select-Object -ExpandProperty IPAddress -First 1
    if (-not $ip) {
      $match = ipconfig | Select-String -Pattern 'IPv4 Address\s*\.\s*:\s*(?<ip>\d+\.\d+\.\d+\.\d+)' | Select-Object -First 1
      if ($match) { $ip = $match.Matches[0].Groups['ip'].Value }
    }
    return $ip
  } catch { return $null }
}

switch ($Mode) {
  'lan' {
    if (-not $Host) { $Host = Get-LocalIPv4 }
    if (-not $Host) { Write-Host "Could not detect LAN IP. Pass -Host 192.168.x.x" -ForegroundColor Yellow; exit 1 }
    $env:ALLOWED_HOSTS = "127.0.0.1,localhost,$Host"
    Remove-Item Env:CSRF_TRUSTED_ORIGINS -ErrorAction SilentlyContinue
    Write-Host "ALLOWED_HOSTS=$env:ALLOWED_HOSTS" -ForegroundColor Cyan
    & $PythonPath manage.py runserver "0.0.0.0:$Port"
  }
  'ngrok' {
    if (-not $NgrokDomain) { Write-Host "Provide -NgrokDomain (e.g., abc123.ngrok-free.app)" -ForegroundColor Yellow; exit 1 }
    $env:ALLOWED_HOSTS = "127.0.0.1,localhost,$NgrokDomain"
    $env:CSRF_TRUSTED_ORIGINS = "https://$NgrokDomain"
    Write-Host "ALLOWED_HOSTS=$env:ALLOWED_HOSTS" -ForegroundColor Cyan
    Write-Host "CSRF_TRUSTED_ORIGINS=$env:CSRF_TRUSTED_ORIGINS" -ForegroundColor Cyan
    Write-Host "Start ngrok in another terminal: ngrok http $Port" -ForegroundColor Green
    & $PythonPath manage.py runserver "0.0.0.0:$Port"
  }
}

