# SSOT Boundary Policy Normalization

## Policy Statement

**SSOT Boundary Rule:** Ban non-doc references to removed prompt roots `data/prompts/` and `data/prompt_libraries/`.

## Exclusion Classes and Rationale

The following directory classes are excluded from enforcement:

1. **docs/** - Documentation directory containing historical references, plans, and reports
   - Rationale: Documentation is expected to reference historical paths for context

2. **archives/** - Archived historical artifacts
   - Rationale: Archives preserve historical state and are not active code

3. **data/manifests/** - Generated historical checksum manifests
   - Rationale: These are generated files containing historical checksums, not enforcement-bearing source code

4. ****/__pycache__/** - Python runtime cache directories
   - Rationale: Runtime artifacts that may contain compiled references

## Enforcement Rules

- **No per-file exceptions:** Only directory-class exclusions are permitted
- **No ad-hoc allowlists:** Specific files cannot be whitelisted
- **Pattern construction:** Tests must construct forbidden patterns to avoid self-matching

## Enforcement Location

- **Test:** `tests/architecture/test_prompt_root_boundary.py`
- **Method:** Pure Python scanner with deterministic file walking
- **Scope:** Entire repository excluding the above directory classes

## Implementation Notes

- Boundary test excludes only the four directory classes above
- All other files, including meta_prompts, prompt_injections, and tests, are subject to enforcement
- Forbidden patterns are constructed as `"data/" + "prompts/"` and `"data/" + "prompt_" + "libraries/"` to avoid self-matching
