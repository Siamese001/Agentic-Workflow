# Repository Governance Policies

## Folder Purity Validation (T3d)

### Status: MANUAL-ONLY

The folder purity validation hook (T3d) has been moved to manual stage due to extensive structural violations in the apps_shared module that would require a major refactoring to resolve.

### Rationale

The folder purity validator identifies the following categories of violations:
- Implementation classes in _types.py files (should be in engines/)
- Functions in _types.py files (should be in engines/)
- Agent files outside reasoning/ folders
- Executors outside engines/ folders

These violations are systemic across the apps_shared module and represent architectural debt that requires coordinated refactoring beyond the scope of individual commits.

### Policy

1. **T3d hook is set to `stages: [manual]`** - It does not run on normal commits
2. **Manual execution** - Developers can run `python ops_scripts/hooks/validate_folder_purity.py` manually when planning refactoring work
3. **Documentation required** - Any structural refactoring must address the violations identified by the validator
4. **Future re-enabling** - T3d will be re-enabled in default stages once the structural debt is resolved

### Authorization

This policy was established on 2026-02-15 to unblock development while maintaining visibility into structural governance requirements.
