# MCP Server Installation Script for Windows PowerShell
# Installs all 6 MCP servers for the Agentic Framework

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "MCP Server Installation for Agentic Framework" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>$null
    $npmVersion = npm --version 2>$null

    if ($nodeVersion -and $npmVersion) {
        Write-Host "✓ Node.js version: $nodeVersion" -ForegroundColor Green
        Write-Host "✓ npm version: $npmVersion" -ForegroundColor Green
    } else {
        throw "Node.js not found"
    }
} catch {
    Write-Host "✗ Node.js is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Node.js first:" -ForegroundColor Yellow
    Write-Host "1. Visit: https://nodejs.org/" -ForegroundColor White
    Write-Host "2. Download the LTS version" -ForegroundColor White
    Write-Host "3. Run the installer" -ForegroundColor White
    Write-Host "4. Restart PowerShell and run this script again" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installing MCP Servers..." -ForegroundColor Green
Write-Host ""

# Define MCP servers to install
$servers = @(
    @{Name="DockerHub"; Package="@modelcontextprotocol/server-dockerhub"},
    @{Name="Context7"; Package="@context7/mcp-server"},
    @{Name="Figma"; Package="@modelcontextprotocol/server-figma"},
    @{Name="Reddit"; Package="@modelcontextprotocol/server-reddit"},
    @{Name="Sequential Thinking"; Package="@modelcontextprotocol/server-sequential-thinking"},
    @{Name="Playwright"; Package="@executeautomation/playwright-mcp-server"}
)

$successCount = 0
$failCount = 0

foreach ($server in $servers) {
    Write-Host "[$($servers.IndexOf($server) + 1)/6] Installing $($server.Name) MCP Server..." -ForegroundColor Yellow

    try {
        # Try to run the package with npx to verify/install
        $output = npx -y $server.Package --version 2>&1

        if ($LASTEXITCODE -eq 0 -or $output -match "version") {
            Write-Host "  ✓ $($server.Name) installed successfully" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "  ✗ $($server.Name) installation failed" -ForegroundColor Red
            Write-Host "    Error: $output" -ForegroundColor DarkRed
            $failCount++
        }
    } catch {
        Write-Host "  ✗ $($server.Name) installation failed" -ForegroundColor Red
        Write-Host "    Error: $_" -ForegroundColor DarkRed
        $failCount++
    }

    Write-Host ""
}

# Summary
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor White
Write-Host "  ✓ Successfully installed: $successCount/6" -ForegroundColor Green
if ($failCount -gt 0) {
    Write-Host "  ✗ Failed: $failCount/6" -ForegroundColor Red
}
Write-Host ""

# Next steps
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Set Environment Variables (Required for some MCPs):" -ForegroundColor White
Write-Host "   For Figma MCP:" -ForegroundColor Cyan
Write-Host "   `$env:FIGMA_ACCESS_TOKEN = 'your_token_here'" -ForegroundColor Gray
Write-Host ""
Write-Host "   For Reddit MCP:" -ForegroundColor Cyan
Write-Host "   `$env:REDDIT_CLIENT_ID = 'your_client_id'" -ForegroundColor Gray
Write-Host "   `$env:REDDIT_CLIENT_SECRET = 'your_secret'" -ForegroundColor Gray
Write-Host "   `$env:REDDIT_USER_AGENT = 'AgenticFramework/1.0'" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Verify Installation:" -ForegroundColor White
Write-Host "   python -c `"from runtime.shared.workflow.mcp_integration import MCPIntegrationManager; mgr = MCPIntegrationManager(); print(f'Loaded {len(mgr.servers)} MCP servers:', mgr.list_servers())`"" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Review Integration Guide:" -ForegroundColor White
Write-Host "   docs/MCP_INTEGRATION_GUIDE.md" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Review Installation Guide:" -ForegroundColor White
Write-Host "   docs/INSTALL_MCP_SERVERS.md" -ForegroundColor Gray
Write-Host ""

if ($successCount -eq 6) {
    Write-Host "All MCP servers installed successfully! 🎉" -ForegroundColor Green
} elseif ($successCount -gt 0) {
    Write-Host "Some MCP servers installed. Check errors above for failed installations." -ForegroundColor Yellow
} else {
    Write-Host "No MCP servers were installed. Please check Node.js installation and try again." -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
