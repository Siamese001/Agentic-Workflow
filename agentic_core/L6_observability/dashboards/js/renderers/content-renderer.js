/**
 * Content Renderer
 * Renders strategic observations, recommendations, interview questions, and alerts
 */

function renderStrategicObservations() {
    const macroContainer = document.getElementById('macroObservations');
    const metricContainer = document.getElementById('metricObservations');
    
    if (!macroContainer || !metricContainer) return;
    
    const data = window.strategicObservationsData;
    if (!data) {
        console.warn('[renderStrategicObservations] strategicObservationsData not found');
        return;
    }
    
    const macroObs = data.macro_observations || [];
    const metricObs = data.metric_observations || [];
    
    macroContainer.innerHTML = macroObs.length > 0 ? macroObs.map(obs => `
        <div style="padding: 12px; background: white; border-radius: 8px; border-left: 4px solid ${obs.color};">
            <div style="font-weight: 600; margin-bottom: 4px;">${obs.icon} ${obs.title}</div>
            <div style="font-size: 0.9em; color: #475569;">${obs.text}</div>
        </div>
    `).join('') : '<div style="color: #6b7280; font-style: italic;">No macro-level observations at this time.</div>';
    
    metricContainer.innerHTML = metricObs.length > 0 ? metricObs.map(obs => `
        <div style="padding: 12px; background: white; border-radius: 8px; border-left: 4px solid ${obs.color};">
            <div style="font-weight: 600; margin-bottom: 4px;">${obs.icon} ${obs.title}</div>
            <div style="font-size: 0.9em; color: #475569;">${obs.text}</div>
        </div>
    `).join('') : '<div style="color: #6b7280; font-style: italic;">All metrics within target ranges.</div>';
}

function renderRecommendations() {
    const container = document.getElementById('recommendationsList');
    if (!container) return;
    
    const data = window.recommendationsData;
    if (!data || data.length === 0) {
        container.innerHTML = '<div style="color: #6b7280; font-style: italic;">No recommendations available.</div>';
        return;
    }
    
    const html = data.slice(0, 10).map(rec => {
        const priorityColor = rec.priority <= 2 ? '#dc2626' : rec.priority <= 5 ? '#f59e0b' : '#3b82f6';
        const priorityLabel = rec.priority <= 2 ? 'Critical' : rec.priority <= 5 ? 'High' : 'Medium';
        
        return `
            <div style="background: white; padding: 16px; border-radius: 8px; border-left: 4px solid ${priorityColor}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <div style="font-weight: 600; font-size: 1.1em; color: #1e293b;">${rec.title}</div>
                    <span style="background: ${priorityColor}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; font-weight: 600;">P${rec.priority} ${priorityLabel}</span>
                </div>
                <div style="font-size: 0.9em; color: #475569; margin-bottom: 8px;">${rec.description}</div>
                ${rec.file_links && rec.file_links.length > 0 ? `
                    <div style="margin-top: 8px;">
                        <strong style="font-size: 0.85em; color: #64748b;">🔗 Files to update:</strong>
                        <div style="margin-top: 4px; display: flex; flex-wrap: wrap; gap: 6px;">
                            ${rec.file_links.map(link => `
                                <a href="vscode://file/${link}" style="font-size: 0.8em; color: #2563eb; text-decoration: none; background: #eff6ff; padding: 4px 8px; border-radius: 4px; border: 1px solid #bfdbfe;" title="Open in VS Code">${link.split('/').pop()}</a>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

function renderInterviewQuestions(totalRow) {
    const container = document.getElementById('interviewQuestions');
    if (!container) return;
    
    const questions = [
        {
            category: "Architecture",
            question: "How does the healing system work across agents?",
            analogy: "Like a factory where each worker has a personal repair toolkit (HealerMixin) and follows a master safety checklist (heal_repository).",
            key_metric: `Healing Invocation: ${totalRow['Invocation %'].toFixed(1)}%`
        },
        {
            category: "Quality",
            question: "What's your approach to managing code complexity?",
            analogy: "We measure workflow complexity like steps in an assembly line. Target is ≤15 steps (CC). Current average is " + totalRow['Avg CC'].toFixed(1) + ".",
            key_metric: `Avg CC: ${totalRow['Avg CC'].toFixed(1)}`
        },
        {
            category: "Testing",
            question: "How do you ensure agent reliability?",
            analogy: "Each agent has quality control inspections (tests) before deployment. " + totalRow['Test %'].toFixed(0) + "% currently have verification procedures.",
            key_metric: `Test Coverage: ${totalRow['Test %'].toFixed(0)}%`
        },
        {
            category: "Safety",
            question: "How do you secure agent interactions?",
            analogy: "MCP Hardening is like adding safety guards to machinery - MCPShield mixin + @hardened decorators prevent unsafe operations.",
            key_metric: `MCP Hardened: ${totalRow['Hardened %'].toFixed(1)}%`
        },
        {
            category: "Observability",
            question: "How do you monitor agent behavior in production?",
            analogy: "Like factory sensors tracking machine health - structured logging, metrics, and tracing give real-time visibility.",
            key_metric: `Observable: ${totalRow['Observable %'].toFixed(1)}%`
        }
    ];
    
    const html = questions.map((q, idx) => `
        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 4px solid ${idx < 3 ? '#2563eb' : '#64748b'};">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <div>
                    <span style="background: #eff6ff; color: #2563eb; padding: 4px 8px; border-radius: 4px; font-size: 0.75em; font-weight: 600; text-transform: uppercase;">${q.category}</span>
                </div>
                <div style="font-size: 0.9em; color: #64748b; font-weight: 600;">${q.key_metric}</div>
            </div>
            <div style="font-size: 1.1em; font-weight: 600; color: #1e293b; margin-bottom: 8px;">Q: ${q.question}</div>
            <div style="font-size: 0.95em; color: #475569; line-height: 1.6;">
                <strong>Analogy:</strong> ${q.analogy}
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

function updateGlobalAlertBanner(territoryData) {
    // This requires aggregateOutlierAlerts which is a complex function
    // For now, just hide the banner to prevent errors
    const banner = document.getElementById('outlierAlertBanner');
    if (banner) {
        banner.style.display = 'none';
    }
}
