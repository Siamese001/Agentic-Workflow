/**
 * Modal Renderer
 * Handles drill-down views for territories and agents.
 */

function openDrillModal(territory) {
    const modal = document.getElementById('drillModal');
    const title = document.getElementById('modalTitle');
    const subtitle = document.getElementById('modalSubtitle');
    const content = document.getElementById('modalContent');
    
    if (!modal || !title || !content) return;
    
    const agentData = window.realAgentData ? window.realAgentData[territory] : null;
    
    title.textContent = territory;
    subtitle.textContent = agentData ? 
        `${agentData.agents.length} Agents • Comprehensive Diagnostics` : 
        'Territory Details';
    
    if (!agentData || !agentData.agents || agentData.agents.length === 0) {
        content.innerHTML = '<div style="padding:20px; text-align:center; color:#6b7280;">No detailed agent data available for this territory.</div>';
        modal.style.display = 'flex';
        return;
    }
    
    // Build agent details table
    let html = `
        <div style="margin-bottom:15px; display:flex; gap:10px; flex-wrap:wrap;">
            <span style="background:#eff6ff; color:#1e40af; padding:4px 12px; border-radius:16px; font-size:0.85em; border:1px solid #bfdbfe;">
                Avg Complexity: ${computeDistributionStats(agentData.complexityHealth).avg.toFixed(1)}
            </span>
            <span style="background:#f0fdf4; color:#166534; padding:4px 12px; border-radius:16px; font-size:0.85em; border:1px solid #bbf7d0;">
                Avg Health: ${computeDistributionStats(agentData.health).avg.toFixed(1)}%
            </span>
        </div>
        <table style="width:100%; border-collapse:collapse; font-size:0.9em;">
            <thead>
                <tr style="background:#f9fafb; border-bottom:2px solid #e5e7eb;">
                    <th style="text-align:left; padding:10px;">Agent Name</th>
                    <th style="text-align:center; padding:10px;">Health</th>
                    <th style="text-align:center; padding:10px;">Heal Cap</th>
                    <th style="text-align:center; padding:10px;">Tests</th>
                    <th style="text-align:center; padding:10px;">Hardened</th>
                    <th style="text-align:left; padding:10px;">Issues</th>
                </tr>
            </thead>
            <tbody>`;
            
    // Sort agents: Health ascending (worst first)
    const sortedAgents = [...agentData.agents].sort((a, b) => a.health - b.health);
    
    sortedAgents.forEach(agent => {
        const healthColor = getColor(agent.health, true);
        const healCapColor = getColor(agent.healCap, true);
        
        // Identify specific issues
        let issues = [];
        if (agent.healCap < 100) issues.push(`<span style="color:#dc2626">Missing Heal</span>`);
        if (agent.invocation !== 'Yes' && agent.invocation !== 'Inherited') issues.push(`<span style="color:#dc2626">No Invoke</span>`);
        if (agent.test < 100) issues.push(`<span style="color:#f59e0b">Low Tests</span>`);
        if (agent.hardened < 100) issues.push(`<span style="color:#f59e0b">Unsafe</span>`);
        if (agent.complexityHealth < 50) issues.push(`<span style="color:#dc2626">Complex (${agent.complexity})</span>`);
        
        html += `
            <tr style="border-bottom:1px solid #e5e7eb;">
                <td style="padding:10px;">
                    <div style="font-weight:600; color:#374151;">${agent.name}</div>
                    <a href="vscode://file/${agent.abs_file}" style="font-size:0.85em; color:#2563eb; text-decoration:none; font-family:monospace;">
                        ${agent.rel}
                    </a>
                </td>
                <td style="padding:10px; text-align:center; font-weight:700; color:${healthColor};">
                    ${agent.health.toFixed(1)}%
                </td>
                <td style="padding:10px; text-align:center; color:${healCapColor};">
                    ${agent.healCap.toFixed(0)}%
                </td>
                <td style="padding:10px; text-align:center;">
                    ${agent.test.toFixed(0)}%
                </td>
                <td style="padding:10px; text-align:center;">
                    ${agent.hardened.toFixed(0)}%
                </td>
                <td style="padding:10px;">
                    ${issues.length > 0 ? issues.join(' • ') : '<span style="color:#16a34a">✓ Healthy</span>'}
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    content.innerHTML = html;
    modal.style.display = 'flex';
}

function formatProblemAgentsTooltip(territory, metricKey, metricName, threshold) {
    const agentData = window.realAgentData ? window.realAgentData[territory] : null;
    if (!agentData || !agentData.agents) return 'No agent data';
    
    // Find agents causing the drag
    const problems = agentData.agents.filter(a => {
        const val = a[metricKey]; // e.g. a.healCap
        return typeof val === 'number' && val < threshold;
    }).map(a => ({
        name: a.name,
        value: a[metricKey],
        path: a.rel
    })).sort((a, b) => a.value - b.value); // Worst first
    
    if (problems.length === 0) return 'All agents healthy';
    
    let tooltip = `<strong>${metricName} Issues:</strong>\n`;
    
    // Calculate remediation effort
    const criticalCount = problems.filter(p => p.value === 0).length;
    const warningCount = problems.length - criticalCount;
    const avgDeficit = problems.reduce((sum, p) => sum + (threshold - p.value), 0) / problems.length;
    
    tooltip += `\n⚠️ ${problems.length} agent(s) below ${threshold}% threshold\n`;
    if (criticalCount > 0) {
        tooltip += `🔴 Critical (0%): ${criticalCount} | `;
    }
    tooltip += `🟡 Warning: ${warningCount}\n`;
    tooltip += `Avg deficit: ${avgDeficit.toFixed(1)} points to threshold\n`;
    tooltip += `\n🔧 TOP REMEDIATION TARGETS:\n`;
    
    const topProblems = problems.slice(0, 3);
    topProblems.forEach((p, idx) => {
        const shortPath = p.path ? p.path.split('/').slice(-2).join('/') : 'path unknown';
        tooltip += `${idx + 1}. ${p.name} (${p.value.toFixed(0)}%) → ${shortPath}\n`;
    });
    
    if (problems.length > 3) {
        tooltip += `   ... +${problems.length - 3} more agents need attention`;
    }
    
    return tooltip;
}
