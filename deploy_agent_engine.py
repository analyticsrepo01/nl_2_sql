#!/usr/bin/env python3
"""
NL2SQL Agent Engine Deployment
Deploy the NL2SQL agent to Vertex AI Agent Engine for scalable production use.
"""

import os
import subprocess
import warnings
import yaml
from pathlib import Path

import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from google.cloud import storage
from google.adk.agents import Agent
from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
import google.auth
from loguru import logger
from sqlalchemy.exc import SAWarning


class NL2SQLAgentEngine:
    """Deployment manager for NL2SQL Agent Engine."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the deployment manager."""
        self.config = self._load_config(config_path)
        self.project_id = None
        self.location = None
        self.staging_bucket = None
        self.agent = None
        self.local_app = None
        self.remote_app = None

        self._setup_environment()
        self._setup_gcs_bucket()
        self._create_agent()

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        return config

    def _setup_environment(self):
        """Setup Google Cloud environment and authentication."""
        # Suppress warnings
        warnings.filterwarnings("ignore", category=SAWarning)

        # Get project ID
        project_id = self.config.get('project_id')

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

        if not project_id:
            raise ValueError(
                "Could not determine project ID. Please set it in config.yaml or "
                "run: gcloud config set project YOUR_PROJECT_ID"
            )

        # Get location
        location = self.config.get('location', 'us-central1')

        # Set environment variables
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
        os.environ["GOOGLE_CLOUD_LOCATION"] = location
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"

        self.project_id = project_id
        self.location = location

        # Disable nl2sql logger
        try:
            logger.disable("nl2sql")
        except:
            pass

        print(f"✓ Environment setup complete")
        print(f"✓ Project ID: {project_id}")
        print(f"✓ Location: {location}")

    def _setup_gcs_bucket(self):
        """Setup GCS bucket for staging."""
        client = storage.Client(project=self.project_id)

        # Create unique bucket name
        unique_prefix = 'nl2sql-agent'
        bucket_name = f"{self.project_id}-{unique_prefix}"
        bucket_uri = f"gs://{bucket_name}"

        bucket = storage.Bucket(client, bucket_name)

        if not bucket.exists():
            print(f"Creating GCS bucket: {bucket_name}")
            try:
                subprocess.run(
                    ['gcloud', 'storage', 'buckets', 'create', bucket_uri,
                     f'--location={self.location}'],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(f"✓ Bucket created: {bucket_name}")
            except subprocess.CalledProcessError as e:
                print(f"Warning: Could not create bucket: {e.stderr}")
                # Try to use an existing bucket
                bucket_name = f"{self.project_id}-sm"  # fallback bucket
                bucket_uri = f"gs://{bucket_name}"
                print(f"Using fallback bucket: {bucket_name}")
        else:
            print(f"✓ Using existing bucket: {bucket_name}")

        self.staging_bucket = bucket_uri

        # Initialize Vertex AI with staging bucket
        vertexai.init(
            project=self.project_id,
            location=self.location,
            staging_bucket=self.staging_bucket
        )

        print(f"✓ Vertex AI initialized with staging bucket: {self.staging_bucket}")

    def _create_agent(self):
        """Create the BigQuery agent."""
        # Extract configuration
        bq_table = self.config['bigquery']['table']
        write_mode_str = self.config['bigquery'].get('write_mode', 'BLOCKED')
        agent_name = self.config['agent']['name']
        model_name = self.config['agent']['model']

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

        # Create Agent (simple format for Agent Engine)
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

        print(f"✓ Agent created: {agent_name}")
        print(f"✓ Model: {model_name}")
        print(f"✓ Target table: {bq_table}")

    def test_locally(self, question: str, user_id: str = "test_user"):
        """
        Test the agent locally before deployment.

        Args:
            question: Question to ask the agent
            user_id: User ID for the session
        """
        print(f"\n{'='*80}")
        print(f"LOCAL TESTING")
        print(f"{'='*80}\n")

        # Create local app if not exists
        if not self.local_app:
            self.local_app = reasoning_engines.AdkApp(
                agent=self.agent,
                enable_tracing=True,
            )
            print(f"✓ Local app created\n")

        # Create session
        session = self.local_app.create_session(user_id=user_id)
        print(f"Session created: {session.id}\n")

        # Query
        print(f"USER: {question}\n")

        for event in self.local_app.stream_query(
            user_id=user_id,
            session_id=session.id,
            message=question,
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

    def deploy(self):
        """Deploy the agent to Vertex AI Agent Engine."""
        print(f"\n{'='*80}")
        print(f"DEPLOYING TO AGENT ENGINE")
        print(f"{'='*80}\n")

        agent_name = self.config['agent']['name']

        # Deploy using agent_engines.create
        self.remote_app = agent_engines.create(
            display_name=agent_name,
            agent_engine=self.agent,
            requirements=[
                "google-cloud-aiplatform[adk,agent_engines]",
                "google-adk",
                "google-genai",
                "google-cloud-bigquery",
                "google-auth",
                "PyYAML",
                "loguru",
                "SQLAlchemy",
            ]
        )

        print(f"\n✓ Agent deployed successfully!")
        print(f"✓ Display name: {self.remote_app.display_name}")
        print(f"✓ Resource name: {self.remote_app.resource_name}")

        return self.remote_app

    def test_remote(self, question: str, user_id: str = "remote_user"):
        """
        Test the deployed agent remotely.

        Args:
            question: Question to ask the agent
            user_id: User ID for the session
        """
        if not self.remote_app:
            raise ValueError("Agent not deployed yet. Call deploy() first.")

        print(f"\n{'='*80}")
        print(f"REMOTE TESTING")
        print(f"{'='*80}\n")

        # Create remote session
        remote_session = self.remote_app.create_session(user_id=user_id)
        session_id = remote_session.get("id") if isinstance(remote_session, dict) else remote_session.id
        print(f"Session created: {session_id}\n")

        # Query
        print(f"USER: {question}\n")

        for event in self.remote_app.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=question,
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

    def list_sessions(self, user_id: str):
        """List all sessions for a user."""
        if not self.remote_app:
            raise ValueError("Agent not deployed yet. Call deploy() first.")

        sessions = self.remote_app.list_sessions(user_id=user_id)
        return sessions

    @staticmethod
    def list_deployed_agents(project_id: str = None, location: str = "us-central1"):
        """
        List all deployed agent engines.

        Args:
            project_id: Google Cloud project ID
            location: Google Cloud location
        """
        if project_id:
            os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
            vertexai.init(project=project_id, location=location)

        print(f"\n{'='*80}")
        print(f"DEPLOYED AGENT ENGINES")
        print(f"{'='*80}\n")

        for idx, agent in enumerate(agent_engines.list(), 1):
            print(f"{idx}. {agent}")
            print(f"   Resource: {agent.resource_name}\n")

    @staticmethod
    def get_deployed_agent(resource_name: str):
        """
        Get a previously deployed agent by resource name.

        Args:
            resource_name: Full resource name of the agent engine
        """
        return agent_engines.get(resource_name)


def main():
    """Main deployment workflow."""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy NL2SQL Agent to Agent Engine")
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--test-local",
        action="store_true",
        help="Test agent locally before deployment"
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Deploy agent to Agent Engine"
    )
    parser.add_argument(
        "--test-remote",
        action="store_true",
        help="Test deployed agent remotely"
    )
    parser.add_argument(
        "--question",
        type=str,
        default="What columns are in the census data table?",
        help="Question to test"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all deployed agents"
    )

    args = parser.parse_args()

    if args.list:
        NL2SQLAgentEngine.list_deployed_agents()
        return

    # Initialize deployment manager
    deployer = NL2SQLAgentEngine(config_path=args.config)

    # Test locally
    if args.test_local:
        deployer.test_locally(args.question)

    # Deploy
    if args.deploy:
        deployer.deploy()

    # Test remotely
    if args.test_remote:
        if not deployer.remote_app:
            print("Deploying agent first...")
            deployer.deploy()
        deployer.test_remote(args.question)

    # Default: show help
    if not (args.test_local or args.deploy or args.test_remote or args.list):
        parser.print_help()
        print("\n" + "="*80)
        print("Quick Start:")
        print("="*80)
        print("1. Test locally:  python deploy_agent_engine.py --test-local")
        print("2. Deploy:        python deploy_agent_engine.py --deploy")
        print("3. Test remote:   python deploy_agent_engine.py --test-remote")
        print("4. List agents:   python deploy_agent_engine.py --list")


if __name__ == "__main__":
    main()
