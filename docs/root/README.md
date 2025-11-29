# Root Documentation - Agentic Workflow 10_10

This directory contains all project-wide documentation as required by the canonical structure defined in **FOLDER_MAP.md**.

## 📁 Documentation Structure

### **`architecture/`**
Core architecture and design documentation

- `FOLDER_STRUCTURE_GUIDE.md` - Complete guide to folder structure and functional organization

### **`integration/`**
External system integration documentation

- `NEO4J_INTEGRATION_README.md` - Neo4j graph database integration guide
- `PINECONE_INTEGRATION.md` - Pinecone vector database integration

### **`refactoring/`**
Historical refactoring documentation and migration guides

- `REORGANIZATION_COMPLETE.md` - Summary of completed reorganization
- `REORGANIZATION_PLAN.md` - Original reorganization plan
- `README_REFACTORING.md` - Refactoring process and methodology
- `11-24-2025/` - Detailed phase-by-phase refactoring documentation

### **`testing/`**
Testing documentation, validation reports, and test results

- `baseline_test_results.md` - Baseline testing results
- `FINAL_SDK_MCP_ANALYSIS.md` - SDK and MCP server analysis
- `MCP_SERVER_INSTALLATION.md` - MCP server setup guide
- `PHASE_*_SUMMARY.md` - Various testing phase summaries
- `setup_validation_report.md` - Environment validation results

### **`injection_types.md`**
Security and injection type documentation

## 🗺️ Navigation

**New to the project?** Start with:

1. `architecture/FOLDER_STRUCTURE_GUIDE.md` - Understand the codebase structure
2. `integration/NEO4J_INTEGRATION_README.md` - Learn about Neo4j integration
3. `refactoring/REORGANIZATION_COMPLETE.md` - Understand recent changes

**Setting up the environment?** Check:

1. `integration/` - Database setup guides
2. `testing/MCP_SERVER_INSTALLATION.md` - MCP server installation
3. `testing/setup_validation_report.md` - Environment validation

## 📚 Documentation Standards

All documentation follows these conventions:

- **Clear headings** with proper markdown structure
- **Code examples** with language specification
- **Navigation links** between related documents
- **Practical examples** and use cases
- **Troubleshooting sections** for common issues

## 🔄 Canonical Structure Enforcement

This repository enforces the canonical structure defined in **FOLDER_MAP.md**:

- **Root documentation** lives in `root_docs/` (this folder)
- **Folder-specific documentation** lives in each major folder's `/docs/` subfolder
- **No documentation** is permitted at the repository root outside this folder
- **All major folders** must contain a `/docs/` subfolder with their local documentation

This ensures consistent organization and makes documentation easily discoverable and maintainable.
