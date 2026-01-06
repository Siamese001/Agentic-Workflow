# PowerShell script to update MCP configuration
# Run this as administrator

$configPath = "$env:APPDATA\Windsurf\config\mcp_config.json"

# Create the new configuration
$newConfig = @{
    mcpServers = @{
        filesystem = @{
            command = "npx"
            args = @("-y", "@modelcontextprotocol/server-filesystem")
            env = @{
                ALLOWED_DIRECTORIES = @("c:\\Git\\Agentic-Workflow")
            }
        }
    }
}

# Convert to JSON and write to file
$jsonContent = $newConfig | ConvertTo-Json -Depth 10
$jsonContent | Out-File -FilePath $configPath -Encoding UTF8

Write-Host "MCP config updated successfully"
Write-Host "Please restart Windsurf for changes to take effect"
