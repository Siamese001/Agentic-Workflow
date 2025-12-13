"""
Workflow Integration - Demonstrates the four enhancements in action.

Shows how to:
1. Load and apply schema validation
2. Build prompts with negative constraints
3. Track cognitive telemetry
4. Route to optimal models dynamically
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .node_executor import (
    NodeExecutor,
    NodeExecutionContext,
    create_node_executor
)
from .schemas import get_schema_registry

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """
    High-level orchestrator that manages workflow execution with all enhancements.
    
    This class demonstrates how the four enhancements work together:
    - Schema validation ensures output consistency
    - Negative constraints prevent unwanted behaviors
    - Telemetry provides observability
    - Model routing optimizes cost and performance
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the orchestrator.
        
        Args:
            config_path: Optional path to workflow configuration
        """
        # Load schema registry
        self.schema_registry = get_schema_registry()
        
        # Load telemetry configuration
        self.telemetry_config = {
            "provider": "langsmith",
            "trace_depth": "full",
            "metrics_to_track": [
                "latency_ms",
                "token_usage_input",
                "token_usage_output",
                "cost_usd",
                "retrieval_doc_count"
            ],
            "span_tagging_rules": {
                "k_node": "extracted from node_id",
                "model_version": "extracted from infrastructure_config",
                "session_id": "runtime_context.session_uuid"
            }
        }
        
        # Create node executor
        self.executor = create_node_executor(
            schema_registry=self.schema_registry,
            telemetry_config=self.telemetry_config
        )
        
        # Session tracking
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Execution statistics
        self.stats = {
            "nodes_executed": 0,
            "total_cost_usd": 0.0,
            "total_latency_ms": 0.0,
            "schema_violations": 0,
            "constraint_violations": 0,
            "model_usage": {}
        }
        
        self.logger = logging.getLogger("WorkflowOrchestrator")
    
    async def execute_workflow(self, workflow_config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete workflow with all enhancements.
        
        Args:
            workflow_config: Workflow configuration with node definitions
            input_data: Input data for the workflow
            
        Returns:
            Workflow results with all node outputs
        """
        self.logger.info(f"Starting workflow execution for session {self.session_id}")
        
        results = {}
        
        # Execute each node in order
        for node_id, node_config in workflow_config.get("nodes", {}).items():
            try:
                # Create execution context
                context = NodeExecutionContext(
                    node_id=node_id,
                    node_config=node_config,
                    input_data=input_data,
                    session_id=self.session_id
                )
                
                # Execute node with all enhancements
                context = await self.executor.execute_node(context)
                
                # Store results
                if context.validated_output:
                    results[node_id] = context.validated_output.model_dump()
                else:
                    results[node_id] = {"error": "Validation failed", "raw": context.raw_output}
                
                # Update statistics
                self._update_stats(context)
                
            except Exception as e:
                self.logger.error(f"Node {node_id} failed: {e}")
                results[node_id] = {"error": str(e)}
        
        # Log workflow summary
        self._log_workflow_summary()
        
        return {
            "session_id": self.session_id,
            "results": results,
            "statistics": self.stats
        }
    
    def _update_stats(self, context: NodeExecutionContext):
        """Update execution statistics.
        
        Args:
            context: Node execution context
        """
        self.stats["nodes_executed"] += 1
        self.stats["total_cost_usd"] += context.actual_cost_usd
        self.stats["total_latency_ms"] += context.execution_time_ms
        
        # Track model usage
        if context.selected_model:
            if context.selected_model not in self.stats["model_usage"]:
                self.stats["model_usage"][context.selected_model] = 0
            self.stats["model_usage"][context.selected_model] += 1
        
        # Track violations
        if context.errors:
            for error in context.errors:
                if "validation" in error.lower():
                    self.stats["schema_violations"] += 1
                if "constraint" in error.lower():
                    self.stats["constraint_violations"] += 1
    
    def _log_workflow_summary(self):
        """Log workflow execution summary."""
        self.logger.info("=== Workflow Execution Summary ===")
        self.logger.info(f"Session: {self.session_id}")
        self.logger.info(f"Nodes Executed: {self.stats['nodes_executed']}")
        self.logger.info(f"Total Cost: ${self.stats['total_cost_usd']:.4f}")
        self.logger.info(f"Avg Latency: {self.stats['total_latency_ms'] / max(1, self.stats['nodes_executed']):.0f}ms")
        self.logger.info(f"Schema Violations: {self.stats['schema_violations']}")
        self.logger.info(f"Model Usage: {self.stats['model_usage']}")


def create_sample_workflow_config() -> Dict[str, Any]:
    """Create a sample workflow configuration demonstrating all enhancements.
    
    Returns:
        Sample workflow configuration
    """
    return {
        "workflow_name": "Resume Generation",
        "version": "24.9",
        "nodes": {
            "K.1_company_job_title_extraction": {
                "system_prompt": "Extract the company name and job title from the job posting.",
                "schema_enforcement": {
                    "enabled": True,
                    "pydantic_model": "K1CompanyJobTitle",
                    "strict_mode": True,
                    "validation_retries": 3
                },
                "infrastructure_config": {
                    "compute_tier": "TIER_3_SPEED",
                    "primary_model": "gpt-4o-mini",
                    "fallback_model": "claude-3-haiku-20240307",
                    "temperature_override": 0.1,
                    "timeout_ms": 15000
                }
            },
            "K.5_executive_summary": {
                "system_prompt": "Generate a compelling executive summary for the resume.",
                "negative_constraints": {
                    "syntax_forbidden": [
                        "Do not use markdown headers (#) within the summary text",
                        "Do not use bullet points or lists",
                        "Do not use XML tags in the final output string"
                    ],
                    "style_forbidden": [
                        "Do not use the word 'spearheaded' (replace with 'led' or 'orchestrated')",
                        "Do not use 'I' or 'My' (enforce third-person implied)",
                        "Do not mention salary expectations or availability"
                    ],
                    "hallucination_guard": [
                        "Do not invent metrics (e.g., '20% growth') if not explicitly in the input context"
                    ]
                },
                "schema_enforcement": {
                    "enabled": True,
                    "pydantic_model": "K5ExecutiveSummary",
                    "strict_mode": True,
                    "validation_retries": 3
                },
                "infrastructure_config": {
                    "compute_tier": "TIER_1_REASONING",
                    "primary_model": "claude-3-5-sonnet-20241022",
                    "fallback_model": "gpt-4o",
                    "temperature_override": 0.7,
                    "timeout_ms": 60000
                }
            },
            "K.6_most_recent_experience": {
                "system_prompt": "Generate 7 achievement bullets for the most recent work experience.",
                "schema_enforcement": {
                    "enabled": True,
                    "pydantic_model": "K6MostRecentExperience",
                    "strict_mode": True,
                    "validation_retries": 3
                },
                "negative_constraints": {
                    "style_forbidden": [
                        "Do not use passive voice (e.g., 'was responsible for')",
                        "Do not start bullets with 'Responsible for' or 'Handled'",
                        "Do not use vague phrases like 'various tasks' or 'etc.'"
                    ],
                    "content_forbidden": [
                        "Do not include personal opinions or feelings",
                        "Do not mention confidential company information"
                    ]
                },
                "infrastructure_config": {
                    "compute_tier": "TIER_2_BALANCED",
                    "primary_model": "gpt-4o",
                    "fallback_model": "claude-3-5-sonnet-20241022",
                    "temperature_override": 0.5,
                    "timeout_ms": 30000
                }
            }
        },
        "telemetry_config": {
            "provider": "langsmith",
            "trace_depth": "full",
            "metrics_to_track": [
                "latency_ms",
                "token_usage_input",
                "token_usage_output",
                "cost_usd",
                "retrieval_doc_count"
            ],
            "span_tagging_rules": {
                "k_node": "extracted from node_id",
                "model_version": "extracted from infrastructure_config",
                "session_id": "runtime_context.session_uuid"
            }
        }
    }


def create_sample_input_data() -> Dict[str, Any]:
    """Create sample input data for workflow execution.
    
    Returns:
        Sample input data
    """
    return {
        "job_posting": """
        Senior Software Engineer at TechCorp Inc.
        
        Location: San Francisco, CA
        
        Requirements:
        - 5+ years of experience in software development
        - Strong proficiency in Python and JavaScript
        - Experience with cloud platforms (AWS, Azure, or GCP)
        - Bachelor's degree in Computer Science or related field
        
        Responsibilities:
        - Design and develop scalable software solutions
        - Lead a team of 3-5 junior developers
        - Collaborate with product managers to define requirements
        - Optimize application performance and reliability
        
        We offer competitive compensation and excellent benefits.
        """,
        "user_profile": {
            "experience_years": 7,
            "current_role": "Software Engineer",
            "previous_companies": ["StartupXYZ", "Tech Solutions Inc."]
        }
    }


# Example usage
async def main():
    """Demonstrate the four enhancements in action."""
    
    # Create orchestrator
    orchestrator = WorkflowOrchestrator()
    
    # Load workflow configuration
    workflow_config = create_sample_workflow_config()
    input_data = create_sample_input_data()
    
    print("=== Workflow Execution with Four Enhancements ===\n")
    
    # Execute workflow
    results = await orchestrator.execute_workflow(workflow_config, input_data)
    
    # Display results
    print(f"Session ID: {results['session_id']}")
    print(f"Total Nodes: {results['statistics']['nodes_executed']}")
    print(f"Total Cost: ${results['statistics']['total_cost_usd']:.4f}\n")
    
    # Show individual node results
    for node_id, result in results['results'].items():
        print(f"=== {node_id} ===")
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            # Display based on node type
            if "company_name" in result:
                print(f"Company: {result['company_name']}")
                print(f"Title: {result['job_title']}")
            elif "summary_text" in result:
                print(f"Summary: {result['summary_text'][:100]}...")
            elif "bullets" in result:
                print(f"Bullets: {len(result['bullets'])} generated")
                for i, bullet in enumerate(result['bullets'][:3], 1):
                    print(f"  {i}. {bullet}")
        
        print()
    
    # Show model usage
    print("=== Model Usage ===")
    for model, count in results['statistics']['model_usage'].items():
        print(f"{model}: {count} calls")
    
    print("\n=== Enhancement Summary ===")
    print("1. ✅ Schema Enforcement: All outputs validated against Pydantic models")
    print("2. ✅ Negative Constraints: Governance barriers applied to prompts")
    print("3. ✅ Cognitive Telemetry: Execution metrics tracked and tagged")
    print("4. ✅ Dynamic Routing: Models selected based on compute tier")


if __name__ == "__main__":
    asyncio.run(main())
