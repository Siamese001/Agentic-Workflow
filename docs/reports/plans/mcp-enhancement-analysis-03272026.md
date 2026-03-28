# MCP Enhancement Analysis & Recommendations

## Current MCP Inventory Status

### ✅ **Tier 1 (Must-Have) - ALREADY IMPLEMENTED**
| MCP | Status | Evidence |
|-----|--------|----------|
| Memory MCP | ✅ **CUSTOM** | SQLite-backed knowledge graph (2,008 entities, 9,981 observations, 17,509 relations) |
| SQLite MCP | ✅ **CUSTOM** | ADG Redis MCP provides ADG-specific SQLite access (17 specialized tools) |
| Filesystem MCP | ✅ **STANDARD** | Global npm, locked to repo root only |
| Git MCP | ✅ **STANDARD** | GitKraken CLI integration |
| Terminal MCP | ❌ **MISSING** | No terminal/command execution MCP |

### 🔄 **Tier 2 (Major Leverage) - PARTIAL**
| MCP | Status | Recommendation |
|-----|--------|---------------|
| Pytest MCP | 🔄 **PARTIAL** | **YES** - 64 test files in `/tests`, extensive pytest infrastructure |
| Redis MCP | ✅ **CUSTOM** | ADG Redis MCP (17 tools) exceeds standard Redis MCP |
| HTTP MCP | 🔄 **PARTIAL** | **YES** - Fetch MCP present but limited |

### 📊 **Tier 3 (Optimization/Scale) - OPPORTUNITY**
| MCP | Status | Recommendation |
|-----|--------|---------------|
| Vector DB MCP | 🔄 **PARTIAL** | **YES** - ChromaDB + extensive embedding infrastructure |
| Context7 MCP | ❌ **MISSING** | **NO** - Limited external context needs |
| Governance MCP | ✅ **CUSTOM** | ADG Redis MCP provides governance-specific tools |

---

## Detailed Recommendations

### **Tier 1 Additions**

#### 1. **Terminal MCP** - **YES** (Critical Gap)
**Why:** Essential for command execution, evidence generation, and system operations
- **Evidence**: 4732 HTTP/network operations, 1676 SQLite operations need terminal access
- **Use Cases**: Running `python tools/generate_full_adg.py`, test execution, CI operations
- **Recommendation**: Add standard terminal MCP with safety restrictions

### **Tier 2 Additions**

#### 2. **Pytest MCP** - **YES** (High ROI)
**Why:** Massive test infrastructure (64 test files, 199K pytest matches)
- **Evidence**: Extensive test suite in `/tests` with ADG, apps, and integration tests
- **Use Cases**: Test discovery, execution, coverage analysis, CI automation
- **Recommendation**: Standard pytest MCP for test automation

#### 3. **HTTP MCP Enhancement** - **YES** (Upgrade Fetch)
**Why:** Current Fetch MCP is basic, need full HTTP capabilities
- **Evidence**: 4732 HTTP operations across codebase, external API integrations
- **Use Cases**: API testing, external service integration, webhooks
- **Recommendation**: Enhanced HTTP MCP with auth, retries, async support

### **Tier 3 Additions**

#### 4. **Vector DB MCP** - **YES** (Strategic)
**Why:** Extensive embedding/vector infrastructure already exists
- **Evidence**: 61K vector/embedding matches, ChromaDB, embedding factories
- **Use Cases**: Semantic search, RAG, similarity queries, ADG semantic analysis
- **Recommendation**: Vector DB MCP to unify ChromaDB/Pinecone access

#### 5. **Context7 MCP** - **NO** (Limited Value)
**Why:** Repository has strong internal context, limited external context needs
- **Evidence**: Self-contained architecture, ADG provides internal context
- **Use Cases**: External context retrieval (limited applicability)
- **Recommendation**: Skip - existing memory/graph MCP sufficient

### **Custom MCP Assessment**

#### 6. **Governance MCP** - **YES** (Already Implemented)
**Why:** ADG Redis MCP provides governance-specific capabilities
- **Evidence**: 17 specialized tools, violation tracking, layer analysis
- **Status**: ✅ **COMPLETE** - Exceeds standard governance MCP

---

## Implementation Priority

### **Immediate (Critical)**
1. **Terminal MCP** - Fill command execution gap
2. **Pytest MCP** - Leverage massive test infrastructure

### **Short-term (High Value)**
3. **HTTP MCP Enhancement** - Upgrade from basic Fetch
4. **Vector DB MCP** - Unify existing vector infrastructure

### **Not Recommended**
5. **Context7 MCP** - Limited ROI for this repository

---

## Final MCP Configuration Recommendation

```json
{
  "mcpServers": {
    // ✅ EXISTING (Keep)
    "sequential-thinking": {...},
    "filesystem": {...},
    "adg_redis": {...},
    "memory": {...},
    "GitKraken": {...},
    "brave-search": {...},
    "deepwiki": {...},
    "fetch": {...},
    
    // 🆕 ADDITIONS
    "terminal": {
      "command": "node",
      "args": ["@modelcontextprotocol/server-terminal"],
      "disabled": false,
      "env": {
        "SHELL_RESTRICTION": "repo-only",
        "COMMAND_WHITELIST": ["python", "pytest", "git", "ls", "cat"]
      }
    },
    
    "pytest": {
      "command": "node", 
      "args": ["@modelcontextprotocol/server-pytest"],
      "cwd": "C:\\Git\\Agentic-Workflow",
      "disabled": false,
      "env": {
        "PYTEST_CONFIG": "tests/conftest.py",
        "COVERAGE_ENABLED": "true"
      }
    },
    
    "http": {
      "command": "node",
      "args": ["@modelcontextprotocol/server-http"],
      "disabled": false,
      "env": {
        "HTTP_TIMEOUT": "30",
        "MAX_RETRIES": "3",
        "AUTH_SUPPORT": "true"
      }
    },
    
    "vector-db": {
      "command": "python",
      "args": ["tools/mcp/vector_db_server.py"],
      "cwd": "C:\\Git\\Agentic-Workflow",
      "disabled": false,
      "env": {
        "CHROMA_PATH": "artifacts/chroma",
        "VECTOR_DIM": "1536"
      }
    }
  }
}
```

## Summary

**Add: 4 MCPs** (Terminal, Pytest, HTTP Enhanced, Vector DB)
**Skip: 1 MCP** (Context7)
**Keep: 8 MCPs** (All existing, including custom ADG Redis/Memory)

**Total: 12 MCPs** - Comprehensive coverage for this sophisticated agentic workflow repository.
