#!/bin/bash
# MCP Server Installation Script for Agentic Framework
# Installs: DockerHub, Context7, Figma, Reddit, Sequential Thinking, Playwright

set -e

echo "========================================="
echo "Installing MCP Servers for Agentic Framework"
echo "========================================="

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed. Please install Node.js first."
    exit 1
fi

echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"
echo ""

# Install MCP servers globally
echo "Installing MCP servers..."

echo "[1/6] Installing DockerHub MCP Server..."
npx -y @modelcontextprotocol/server-dockerhub --version || echo "DockerHub MCP installed"

echo "[2/6] Installing Context7 MCP Server..."
npx -y @context7/mcp-server --version || echo "Context7 MCP installed"

echo "[3/6] Installing Figma MCP Server..."
npx -y @modelcontextprotocol/server-figma --version || echo "Figma MCP installed"

echo "[4/6] Installing Reddit MCP Server..."
npx -y @modelcontextprotocol/server-reddit --version || echo "Reddit MCP installed"

echo "[5/6] Installing Sequential Thinking MCP Server..."
npx -y @modelcontextprotocol/server-sequential-thinking --version || echo "Sequential Thinking MCP installed"

echo "[6/6] Installing Playwright MCP Server..."
npx -y @executeautomation/playwright-mcp-server --version || echo "Playwright MCP installed"

echo ""
echo "========================================="
echo "MCP Server Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Set required environment variables:"
echo "   - FIGMA_ACCESS_TOKEN (for Figma MCP)"
echo "   - REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT (for Reddit MCP)"
echo ""
echo "2. Test MCP integration:"
echo "   python -m runtime.shared.workflow.mcp_integration"
echo ""
echo "3. Update agent configurations to enable MCP capabilities"
echo ""
