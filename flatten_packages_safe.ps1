# Safely flatten single-file packages with validation
$errorActionPreference = "Stop"

# Get list of single-file packages directly
$packages = @()
Get-ChildItem -Recurse -Directory | ForEach-Object {
    $dir = $_
    if ($dir.Name -eq "__pycache__") { return }
    
    $children = Get-ChildItem $dir.FullName | Where-Object { $_.Name -ne "__pycache__" }
    if ($children.Count -eq 1 -and $children[0].Name -eq "__init__.py") {
        $packages += $dir
    }
}

Write-Host "Found $($packages.Count) single-file packages to flatten"

# Process each package
foreach ($pkg in $packages) {
    $initFile = Join-Path $pkg.FullName "__init__.py"
    $newFile = Join-Path $pkg.Parent.FullName "$($pkg.Name).py"
    
    Write-Host "Processing: $($pkg.FullName)"
    
    # Check if target already exists
    if (Test-Path $newFile) {
        Write-Host "  SKIP: Target already exists - $newFile" -ForegroundColor Yellow
        continue
    }
    
    # Move the file using git mv to preserve history
    try {
        $relInit = $initFile.Replace((Get-Location).Path + "\", "").Replace("\", "/")
        $relNew = $newFile.Replace((Get-Location).Path + "\", "").Replace("\", "/")
        
        Write-Host "  git mv `"$relInit`" `"$relNew`""
        git mv $relInit $relNew
        
        # Remove the empty directory
        Write-Host "  Removing empty directory: $($pkg.FullName)"
        Remove-Item $pkg.FullName -Force
    }
    catch {
        Write-Host "  ERROR: $_" -ForegroundColor Red
    }
}

Write-Host "Flattening complete!"
