/**
 * Prioritized Recommendations
 * Loaded as global variable for file:// protocol compatibility
 */
window.recommendationsData = [
  {
    "priority": 1,
    "title": "Reduce Cyclomatic Complexity",
    "description": "<span style='color:#666'>17 territories have Avg CC >15 (avg: 38.3)</span><br><b>Action:</b> Refactor complex methods into smaller primitives. Target CC \u226410.<br><span style='color:#059669'><b>Impact:</b> Medium - Reduces bug density and improves testability.</span>",
    "impact": "HIGH",
    "effort": "MEDIUM"
  },
  {
    "priority": 2,
    "title": "Complete Type Annotations",
    "description": "<span style='color:#666'>Current: 95.0% | Gap: 5.0pp</span><br><b>Action:</b> Add type hints to function parameters and return types.<br><span style='color:#059669'><b>Impact:</b> Medium - Enables static analysis and IDE support.</span>",
    "impact": "HIGH",
    "effort": "MEDIUM"
  },
  {
    "priority": 3,
    "title": "Complete Documentation",
    "description": "<span style='color:#666'>Current: 96.9% | Gap: 3.1pp</span><br><b>Action:</b> Add docstrings to all public methods and classes.<br><span style='color:#059669'><b>Impact:</b> Medium - Reduces hallucinated tool usage by constraining search space.</span>",
    "impact": "HIGH",
    "effort": "MEDIUM"
  }
];
