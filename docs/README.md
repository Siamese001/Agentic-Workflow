# Documentation - Agentic Workflow 10_10

This directory contains all documentation for the Agentic Workflow 10_10 project, organized by functional area.

## 📁 Documentation Structure

### **`architecture/`**

Core architecture and design documentation

- `FOLDER_STRUCTURE_GUIDE.md` - Complete guide to folder structure and functional organization
- Understanding the L1-L5 layer architecture and capability-based organization

### **`integration/`**

External system integration documentation

- `NEO4J_INTEGRATION_README.md` - Neo4j graph database integration guide
- `PINECONE_INTEGRATION.md` - Pinecone vector database integration
- Database setup, configuration, and usage patterns

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

Security and injection type documentation (moved from prompts/)

## 🗺️ Quick Navigation

**New to the project?** Start with:

1. `architecture/FOLDER_STRUCTURE_GUIDE.md` - Understand the codebase structure
2. `integration/NEO4J_INTEGRATION_README.md` - Learn about Neo4j integration
3. `refactoring/REORGANIZATION_COMPLETE.md` - Understand recent changes

**Setting up the environment?** Check:

1. `integration/` - Database setup guides
2. `testing/MCP_SERVER_INSTALLATION.md` - MCP server installation
3. `testing/setup_validation_report.md` - Environment validation

**Working on a specific feature?** Refer to:

1. `architecture/` - Understanding where your code belongs
2. `integration/` - Database and external service patterns
3. `testing/` - Testing approaches and validation

## 📚 Documentation Standards

All documentation follows these conventions:

- **Clear headings** with proper markdown structure
- **Code examples** with language specification
- **Navigation links** between related documents
- **Practical examples** and use cases
- **Troubleshooting sections** for common issues

## 🔄 Recent Changes

- **Moved all root-level markdown files** to appropriate `docs/` subdirectories
- **Organized by functional area** rather than scattered across project
- **Consolidated testing documentation** from multiple locations
- **Centralized refactoring history** in dedicated folder

This organization makes it easier to find relevant documentation and understand the project structure.
