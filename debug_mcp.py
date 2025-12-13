"""Debug MCP server connection issues."""

import asyncio
import subprocess
import sys

async def test_mcp_directly():
    """Test MCP servers directly with subprocess to see errors."""
    
    servers = [
        {
            "name": "filesystem",
            "cmd": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "./output", "./logs", "./project_knowledge"],
            "timeout": 30
        },
        {
            "name": "browser", 
            "cmd": ["npx", "-y", "@modelcontextprotocol/server-puppeteer"],
            "timeout": 30
        }
    ]
    
    for server in servers:
        print(f"\n🔍 Testing {server['name']} server...")
        print(f"Command: {' '.join(server['cmd'])}")
        
        try:
            # Run with timeout to prevent hanging
            process = await asyncio.create_subprocess_exec(
                *server['cmd'],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="c:/Git/Agentic-Workflow"
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=server['timeout']
                )
                
                print(f"Exit code: {process.returncode}")
                
                if stdout:
                    print(f"STDOUT:\n{stdout.decode()}")
                if stderr:
                    print(f"STDERR:\n{stderr.decode()}")
                    
            except asyncio.TimeoutError:
                print("⏰ Server timed out - this might be normal (MCP servers wait for stdin)")
                process.terminate()
                await process.wait()
                
        except Exception as e:
            print(f"❌ Failed to start {server['name']}: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_directly())
