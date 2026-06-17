# Complete MCP Server Configuration - Historical & Current

## Overview
This document contains the **complete MCP server configuration** for legacy editor, including all servers found in historical commits and archives.

**Total MCP Servers Configured**: 28

---

## Installation Location
**File**: `C:\Users\amita\AppData\Roaming\legacy editor\User\settings.json`

---

## Complete MCP Server List

### Core Infrastructure (Always-On)

#### 1. **Playwright** - Browser Automation
- **Package**: `@executeautomation/playwright-mcp-server`
- **Purpose**: Web automation, testing, scraping
- **Priority**: HIGH
- **Status**: ✅ Installed

#### 2. **Sequential Thinking** - Advanced Reasoning
- **Package**: `@modelcontextprotocol/server-sequential-thinking`
- **Purpose**: Multi-step reasoning, chain-of-thought
- **Priority**: HIGH
- **Status**: ✅ Installed

#### 3. **Filesystem** - File Operations
- **Package**: `@modelcontextprotocol/server-filesystem`
- **Root**: `c:\Git\Agentic-Workflow`
- **Priority**: HIGH
- **Status**: ✅ Installed

#### 4. **Memory** - Persistent Context
- **Package**: `@modelcontextprotocol/server-memory`
- **Purpose**: Store/retrieve conversation context
- **Priority**: HIGH
- **Status**: ✅ Installed

---

### Version Control & Code Management

#### 5. **GitHub** - Repository Operations
- **Package**: `@modelcontextprotocol/server-github`
- **Env**: `GITHUB_PERSONAL_ACCESS_TOKEN`
- **Priority**: HIGH
- **Status**: ✅ Installed

#### 6. **Git** - Local Version Control
- **Package**: `@modelcontextprotocol/server-git`
- **Repository**: `c:\Git\Agentic-Workflow`
- **Priority**: HIGH
- **Status**: ✅ Installed

#### 7. **GitKraken** - Advanced Git UI
- **Command**: `gk.exe` (GitLens integration)
- **Purpose**: Visual git operations, PR management
- **Priority**: MEDIUM
- **Status**: ✅ Installed
- **Note**: Uses GitLens MCP bridge

---

### Search & Web Access

#### 8. **Brave Search** - Web Search
- **Package**: `@modelcontextprotocol/server-brave-search`
- **Env**: `BRAVE_API_KEY`
- **Priority**: HIGH
- **Status**: ✅ Installed

#### 9. **Fetch** - HTTP Requests
- **Package**: `@modelcontextprotocol/server-fetch`
- **Purpose**: HTTP requests to external APIs
- **Priority**: HIGH
- **Status**: ✅ Installed

---

### Database & Storage

#### 10. **PostgreSQL** - Relational Database
- **Package**: `@modelcontextprotocol/server-postgres`
- **Connection**: `postgresql://localhost/agentic_workflow`
- **Priority**: HIGH
- **Status**: ✅ Installed

#### 11. **SQLite** - Local Database
- **Package**: `@modelcontextprotocol/server-sqlite`
- **DB Path**: `c:\Git\Agentic-Workflow\data\agentic.db`
- **Priority**: HIGH
- **Status**: ✅ Installed

#### 12. **Redis** - In-Memory Cache
- **Package**: `@modelcontextprotocol/server-redis`
- **Env**: `REDIS_URL`
- **Priority**: HIGH
- **Status**: ✅ Installed

#### 13. **Pinecone** - Vector Database
- **Package**: `@pinecone-database/mcp`
- **Env**: `PINECONE_API_KEY`
- **Priority**: HIGH
- **Status**: ✅ Installed

#### 14. **ChromaDB** - Vector Store
- **Package**: `@modelcontextprotocol/server-chromadb`
- **Env**: `CHROMA_URL`
- **Priority**: MEDIUM
- **Status**: ✅ Installed

---

### Browser Automation

#### 15. **Puppeteer** - Headless Browser
- **Package**: `@modelcontextprotocol/server-puppeteer`
- **Purpose**: Advanced browser automation
- **Priority**: MEDIUM
- **Status**: ✅ Installed

---

### External Services

#### 16. **Google Maps** - Location Services
- **Package**: `@modelcontextprotocol/server-google-maps`
- **Env**: `GOOGLE_MAPS_API_KEY`
- **Priority**: LOW
- **Status**: ✅ Installed

#### 17. **Slack** - Team Communication
- **Package**: `@modelcontextprotocol/server-slack`
- **Env**: `SLACK_BOT_TOKEN`, `SLACK_TEAM_ID`
- **Priority**: MEDIUM
- **Status**: ✅ Installed

#### 18. **Discord** - Community Communication
- **Package**: `@modelcontextprotocol/server-discord`
- **Env**: `DISCORD_BOT_TOKEN`
- **Priority**: LOW
- **Status**: ✅ Installed

#### 19. **Sentry** - Error Tracking
- **Package**: `@modelcontextprotocol/server-sentry`
- **Env**: `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`
- **Priority**: MEDIUM
- **Status**: ✅ Installed

---

### Productivity & Documentation

#### 20. **Notion** - Documentation Management
- **Package**: `@modelcontextprotocol/server-notion`
- **Env**: `NOTION_API_KEY`
- **Priority**: MEDIUM
- **Status**: ✅ Installed

#### 21. **Linear** - Project Management
- **Package**: `@modelcontextprotocol/server-linear`
- **Env**: `LINEAR_API_KEY`
- **Priority**: LOW
- **Status**: ✅ Installed

#### 22. **Google Drive** - Cloud Storage
- **Package**: `@modelcontextprotocol/server-google-drive`
- **Env**: `GOOGLE_DRIVE_CREDENTIALS`
- **Priority**: LOW
- **Status**: ✅ Installed

---

### Design & Content

#### 23. **Figma** - Design System Integration
- **Remote**: `https://mcp.figma.com/mcp`
- **Purpose**: Design assets, design-to-code
- **Priority**: MEDIUM
- **Status**: ✅ Installed

#### 24. **EverArt** - AI Image Generation
- **Package**: `@modelcontextprotocol/server-everart`
- **Env**: `EVERART_API_KEY`
- **Priority**: LOW
- **Status**: ✅ Installed

---

### Communication & Outreach

#### 25. **SendEmail** - Email Sending
- **Package**: `@modelcontextprotocol/server-sendemail`
- **Env**: `SENDGRID_API_KEY`
- **Priority**: MEDIUM
- **Status**: ✅ Installed

---

### Cloud & Backend

#### 26. **AWS Knowledge Base** - Retrieval
- **Package**: `@modelcontextprotocol/server-aws-kb-retrieval`
- **Env**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- **Priority**: LOW
- **Status**: ✅ Installed

#### 27. **Supabase** - Backend Services
- **Package**: `@modelcontextprotocol/server-supabase`
- **Env**: `SUPABASE_URL`, `SUPABASE_KEY`
- **Priority**: MEDIUM
- **Status**: ✅ Installed

---

### Documentation & Knowledge

#### 28. **DeepWiki** - Repository Documentation
- **Remote**: `https://mcp.deepwiki.com/mcp`
- **Purpose**: Private repository documentation access
- **Priority**: MEDIUM
- **Status**: ✅ Installed

#### 29. **Time** - Time/Date Operations
- **Command**: `python -m mcp_server_time`
- **Purpose**: Time zone conversions, scheduling
- **Priority**: LOW
- **Status**: ✅ Installed

---

## Environment Variables Required

Create a `.env` file or set system environment variables:

```bash
# Version Control
GITHUB_TOKEN=ghp_your_github_token

# Search & Web
BRAVE_API_KEY=your_brave_api_key

# Databases
DATABASE_URL=postgresql://user:pass@localhost:5432/agentic_workflow
REDIS_URL=redis://localhost:6379
PINECONE_API_KEY=your_pinecone_key
CHROMA_URL=http://localhost:8000

# Communication
SLACK_BOT_TOKEN=EXAMPLE_SLACK_TOKEN_NOT_REAL
SLACK_TEAM_ID=your_team_id
DISCORD_BOT_TOKEN=your_discord_token
SENDGRID_API_KEY=SG.your_sendgrid_key

# Productivity
NOTION_API_KEY=secret_your_notion_key
LINEAR_API_KEY=lin_api_your_key
GOOGLE_DRIVE_CREDENTIALS=your_credentials_json

# Design & Content
FIGMA_TOKEN=your_figma_token
FIGMA_TEAM_ID=your_team_id
EVERART_API_KEY=your_everart_key

# Cloud Services
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key

# Monitoring
SENTRY_AUTH_TOKEN=your_sentry_token
SENTRY_ORG=your_org_name
GOOGLE_MAPS_API_KEY=your_google_maps_key
```

---

## Historical Configuration Sources

### Commit b61340122 (Dec 31, 2025)
- Added 18 MCP servers with priority classification
- Introduced role-based MCP mappings (CODER, RESEARCHER, etc.)
- Created `install_all_mcps.ps1` installation script

### Archive: `mcp_server_config.json`
- Windows-specific configuration with `cmd.exe` wrapper
- Figma Pro integration
- Terminal MCP placeholder

### Archive: `mcp.manifest.json`
- MCP-compliant orchestration manifest
- Redis, ChromaDB, OpenAI tool definitions

---

## Installation Script

Historical PowerShell script available at:
`agentic_core/L0_maintenance/scripts/install_all_mcps.ps1`

To install all servers:
```powershell
cd c:\Git\Agentic-Workflow
.\agentic_core\L0_maintenance\scripts\install_all_mcps.ps1
```

---

## Role-Based MCP Mappings

From `agentic_core/config/mcp_mappings.yaml`:

- **CODER**: GitHub, Git, Telemetry
- **RESEARCHER**: Brave Search, Fetch, Filesystem
- **DATA_ANALYST**: Postgres, SQLite
- **K25_DEEP_RESEARCHER**: Brave Search, Fetch, Filesystem (research cache)
- **OUTREACH**: SendEmail, Slack
- **DOCUMENTATION**: Notion
- **BACKEND**: Supabase

---

## Next Steps

1. **Restart legacy editor** to load all 29 MCP servers
2. **Set Environment Variables** (see above)
3. **Verify Installation**: Check MCP panel in Codex
4. **Test Individual Servers**: Use MCP tools in conversations

---

## Troubleshooting

### GitKraken Not Found
- Install GitLens extension in legacy editor
- Path: `C:\Users\amita\AppData\Roaming\legacy editor\User\globalStorage\eamodio.gitlens\gk.exe`

### Python MCP Servers (Time)
- Requires: `pip install mcp-server-time`
- Ensure Python is in PATH

### Remote MCP Servers (Figma, DeepWiki)
- Requires: `npx mcp-remote`
- OAuth may be required for Figma

---

**Last Updated**: 2026-02-03
**Total Servers**: 29
**Configuration File**: `C:\Users\amita\AppData\Roaming\legacy editor\User\settings.json`
**Historical Commit**: `b61340122` (Dec 31, 2025)
