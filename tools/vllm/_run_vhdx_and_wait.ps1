# Helper: shut WSL down, wait, then check VHDX/log status.
# Used to give the elevated optimize_vhdx.ps1 script a clear window to grab the VHDX.

$logPath = "C:\Git\Agentic-Workflow\artifacts\vhdx_optimize.log"
$vhdx = "C:\Users\amita\AppData\Local\wsl\{358ed4de-0575-4f25-973c-dacd8fec83c2}\ext4.vhdx"

Write-Host "Shutting down WSL to release VHDX lock..."
wsl --shutdown
Start-Sleep -Seconds 8

Write-Host "Waiting up to 5 min for Optimize-VHD to complete (NOT touching wsl during this)..."
$end = (Get-Date).AddMinutes(5)
$lastSize = (Get-Item $vhdx).Length

while ((Get-Date) -lt $end) {
    Start-Sleep -Seconds 15
    if (Test-Path $logPath) {
        $contents = Get-Content $logPath -Raw -ErrorAction SilentlyContinue
        if ($contents -match "----DONE----") {
            Write-Host "Script signaled DONE at $(Get-Date -Format HH:mm:ss)"
            break
        }
    }
    $cur = (Get-Item $vhdx).Length
    $sizeGB = [math]::Round($cur / 1GB, 2)
    $delta = $cur - $lastSize
    Write-Host "  $(Get-Date -Format HH:mm:ss)  vhdx=${sizeGB} GB  delta=$delta"
    $lastSize = $cur
}

Write-Host ""
Write-Host "=== Final log ==="
if (Test-Path $logPath) {
    Get-Content $logPath
} else {
    Write-Host "(no log written - elevated PS may not have started)"
}

Write-Host ""
Write-Host "=== VHDX final size ==="
$v = Get-Item $vhdx
$gb = [math]::Round($v.Length / 1GB, 2)
Write-Host "  $gb GB  ($($v.LastWriteTime))"
