# Agent Engine Deployment Guide

This guide shows how to deploy your NL2SQL agent to Vertex AI Agent Engine for scalable production use.

## Files Overview

### 1. **nl2sql_agent.py** (Local Development)
- Original agent for local testing and development
- Class-based implementation with full control
- Run interactively or with single queries

### 2. **root_agent.py** (Agent Definition)
- Standalone agent definition in root_agent format
- Ready for Agent Engine deployment
- Minimal, clean agent definition

### 3. **deploy_agent_engine.py** (Deployment Manager)
- Complete deployment workflow
- Local and remote testing
- Automatic GCS bucket setup
- Deployment management

## Quick Start

### Method 1: Using Deployment Manager (Recommended)

```bash
# 1. Test locally first
python deploy_agent_engine.py --test-local --question "What columns are in the table?"

# 2. Deploy to Agent Engine
python deploy_agent_engine.py --deploy

# 3. Test the deployed agent
python deploy_agent_engine.py --test-remote --question "How many rows are in the table?"

# 4. List all deployed agents
python deploy_agent_engine.py --list
```

### Method 2: Using Jupyter Notebook

```python
# Import the deployment manager
from deploy_agent_engine import NL2SQLAgentEngine

# Initialize
deployer = NL2SQLAgentEngine(config_path="config.yaml")

# Test locally
deployer.test_locally("What are the columns in the census data?")

# Deploy to Agent Engine
remote_app = deployer.deploy()

# Test remotely
deployer.test_remote("How many rows are there?")

# List sessions
sessions = deployer.list_sessions(user_id="remote_user")
print(sessions)
```

### Method 3: Using root_agent Directly

```python
import vertexai
from vertexai import agent_engines
from root_agent import root_agent

# The root_agent is already configured and ready to deploy

# Deploy
remote_app = agent_engines.create(
    display_name="nl2sql_census_agent",
    agent_engine=root_agent,
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
        "google-adk",
        "google-genai",
        "google-cloud-bigquery",
        "google-auth",
        "PyYAML",
    ]
)

print(f"Deployed: {remote_app.resource_name}")
```

## Deployment Workflow

### Step 1: Environment Setup

The deployment script automatically:
- Detects your GCP project ID
- Sets up environment variables
- Initializes Vertex AI
- Creates/uses a GCS bucket for staging

### Step 2: Local Testing

Before deploying, test the agent locally:

```python
deployer = NL2SQLAgentEngine()
deployer.test_locally("What is the schema of the census table?")
```

Expected output:
```
================================================================================
LOCAL TESTING
================================================================================

Session created: abc-123-def

USER: What is the schema of the census table?

AGENT: The census_data table contains the following columns: ...
```

### Step 3: Deploy to Agent Engine

Deploy the agent to production:

```python
remote_app = deployer.deploy()
```

Expected output:
```
================================================================================
DEPLOYING TO AGENT ENGINE
================================================================================

Deploying google.adk.agents.Agent as an application.
Identified the following requirements: {...}
Using bucket my-project-0004-346516-nl2sql-agent
Creating AgentEngine
AgentEngine created. Resource name: projects/.../reasoningEngines/...

✓ Agent deployed successfully!
✓ Display name: census_nl2sql_agent
✓ Resource name: projects/255766800726/locations/us-central1/reasoningEngines/...
```

### Step 4: Test Deployed Agent

Test the deployed agent remotely:

```python
deployer.test_remote("How many unique occupations are there?")
```

### Step 5: Access from Anywhere

Once deployed, access the agent from any environment:

```python
import vertexai
from vertexai import agent_engines

# Initialize Vertex AI
vertexai.init(project="my-project-0004-346516", location="us-central1")

# Get the deployed agent
remote_app = agent_engines.get('projects/.../reasoningEngines/...')

# Create session and query
session = remote_app.create_session(user_id="user123")
for event in remote_app.stream_query(
    user_id="user123",
    session_id=session["id"],
    message="What is the average age in the census data?"
):
    print(event)
```

## Command Line Usage

### Test Locally
```bash
python deploy_agent_engine.py --test-local --question "Your question here"
```

### Deploy
```bash
python deploy_agent_engine.py --deploy
```

### Test Remote
```bash
python deploy_agent_engine.py --test-remote --question "Your question here"
```

### All in One
```bash
python deploy_agent_engine.py --test-local --deploy --test-remote
```

### List Deployed Agents
```bash
python deploy_agent_engine.py --list
```

## Configuration

The deployment uses the same `config.yaml`:

```yaml
project_id: "my-project-0004-346516"
location: "us-central1"

bigquery:
  table: "my-project-0004-346516.census.census_data"
  dataset: "census"
  write_mode: "BLOCKED"

agent:
  name: "census_nl2sql_agent"
  model: "gemini-2.5-flash"
  description: "Agent to answer questions about census data"
```

## GCS Bucket

The deployment automatically creates a GCS bucket for staging:
- Bucket name: `{project_id}-nl2sql-agent`
- Location: Same as your configured location
- Used for: Storing agent artifacts and dependencies

If the bucket already exists, it will be reused.

## Managing Deployed Agents

### List All Agents
```python
from deploy_agent_engine import NL2SQLAgentEngine

NL2SQLAgentEngine.list_deployed_agents(
    project_id="my-project-0004-346516",
    location="us-central1"
)
```

### Get Specific Agent
```python
from deploy_agent_engine import NL2SQLAgentEngine

agent = NL2SQLAgentEngine.get_deployed_agent(
    resource_name="projects/.../reasoningEngines/..."
)
```

### Delete Agent
```python
from vertexai import agent_engines

agent = agent_engines.get('projects/.../reasoningEngines/...')
agent.delete()
```

## Updating the Deployed Agent

To update an already deployed agent:

1. **Update your configuration** in `config.yaml`
2. **Redeploy** with a new display name or delete the old one first

```python
# Delete old deployment
old_agent = agent_engines.get('projects/.../reasoningEngines/...')
old_agent.delete()

# Deploy new version
deployer = NL2SQLAgentEngine()
new_agent = deployer.deploy()
```

## Monitoring and Logs

View deployment and execution logs:
1. Go to Google Cloud Console
2. Navigate to Vertex AI > Agent Engine
3. Click on your agent
4. View logs and metrics

Or use the link provided during deployment:
```
View progress and logs at https://console.cloud.google.com/logs/query?project=my-project-0004-346516
```

## Troubleshooting

### Deployment Fails
- Check GCS bucket permissions
- Verify Vertex AI API is enabled
- Ensure you have Agent Engine permissions

### Agent Not Responding
- Check agent logs in Cloud Console
- Verify BigQuery permissions
- Test locally first with `--test-local`

### Authentication Issues
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### Requirements Issues
The deployment automatically packages these requirements:
- google-cloud-aiplatform[adk,agent_engines]
- google-adk
- google-genai
- google-cloud-bigquery
- google-auth
- PyYAML
- loguru
- SQLAlchemy

## Production Best Practices

1. **Test Locally First**: Always test with `--test-local` before deploying
2. **Version Control**: Tag deployments with version numbers in display_name
3. **Monitor Usage**: Track agent usage and costs in Cloud Console
4. **Set Quotas**: Configure appropriate quotas for production
5. **Backup Config**: Keep configuration files in version control

## Cost Optimization

- **Development**: Use `nl2sql_agent.py` for local testing (free)
- **Staging**: Deploy to Agent Engine for integration testing
- **Production**: Use deployed Agent Engine with appropriate quotas

## Next Steps

1. ✅ Test locally with sample questions
2. ✅ Deploy to Agent Engine
3. ✅ Test remote deployment
4. 📝 Integrate with your application
5. 📊 Monitor usage and performance
6. 🔄 Update and redeploy as needed
