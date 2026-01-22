#!/usr/bin/env python3
"""Test initialization chain integrity for L0 DNA mixins."""

class TestInit:
    """Base class with no __init__."""
    pass


class HealerMixinTest(TestInit):
    """Simulates HealerMixin."""
    def __init__(self, **kwargs):
        print(f"  → HealerMixin.__init__ called with kwargs: {kwargs}")
        super().__init__(**kwargs)
        self._healer_initialized = True


class MCPHardenedMixinTest(TestInit):
    """Simulates MCPHardenedMixin."""
    def __init__(self, **kwargs):
        print(f"  → MCPHardenedMixin.__init__ called with kwargs: {kwargs}")
        super().__init__(**kwargs)
        self._mcp_initialized = True


class SubatomicTestingMixinTest(TestInit):
    """Simulates SubatomicTestingMixin (no __init__)."""
    pass


class InstructionalInjectionMixinTest(TestInit):
    """Simulates InstructionalInjectionMixin (no __init__)."""
    pass


class InfrastructureMixinTest(
    HealerMixinTest,
    MCPHardenedMixinTest,
    SubatomicTestingMixinTest,
    InstructionalInjectionMixinTest
):
    """Simulates InfrastructureMixin."""
    def __init__(self):
        print("  → InfrastructureMixin.__init__ called")
        super().__init__()
        self._infra_initialized = True


class SovereignBaseAgentTest(InfrastructureMixinTest):
    """Simulates SovereignBaseAgent."""
    def __post_init__(self):
        print("  → SovereignBaseAgent.__post_init__ called")
        super().__init__()
        self._sovereign_initialized = True


class ConcreteAgentTest(SovereignBaseAgentTest):
    """Simulates a concrete agent."""
    def __init__(self):
        print("ConcreteAgent.__init__ called")
        super().__init__()
        self.__post_init__()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("INITIALIZATION CHAIN TEST")
    print("="*70)
    
    print("\nMRO Chain:")
    for i, cls in enumerate(ConcreteAgentTest.__mro__):
        print(f"  {i}. {cls.__name__}")
    
    print("\nInitialization Sequence:")
    agent = ConcreteAgentTest()
    
    print("\nVerification:")
    print(f"  _healer_initialized: {getattr(agent, '_healer_initialized', 'MISSING')}")
    print(f"  _mcp_initialized: {getattr(agent, '_mcp_initialized', 'MISSING')}")
    print(f"  _infra_initialized: {getattr(agent, '_infra_initialized', 'MISSING')}")
    print(f"  _sovereign_initialized: {getattr(agent, '_sovereign_initialized', 'MISSING')}")
    
    all_initialized = all([
        getattr(agent, '_healer_initialized', False),
        getattr(agent, '_mcp_initialized', False),
        getattr(agent, '_infra_initialized', False),
        getattr(agent, '_sovereign_initialized', False),
    ])
    
    print("\n" + "="*70)
    if all_initialized:
        print("✅ INITIALIZATION CHAIN INTACT - All mixins initialized")
    else:
        print("❌ INITIALIZATION CHAIN BROKEN - Dead zones detected")
    print("="*70 + "\n")
