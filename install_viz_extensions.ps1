# VS Code Extension Installation Script for Data Visualization
# Run this in PowerShell to automatically install required extensions

Write-Host "🚀 Installing VS Code Extensions for Data Visualization..." -ForegroundColor Green

# Function to install extensions
function Install-VSCodeExtension {
    param([string]$ExtensionId, [string]$Name)
    
    Write-Host "Installing $Name..." -ForegroundColor Yellow
    
    # Try different VS Code executable paths
    $vscodePaths = @(
        "${env:LOCALAPPDATA}\Programs\Microsoft VS Code\bin\code.cmd",
        "${env:ProgramFiles}\Microsoft VS Code\bin\code.cmd",
        "${env:ProgramFiles(x86)}\Microsoft VS Code\bin\code.cmd",
        "code"
    )
    
    $installed = $false
    foreach ($codePath in $vscodePaths) {
        try {
            if (Test-Path $codePath -ErrorAction SilentlyContinue) {
                & $codePath --install-extension $ExtensionId --force 2>$null
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ $Name installed successfully" -ForegroundColor Green
                    $installed = $true
                    break
                }
            } elseif ($codePath -eq "code") {
                & code --install-extension $ExtensionId --force 2>$null
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ $Name installed successfully" -ForegroundColor Green
                    $installed = $true
                    break
                }
            }
        } catch {
            continue
        }
    }
    
    if (-not $installed) {
        Write-Host "⚠️  Could not install $Name automatically" -ForegroundColor Red
        Write-Host "   Please install manually: Extensions → Search '$ExtensionId'" -ForegroundColor Yellow
    }
}

# Essential extensions for data visualization
$extensions = @(
    @{Id="ritwickdey.liveserver"; Name="Live Server - Launch HTML dashboards"},
    @{Id="mechatroner.rainbow-csv"; Name="Rainbow CSV - Color-coded CSV files"},
    @{Id="janisdd.vscode-edit-csv"; Name="Edit CSV - Interactive CSV editing"},
    @{Id="ms-python.python"; Name="Python - Core Python support"},
    @{Id="ms-toolsai.jupyter"; Name="Jupyter - Notebook support"},
    @{Id="davidanson.vscode-markdownlint"; Name="Markdown Lint - Better markdown"},
    @{Id="formulahendry.auto-rename-tag"; Name="Auto Rename Tag - HTML editing"},
    @{Id="esbenp.prettier-vscode"; Name="Prettier - Code formatting"}
)

Write-Host "Installing ${extensions.Count} extensions..." -ForegroundColor Cyan

foreach ($ext in $extensions) {
    Install-VSCodeExtension -ExtensionId $ext.Id -Name $ext.Name
}

Write-Host "`n🎯 Installation Complete!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Restart VS Code to activate extensions" -ForegroundColor Yellow
Write-Host "2. Open dashboard: http://localhost:8080/autonomy_dashboard.html" -ForegroundColor Yellow
Write-Host "3. Right-click HTML files → 'Open with Live Server'" -ForegroundColor Yellow

# Launch dashboard in default browser
Write-Host "`n🌐 Opening dashboard in browser..." -ForegroundColor Green
Start-Process "http://localhost:8080/autonomy_dashboard.html"
