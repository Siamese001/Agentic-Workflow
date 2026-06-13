# Comprehensive CST Migration Roadmap: Phases 1.3+

This comprehensive roadmap covers the complete migration of all healing capabilities from legacy string-based operations to zero-loss CST-based transformations, addressing all identified shortcomings and establishing a unified healing architecture.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State Assessment

### ✅ **Phase 1.1b COMPLETE**: Import Healing (CST Verified)
- `SurgicalImportRemover` working with zero-loss guarantee
- `heal_imports()` successfully migrated to CST approach
- Comprehensive test coverage with preservation verification

### 🔄 **Phase 1.2 ACTIVE**: Canon Healing (In Progress)
- `SurgicalDocstringInserter` exists but has implementation bugs
- `SurgicalBareExceptFixer` exists but needs integration
- `heal_canon()` still using legacy string operations

### ❌ **Phase 1.3 PENDING**: Structural Healing (Not Started)
- `heal_structural()` uses primitive line-based operations
- No CST transformers for structural fixes
- Missing violation detection for structural issues

## Complete Migration Roadmap

### **Phase 1.2: Canon Healing CST Migration** (Current Priority)

#### **Step 1.2.1: Fix SurgicalDocstringInserter**
**Critical Issues**:
- Incorrectly creates `cst.Module` instead of updating body
- Missing indentation handling
- No proper `cst.IndentedBlock` usage

**Required Fix**:
```python
def leave_ClassDef(self, original_node, updated_node):
    # CORRECT: Use cst.IndentedBlock for body structure
    docstring = cst.SimpleStatementLine(
        body=[cst.Expr(value=cst.SimpleString(value='"""Class docstring"""'))]
    )
    new_body = cst.IndentedBlock(body=[docstring] + list(updated_node.body.body))
    return updated_node.with_changes(body=new_body)
```

#### **Step 1.2.2: Create SurgicalFutureImportInserter**
**Missing Transformer**: No CST transformer for `__future__` imports

**Implementation**:
```python
class SurgicalFutureImportInserter(cst.CSTTransformer):
    def leave_Module(self, original_node, updated_node):
        # Insert future import after shebang/docstring
        # Preserve existing imports and comments
```

#### **Step 1.2.3: Refactor heal_canon()**
**Current Legacy Issues**:
- String-based line manipulation
- No surgical context creation
- Missing violation detection

**Migration Pattern**:
```python
def heal_canon(self, file_path: Path):
    # 1. Parse AST and detect canon violations
    # 2. Create SurgicalContext objects
    # 3. Use self.heal_surgical_cst()
    # 4. Map results to HealingAction objects
```

### **Phase 1.3: Structural Healing CST Migration**

#### **Current Legacy Issues**:
- `heal_structural()` uses primitive string operations
- Handles trailing whitespace and blank lines with line manipulation
- No CST transformers for structural fixes
- Missing violation detection framework

#### **Step 1.3.1: Create Structural CST Transformers**
**New Transformers Needed**:
```python
class SurgicalWhitespaceFixer(cst.CSTTransformer):
    """Remove trailing whitespace while preserving formatting."""

class SurgicalBlankLineNormalizer(cst.CSTTransformer):
    """Normalize excessive blank lines while preserving structure."""

class SurgicalLineEndingFixer(cst.CSTTransformer):
    """Fix inconsistent line endings."""
```

#### **Step 1.3.2: Implement Structural Violation Detection**
**Detection Logic**:
```python
def detect_structural_violations(self, content: str, tree: ast.AST):
    violations = []
    # Detect trailing whitespace
    # Detect excessive blank lines
    # Detect inconsistent line endings
    # Create ViolationConstraint objects
```

#### **Step 1.3.3: Refactor heal_structural()**
**Complete CST Migration**:
```python
def heal_structural(self, file_path: Path):
    # Replace all string operations with CST approach
    # Use surgical context pattern
    # Apply multiple transformers in sequence
```

### **Phase 2.0: Advanced Healing Capabilities**

#### **Step 2.1: Type Hint Healing**
**Missing Capabilities**:
- No CST transformers for type hint fixes
- `TypeHintFixerAgent` exists but uses legacy approach
- Missing import management for type hints

**New Transformers**:
```python
class SurgicalTypeHintInserter(cst.CSTTransformer):
    """Add missing type hints to function signatures."""

class SurgicalImportOrganizer(cst.CSTTransformer):
    """Organize imports and add typing imports."""
```

#### **Step 2.2: Naming Convention Healing**
**Current Gap**: No CST-based naming enforcement
- `NamingLawHealerAgent` exists but uses string operations
- Missing AST-level identifier analysis

**New Transformers**:
```python
class SurgicalNamingFixer(cst.CSTTransformer):
    """Fix naming conventions in classes, functions, variables."""

class SurgicalImportRenamer(cst.CSTTransformer):
    """Update imports when renaming symbols."""
```

#### **Step 2.3: Gravity/Hierarchy Healing**
**Advanced Structural Healing**:
- File move operations with import fixing
- Hierarchy compliance fixes
- Blueprint enforcement

**New Capabilities**:
```python
class SurgicalFileMover:
    """Move files with automatic import fixing."""

class SurgicalHierarchyFixer(cst.CSTTransformer):
    """Fix module hierarchy violations."""
```

### **Phase 3.0: Unified Healing Architecture**

#### **Step 3.1: Healing Orchestration**
**Current Issues**:
- Separate healing methods with duplicated logic
- No unified healing pipeline
- Missing cross-healing coordination

**Unified Architecture**:
```python
class UnifiedCSTHealer:
    """Single entry point for all CST-based healing."""

    def heal_all(self, file_path: Path, healing_config: HealingConfig):
        # Detect all violations
        # Create unified surgical context
        # Apply all transformers in optimal order
        # Return comprehensive results
```

#### **Step 3.2: Healing Strategy Engine**
**Smart Healing**:
- Conflict resolution between transformers
- Optimal transformer ordering
- Healing dependency management

#### **Step 3.3: Healing Validation Framework**
**Quality Assurance**:
- Zero-loss validation for all operations
- Automatic rollback on failures
- Healing effectiveness metrics

### **Phase 4.0: Performance & Scalability**

#### **Step 4.1: Batch Healing Optimization**
**Current Limitation**: File-by-file processing
- Multi-file healing coordination
- Dependency-aware batch processing
- Parallel healing capabilities

#### **Step 4.2: Healing Caching**
**Performance Optimization**:
- AST parsing caching
- Transformer result caching
- Incremental healing support

#### **Step 4.3: Large-Scale Healing**
**Enterprise Features**:
- Repository-scale healing coordination
- Healing progress tracking
- Rollback capabilities

## Implementation Priorities

### **Immediate (Phase 1.2)**:
1. Fix `SurgicalDocstringInserter` implementation bugs
2. Create `SurgicalFutureImportInserter` transformer
3. Refactor `heal_canon()` to use CST approach
4. Add comprehensive canon healing tests

### **Short-term (Phase 1.3)**:
1. Create structural CST transformers
2. Implement structural violation detection
3. Refactor `heal_structural()` method
4. Add structural healing test coverage

### **Medium-term (Phase 2.0)**:
1. Implement type hint healing transformers
2. Create naming convention fixers
3. Add gravity/hierarchy healing capabilities
4. Unify healing architecture

### **Long-term (Phases 3.0-4.0)**:
1. Build unified healing orchestration
2. Add healing strategy engine
3. Implement performance optimizations
4. Add enterprise-scale features

## Technical Debt & Shortcomings

### **Current Issues**:
1. **Inconsistent Healing Patterns**: Mix of CST and string approaches
2. **Duplicate Logic**: Similar patterns across healing methods
3. **Missing Violation Detection**: No standardized violation creation
4. **Limited Test Coverage**: Many healing paths untested
5. **No Healing Validation**: No zero-loss verification framework

### **Architecture Problems**:
1. **Fragmented Healing**: Separate agents with duplicated logic
2. **No Healing Orchestration**: No unified healing pipeline
3. **Missing Error Handling**: No rollback or recovery mechanisms
4. **Performance Issues**: No caching or optimization

## Success Criteria

### **Phase Completion Criteria**:
- ✅ All string-based operations replaced with CST
- ✅ Zero-loss guarantee for all healing operations
- ✅ Comprehensive test coverage with preservation verification
- ✅ Unified healing architecture established
- ✅ Performance optimized for large-scale operations

### **Quality Gates**:
- All healing operations preserve comments and formatting
- No regression in existing functionality
- Comprehensive error handling and rollback
- Performance benchmarks met

## Risk Mitigation

### **Technical Risks**:
- **CST Complexity**: Use established patterns from Phase 1.1b
- **Transformer Conflicts**: Implement conflict resolution framework
- **Performance Degradation**: Add caching and optimization
- **Regression Risk**: Comprehensive test coverage

### **Implementation Risks**:
- **Scope Creep**: Clear phase boundaries and priorities
- **Integration Issues**: Incremental migration with fallbacks
- **Resource Constraints**: Prioritize high-impact healing types

This roadmap provides a complete path from the current mixed state to a fully unified, zero-loss CST-based healing architecture.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

