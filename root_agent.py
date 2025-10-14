#!/usr/bin/env python3
"""
Root Agent Definition for NL2SQL BigQuery Agent
This file defines the agent in root_agent format for easy deployment to Agent Engine.
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
from toolbox_core import ToolboxSyncClient


def setup_environment(config_path: str = "config.yaml"):
    """Setup Google Cloud environment."""
    # Suppress warnings
    warnings.filterwarnings("ignore", category=SAWarning)

    # Load config
    with open(config_path, 'r') as f:
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
#     bigquery_toolset = BigQueryToolset(
#         credentials_config=credentials_config,
#         bigquery_tool_config=tool_config
        
#     )
    bigquery_toolset = BigQueryToolset(
        credentials_config=credentials_config, bigquery_tool_config=tool_config, tool_filter=['ask_data_insights','forecast']
    )
    return bigquery_toolset


# Setup environment and configuration
config = setup_environment()

# Create BigQuery toolset
bigquery_toolset = create_bigquery_toolset(config)


# Instantiate a Toolbox toolset. Only forecasting tool used. Make sure the Toolbox MCP server is already running locally. You can learn more at this codelab
toolbox = ToolboxSyncClient("http://127.0.0.1:5000")
mcp_tools = toolbox.load_toolset('bq-mcp-toolset')



# Extract configuration values
bq_table = config['bigquery']['table']
agent_name = config['agent']['name']
model_name = config['agent']['model']
agent_description = config['agent']['description']

# Define the root agent (in the format expected by Agent Engine)
root_agent = Agent(
    model=model_name,
    name=agent_name,
    description=agent_description,
    instruction=f"""
    You are a data analysis assistant with access to BigQuery tools.

    Your primary focus is this data table: {bq_table}

    When answering questions:
    1. First, understand the user's question and what data they need
    2. Use the BigQuery tools to explore the table schema and understand the data structure
    3. Generate and execute appropriate SQL queries to answer the question
    4. Provide clear, concise answers based on the query results
    5. If you encounter any issues, explain them clearly to the user

    Always use the BigQuery tools available to you to answer questions accurately.
    """,
    tools=mcp_tools+[bigquery_toolset],
    # tools=[bigquery_toolset],

)

print(f"✓ Root agent created: {agent_name}")
print(f"✓ Model: {model_name}")
print(f"✓ Target table: {bq_table}")


# Usage examples (can be commented out for deployment):
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test NL2SQL Root Agent")
    parser.add_argument(
        "--question",
        type=str,
        default="What columns are in the census data table?",
        help="Question to ask the agent"
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default="test_user",
        help="User ID for the session"
    )

    args = parser.parse_args()

    print("\n" + "="*80)
    print("Root Agent Definition Loaded")
    print("="*80)
    print(f"\nAgent Name: {root_agent.name}")
    print(f"Model: {root_agent.model}")
    print(f"Description: {root_agent.description}")

    # Test the agent locally
    print("\n" + "="*80)
    print("Testing Agent Locally")
    print("="*80 + "\n")

    from vertexai.preview import reasoning_engines

    # Create local app
    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    # Create session
    session = app.create_session(user_id=args.user_id)
    print(f"Session created: {session.id}\n")

    # Test question
    test_question = args.question
    print(f"USER: {test_question}\n")

    for event in app.stream_query(
        user_id=args.user_id,
        session_id=session.id,
        message=test_question,
    ):
        # Display tool calls (including SQL execution)
        if 'actions' in event:
            actions = event.get('actions', {})
            if 'tool_calls' in actions:
                for tool_call in actions['tool_calls']:
                    tool_name = tool_call.get('name', 'unknown')
                    if 'execute_sql' in tool_name:
                        args = tool_call.get('args', {})
                        sql = args.get('query', '')
                        if sql:
                            print(f"🔍 SQL QUERY EXECUTED:")
                            print(f"{'='*80}")
                            print(sql)
                            print(f"{'='*80}\n")

        # Display agent response
        if 'content' in event:
            parts = event['content'].get('parts', [])
            for part in parts:
                if 'text' in part:
                    print(f"AGENT: {part['text']}\n")

    print("\n" + "="*80)
    print("Agent tested successfully!")
    print("="*80)
    print(f"\nTo deploy this agent to Agent Engine, use:")
    print("  python deploy_agent_engine.py --deploy")
    print("\nOr in Python:")
    print("  from vertexai import agent_engines")
    print("  from root_agent import root_agent")
    print("  remote_app = agent_engines.create(")
    print("      display_name='nl2sql_agent',")
    print("      agent_engine=root_agent,")
    print("      requirements=[...]")
    print("  )")
