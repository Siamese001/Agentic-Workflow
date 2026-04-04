"""
Sequential Thinking Prompt Templates for SWE 1.5

This module contains specialized prompt templates designed to trigger
and guide sequential thinking for various software engineering tasks.
"""

from dataclasses import dataclass
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

    # ADG-based templates
    SWE_ADG_ANALYSIS = "swe_adg_analysis"
    SWE_VIOLATION_REMEDIATION = "swe_violation_remediation"
    SWE_LAYER_BOUNDARY_AUDIT = "swe_layer_boundary_audit"
    SWE_DEPENDENCY_GRAPH_ANALYSIS = "swe_dependency_graph_analysis"
    SWE_ARCHITECTURAL_REVIEW = "swe_architectural_review"
    SWE_ANTIPATTERN_DETECTION = "swe_antipattern_detection"
    SWE_SYSTEM_RESTRUCTURING = "swe_system_restructuring"
    SWE_GRAPH_TRAVERSAL_OPTIMIZATION = "swe_graph_traversal_optimization"

@dataclass
class SequentialThinkingPrompt:
    """Sequential thinking prompt template."""

    template_id: str
    name: str
    template_type: SequentialThinkingTemplate
    content: str
    version: str
    description: str
    tags: list[str]
    variables: list[str]
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
    ),

    # ADG-based Templates
    SequentialThinkingTemplate.SWE_ADG_ANALYSIS: SequentialThinkingPrompt(
        template_id="swe_adg_analysis_seq_v1",
        name="ADG Graph Analysis Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_ADG_ANALYSIS,
        content="""# Sequential ADG Analysis: {analysis_title}

## Context
{context}

## ADG Graph Statistics
- Total Nodes: {node_count}
- Total Edges: {edge_count}
- Layers: {layer_info}
- Violations: {violation_count}

## Sequential ADG Analysis Requirements

Please provide a structured sequential thinking analysis of the ADG graph:

### Thought 1: Graph Structure & Topology Analysis
- What is the overall graph topology and density?
- How are nodes distributed across layers (L0-L6)?
- What are the key connectivity patterns?
- Identify graph clusters and communities

### Thought 2: Layer Boundary & Gravity Analysis
- How well do layer boundaries respect gravity rules?
- What violations exist in layer transitions?
- Which layers have the most cross-layer dependencies?
- Analyze upward vs downward dependency patterns

### Thought 3: Dependency Flow & Impact Analysis
- What are the critical dependency paths?
- Which nodes have the highest betweenness centrality?
- Identify potential single points of failure
- Map information flow through the system

### Thought 4: Violation Pattern & Anti-pattern Detection
- What types of violations are most prevalent?
- Are there systematic anti-patterns in the graph?
- Which files/modules have the most violations?
- Analyze violation severity and impact

### Thought 5: Architectural Insights & Recommendations
- What does the graph reveal about system architecture?
- Where are architectural hotspots and bottlenecks?
- What refactoring opportunities exist?
- Identify areas for architectural improvement

### Thought 6: Graph Health & Maintenance Strategy
- What is the overall health of the dependency graph?
- How can graph quality be maintained over time?
- What metrics should be tracked for graph health?
- Develop a strategy for ongoing graph optimization

## Expected Output Format
For each thought, provide:
- Graph analysis findings with specific metrics
- Visual insights about system structure
- Actionable recommendations based on graph properties
- Risk assessment based on dependency patterns

Please analyze this ADG graph systematically using sequential thinking.""",
        version="1.0.0",
        description="Sequential thinking template for ADG graph analysis",
        tags=["adg", "graph", "analysis", "architecture", "dependencies"],
        variables=["analysis_title", "context", "node_count", "edge_count", "layer_info", "violation_count"],
        complexity_threshold="high",
        estimated_tokens=7500
    ),

    SequentialThinkingTemplate.SWE_VIOLATION_REMEDIATION: SequentialThinkingPrompt(
        template_id="swe_violation_remediation_seq_v1",
        name="Violation Remediation Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_VIOLATION_REMEDIATION,
        content="""# Sequential Violation Remediation: {remediation_title}

## Context
{context}

## Violation Summary
- Total Violations: {violation_count}
- High Severity: {high_severity_count}
- Medium Severity: {medium_severity_count}
- Low Severity: {low_severity_count}
- Most Common Types: {common_violation_types}

## Sequential Violation Remediation Requirements

Please provide a structured sequential thinking approach to remediate violations:

### Thought 1: Violation Classification & Prioritization
- How should violations be classified by severity and impact?
- Which violations pose the highest architectural risk?
- What are the dependencies between violations?
- Prioritize violations based on system impact and fix complexity

### Thought 2: Root Cause Analysis & Pattern Detection
- What are the underlying causes of these violations?
- Are there systematic patterns in violation occurrences?
- Which files or modules are violation hotspots?
- Identify architectural or process issues causing violations

### Thought 3: Remediation Strategy & Approach
- What is the overall strategy for violation remediation?
- Should violations be fixed incrementally or in batches?
- What are the risks and mitigation strategies for fixes?
- How will fixes be validated and tested?

### Thought 4: Implementation Planning & Sequencing
- What is the optimal sequence for fixing violations?
- How will fixes be coordinated across teams?
- What are the dependencies between different fixes?
- Plan for rollback and recovery strategies

### Thought 5: Prevention & Process Improvement
- How can similar violations be prevented in the future?
- What process improvements are needed?
- How can automated detection be enhanced?
- Develop guidelines for violation-free development

### Thought 6: Monitoring & Quality Assurance
- How will violation-free status be maintained?
- What metrics should be tracked for ongoing quality?
- How will code reviews and checks be enhanced?
- Plan for continuous quality improvement

## Expected Output Format
For each thought, provide:
- Specific remediation steps and priorities
- Risk assessment for each fix
- Implementation timeline and dependencies
- Prevention strategies and process improvements

Please remediate these violations systematically using sequential thinking.""",
        version="1.0.0",
        description="Sequential thinking template for violation remediation",
        tags=["violations", "remediation", "quality", "anti-patterns", "architecture"],
        variables=["remediation_title", "context", "violation_count", "high_severity_count", "medium_severity_count", "low_severity_count", "common_violation_types"],
        complexity_threshold="high",
        estimated_tokens=7000
    ),

    SequentialThinkingTemplate.SWE_LAYER_BOUNDARY_AUDIT: SequentialThinkingPrompt(
        template_id="swe_layer_boundary_audit_seq_v1",
        name="Layer Boundary Audit Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_LAYER_BOUNDARY_AUDIT,
        content="""# Sequential Layer Boundary Audit: {audit_title}

## Context
{context}

## Layer Architecture Overview
- Total Layers: {layer_count}
- Layer Distribution: {layer_distribution}
- Boundary Violations: {boundary_violations}
- Gravity Violations: {gravity_violations}

## Sequential Layer Boundary Audit Requirements

Please provide a structured sequential thinking analysis of layer boundaries:

### Thought 1: Layer Architecture & Design Review
- What is the intended layer architecture and purpose?
- How well are layer boundaries defined and documented?
- What are the intended dependency directions (gravity)?
- Assess the clarity and consistency of layer design

### Thought 2: Boundary Violation Analysis
- What specific violations exist in layer boundaries?
- Which violations break architectural principles?
- How do violations impact system maintainability?
- Categorize violations by type and severity

### Thought 3: Dependency Flow & Gravity Assessment
- How well do dependencies respect layer gravity?
- What are the problematic upward dependencies?
- Which layers have excessive cross-dependencies?
- Analyze the impact on system stability

### Thought 4: Architectural Impact & Risk Analysis
- What are the architectural risks from boundary violations?
- How do violations affect system modularity?
- What are the maintenance and evolution challenges?
- Assess impact on testing and deployment

### Thought 5: Remediation & Refactoring Strategy
- What is the strategy for fixing boundary violations?
- How can dependencies be restructured to respect boundaries?
- What refactoring patterns are most appropriate?
- Plan incremental improvement approach

### Thought 6: Governance & Prevention Strategy
- How can layer boundary compliance be enforced?
- What automated checks and validations are needed?
- How will architectural reviews be enhanced?
- Develop ongoing governance and monitoring strategy

## Expected Output Format
For each thought, provide:
- Specific boundary violation analysis
- Architectural risk assessment
- Remediation recommendations and priorities
- Governance and prevention strategies

Please audit these layer boundaries systematically using sequential thinking.""",
        version="1.0.0",
        description="Sequential thinking template for layer boundary audit",
        tags=["layers", "boundaries", "architecture", "governance", "violations"],
        variables=["audit_title", "context", "layer_count", "layer_distribution", "boundary_violations", "gravity_violations"],
        complexity_threshold="high",
        estimated_tokens=6500
    ),

    SequentialThinkingTemplate.SWE_DEPENDENCY_GRAPH_ANALYSIS: SequentialThinkingPrompt(
        template_id="swe_dependency_graph_analysis_seq_v1",
        name="Dependency Graph Analysis Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_DEPENDENCY_GRAPH_ANALYSIS,
        content="""# Sequential Dependency Graph Analysis: {analysis_title}

## Context
{context}

## Dependency Graph Metrics
- Total Dependencies: {dependency_count}
- Circular Dependencies: {circular_deps}
- Longest Dependency Chain: {longest_chain}
- Highly Connected Nodes: {hub_nodes}

## Sequential Dependency Graph Analysis Requirements

Please provide a structured sequential thinking analysis of dependencies:

### Thought 1: Graph Topology & Structure Analysis
- What is the overall structure of the dependency graph?
- How dense or sparse are the connections?
- What are the key graph clusters and components?
- Identify the backbone of the dependency structure

### Thought 2: Critical Dependencies & Bottlenecks
- Which dependencies are most critical to system operation?
- What are the potential single points of failure?
- How resilient is the system to dependency failures?
- Identify dependency bottlenecks and constraints

### Thought 3: Circular Dependency & Cycle Analysis
- What circular dependencies exist in the system?
- How do cycles impact system maintainability?
- What are the risks from circular dependencies?
- Develop strategies for cycle elimination

### Thought 4: Dependency Coupling & Cohesion Assessment
- How tightly coupled are system components?
- What are the cohesion levels within modules?
- Which dependencies indicate poor separation of concerns?
- Assess impact on modifiability and testability

### Thought 5: Evolution & Maintenance Analysis
- How will dependencies evolve over time?
- What are the risks of dependency accumulation?
- How can dependency growth be managed?
- Plan for sustainable dependency management

### Thought 6: Optimization & Refactoring Strategy
- What dependencies can be eliminated or simplified?
- How can dependency structure be improved?
- What refactoring patterns are most beneficial?
- Develop a dependency optimization roadmap

## Expected Output Format
For each thought, provide:
- Dependency analysis with specific metrics
- Risk assessment for dependency issues
- Refactoring recommendations and priorities
- Long-term dependency management strategy

Please analyze this dependency graph systematically using sequential thinking.""",
        version="1.0.0",
        description="Sequential thinking template for dependency graph analysis",
        tags=["dependencies", "graph", "coupling", "architecture", "refactoring"],
        variables=["analysis_title", "context", "dependency_count", "circular_deps", "longest_chain", "hub_nodes"],
        complexity_threshold="high",
        estimated_tokens=7000
    ),

    SequentialThinkingTemplate.SWE_ARCHITECTURAL_REVIEW: SequentialThinkingPrompt(
        template_id="swe_architectural_review_seq_v1",
        name="Architectural Review Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_ARCHITECTURAL_REVIEW,
        content="""# Sequential Architectural Review: {review_title}

## Context
{context}

## Architecture Overview
- System Components: {component_count}
- Architectural Patterns: {patterns_used}
- Integration Points: {integration_points}
- Quality Attributes: {quality_attributes}

## Sequential Architectural Review Requirements

Please provide a structured sequential thinking architectural review:

### Thought 1: Architectural Principles & Design Assessment
- How well does the architecture follow established principles?
- What are the strengths of the current design?
- Where are architectural principles violated?
- Assess overall architectural coherence and consistency

### Thought 2: Component Structure & Relationships Analysis
- How well are components structured and organized?
- What are the key component relationships and interactions?
- Which components have excessive responsibilities?
- Analyze component cohesion and coupling

### Thought 3: Quality Attributes & Non-Functional Requirements
- How well does the architecture address quality requirements?
- What are the performance, scalability, and reliability characteristics?
- How are security and maintainability addressed?
- Assess trade-offs between quality attributes

### Thought 4: Integration & Interface Design Review
- How well are system interfaces designed and implemented?
- What are the integration patterns and their effectiveness?
- How are external dependencies managed?
- Assess integration complexity and risks

### Thought 5: Evolution & Change Management Assessment
- How well can the architecture evolve and adapt?
- What are the change hotspots and areas of fragility?
- How is technical debt managed in the architecture?
- Assess long-term sustainability and maintainability

### Thought 6: Recommendations & Improvement Strategy
- What specific architectural improvements are needed?
- How should architectural decisions be prioritized?
- What is the roadmap for architectural evolution?
- Develop governance and decision-making processes

## Expected Output Format
For each thought, provide:
- Architectural assessment with specific findings
- Risk analysis and mitigation strategies
- Improvement recommendations with priorities
- Long-term architectural roadmap

Please conduct this architectural review systematically using sequential thinking.""",
        version="1.0.0",
        description="Sequential thinking template for architectural review",
        tags=["architecture", "review", "quality", "patterns", "design"],
        variables=["review_title", "context", "component_count", "patterns_used", "integration_points", "quality_attributes"],
        complexity_threshold="high",
        estimated_tokens=7500
    ),

    SequentialThinkingTemplate.SWE_ANTIPATTERN_DETECTION: SequentialThinkingPrompt(
        template_id="swe_antipattern_detection_seq_v1",
        name="Anti-pattern Detection Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_ANTIPATTERN_DETECTION,
        content="""# Sequential Anti-pattern Detection: {detection_title}

## Context
{context}

## Anti-pattern Summary
- Total Anti-patterns: {antipattern_count}
- High Impact: {high_impact_count}
- Common Categories: {common_categories}
- Affected Files: {affected_files}

## Sequential Anti-pattern Detection Requirements

Please provide a structured sequential thinking analysis of anti-patterns:

### Thought 1: Anti-pattern Classification & Categorization
- What types of anti-patterns are present in the codebase?
- How should anti-patterns be classified by severity and impact?
- Which anti-patterns are most prevalent?
- Identify patterns of anti-pattern occurrence

### Thought 2: Root Cause Analysis & Systemic Issues
- What are the underlying causes of these anti-patterns?
- Are there systemic issues in development practices?
- How do anti-patterns relate to architectural decisions?
- Identify process or knowledge gaps causing anti-patterns

### Thought 3: Impact Assessment & Risk Analysis
- What is the impact of each anti-pattern on system quality?
- How do anti-patterns affect maintainability and performance?
- Which anti-patterns pose the highest risk?
- Assess technical debt accumulation from anti-patterns

### Thought 4: Refactoring Strategy & Prioritization
- What is the strategy for eliminating anti-patterns?
- How should refactoring efforts be prioritized?
- What are the dependencies between different fixes?
- Plan incremental refactoring approach

### Thought 5: Prevention & Process Improvement
- How can similar anti-patterns be prevented in the future?
- What development practices need improvement?
- How can code reviews and guidelines be enhanced?
- Develop education and training strategies

### Thought 6: Quality Assurance & Monitoring Strategy
- How can anti-pattern detection be automated?
- What metrics should be tracked for code quality?
- How will quality gates be implemented?
- Plan ongoing quality monitoring and improvement

## Expected Output Format
For each thought, provide:
- Specific anti-pattern analysis with examples
- Impact assessment and risk evaluation
- Refactoring recommendations and priorities
- Prevention and quality improvement strategies

Please detect and analyze these anti-patterns systematically using sequential thinking.""",
        version="1.0.0",
        description="Sequential thinking template for anti-pattern detection",
        tags=["anti-patterns", "quality", "refactoring", "technical-debt", "best-practices"],
        variables=["detection_title", "context", "antipattern_count", "high_impact_count", "common_categories", "affected_files"],
        complexity_threshold="medium",
        estimated_tokens=6500
    ),

    SequentialThinkingTemplate.SWE_SYSTEM_RESTRUCTURING: SequentialThinkingPrompt(
        template_id="swe_system_restructuring_seq_v1",
        name="System Restructuring Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_SYSTEM_RESTRUCTURING,
        content="""# Sequential System Restructuring: {restructuring_title}

## Context
{context}

## Current System State
- System Size: {system_size}
- Complexity Metrics: {complexity_metrics}
- Identified Issues: {identified_issues}
- Restructuring Goals: {restructuring_goals}

## Sequential System Restructuring Requirements

Please provide a structured sequential thinking approach to system restructuring:

### Thought 1: Current State Analysis & Problem Definition
- What are the specific problems requiring restructuring?
- How is the current system structured and organized?
- What are the pain points and bottlenecks?
- Define the scope and boundaries of restructuring effort

### Thought 2: Target Architecture Design & Vision
- What should the restructured system look like?
- How will components be organized and related?
- What architectural patterns will be applied?
- Design the target state with clear principles

### Thought 3: Migration Strategy & Transition Planning
- How will the system be migrated from current to target state?
- What is the optimal sequence of restructuring steps?
- How will system continuity be maintained during transition?
- Plan for rollback and recovery strategies

### Thought 4: Risk Assessment & Mitigation Planning
- What are the major risks in this restructuring effort?
- How will risks be identified, assessed, and mitigated?
- What are the potential failure modes and impacts?
- Develop comprehensive risk management strategy

### Thought 5: Implementation Planning & Execution Strategy
- What resources and timeline are needed for restructuring?
- How will changes be implemented and validated?
- What are the coordination and communication requirements?
- Plan detailed implementation approach

### Thought 6: Validation & Success Measurement
- How will restructuring success be measured and validated?
- What are the key performance indicators and metrics?
- How will system quality and performance be verified?
- Plan for ongoing monitoring and optimization

## Expected Output Format
For each thought, provide:
- Detailed restructuring analysis and recommendations
- Migration strategy with specific steps and timelines
- Risk assessment and mitigation plans
- Success metrics and validation approaches

Please plan this system restructuring systematically using sequential thinking.""",
        version="1.0.0",
        description="Sequential thinking template for system restructuring",
        tags=["restructuring", "architecture", "migration", "transformation", "strategy"],
        variables=["restructuring_title", "context", "system_size", "complexity_metrics", "identified_issues", "restructuring_goals"],
        complexity_threshold="critical",
        estimated_tokens=8000
    ),

    SequentialThinkingTemplate.SWE_GRAPH_TRAVERSAL_OPTIMIZATION: SequentialThinkingPrompt(
        template_id="swe_graph_traversal_optimization_seq_v1",
        name="Graph Traversal Optimization Sequential Thinking",
        template_type=SequentialThinkingTemplate.SWE_GRAPH_TRAVERSAL_OPTIMIZATION,
        content="""# Sequential Graph Traversal Optimization: {optimization_title}

## Context
{context}

## Graph Performance Metrics
- Current Traversal Time: {current_traversal_time}
- Graph Size: {graph_size}
- Traversal Frequency: {traversal_frequency}
- Performance Bottlenecks: {bottlenecks}

## Sequential Graph Traversal Optimization Requirements

Please provide a structured sequential thinking approach to optimize graph traversal:

### Thought 1: Current Performance Analysis & Bottleneck Identification
- What are the current performance characteristics of graph traversal?
- Where are the bottlenecks in traversal operations?
- How do different graph structures affect traversal performance?
- Identify specific performance issues and their causes

### Thought 2: Traversal Algorithm Analysis & Selection
- What traversal algorithms are currently being used?
- How appropriate are these algorithms for the graph structure?
- What alternative algorithms might be more efficient?
- Analyze algorithmic complexity and suitability

### Thought 3: Data Structure Optimization & Indexing Strategy
- How can the graph data structures be optimized for traversal?
- What indexing strategies would improve traversal performance?
- How can memory layout and access patterns be improved?
- Design optimized data structures for specific traversal patterns

### Thought 4: Caching & Memoization Strategy
- What traversal results can be cached for performance improvement?
- How can memoization be applied to expensive traversal operations?
- What are the cache invalidation and consistency requirements?
- Design effective caching and memoization strategies

### Thought 5: Parallelization & Concurrency Optimization
- How can traversal operations be parallelized?
- What are the opportunities for concurrent processing?
- How will thread safety and consistency be maintained?
- Design parallelization strategy for traversal operations

### Thought 6: Monitoring & Continuous Optimization
- How will traversal performance be monitored and measured?
- What metrics will indicate optimization success?
- How will performance be maintained over time?
- Plan for ongoing optimization and performance tuning

## Expected Output Format
For each thought, provide:
- Performance analysis with specific metrics and benchmarks
- Optimization recommendations with implementation details
- Risk assessment for optimization changes
- Monitoring and maintenance strategies

Please optimize this graph traversal systematically using sequential thinking.""",
        version="1.0.0",
        description="Sequential thinking template for graph traversal optimization",
        tags=["optimization", "performance", "graph", "algorithms", "traversal"],
        variables=["optimization_title", "context", "current_traversal_time", "graph_size", "traversal_frequency", "bottlenecks"],
        complexity_threshold="high",
        estimated_tokens=7000
    )
}

def get_template(template_type: SequentialThinkingTemplate) -> SequentialThinkingPrompt:
    """Get a sequential thinking template by type."""
    return SEQUENTIAL_THINKING_TEMPLATES.get(template_type)

def get_all_templates() -> dict[SequentialThinkingTemplate, SequentialThinkingPrompt]:
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

def get_template_for_complexity(complexity: str) -> list[SequentialThinkingTemplate]:
    """Get suitable templates for a given complexity level."""
    complexity_map = {
        "low": [SequentialThinkingTemplate.SWE_ANALYSIS, SequentialThinkingTemplate.SWE_TESTING],
        "medium": [SequentialThinkingTemplate.SWE_ANALYSIS, SequentialThinkingTemplate.SWE_DEBUGGING,
                  SequentialThinkingTemplate.SWE_REFACTORING, SequentialThinkingTemplate.SWE_TESTING,
                  SequentialThinkingTemplate.SWE_PLANNING],
        "high": [SequentialThinkingTemplate.SWE_ARCHITECTURE, SequentialThinkingTemplate.SWE_IMPLEMENTATION,
                 SequentialThinkingTemplate.SWE_INTEGRATION, SequentialThinkingTemplate.SWE_PLANNING,
                 SequentialThinkingTemplate.SWE_ADG_ANALYSIS, SequentialThinkingTemplate.SWE_VIOLATION_REMEDIATION,
                 SequentialThinkingTemplate.SWE_LAYER_BOUNDARY_AUDIT, SequentialThinkingTemplate.SWE_DEPENDENCY_GRAPH_ANALYSIS,
                 SequentialThinkingTemplate.SWE_ARCHITECTURAL_REVIEW, SequentialThinkingTemplate.SWE_ANTIPATTERN_DETECTION,
                 SequentialThinkingTemplate.SWE_GRAPH_TRAVERSAL_OPTIMIZATION],
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
