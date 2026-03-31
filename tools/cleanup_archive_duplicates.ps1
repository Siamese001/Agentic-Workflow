# Simple PowerShell script to clean up archive duplicates

$archiveDir = "C:\Git\Agentic-Workflow\artifacts\adg\_archive\2026-03"

# Get all zip files
$zipFiles = Get-ChildItem -Path $archiveDir -Name "*.zip.gz"

Write-Host "Found $($zipFiles.Count) zip files"
Write-Host "Checking for duplicates..."

$totalFreed = 0
$filesRemoved = 0

foreach ($zipFile in $zipFiles) {
    # Extract timestamp from zip filename
    # Pattern: adg_run_MMDDYYYY_HHMM.zip.gz
    if ($zipFile -match "adg_run_(\d{8}_\d{4})\.zip\.gz") {
        $timestamp = $matches[1]
        Write-Host "`nProcessing timestamp: $timestamp"

        # Find individual files with this timestamp (excluding zip files)
        $individualFiles = Get-ChildItem -Path $archiveDir -Name "*$timestamp*.gz" | Where-Object { $_ -notlike "*.zip.gz" }

        if ($individualFiles.Count -gt 0) {
            Write-Host "  Found $($individualFiles.Count) individual files to remove:"

            foreach ($file in $individualFiles) {
                $filePath = Join-Path $archiveDir $file
                $fileSize = (Get-Item $filePath).Length
                Write-Host "    Removing: $file ($([math]::Round($fileSize/1MB, 2)) MB)"

                Remove-Item $filePath -Force
                $totalFreed += $fileSize
                $filesRemoved++
            }

            Write-Host "  Keeping: $zipFile"
        }
    }
}

Write-Host "`nCleanup Complete!"
Write-Host "Files removed: $filesRemoved"
Write-Host "Space freed: $([math]::Round($totalFreed/1MB, 1)) MB"

# Verify cleanup
$remainingFiles = Get-ChildItem -Path $archiveDir -Name "*.gz" | Where-Object { $_ -notlike "*.zip.gz" }
Write-Host "Remaining individual files: $($remainingFiles.Count)"

if ($remainingFiles.Count -eq 0) {
    Write-Host "✅ Archive is now efficient!"
} else {
    Write-Host "⚠️  Still have $($remainingFiles.Count) individual files remaining"
}
