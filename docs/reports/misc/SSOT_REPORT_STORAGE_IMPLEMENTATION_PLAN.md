# SSOT Report Storage Implementation - Phased Execution Plan

Implement a comprehensive phased approach to ensure all reports are stored in the canonical SSOT location `docs/reports` with maximum success probability through incremental, validated steps.

## Current State Analysis

**SSOT Location**: `docs/reports/` contains 180+ properly organized reports
**Scattered Reports**: Found references to `docs/reports/plans/` in multiple phase summaries
**Root Reports**: Multiple reports in project root (PHASE*.md, RCA*.md, etc.)
**No `.windsurf` Directory**: The `.windsurf` directory doesn't exist in current workspace

## Phased Implementation Strategy

### **Phase 1: Foundation & Discovery (Days 1-2)**
**Objective**: Establish validation framework without disruption

**1.1 Discovery Enhancement**
- Extend `agentic_core/utils/ssot_discovery.py` with `validate_report_location()`
- Create `ReportLocationValidator` class with pattern matching
- Add report patterns to existing discovery system

**1.2 Pre-commit Hook Foundation**
- Create `.pre-commit-config.yaml` entry for `check-report-location`
- Implement basic validation script in `scripts/hooks/validate_report_location.py`
- Hook runs in dry-run mode (no moves) for first 48 hours

**1.3 Baseline Inventory**
- Generate comprehensive report location manifest
- Categorize reports: SSOT-compliant vs misplaced
- Create migration priority matrix

### **Phase 2: Controlled Migration (Days 3-4)**
**Objective**: Safely migrate high-priority misplaced reports

**2.1 Migration Script Development**
- Create `ops_scripts/maintenance/migrate_reports_to_ssot.py`
- Implement git-aware moves with history preservation
- Add rollback capability and backup procedures

**2.2 Pilot Migration**
- Select 5-10 low-risk reports for pilot migration
- Validate git history preservation
- Update internal references automatically
- Generate migration manifest

**2.3 Validation Framework**
- Extend Guardian tests with report location validation
- Add `test_report_location_compliance.py` to test suite
- Implement automated reference checking

### **Phase 3: Enforcement Activation (Days 5-6)**
**Objective**: Activate pre-commit hook with auto-correction

**3.1 Hook Activation**
- Switch pre-commit hook from dry-run to active mode
- Enable auto-move functionality for new reports
- Add violation reporting to `logs/compliance_reports/`

**3.2 Bulk Migration**
- Execute migration on remaining misplaced reports
- Prioritize by usage frequency and importance
- Maintain detailed migration logs

**3.3 Reference Updates**
- Update all internal references to moved reports
- Update documentation and README files
- Validate no broken links remain

### **Phase 4: Agent Integration (Days 7-8)**
**Objective**: Ensure all agents generate reports in SSOT location

**4.1 Report Generation Protocol**
- Standardize report output paths across all agents
- Update report generation methods to use `docs/reports/`
- Implement timestamped subdirectory organization

**4.2 Agent Updates**
- Audit all report-generating agents
- Update hardcoded paths to use SSOT protocol
- Add report location validation to agent tests

**4.3 CI/CD Integration**
- Add report location validation to GitHub Actions
- Integrate with existing dashboard monitoring
- Add compliance metrics to observability

### **Phase 5: Hardening & Documentation (Days 9-10)**
**Objective**: Complete hardening and team enablement

**5.1 Advanced Validation**
- Implement semantic report naming validation
- Add report metadata standards enforcement
- Create report quality gate validation

**5.2 Documentation & Training**
- Update `.windsurfrules` with report location rules
- Create team training materials
- Document troubleshooting procedures

**5.3 Monitoring & Maintenance**
- Add report location metrics to dashboards
- Implement ongoing compliance monitoring
- Create maintenance automation scripts

## Sub-Phase Breakdown for Maximum Success

### **Phase 1 Sub-Phases**
- **1.1a**: Discovery extension (4 hours)
- **1.1b**: Pattern matching implementation (2 hours)
- **1.2a**: Hook foundation (3 hours)
- **1.2b**: Dry-run validation (3 hours)
- **1.3a**: Inventory generation (2 hours)
- **1.3b**: Priority matrix creation (2 hours)

### **Phase 2 Sub-Phases**
- **2.1a**: Migration script core (6 hours)
- **2.1b**: Git-aware moves (4 hours)
- **2.2a**: Pilot selection (1 hour)
- **2.2b**: Pilot execution (4 hours)
- **2.2c**: Pilot validation (3 hours)
- **2.3a**: Test framework extension (4 hours)
- **2.3b**: Compliance test creation (4 hours)

### **Phase 3 Sub-Phases**
- **3.1a**: Hook activation (2 hours)
- **3.1b**: Auto-move enablement (3 hours)
- **3.1c**: Violation reporting (3 hours)
- **3.2a**: Bulk migration execution (8 hours)
- **3.2b**: Migration validation (4 hours)
- **3.3a**: Reference scanning (4 hours)
- **3.3b**: Reference updates (4 hours)

### **Phase 4 Sub-Phases**
- **4.1a**: Protocol standardization (3 hours)
- **4.1b**: Subdirectory organization (2 hours)
- **4.2a**: Agent audit (4 hours)
- **4.2b**: Agent updates (8 hours)
- **4.2c**: Agent testing (4 hours)
- **4.3a**: CI/CD integration (4 hours)
- **4.3b**: Dashboard integration (4 hours)

### **Phase 5 Sub-Phases**
- **5.1a**: Semantic validation (4 hours)
- **5.1b**: Metadata standards (3 hours)
- **5.1c**: Quality gates (3 hours)
- **5.2a**: Rules update (2 hours)
- **5.2b**: Training materials (4 hours)
- **5.2c**: Documentation (2 hours)
- **5.3a**: Metrics implementation (4 hours)
- **5.3b**: Monitoring setup (3 hours)
- **5.3c**: Maintenance automation (3 hours)

## Success Criteria by Phase

**Phase 1**: Discovery system operational, baseline inventory complete
**Phase 2**: Pilot migration successful, validation framework proven
**Phase 3**: All reports migrated, pre-commit hook active
**Phase 4**: All agents compliant, CI/CD integration complete
**Phase 5**: Full hardening, team trained, monitoring operational

## Risk Mitigation per Phase

**Phase 1**: Backup all reports before discovery, implement read-only operations
**Phase 2**: Use feature flags, maintain rollback capability, pilot testing
**Phase 3**: Gradual activation, continuous monitoring, quick rollback procedures
**Phase 4**: Comprehensive testing, backward compatibility, staged rollout
**Phase 5**: Documentation validation, training verification, monitoring alerts

## Rollback Strategy

Each phase includes specific rollback triggers and procedures:
- Phase 1: Disable discovery extensions
- Phase 2: Revert pilot migrations using git
- Phase 3: Disable pre-commit hook
- Phase 4: Revert agent updates to previous version
- Phase 5: Maintain previous monitoring system

## Validation Checkpoints

End of each phase requires:
- Automated test suite passing
- Manual review of migrated reports
- Performance impact assessment
- Team sign-off on changes
- Documentation update verification
