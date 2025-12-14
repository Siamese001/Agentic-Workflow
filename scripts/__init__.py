import logging
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
'\n\n\nLOGGER = logging.getLogger(__name__)\nAgentic-Workflow Root Package\n=============================\n\nThis is the root package for the Agentic Workflow system, providing a unified\narchitecture for agentic AI operations with the following taxonomy:\n\n    01_agentic_core/    - Core agent implementations (L1-L5 layers)\n    02_schemas/         - Schema definitions and validation\n    03_runtime/         - Runtime services and shared utilities\n    04_prompt_governance/ - Prompt templates and governance\n    05_config/          - Configuration files (YAML/JSON only)\n    06_data/            - Data storage, archives, and semantic cache\n    07_observability/   - Logging, metrics, and tracing\n    08_scripts/         - function scripts and tools\n    09_apps/            - Application implementations (LIC, RG)\n    10_tests/           - Test suites\n\nAuto-hardened by WINDSURF v7 — Production-ready, type-safe, zero-loss.\n'
__version__ = '7.0.0'
__author__ = 'Agentic Workflow Team'
__all__ = ['__version__', '__author__']
