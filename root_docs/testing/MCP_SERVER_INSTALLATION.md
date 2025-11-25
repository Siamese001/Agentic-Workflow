# MCP SERVER INSTALLATION GUIDE
## Agentic-Workflow-10_10 Architecture

This document provides complete installation and validation instructions for all MCP servers required by the Agentic-Workflow-10_10 system.

---

## RECOMMENDED MCP SERVERS

Based on the SDK vs MCP analysis, the following MCP servers should be installed:

### 1. **Filesystem MCP Server** (REQUIRED)
- **Purpose**: Agent-visible file operations for L2 execution layer
- **Use Cases**: Prompt CMS, journal persistence, golden datasets
- **Installation**:
  ```bash
  npm install -g @modelcontextprotocol/server-filesystem
  ```
- **Configuration**: Add to MCP settings
  ```json
  {
    "mcpServers": {
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/directory"]
      }
    }
  }
  ```

### 2. **SQLite MCP Server** (RECOMMENDED)
- **Purpose**: Agent-queryable metadata store for temporal graphs
- **Use Cases**: L4 state layer metadata queries
- **Installation**:
  ```bash
  npm install -g @modelcontextprotocol/server-sqlite
  ```
- **Configuration**:
  ```json
  {
    "mcpServers": {
      "sqlite": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sqlite", "--db-path", "/path/to/database.db"]
      }
    }
  }
  ```

### 3. **Brave Search MCP Server** (OPTIONAL)
- **Purpose**: Agent-initiated web search for external knowledge retrieval
- **Use Cases**: L2 optional web search tool
- **Installation**:
  ```bash
  npm install -g @modelcontextprotocol/server-brave-search
  ```
- **Configuration** (requires BRAVE_API_KEY):
  ```json
  {
    "mcpServers": {
      "brave-search": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "env": {
          "BRAVE_API_KEY": "your-api-key-here"
        }
      }
    }
  }
  ```

### 4. **GitHub MCP Server** (OPTIONAL)
- **Purpose**: Agent-visible repository operations for prompt CMS
- **Use Cases**: Version control for prompt changelog
- **Installation**:
  ```bash
  npm install -g @modelcontextprotocol/server-github
  ```
- **Configuration** (requires GITHUB_TOKEN):
  ```json
  {
    "mcpServers": {
      "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {
          "GITHUB_TOKEN": "your-github-token-here"
        }
      }
    }
  }
  ```

### 5. **Pinecone MCP Server** (OPTIONAL - HYBRID MODE)
- **Purpose**: Agent-initiated semantic search (alternative to SDK)
- **Use Cases**: L2 vector search executor for agent-visible operations
- **Note**: Already available via pinecone-mcp-server MCP server in your environment
- **Configuration**:
  ```json
  {
    "mcpServers": {
      "pinecone": {
        "command": "mcp",
        "args": ["run", "pinecone-mcp-server"],
        "env": {
          "PINECONE_API_KEY": "your-pinecone-api-key-here"
        }
      }
    }
  }
  ```

---

## MCP SERVERS NOT RECOMMENDED

The following services should remain SDK-only:

- **Redis**: L4 state layer requires direct SDK control for deterministic caching
- **ChromaDB**: Meta layer vector operations need SDK-level performance control
- **OpenAI/Anthropic/Gemini**: L2 execution layer must own LLM provider calls
- **OpenTelemetry**: System-level observability, not agent-visible
- **Pydantic/NumPy/Pandas**: Core libraries, not external services

---

## INSTALLATION COMMANDS

### Quick Install (All Recommended Servers)
```bash
# Install Node.js MCP servers
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-sqlite

# Optional servers
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-github
```

### Verify Installation
```bash
# Check installed MCP servers
npm list -g --depth=0 | grep @modelcontextprotocol

# Test filesystem server
npx -y @modelcontextprotocol/server-filesystem --help

# Test SQLite server
npx -y @modelcontextprotocol/server-sqlite --help
```

---

## MCP SERVER VALIDATION

After installation, validate each server:

### 1. Filesystem Server Test
```bash
# Start server with test directory
npx -y @modelcontextprotocol/server-filesystem /tmp/test

# Expected: Server starts without errors
```

### 2. SQLite Server Test
```bash
# Create test database
sqlite3 test.db "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);"

# Start server
npx -y @modelcontextprotocol/server-sqlite --db-path test.db

# Expected: Server starts and connects to database
```

### 3. Brave Search Test (requires API key)
```bash
export BRAVE_API_KEY="your-key"
npx -y @modelcontextprotocol/server-brave-search

# Expected: Server starts without authentication errors
```

### 4. GitHub Test (requires token)
```bash
export GITHUB_TOKEN="your-token"
npx -y @modelcontextprotocol/server-github

# Expected: Server starts and authenticates
```

---

## INTEGRATION WITH AGENTIC-WORKFLOW-10_10

### L2 Execution Layer Integration
MCP servers should be integrated into L2 execution layer for agent-visible operations:

1. **File Operations**: Use filesystem MCP for prompt CMS and journal operations
2. **Metadata Queries**: Use SQLite MCP for temporal graph queries
3. **Web Search**: Use Brave MCP for external knowledge retrieval
4. **Version Control**: Use GitHub MCP for prompt changelog

### Safety Layer (L5) Integration
All MCP tool invocations must pass through L5 safety layer:
- Input validation
- Output sanitization
- Rate limiting
- Audit logging

### Orchestration Layer (L3) Integration
MCP tools should be registered in L3 DAG as typed nodes:
- Input schema validation
- Output schema validation
- Error handling
- Timeout management

---

## TROUBLESHOOTING

### Issue: MCP server not found
**Solution**: Ensure Node.js and npm are installed and on PATH
```bash
node --version
npm --version
```

### Issue: Permission denied
**Solution**: Run with appropriate permissions or use `--prefix` for local install
```bash
npm install --prefix ~/.local @modelcontextprotocol/server-filesystem
```

### Issue: Server fails to start
**Solution**: Check logs and ensure all environment variables are set
```bash
# Enable debug logging
export DEBUG=mcp:*
npx -y @modelcontextprotocol/server-filesystem /path/to/dir
```

---

## SECURITY CONSIDERATIONS

1. **Filesystem Access**: Restrict MCP filesystem server to specific directories
2. **API Keys**: Store in environment variables, never hardcode
3. **Rate Limiting**: Implement rate limits for external API calls (Brave, GitHub)
4. **Audit Logging**: Log all MCP tool invocations for security audit
5. **Input Validation**: Validate all inputs before passing to MCP servers

---

## PERFORMANCE CONSIDERATIONS

1. **Connection Pooling**: Reuse MCP server connections where possible
2. **Timeout Management**: Set appropriate timeouts for all MCP calls
3. **Error Handling**: Implement circuit breakers for failing MCP servers
4. **Caching**: Cache MCP responses where appropriate (e.g., file reads)
5. **Async Operations**: Use async MCP calls to avoid blocking L2 execution

---

## NEXT STEPS

1. Install required MCP servers (filesystem, SQLite)
2. Configure MCP settings in your IDE or runtime environment
3. Integrate MCP tools into L2 execution layer
4. Add L5 safety checks for all MCP operations
5. Test end-to-end workflow with MCP tools enabled
6. Monitor performance and adjust timeouts/rate limits as needed

---

## REFERENCES

- MCP Specification: https://modelcontextprotocol.io/
- MCP Server Registry: https://github.com/modelcontextprotocol/servers
- Pinecone MCP Server: Already available in your environment
- Brave Search MCP: https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search
- GitHub MCP: https://github.com/modelcontextprotocol/servers/tree/main/src/github
