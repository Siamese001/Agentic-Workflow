"""
Integration Tests for Token Planning Estimator

Tests for real-world planning scenarios, integration with planning workflows,
and end-to-end functionality.
"""

from pathlib import Path

import pytest


# Lazy imports to avoid collection-time conflicts
@pytest.fixture
def token_estimator_classes():
    from tools.utils.planning.preflight_hook import TokenBudgetExceededError, require_token_budget
    return require_token_budget, TokenBudgetExceededError


@pytest.fixture
def planning_preflight_hook(tmp_path):
    from tools.utils.planning.preflight_hook import PlanningPreflightHook
    budget_file = tmp_path / "integration_budget.json"
    return PlanningPreflightHook(budget_file=budget_file)


class TestTokenEstimatorIntegration:
    """Integration tests for real planning scenarios"""

    def setup_method(self):
        """Setup test fixtures"""
        from tools.utils.planning.preflight_hook import PlanningPreflightHook
        import tempfile
        import uuid
        # Use unique temp directory per test to avoid parallel execution conflicts
        self.temp_dir = Path(tempfile.gettempdir()) / f"test_integration_{uuid.uuid4().hex[:8]}"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.budget_file = self.temp_dir / "integration_budget.json"
        self.hook = PlanningPreflightHook(budget_file=self.budget_file)

    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil
        import time
        # Wait a moment for file handles to close (Windows)
        time.sleep(0.1)
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors on Windows

    def test_real_planning_scenario_feature_development(self):
        """Test a realistic feature development planning scenario"""
        # Simulate a real feature development workflow
        planning_steps = [
            {
                'name': 'requirements_analysis',
                'type': 'analysis',
                'system_prompt': 'You are a senior software architect analyzing requirements for a new feature.',
                'user_prompt': 'Analyze the requirements for implementing user authentication with JWT tokens.',
                'files': [
                    {'path': 'requirements.md', 'content': '# Authentication Requirements\n\n## User Stories\n- As a user, I want to login with email/password\n- As a user, I want to stay logged in across sessions\n- As an admin, I want to manage user sessions\n\n## Technical Requirements\n- JWT token-based authentication\n- Secure password hashing\n- Session management\n- Rate limiting\n\n## Security Requirements\n- Password complexity validation\n- Account lockout after failed attempts\n- Secure token storage\n' * 10},  # Multiply to make it larger
                    {'path': 'api_spec.yaml', 'content': 'openapi: 3.0.0\ninfo:\n  title: Auth API\n  version: 1.0.0\npaths:\n  /auth/login:\n    post:\n      summary: User login\n      requestBody:\n        content:\n          application/json:\n            schema:\n              type: object\n              properties:\n                email:\n                  type: string\n                password:\n                  type: string\n' * 20}
                ],
                'retrieved_context': [
                    {'content': 'JWT best practices article...' * 100},
                    {'content': 'Security guidelines for authentication...' * 100},
                    {'content': 'Database schema design patterns...' * 100}
                ]
            },
            {
                'name': 'design_architecture',
                'type': 'design',
                'system_prompt': 'You are a system designer creating the authentication architecture.',
                'user_prompt': 'Design the authentication system architecture based on the requirements.',
                'files': [
                    {'path': 'current_architecture.md', 'content': '# Current System\n\n## Components\n- User Service\n- API Gateway\n- Database\n\n## Limitations\n- No authentication\n- No session management\n' * 15}
                ],
                'diffs': [
                    {'path': 'architecture.md', 'content': 'diff --git a/architecture.md b/architecture.md\n+++ b/architecture.md\n@@ -1,10 +1,20 @@\n # Current System\n \n ## Components\n - User Service\n - API Gateway\n - Database\n+\n+## New Components\n+- Auth Service\n+- Token Store\n+- Session Manager\n' * 10}
                ],
                'prior_steps': ['requirements_analysis completed successfully']
            },
            {
                'name': 'implementation_planning',
                'type': 'planning',
                'system_prompt': 'You are a tech lead planning the implementation.',
                'user_prompt': 'Create detailed implementation plan for the authentication feature.',
                'files': [
                    {'path': 'project_structure.py', 'content': '# Project Structure\nsrc/\n  auth/\n    models.py\n    services.py\n    routes.py\n  utils/\n    security.py\n    validators.py\n' * 20},
                    {'path': 'database_schema.sql', 'content': '-- Users table\nCREATE TABLE users (\n  id SERIAL PRIMARY KEY,\n  email VARCHAR(255) UNIQUE NOT NULL,\n  password_hash VARCHAR(255) NOT NULL,\n  created_at TIMESTAMP DEFAULT NOW()\n);\n\n-- Sessions table\nCREATE TABLE sessions (\n  id SERIAL PRIMARY KEY,\n  user_id INTEGER REFERENCES users(id),\n  token_hash VARCHAR(255) NOT NULL,\n  expires_at TIMESTAMP NOT NULL\n);\n' * 15}
                ],
                'logs': [
                    {'source': 'build.log', 'content': 'INFO: Building authentication module...\nERROR: Missing dependency: bcrypt\nWARN: Consider using passlib instead\nINFO: Database migration needed\n' * 10}
                ],
                'retrieved_context': [
                    {'content': 'Python authentication libraries comparison...' * 50},
                    {'content': 'Database migration best practices...' * 50}
                ],
                'prior_steps': ['requirements_analysis completed', 'design_architecture completed']
            }
        ]

        # Execute all planning steps
        results = []
        for step in planning_steps:
            estimate = self.hook.preflight_check(
                plan_step=f"feature_auth/{step['name']}",
                system_prompt=step['system_prompt'],
                user_prompt=step['user_prompt'],
                files=step.get('files', []),
                diffs=step.get('diffs', []),
                logs=step.get('logs', []),
                retrieved_context=step.get('retrieved_context', []),
                prior_steps=step.get('prior_steps', [])
            )

            results.append(estimate)

            # Verify each step is within budget
            assert estimate.total_projected_tokens < 200000
            assert estimate.status in ['green', 'yellow']

            print(f"Step {step['name']}: {estimate.total_projected_tokens:,} tokens ({estimate.status})")

        # Verify overall results
        assert len(results) == 3
        total_tokens = sum(r.total_projected_tokens for r in results)
        assert total_tokens < 600000  # All steps combined should be reasonable

        # Check budget history
        summary = self.hook.get_budget_summary()
        assert summary['total_steps'] == 3
        assert summary['average_tokens_per_step'] > 0

        print(f"Integration test completed: {summary['total_steps']} steps, {total_tokens:,} total tokens")

    def test_bug_fix_scenario(self):
        """Test a bug fix planning scenario with logs and debugging"""
        bug_fix_steps = [
            {
                'name': 'bug_analysis',
                'type': 'debugging',
                'system_prompt': 'You are a senior developer analyzing a production bug.',
                'user_prompt': 'Analyze the following error and identify the root cause.',
                'files': [
                    {'path': 'buggy_code.py', 'content': '''
def process_user_data(user_id):
    """Process user data with potential issues"""
    user = get_user_from_db(user_id)

    # Potential null reference
    profile = user.profile
    preferences = profile.preferences

    # Process preferences without null checks
    for pref in preferences:
        if pref.type == 'notification':
            send_notification(pref.value)

    return True

def get_user_from_db(user_id):
    """Get user from database"""
    return User.query.get(user_id)
''' * 50}
                ],
                'logs': [
                    {'source': 'error.log', 'content': '''
2024-03-26 10:15:32 ERROR: AttributeError in process_user_data
Traceback (most recent call last):
  File "app.py", line 123, in process_request
    result = process_user_data(user_id)
  File "models.py", line 45, in process_user_data
    preferences = profile.preferences
AttributeError: 'NoneType' object has no attribute 'preferences'

2024-03-26 10:15:33 ERROR: Same error for user_id: 12345
2024-03-26 10:15:34 ERROR: Same error for user_id: 67890
2024-03-26 10:15:35 ERROR: Same error for user_id: 11111
''' * 20},
                    {'source': 'access.log', 'content': '''
2024-03-26 10:15:30 GET /api/users/12345/process 200
2024-03-26 10:15:31 GET /api/users/67890/process 200
2024-03-26 10:15:32 GET /api/users/11111/process 500
2024-03-26 10:15:33 GET /api/users/22222/process 500
''' * 30}
                ],
                'retrieved_context': [
                    {'content': 'Python null reference handling best practices...' * 30},
                    {'content': 'Database query error handling patterns...' * 30}
                ]
            },
            {
                'name': 'fix_implementation',
                'type': 'implementation',
                'system_prompt': 'You are implementing the bug fix.',
                'user_prompt': 'Implement a robust fix for the null reference error.',
                'files': [
                    {'path': 'buggy_code.py', 'content': '''
def process_user_data(user_id):
    """Process user data with potential issues"""
    user = get_user_from_db(user_id)

    # Potential null reference
    profile = user.profile
    preferences = profile.preferences

    # Process preferences without null checks
    for pref in preferences:
        if pref.type == 'notification':
            send_notification(pref.value)

    return True

def get_user_from_db(user_id):
    """Get user from database"""
    return User.query.get(user_id)
''' * 50}
                ],
                'diffs': [
                    {'path': 'buggy_code.py', 'content': '''
diff --git a/buggy_code.py b/buggy_code.py
+++ b/buggy_code.py
@@ -1,18 +1,25 @@
 def process_user_data(user_id):
     """Process user data with potential issues"""
     user = get_user_from_db(user_id)
+
+    # Handle null user
+    if user is None:
+        logger.error(f"User {user_id} not found")
+        return False

     # Potential null reference
     profile = user.profile
+    if profile is None:
+        logger.warning(f"User {user_id} has no profile")
+        return True
+
     preferences = profile.preferences
+    if preferences is None:
+        logger.warning(f"User {user_id} has no preferences")
+        return True

     # Process preferences without null checks
     for pref in preferences:
         if pref.type == 'notification':
             send_notification(pref.value)

     return True
''' * 20}
                ],
                'prior_steps': ['bug_analysis completed - identified null reference issue']
            }
        ]

        # Execute bug fix scenario
        for step in bug_fix_steps:
            estimate = self.hook.preflight_check(
                plan_step=f"bug_fix/{step['name']}",
                system_prompt=step['system_prompt'],
                user_prompt=step['user_prompt'],
                files=step.get('files', []),
                diffs=step.get('diffs', []),
                logs=step.get('logs', []),
                retrieved_context=step.get('retrieved_context', []),
                prior_steps=step.get('prior_steps', [])
            )

            # Verify budget compliance
            assert estimate.total_projected_tokens < 200000
            assert estimate.action in ['proceed', 'compress']

            print(f"Bug fix step {step['name']}: {estimate.total_projected_tokens:,} tokens")

    def test_api_refactoring_scenario(self):
        """Test API refactoring with many files and complex diffs"""
        api_refactor_steps = [
            {
                'name': 'legacy_analysis',
                'type': 'analysis',
                'system_prompt': 'You are analyzing a legacy API for refactoring.',
                'user_prompt': 'Analyze the legacy API endpoints and identify refactoring opportunities.',
                'files': [
                    {'path': 'legacy_api_v1.py', 'content': '''
# Legacy API v1 - Multiple endpoints in one file
@app.route('/api/v1/users', methods=['GET'])
def get_users():
    return jsonify(User.query.all())

@app.route('/api/v1/users/<int:id>', methods=['GET'])
def get_user(id):
    return jsonify(User.query.get_or_404(id))

@app.route('/api/v1/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return jsonify(user), 201

@app.route('/api/v1/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = User.query.get_or_404(id)
    for key, value in data.items():
        setattr(user, key, value)
    db.session.commit()
    return jsonify(user)

@app.route('/api/v1/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return '', 204
''' * 100},
                    {'path': 'legacy_models.py', 'content': '''
# Legacy models with issues
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))  # Plain text!

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'email': self.email}
''' * 50}
                ],
                'retrieved_context': [
                    {'content': 'REST API design principles...' * 40},
                    {'content': 'Flask blueprint patterns...' * 40},
                    {'content': 'API versioning strategies...' * 40}
                ]
            },
            {
                'name': 'refactor_design',
                'type': 'design',
                'system_prompt': 'You are designing the refactored API architecture.',
                'user_prompt': 'Design a clean, modular API architecture following best practices.',
                'files': [
                    {'path': 'current_structure.py', 'content': '''
# Current monolithic structure
app.py - Main application
models.py - All models
legacy_api_v1.py - All API endpoints
utils.py - Utility functions
''' * 30}
                ],
                'diffs': [
                    {'path': 'api_structure.md', 'content': '''
# Proposed API Structure

## New Structure
```
api/
  v2/
    __init__.py
    users/
      __init__.py
      routes.py
      schemas.py
      services.py
    auth/
      __init__.py
      routes.py
      schemas.py
      services.py
```

## Benefits
- Modular endpoints
- Separation of concerns
- Easier testing
- Better maintainability
''' * 20}
                ],
                'prior_steps': ['legacy_analysis completed - identified monolithic structure']
            }
        ]

        # Execute API refactoring scenario
        for step in api_refactor_steps:
            estimate = self.hook.preflight_check(
                plan_step=f"api_refactor/{step['name']}",
                system_prompt=step['system_prompt'],
                user_prompt=step['user_prompt'],
                files=step.get('files', []),
                diffs=step.get('diffs', []),
                logs=[],
                retrieved_context=step.get('retrieved_context', []),
                prior_steps=step.get('prior_steps', [])
            )

            # Verify budget compliance
            assert estimate.total_projected_tokens < 200000
            assert estimate.status in ['green', 'yellow']

            print(f"API refactor step {step['name']}: {estimate.total_projected_tokens:,} tokens")

    def test_decorator_integration(self, token_estimator_classes):
        """Test decorator integration with real workflow functions"""
        require_token_budget, _ = token_estimator_classes

        @require_token_budget(self.hook)
        def analyze_requirements(system_prompt, user_prompt, files, **kwargs):
            """Simulated requirements analysis function"""
            return {"status": "completed", "recommendations": ["Use JWT", "Add rate limiting"]}

        @require_token_budget(self.hook)
        def design_architecture(system_prompt, user_prompt, files, diffs, **kwargs):
            """Simulated architecture design function"""
            return {"status": "completed", "components": ["Auth Service", "Token Store"]}

        @require_token_budget(self.hook)
        def plan_implementation(system_prompt, user_prompt, files, **kwargs):
            """Simulated implementation planning function"""
            return {"status": "completed", "tasks": ["Create models", "Implement routes"]}

        # Test decorator enforcement
        result1 = analyze_requirements(
            system_prompt="Analyze auth requirements",
            user_prompt="What do we need for user authentication?",
            files=[{"path": "requirements.md", "content": "Authentication requirements..." * 100}]
        )
        assert result1["status"] == "completed"

        result2 = design_architecture(
            system_prompt="Design auth system",
            user_prompt="Create the architecture",
            files=[{"path": "current.py", "content": "Current system..." * 50}],
            diffs=[{"path": "changes.md", "content": "Proposed changes..." * 30}]
        )
        assert result2["status"] == "completed"

        result3 = plan_implementation(
            system_prompt="Plan implementation",
            user_prompt="Create implementation plan",
            files=[{"path": "plan.md", "content": "Implementation plan..." * 80}]
        )
        assert result3["status"] == "completed"

        # Verify budget history
        summary = self.hook.get_budget_summary()
        assert summary['total_steps'] >= 3
        assert all(status in ['green', 'yellow'] for status in summary['status_distribution'].keys())

    def test_budget_persistence_across_sessions(self):
        """Test budget history persistence across multiple sessions"""
        # Session 1: Add some estimates
        for i in range(5):
            self.hook.preflight_check(
                plan_step=f"session1_step_{i}",
                system_prompt=f"System prompt {i}",
                user_prompt=f"User prompt {i}",
                files=[{"path": f"file_{i}.py", "content": f"content {i}" * 100}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

        summary1 = self.hook.get_budget_summary()
        assert summary1['total_steps'] == 5

        # Simulate session restart - create new hook with same file
        from tools.utils.planning.preflight_hook import PlanningPreflightHook
        new_hook = PlanningPreflightHook(budget_file=self.budget_file)
        summary2 = new_hook.get_budget_summary()

        # Should have persisted the history
        assert summary2['total_steps'] == 5
        assert summary2['average_tokens_per_step'] == summary1['average_tokens_per_step']

        # Session 2: Add more estimates
        for i in range(3):
            new_hook.preflight_check(
                plan_step=f"session2_step_{i}",
                system_prompt=f"New system prompt {i}",
                user_prompt=f"New user prompt {i}",
                files=[{"path": f"new_file_{i}.py", "content": f"new content {i}" * 100}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

        final_summary = new_hook.get_budget_summary()
        assert final_summary['total_steps'] == 8  # 5 + 3

        print(f"Persistence test: {final_summary['total_steps']} steps across sessions")

    def test_concurrent_planning_simulation(self):
        """Test simulated concurrent planning operations"""
        # Simulate multiple planning operations happening concurrently
        operations = []

        for i in range(10):
            estimate = self.hook.preflight_check(
                plan_step=f"concurrent_op_{i}",
                system_prompt=f"Concurrent operation {i}",
                user_prompt=f"Process {i}",
                files=[{"path": f"concurrent_{i}.py", "content": f"content {i}" * 100}],
                diffs=[],
                logs=[],
                retrieved_context=[{"content": f"context_{i}" * 50}],
                prior_steps=[]
            )
            operations.append(estimate)

        # All operations should be recorded
        summary = self.hook.get_budget_summary()
        assert summary['total_steps'] >= 10

        # All estimates should be valid
        for op in operations:
            assert op.total_projected_tokens < 200000
            assert op.status in ['green', 'yellow']

        # Check for any budget violations
        violations = [op for op in operations if op.status == 'red']
        assert len(violations) == 0, f"Found {len(violations)} budget violations"

        print(f"Concurrent operations test: {len(operations)} operations completed successfully")

    def test_extreme_scenario_many_files(self):
        """Test scenario with many files (like a large codebase analysis)"""
        # Simulate analyzing a large codebase with many files
        many_files = []
        for i in range(50):  # 50 files
            content = f"""
# File {i}: Module {i}
class Module{i}:
    def __init__(self):
        self.name = "module_{i}"
        self.version = "1.0.{i}"

    def process(self, data):
        # Processing logic for module {i}
        result = data * i
        return result

    def validate(self, input_data):
        # Validation logic for module {i}
        if not input_data:
            raise ValueError("Input cannot be empty")
        return True

# Utility functions for module {i}
def helper_function_{i}(param):
    return param.upper()

def constant_value_{i}():
    return i * 42
""" * 10  # Multiply to make files larger

            many_files.append({
                "path": f"modules/module_{i}.py",
                "content": content
            })

        # Test with many files
        estimate = self.hook.preflight_check(
            plan_step="large_codebase_analysis",
            system_prompt="You are analyzing a large codebase for refactoring opportunities.",
            user_prompt="Analyze all 50 modules and identify common patterns and refactoring opportunities.",
            files=many_files,
            diffs=[],
            logs=[],
            retrieved_context=[
                {"content": "Code analysis best practices..." * 100},
                {"content": "Refactoring patterns..." * 100}
            ],
            prior_steps=[]
        )

        # Should handle many files gracefully
        assert estimate.total_projected_tokens < 200000
        assert estimate.status in ['green', 'yellow', 'red']

        # Should show files as major contributor
        file_contributors = [c for c in estimate.top_contributors if c['type'] == 'file']
        assert len(file_contributors) > 0

        print(f"Large codebase test: {len(many_files)} files, {estimate.total_projected_tokens:,} tokens")

    def test_memory_efficiency_with_large_history(self):
        """Test memory efficiency with large budget history"""
        # Clear any leftover state from previous tests
        self.hook.clear_history()
        
        # Add many steps to budget history
        for i in range(100):
            self.hook.preflight_check(
                plan_step=f"memory_test_{i}",
                system_prompt=f"Memory test step {i}",
                user_prompt=f"Test prompt {i}",
                files=[{"path": f"test_{i}.py", "content": f"test content {i}" * 50}],
                diffs=[],
                logs=[],
                retrieved_context=[],
                prior_steps=[]
            )

        # Check that history is managed efficiently
        summary = self.hook.get_budget_summary()
        assert summary['total_steps'] == 100

        # Should still be able to compute statistics efficiently
        assert summary['average_tokens_per_step'] > 0
        assert len(summary['status_distribution']) > 0

        # Test history clearing
        self.hook.clear_history()
        cleared_summary = self.hook.get_budget_summary()
        assert cleared_summary['total_steps'] == 0

        print(f"Memory efficiency test: {summary['total_steps']} steps managed efficiently")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
