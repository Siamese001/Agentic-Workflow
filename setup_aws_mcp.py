#!/usr/bin/env python3
"""
Setup script for AWS MCP server configuration.
This script helps configure AWS credentials and MCP server settings.
"""

import os
import json
import sys
from pathlib import Path


def setup_aws_credentials():
    """Setup AWS credentials file."""
    aws_dir = Path.home() / ".aws"
    aws_dir.mkdir(exist_ok=True)
    
    credentials_file = aws_dir / "credentials"
    config_file = aws_dir / "config"
    
    print("\n=== AWS Credentials Setup ===")
    print("Please enter your AWS credentials:")
    
    access_key = input("AWS Access Key ID: ").strip()
    secret_key = input("AWS Secret Access Key: ").strip()
    region = input("Default Region (us-east-1): ").strip() or "us-east-1"
    
    # Write credentials
    if not credentials_file.exists():
        credentials_content = f"""[default]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}

[profile mcp]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}
region = {region}
"""
        credentials_file.write_text(credentials_content)
        print(f"✓ Created credentials file: {credentials_file}")
    else:
        print(f"⚠ Credentials file already exists: {credentials_file}")
        overwrite = input("Overwrite? (y/N): ").strip().lower()
        if overwrite == 'y':
            credentials_content = f"""[default]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}

[profile mcp]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}
region = {region}
"""
            credentials_file.write_text(credentials_content)
            print("✓ Updated credentials file")
    
    # Write config
    if not config_file.exists():
        config_content = f"""[default]
region = {region}
output = json

[profile mcp]
region = {region}
output = json
"""
        config_file.write_text(config_content)
        print(f"✓ Created config file: {config_file}")
    else:
        print(f"⚠ Config file already exists: {config_file}")
    
    return True


def setup_mcp_config():
    """Setup MCP configuration for AWS."""
    print("\n=== MCP Configuration Setup ===")
    
    # Create MCP config in the project directory
    project_root = Path(__file__).parent
    mcp_config_file = project_root / "mcp-aws-config.json"
    
    mcp_config = {
        "mcpServers": {
            "aws": {
                "command": "python",
                "args": ["-m", "mcp_server_aws"],
                "env": {
                    "AWS_PROFILE": "mcp",
                    "AWS_REGION": "us-east-1"
                }
            }
        }
    }
    
    mcp_config_file.write_text(json.dumps(mcp_config, indent=2))
    print(f"✓ Created MCP config: {mcp_config_file}")
    
    return True


def test_aws_connection():
    """Test AWS connection."""
    print("\n=== Testing AWS Connection ===")
    
    import subprocess
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity", "--profile", "mcp"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✓ AWS connection successful!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ AWS connection failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("✗ AWS CLI not found. Please install it with: pip install awscli")
        return False


def main():
    """Main setup function."""
    print("AWS MCP Server Setup")
    print("=" * 50)
    
    # Check if required packages are installed
    try:
        import mcp_server_aws
        print("✓ mcp-server-aws is installed")
    except ImportError:
        print("✗ mcp-server-aws not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp-server-aws"])
    
    # Setup AWS credentials
    setup_aws_credentials()
    
    # Setup MCP configuration
    setup_mcp_config()
    
    # Test connection
    test_aws_connection()
    
    print("\n=== Setup Complete ===")
    print("Next steps:")
    print("1. Update your IDE's MCP settings to use the mcp-aws-config.json file")
    print("2. Restart your IDE to load the AWS MCP server")
    print("3. You can now use AWS services through MCP")


if __name__ == "__main__":
    main()
