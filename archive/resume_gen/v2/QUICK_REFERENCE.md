# V2 Architecture Quick Reference

## File Structure
```
resume_gen_files/
├── workflow_RES_v2.py      # Main orchestrator (180K)
├── run_workflow_RES_v2.py  # Launcher (11K)
├── governor.py             # V2 agents (34K)
├── config_RES.py           # Config + GovernorConfig (20K)
├── models_RES.py           # Data models (15K)
├── utils_RES.py            # Utilities (33K)
├── rag_RES.py              # RAG + LibrarianAgent (46K)
├── prompts_RES.py          # Prompt templates (30K)
├── validation_RES.py       # Validators (132K)
├── state_manager_RES.py    # State persistence (14K)
└── *.json                  # Data files (8 files)
```

## Run Commands
```bash
# New run
python run_workflow_RES_v2.py --job-input job_input.json

# Resume run
python run_workflow_RES_v2.py --resume-id <run_id>

# List runs
python run_workflow_RES_v2.py --list-runs
```

## Import Pattern
```python
# Main orchestrator
from workflow_RES_v2 import WorkflowOrchestrator

# Governor components
from governor import PolicyAgent, CostRouter, ContextRelayLayer

# Configuration
from config_RES import CONFIG

# Supporting modules
from models_RES import ResumeSection, ValidationResult
from utils_RES import TextUtils, CodeInterpreterTool
from rag_RES import EnhancedJobDescriptionAnalyzer
from validation_RES import PreFlightValidator
```

## Version Info
- All modules: v17.00
- Architecture: V2 Agentic with Async Governor
- Python: 3.8+
- Status: Production Ready ✅
