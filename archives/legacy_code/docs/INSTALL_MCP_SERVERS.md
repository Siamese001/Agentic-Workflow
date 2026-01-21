# MCP Server Installation Guide - Windows

## Prerequisites Installation

### Step 1: Install Node.js

MCP servers require Node.js 18+ to run. Install it first:

1. **Download Node.js**:
   - Visit: https://nodejs.org/
   - Download the **LTS version** (Long Term Support)
   - Choose Windows Installer (.msi) - 64-bit

2. **Run the Installer**:
   - Double-click the downloaded `.msi` file
   - Follow the installation wizard
   - **Important**: Check "Automatically install necessary tools" option
   - Complete the installation

3. **Verify Installation**:
   ```powershell
   node --version
   npm --version
   npx --version
   ```

   You should see version numbers for all three commands.

4. **Restart PowerShell/Terminal** after installation to refresh PATH.

---

## MCP Server Installation

Once Node.js is installed, run these commands in PowerShell:

### 1. DockerHub MCP Server
```powershell
npx -y @modelcontextprotocol/server-dockerhub
```

### 2. Context7 MCP Server
```powershell
npx -y @context7/mcp-server
```

### 3. Figma MCP Server
```powershell
npx -y @modelcontextprotocol/server-figma
```

### 4. Reddit MCP Server
```powershell
npx -y @modelcontextprotocol/server-reddit
```

### 5. Sequential Thinking MCP Server
```powershell
npx -y @modelcontextprotocol/server-sequential-thinking
```

### 6. Playwright MCP Server
```powershell
npx -y @executeautomation/playwright-mcp-server
```

---

## Environment Variables Setup

### Required API Keys

1. **Figma Access Token** (for Figma MCP):
   - Go to: https://www.figma.com/developers/api#access-tokens
   - Generate a personal access token
   - Copy the token

2. **Reddit API Credentials** (for Reddit MCP):
   - Go to: https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App"
   - Choose "script" type
   - Note your `client_id` and `client_secret`

### Set Environment Variables (Windows)

**Option A: System Environment Variables (Permanent)**

1. Press `Win + X` and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables", click "New"
5. Add each variable:

```
Variable Name: FIGMA_ACCESS_TOKEN
Value: your_figma_token_here

Variable Name: REDDIT_CLIENT_ID
Value: your_reddit_client_id

Variable Name: REDDIT_CLIENT_SECRET
Value: your_reddit_secret

Variable Name: REDDIT_USER_AGENT
Value: AgenticFramework/1.0
```

**Option B: PowerShell Session (Temporary)**

```powershell
$env:FIGMA_ACCESS_TOKEN = "your_figma_token_here"
$env:REDDIT_CLIENT_ID = "your_reddit_client_id"
$env:REDDIT_CLIENT_SECRET = "your_reddit_secret"
$env:REDDIT_USER_AGENT = "AgenticFramework/1.0"
```

**Option C: .env File (Recommended for Development)**

Create a `.env` file in `c:/Git/Agentic-Workflow/`:

```bash
# Figma MCP
FIGMA_ACCESS_TOKEN=your_figma_token_here

# Reddit MCP
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=AgenticFramework/1.0
```

Then install `python-dotenv`:
```powershell
pip install python-dotenv
```

---

## Verification

### Test MCP Integration

Run this Python script to verify all MCPs are accessible:

```powershell
cd c:/Git/Agentic-Workflow
python -c "from runtime.shared.workflow.mcp_integration import MCPIntegrationManager; mgr = MCPIntegrationManager(); print(f'Loaded {len(mgr.servers)} MCP servers:', mgr.list_servers())"
```

Expected output:
```
Loaded 6 MCP servers: ['dockerhub', 'context7', 'figma', 'reddit', 'sequential-thinking', 'playwright']
```

### Test Individual MCP Servers

**Test DockerHub MCP:**
```powershell
npx @modelcontextprotocol/server-dockerhub
# Should start without errors
```

**Test Playwright MCP:**
```powershell
npx @executeautomation/playwright-mcp-server
# Should start without errors
```

---

## Troubleshooting

### Issue: "npx: The term 'npx' is not recognized"

**Solution**: Node.js is not installed or not in PATH.
1. Install Node.js from https://nodejs.org/
2. Restart PowerShell/Terminal
3. Verify with `node --version`

### Issue: "Cannot find module '@modelcontextprotocol/server-dockerhub'"

**Solution**: Package not installed.
```powershell
npm install -g @modelcontextprotocol/server-dockerhub
```

### Issue: "FIGMA_ACCESS_TOKEN not set"

**Solution**: Set environment variable (see above) and restart your terminal/IDE.

### Issue: MCP server starts but immediately exits

**Solution**: Check server logs and ensure all dependencies are installed:
```powershell
npm install -g playwright
npx playwright install
```

---

## Quick Install Script (All-in-One)

Save this as `install_all_mcps.ps1`:

```powershell
# Install all MCP servers
Write-Host "Installing MCP Servers..." -ForegroundColor Green

$servers = @(
    "@modelcontextprotocol/server-dockerhub",
    "@context7/mcp-server",
    "@modelcontextprotocol/server-figma",
    "@modelcontextprotocol/server-reddit",
    "@modelcontextprotocol/server-sequential-thinking",
    "@executeautomation/playwright-mcp-server"
)

foreach ($server in $servers) {
    Write-Host "Installing $server..." -ForegroundColor Yellow
    npx -y $server --version
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ $server installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ $server installation failed" -ForegroundColor Red
    }
}

Write-Host "`nAll MCP servers installed!" -ForegroundColor Green
Write-Host "Don't forget to set environment variables for Figma and Reddit MCPs" -ForegroundColor Yellow
```

Run with:
```powershell
powershell -ExecutionPolicy Bypass -File install_all_mcps.ps1
```

---

## Next Steps

After installation:

1. **Set environment variables** for Figma and Reddit
2. **Test integration** with the verification script above
3. **Review the integration guide**: `docs/MCP_INTEGRATION_GUIDE.md`
4. **Start using MCP-enhanced agents**:
   ```python
   from runtime.shared.workflow.mcp_integration import K11MCPEnhancer

   enhancer = K11MCPEnhancer()
   research = await enhancer.autonomous_company_research("TechCorp")
   ```

---

## Support

If you encounter issues:
1. Check Node.js version: `node --version` (should be 18+)
2. Check npm cache: `npm cache clean --force`
3. Reinstall specific MCP: `npm install -g <package-name>`
4. Review logs in `runtime/logs/mcp_integration.log`

For more help, see: https://modelcontextprotocol.io/docs
