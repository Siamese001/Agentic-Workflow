# ADG Prompt Assembly

Structured packet builders that convert raw ADG canonical outputs into grounded, deterministic, contradiction-aware, token-budgeted **PromptEnvelope** packets.

## Architecture

```
tools/adg/prompt_assembly/
    contracts.py              # Core types: EvidenceItem, EvidenceBundle, PromptEnvelope
    retrieval/
        adapters.py           # 6 retrieval adapters (C0-side, read-only)
    shaping/
        evidence_shaper.py    # Dedupe, normalize, reconcile, contradiction-retain
    packets/
        registry.py           # 8 packet templates + PacketRegistry
        builders.py           # 8 builder functions + build_packet() dispatcher
    budgeting/
        token_budgeter.py     # Token estimation, stratification, overflow handling
    cli.py                    # CLI entrypoint
```

### Boundary Rules

- **C0 retrieves only** — retrieval adapters fetch raw data, nothing else
- **Prompt assembly packages only** — builders assemble, never retrieve or execute
- **Graph DB augments** — all graph DB evidence carries `is_derived=True`
- **Contradictions preserved** — never hidden, always surfaced as `contradiction_flags`
- **No prompt scatter** — all packet types go through the central PacketRegistry

## Packet Types

| Type | Purpose |
|------|---------|
| `determinism_rca` | Diagnose digest mismatches, reconciliation failures |
| `p0_failure` | Analyze hard-fail violations (layer, cycles, dynamic_exec) |
| `ratchet_review` | Compare P1/P2 counts against baseline ceilings |
| `unknown_unresolved_triage` | Classify unknown modules and unresolved imports |
| `hotspot_investigation` | Identify high fan-in/fan-out nodes and risk surfaces |
| `infrastructure_boundary` | Detect raw infra spread and write-path bypass risks |
| `graph_path_explanation` | Explain exact violating paths and illegal hops |
| `executive_summary` | Concise one-run summary with blockers and next steps |

## CLI Usage

```bash
# List all packet types
python -m tools.adg.prompt_assembly --list

# Build a specific packet (JSON output)
python -m tools.adg.prompt_assembly --packet executive_summary

# Build with markdown output
python -m tools.adg.prompt_assembly --packet ratchet_review --format markdown

# Build all packets
python -m tools.adg.prompt_assembly --all

# Write to directory
python -m tools.adg.prompt_assembly --all --output artifacts/adg/packets/

# Specify SQLite path
python -m tools.adg.prompt_assembly --packet hotspot_investigation --sqlite path/to/db.sqlite

# Graph path explanation with node arguments
python -m tools.adg.prompt_assembly --packet graph_path_explanation --from-node module_a --to-node module_b
```

## PromptEnvelope Structure

Every packet follows strict block ordering:

1. **system_block** — operator mode / role definition
2. **policy_block** — invariants, constraints (shared across all packets)
3. **task_block** — what the consumer should do
4. **must_use_evidence** — canonical evidence (source-of-truth)
5. **optional_evidence** — derived/augmenting evidence (graph DB)
6. **contradiction_flags** — explicit disagreements between sources
7. **abstain_instructions** — when/how to refuse if evidence insufficient
8. **refine_instructions** — what to request for better evidence
9. **output_schema** — expected response structure
10. **replay_metadata** — snapshot IDs, commit SHAs, digests for replay

## Token Budgeting

Each packet type has a defined token budget. When evidence exceeds the budget:

1. **Optional evidence trimmed first** (derived/graph DB)
2. **Must-use evidence narrowed** by severity stratification
3. **Summarize** — condense overflow into counts
4. **Abstain** — if even minimal evidence doesn't fit

Fixed blocks (system, policy, task, contradictions, schema) are **never trimmed**.

## Tests

```bash
python -m pytest tests/unit/tools/adg/prompt_assembly/ -v
```

62 tests covering contracts, shaper, budgeter, registry, and builders.
