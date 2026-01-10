"""
Unit tests for ReportGenerator primitive.
Phase 9: Autonomous Evolution - L0 Primitive Test Coverage
"""
import pytest
from collections import Counter
from agentic_core.L0_maintenance.primitives.report_generator import ReportGenerator


class TestReportGenerator:
    """Comprehensive test suite for ReportGenerator."""
    
    def test_initialization(self):
        """Test ReportGenerator initializes correctly."""
        generator = ReportGenerator()
        
        assert hasattr(generator, 'generate_capability_report')
        assert hasattr(generator, 'generate_summary_table')
    
    def test_generate_capability_report_minimal(self):
        """Test generating report with minimal data."""
        generator = ReportGenerator()
        
        report = generator.generate_capability_report(
            live_agent_count=5,
            dead_agent_count=3,
            suspect_agent_count=1,
            live_cap_counter=Counter(),
            dead_cap_detail={},
            unique_to_dead=set(),
            underrepresented={},
            recommendations=[]
        )
        
        assert isinstance(report, str)
        assert "ULTRA CAPABILITY SUPPLEMENTATION ANALYSIS REPORT" in report
        assert "Executive Summary" in report
        assert "5" in report  # live agent count
        assert "3" in report  # dead agent count
    
    def test_generate_executive_summary(self):
        """Test executive summary section generation."""
        generator = ReportGenerator()
        
        lines = generator._generate_executive_summary(
            live_count=10,
            dead_count=5,
            suspect_count=2,
            unique_to_dead={'capability1', 'capability2'},
            underrepresented={'cap3': 1}
        )
        
        summary = "\n".join(lines)
        assert "Executive Summary" in summary
        assert "10" in summary
        assert "5" in summary
        assert "2" in summary
        assert "| Metric | Count |" in summary
    
    def test_generate_live_capabilities_section(self):
        """Test live capabilities section generation."""
        generator = ReportGenerator()
        
        cap_counter = Counter({
            'healing': 5,
            'validation': 3,
            'detection': 2
        })
        
        lines = generator._generate_live_capabilities_section(cap_counter)
        
        section = "\n".join(lines)
        assert "Live Agent Capability Coverage" in section
        assert "healing" in section
        assert "validation" in section
        assert "detection" in section
        assert "5" in section
        assert "3" in section
    
    def test_generate_unique_capabilities_section_with_data(self):
        """Test unique capabilities section with actual data."""
        generator = ReportGenerator()
        
        unique_to_dead = {'git_operations', 'redis_integration'}
        dead_cap_detail = {
            'DeadAgent1': {
                'file': '/path/to/agent1.py',
                'caps': {
                    'semantic_tags': {'git_operations'},
                    'patterns': set()
                }
            },
            'DeadAgent2': {
                'file': '/path/to/agent2.py',
                'caps': {
                    'semantic_tags': set(),
                    'patterns': {'redis_integration'}
                }
            }
        }
        
        lines = generator._generate_unique_capabilities_section(
            unique_to_dead, dead_cap_detail
        )
        
        section = "\n".join(lines)
        assert "Unique Capabilities in DEAD Agents" in section
        assert "GIT_OPERATIONS" in section.upper()
        assert "REDIS_INTEGRATION" in section.upper()
        assert "DeadAgent1" in section or "DEADAGENT1" in section
        assert "DeadAgent2" in section or "DEADAGENT2" in section
    
    def test_generate_unique_capabilities_section_empty(self):
        """Test unique capabilities section with no unique capabilities."""
        generator = ReportGenerator()
        
        lines = generator._generate_unique_capabilities_section(
            unique_to_dead=set(),
            dead_cap_detail={}
        )
        
        section = "\n".join(lines)
        assert "Unique Capabilities in DEAD Agents" in section
        assert "No completely unique capabilities" in section
    
    def test_generate_underrepresented_section_with_data(self):
        """Test underrepresented capabilities section with data."""
        generator = ReportGenerator()
        
        underrepresented = {
            'pruning': 1,
            'monitoring': 1
        }
        dead_cap_detail = {
            'DeadAgent1': {
                'file': '/path/to/agent1.py',
                'caps': {
                    'semantic_tags': {'pruning'},
                    'patterns': set()
                }
            },
            'DeadAgent2': {
                'file': '/path/to/agent2.py',
                'caps': {
                    'semantic_tags': {'monitoring'},
                    'patterns': set()
                }
            }
        }
        
        lines = generator._generate_underrepresented_section(
            underrepresented, dead_cap_detail
        )
        
        section = "\n".join(lines)
        assert "Underrepresented Capabilities" in section
        assert "pruning" in section
        assert "monitoring" in section
        assert "| Capability | Live Count | Potential Donors |" in section
    
    def test_generate_underrepresented_section_empty(self):
        """Test underrepresented section with no underrepresented capabilities."""
        generator = ReportGenerator()
        
        lines = generator._generate_underrepresented_section(
            underrepresented={},
            dead_cap_detail={}
        )
        
        section = "\n".join(lines)
        assert "Underrepresented Capabilities" in section
        assert "All capabilities well-represented" in section
    
    def test_generate_recommendations_section_with_data(self):
        """Test recommendations section with actual recommendations."""
        generator = ReportGenerator()
        
        recommendations = [
            {
                'target_agent': 'LiveAgent1',
                'donor_agent': 'DeadAgent1',
                'capability': 'git_operations',
                'method': 'git_commit',
                'priority': 'High'
            },
            {
                'target_agent': 'LiveAgent2',
                'donor_agent': 'DeadAgent2',
                'capability': 'redis_integration',
                'method': 'cache_data',
                'priority': 'Medium'
            }
        ]
        
        lines = generator._generate_recommendations_section(recommendations)
        
        section = "\n".join(lines)
        assert "Supplementation Recommendations" in section
        assert "2" in section  # Total recommendations count
        assert "LiveAgent1" in section or "LIVEAGENT1" in section
        assert "DeadAgent1" in section or "DEADAGENT1" in section
        assert "git_operations" in section or "GIT_OPERATIONS" in section
        assert "High" in section or "HIGH" in section
    
    def test_generate_recommendations_section_empty(self):
        """Test recommendations section with no recommendations."""
        generator = ReportGenerator()
        
        lines = generator._generate_recommendations_section([])
        
        section = "\n".join(lines)
        assert "Supplementation Recommendations" in section
        assert "No supplementation needed" in section
    
    def test_generate_summary_table_with_data(self):
        """Test generating markdown table from data."""
        generator = ReportGenerator()
        
        data = [
            {'Name': 'Agent1', 'Status': 'Active', 'Count': 5},
            {'Name': 'Agent2', 'Status': 'Inactive', 'Count': 3},
            {'Name': 'Agent3', 'Status': 'Active', 'Count': 7}
        ]
        
        table = generator.generate_summary_table(data)
        
        assert "| Name | Status | Count |" in table
        assert "Agent1" in table
        assert "Agent2" in table
        assert "Agent3" in table
        assert "Active" in table
        assert "Inactive" in table
    
    def test_generate_summary_table_empty(self):
        """Test generating table with empty data."""
        generator = ReportGenerator()
        
        table = generator.generate_summary_table([])
        
        assert table == ""
    
    def test_full_report_structure(self):
        """Test complete report structure with all sections."""
        generator = ReportGenerator()
        
        report = generator.generate_capability_report(
            live_agent_count=10,
            dead_agent_count=5,
            suspect_agent_count=2,
            live_cap_counter=Counter({'healing': 3, 'validation': 2}),
            dead_cap_detail={
                'DeadAgent1': {
                    'file': '/path/to/agent1.py',
                    'caps': {
                        'semantic_tags': {'git_operations'},
                        'patterns': set()
                    }
                }
            },
            unique_to_dead={'git_operations'},
            underrepresented={'monitoring': 1},
            recommendations=[
                {
                    'target_agent': 'LiveAgent1',
                    'donor_agent': 'DeadAgent1',
                    'capability': 'git_operations',
                    'method': 'git_commit',
                    'priority': 'High'
                }
            ]
        )
        
        # Verify all major sections present
        assert "ULTRA CAPABILITY SUPPLEMENTATION ANALYSIS REPORT" in report
        assert "Executive Summary" in report
        assert "Live Agent Capability Coverage" in report
        assert "Unique Capabilities in DEAD Agents" in report
        assert "Underrepresented Capabilities" in report
        assert "Supplementation Recommendations" in report
        
        # Verify data is present
        assert "10" in report
        assert "healing" in report or "HEALING" in report
        assert "GIT_OPERATIONS" in report.upper()
        assert "LiveAgent1" in report or "LIVEAGENT1" in report
    
    def test_report_contains_timestamp(self):
        """Test that generated report contains timestamp."""
        generator = ReportGenerator()
        
        report = generator.generate_capability_report(
            live_agent_count=1,
            dead_agent_count=1,
            suspect_agent_count=0,
            live_cap_counter=Counter(),
            dead_cap_detail={},
            unique_to_dead=set(),
            underrepresented={},
            recommendations=[]
        )
        
        assert "Generated:" in report
        # Should contain ISO format timestamp
        assert "T" in report  # ISO format has T separator
    
    def test_donor_truncation_in_underrepresented(self):
        """Test that donor list is truncated when too many donors."""
        generator = ReportGenerator()
        
        # Create 5 dead agents with same capability
        dead_cap_detail = {
            f'DeadAgent{i}': {
                'file': f'/path/to/agent{i}.py',
                'caps': {
                    'semantic_tags': {'monitoring'},
                    'patterns': set()
                }
            }
            for i in range(1, 6)
        }
        
        underrepresented = {'monitoring': 1}
        
        lines = generator._generate_underrepresented_section(
            underrepresented, dead_cap_detail
        )
        
        section = "\n".join(lines)
        # Should show first 3 and indicate more
        assert "(+2 more)" in section or "DeadAgent1" in section
    
    def test_markdown_formatting(self):
        """Test that report uses proper markdown formatting."""
        generator = ReportGenerator()
        
        report = generator.generate_capability_report(
            live_agent_count=5,
            dead_agent_count=3,
            suspect_agent_count=1,
            live_cap_counter=Counter({'healing': 2}),
            dead_cap_detail={},
            unique_to_dead=set(),
            underrepresented={},
            recommendations=[]
        )
        
        # Check for markdown elements
        assert report.startswith("# ")  # H1 header
        assert "## " in report  # H2 headers
        assert "| " in report  # Tables
        assert "---" in report  # Horizontal rules or table separators
        assert "**" in report  # Bold text
    
    def test_counter_sorting(self):
        """Test that capabilities are sorted by count in descending order."""
        generator = ReportGenerator()
        
        cap_counter = Counter({
            'healing': 5,
            'validation': 10,
            'detection': 3,
            'monitoring': 7
        })
        
        lines = generator._generate_live_capabilities_section(cap_counter)
        section = "\n".join(lines)
        
        # validation (10) should appear before healing (5)
        val_pos = section.find('validation')
        heal_pos = section.find('healing')
        assert val_pos < heal_pos
