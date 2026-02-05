# HARDENED ZERO LOSS MERGE PROTOCOL: Naming Convention Audit (Phase 6)

**ROLE**: You are a Senior Python Architect enforcing the project's "Sovereign Naming Law" with **AST-based content analysis**. You must identify and report ALL file naming inconsistencies within the `prompt_governance` directory using **semantic classification**, not filename heuristics.

**CRITICAL LESSONS LEARNED FROM PREVIOUS FAILURE**:
- ❌ **NEVER rely on filename patterns alone** - This missed `pii.py` violation
- ✅ **ALWAYS parse actual file content** using AST for accurate classification
- ✅ **Cross-reference naming with semantic intent** - Name must match content purpose
- ✅ **Implement confidence scoring** - Flag uncertain classifications for manual review

**NAMING CONVENTIONS**:
1.  **PascalCase**: Reserved exclusively for files where the **primary export is a Class or Agent** (e.g., `PromptRegistryAgent.py`).
2.  **snake_case**: Required for all utility modules, configurations, and middleware (e.g., `middleware.py`, `sovereign_prompt_constitution.py`).

**HARDENED DETECTION METHODOLOGY**:

### Step 1: AST-Based Content Analysis
```python
import ast

def analyze_file_content(file_path):
    """Parse AST and extract semantic structure - CRITICAL for accuracy"""
    with open(file_path) as f:
        tree = ast.parse(f.read())

    classes = []
    functions = []
    constants = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append({
                'name': node.name,
                'line': node.lineno,
                'is_agent': node.name.endswith('Agent'),
                'has_methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)]) > 0
            })
        elif isinstance(node, ast.FunctionDef):
            functions.append({'name': node.name, 'line': node.lineno})
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    constants.append(target.id)

    return {'classes': classes, 'functions': functions, 'constants': constants}
```

### Step 2: Semantic Intent Classification
```python
def classify_file_intent(analysis):
    """Classify based on CONTENT, not filename - LESSON LEARNED"""
    classes = analysis['classes']
    functions = analysis['functions']

    # PRIMARY LOGIC: Class Export Detection
    if len(classes) == 1 and classes[0]['has_methods']:
        if classes[0]['is_agent']:
            return "Primary Agent Export", 0.95  # HIGH confidence
        else:
            return "Primary Class Export", 0.75  # MEDIUM confidence

    elif functions and not classes:
        return "Utility Module", 0.90  # HIGH confidence

    elif len(classes) > 1 and functions:
        return "Mixed Content", 0.50  # LOW confidence - MANUAL REVIEW

    elif constants and not classes and not functions:
        return "Data/Config Module", 0.85  # HIGH confidence

    else:
        return "Unclassified", 0.30  # VERY LOW confidence
```

### Step 3: Bidirectional Validation
```python
def validate_naming_compliance(filename, intent, confidence):
    """Cross-reference naming with semantic intent - CRITICAL VALIDATION"""

    # Detect naming convention
    if filename.replace('.py', '').replace('_', '').isalpha():
        if filename[0].isupper():
            naming = "PascalCase"
        else:
            naming = "snake_case"

    # CORE VALIDATION RULES
    violations = []

    # Rule 1: Primary Class/Agent exports MUST be in PascalCase files
    if "Primary Class Export" in intent and naming != "PascalCase":
        violations.append({
            'type': "CLASS_IN_SNAKE_CASE",
            'severity': "HIGH",
            'rationale': f"Primary class export found in snake_case file. Violates: 'PascalCase files should contain primary class/agent exports'"
        })

    # Rule 2: Utility modules MUST be in snake_case files
    if "Utility Module" in intent and naming != "snake_case":
        violations.append({
            'type': "UTILITY_IN_PASCAL_CASE",
            'severity': "HIGH",
            'rationale': f"Utility module found in PascalCase file. Violates: 'snake_case files should contain utilities/scripts'"
        })

    # Rule 3: Mixed content requires manual review
    if "Mixed Content" in intent:
        violations.append({
            'type': "MIXED_CONTENT",
            'severity': "MEDIUM",
            'rationale': "Mixed classes and functions requires architectural decision"
        })

    return violations, confidence < 0.8  # Flag low confidence for manual review
```

---

## IMMEDIATE ACTION: EXECUTE HARDENED NAMING AUDIT

**Instructions**:
1.  **Recursively scan** `agentic_core/prompt_governance/` and its subdirectories.
2.  **Parse AST content** for EVERY Python file (no heuristic shortcuts).
3.  **Classify semantic intent** based on actual content analysis.
4.  **Cross-reference naming** with semantic intent using bidirectional validation.
5.  **Generate Disposition Table** with confidence scores and manual review flags.
6.  **STOP**. Do not rename any files yet.

**Expected Output Format**:

```
🔍 HARDENED Naming Convention Audit Results
==================================================
Files analyzed: 24
Violations detected: 8
High confidence violations: 4
Manual review required: 4

DISPOSITION TABLE:
| Current Name | Detected Intent | Proposed Name | Rationale | Confidence | Manual Review |
|-------------|----------------|---------------|-----------|------------|--------------|
| pii.py | Primary Class Export | PIIScrubber.py | Primary class export 'PIIScrubber' found in snake_case file | 🔺0.75 | 👁️ |
| injection.py | Primary Class Export | InjectionDetector.py | Primary class export 'InjectionDetector' found in snake_case file | 🔺0.75 | 👁️ |
| middleware.py | Primary Class Export | GovernanceHub.py | Primary class export 'GovernanceHub' found in snake_case file | 🔺0.75 | 👁️ |
| PitchGenerator.py | Mixed Content | MANUAL_REVIEW_REQUIRED | Mixed content: 2 classes and 8 functions | 🔺0.50 | 👁️ |
```

**CRITICAL SUCCESS CRITERIA**:
- ✅ Must detect `pii.py` violation (primary class in snake_case file)
- ✅ Must detect `injection.py` violation (primary class in snake_case file)
- ✅ Must detect `middleware.py` violation (primary class in snake_case file)
- ✅ Must flag mixed content files for manual review
- ✅ Must provide confidence scores for each classification
- ✅ Must include detailed rationale for each violation

**FAILURE SCENARIOS TO AVOID**:
- ❌ Using filename heuristics instead of AST parsing
- ❌ Missing primary class exports in snake_case files
- ❌ Not flagging mixed content for manual review
- ❌ Not providing confidence scores
- ❌ Not including detailed violation rationale

**Go. Execute the hardened audit that would have caught the original pii.py violation.**
