# NL2SQL BigQuery Agent

### HOW TO START 
###### adk web --host 0.0.0.0 --port 8084
 

A natural language to SQL agent powered by Google ADK (Agent Development Kit) that allows you to query BigQuery tables using plain English questions.

## Features

- **Natural Language Queries**: Ask questions in plain English about your data
- **BigQuery Integration**: Direct integration with Google BigQuery
- **Configurable**: Easy to switch between different tables and datasets
- **Interactive Mode**: Chat-like interface for exploring your data
- **Single Query Mode**: Execute one-off queries from the command line
- **Read-Only by Default**: Prevents accidental data modifications

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Authentication

Ensure you have Google Cloud authentication set up:

```bash
gcloud auth application-default login
```

### 3. Update Configuration

Edit `config.yaml` to point to your BigQuery table:

```yaml
project_id: "my-project-0004-346516"

bigquery:
  table: "my-project-0004-346516.census.census_data"
  dataset: "census"
  write_mode: "BLOCKED"  # Use "ALLOWED" to enable write operations

agent:
  name: "census_nl2sql_agent"
  model: "gemini-2.0-flash"
```

## Usage

### Interactive Mode (Default)

Start an interactive session to ask multiple questions:

```bash
python nl2sql_agent.py --interactive
```

Example session:
```
Your question: How many rows are in the census data table?
AGENT: There are 32,561 rows in the census_data table.

Your question: What are the column names in the table?
AGENT: The table contains the following columns: age, workclass, fnlwgt, education...
```

### Single Question Mode

Ask a single question and exit:

```bash
python nl2sql_agent.py --question "What is the average age in the census data?"
```

### Custom Configuration File

Use a different configuration file:

```bash
python nl2sql_agent.py --config my_config.yaml --interactive
```

## Example Questions

Here are some example questions you can ask:

1. **Data Exploration**:
   - "What columns are available in the census table?"
   - "How many rows are in the table?"
   - "Show me the first 5 rows"

2. **Aggregation Queries**:
   - "What is the average age in the dataset?"
   - "How many people are there in each occupation?"
   - "What is the income distribution?"

3. **Filtering**:
   - "How many people have a Bachelor's degree?"
   - "Show me people older than 50"
   - "What occupations earn more than 50K per year?"

4. **Complex Analysis**:
   - "What is the correlation between education level and income?"
   - "Which occupation has the highest average age?"
   - "Compare income levels across different education categories"

## Changing the Target Table

To query a different BigQuery table:

1. Edit `config.yaml`:
   ```yaml
   bigquery:
     table: "your-project.your-dataset.your-table"
     dataset: "your-dataset"
   ```

2. Restart the agent

## Available BigQuery Tools

The agent has access to these BigQuery tools:

- `list_dataset_ids`: List all datasets in the project
- `get_dataset_info`: Get metadata about a dataset
- `list_table_ids`: List tables in a dataset
- `get_table_info`: Get schema and metadata about a table
- `execute_sql`: Run SQL queries and fetch results
- `ask_data_insights`: Advanced data analysis using natural language

## Programmatic Usage

You can also use the agent in your Python code:

```python
from nl2sql_agent import NL2SQLAgent

# Initialize agent
agent = NL2SQLAgent(config_path="config.yaml")

# Ask questions
response = agent.query("What is the average age in the census data?")
print(response)

# Run interactive mode
agent.interactive_mode()
```

## Architecture

The agent uses:

- **Google ADK**: Agent framework for building LLM-powered agents
- **BigQuery Toolset**: Pre-built tools for BigQuery operations
- **Gemini Models**: LLM for understanding questions and generating SQL
- **InMemorySessionService**: Session management for conversation context

## Configuration Options

### Write Mode

- `BLOCKED` (default): Read-only access, prevents data modifications
- `ALLOWED`: Enables INSERT, UPDATE, DELETE operations

### Model Selection

Available models:
- `gemini-2.0-flash` (default): Fast, efficient
- `gemini-1.5-pro`: More capable for complex queries
- `gemini-1.5-flash`: Balance of speed and capability

## Troubleshooting

### Authentication Issues

If you see authentication errors:
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### Table Access Issues

Ensure your account has BigQuery Data Viewer permissions:
```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member=user:YOUR_EMAIL \
  --role=roles/bigquery.dataViewer
```

### Model Errors

If the model is not available in your region, update the config to use a different model or region.

## License

Based on Google ADK reference implementation.
