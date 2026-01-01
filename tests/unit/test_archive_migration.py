"""Tests for migrated archive modules.

Validates that all modules migrated from archives/ to agentic_core/ work correctly.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock


class TestReflectionEngineImport:
    """Test reflection_engine module imports and basic functionality."""
    
    def test_import_reflection_engine(self):
        """Test that ReflectionEngine can be imported."""
        from agentic_core.runtime.shared_runtime.reflection_engine import ReflectionEngine
        assert ReflectionEngine is not None
    
    def test_import_critique_result(self):
        """Test that CritiqueResult can be imported."""
        from agentic_core.runtime.shared_runtime.reflection_engine import CritiqueResult
        assert CritiqueResult is not None
    
    def test_import_validation_criterion(self):
        """Test that ValidationCriterion can be imported."""
        from agentic_core.runtime.shared_runtime.reflection_engine import ValidationCriterion
        assert ValidationCriterion is not None
    
    def test_critique_result_creation(self):
        """Test CritiqueResult can be instantiated."""
        from agentic_core.runtime.shared_runtime.reflection_engine import CritiqueResult
        result = CritiqueResult(
            is_valid=True,
            confidence_score=0.85,
            critique_reasoning="Content meets quality standards",
            validation_type="test"
        )
        assert result.is_valid is True
        assert result.confidence_score == 0.85
    
    def test_validation_criterion_creation(self):
        """Test ValidationCriterion can be instantiated."""
        from agentic_core.runtime.shared_runtime.reflection_engine import ValidationCriterion
        criterion = ValidationCriterion(
            name="test_criterion",
            description="A test validation criterion",
            validator=r".*",
            is_required=True,
            weight=0.8
        )
        assert criterion.name == "test_criterion"
        assert criterion.weight == 0.8


class TestSignalEnhancerImport:
    """Test signal_enhancer module imports and basic functionality."""
    
    def test_import_signal_enhancer(self):
        """Test that SignalEnhancer can be imported."""
        from agentic_core.runtime.shared_runtime.signal_enhancer import SignalEnhancer
        assert SignalEnhancer is not None
    
    def test_import_signal_quality(self):
        """Test that SignalQuality can be imported."""
        from agentic_core.runtime.shared_runtime.signal_enhancer import SignalQuality
        assert SignalQuality is not None
    
    def test_import_quality_thresholds(self):
        """Test that QualityThresholds can be imported."""
        from agentic_core.runtime.shared_runtime.signal_enhancer import QualityThresholds
        assert QualityThresholds is not None
    
    def test_signal_enhancer_creation(self):
        """Test SignalEnhancer can be instantiated."""
        from agentic_core.runtime.shared_runtime.signal_enhancer import SignalEnhancer
        enhancer = SignalEnhancer(name="test_enhancer")
        assert enhancer.name == "test_enhancer"
    
    def test_signal_quality_enum(self):
        """Test SignalQuality enum values."""
        from agentic_core.runtime.shared_runtime.signal_enhancer import SignalQuality
        assert SignalQuality.EXCELLENT.value == "excellent"
        assert SignalQuality.HIGH.value == "high"
        assert SignalQuality.GOOD.value == "good"
        assert SignalQuality.MARGINAL.value == "marginal"
        assert SignalQuality.POOR.value == "poor"
    
    def test_assess_signal(self):
        """Test signal assessment functionality."""
        from agentic_core.runtime.shared_runtime.signal_enhancer import SignalEnhancer
        enhancer = SignalEnhancer(name="test")
        assessment = enhancer.assess_signal("This is high quality technical content with specific data points from 2024.")
        assert assessment is not None
        assert hasattr(assessment, 'composite_score')
        assert hasattr(assessment, 'quality_level')


class TestPromptAssemblerImport:
    """Test prompt_assembler module imports and basic functionality."""
    
    def test_import_prompt_assembler(self):
        """Test that PromptAssembler can be imported."""
        from agentic_core.prompt_governance.prompt_assembler import PromptAssembler
        assert PromptAssembler is not None
    
    def test_import_prompt_components(self):
        """Test that PromptComponents can be imported."""
        from agentic_core.prompt_governance.prompt_assembler import PromptComponents
        assert PromptComponents is not None
    
    def test_import_prompt_template(self):
        """Test that PromptTemplate can be imported."""
        from agentic_core.prompt_governance.prompt_assembler import PromptTemplate
        assert PromptTemplate is not None


class TestCognitiveContractsImport:
    """Test cognitive_contracts module imports and basic functionality."""
    
    def test_import_cognitive_contract(self):
        """Test that CognitiveContract can be imported."""
        from agentic_core.schemas.models.cognitive_contracts import CognitiveContract
        assert CognitiveContract is not None
    
    def test_import_contract_stage(self):
        """Test that ContractStage can be imported."""
        from agentic_core.schemas.models.cognitive_contracts import ContractStage
        assert ContractStage is not None
    
    def test_import_plan(self):
        """Test that Plan can be imported."""
        from agentic_core.schemas.models.cognitive_contracts import Plan
        assert Plan is not None
    
    def test_import_constraint(self):
        """Test that Constraint can be imported."""
        from agentic_core.schemas.models.cognitive_contracts import Constraint
        assert Constraint is not None


class TestRuntimeModelsImport:
    """Test runtime_models module imports and basic functionality."""
    
    def test_import_micro_stage(self):
        """Test that MicroStage can be imported."""
        from agentic_core.schemas.models.runtime_models import MicroStage
        assert MicroStage is not None
    
    def test_import_hop_state(self):
        """Test that HopState can be imported."""
        from agentic_core.schemas.models.runtime_models import HopState
        assert HopState is not None
    
    def test_import_retry_policy(self):
        """Test that RetryPolicy can be imported."""
        from agentic_core.schemas.models.runtime_models import RetryPolicy
        assert RetryPolicy is not None
    
    def test_import_injection_type(self):
        """Test that InjectionType can be imported."""
        from agentic_core.schemas.models.runtime_models import InjectionType
        assert InjectionType is not None


class TestDAGManagerImport:
    """Test dynamic_dag_manager module imports and basic functionality."""
    
    def test_import_dag_manager(self):
        """Test that DAGManager can be imported."""
        from agentic_core.L3_orchestration.dynamic_dag_manager import DAGManager
        assert DAGManager is not None
    
    def test_import_graph_transaction(self):
        """Test that GraphTransaction can be imported."""
        from agentic_core.L3_orchestration.dynamic_dag_manager import GraphTransaction
        assert GraphTransaction is not None
    
    def test_import_mutation_action(self):
        """Test that MutationAction can be imported."""
        from agentic_core.L3_orchestration.dynamic_dag_manager import MutationAction
        assert MutationAction is not None
    
    def test_import_dag_mutation(self):
        """Test that DAGMutation can be imported."""
        from agentic_core.L3_orchestration.dynamic_dag_manager import DAGMutation
        assert DAGMutation is not None
    
    def test_dag_manager_creation(self):
        """Test DAGManager can be instantiated."""
        from agentic_core.L3_orchestration.dynamic_dag_manager import DAGManager, DAGConfig
        config = DAGConfig(
            max_depth=10,
            max_nodes=100,
            allow_cycles=False,
            enable_history=True
        )
        manager = DAGManager(config=config)
        assert manager is not None


class TestSecurityModulesImport:
    """Test security modules imports."""
    
    def test_import_input_validator(self):
        """Test that InputValidator can be imported."""
        from agentic_core.L5_safety.guardrails.input_validator import InputValidator
        assert InputValidator is not None
    
    def test_import_secure_config_manager(self):
        """Test that SecureConfigManager can be imported."""
        from agentic_core.L5_safety.guardrails.secure_config import SecureConfigManager
        assert SecureConfigManager is not None
    
    def test_import_secure_error(self):
        """Test that SecureError can be imported."""
        from agentic_core.L5_safety.guardrails.secure_error import SecureError
        assert SecureError is not None
    
    def test_import_secure_logger(self):
        """Test that SecureLogger can be imported."""
        from agentic_core.L5_safety.guardrails.secure_logger import SecureLogger
        assert SecureLogger is not None


class TestIntegration:
    """Integration tests for migrated modules."""
    
    def test_all_runtime_shared_imports(self):
        """Test all runtime.shared_runtime imports work together."""
        from agentic_core.runtime.shared_runtime import (
            ReflectionEngine,
            CritiqueResult,
            ValidationCriterion,
            ReflectionConfig,
            MutationRequest,
            SignalEnhancer,
            SignalQuality,
            SignalAssessment,
            QualityThresholds,
            ClaimAnalysis,
        )
        assert all([
            ReflectionEngine,
            CritiqueResult,
            ValidationCriterion,
            ReflectionConfig,
            MutationRequest,
            SignalEnhancer,
            SignalQuality,
            SignalAssessment,
            QualityThresholds,
            ClaimAnalysis,
        ])
    
    def test_all_schemas_models_imports(self):
        """Test all schemas.models imports work together."""
        from agentic_core.schemas.models import (
            CognitiveContract,
            CognitiveContractManager,
            CognitiveContractValidator,
            ContractStage,
            Constraint,
            Plan,
            MicroStage,
            HopState,
            RetryPolicy,
            MicroCheckpoint,
            StageTransition,
            InjectionType,
        )
        assert all([
            CognitiveContract,
            CognitiveContractManager,
            CognitiveContractValidator,
            ContractStage,
            Constraint,
            Plan,
            MicroStage,
            HopState,
            RetryPolicy,
            MicroCheckpoint,
            StageTransition,
            InjectionType,
        ])
    
    def test_prompt_governance_imports(self):
        """Test prompt_governance imports work."""
        from agentic_core.prompt_governance import (
            PromptAssembler,
            PromptComponents,
            PromptTemplate,
        )
        assert all([PromptAssembler, PromptComponents, PromptTemplate])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
