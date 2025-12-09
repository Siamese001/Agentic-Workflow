# CANON 2025 — FOLDER NAMING LAW

## ✅ ALLOWED

- `archives/` (plural) - CORRECT, Canon-approved

## ❌ FORBIDDEN FOREVER

- `archive/` (singular) - ZOMBIE, will be executed on sight

## ZOMBIE EXTERMINATION PROTOCOL

Any code, script, or human that attempts to create `archive/` will face:

1. **Pre-commit hook failure** - Instant death
2. **Git hook failure** - Instant death  
3. **CI pipeline failure** - Instant death
4. **Canon validator failure** - Instant death

## EXAMPLES OF ZOMBIE CREATION (ALL FORBIDDEN)

```python
# THESE WILL DIE
os.mkdir("archive")          # ❌ ZOMBIE
Path("archive").mkdir()      # ❌ ZOMBIE
mkdir("archive")             # ❌ ZOMBIE
```

## CORRECT USAGE

```python
# THESE LIVE
os.mkdir("archives")         # ✅ CANON
Path("archives").mkdir()     # ✅ CANON
mkdir("archives")            # ✅ CANON
```

## ENFORCEMENT

- Pre-commit hooks scan every commit
- Git hooks prevent zombie creation
- CI/CD validates folder naming
- Canon validator checks structure

### THE ZOMBIE DIES TODAY. ONLY `archives/` LIVES FOREVER.

*Canon 2025 - Final Extermination Order*
