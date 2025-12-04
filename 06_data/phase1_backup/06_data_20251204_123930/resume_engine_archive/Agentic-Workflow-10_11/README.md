# Agentic Workflow 10_10

A sophisticated multi-layer agentic architecture for temporal knowledge graph processing and intelligent workflow orchestration.

## 🏗️ Architecture Overview

This project implements a **5-layer agentic architecture** with capability-based organization:

```text
L1 (Planning)     → L2 (Execution) → L3 (Orchestration) → L4 (State) → L5 (Safety)
     ↑                    ↑                ↑                   ↑            ↑
   Strategy           Tools           Workflow          Data        Policy
   & Logic          & Actions        & Control        & Storage   & Rules
```

## 📚 Documentation

All documentation is organized in the **`root_docs/`** folder according to the canonical structure defined in **FOLDER_MAP.md**.

### **📖 [Documentation Overview](root_docs/docs_overview.md)**

- **[Architecture Guide](root_docs/architecture/FOLDER_STRUCTURE_GUIDE.md)** - Complete folder structure and functional organization
- **[Neo4j Integration](root_docs/integration/NEO4J_INTEGRATION_README.md)** - Graph database integration guide
- **[Pinecone Integration](root_docs/integration/PINECONE_INTEGRATION.md)** - Vector database integration
- **[Refactoring History](root_docs/refactoring/)** - Migration and reorganization documentation
- **[Testing Documentation](root_docs/testing/)** - Test results and validation reports

## Environment

### Python Version Update (2025-01)
This project now targets:

```text
Python 3.12.x
```

Python 3.14 is not yet fully supported by Pydantic, FastAPI, Redis, or OpenAI SDKs, and causes runtime errors.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Neo4j database (optional, for graph features)
- Pinecone account (for vector storage)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Agentic-Workflow-10_10

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USERNAME="neo4j"
export NEO4J_PASSWORD="your_password"
```

## 📁 Canonical Structure

This repository follows the canonical structure defined in **FOLDER_MAP.md**:

### Core Layers

- **`l1/`** - Planning layer: Strategic thinking and decision-making
- **`l2/`** - Execution layer: Tool execution and direct actions
- **`l3/`** - Orchestration layer: Workflow coordination and control
- **`l4/`** - State layer: Data storage and state management
- **`l5/`** - Safety layer: Safety, policy, and governance

### Capability Folders

- **`agents/`** - All agent implementations
- **`orchestration/`** - Workflow and DAG management
- **`state/`** - Data models and storage
- **`infrastructure/`** - Core infrastructure components
- **`providers/`** - External service integrations
- **`tools/`** - Reusable tools and utilities

### Documentation Rule

**Every major folder contains a `/docs/` subfolder where ALL documentation for that folder is stored.** No documentation exists at the repository root outside `root_docs/`.

## 🔧 Key Features

### **Temporal Knowledge Graph**

- Entity resolution and canonicalization
- Temporal triplet extraction and validation
- Multi-hop reasoning and trend analysis
- Neo4j and Pinecone dual-backend support

### **Agentic Architecture**

- Layer-based separation of concerns
- Capability-driven organization
- Safety-first design with L5 validation
- Workflow orchestration with DAG execution

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run Neo4j integration tests
pytest tests/unit/l2_execution/test_neo4j_integration.py
```

## 🛠️ Development

### Code Quality

```bash
# Linting
ruff check .

# Type checking
mypy .

# Import validation
python import_check.py
```

### Architecture Compliance

- Follow L1-L5 layer separation
- Maintain capability-based organization
- Ensure graceful degradation for optional components
- Write comprehensive tests for all layers

## 🤝 Contributing

1. Read the [Architecture Guide](root_docs/architecture/FOLDER_STRUCTURE_GUIDE.md)
2. Understand the layering principles
3. Follow the established patterns
4. Add appropriate tests
5. Update documentation in the appropriate `/docs/` folder

## 📄 License

[License information here]

---

**For detailed documentation, see the [root_docs/](root_docs/) folder.**
