# Fix all indentation errors caused by the reorganization
# Pattern: except ...:\n    pass\npass\nlogger.error

Get-ChildItem -Path "." -Filter "*.py" -Recurse | ForEach-Object {
    $file = $_.FullName
    $content = Get-Content $file -Raw

    # Fix the malformed exception blocks
    $pattern = '(?s)(\s+except\s+.*?:\s*\n)\s+pass\n\s+pass\n(.+?logger\.error)'
    $replacement = '$1            $2'

    if ($content -match $pattern) {
        $newContent = $content -replace $pattern, $replacement
        Set-Content $file $newContent -NoNewline
        Write-Host "Fixed: $file"
    }
}

Write-Host "Done fixing indentation errors."
