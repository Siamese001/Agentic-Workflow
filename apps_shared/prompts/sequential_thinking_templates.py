"""
Sequential Thinking Prompt Templates for SWE 1.5

This module contains specialized prompt templates designed to trigger
and guide sequential thinking for various software engineering tasks.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

class SequentialThinkingTemplate(Enum):
    """Sequential thinking template types."""

    SWE_ANALYSIS = "swe_analysis"
    SWE_DEBUGGING = "swe_debugging"
    SWE_IMPLEMENTATION = "swe_implementation"
    SWE_ARCHITECTURE = "swe_architecture"
    SWE_REFACTORING = "swe_refactoring"
    SWE_TESTING = "swe_testing"
    SWE_PLANNING = "swe_planning"
    SWE_INTEGRATION = "swe_integration"

@dataclass
class SequentialThinkingPrompt:
    """Sequential thinking prompt template."""

    template_id: str
    name: str
    template_type: SequentialThinkingTemplate
    content: str
    version: str
    description: str
    tags: List[str]
    variables: List[str]
    complexity_threshold: str = "medium"
    estimated_tokens: int = 5000

# Sequential Thinking Templates Library

SEQUENTIAL_THINKING_TEMPLATES = {
    SequentialThinkingTemplate.SWE_ANALYSIS: SequentialThinkingPrompt(
        template_id="swe_analysis_seq_v1",
        name="SWE Analysis Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_ANALYSIS,
        content="""# Sequential Analysis: {problem_title}

## Context
{context}

## Core Question
{core_question}

## Sequential Analysis Requirements

Please provide a structured sequential thinking analysis that breaks this problem down as follows:

### Thought 1: Problem Understanding & Scoping
- What is the core issue or requirement?
- What are the key constraints and boundaries?
- What information is missing or unclear?
- Define the scope and identify what's out of scope

### Thought 2: Current State Assessment
- What exists currently in the codebase?
- What are the strengths and weaknesses?
- What patterns or anti-patterns do you observe?
- Document pain points and bottlenecks

### Thought 3: Systematic Decomposition
- Break the problem into smaller, manageable components
- Identify dependencies between components
- Prioritize components by importance or risk
- Map out the relationships and interactions

### Thought 4: Analysis Strategy & Approach
- What analysis approach will be most effective?
- What tools or techniques should be used?
- How will you validate your analysis?
- What metrics or indicators will you track?

### Thought 5: Risk Assessment & Mitigation
- What could go wrong with this analysis?
- What are the common pitfalls in this type of problem?
- How will you mitigate these risks?
- What assumptions are you making?

### Thought 6: Findings & Recommendations
- What are your key findings?
- What specific actions should be taken?
- What are the next steps and dependencies?
- How will you measure success?

## Expected Output Format
For each thought, provide:
- Clear analysis and reasoning
- Specific recommendations with rationale
- Next steps and dependencies
- Confidence level and key assumptions

Please analyze this systematically using the sequential thinking approach.""",
        version="1.0.0",
        description="Sequential thinking template for software engineering analysis tasks",
        tags=["swe", "analysis", "sequential", "thinking", "systematic"],
        variables=["problem_title", "context", "core_question"],
        complexity_threshold="medium",
        estimated_tokens=6000
    ),

    SequentialThinkingTemplate.SWE_DEBUGGING: SequentialThinkingPrompt(
        template_id="swe_debugging_seq_v1",
        name="SWE Debugging Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_DEBUGGING,
        content="""# Sequential Debugging: {problem_title}

## Context
{context}

## Error Information
{error_details}

## Sequential Debugging Requirements

Please provide a structured sequential thinking analysis for debugging:

### Thought 1: Problem Definition & Symptom Analysis
- What exactly is the symptom or error?
- When and where does it occur?
- What are the reproduction steps?
- What is the frequency and consistency?

### Thought 2: Information Gathering & Evidence Collection
- What logs, traces, or error messages are available?
- What recent changes might be related?
- What environmental factors could be relevant?
- What data points can help isolate the issue?

### Thought 3: Hypothesis Formation & Prioritization
- What are the most likely root causes?
- How can you prioritize hypotheses by probability?
- What evidence supports each hypothesis?
- How can you quickly test each hypothesis?

### Thought 4: Systematic Investigation & Isolation
- How will you test each hypothesis methodically?
- What debugging tools or techniques will you use?
- How will you isolate variables and eliminate possibilities?
- What experiments can you run?

### Thought 5: Solution Development & Implementation
- What is the most likely fix based on evidence?
- How will you implement the solution safely?
- What testing is needed to validate the fix?
- How will you verify the root cause is addressed?

### Thought 6: Prevention & Learning
- How can similar issues be prevented in the future?
- What monitoring or alerts should be added?
- What documentation should be updated?
- What process improvements are needed?

## Expected Output Format
For each thought, provide:
- Specific debugging steps and rationale
- Evidence-based conclusions
- Clear action items with priorities
- Prevention strategies

Please debug this systematically using sequential thinking.""",
        version="1.0.0",
        description="Sequential thinking template for systematic debugging",
        tags=["swe", "debugging", "sequential", "thinking", "systematic"],
        variables=["problem_title", "context", "error_details"],
        complexity_threshold="medium",
        estimated_tokens=5500
    ),

    SequentialThinkingTemplate.SWE_IMPLEMENTATION: SequentialThinkingPrompt(
        template_id="swe_implementation_seq_v1",
        name="SWE Implementation Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_IMPLEMENTATION,
        content="""# Sequential Implementation Planning: {feature_title}

## Context
{context}

## Requirements
{requirements}

## Sequential Implementation Requirements

Please provide a structured sequential thinking analysis for implementation:

### Thought 1: Requirements Analysis & Clarification
- What exactly needs to be implemented?
- What are the functional and non-functional requirements?
- What are the acceptance criteria and success metrics?
- What ambiguities need clarification?

### Thought 2: Design Approach & Architecture
- What architectural pattern should be used?
- How should the code be structured and organized?
- What design principles and patterns apply?
- How will this integrate with existing architecture?

### Thought 3: Implementation Strategy & Sequencing
- What is the optimal sequence of implementation?
- What components should be built first?
- How will dependencies be managed?
- What are the key milestones?

### Thought 4: Risk Assessment & Mitigation
- What implementation risks exist?
- How will you handle edge cases and errors?
- What testing strategy is needed?
- How will you ensure backward compatibility?

### Thought 5: Integration & Deployment Planning
- How will this integrate with existing systems?
- What APIs or interfaces are needed?
- How will deployment be managed?
- What rollback strategies are in place?

### Thought 6: Validation & Quality Assurance
- How will you verify the implementation?
- What test cases are needed?
- How will you measure success and quality?
- What documentation is required?

## Expected Output Format
For each thought, provide:
- Detailed implementation plan
- Risk mitigation strategies
- Testing and validation approach
- Integration and deployment steps

Please plan this implementation systematically using sequential thinking.""",
        version="1.0.0",
        description="Sequential thinking template for implementation planning",
        tags=["swe", "implementation", "sequential", "thinking", "planning"],
        variables=["feature_title", "context", "requirements"],
        complexity_threshold="high",
        estimated_tokens=6500
    ),

    SequentialThinkingTemplate.SWE_ARCHITECTURE: SequentialThinkingPrompt(
        template_id="swe_architecture_seq_v1",
        name="SWE Architecture Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_ARCHITECTURE,
        content="""# Sequential Architecture Analysis: {system_title}

## Context
{context}

## Architecture Challenge
{architecture_challenge}

## Sequential Architecture Analysis Requirements

Please provide a structured sequential thinking analysis for architecture:

### Thought 1: System Understanding & Boundaries
- What is the system scope and boundaries?
- What are the key architectural drivers?
- What constraints and requirements shape the architecture?
- What are the quality attributes and non-functional requirements?

### Thought 2: Current Architecture Assessment
- What is the current architecture state?
- What are the strengths and weaknesses?
- What technical debt exists?
- What patterns and anti-patterns are present?

### Thought 3: Architectural Decision Analysis
- What key architectural decisions need to be made?
- What are the trade-offs for each decision?
- How do decisions align with business goals?
- What are the long-term implications?

### Thought 4: Design Pattern Selection
- What architectural patterns are most suitable?
- How will patterns be composed and combined?
- What are the integration points between patterns?
- How will patterns support scalability and maintainability?

### Thought 5: Risk Assessment & Evolution
- What architectural risks exist?
- How will the architecture evolve over time?
- What are the migration strategies?
- How will architectural governance be maintained?

### Thought 6: Implementation & Governance Strategy
- How will architectural decisions be implemented?
- What governance processes are needed?
- How will compliance be ensured?
- What metrics will track architectural health?

## Expected Output Format
For each thought, provide:
- Architectural analysis with rationale
- Decision frameworks and trade-offs
- Implementation roadmaps
- Governance strategies

Please analyze this architecture systematically using sequential thinking.""",
        version="1.0.0",
        description="Sequential thinking template for architecture analysis",
        tags=["swe", "architecture", "sequential", "thinking", "design"],
        variables=["system_title", "context", "architecture_challenge"],
        complexity_threshold="high",
        estimated_tokens=7000
    ),

    SequentialThinkingTemplate.SWE_REFACTORING: SequentialThinkingPrompt(
        template_id="swe_refactoring_seq_v1",
        name="SWE Refactoring Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_REFACTORING,
        content="""# Sequential Refactoring Analysis: {refactoring_title}

## Context
{context}

## Refactoring Goals
{refactoring_goals}

## Sequential Refactoring Requirements

Please provide a structured sequential thinking analysis for refactoring:

### Thought 1: Code Analysis & Problem Identification
- What are the specific code quality issues?
- What patterns or smells need addressing?
- What are the root causes of technical debt?
- What are the business impacts of current state?

### Thought 2: Refactoring Strategy & Prioritization
- What refactoring techniques are most appropriate?
- How should refactoring be prioritized?
- What are the riskiest areas to refactor?
- What is the optimal sequence of changes?

### Thought 3: Safety Measures & Risk Mitigation
- How will you ensure refactoring safety?
- What tests are needed before and after?
- What rollback strategies are in place?
- How will you maintain functionality during refactoring?

### Thought 4: Implementation Planning
- What are the specific refactoring steps?
- How will changes be validated?
- What are the intermediate states?
- How will you coordinate with team members?

### Thought 5: Integration & Testing Strategy
- How will refactored code be integrated?
- What testing approach ensures correctness?
- How will performance be validated?
- What are the acceptance criteria?

### Thought 6: Long-term Maintenance & Prevention
- How will similar issues be prevented?
- What coding standards need updating?
- What automated checks should be added?
- How will code quality be maintained?

## Expected Output Format
For each thought, provide:
- Specific refactoring steps with rationale
- Risk mitigation strategies
- Testing and validation plans
- Long-term maintenance approaches

Please plan this refactoring systematically using sequential thinking.""",
        version="1.0.0",
        description="Sequential thinking template for refactoring planning",
        tags=["swe", "refactoring", "sequential", "thinking", "quality"],
        variables=["refactoring_title", "context", "refactoring_goals"],
        complexity_threshold="medium",
        estimated_tokens=6000
    ),

    SequentialThinkingTemplate.SWE_TESTING: SequentialThinkingPrompt(
        template_id="swe_testing_seq_v1",
        name="SWE Testing Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_TESTING,
        content="""# Sequential Testing Strategy: {testing_title}

## Context
{context}

## Testing Requirements
{testing_requirements}

## Sequential Testing Requirements

Please provide a structured sequential thinking analysis for testing:

### Thought 1: Testing Scope & Requirements Analysis
- What needs to be tested and why?
- What are the critical paths and edge cases?
- What are the testing priorities based on risk?
- What are the success criteria and metrics?

### Thought 2: Test Strategy & Approach
- What testing levels are needed (unit, integration, system)?
- What testing methodologies are most appropriate?
- How will test coverage be measured and ensured?
- What automation strategies will be used?

### Thought 3: Test Design & Case Planning
- What test cases need to be designed?
- How will test data be managed?
- What are the test environment requirements?
- How will tests be organized and structured?

### Thought 4: Risk Assessment & Coverage Analysis
- What are the highest risk areas?
- How will coverage gaps be identified?
- What are the testing constraints and limitations?
- How will testing risks be mitigated?

### Thought 5: Implementation & Execution Planning
- What is the test implementation sequence?
- How will tests be integrated into CI/CD?
- What are the resource and timeline requirements?
- How will test execution be coordinated?

### Thought 6: Quality Assurance & Continuous Improvement
- How will test quality be ensured?
- What metrics will track testing effectiveness?
- How will the testing process improve over time?
- What are the feedback mechanisms?

## Expected Output Format
For each thought, provide:
- Comprehensive testing strategy
- Specific test design recommendations
- Risk-based testing priorities
- Quality assurance measures

Please design this testing strategy systematically using sequential thinking.""",
        version="1.0.0",
        description="Sequential thinking template for testing strategy",
        tags=["swe", "testing", "sequential", "thinking", "quality"],
        variables=["testing_title", "context", "testing_requirements"],
        complexity_threshold="medium",
        estimated_tokens=5500
    ),

    SequentialThinkingTemplate.SWE_PLANNING: SequentialThinkingPrompt(
        template_id="swe_planning_seq_v1",
        name="SWE Planning Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_PLANNING,
        content="""# Sequential Planning Analysis: {planning_title}

## Context
{context}

## Planning Objectives
{planning_objectives}

## Sequential Planning Requirements

Please provide a structured sequential thinking analysis for planning:

### Thought 1: Goal Definition & Success Criteria
- What are the specific objectives and outcomes?
- How will success be measured?
- What are the key deliverables?
- What are the constraints and dependencies?

### Thought 2: Current State & Gap Analysis
- What is the current state assessment?
- What gaps need to be addressed?
- What resources and capabilities are available?
- What are the strengths and weaknesses?

### Thought 3: Strategy Development & Option Analysis
- What are the possible approaches and strategies?
- How should options be evaluated and compared?
- What are the trade-offs and implications?
- What is the recommended approach and why?

### Thought 4: Implementation Planning & Sequencing
- What is the optimal implementation sequence?
- What are the key milestones and checkpoints?
- How will dependencies be managed?
- What are the critical path items?

### Thought 5: Risk Management & Contingency Planning
- What are the primary risks and uncertainties?
- How will risks be mitigated and managed?
- What contingency plans are needed?
- How will progress be monitored and adjusted?

### Thought 6: Resource Planning & Execution Strategy
- What resources are needed and when?
- How will execution be coordinated and managed?
- What communication and reporting mechanisms are needed?
- How will stakeholders be engaged and informed?

## Expected Output Format
For each thought, provide:
- Strategic analysis with clear rationale
- Implementation roadmap with milestones
- Risk mitigation strategies
- Resource allocation plans

Please develop this plan systematically using sequential thinking.""",
        version="1.0.0",
        description="Sequential thinking template for strategic planning",
        tags=["swe", "planning", "sequential", "thinking", "strategy"],
        variables=["planning_title", "context", "planning_objectives"],
        complexity_threshold="high",
        estimated_tokens=6500
    ),

    SequentialThinkingTemplate.SWE_INTEGRATION: SequentialThinkingPrompt(
        template_id="swe_integration_seq_v1",
        name="SWE Integration Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_INTEGRATION,
        content="""# Sequential Integration Analysis: {integration_title}

## Context
{context}

## Integration Requirements
{integration_requirements}

## Sequential Integration Requirements

Please provide a structured sequential thinking analysis for integration:

### Thought 1: Integration Scope & Interface Analysis
- What systems or components need integration?
- What are the interface requirements and contracts?
- What are the data flow and communication patterns?
- What are the integration boundaries and responsibilities?

### Thought 2: Technical Architecture & Design
- What integration patterns and approaches are suitable?
- How will systems communicate and exchange data?
- What are the security and performance considerations?
- How will scalability and reliability be ensured?

### Thought 3: Implementation Strategy & Phasing
- What is the optimal integration sequence?
- How will integration be phased and rolled out?
- What are the dependencies and prerequisites?
- How will parallel development be coordinated?

### Thought 4: Testing & Validation Strategy
- How will integration be tested and validated?
- What are the test scenarios and edge cases?
- How will performance and load testing be conducted?
- What are the acceptance criteria?

### Thought 5: Risk Assessment & Mitigation
- What are the integration risks and failure modes?
- How will system failures be handled?
- What are the rollback and recovery strategies?
- How will data consistency be ensured?

### Thought 6: Deployment & Operations Planning
- How will integration be deployed and configured?
- What monitoring and observability is needed?
- How will operational issues be handled?
- What are the maintenance and support requirements?

## Expected Output Format
For each thought, provide:
- Technical integration design
- Implementation roadmap
- Risk mitigation strategies
- Operations and maintenance plans

Please design this integration systematically using sequential thinking.""",
        version="1.0.0",
        description="Sequential thinking template for system integration",
        tags=["swe", "integration", "sequential", "thinking", "architecture"],
        variables=["integration_title", "context", "integration_requirements"],
        complexity_threshold="high",
        estimated_tokens=7000
    )
}

def get_template(template_type: SequentialThinkingTemplate) -> SequentialThinkingPrompt:
    """Get a sequential thinking template by type."""
    return SEQUENTIAL_THINKING_TEMPLATES.get(template_type)

def get_all_templates() -> Dict[SequentialThinkingTemplate, SequentialThinkingPrompt]:
    """Get all sequential thinking templates."""
    return SEQUENTIAL_THINKING_TEMPLATES

def render_template(template_type: SequentialThinkingTemplate, **kwargs) -> str:
    """Render a sequential thinking template with provided variables."""
    template = get_template(template_type)
    if not template:
        raise ValueError(f"Template not found: {template_type}")

    content = template.content

    # Replace template variables
    for var in template.variables:
        if var in kwargs:
            placeholder = f"{{{var}}}"
            content = content.replace(placeholder, str(kwargs[var]))

    return content

def get_template_for_complexity(complexity: str) -> List[SequentialThinkingTemplate]:
    """Get suitable templates for a given complexity level."""
    complexity_map = {
        "low": [SequentialThinkingTemplate.SWE_ANALYSIS, SequentialThinkingTemplate.SWE_TESTING],
        "medium": [SequentialThinkingTemplate.SWE_ANALYSIS, SequentialThinkingTemplate.SWE_DEBUGGING,
                  SequentialThinkingTemplate.SWE_REFACTORING, SequentialThinkingTemplate.SWE_TESTING,
                  SequentialThinkingTemplate.SWE_PLANNING],
        "high": [SequentialThinkingTemplate.SWE_ARCHITECTURE, SequentialThinkingTemplate.SWE_IMPLEMENTATION,
                 SequentialThinkingTemplate.SWE_INTEGRATION, SequentialThinkingTemplate.SWE_PLANNING],
        "critical": list(SequentialThinkingTemplate)  # All templates for critical complexity
    }

    return complexity_map.get(complexity.lower(), [])

# Example usage
def example_usage():
    """Example of how to use sequential thinking templates."""

    # Get template for analysis
    analysis_template = get_template(SequentialThinkingTemplate.SWE_ANALYSIS)

    # Render with variables
    rendered = render_template(
        SequentialThinkingTemplate.SWE_ANALYSIS,
        problem_title="Database Performance Issue",
        context="User reports slow query performance",
        core_question="How can we optimize database performance?"
    )

    print("Template rendered successfully")
    print(f"Estimated tokens: {analysis_template.estimated_tokens}")
    print(f"Complexity threshold: {analysis_template.complexity_threshold}")

if __name__ == "__main__":
    example_usage()
