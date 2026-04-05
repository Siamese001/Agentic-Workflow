# Remove all empty directories in the repository
# Runs multiple passes to handle nested empty directories

$repoRoot = "c:/Git/Agentic-Workflow"
$maxPasses = 10
$pass = 0
$removedCount = 0

Write-Host "Starting empty directory removal..."

do {
    $pass++
    $passRemovedCount = 0

    # Get all directories, sorted by depth (deepest first)
    $dirs = Get-ChildItem -Path $repoRoot -Directory -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '\\\.git\\' -and $_.FullName -notmatch '\\__pycache__\\' } |
        Sort-Object { $_.FullName.Split('\').Count } -Descending

    foreach ($dir in $dirs) {
        # Check if directory is empty (no files and no subdirectories)
        $items = Get-ChildItem -Path $dir.FullName -Force -ErrorAction SilentlyContinue
        if ($items.Count -eq 0) {
            try {
                Remove-Item -Path $dir.FullName -Force -ErrorAction Stop
                Write-Host "Removed: $($dir.FullName)"
                $passRemovedCount++
                $removedCount++
            }
            catch {
                Write-Warning "Failed to remove: $($dir.FullName) - $($_.Exception.Message)"
            }
        }
    }

    Write-Host "Pass $pass completed: Removed $passRemovedCount directories"

} while ($passRemovedCount -gt 0 -and $pass -lt $maxPasses)

Write-Host "`nTotal directories removed: $removedCount"
Write-Host "Empty directory removal complete!"
