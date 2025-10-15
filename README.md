# NL2SQL BigQuery Agent

A natural language to SQL agent powered by Google ADK (Agent Development Kit) that allows you to query BigQuery tables using plain English questions.

### 🚀 Quick Start
```bash
adk web --host 0.0.0.0 --port 8084
```

## 📋 Overview

This project provides a complete NL2SQL solution for BigQuery with:
- **Insurance Sales Dataset** (500 records pre-loaded)
- **Gemini 2.5 Flash** LLM for natural language understanding
- **Full BigQuery Toolset** including forecasting and advanced analytics
- **ADK Web Interface** for interactive queries
- **Agent Engine Deployment** for production use

## ✨ Features

- **Natural Language Queries**: Ask questions in plain English about your data
- **BigQuery ML Integration**: Time series forecasting and predictions
- **Advanced Analytics**: Natural language data insights with `ask_data_insights`
- **Configurable**: Easy to switch between different tables and datasets
- **Multiple Interfaces**: Web UI, CLI, and programmatic access
- **Deployment Ready**: Deploy to Vertex AI Agent Engine
- **Read-Only by Default**: Prevents accidental data modifications

## 🎯 Current Dataset

**Insurance Sales Ledger** (`my-project-0004-346516.insurance.agent_sales_ledger`)
- 500 policy sales records
- Agent performance tracking
- Customer demographics
- Premium and commission data

## 📦 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `google-genai` - Gemini AI SDK
- `google-adk` - Agent Development Kit
- `google-cloud-bigquery` - BigQuery client
- `google-cloud-aiplatform` - Vertex AI
- `google-auth` - Authentication
- `PyYAML` - Configuration
- `loguru` - Logging

### 2. Configure Authentication

```bash
gcloud auth application-default login
gcloud config set project my-project-0004-346516
```

### 3. Update Configuration

Edit `config.yaml` to point to your BigQuery table:

```yaml
project_id: "my-project-0004-346516"
location: "us-central1"

bigquery:
  table: "my-project-0004-346516.insurance.agent_sales_ledger"
  dataset: "insurance"
  write_mode: "BLOCKED"

agent:
  name: "insurance_sales_agent"
  model: "gemini-2.5-flash"  # Latest Gemini 2.5
  description: "Agent to answer questions about insurance sales data"
```

## 🚀 Usage

### ADK Web Interface (Recommended)

Start the web interface:

```bash
cd /home/jupyter/GenAI10/nl_2_sql
adk web --host 0.0.0.0 --port 8084
```

Access at: `http://localhost:8084`

### Interactive CLI Mode

```bash
python nl2sql_agent.py --interactive
```

Example session:
```
Your question: Who is the top performing agent by commission?
AGENT: Jennifer Thomas is the top performing agent with $57,927.94 in commission from 56 sales.

Your question: Forecast premium revenue for next quarter
AGENT: Based on the time series analysis...
```

### Single Question Mode

```bash
python nl2sql_agent.py --question "What is the average premium amount?"
```

### Test Root Agent Directly

```bash
python root_agent.py --question "How many active policies are there?"
```

## 💡 Example Questions

### Basic Queries
- "How many policies were sold?"
- "What are the unique product types?"
- "Show me all agents and their offices"
- "What is the total annual premium collected?"

### Analytics & Insights
- "Which agent has the highest commission?"
- "Compare sales performance across different offices"
- "What is the average premium for smokers vs non-smokers?"
- "Show me the top 5 products by revenue"
- "Analyze the relationship between customer age and premium"

### Forecasting (BigQuery ML)
- "Forecast premium revenue for next 3 months"
- "Predict sales trends for the next quarter"
- "Use ML to forecast commission earnings"

### Advanced Analysis
- "Use ask_data_insights to analyze customer demographics"
- "What patterns exist in policy cancellations?"
- "Which office location has the best retention rate?"

## 🛠️ Available BigQuery Tools

The agent has access to the **full BigQuery ADK toolset**:

### Core Tools
- `list_dataset_ids` - List all datasets in the project
- `get_dataset_info` - Get metadata about a dataset
- `list_table_ids` - List tables in a dataset
- `get_table_info` - Get schema and metadata about a table
- `execute_sql` - Run SQL queries and fetch results

### Advanced Analytics
- **`forecast`** - Time series forecasting using BigQuery ML (ML.FORECAST)
- **`ask_data_insights`** - Natural language data analysis and insights

## 📊 Insurance Dataset

The pre-loaded insurance dataset contains:

**Policy Information:**
- Policy sale ID, number, timestamp
- Effective date, status (Active/Lapsed/Cancelled)

**Agent Information:**
- Agent ID, name, license number
- Office location, manager name

**Customer Information:**
- Customer ID, age, gender
- Postal code, smoker status

**Product Information:**
- Product code, name, type, subtype
- Individual, Family, Critical Illness, Senior, Group plans

**Financial Information:**
- Monthly/annual premiums
- Payment frequency
- Commission rate and earnings

See `tables/README.md` for detailed schema and sample queries.

## 🚀 Deployment to Agent Engine

Deploy your agent to Vertex AI Agent Engine for production use:

### Test Locally First
```bash
python deploy_agent_engine.py --test-local
```

### Deploy to Agent Engine
```bash
python deploy_agent_engine.py --deploy
```

### Test Deployed Agent
```bash
python deploy_agent_engine.py --test-remote
```

### List Deployed Agents
```bash
python deploy_agent_engine.py --list
```

See `DEPLOYMENT.md` for detailed deployment instructions.

## 🔧 Configuration Options

### Write Mode
- `BLOCKED` (default): Read-only access, prevents data modifications
- `ALLOWED`: Enables INSERT, UPDATE, DELETE operations

### Model Selection

**Current (Recommended):**
- **`gemini-2.5-flash`** - Latest Gemini 2.5, fast and efficient ✅

**Alternative Models:**
- `gemini-2.0-flash` - Previous generation
- `gemini-1.5-pro` - More capable for complex queries
- `gemini-1.5-flash` - Balance of speed and capability

### Location
- `us-central1` (default) - US Central region
- Change in `config.yaml` if needed

## 🏗️ Architecture

The agent uses:

- **Google ADK** - Agent framework for building LLM-powered agents
- **BigQuery Toolset** - Pre-built tools for BigQuery operations
- **Gemini 2.5 Flash** - Latest LLM for understanding questions and generating SQL
- **Vertex AI** - Cloud-based model inference
- **InMemorySessionService** - Session management for conversation context
- **Agent Engine** - Production deployment platform

## 📁 Project Structure

```
nl_2_sql/
├── agent/
│   ├── root_agent.py          # ADK web server agent
│   └── insurance_agent.py     # Insurance-specific agent
├── tables/
│   ├── generate_insurance_data.py
│   ├── create_insurance_table.py
│   └── agent_sales_ledger_denormalized.csv
├── reference_code/            # Example implementations
├── nl2sql_agent.py           # Interactive CLI agent
├── root_agent.py             # Standalone agent
├── deploy_agent_engine.py    # Deployment manager
├── config.yaml               # Configuration
├── requirements.txt          # Dependencies
├── README.md                 # This file
├── DEPLOYMENT.md            # Deployment guide
└── SETUP_GUIDE.md           # Setup instructions
```

## 🔄 Switching Tables

To query a different BigQuery table:

1. Update `config.yaml`:
   ```yaml
   bigquery:
     table: "your-project.your-dataset.your-table"
     dataset: "your-dataset"
   ```

2. Restart the agent:
   ```bash
   adk web --host 0.0.0.0 --port 8084
   ```

## 🧪 Programmatic Usage

```python
from nl2sql_agent import NL2SQLAgent

# Initialize agent
agent = NL2SQLAgent(config_path="config.yaml")

# Ask questions
response = agent.query("What is the average premium amount?")
print(response)

# Interactive mode
agent.interactive_mode()
```

## 🐛 Troubleshooting

### Authentication Issues
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### Table Access Issues
Ensure BigQuery permissions:
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member=user:YOUR_EMAIL \
  --role=roles/bigquery.dataViewer
```

### Model Errors
If `gemini-2.5-flash` is not available in your region:
- Check available models in your region
- Update `model` in `config.yaml`

### Web Server Issues
```bash
# Kill existing server
pkill -f "adk web"

# Restart
cd /home/jupyter/GenAI10/nl_2_sql
adk web --host 0.0.0.0 --port 8084
```

## 📚 Documentation

- **Setup Guide**: `SETUP_GUIDE.md` - Detailed setup instructions
- **Deployment Guide**: `DEPLOYMENT.md` - Agent Engine deployment
- **Data Documentation**: `tables/README.md` - Dataset details
- **Google ADK Docs**: https://google.github.io/adk-docs/

## 🔗 Links

- **GitHub Repository**: https://github.com/analyticsrepo01/nl_2_sql
- **Google ADK**: https://google.github.io/adk-docs/
- **BigQuery**: https://cloud.google.com/bigquery

## 📝 License

Based on Google ADK reference implementation.

## 🎯 Quick Commands Reference

```bash
# Start web interface
adk web --host 0.0.0.0 --port 8084

# Interactive CLI
python nl2sql_agent.py --interactive

# Single question
python nl2sql_agent.py --question "Your question here"

# Test root agent
python root_agent.py --question "Your question here"

# Deploy to Agent Engine
python deploy_agent_engine.py --deploy

# Test deployment
python deploy_agent_engine.py --test-remote

# Generate new insurance data
cd tables && python generate_insurance_data.py
```

---

**Powered by Google ADK & Gemini 2.5 Flash** 🚀
