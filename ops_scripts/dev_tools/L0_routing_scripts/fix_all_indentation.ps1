# Comprehensive fix for all indentation errors
# Pattern: except ...:\n    pass\npass\nlogger.error

Write-Host "Scanning for indentation errors..."

$files = Get-ChildItem -Path "." -Filter "*.py" -Recurse
$fixedCount = 0

foreach ($file in $files) {
    $content = Get-Content $file -Raw

    # Multiple patterns to catch all variations
    $patterns = @(
        '(?s)(\s+except\s+.*?:\s*\n)\s+pass\n\s+pass\n(.+?logger\.)',
        '(?s)(\s+except\s+.*?:\s*\n)\s+pass\n\s+pass\n(.+?return)',
        '(?s)(\s+except\s+.*?:\s*\n)\s+pass\n\s+pass\s*\n(.+?)',
        '(?s)\n\s+pass\n\s+pass\n(.+?logger\.)',
        '(?s)\n\s+pass\n\s+pass\n(.+?return)'
    )

    $changed = $false
    foreach ($pattern in $patterns) {
        if ($content -match $pattern) {
            # Fix by removing the pass statements and properly indenting the next line
            $content = $content -replace $pattern, '$1            $2'
            $changed = $true
        }
    }

    if ($changed) {
        Set-Content $file $content -NoNewline
        Write-Host "Fixed: $($file.FullName)"
        $fixedCount++
    }
}

Write-Host "Fixed $fixedCount files with indentation errors."
