# SDK & MCP Implementation Plan

**Objective**: Implement the documented SDKs_MCPS migration that exists only in documentation, ensuring all agentic_core and apps_* modules actually use data/sdks_mcps client wrappers instead of direct SDK imports.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Critical Discovery: Documentation vs Reality Gap

**What SDKs_MCPS_Migration_Guide.md claims:**
- ✅ SovereignLLMGateway migrated to use client wrappers
- ✅ EmbeddingSovereignAgent migrated to use client wrappers
- ✅ Apps RG and Shared clients migrated
- ✅ Status: "Migration Complete"

**What verification actually shows:**
- ❌ SovereignLLMGateway: Still uses `import openai`, `import anthropic`, `import google.generativeai`
- ❌ EmbeddingSovereignAgent: Still uses `import google.generativeai`, `import openai`
- ❌ Apps modules: No imports of data.sdks_mcps.client_wrappers found
- ❌ Reality: Migration exists only in documentation, not in code

## Current State Analysis

### Infrastructure Status ✅
- `data/sdks_mcps/client_wrappers/` exists with production-ready clients
- Builder functions available: `create_openai_client`, `create_anthropic_client`, `create_vertex_client`
- MCP catalog and validation infrastructure in place
- Client wrappers have advanced features (caching, retry logic, observability)

### Implementation Status ❌
- **Zero usage** of client wrappers in target files
- **Direct SDK imports** still present everywhere
- **No actual migration** performed despite documentation claiming completion

## Implementation Plan

### Phase 1: Core Gateway Migration (Priority 1)

**1.1 SovereignLLMGateway Migration**
```python
# Current (lines 110, 125, 140):
import openai
import anthropic
import google.generativeai as genai

# Target:
from data.sdks_mcps.client_wrappers import create_openai_client, create_anthropic_client, create_vertex_client
```

**1.2 EmbeddingSovereignAgent Migration**
```python
# Current (lines 221, 238):
import google.generativeai as genai
import openai

# Target:
from data.sdks_mcps.client_wrappers import create_vertex_client, create_openai_client
```

**1.3 Implementation Strategy**
- Replace direct SDK imports with client wrapper imports
- Update client initialization to use builder functions
- Maintain existing interface contracts to avoid breaking changes
- Add comprehensive tests to verify functionality

### Phase 2: Apps Layer Migration (Priority 2)

**2.1 Apps RG Anthropic Client**
- File: `apps_rg/utils/providers_anthropic_client.py`
- Replace direct Anthropic SDK with `create_anthropic_client`
- Simplify API key handling (managed by wrapper)

**2.2 Apps Shared Google Client**
- File: `apps_shared/utils/providers_google_genai_client.py`
- Replace Google GenAI SDK with `create_vertex_client`
- Remove legacy fallback logic

### Phase 3: Extended MCP Integration (Priority 3)

**3.1 Pinecone MCP Client**
- Create `data/sdks_mcps/client_wrappers/pinecone_client.py`
- Implement via mcp9_ tools with sovereign architecture
- Add Redis caching layer

**3.2 Redis MCP Client**
- Create `data/sdks_mcps/client_wrappers/redis_client.py`
- Implement caching operations via mcp9_ tools
- Add connection pooling and batch operations

**3.3 Additional MCP Clients**
- Filesystem MCP client (mcp5_)
- Brave Search client (mcp0_)
- Playwright client (mcp10_)
- Memory Graph client (mcp8_)

## File-by-File Implementation Details

### SovereignLLMGateway.py Changes

**Import Section:**
```diff
- import openai
- import anthropic
- import google.generativeai as genai
+ from data.sdks_mcps.client_wrappers import (
+     create_openai_client,
+     create_anthropic_client,
+     create_vertex_client
+ )
```

**Client Initialization:**
```diff
- self.openai_client = openai.Client(api_key=config.OPENAI_API_KEY)
- self.anthropic_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
- genai.configure(api_key=config.GOOGLE_API_KEY)
+ self.openai_client = create_openai_client()
+ self.anthropic_client = create_anthropic_client()
+ self.vertex_client = create_vertex_client()
```

### EmbeddingSovereignAgent.py Changes

**Import Section:**
```diff
- import google.generativeai as genai
- import openai
+ from data.sdks_mcps.client_wrappers import create_vertex_client, create_openai_client
```

**Method Updates:**
```diff
- genai.configure(api_key=config.GOOGLE_API_KEY)
- self.vertex_client = genai.GenerativeModel(config.GEMINI_MODEL)
+ self.vertex_client = create_vertex_client()
- self.openai_client = openai.Client(api_key=config.OPENAI_API_KEY)
+ self.openai_client = create_openai_client()
```

## Testing Strategy

### Phase 1 Tests
```python
# tests/unit/sdks_mcps/test_gateway_migration.py
class TestGatewayMigration:
    def test_sovereign_llm_gateway_uses_wrappers(self):
        """Verify SovereignLLMGateway uses client wrappers."""
        from agentic_core.L2_execution.enforcement.SovereignLLMGateway import SovereignLLMGateway
        gateway = SovereignLLMGateway()

        # Verify client types
        from data.sdks_mcps.client_wrappers import OpenAIClient, AnthropicClient, VertexClient
        assert isinstance(gateway.openai_client, OpenAIClient)
        assert isinstance(gateway.anthropic_client, AnthropicClient)
        assert isinstance(gateway.vertex_client, VertexClient)

    def test_embedding_agent_uses_wrappers(self):
        """Verify EmbeddingSovereignAgent uses client wrappers."""
        # Similar verification for embedding agent
```

### Integration Tests
```python
# tests/integration/sdks_mcps/test_end_to_end_functionality.py
class TestEndToEndFunctionality:
    async def test_chat_completion_through_wrapper(self):
        """Test chat completion works through client wrapper."""
        # Verify actual LLM calls work through new wrapper architecture

    async def test_embedding_through_wrapper(self):
        """Test embeddings work through client wrapper."""
        # Verify embedding generation works through new architecture
```

## Validation Approach

### Pre-Implementation Validation
1. **Baseline Tests**: Run existing tests to establish current functionality
2. **Import Analysis**: Document all direct SDK imports across codebase
3. **Dependency Mapping**: Map all SDK usage patterns

### Post-Implementation Validation
1. **Functional Tests**: Ensure all LLM operations work correctly
2. **Performance Tests**: Verify no significant performance degradation
3. **Integration Tests**: Test end-to-end workflows
4. **Regression Tests**: Ensure no breaking changes

## Risk Mitigation

### Technical Risks
- **Breaking Changes**: Maintain exact interface contracts during migration
- **Performance Impact**: Client wrappers include optimizations, should improve performance
- **Configuration Issues**: Client wrappers handle configuration automatically

### Rollback Strategy
- **Branch Protection**: Implement in feature branch with easy rollback
- **Gradual Migration**: Migrate one component at a time
- **Feature Flags**: Add flags to switch between old/new implementations

## Success Metrics

### Quantitative
- **Migration Coverage**: 100% of documented files migrated
- **Test Pass Rate**: 100% of existing tests continue to pass
- **Performance**: <5% impact on response times
- **Error Rate**: No increase in error rates

### Qualitative
- **Centralized Management**: All LLM interactions through data/sdks_mcps
- **Enhanced Observability**: Unified logging and metrics
- **Improved Security**: Centralized API key management
- **Developer Experience**: Simplified client creation and usage

## Timeline

**Week 1: Phase 1 - Core Gateway Migration**
- Day 1-2: SovereignLLMGateway migration
- Day 3-4: EmbeddingSovereignAgent migration
- Day 5: Testing and validation

**Week 2: Phase 2 - Apps Layer Migration**
- Day 1-2: Apps RG and Shared client migration
- Day 3-4: Integration testing
- Day 5: Documentation updates

**Week 3-4: Phase 3 - Extended MCP Integration**
- Pinecone, Redis, and additional MCP clients
- Comprehensive testing and validation

## Next Steps

1. **Immediate**: Create feature branch for migration
2. **Priority 1**: Implement SovereignLLMGateway migration
3. **Priority 2**: Implement EmbeddingSovereignAgent migration
4. **Validation**: Run comprehensive test suite
5. **Documentation**: Update migration guide to reflect actual implementation

This plan bridges the critical gap between documented migration claims and actual implementation, ensuring the data/sdks_mcps infrastructure is actually used as intended.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

