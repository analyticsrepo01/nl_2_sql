#!/usr/bin/env python3
"""
Create BigQuery table for insurance sales data and load CSV data.
"""

import os
import subprocess
from pathlib import Path
from google.cloud import bigquery

# Configuration
PROJECT_ID = "my-project-0004-346516"  # Change this to your project ID
DATASET_ID = "insurance"
TABLE_ID = "agent_sales_ledger"
CSV_FILE = "agent_sales_ledger_denormalized.csv"

# Get project ID from gcloud if not set
def get_project_id():
    try:
        result = subprocess.run(
            ['gcloud', 'config', 'get-value', 'core/project'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return PROJECT_ID

# Table schema
SCHEMA = [
    bigquery.SchemaField("policy_sale_id", "STRING", mode="REQUIRED", description="Unique identifier for each policy sale transaction."),
    bigquery.SchemaField("policy_number", "STRING", mode="NULLABLE", description="The official policy number assigned to the customer."),
    bigquery.SchemaField("sale_timestamp", "TIMESTAMP", mode="REQUIRED", description="Exact date and time the policy was sold."),
    bigquery.SchemaField("policy_effective_date", "DATE", mode="NULLABLE", description="The date the policy coverage begins."),
    bigquery.SchemaField("policy_status", "STRING", mode="NULLABLE", description="Current status of the policy (e.g., Active, Lapsed, Cancelled)."),

    # Agent Information
    bigquery.SchemaField("agent_id", "STRING", mode="REQUIRED", description="Unique identifier for the insurance agent."),
    bigquery.SchemaField("agent_full_name", "STRING", mode="NULLABLE", description="Full name of the agent."),
    bigquery.SchemaField("agent_license_number", "STRING", mode="NULLABLE", description="The agent's state-issued insurance license number."),
    bigquery.SchemaField("agent_office_location", "STRING", mode="NULLABLE", description="The physical branch or office the agent is associated with."),
    bigquery.SchemaField("agent_manager_name", "STRING", mode="NULLABLE", description="Name of the agent's direct manager."),

    # Customer Information
    bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED", description="Unique identifier for the customer."),
    bigquery.SchemaField("customer_age_at_purchase", "INTEGER", mode="NULLABLE", description="The customer's age when they purchased the policy."),
    bigquery.SchemaField("customer_gender", "STRING", mode="NULLABLE", description="Gender of the customer (e.g., Male, Female, Other)."),
    bigquery.SchemaField("customer_postal_code", "STRING", mode="NULLABLE", description="Postal code of the customer's residence for geographic analysis."),
    bigquery.SchemaField("customer_smoker_status", "BOOLEAN", mode="NULLABLE", description="Indicates if the customer is a smoker (true/false)."),

    # Product Information
    bigquery.SchemaField("product_code", "STRING", mode="NULLABLE", description="A unique code for the insurance product sold."),
    bigquery.SchemaField("product_name", "STRING", mode="NULLABLE", description="The name of the health insurance product (e.g., Gold PPO Plan, Silver HMO Plan)."),
    bigquery.SchemaField("product_type", "STRING", mode="NULLABLE", description="The primary type of insurance, e.g., 'Health Insurance'."),
    bigquery.SchemaField("product_subtype", "STRING", mode="NULLABLE", description="Specific subtype, e.g., 'Individual', 'Family Floater', 'Critical Illness', 'Senior Citizen', 'Group Plan', 'Top-Up'."),

    # Financials
    bigquery.SchemaField("monthly_premium", "FLOAT64", mode="NULLABLE", description="The monthly premium amount for the policy."),
    bigquery.SchemaField("annualized_premium", "FLOAT64", mode="NULLABLE", description="The total premium amount for a full year."),
    bigquery.SchemaField("payment_frequency", "STRING", mode="NULLABLE", description="How often the premium is paid (e.g., Monthly, Quarterly, Annually)."),
    bigquery.SchemaField("commission_rate", "FLOAT64", mode="NULLABLE", description="The commission percentage for the agent on this sale (e.g., 0.15 for 15%)."),
    bigquery.SchemaField("commission_earned_first_year", "FLOAT64", mode="NULLABLE", description="Total commission amount earned by the agent for the first year."),
]


def create_dataset(client, project_id, dataset_id):
    """Create BigQuery dataset if it doesn't exist."""
    dataset_ref = f"{project_id}.{dataset_id}"

    try:
        client.get_dataset(dataset_ref)
        print(f"✓ Dataset {dataset_ref} already exists")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset, timeout=30)
        print(f"✓ Created dataset {dataset_ref}")


def create_table(client, project_id, dataset_id, table_id, schema):
    """Create BigQuery table."""
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    try:
        client.get_table(table_ref)
        print(f"✓ Table {table_ref} already exists")
        # Delete and recreate
        client.delete_table(table_ref)
        print(f"  Deleted existing table")
    except Exception:
        pass

    table = bigquery.Table(table_ref, schema=schema)
    table = client.create_table(table)
    print(f"✓ Created table {table_ref}")


def load_csv_data(client, project_id, dataset_id, table_id, csv_filepath):
    """Load CSV data into BigQuery table."""
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    job_config = bigquery.LoadJobConfig(
        schema=SCHEMA,
        skip_leading_rows=1,  # Skip header row
        source_format=bigquery.SourceFormat.CSV,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    with open(csv_filepath, "rb") as source_file:
        load_job = client.load_table_from_file(
            source_file,
            table_ref,
            job_config=job_config
        )

    load_job.result()  # Wait for the job to complete

    table = client.get_table(table_ref)
    print(f"✓ Loaded {table.num_rows} rows into {table_ref}")


def main():
    """Main execution."""
    print("="*80)
    print("BigQuery Insurance Table Setup")
    print("="*80 + "\n")

    # Get project ID
    project_id = get_project_id()
    print(f"Project ID: {project_id}\n")

    # Initialize BigQuery client
    client = bigquery.Client(project=project_id)

    # Create dataset
    print("Step 1: Creating dataset...")
    create_dataset(client, project_id, DATASET_ID)

    # Create table
    print("\nStep 2: Creating table...")
    create_table(client, project_id, DATASET_ID, TABLE_ID, SCHEMA)

    # Load CSV data
    print("\nStep 3: Loading CSV data...")
    csv_path = Path(__file__).parent / CSV_FILE

    if not csv_path.exists():
        print(f"ERROR: CSV file not found: {csv_path}")
        print("Run generate_insurance_data.py first!")
        return

    load_csv_data(client, project_id, DATASET_ID, TABLE_ID, csv_path)

    # Summary
    print("\n" + "="*80)
    print("SETUP COMPLETE")
    print("="*80)
    print(f"\n✓ Dataset: {project_id}.{DATASET_ID}")
    print(f"✓ Table: {project_id}.{DATASET_ID}.{TABLE_ID}")
    print(f"\nFull table reference: {project_id}.{DATASET_ID}.{TABLE_ID}")

    # Query sample
    print("\n" + "="*80)
    print("SAMPLE QUERY")
    print("="*80)

    query = f"""
    SELECT
        agent_full_name,
        COUNT(*) as total_sales,
        SUM(annualized_premium) as total_premium,
        SUM(commission_earned_first_year) as total_commission
    FROM `{project_id}.{DATASET_ID}.{TABLE_ID}`
    GROUP BY agent_full_name
    ORDER BY total_commission DESC
    LIMIT 5
    """

    print("\nTop 5 Agents by Commission:")
    print("-" * 80)

    query_job = client.query(query)
    results = query_job.result()

    for i, row in enumerate(results, 1):
        print(f"{i}. {row.agent_full_name}")
        print(f"   Sales: {row.total_sales} | Premium: ${row.total_premium:,.2f} | Commission: ${row.total_commission:,.2f}")

    print("\n" + "="*80)
    print("Update your config.yaml with:")
    print("="*80)
    print(f"""
bigquery:
  table: "{project_id}.{DATASET_ID}.{TABLE_ID}"
  dataset: "{DATASET_ID}"
""")


if __name__ == "__main__":
    main()
