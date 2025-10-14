#!/usr/bin/env python3
"""
Insurance Agent Definition for NL2SQL
This agent specifically handles insurance sales data queries.
"""

import os
import subprocess
import warnings
import yaml

import vertexai
from google.adk.agents import Agent
from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
import google.auth
from loguru import logger
from sqlalchemy.exc import SAWarning


def setup_environment(config_path: str = "config_insurance.yaml"):
    """Setup Google Cloud environment."""
    # Suppress warnings
    warnings.filterwarnings("ignore", category=SAWarning)

    # Load config - handle both relative and absolute paths
    from pathlib import Path

    config_file = Path(config_path)

    # If not found, try parent directory (for ADK web server)
    if not config_file.exists():
        config_file = Path(__file__).parent.parent / config_path

    # If still not found, try current working directory
    if not config_file.exists():
        config_file = Path.cwd() / config_path

    if not config_file.exists():
        raise FileNotFoundError(
            f"config_insurance.yaml not found. Searched in: {config_path}, "
            f"{Path(__file__).parent.parent / config_path}, "
            f"{Path.cwd() / config_path}"
        )

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # Get project ID
    project_id = config.get('project_id')
    if not project_id or project_id == "your-project-id":
        try:
            result = subprocess.run(
                ['gcloud', 'config', 'get-value', 'core/project'],
                capture_output=True,
                text=True,
                check=True
            )
            project_id = result.stdout.strip()
        except:
            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

    # Get location
    location = config.get('location', 'us-central1')

    # Set environment variables
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    os.environ["GOOGLE_CLOUD_LOCATION"] = location
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"

    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)

    # Disable nl2sql logger
    try:
        logger.disable("nl2sql")
    except:
        pass

    print(f"✓ Project ID: {project_id}")
    print(f"✓ Location: {location}")

    return config


def create_bigquery_toolset(config: dict):
    """Create BigQuery toolset."""
    write_mode_str = config['bigquery'].get('write_mode', 'BLOCKED')
    write_mode = WriteMode.BLOCKED if write_mode_str == "BLOCKED" else WriteMode.ALLOWED

    # Tool configuration
    tool_config = BigQueryToolConfig(write_mode=write_mode)

    # Get application default credentials
    application_default_credentials, _ = google.auth.default()
    credentials_config = BigQueryCredentialsConfig(
        credentials=application_default_credentials
    )

    # Instantiate BigQuery toolset
    bigquery_toolset = BigQueryToolset(
        credentials_config=credentials_config,
        bigquery_tool_config=tool_config
    )

    return bigquery_toolset


# Setup environment and configuration
config = setup_environment()

# Create BigQuery toolset
bigquery_toolset = create_bigquery_toolset(config)

# Extract configuration values
bq_table = config['bigquery']['table']
agent_name = config['agent']['name']
model_name = config['agent']['model']
agent_description = config['agent']['description']

# Define the root agent for insurance data
root_agent = Agent(
    model=model_name,
    name=agent_name,
    description=agent_description,
    instruction=f"""
    You are an insurance sales data analyst with access to BigQuery tools.

    Your primary focus is the insurance sales ledger table: {bq_table}

    This table contains insurance policy sales data including:
    - Agent information (name, license, office location, manager)
    - Customer demographics (age, gender, postal code, smoker status)
    - Product details (product name, type, subtype)
    - Financial data (premiums, payment frequency, commission)
    - Policy status (Active, Lapsed, Cancelled)

    When answering questions:
    1. Understand the user's question about insurance sales, agents, customers, or products
    2. Use the BigQuery tools to explore the table schema if needed
    3. Generate appropriate SQL queries to answer the question
    4. Provide clear insights with relevant metrics and trends
    5. For financial questions, always format currency appropriately

    Always use the BigQuery tools available to you to answer questions accurately.
    """,
    tools=[bigquery_toolset],
)

print(f"✓ Insurance agent created: {agent_name}")
print(f"✓ Model: {model_name}")
print(f"✓ Target table: {bq_table}")
