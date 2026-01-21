# Model Context Protocol (MCP) Integration

## Overview

The Model Context Protocol (MCP) transforms agents from using hardcoded tool integrations to dynamically discovering capabilities at runtime. Instead of writing `read_pdf()` functions, agents connect to MCP servers and "discover" the ability to read files, query databases, search the web, and more.

## Architecture

```
Agent Role → MCP Manager → MCP Servers → Dynamic Tools
    ↓              ↓            ↓           ↓
 RESEARCHER → Connection → Brave Search → search_brave()
 CODER      → Manager   → GitHub      → git_commit()
```

## Key Benefits

1. **Dynamic Skill Acquisition**: Add new capabilities by updating YAML config, not code

2. **Separation of Concerns**: Agent handles cognition, MCP handles I/O

3. **Zero-Code Integration**: Connect to any service with an MCP server

4. **Runtime Discovery**: Agents learn what tools are available at startup

## Configuration

### MCP Mappings (`config/mcp_mappings.yaml`)

```yaml
# Global servers (available to all agents)
defaults:
  - server: "filesystem"
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "./"]
    description: "Local filesystem access"

  - server: "memory"
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-memory"]
    description: "Persistent memory storage"

# Role-specific servers
roles:
  RESEARCHER:
    - server: "brave-search"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-brave-search"]
      env:
        BRAVE_API_KEY: "${BRAVE_API_KEY}"
      description: "Web search via Brave Search API"

    - server: "fetch"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-fetch"]
      description: "HTTP fetch for web content"

  CODER:
    - server: "github"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-github"]
      env:
        GITHUB_TOKEN: "${GITHUB_TOKEN}"
      description: "GitHub repository operations"
```

## Implementation

### 1. MCP Connection Manager

The `MCPConnectionManager` handles:
- Loading server configurations
- Establishing stdio connections
- Tool discovery and aggregation
- Routing tool calls to appropriate servers

```python
from agentic_core.L2_execution.mcp_manager import MCPConnectionManager

# Load configuration
config = load_mcp_config("config/mcp_mappings.yaml")

# Create manager
manager = MCPConnectionManager(config)

# Connect servers for a role
await manager.connect_servers("RESEARCHER")

# Execute discovered tools
result = await manager.execute_tool("search_brave", {"query": "AI research"})
```

### 2. Integration with HardenedAutonomousHop

MCP is integrated as an optional hardening layer:

```python
from runtime.core.hardened_autonomous_hop import (
    HardenedAutonomousHop,
    HardeningConfig
)

# Enable MCP in configuration
hardening = HardeningConfig(
    enable_mcp=True,
    mcp_role="RESEARCHER",
    mcp_config_path="config/mcp_mappings.yaml"
)

# Create hardened agent with MCP
agent = HardenedAutonomousHop(
    hop_function=my_function,
    config=HardenedAutonomousHopConfig(hardening=hardening)
)

# Run - automatically connects to MCP servers
result = await agent.run("Research latest AI developments")
```

## Available MCP Servers

### Official Servers

1. **Filesystem** (`@modelcontextprotocol/server-filesystem`)
   - Read/write files
   - List directories
   - File operations

2. **Memory** (`@modelcontextprotocol/server-memory`)
   - Persistent key-value storage
   - Context retention

3. **Brave Search** (`@modelcontextprotocol/server-brave-search`)
   - Web search capabilities
   - Requires `BRAVE_API_KEY`

4. **GitHub** (`@modelcontextprotocol/server-github`)
   - Repository operations
   - Issues, PRs, commits
   - Requires `GITHUB_TOKEN`

5. **PostgreSQL** (`@modelcontextprotocol/server-postgres`)
   - Database queries
   - Schema inspection
   - Requires connection string

6. **Git** (`@modelcontextprotocol/server-git`)
   - Local git operations
   - Commit, push, pull

### Community Servers

- **Slack**: Team communication
- **Jira**: Issue tracking
- **Salesforce**: CRM operations
- **Google Drive**: Document management

## Usage Examples

### Research Agent with MCP

```python
# Configuration enables filesystem and search
agent = HardenedAutonomousHop(
    hop_function=research_function,
    config=HardenedAutonomousHopConfig(
        hardening=HardeningConfig(
            enable_mcp=True,
            mcp_role="RESEARCHER"
        )
    )
)

# Agent discovers and uses MCP tools
result = await agent.run("""
Research quantum computing papers and save findings
to research/quantum_computing.md
""")

# Behind the scenes:
# 1. Connects to filesystem and brave-search MCP servers
# 2. Discovers tools: read_file, write_file, search_brave
# 3. Uses tools to research and save results
```

### Coder Agent with MCP

```python
# Configuration enables GitHub and git
agent = HardenedAutonomousHop(
    hop_function=coding_function,
    config=HardenedAutonomousHopConfig(
        hardening=HardeningConfig(
            enable_mcp=True,
            mcp_role="CODER"
        )
    )
)

# Agent uses GitHub MCP tools
result = await agent.run("""
Create a new feature branch and submit a PR
for the authentication enhancement
""")

# Uses discovered tools:
# - git_create_branch
# - git_commit
# - github_create_pull_request
```

## Best Practices

### 1. Environment Variables

Store sensitive credentials in environment variables:

```bash
export BRAVE_API_KEY="your-brave-api-key"
export GITHUB_TOKEN="your-github-token"
export DATABASE_URL="postgresql://user:pass@localhost/db"
```

### 2. Server Selection

Choose servers based on agent role:

- **RESEARCHER**: filesystem, brave-search, fetch
- **CODER**: filesystem, git, github
- **DATA_ANALYST**: postgres, sqlite, filesystem
- **CONTEXT_GATHERER**: github, fetch, filesystem

### 3. Error Handling

MCP connections are fault-tolerant:

```python
try:
    await manager.connect_servers("RESEARCHER")
    tools = manager.get_tools_schema()
except Exception as e:
    logger.warning(f"MCP connection failed: {e}")
    # Fallback to built-in tools
```

### 4. Performance

- MCP servers use stdio for low-latency communication
- Connections are established once per session
- Tools are cached after discovery

## Migration from Tool Registry

### Before (Tool Registry)

```python
# Hardcoded tool function
def search_web(query: str) -> str:
    # Implementation here
    pass

# Register tool
registry.register_tool("search_web", search_web)
```

### After (MCP)

```yaml
# Just add to config
roles:
  RESEARCHER:
    - server: "brave-search"
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-brave-search"]
      env:
        BRAVE_API_KEY: "${BRAVE_API_KEY}"
```

No code changes needed - agent discovers the tool automatically!

## Security Considerations

1. **Sandboxing**: MCP servers run in separate processes

2. **Permissions**: Each server gets only required environment variables

3. **Network Control**: Disable network for sensitive operations

4. **Resource Limits**: Configure timeouts and memory limits

## Troubleshooting

### Common Issues

1. **Server Not Found**
   ```
   Error: Tool 'search_brave' not found
   ```
   - Check MCP server is running
   - Verify role configuration in YAML
   - Check environment variables

2. **Connection Failed**
   ```
   Error: Failed to connect to MCP server
   ```
   - Install Node.js (required for npx)
   - Check server command and arguments
   - Verify network access

3. **Permission Denied**
   ```
   Error: BRAVE_API_KEY not found
   ```
   - Set environment variables
   - Check .env file
   - Verify API key validity

### Debug Mode

Enable debug logging:

```python
import logging
logging.getLogger("agentic_core.L2_execution.mcp_manager").setLevel(logging.DEBUG)
```

## Future Enhancements

1. **Custom MCP Servers**: Build domain-specific servers
2. **Resource Subscriptions**: Real-time data updates
3. **Server Chaining**: Compose multiple servers
4. **Dynamic Loading**: Add/remove servers at runtime

## Conclusion

MCP transforms agents from static tool users to dynamic capability discoverers. This enables:
- Faster integration with new services
- Cleaner agent code (no hardcoded integrations)
- Better separation of concerns
- Easier testing and maintenance

The integration maintains all hardening features while adding dynamic tool discovery, creating truly autonomous and adaptable agents.
