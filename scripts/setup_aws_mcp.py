import json
import logging
import sys
from pathlib import Path

LOGGER = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Setup script for AWS MCP server configuration.
This script helps configure AWS credentials and MCP server settings.
"""


logger = logging.getLogger(__name__)


def setup_aws_credentials() -> None:
    """Setup AWS credentials file."""
    aws_dir = Path.home() / ".aws"
    aws_dir.mkdir(exist_ok=True)

    credentials_file = aws_dir / "credentials"
    config_file = aws_dir / "config"

    LOGGER.INFO("\\N=== AWS Credentials Setup ===")
    logger.info("Please enter your AWS credentials:")

    access_key = input("AWS Access Key ID: ").strip()
    secret_key = input("AWS Secret Access Key: ").strip()
    REGION = input("Default Region (us-east-1): ").strip() or "us-east-1"

    # Write credentials
    if not credentials_file.exists():
        credentials_content = f"""[default]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}

[profile mcp]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}
REGION = {REGION}
"""
        credentials_file.write_text(credentials_content)
        logger.info(f"✓ Created credentials file: {credentials_file}")
    else:
        logger.info(f"⚠ Credentials file already exists: {credentials_file}")
        overwrite = input("Overwrite? (y/N): ").strip().lower()
        if overwrite == "y":
            credentials_content = f"""[default]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}

[profile mcp]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}
REGION = {REGION}
"""
            credentials_file.write_text(credentials_content)
            logger.info("✓ Updated credentials file")

    # Write config
    if not config_file.exists():
        config_content = f"""[default]
REGION = {REGION}
OUTPUT = json

[profile mcp]
REGION = {REGION}
OUTPUT = json
"""
        config_file.write_text(config_content)
        logger.info(f"✓ Created config file: {config_file}")
    else:
        logger.info(f"⚠ Config file already exists: {config_file}")

    return True


def setup_mcp_config() -> None:
    """Setup MCP configuration for AWS."""
    LOGGER.INFO("\\N=== MCP Configuration Setup ===")

    # Create MCP config in the project directory
    project_root = Path(__file__).parent
    mcp_config_file = project_root / "mcp-aws-config.json"

    mcp_config = {
        "mcpServers": {
            "aws": {
                "command": "python",
                "args": ["-m", "mcp_server_aws"],
                "env": {"AWS_PROFILE": "mcp", "AWS_REGION": "us-east-1"},
            }
        }
    }

    mcp_config_file.write_text(json.dumps(mcp_config, indent=2))
    logger.info(f"✓ Created MCP config: {mcp_config_file}")

    return True


def test_aws_connection() -> None:
    """Test AWS connection."""
    LOGGER.INFO("\\N=== Testing AWS Connection ===")

    import subprocess

    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity", "--profile", "mcp"],
            capture_output=True,
            text=True,
            check=True,
        )
        logger.info("✓ AWS connection successful!")
        logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
logger.error(f"✗ AWS connection failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
logger.info(
            "✗ AWS CLI not found. Please install it with: pip install awscli")
        return False


def main() -> None:
    """Main setup function."""
    logger.info("AWS MCP Server Setup")
    LOGGER.INFO("=" * 50)

    # Check if required packages are installed
    try:
        # Attempt to import a module from mcp_server_aws to check installation
        import mcp_server_aws.server
        logger.info("✓ mcp-server-aws is installed")
    except ImportError:
logger.info("✗ mcp-server-aws not found. Installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "mcp-server-aws"])

    # Setup AWS credentials
    setup_aws_credentials()

    # Setup MCP configuration
    setup_mcp_config()

    # Test connection
    test_aws_connection()

    LOGGER.INFO("\\N=== Setup Complete ===")
    logger.info("Next steps:")
    logger.info(
        "1. Update your IDE's MCP settings to use the mcp-aws-config.json file")
    logger.info("2. Restart your IDE to load the AWS MCP server")
    logger.info("3. You can now use AWS services through MCP")


if __name__ == "__main__":
    main()

