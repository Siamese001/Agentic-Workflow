# Graph Construction Protocol

**T3 mandatory, T2 recommended. Per §0 and §2.1.**

## Step 1: Define Graph Roots

Identify starting points: direct modification targets, suspected impact targets, registry/factory entry points.

## Step 2: Required Node Types

Modules, classes, functions/methods, symbols, decorators, registry entries, factory/provider definitions, config objects, CLI entrypoints, test functions.

## Step 3: Required Edge Types

| Edge Type | Example |
|-----------|---------|
| Module imports | `import X` |
| Symbol imports | `from X import Y` |
| Class inheritance | `class A(B)` |
| Protocol/mixin realization | `class A(Protocol)` |
| Function/method calls | `A calls B` |
| Decorator attachment | `@decorator` |
| Registry lookup/registration | `register(X)`, `get_agent(Y)` |
| Factory/provider resolution | `create_X()`, `provide_Y()` |
| Config consumption | reads `config.X` |
| CLI entrypoint→function | `main()` → `run()` |
| Test→production coverage | `test_X imports X` |

## Step 4: Build the Graph

Use ADG hot cache (`adg_status`, `adg_node`, `adg_edge_fanout/fanin`) or `tools/generate_full_adg.py` for fresh builds.

## Step 5: Extract Relationships

For each root: upstream dependencies (what it imports), downstream dependents (what imports it), call edges, inheritance edges, registry/factory edges, test coverage edges.

## Step 6: Cross-Layer & Boundary Checks

- Identify edges crossing L0–L6 boundaries
- Detect cycles and SCCs (circular dependencies = HARD FAIL per §8.2)
- Check layer inversion violations

## Step 7: Document Graph Metadata

Record: construction timestamp, tool used, repo commit, total files analyzed, parse errors (if >0 → see `fail_closed_discipline.md`).

## Compliance Checklist

- [ ] Graph roots defined
- [ ] Required edge types extracted
- [ ] Upstream/downstream identified
- [ ] Cross-layer edges checked
- [ ] Cycles/boundary violations checked
- [ ] Test coverage edges mapped
- [ ] Parse failures recorded (if any)
- [ ] NO grep/regex as primary method
