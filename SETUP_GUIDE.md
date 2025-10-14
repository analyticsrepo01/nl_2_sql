# Setup Guide - NL2SQL BigQuery Agent

## Authentication Setup

The agent now includes comprehensive Google Cloud authentication that:

### 1. Environment Variables Setup
- Sets `GOOGLE_CLOUD_PROJECT` from config or auto-detects from gcloud
- Sets `GOOGLE_CLOUD_LOCATION` (default: us-central1)
- Sets `GOOGLE_GENAI_USE_VERTEXAI=TRUE` to use Vertex AI API

### 2. Vertex AI Initialization
- Automatically initializes Vertex AI with your project and location
- Suppresses SQLAlchemy warnings for cleaner output
- Provides verbose authentication feedback

### 3. Project ID Auto-Detection
The agent tries to find your project ID in this order:
1. From `config.yaml` file
2. From `gcloud config get-value core/project`
3. From `GOOGLE_CLOUD_PROJECT` environment variable

## Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `google-genai` - GenAI SDK
- `google-adk` - Agent Development Kit
- `google-cloud-bigquery` - BigQuery client
- `google-cloud-aiplatform` - Vertex AI
- `google-auth` - Authentication
- `PyYAML` - Configuration files
- `loguru` - Logging
- `SQLAlchemy` - Database toolkit

### 2. Configure Google Cloud

```bash
# Set your project
gcloud config set project my-project-0004-346516

# Authenticate
gcloud auth application-default login

# Verify
gcloud config get-value core/project
```

### 3. Update Configuration

Edit `config.yaml`:
```yaml
project_id: "my-project-0004-346516"
location: "us-central1"

bigquery:
  table: "my-project-0004-346516.census.census_data"
  dataset: "census"
  write_mode: "BLOCKED"
```

### 4. Run the Agent

```bash
# Interactive mode
python nl2sql_agent.py --interactive

# Single question
python nl2sql_agent.py --question "What columns are in the table?"
```

## What Happens on Startup

When you run the agent, it will:

1. **Load Configuration** from `config.yaml`

2. **Setup Authentication**:
   - Detect project ID automatically
   - Initialize Vertex AI
   - Set environment variables
   - Print confirmation:
     ```
     ✓ Authentication setup complete
     ✓ Project ID: my-project-0004-346516
     ✓ Location: us-central1
     ```

3. **Initialize Agent**:
   - Create BigQuery toolset
   - Setup agent with Gemini model
   - Create session service
   - Print confirmation:
     ```
     ✓ Agent 'census_nl2sql_agent' initialized successfully
     ✓ Model: gemini-2.0-flash
     ✓ Target table: my-project-0004-346516.census.census_data
     ✓ Write mode: BLOCKED
     ```

4. **Ready for Questions**!

## Troubleshooting

### Error: Could not determine project ID
```bash
# Solution 1: Set in gcloud
gcloud config set project YOUR_PROJECT_ID

# Solution 2: Set in config.yaml
project_id: "YOUR_PROJECT_ID"

# Solution 3: Set environment variable
export GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
```

### Error: Authentication failed
```bash
# Re-authenticate
gcloud auth application-default login
```

### Error: Model not available
- Check if model is available in your region
- Try different model in config.yaml:
  - `gemini-2.0-flash`
  - `gemini-1.5-pro`
  - `gemini-1.5-flash`

### Error: Table access denied
```bash
# Grant BigQuery permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=user:YOUR_EMAIL \
  --role=roles/bigquery.dataViewer
```

## Environment Variables Reference

The agent automatically sets these:

| Variable | Value | Purpose |
|----------|-------|---------|
| `GOOGLE_CLOUD_PROJECT` | Your project ID | Identifies GCP project |
| `GOOGLE_CLOUD_LOCATION` | us-central1 | Sets default region |
| `GOOGLE_GENAI_USE_VERTEXAI` | TRUE | Uses Vertex AI instead of API |

## Next Steps

1. Test the agent:
   ```bash
   python nl2sql_agent.py --question "Show me the table schema"
   ```

2. Start interactive session:
   ```bash
   python nl2sql_agent.py --interactive
   ```

3. Try example questions from `README.md`

4. To change tables, just update `config.yaml` and restart
