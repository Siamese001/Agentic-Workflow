"""
Usage Examples for Agentic Core Tools
Demonstrates integration with Gemini 2.5/3.0 and AtomicBlackboard.
"""

import os

from agentic_core.tools import (
    create_tool_registry,
    ReadFileArgs,
    WriteFileArgs,
    ExecuteCommandArgs,
    read_file,
    write_file,
    execute_command,
)


def example_basic_file_operations():
    """Example: Basic file operations with sandbox validation."""
    print("=== Basic File Operations ===\n")
    
    try:
        content = read_file(ReadFileArgs(path="apps_shared/canon_validator_v2_agentic.py"))
        print(f"✅ Read file: {len(content)} characters")
    except Exception as e:
        print(f"❌ Read failed: {e}")
    
    try:
        write_file(
            WriteFileArgs(
                path="output/example.txt",
                content="Hello from sandboxed filesystem!",
                create_dirs=True
            )
        )
        print("✅ Write file: output/example.txt")
    except Exception as e:
        print(f"❌ Write failed: {e}")


def example_sandbox_violations():
    """Example: Sandbox violations are caught and prevented."""
    print("\n=== Sandbox Violation Examples ===\n")
    
    try:
        read_file(ReadFileArgs(path="../../../etc/passwd"))
        print("❌ Should have blocked path traversal!")
    except Exception as e:
        print(f"✅ Blocked path traversal: {type(e).__name__}")
    
    try:
        read_file(ReadFileArgs(path=".git/config"))
        print("❌ Should have blocked .git access!")
    except Exception as e:
        print(f"✅ Blocked .git access: {type(e).__name__}")
    
    try:
        read_file(ReadFileArgs(path="archives/old_code.py"))
        print("❌ Should have blocked archives access!")
    except Exception as e:
        print(f"✅ Blocked archives access: {type(e).__name__}")


def example_subprocess_execution():
    """Example: Timeout-protected subprocess execution."""
    print("\n=== Subprocess Execution ===\n")
    
    try:
        returncode, stdout, stderr = execute_command(
            ExecuteCommandArgs(
                command="python",
                args=["--version"],
                timeout=5
            )
        )
        print(f"✅ Python version: {stdout.strip()}")
    except Exception as e:
        print(f"❌ Command failed: {e}")


def example_gemini_integration():
    """Example: Integration with Gemini 2.5/3.0 using FunctionDeclarations."""
    print("\n=== Gemini Integration ===\n")
    
    try:
        from google import genai
        from google.genai import types
        
        registry = create_tool_registry()
        tools = registry.get_function_declarations()
        
        print(f"✅ Registered {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
        
        if not os.getenv("GOOGLE_API_KEY"):
            print("\n⚠️  Set GOOGLE_API_KEY to test Gemini integration")
            return
        
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        
        config = types.GenerateContentConfig(
            temperature=0.2,
            tools=tools
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="List the Python files in the apps_shared directory",
            config=config
        )
        
        if response.candidates[0].content.parts[0].function_call:
            call = response.candidates[0].content.parts[0].function_call
            print(f"\n✅ Gemini called tool: {call.name}")
            print(f"   Arguments: {dict(call.args)}")
            
            result = registry.execute_tool(
                name=call.name,
                args=dict(call.args)
            )
            print(f"   Result: {result[:100]}..." if isinstance(result, str) else f"   Result: {result}")
        else:
            print(f"\n✅ Gemini response: {response.text}")
    
    except ImportError:
        print("❌ google-genai not installed. Run: pip install google-genai")
    except Exception as e:
        print(f"❌ Gemini integration failed: {e}")


def example_healing_lease_integration():
    """Example: HealingLease integration with AtomicBlackboard."""
    print("\n=== HealingLease Integration ===\n")
    
    try:
        from agentic_core.L4_state.atomic_blackboard import AtomicBlackboard
        
        blackboard = AtomicBlackboard()
        agent_id = "healer_agent_001"
        file_path = "output/healed_file.py"
        
        blackboard.acquire_healing_lease(agent_id, file_path)
        print(f"✅ Acquired HealingLease: {agent_id} -> {file_path}")
        
        write_file(
            WriteFileArgs(
                path=file_path,
                content="# Healed code\nprint('Hello, World!')",
                create_dirs=True
            ),
            blackboard=blackboard,
            agent_id=agent_id
        )
        print(f"✅ Write verified with HealingLease")
        
        blackboard.release_healing_lease(agent_id, file_path)
        print(f"✅ Released HealingLease")
        
        try:
            write_file(
                WriteFileArgs(path=file_path, content="# Unauthorized"),
                blackboard=blackboard,
                agent_id="unauthorized_agent"
            )
            print("❌ Should have blocked unauthorized write!")
        except Exception as e:
            print(f"✅ Blocked unauthorized write: {type(e).__name__}")
    
    except ImportError:
        print("⚠️  AtomicBlackboard not available (Phase 2 not implemented)")
    except Exception as e:
        print(f"❌ HealingLease integration failed: {e}")


def example_tool_registry_custom():
    """Example: Register custom tools with the registry."""
    print("\n=== Custom Tool Registration ===\n")
    
    from pydantic import BaseModel, Field
    
    class CustomToolArgs(BaseModel):
        message: str = Field(..., description="Message to process")
    
    def custom_tool(args: CustomToolArgs) -> str:
        return f"Processed: {args.message.upper()}"
    
    registry = create_tool_registry()
    
    registry.register_tool(
        name="custom_tool",
        description="A custom tool that processes messages",
        args_model=CustomToolArgs,
        function=custom_tool
    )
    
    print(f"✅ Registered custom tool")
    print(f"   Total tools: {len(registry.get_tool_names())}")
    
    result = registry.execute_tool(
        name="custom_tool",
        args={"message": "hello world"}
    )
    print(f"   Result: {result}")


if __name__ == "__main__":
    print("Agentic Core Tools - Usage Examples\n")
    print("=" * 60)
    
    example_basic_file_operations()
    example_sandbox_violations()
    example_subprocess_execution()
    example_gemini_integration()
    example_healing_lease_integration()
    example_tool_registry_custom()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
