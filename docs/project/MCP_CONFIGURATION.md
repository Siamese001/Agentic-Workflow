# MCP Server Configuration for Windsurf

## Overview
This document describes the Model Context Protocol (MCP) servers configured in Windsurf for the Agentic-Workflow project.

## Installation Location
**File**: `C:\Users\amita\AppData\Roaming\Windsurf\User\settings.json`

## Configured MCP Servers

### 1. **Playwright** - Browser Automation
- **Package**: `@executeautomation/playwright-mcp-server`
- **Purpose**: Web automation, testing, scraping
- **Tools**: Navigate, click, type, screenshot, evaluate JavaScript
- **Status**: ✅ Installed

### 2. **Sequential Thinking** - Advanced Reasoning
- **Package**: `@modelcontextprotocol/server-sequential-thinking`
- **Purpose**: Multi-step reasoning, chain-of-thought processing
- **Tools**: Complex problem decomposition, hypothesis verification
- **Status**: ✅ Installed

### 3. **Filesystem** - File Operations
- **Package**: `@modelcontextprotocol/server-filesystem`
- **Purpose**: Read/write files, directory operations
- **Root Path**: `c:\Git\Agentic-Workflow`
- **Status**: ✅ Installed

### 4. **Memory** - Persistent Context
- **Package**: `@modelcontextprotocol/server-memory`
- **Purpose**: Store and retrieve conversation context
- **Tools**: Create, read, update, delete memories
- **Status**: ✅ Installed

### 5. **GitHub** - Repository Operations
- **Package**: `@modelcontextprotocol/server-github`
- **Purpose**: GitHub API integration
- **Env**: `GITHUB_PERSONAL_ACCESS_TOKEN`
- **Status**: ✅ Installed (requires token)

### 6. **Git** - Version Control
- **Package**: `@modelcontextprotocol/server-git`
- **Purpose**: Git operations (commit, push, pull, branch)
- **Repository**: `c:\Git\Agentic-Workflow`
- **Status**: ✅ Installed

### 7. **Brave Search** - Web Search
- **Package**: `@modelcontextprotocol/server-brave-search`
- **Purpose**: Web search capabilities
- **Env**: `BRAVE_API_KEY`
- **Status**: ✅ Installed (requires API key)

### 8. **Fetch** - HTTP Requests
- **Package**: `@modelcontextprotocol/server-fetch`
- **Purpose**: Make HTTP requests to external APIs
- **Status**: ✅ Installed

### 9. **PostgreSQL** - Database Operations
- **Package**: `@modelcontextprotocol/server-postgres`
- **Purpose**: PostgreSQL database queries
- **Connection**: `postgresql://localhost/agentic_workflow`
- **Status**: ✅ Installed (requires DB setup)

### 10. **SQLite** - Local Database
- **Package**: `@modelcontextprotocol/server-sqlite`
- **Purpose**: SQLite database operations
- **DB Path**: `c:\Git\Agentic-Workflow\data\agentic.db`
- **Status**: ✅ Installed

### 11. **Puppeteer** - Headless Browser
- **Package**: `@modelcontextprotocol/server-puppeteer`
- **Purpose**: Advanced browser automation
- **Status**: ✅ Installed

### 12. **Google Maps** - Location Services
- **Package**: `@modelcontextprotocol/server-google-maps`
- **Purpose**: Geocoding, directions, places
- **Env**: `GOOGLE_MAPS_API_KEY`
- **Status**: ✅ Installed (requires API key)

### 13. **Slack** - Team Communication
- **Package**: `@modelcontextprotocol/server-slack`
- **Purpose**: Send messages, read channels
- **Env**: `SLACK_BOT_TOKEN`, `SLACK_TEAM_ID`
- **Status**: ✅ Installed (requires tokens)

### 14. **Sentry** - Error Tracking
- **Package**: `@modelcontextprotocol/server-sentry`
- **Purpose**: Monitor errors and performance
- **Env**: `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`
- **Status**: ✅ Installed (requires config)

### 15. **AWS Knowledge Base** - Retrieval
- **Package**: `@modelcontextprotocol/server-aws-kb-retrieval`
- **Purpose**: Query AWS Knowledge Base
- **Env**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- **Status**: ✅ Installed (requires AWS config)

### 16. **EverArt** - AI Image Generation
- **Package**: `@modelcontextprotocol/server-everart`
- **Purpose**: Generate AI images
- **Env**: `EVERART_API_KEY`
- **Status**: ✅ Installed (requires API key)

---

## Additional MCP Servers to Consider

### 17. **Redis** - In-Memory Data Store

- **Package**: `@modelcontextprotocol/server-redis`
- **Purpose**: Cache, session storage, pub/sub
- **Env**: `REDIS_URL`
- **Status**: ✅ Installed (requires Redis server)

### 18. **Pinecone** - Vector Database
- **Package**: `@pinecone-database/mcp-server-pinecone`
- **Purpose**: Vector search, embeddings storage
- **Env**: `PINECONE_API_KEY`, `PINECONE_ENVIRONMENT`
- **Status**: ✅ Installed (requires Pinecone account)

### GitKraken (Not Available as MCP)
**Note**: GitKraken does not have an official MCP server. Use the `git` MCP server instead for version control operations.

---

## Environment Variables Required

Create a `.env` file or set system environment variables:

```bash
# GitHub
GITHUB_TOKEN=your_github_token

# Brave Search
BRAVE_API_KEY=your_brave_api_key

# Google Maps
GOOGLE_MAPS_API_KEY=your_google_maps_key

# Slack
SLACK_BOT_TOKEN=EXAMPLE_SLACK_TOKEN_NOT_REAL
SLACK_TEAM_ID=your_team_id

# Sentry
SENTRY_AUTH_TOKEN=your_sentry_token
SENTRY_ORG=your_org_name

# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# EverArt
EVERART_API_KEY=your_everart_key

# Redis (if added)
REDIS_URL=redis://localhost:6379

# Pinecone (if added)
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment
```

---

## Usage in Windsurf

After configuration, restart Windsurf to load the MCP servers. You can then:

1. **Check MCP Status**: Look for MCP indicators in the Cursor Agent panel
2. **Use MCP Tools**: Tools will be available automatically in conversations
3. **Debug**: Check Windsurf logs if servers fail to start

---

## Troubleshooting

### Server Won't Start
- Ensure Node.js and npm are installed
- Check that npx is in your PATH
- Verify environment variables are set

### Permission Errors
- Run Windsurf as administrator (Windows)
- Check file/directory permissions

### API Key Issues
- Verify API keys are valid
- Check environment variable syntax: `${VAR_NAME}`

---

## References

- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
- [Windsurf MCP Guide](https://docs.codeium.com/windsurf/mcp)

---

**Last Updated**: 2026-02-03
**Configuration File**: `C:\Users\amita\AppData\Roaming\Windsurf\User\settings.json`
