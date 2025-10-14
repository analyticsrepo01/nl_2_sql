#!/usr/bin/env python3
"""
NL2SQL BigQuery Agent
An agent that converts natural language questions to SQL queries for BigQuery tables.
"""

import asyncio
import warnings
import os
import subprocess
import yaml
from pathlib import Path
from typing import Optional

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
from google.genai import types
import google.auth
import vertexai
from loguru import logger
from sqlalchemy.exc import SAWarning


class NL2SQLAgent:
    """Natural Language to SQL Agent for BigQuery."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the NL2SQL Agent with configuration."""
        self.config = self._load_config(config_path)
        self.agent = None
        self.runner = None
        self.session = None
        self.session_service = None
        self._setup_authentication()
        self._setup_agent()

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        return config

    def _setup_authentication(self):
        """Setup Google Cloud authentication and Vertex AI."""
        # Suppress warnings
        warnings.filterwarnings("ignore", category=SAWarning)

        # Get project ID from config or environment
        project_id = self.config.get('project_id')

        # If not in config, try to get from gcloud
        if not project_id or project_id == "your-project-id":
            try:
                result = subprocess.run(
                    ['gcloud', 'config', 'get-value', 'core/project'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                project_id = result.stdout.strip()
                if project_id:
                    self.config['project_id'] = project_id
            except:
                pass

        # If still not found, try environment variable
        if not project_id:
            project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
            if project_id:
                self.config['project_id'] = project_id

        if not project_id:
            raise ValueError(
                "Could not determine project ID. Please set it in config.yaml or "
                "run: gcloud config set project YOUR_PROJECT_ID"
            )

        # Get location from config
        location = self.config.get('location', 'us-central1')

        # Set environment variables
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
        os.environ["GOOGLE_CLOUD_LOCATION"] = location
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"  # Use Vertex AI API

        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)

        # Disable loguru logger if needed
        try:
            logger.disable("nl2sql")
        except:
            pass

        print(f"✓ Authentication setup complete")
        print(f"✓ Project ID: {project_id}")
        print(f"✓ Location: {location}")

    def _setup_agent(self):
        """Setup the BigQuery agent with tools and configuration."""
        # Extract configuration values
        project_id = self.config['project_id']
        bq_table = self.config['bigquery']['table']
        write_mode_str = self.config['bigquery'].get('write_mode', 'BLOCKED')
        agent_name = self.config['agent']['name']
        model_name = self.config['agent']['model']
        app_name = self.config['session']['app_name']
        user_id = self.config['session']['user_id']
        session_id = self.config['session']['session_id']

        # Configure write mode
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

        # Agent Definition
        self.agent = Agent(
            model=model_name,
            name=agent_name,
            description=self.config['agent']['description'],
            instruction=f"""
            You are a data analysis assistant with access to BigQuery tools.

            Your primary focus is the census data table: {bq_table}

            When answering questions:
            1. First, understand the user's question and what data they need
            2. Use the BigQuery tools to explore the table schema and understand the data structure
            3. Generate and execute appropriate SQL queries to answer the question
            4. Provide clear, concise answers based on the query results
            5. If you encounter any issues, explain them clearly to the user

            Always use the BigQuery tools available to you to answer questions accurately.
            """,
            tools=[bigquery_toolset],
        )

        # Session and Runner setup
        self.session_service = InMemorySessionService()
        self.session = asyncio.run(
            self.session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
        )
        self.runner = Runner(
            agent=self.agent,
            app_name=app_name,
            session_service=self.session_service
        )

        print(f"✓ Agent '{agent_name}' initialized successfully")
        print(f"✓ Model: {model_name}")
        print(f"✓ Target table: {bq_table}")
        print(f"✓ Write mode: {write_mode_str}")

    def query(self, question: str, verbose: bool = True) -> str:
        """
        Ask a natural language question and get an answer.

        Args:
            question: Natural language question about the data
            verbose: If True, print the conversation

        Returns:
            The agent's response as a string
        """
        user_id = self.config['session']['user_id']
        session_id = self.config['session']['session_id']

        content = types.Content(role="user", parts=[types.Part(text=question)])
        events = self.runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        )

        if verbose:
            print(f"\n{'='*80}")
            print(f"USER: {question}")
            print(f"{'='*80}\n")

        response = ""
        for event in events:
            if event.is_final_response():
                response = event.content.parts[0].text
                if verbose:
                    print(f"AGENT: {response}\n")

        return response

    def interactive_mode(self):
        """Run the agent in interactive mode."""
        print(f"\n{'='*80}")
        print(f"  NL2SQL Agent - Interactive Mode")
        print(f"{'='*80}")
        print(f"\nTable: {self.config['bigquery']['table']}")
        print(f"\nType 'exit' or 'quit' to end the session\n")

        while True:
            try:
                question = input("Your question: ").strip()

                if question.lower() in ['exit', 'quit', 'q']:
                    print("\nGoodbye!")
                    break

                if not question:
                    continue

                self.query(question, verbose=True)

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}\n")


def main():
    """Main entry point for the NL2SQL agent."""
    import argparse

    parser = argparse.ArgumentParser(description="NL2SQL BigQuery Agent")
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )
    parser.add_argument(
        "--question",
        type=str,
        help="Ask a single question and exit"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )

    args = parser.parse_args()

    # Initialize agent
    agent = NL2SQLAgent(config_path=args.config)

    # Run based on mode
    if args.question:
        # Single question mode
        agent.query(args.question, verbose=True)
    elif args.interactive:
        # Interactive mode
        agent.interactive_mode()
    else:
        # Default to interactive mode
        agent.interactive_mode()


if __name__ == "__main__":
    main()
