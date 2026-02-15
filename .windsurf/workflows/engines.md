---
description: LCD+ 6-folder canonical skeleton for L0-L6 layer refactoring
---

# LCD+ Canonical Layer Skeleton

## Target Architecture

```text
agentic_core/
│
├── platform/                                 # cross-cutting ONLY (no L0-L6 imports)
│   ├── base_agents/
│   ├── interfaces/
│   ├── contracts/
│   ├── runtime/
│   ├── config/
│   ├── types/
│   ├── utils/
│   └── exceptions/
│
├── L0_maintenance/
│   ├── config/                               # absorbs: logs/, keys/
│   ├── types/
│   ├── reasoning/                            # absorbs: agents/, strategies/
│   ├── enforcement/                          # absorbs: integrity/, sensors/
│   ├── validators/
│   ├── utils/                                # absorbs: bootstrap/, legacy utils/
│   └── scripts/                              # NUANCE: ops-only (no LCD+ inside)
│
├── L1_cognition/
│   ├── config/
│   ├── types/                                # absorbs: meta_learning/types/
│   ├── reasoning/                            # absorbs: engine/, agents/, meta_learning/engine/
│   ├── enforcement/
│   ├── validators/                           # absorbs: meta_learning/validators/
│   ├── utils/
│   └── meta_learning/                        # NUANCE: package-only (no nested skeleton)
│
├── L2_execution/
│   ├── config/
│   ├── types/                                # absorbs: mcp/types/, sandbox/types/
│   ├── reasoning/                            # absorbs: engine/
│   ├── enforcement/                          # absorbs: mcp/, sandbox/docker/, sandbox/vm/
│   ├── validators/                           # absorbs: mcp/validators/
│   ├── utils/                                # absorbs: mcp/utils/
│   └── tools/                                # NUANCE: registry-only
│
├── L3_orchestration/
│   ├── config/
│   ├── types/
│   ├── reasoning/                            # absorbs: engine/, orchestrators/, strategies/,
│   │                                         #   routers/, patterns/, diagnostics/
│   ├── enforcement/                          # absorbs: core/ (execution constraints)
│   ├── validators/
│   └── utils/
│
├── L4_state/
│   ├── config/
│   ├── types/
│   ├── reasoning/                            # state planners only
│   ├── enforcement/                          # absorbs: ledger/, graph/
│   ├── validators/
│   ├── utils/
│   └── memory/                               # NUANCE: persistence providers only
│
├── L5_safety/
│   ├── config/                               # absorbs: *_config.py from validators/core/
│   ├── types/                                # absorbs: *_types.py, *Protocol.py from validators/core/
│   ├── reasoning/                            # absorbs: cognition/, red_teaming/, policy_engine/,
│   │                                         #   strategies/, adapters/, *Agent.py (reasoning-side)
│   ├── enforcement/                          # absorbs: guardrails/, governance/, security/,
│   │                                         #   gravity/, runtime/, human_review/, core/
│   ├── validators/                           # absorbs: validators/, anti_patterns/, *_validator.py
│   └── utils/                                # absorbs: surgical/, *_util.py, *_mixin.py
│
├── L6_observability/
│   ├── config/
│   ├── types/
│   ├── reasoning/                            # absorbs: agents/, engine/
│   ├── enforcement/                          # absorbs: audit/, compliance/, metrics/
│   ├── validators/
│   ├── utils/
│   └── dashboards/                           # NUANCE: static assets/build only (no python)
│
└── domains/                                  # OPTIONAL: separate from platform if needed
    ├── knowledge/
    └── prompt_governance/
```

## The 6-Folder LCD+ Standard

Every `L{n}_{name}/` layer MUST contain exactly these 6 subfolders, plus at most 1-2 nuance folders.

```text
L{n}_{name}/
├── config/          # The Layer's Laws           (snake_case.py)
├── types/           # The Layer's Language        (snake_case.py)
├── reasoning/       # Decision-making agents      (PascalCaseAgent.py)
├── enforcement/     # Constraint execution        (PascalCaseAgent.py)
├── validators/      # Passive auditing            (snake_case.py)
└── utils/           # Shared tooling              (snake_case.py)
```

### Classification Dimensions

| Folder       | Question It Answers            | Examples                                       |
| ------------ | ------------------------------ | ---------------------------------------------- |
| config/      | What are the rules?            | blueprint configs, registry configs             |
| types/       | What is the vocabulary?        | data models, enums, type defs, protocols, exceptions |
| reasoning/   | What should we do?             | planners, analyzers, strategists, routers       |
| enforcement/ | How do we prevent violations?  | guardrails, governors, seals, gates             |
| validators/  | Did we do it correctly?        | integrity checks, compliance audits, validators |
| utils/       | What tools do we share?        | parsers, formatters, helpers, mixins            |

### Hard Invariants

1. **Enforcement MUST run without reasoning.** Guardrails, gates, and governors cannot depend on reasoning agents. Reasoning MAY call enforcement, never the reverse.
2. **Platform has ZERO imports from L0-L6.** Layers import platform, never the reverse.
3. **Protocols belong in types/, not validators/.** Protocols define vocabulary, not audit logic.

---

## Platform Layer

Cross-cutting infrastructure that all L0-L6 layers may import. No layer-specific logic.

| Folder         | Absorbs From              | Purpose                                |
| -------------- | ------------------------- | -------------------------------------- |
| base_agents/   | `base_agents/`            | Identity-only base classes             |
| interfaces/    | `interfaces/`             | Abstract interface definitions         |
| contracts/     | `mixins/contracts/`       | Cross-layer contracts and capabilities |
| runtime/       | `runtime/`                | Shared runtime engine, exceptions      |
| config/        | `config/`                 | Global configuration                   |
| types/         | (new)                     | Cross-layer type definitions           |
| utils/         | `utils/`                  | Cross-layer utilities                  |
| exceptions/    | `runtime/exceptions/`     | Shared exception hierarchy             |

---

## Per-Layer Absorption Maps

### L0_maintenance

| Current Folder   | Target         | File Count |
| ---------------- | -------------- | ---------- |
| agents/          | reasoning/     | 3          |
| strategies/      | reasoning/     | 1          |
| integrity/       | enforcement/   | 2          |
| sensors/         | enforcement/   | 2          |
| utils/           | utils/         | 13         |
| bootstrap/       | utils/         | 1          |
| logs/            | config/        | 1          |
| keys/            | config/        | 0          |
| scripts/         | scripts/ (nuance) | 305     |

### L1_cognition

| Current Folder           | Target       | File Count |
| ------------------------ | ------------ | ---------- |
| engine/                  | reasoning/   | 21         |
| agents/                  | reasoning/   | 8          |
| meta_learning/engine/    | reasoning/   | 5          |
| config/                  | config/      | 2          |
| types/                   | types/       | 9          |
| meta_learning/types/     | types/       | 5          |
| validators/              | validators/  | 6          |
| meta_learning/validators/| validators/  | 1          |
| utils/                   | utils/       | 8          |

### L2_execution

| Current Folder    | Target         | File Count |
| ----------------- | -------------- | ---------- |
| engine/ (all)     | reasoning/     | 8          |
| mcp/ (agents)     | enforcement/   | 6          |
| sandbox/docker/   | enforcement/   | 1          |
| sandbox/vm/       | enforcement/   | 2          |
| config/           | config/        | 7          |
| types/            | types/         | 3          |
| mcp/types/        | types/         | 3          |
| sandbox/types/    | types/         | 1          |
| mcp/validators/   | validators/    | 1          |
| utils/            | utils/         | 1          |
| mcp/utils/        | utils/         | 2          |
| tools/            | tools/ (nuance)| 17         |

### L3_orchestration

| Current Folder | Target       | File Count |
| -------------- | ------------ | ---------- |
| engine/        | reasoning/   | 19         |
| orchestrators/ | reasoning/   | 11         |
| strategies/    | reasoning/   | 3          |
| routers/       | reasoning/   | 3          |
| patterns/      | reasoning/   | 1          |
| diagnostics/   | reasoning/   | 1          |
| core/          | enforcement/ | 3          |
| config/        | config/      | 2          |
| types/         | types/       | 17         |

### L4_state

| Current Folder  | Target            | File Count |
| --------------- | ----------------- | ---------- |
| ledger/         | enforcement/      | 6          |
| graph/          | enforcement/      | 2          |
| config/         | config/           | 2          |
| types/          | types/            | 8          |
| utils/          | utils/            | 11         |
| memory/         | memory/ (nuance)  | 17         |

### L5_safety (validators/core/ 112-file decomposition)

| File Pattern     | Target                    | Count |
| ---------------- | ------------------------- | ----- |
| *Agent.py        | reasoning/                | 41    |
| *_validator.py   | validators/               | 13    |
| *_util.py        | utils/                    | 20    |
| *_script.py      | OUT → ops_scripts/general/| 10    |
| *_types.py       | types/                    | 9     |
| *_config.py      | config/                   | 5     |
| *_mixin.py       | utils/                    | 4     |
| *Protocol.py     | types/                    | 4     |
| *Adapter.py      | reasoning/                | 1     |
| *Error.py        | types/                    | 1     |
| *Strategy.py     | reasoning/                | 1     |
| other            | classify manually         | 3     |

**Additional L5 folder absorption:**

| Current Folder         | Target       | File Count |
| ---------------------- | ------------ | ---------- |
| cognition/             | reasoning/   | 7          |
| red_teaming/           | reasoning/   | 4          |
| policy_engine/         | reasoning/   | 13         |
| strategies/            | reasoning/   | 2          |
| adapters/              | reasoning/   | 4          |
| guardrails/            | enforcement/ | 18         |
| governance/            | enforcement/ | 5          |
| security/              | enforcement/ | 4          |
| gravity/               | enforcement/ | 15         |
| runtime/               | enforcement/ | 2          |
| human_review/          | enforcement/ | 1          |
| core/                  | enforcement/ | 6          |
| validators/ root       | validators/  | 27         |
| validators/anti_patterns/| validators/| 7          |
| validators/surgical/   | utils/       | 3          |

### L6_observability

| Current Folder | Target         | File Count |
| -------------- | -------------- | ---------- |
| agents/        | reasoning/     | 13         |
| engine/        | reasoning/     | 1          |
| audit/         | enforcement/   | 1          |
| compliance/    | enforcement/   | 1          |
| metrics/       | enforcement/   | 2          |
| tracing/       | enforcement/   | 0          |
| telemetry/     | enforcement/   | 0          |
| reports/       | enforcement/   | 0          |
| logs/          | config/        | 0          |
| types/         | types/         | 1          |
| utils/         | utils/         | 1          |
| dashboards/    | dashboards/ (nuance) | 7    |

---

## Naming Conventions

| Folder       | Convention              | Example                          |
| ------------ | ----------------------- | -------------------------------- |
| config/      | `snake_case_config.py`  | `structure_blueprint_config.py`  |
| types/       | `snake_case_types.py`   | `health_status_types.py`         |
| reasoning/   | `PascalCaseAgent.py`    | `FileClassificationAgent.py`     |
| enforcement/ | `PascalCaseAgent.py`    | `GovernanceEnforcerAgent.py`     |
| validators/  | `snake_case_validator.py` | `ddd_alignment_validator.py`   |
| utils/       | `snake_case_util.py`    | `location_utils.py`              |

---

## Implementation Steps (Per Layer)

1. Create the 6 LCD+ folders + `__init__.py`
2. Classify every file by suffix/AST into target folder
3. Move files with `Move-Item`
4. Delete empty dissolved folders
5. Run mass import fix across codebase
6. Update `structure_blueprint_config.py`
7. Run `FileClassificationAgent --validate`
8. Run guardian tests
9. Verify no circular imports between reasoning/ and enforcement/

## Migration Order

1. **platform/** first (extract cross-cutting infra)
2. **L5_safety** (worst sprawl, highest payoff)
3. **L3_orchestration** (9 folders → 6)
4. **L6_observability** (13 folders → 7)
5. **L0_maintenance** (9 folders → 7)
6. **L2_execution** (7 folders → 7)
7. **L1_cognition** (7 folders → 7)
8. **L4_state** (6 folders → 7)
9. **domains/** last (knowledge/, prompt_governance/)
