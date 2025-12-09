# Folder Structure Guide - Agentic Workflow 10_10

This guide explains the functional purpose of each folder in the Agentic Workflow 10_10 repository to help you understand where files are located and what they do.

## 🏗️ Architecture Overview

This project uses a **5-layer agentic architecture** (L1-L5) plus capability-based organization. Think of it like a company with different departments and management levels.

```text
L1 (Planning)     → L2 (Execution) → L3 (Orchestration) → L4 (State) → L5 (Safety)
     ↑                    ↑                ↑                   ↑            ↑
   Strategy           Tools           Workflow          Data        Policy
   & Logic          & Actions        & Control        & Storage   & Rules
```

## 📁 Core Folders Explained

### **L1 - Planning Layer** (`l1/`)

**Purpose**: Strategic thinking and decision-making

- **What it does**: Creates plans, strategies, and analyzes what needs to be done
- **Analogy**: The executive team that decides company strategy
- **Key files**:
  - `strategy_planning.py` - Creates high-level strategies
  - `qa_planning.py` - Plans question-answering approaches
  - `safety_planning.py` - Plans safety measures
  - `interfaces.py` - Defines planning contracts

### **L2 - Execution Layer** (`l2/`)

**Purpose**: Tool execution and direct actions

- **What it does**: Actually runs tools, calls APIs, executes code
- **Analogy**: The workers who use tools to get things done
- **Key files**:
  - `agents.py` - Main execution agents
  - `factual_qa.py` - Answers factual questions (Neo4j integration)
  - `kg_writer.py` - Writes to knowledge graphs (Neo4j integration)
  - `tool_output_validator.py` - Validates tool outputs

### **L3 - Orchestration Layer** (`l3/`)

**Purpose**: Workflow coordination and control

- **What it does**: Manages complex workflows, coordinates between agents
- **Analogy**: Project managers who coordinate teams
- **Key files**:
  - `unified_workflow_orchestrator.py` - Main workflow controller
  - `adapters.py` - Adapters for different workflow components
  - `interfaces.py` - Defines orchestration contracts

### **L4 - State Layer** (`l4/`)

**Purpose**: Data storage and state management

- **What it does**: Manages all data, databases, and system state
- **Analogy**: The data warehouse and records department
- **Key files**:
  - `state_manager.py` - Manages system state
  - `adapters.py` - Database adapters (SQLite, Pinecone, etc.)

### **L5 - Safety Layer** (`l5/`)

**Purpose**: Safety, policy, and governance

- **What it does**: Enforces rules, validates safety, prevents harmful actions
- **Analogy**: Legal and compliance department
- **Key files**:
  - `safety_validator.py` - Validates safety of actions
  - `adapters.py` - Safety policy adapters

## 🔧 Capability-Based Folders

### **`agents/`**

**Purpose**: All agent implementations

- Contains planning agents, execution agents, and meta-agents
- Organized by capability rather than layer

### **`orchestration/`**

**Purpose**: Workflow and DAG management

- `kg_ingestion_dag.py` - Knowledge graph ingestion workflow
- `workflow_engine.py` - Core workflow execution engine

### **`state/`**

**Purpose**: Data models and storage

- `temporal_kg.py` - Temporal knowledge graph (Pinecone-backed)
- `entity_resolution.py` - Entity resolution system
- `triplet_store.py` - Triplet storage (SQLite/NetworkX)

### **`infrastructure/`**

**Purpose**: Core infrastructure components

- `dag_engine/` - Directed acyclic graph execution engine
- `prompts/` - Prompt management system

### **`providers/`**

**Purpose**: External service integrations

- LLM providers, database providers, API providers

### **`tools/`**

**Purpose**: Reusable tools and utilities

- File operations, search, validation tools

## 🤔 What is "cms"?

**CMS** = **Content Management System** for prompts

Located in `prompts/cms/`, this is a specialized system for:

- Managing prompt templates and versions
- Storing prompt schemas and validation
- Compiling and rendering prompts
- Maintaining prompt changelogs

**Why it exists**: The system needs sophisticated prompt management for different agents, use cases, and languages. The CMS ensures prompts are versioned, validated, and easily retrievable.

## 📊 Other Important Folders

### **`config/`**

- Configuration files and settings
- Environment-specific configs

### **`core/`**

- Core models, interfaces, and shared utilities
- Fundamental data structures

### **`eval/`**

- Evaluation and testing frameworks
- Golden state testing, simulation

### **`tests/`**

- Unit tests, integration tests
- Organized by layer and capability

### **`cli/`**

- Command-line interface tools
- Batch processing utilities

### **`runtime/`**

- Runtime monitoring and observability
- Performance metrics and logging

## 🗺️ Navigation Tips

### Looking for something specific?

**To add a new feature:**

1. Planning logic → `l1/`
2. Tool execution → `l2/`
3. Workflow coordination → `orchestration/`
4. Data storage → `state/`
5. Safety rules → `l5/`

**To debug an issue:**

1. Strategy problems → `l1/`
2. Tool failures → `l2/`
3. Workflow issues → `orchestration/`
4. Data problems → `state/`
5. Safety violations → `l5/`

**To understand data flow:**

```text
Input → L1 (Plan) → L3 (Orchestrate) → L2 (Execute) → L4 (Store) → L5 (Validate)
```

## 🔄 Recent Changes (Neo4j Integration)

The Neo4j integration added these key files:

- `graph_store_neo4j.py` - Neo4j database layer (L4)
- `graph_query.py` - Simple Cypher query interface
- `l2/factual_qa.py` - Neo4j-backed factual QA
- `l2/kg_writer.py` - Neo4j mirroring for ingestion

These follow the same layering principles:

- Neo4j storage = L4 (State layer)
- Neo4j queries = L2 (Execution layer)
- Neo4j mirroring = L2 (Execution layer)

## 💡 Mental Model

Think of this as a **smart company**:

- **L1** = Executives planning strategy
- **L2** = Workers using tools
- **L3** = Project managers coordinating work
- **L4** = Data warehouse storing everything
- **L5** = Legal/compliance ensuring safety

The **capability folders** (`agents/`, `orchestration/`, etc.) are like **departments** that contain people from different levels working together on specific capabilities.

This structure ensures:

- **Clear separation of concerns**
- **Testable components**
- **Reusable capabilities**
- **Scalable architecture**
