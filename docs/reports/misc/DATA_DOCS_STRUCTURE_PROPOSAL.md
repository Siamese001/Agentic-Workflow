# Data and Docs Directory Structure Analysis & Proposal

## 🔍 Current State Analysis

### **Data Directory Structure**
```
data/
├── archives/           # Empty - archival storage
├── cache/             # Empty - temporary cache files
├── external/          # External reference materials
│   ├── openai_best_practices/
│   └── reference_playbooks/
├── freeze_reports/    # 3 files - system freeze reports
├── golden/           # 3 files - golden dataset/test files
├── golden_state/     # Empty - golden state snapshots
├── logs/             # Empty - data processing logs
├── manifests/        # 3 files - data manifests
├── output/           # 11 files - audit outputs and test results
├── processed/        # Empty - processed data files
├── prompt_governance/ # 161 files - prompt governance data
│   ├── evaluations/   # 4 files
│   ├── governance/    # 65 files
│   ├── injections/    # 71 files
│   ├── prompt_injections/ # 4 files
│   ├── registry/      # 4 files
│   ├── safety/        # 6 files
│   └── versioning/    # 2 files
├── prompt_libraries/  # Empty - prompt template libraries
├── prompts/           # Empty - prompt templates
├── raw/               # 1 file - raw input data
├── sdks_mcps/         # 14 files - SDK and MCP configurations
└── tasks/             # 3 files - task definitions
```

### **Docs Directory Structure**
```
docs/
├── MCP/               # 16 files - MCP integration documentation
├── metrics/           # 1 file - metrics documentation
└── reports/           # 99 files - project reports and analyses
```

---

## 🎯 Proposed Optimized Structure

### **Data Directory Reorganization**

#### **Rationale**
- Many empty directories indicate over-provisioned structure
- Content is heavily concentrated in prompt_governance and reports
- Need clearer separation of data types and purposes

#### **Proposed Structure**
```
data/
├── raw/                    # Raw input data and sources
│   ├── external/          # External reference materials
│   │   ├── openai_best_practices/
│   │   └── reference_playbooks/
│   └── inputs/            # Raw input files
├── processed/             # Processed and transformed data
│   ├── audit_results/     # Audit output files (from output/)
│   ├── evaluations/       # Evaluation results (from prompt_governance/evaluations/)
│   └── manifests/         # Data manifests
├── datasets/              # Structured datasets
│   ├── golden/           # Golden test datasets
│   ├── test_data/        # Test datasets
│   └── reference/        # Reference datasets
├── configurations/        # Configuration files
│   ├── sdks_mcps/        # SDK and MCP configurations
│   ├── prompts/          # Prompt configurations
│   └── tasks/            # Task definitions
├── governance/            # Governance and security data
│   ├── prompt_governance/ # Prompt governance data
│   │   ├── injections/   # Injection test data
│   │   ├── safety/       # Safety test data
│   │   ├── registry/      # Registry data
│   │   └── versioning/    # Version control data
│   └── security/         # Security-related data
├── cache/                 # Temporary cache files
├── archives/              # Archived historical data
└── logs/                  # Data processing logs
```

### **Docs Directory Reorganization**

#### **Rationale**
- Current structure is too flat
- Need better categorization by document type and purpose
- MCP documentation should be integrated with other technical docs

#### **Proposed Structure**
```
docs/
├── technical/             # Technical documentation
│   ├── architecture/     # Architecture documents
│   ├── integration/       # Integration guides
│   │   ├── mcp/          # MCP integration docs
│   │   └── sdks/         # SDK documentation
│   ├── api/              # API documentation
│   └── configuration/    # Configuration guides
├── project/               # Project management docs
│   ├── phases/           # Phase-by-phase documentation
│   ├── planning/         # Planning documents
│   └── governance/       # Project governance
├── analysis/              # Analysis and research
│   ├── reports/          # Analysis reports
│   ├── metrics/          # Metrics and measurements
│   └── investigations/   # RCA and investigation reports
├── guides/                # User and developer guides
│   ├── user_guides/      # End-user guides
│   ├── developer_guides/ # Developer documentation
│   └── deployment/       # Deployment guides
└── archive/               # Archived documentation
```

---

## 📋 File Migration Plan

### **Data Directory Migrations**

#### **Files to Move**
1. **prompt_governance/** → `data/governance/prompt_governance/`
   - Keep all existing substructure
   - This is a logical grouping with governance data

2. **output/** → `data/processed/audit_results/`
   - Move all audit JSON files
   - Move test reports

3. **external/** → `data/raw/external/`
   - Keep existing structure
   - Better reflects "raw external data"

4. **golden/** → `data/datasets/golden/`
   - Move golden test datasets

5. **sdks_mcps/** → `data/configurations/sdks_mcps/`
   - Configuration files belong here

6. **manifests/** → `data/processed/manifests/`
   - Data manifests are processed artifacts

7. **tasks/** → `data/configurations/tasks/`
   - Task definitions are configurations

8. **freeze_reports/** → `data/processed/freeze_reports/`
   - Freeze reports are processed outputs

#### **Directories to Remove**
- **prompt_libraries/** (empty)
- **prompts/** (empty)
- **golden_state/** (empty)
- **logs/** (empty - can be recreated if needed)
- **cache/** (empty - can be recreated if needed)
- **processed/** (will be recreated with new structure)

### **Docs Directory Migrations**

#### **Files to Move**
1. **MCP/** → `docs/technical/integration/mcp/`
   - All MCP integration documentation
   - Better integrated with other technical docs

2. **reports/** → `docs/analysis/reports/`
   - Move all 99 report files
   - Better categorized as analysis documents

3. **metrics/** → `docs/analysis/metrics/`
   - Metrics documentation
   - Logical grouping with analysis

#### **New Structure to Create**
- Create all proposed directories
- Move files according to plan
- Update any internal references

---

## 🎯 Benefits of Reorganization

### **Data Directory Benefits**
1. **Clearer Data Flow**: raw → processed → datasets
2. **Better Categorization**: Governance, configuration, and analysis separated
3. **Reduced Clutter**: Eliminate empty directories
4. **Scalable Structure**: Room for growth in each category

### **Docs Directory Benefits**
1. **Improved Navigation**: Logical categorization by purpose
2. **Better Integration**: MCP docs integrated with technical docs
3. **Enhanced Search**: Easier to find specific document types
4. **Professional Structure**: Follows standard documentation practices

---

## ⚠️ Risk Mitigation

### **Potential Risks**
1. **Broken references** - Internal links may break
2. **Automation disruption** - Scripts may reference old paths
3. **Team confusion** - Users may not know new structure

### **Mitigation Strategies**
1. **Update all references** - Search and replace internal links
2. **Update automation** - Modify scripts to use new paths
3. **Documentation** - Create migration guide and new structure overview
4. **Gradual migration** - Move in phases with validation

---

## 📈 Impact Summary

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Data directories** | 16 (many empty) | 12 (all purposeful) | **-25%** |
| **Docs directories** | 3 (flat) | 15 (categorized) | **+400%** |
| **Navigation clarity** | Low | High | **Major improvement** |
| **Empty directories** | 7 | 0 | **-100%** |

---

## ✅ Success Criteria

1. ✅ **All files moved** to appropriate new locations
2. ✅ **Empty directories eliminated**
3. ✅ **Logical categorization** implemented
4. ✅ **References updated** and working
5. ✅ **Team documentation** provided
6. ✅ **Automation updated** and tested

**Result**: Well-organized, maintainable, and scalable data and documentation structure that supports project growth and team productivity.
