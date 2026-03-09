# Graph Construction Protocol

**MANDATORY before any non-trivial code investigation per §3.4.**

## Step 1: Define Graph Roots

Identify the starting points for graph analysis:

```
GRAPH_ROOTS:
- path/to/file1.py (direct modification target)
- path/to/file2.py (suspected impact target)
- path/to/file3.py (registry/factory entry point)
```

## Step 2: Specify Required Node Types

At minimum, the graph MUST model these node types where applicable:

```
NODE_TYPES:
✅ Modules (Python files)
✅ Classes
✅ Functions/methods
✅ Symbols (variables, constants)
✅ Decorators
✅ Registry entries
✅ Factory/provider definitions
✅ Config objects
✅ CLI entrypoints
✅ Test functions
```

## Step 3: Specify Required Edge Types

At minimum, the graph MUST model these edge types where applicable (§3.4):

```
EDGE_TYPES:
✅ Module import edges (import statements)
✅ Symbol import edges (from X import Y)
✅ Class inheritance edges (class A(B))
✅ Protocol/mixin realization edges (class A(Protocol))
✅ Function/method call edges (A calls B)
✅ Decorator attachment edges (@decorator)
✅ Registry lookup/registration edges (register(X), get_agent(Y))
✅ Factory/provider resolution edges (create_X(), provide_Y())
✅ Config consumption edges (reads config.X)
✅ CLI entrypoint → function edges (main() → run())
✅ Test → production coverage edges (test_X imports X)
```

## Step 4: Build the Graph

Use AST parsing and module inspection to construct the graph:

**Recommended tools:**
- Python `ast` module for AST parsing
- `importlib` for module inspection
- Repository-specific tools: `tools/dep_graph_db.py`, `ops_scripts/ci/_ast_*.py`

**Output format:**
```
DEPENDENCY_GRAPH:
Nodes: <count>
Edges: <count>
Graph roots: [list]
Max depth: <depth>
```

## Step 5: Extract Graph Relationships

For each graph root, extract:

### Upstream Dependencies (What this file imports/depends on)
```
file1.py imports:
  - common/utils.py (module import)
  - config/settings.py (symbol import: SETTING_X)
  - agentic_core/L2_execution/base.py (class inheritance: BaseClass)
```

### Downstream Dependents (What imports/depends on this file)
```
file1.py used by:
  - file2.py (module import)
  - apps_lic/engines/control_plane.py (function call: file1.process())
  - tests/test_file1.py (test coverage)
```

### Call Edges (Function/method calls)
```
file1.py::function_a calls:
  - file1.py::function_b (internal call)
  - common/utils.py::helper_function (external call)
```

### Inheritance Edges (Class hierarchies)
```
file1.py::MyClass inherits from:
  - agentic_core/L2_execution/base.py::BaseClass
  - mixins/logging.py::LoggingMixin
```

### Registry/Factory Edges (Dynamic resolution)
```
file1.py::MyAgent registered as:
  - "my_agent" in agent_registry

file1.py::create_processor resolves to:
  - ProcessorA (when config.mode == "A")
  - ProcessorB (when config.mode == "B")
```

### Test Coverage Edges (Test → production)
```
tests/test_file1.py covers:
  - file1.py::function_a (direct test)
  - file1.py::function_b (indirect via function_a)

Coverage gaps:
  - file1.py::function_c (NO TEST COVERAGE)
```

## Step 6: Detect Cross-Layer Edges

Identify edges that cross architectural layer boundaries:

```
CROSS_LAYER_EDGES:
- file1.py → agentic_core/L2_execution/base.py (L5→L2, VALID per architecture)
- apps_lic/reasoning/Agent.py → tools/evidence/helper.py (apps→tools, INVALID - HARD FAIL)
```

## Step 7: Detect Cycles and SCCs

Identify circular dependencies:

```
CYCLE_DETECTION:
No cycles detected
OR
Cycle detected: file1.py → file2.py → file3.py → file1.py (HARD FAIL per §4.3)

Strongly Connected Components (SCCs):
- SCC1: [file1.py, file2.py] (mutual dependency)
```

## Step 8: Validate Boundary Compliance

Check for layer inversions and sovereignty violations:

```
BOUNDARY_VALIDATION:
Layer structure (per structure_blueprint.py):
  L0_routing → L1_cognition → L2_execution → ... → L6_meta

Violations:
None detected
OR
- L2_execution/tools/write_gateway.py → L0_routing/scripts/execute_ssot.py (LAYER INVERSION - HARD FAIL)
```

## Step 9: Document Graph Metadata

Record graph construction metadata for evidence:

```
GRAPH_METADATA:
Construction timestamp: <ISO timestamp>
Graph extractor: <tool/script used>
AST parser version: <version>
Repository commit: <git hash>
Total files analyzed: <count>
Parse errors: <count> (if >0, see fail-closed discipline)
Incomplete files: [list if any]
```

## Fail-Closed Discipline (§3.6)

If AST parsing fails:

```
PARSE_FAILURES:
❌ file_with_syntax_error.py: SyntaxError at line 42
❌ file_with_encoding_issue.py: UnicodeDecodeError

IMPACT:
- Graph is INCOMPLETE
- Conclusions are PARTIAL
- Confidence level: LOW
- DO NOT proceed with high-confidence claims
- DO NOT fall back to grep/regex silently

REQUIRED ACTIONS:
1. Record exact parse errors
2. Identify blocked files
3. Mark all conclusions as PARTIAL
4. Stop short of claiming confidence
5. Report limitation explicitly
```

## Constitutional Compliance Checklist

Before proceeding with analysis:

- [ ] Graph roots explicitly defined
- [ ] All required node types included
- [ ] All required edge types included
- [ ] Upstream dependencies extracted
- [ ] Downstream dependents extracted
- [ ] Cross-layer edges identified
- [ ] Cycles/SCCs detected
- [ ] Boundary violations checked
- [ ] Test coverage edges mapped
- [ ] Parse failures recorded (if any)
- [ ] NO silent fallback to grep/regex
- [ ] Graph metadata documented
