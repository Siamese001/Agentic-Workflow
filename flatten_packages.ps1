# Flatten single-file packages
# PowerShell version for Windows

$errorActionPreference = "Stop"

# Read the bash script and convert paths
$bashScript = Get-Content "flatten_packages.sh"
foreach ($line in $bashScript) {
    if ($line.StartsWith("git mv ")) {
        # Convert git mv command
        $content = $line -replace 'git mv "', '' -replace '" "', '" -> "' -replace '"$', ''
        $parts = $content -split ' -> '
        if ($parts.Count -eq 2) {
            $old = $parts[0] -replace '\\', '\'
            $new = $parts[1] -replace '\\', '\'
            Write-Host "Moving: $old -> $new"
            if (Test-Path $old) {
                git mv $old $new
            }
        }
    } elseif ($line.StartsWith("rmdir ")) {
        # Remove directory
        $dir = $line -replace 'rmdir "', '' -replace '"$', ''
        $dir = $dir -replace '\\', '\'
        Write-Host "Removing directory: $dir"
        if (Test-Path $dir) {
            Remove-Item $dir -Force
        }
    }
}
