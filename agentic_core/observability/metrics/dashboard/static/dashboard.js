// SSOT-derived high-signal category registry
// Directly from structure_blueprint.py semantic layer definitions
const CATEGORY_MAP = {
    "L0_maintenance": {
        full: "L0 Maintenance",
        description: "System maintenance, scripts, logs, benchmarks, and infrastructure utilities.",
        color: "#999999"
    },
    "L1_cognition": {
        full: "L1 Cognition",
        description: "Core reasoning primitives: thought engine, intent analysis, planning, decomposition, reflection, and advanced deliberation patterns.",
        color: "var(--color-l1)"
    },
    "L2_execution": {
        full: "L2 Execution",
        description: "Tool registry, action handlers, MCP clients (fetch, filesystem, SemanticCache, router). External capability execution.",
        color: "var(--color-l2)"
    },
    "L3_orchestration": {
        full: "L3 Orchestration",
        description: "Workflow engines, fission logic, vitality monitoring, multi-agent coordination, mission routing, and supervisor patterns.",
        color: "var(--color-l3)"
    },
    "L4_state": {
        full: "L4 State",
        description: "Validation contexts, immutable ledgers, memory stores, filesystem persistence, and runtime state integrity.",
        color: "var(--color-l4)"
    },
    "L5_safety": {
        full: "L5 Safety",
        description: "Guardrails, validators, gravity enforcement, red teaming, healing agents, and constitutional compliance.",
        color: "var(--color-l5)"
    },
    "config": {
        full: "Configuration",
        description: "Blueprint sovereign, environments, feature flags, and secrets management.",
        color: "var(--color-utils)"
    },
    "schemas": {
        full: "Schemas",
        description: "Data models, message types, validators, and type definitions.",
        color: "var(--color-utils)"
    },
    "prompt_governance": {
        full: "Prompt Governance",
        description: "Meta-prompts, version registry, rendering, and prompt templates.",
        color: "var(--color-utils)"
    },
    "observability": {
        full: "Observability",
        description: "Metrics, tracing, telemetry, compliance reporting, and system health monitoring.",
        color: "var(--color-utils)"
    },
    "utils": {
        full: "Core Utilities",
        description: "Naming, extensions, wrappers, and general helpers.",
        color: "var(--color-utils)"
    },
    "patterns": {
        full: "Patterns",
        description: "Agent roles, communication flow, interaction patterns, and reasoning patterns.",
        color: "var(--color-utils)"
    },
    "semantic_memory": {
        full: "Semantic Memory",
        description: "Vector store, embeddings, retrieval, and semantic indexing.",
        color: "var(--color-utils)"
    },
    "knowledge": {
        full: "Knowledge",
        description: "Document loaders, static index, and research cache.",
        color: "var(--color-utils)"
    },
    "runtime": {
        full: "Runtime",
        description: "Shared runtime, environment setup, and resource management.",
        color: "var(--color-utils)"
    },
    "apps_rg": {
        full: "Apps: Resume Generation",
        description: "Domain-specific logic nodes, engines, templates, and flows for resume parsing and document generation.",
        color: "var(--color-apps)"
    },
    "apps_lic": {
        full: "Apps: LinkedIn Connector",
        description: "Outreach automation, browser drivers, campaign flows, and message generation for LinkedIn interactions.",
        color: "var(--color-apps)"
    },
    "apps_shared": {
        full: "Apps: Shared Base",
        description: "Cross-app base definitions, common utils, core components, and shared agent templates.",
        color: "var(--color-apps)"
    }
};

let chartInstance = null;

async function loadDashboard() {
    try {
        const response = await fetch('/api/metrics');
        if (!response.ok) {
            throw new Error(`API returned ${response.status}`);
        }

        const data = await response.json();
        const counts = data.layer_counts || {};

        // Transform raw keys to high-signal
        const labels = [];
        const values = [];
        const backgroundColors = [];
        let glossaryHTML = '';
        let total = 0;

        // Sort by activation count (descending) for better visualization
        const sortedEntries = Object.entries(counts).sort((a, b) => b[1] - a[1]);

        sortedEntries.forEach(([key, value]) => {
            const cat = CATEGORY_MAP[key] || {
                full: key.replace(/_/g, ' ').toUpperCase(),
                description: "Unknown territory (add to CATEGORY_MAP for proper documentation)",
                color: "#cccccc"
            };

            labels.push(cat.full);
            values.push(value);
            backgroundColors.push(cat.color);
            total += value;
        });

        // Compute Shannon entropy (base-2, didactic interpretation)
        const proportions = values.map(v => total > 0 ? v / total : 0);
        const entropy = proportions.reduce((acc, p) => {
            return p > 0 ? acc - p * Math.log2(p) : acc;
        }, 0);

        const maxEntropy = Math.log2(labels.length || 1);
        const entropyPercent = maxEntropy > 0 ? ((entropy / maxEntropy) * 100).toFixed(1) : 0;

        // Determine health color based on entropy
        let healthColor = '#991b1b'; // Red - poor coverage
        let healthLabel = 'Poor Coverage';
        if (entropyPercent > 70) {
            healthColor = '#065f46'; // Green - excellent
            healthLabel = 'Excellent Coverage';
        } else if (entropyPercent > 50) {
            healthColor = '#65a30d'; // Yellow-green - good
            healthLabel = 'Good Coverage';
        } else if (entropyPercent > 30) {
            healthColor = '#a16207'; // Orange - fair
            healthLabel = 'Fair Coverage';
        }

        // Update entropy display
        const entropyDisplay = document.getElementById('entropy-display');
        const entropyContent = `
            <div style="color: ${healthColor}; font-weight: bold; font-size: 1.2em;">
                ${healthLabel}: ${entropy.toFixed(2)} / ${maxEntropy.toFixed(2)} bits (${entropyPercent}% of maximum)
            </div>
            <small style="color: #666; margin-top: 10px; display: block;">
                <strong>What this means:</strong> Higher entropy = better layer exploration and balanced system health. 
                Low entropy = over-reliance on few territories (potential bottleneck). 
                Ideal: >70% for healthy autonomous system.
            </small>
        `;
        entropyDisplay.innerHTML = entropyContent;
        entropyDisplay.style.borderLeftColor = healthColor;

        // Generate recommendations based on entropy and coverage
        const recommendations = [];
        
        if (entropyPercent < 30) {
            const underrepresented = sortedEntries[sortedEntries.length - 1];
            recommendations.push(`⚠️ Critical: Imbalance detected. Prioritize ${CATEGORY_MAP[underrepresented[0]]?.full || underrepresented[0]} territory (${underrepresented[1]} activations)`);
            recommendations.push(`Increase coverage: Current entropy ${entropyPercent}% is below healthy threshold (>70%)`);
        } else if (entropyPercent < 50) {
            const underrepresented = sortedEntries[sortedEntries.length - 1];
            recommendations.push(`⚠️ Fair coverage: Consider expanding ${CATEGORY_MAP[underrepresented[0]]?.full || underrepresented[0]} territory`);
            recommendations.push(`Target entropy >70% for optimal system balance`);
        } else if (entropyPercent < 70) {
            recommendations.push(`✓ Good coverage: Continue monitoring layer distribution`);
            recommendations.push(`Maintain entropy >70% for sustained autonomous system health`);
        } else {
            recommendations.push(`✓ Excellent coverage: System entropy is well-balanced`);
            recommendations.push(`Continue monitoring to maintain healthy layer exploration`);
        }

        // Add general recommendations
        recommendations.push(`Monitor ${labels.length} territories for activation patterns`);
        recommendations.push(`Use CoverageAgent to detect and correct imbalances automatically`);

        // Populate recommendations list
        const recommendationsList = document.getElementById('recommendations-list');
        recommendationsList.innerHTML = recommendations
            .map(rec => `<li>${rec}</li>`)
            .join('');
        
        // Show recommendations section
        const recommendationsDiv = document.getElementById('recommendations');
        if (recommendations.length > 0) {
            recommendationsDiv.style.display = 'block';
        }

        // Build glossary with live percentages
        glossaryHTML = '<div>';
        sortedEntries.forEach(([key, value]) => {
            const cat = CATEGORY_MAP[key] || {
                full: key.replace(/_/g, ' ').toUpperCase(),
                description: "Unknown territory",
                color: "#cccccc"
            };

            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;

            glossaryHTML += `
                <div class="glossary-item" style="border-left-color: ${cat.color};">
                    <strong>${cat.full}</strong><br>
                    <small>${cat.description}</small><br>
                    <em>Activations: ${value} (${percentage}% of total)</em>
                </div>`;
        });
        glossaryHTML += '</div>';

        document.getElementById('glossary-content').innerHTML = glossaryHTML || '<p>No data available</p>';

        // Create or update chart
        const ctx = document.getElementById('coverageChart').getContext('2d');

        // Destroy existing chart if it exists
        if (chartInstance) {
            chartInstance.destroy();
        }

        chartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: backgroundColors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            title: (context) => {
                                return context[0].label;
                            },
                            label: (context) => {
                                const value = context.parsed;
                                const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return `Activations: ${value} (${percentage}%)`;
                            },
                            afterLabel: (context) => {
                                const label = context.label;
                                const cat = Object.values(CATEGORY_MAP).find(c => c.full === label);
                                return cat ? cat.description : "No description available";
                            }
                        },
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: {
                            size: 13,
                            weight: 'bold'
                        },
                        bodyFont: {
                            size: 12
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error loading dashboard:', error);
        document.getElementById('entropy-display').innerHTML = `
            <div class="error">
                <strong>Error loading dashboard:</strong> ${error.message}
            </div>
        `;
        document.getElementById('glossary-content').innerHTML = `
            <div class="error">
                Failed to load metrics. Please check the server is running.
            </div>
        `;
    }
}

// Load dashboard on page load
document.addEventListener('DOMContentLoaded', loadDashboard);

// Refresh every 30 seconds
setInterval(loadDashboard, 30000);
