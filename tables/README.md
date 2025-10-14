# Insurance Sales Data

This directory contains synthetic insurance sales data for testing the NL2SQL agent.

## 📊 Dataset Overview

**Table**: `my-project-0004-346516.insurance.agent_sales_ledger`

- **Records**: 500 insurance policy sales
- **Time Period**: Last 12 months
- **Total Premium**: ~$3M annually
- **Total Commission**: ~$460K

## 📁 Files

### 1. `generate_insurance_data.py`
Generates realistic synthetic insurance sales data with:
- 10 insurance agents across 5 offices
- 10 different health insurance products
- Customer demographics (age, gender, smoker status)
- Premium and commission calculations

**Run:**
```bash
python generate_insurance_data.py
```

### 2. `agent_sales_ledger_denormalized.csv`
Generated CSV file with 500 records containing:
- Policy information
- Agent details
- Customer demographics
- Product information
- Financial data (premiums, commissions)

### 3. `create_insurance_table.py`
Creates BigQuery table and loads the CSV data.

**Run:**
```bash
python create_insurance_table.py
```

## 📋 Table Schema

### Policy Information
- `policy_sale_id` (STRING, REQUIRED) - Unique sale transaction ID
- `policy_number` (STRING) - Official policy number
- `sale_timestamp` (TIMESTAMP, REQUIRED) - When policy was sold
- `policy_effective_date` (DATE) - Coverage start date
- `policy_status` (STRING) - Active, Lapsed, or Cancelled

### Agent Information
- `agent_id` (STRING, REQUIRED) - Unique agent identifier
- `agent_full_name` (STRING) - Agent's full name
- `agent_license_number` (STRING) - State insurance license
- `agent_office_location` (STRING) - Branch/office location
- `agent_manager_name` (STRING) - Direct manager name

### Customer Information
- `customer_id` (STRING, REQUIRED) - Unique customer identifier
- `customer_age_at_purchase` (INTEGER) - Age at purchase
- `customer_gender` (STRING) - Male, Female, Other
- `customer_postal_code` (STRING) - ZIP code
- `customer_smoker_status` (BOOLEAN) - Smoker status

### Product Information
- `product_code` (STRING) - Unique product code
- `product_name` (STRING) - Product name (e.g., Gold PPO Plan)
- `product_type` (STRING) - Always "Health Insurance"
- `product_subtype` (STRING) - Individual, Family, Critical Illness, etc.

### Financial Information
- `monthly_premium` (FLOAT64) - Monthly premium amount
- `annualized_premium` (FLOAT64) - Annual premium
- `payment_frequency` (STRING) - Monthly, Quarterly, Annually
- `commission_rate` (FLOAT64) - Commission percentage (0.10-0.20)
- `commission_earned_first_year` (FLOAT64) - Total first year commission

## 🎯 Sample Questions for the Agent

### Basic Queries
- "How many policies were sold?"
- "What are the unique product types?"
- "Show me all agents and their offices"

### Aggregations
- "What is the total annual premium collected?"
- "Which agent has the highest total commission?"
- "What is the average age of customers?"

### Filtering
- "How many active policies are there?"
- "Show me all policies sold by Sarah Johnson"
- "What policies were sold in the Manhattan Branch?"

### Complex Analytics
- "Which product has the highest average premium?"
- "Compare commission earnings across different offices"
- "What is the average premium for smokers vs non-smokers?"
- "Show me the top 5 agents by number of sales"
- "Which product subtype generates the most revenue?"

## 🚀 Quick Start

### 1. Generate Data (Already Done)
```bash
cd tables
python generate_insurance_data.py
```

### 2. Create BigQuery Table (Already Done)
```bash
python create_insurance_table.py
```

### 3. Update Agent Configuration
Use `config_insurance.yaml`:
```bash
# Run agent with insurance config
python nl2sql_agent.py --config config_insurance.yaml --interactive

# Or with ADK web server
adk web --host 0.0.0.0 --port 8084
```

### 4. Test the Agent
```bash
python root_agent.py --question "Who is the top performing agent?"
```

## 📈 Data Statistics

**Agents (10 total):**
- Jennifer Thomas - $57,927 commission (56 sales)
- Michael Wilson - $55,969 commission (66 sales)
- Robert Williams - $50,104 commission (54 sales)

**Products (10 types):**
- Individual Plans (Gold, Silver, Platinum, Basic)
- Family Floater Plans
- Critical Illness Coverage
- Senior Citizen Plans
- Group Corporate Plans
- Top-Up Plans

**Policy Status Distribution:**
- Active: ~74%
- Lapsed: ~16%
- Cancelled: ~10%

**Premium Range:**
- Minimum: ~$250/month
- Maximum: ~$850/month
- Average: ~$420/month

## 🔄 Regenerate Data

To create a new dataset with different random values:

```bash
python generate_insurance_data.py
python create_insurance_table.py
```

This will create fresh data with the same structure but different values.
