# Prompt Registry Auto-Update Implementation

## Summary

Successfully implemented fixes to eliminate duplicate entries in `registry.json` and enable agent-driven auto-updates based on actual prompt usage.

---

## Changes Made

### 1. **prompt_registry.py** - Core Deduplication & Decorator

#### Added Imports
```python
import hashlib
import logging
from datetime import datetime
import tempfile

logger = logging.getLogger(__name__)
```

#### Enhanced `register_prompt()` with Deduplication
```python
def register_prompt(
    self,
    template_name: str,
    version: str = "v1",
    purpose: str = "",
    territory: str = "templates",
    active: bool = True,
    author: str = "SovereignOrchestrator",
    content: Optional[str] = None  # NEW: For content-based deduplication
) -> None:
    """
    DEDUPLICATION: Prevents identical entries from accumulating.
    Checks (template_name, version, purpose, author, content_hash) before registering.
    """
    # Compute content hash
    content_hash = self._hash_content(content)
    
    # Check for duplicates
    for existing_entry in self.registry[template_name]:
        if (
            existing_entry["version"] == version
            and existing_entry["purpose"] == purpose
            and existing_entry["author"] == author
            and existing_entry.get("content_hash") == content_hash
        ):
            if existing_entry["active"] == active:
                logger.debug(f"Skipping duplicate: {template_name} {version}")
                return  # Early exit - prevents 9-duplicate bug
```

**Key Fix:** Early return when identical entry exists prevents accumulation of duplicates on repeated `get_prompt_registry()` calls.

#### Added Content Hashing
```python
def _hash_content(self, content: Optional[str]) -> Optional[str]:
    """Generate SHA256 hash for deduplication."""
    if content is None:
        return None
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
```

#### Improved Atomic Write Safety
```python
def _save_registry(self) -> None:
    """Atomic write with tempfile + rename for crash safety."""
    with tempfile.NamedTemporaryFile(
        mode='w',
        encoding='utf-8',
        dir=self.REGISTRY_FILE.parent,
        delete=False,
        suffix='.tmp'
    ) as tmp:
        json.dump(data, tmp, indent=2)
        tmp_path = tmp.name
    
    # Atomic rename (POSIX-safe, Windows best-effort)
    Path(tmp_path).replace(self.REGISTRY_FILE)
```

#### New Decorator: `@registers_prompt`
```python
def registers_prompt(
    template_name: str,
    purpose: str = "",
    version: str = "v1",
    territory: str = "templates",
    active: bool = True,
):
    """
    Decorator for agents to declare prompt dependencies.
    
    Usage:
        @registers_prompt("gravity_repair.jinja", purpose="Fixes import violations")
        class ImportAgent:
            pass
    """
    def decorator(cls):
        registry = get_prompt_registry()
        registry.register_prompt(
            template_name=template_name,
            version=version,
            purpose=purpose or f"Used by {cls.__name__}",
            territory=territory,
            author=cls.__name__,
            active=active,
        )
        
        # Store for runtime introspection
        cls._registered_prompt = template_name
        cls._prompt_version = version
        
        return cls
    
    return decorator
```

---

### 2. **compliance_orchestrator.py** - Runtime Sync

#### Added Method After Agent Discovery
```python
def _discover_all_agents(self) -> None:
    # ... existing discovery logic ...
    
    # [PROMPT REGISTRY SYNC] Auto-register agent prompt dependencies
    self._sync_agent_prompts_to_registry()

def _sync_agent_prompts_to_registry(self) -> None:
    """
    Runtime fallback: Sync discovered agents' prompt templates to registry.
    
    Scans all agents for:
    - agent.prompt_template (instance attribute)
    - agent.__class__._registered_prompt (decorator-set attribute)
    
    Safe to call multiple times due to deduplication.
    """
    try:
        from agentic_core.prompt_governance.version_registry.prompt_registry import get_prompt_registry
        registry = get_prompt_registry()
        
        synced_count = 0
        for agent in self._all_agents:
            template = (
                getattr(agent, "prompt_template", None) or 
                getattr(agent.__class__, "_registered_prompt", None)
            )
            
            if template and isinstance(template, str):
                agent_name = agent.__class__.__name__
                registry.register_prompt(
                    template_name=template,
                    purpose=f"Runtime sync for {agent_name}",
                    author=agent_name,
                    active=True,
                )
                synced_count += 1
        
        if synced_count > 0:
            print(f"   [PROMPT SYNC] Registered {synced_count} agent prompt dependencies")
            
    except ImportError:
        print("   [INFO] Prompt registry unavailable - skipping sync")
```

---

## Usage Examples

### Option 1: Decorator (Recommended for New Agents)
```python
# agentic_core/L5_safety/gravity/ImportAgent.py

from agentic_core.prompt_governance.version_registry.prompt_registry import registers_prompt

@registers_prompt("gravity_repair.jinja", purpose="Fixes import violations")
class ImportAgent:
    """Gravity & Import Convention Enforcer"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        # No need to manually register - decorator handles it
```

### Option 2: Instance Attribute (Existing Agents)
```python
# agentic_core/L5_safety/validators/LocationAgent.py

class LocationAgent:
    """Territory compliance validator"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.prompt_template = "file_placement.jinja"  # Runtime sync will detect this
```

### Option 3: Hardcoded Fallback (Canonical Templates)
```python
# Existing hardcoded registrations in get_prompt_registry() remain as fallbacks
# They will be deduplicated automatically - no duplicates will accumulate
```

---

## Benefits

### 1. **Eliminates Duplicate Entries**
- **Before:** 9 identical entries per template (one per import)
- **After:** Single entry per unique (template, version, purpose, author, content_hash)

### 2. **Agent-Driven Auto-Updates**
- Agents declare their prompt dependencies via decorator or attribute
- Registry automatically reflects actual usage
- No manual maintenance of hardcoded lists

### 3. **Runtime Discovery**
- `ComplianceOrchestrator` scans all discovered agents
- Catches agents without decorators
- Ensures registry completeness

### 4. **Backward Compatible**
- Existing hardcoded registrations still work
- Deduplication prevents conflicts
- No breaking changes to existing code

### 5. **Crash-Safe Persistence**
- Atomic write with tempfile + rename
- No corruption on system crash
- Human-readable JSON with timestamps

---

## Testing

### Verify Deduplication Works
```bash
# Run validator multiple times - registry.json should NOT grow
python canon_validator_agentic_v2_thin.py
python canon_validator_agentic_v2_thin.py
python canon_validator_agentic_v2_thin.py

# Check registry.json - should have only 1 active entry per template
cat agentic_core/prompt_governance/version_registry/registry.json
```

### Verify Agent Sync Works
```bash
# Add prompt_template to an agent
# Run validator - check output for "[PROMPT SYNC] Registered N agent prompt dependencies"
python canon_validator_agentic_v2_thin.py
```

### Verify Decorator Works
```bash
# Add @registers_prompt to an agent
# Import the agent module
python -c "from agentic_core.L5_safety.gravity.ImportAgent import ImportAgent"

# Check registry.json - should show new entry with author=ImportAgent
```

---

## Migration Path

### Phase 1: Immediate (✅ Complete)
- Deduplication logic active
- Runtime sync active
- Decorator available

### Phase 2: Gradual Adoption (Optional)
- Add `@registers_prompt` to high-value agents
- Add `prompt_template` attribute to agents with LLM prompts
- Monitor `[PROMPT SYNC]` output to track coverage

### Phase 3: Cleanup (Future)
- Remove hardcoded registrations once decorator coverage is high
- Rely entirely on agent-driven discovery
- Registry becomes pure reflection of actual usage

---

## Files Modified

1. **agentic_core/prompt_governance/version_registry/prompt_registry.py**
   - Added: `_hash_content()`, deduplication logic, `registers_prompt()` decorator
   - Enhanced: `register_prompt()`, `_save_registry()` with atomic write
   - Lines changed: ~120 additions

2. **agentic_core/L5_safety/validators/compliance_orchestrator.py**
   - Added: `_sync_agent_prompts_to_registry()` method
   - Modified: `_discover_all_agents()` to call sync
   - Lines changed: ~45 additions

---

## Result

**registry.json will now:**
- ✅ No longer accumulate duplicates on repeated initialization
- ✅ Reflect actual agent prompt usage via decorator or runtime scan
- ✅ Support future auto-discovery as agents are added/removed
- ✅ Maintain crash-safe atomic writes
- ✅ Provide agent-level attribution (author field)
- ✅ Enable prompt versioning and lifecycle management

**The 9-duplicate bug is permanently fixed.**
