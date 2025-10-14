#!/usr/bin/env python3
"""
Generate synthetic insurance sales data for testing the NL2SQL agent.
Creates realistic insurance agent sales records with 500+ entries.
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Seed for reproducibility
random.seed(42)

# Agent data
AGENTS = [
    {"id": "AGT001", "name": "Sarah Johnson", "license": "LIC-NY-54321", "office": "Manhattan Branch", "manager": "Michael Chen"},
    {"id": "AGT002", "name": "Robert Williams", "license": "LIC-NY-87654", "office": "Brooklyn Branch", "manager": "Michael Chen"},
    {"id": "AGT003", "name": "Maria Garcia", "license": "LIC-NY-23456", "office": "Queens Branch", "manager": "Jennifer Davis"},
    {"id": "AGT004", "name": "James Brown", "license": "LIC-NY-98765", "office": "Manhattan Branch", "manager": "Michael Chen"},
    {"id": "AGT005", "name": "Linda Martinez", "license": "LIC-NY-34567", "office": "Bronx Branch", "manager": "Jennifer Davis"},
    {"id": "AGT006", "name": "David Lee", "license": "LIC-NY-45678", "office": "Staten Island Branch", "manager": "Robert Taylor"},
    {"id": "AGT007", "name": "Patricia Anderson", "license": "LIC-NY-56789", "office": "Queens Branch", "manager": "Jennifer Davis"},
    {"id": "AGT008", "name": "Michael Wilson", "license": "LIC-NY-67890", "office": "Brooklyn Branch", "manager": "Michael Chen"},
    {"id": "AGT009", "name": "Jennifer Thomas", "license": "LIC-NY-78901", "office": "Manhattan Branch", "manager": "Michael Chen"},
    {"id": "AGT010", "name": "Christopher Moore", "license": "LIC-NY-89012", "office": "Bronx Branch", "manager": "Jennifer Davis"},
]

# Product definitions
PRODUCTS = [
    {"code": "GOLD-PPO-001", "name": "Gold PPO Plan", "type": "Health Insurance", "subtype": "Individual", "monthly": 450, "commission": 0.15},
    {"code": "SILVER-HMO-001", "name": "Silver HMO Plan", "type": "Health Insurance", "subtype": "Individual", "monthly": 320, "commission": 0.12},
    {"code": "PLAT-PPO-001", "name": "Platinum PPO Plan", "type": "Health Insurance", "subtype": "Individual", "monthly": 650, "commission": 0.18},
    {"code": "FAMILY-GOLD-001", "name": "Family Gold Floater", "type": "Health Insurance", "subtype": "Family Floater", "monthly": 850, "commission": 0.16},
    {"code": "FAMILY-SILVER-001", "name": "Family Silver Plan", "type": "Health Insurance", "subtype": "Family Floater", "monthly": 620, "commission": 0.14},
    {"code": "CRIT-ILL-001", "name": "Critical Illness Shield", "type": "Health Insurance", "subtype": "Critical Illness", "monthly": 280, "commission": 0.20},
    {"code": "SENIOR-CARE-001", "name": "Senior Care Plus", "type": "Health Insurance", "subtype": "Senior Citizen", "monthly": 580, "commission": 0.17},
    {"code": "GROUP-CORP-001", "name": "Corporate Group Plan", "type": "Health Insurance", "subtype": "Group Plan", "monthly": 380, "commission": 0.10},
    {"code": "TOPUP-SUPER-001", "name": "Super Top-Up 10L", "type": "Health Insurance", "subtype": "Top-Up", "monthly": 180, "commission": 0.15},
    {"code": "BASIC-HMO-001", "name": "Basic HMO Plan", "type": "Health Insurance", "subtype": "Individual", "monthly": 250, "commission": 0.10},
]

# Payment frequencies and their multipliers
PAYMENT_FREQUENCIES = {
    "Monthly": 1,
    "Quarterly": 3,
    "Semi-Annually": 6,
    "Annually": 12
}

# Policy statuses
POLICY_STATUSES = ["Active", "Active", "Active", "Active", "Active", "Lapsed", "Cancelled", "Active"]

# ZIP codes (NY area)
ZIP_CODES = ["10001", "10002", "10003", "10019", "10025", "11201", "11211", "11215", "11217",
             "10453", "10456", "10458", "11101", "11103", "11354", "11355", "10301", "10305"]

# Generate records
def generate_records(num_records=500):
    records = []
    start_date = datetime.now() - timedelta(days=365)

    for i in range(num_records):
        # Random selections
        agent = random.choice(AGENTS)
        product = random.choice(PRODUCTS)
        payment_freq = random.choice(list(PAYMENT_FREQUENCIES.keys()))

        # Generate timestamps
        sale_timestamp = start_date + timedelta(days=random.randint(0, 365),
                                                hours=random.randint(8, 18),
                                                minutes=random.randint(0, 59))
        policy_effective_date = sale_timestamp.date() + timedelta(days=random.randint(1, 30))

        # Customer data
        customer_age = random.randint(22, 75)
        is_smoker = random.choice([True, False, False, False])  # 25% smokers
        gender = random.choice(["Male", "Female", "Other"])

        # Calculate premiums
        monthly_premium = product["monthly"]
        # Add variation based on age and smoker status
        if customer_age > 50:
            monthly_premium *= random.uniform(1.1, 1.3)
        if is_smoker:
            monthly_premium *= 1.25

        monthly_premium = round(monthly_premium, 2)
        annualized_premium = round(monthly_premium * 12, 2)
        commission_earned = round(annualized_premium * product["commission"], 2)

        # Create record
        record = {
            "policy_sale_id": f"SALE-{i+1:06d}",
            "policy_number": f"POL-{random.randint(100000, 999999)}",
            "sale_timestamp": sale_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "policy_effective_date": policy_effective_date.strftime("%Y-%m-%d"),
            "policy_status": random.choice(POLICY_STATUSES),

            # Agent info
            "agent_id": agent["id"],
            "agent_full_name": agent["name"],
            "agent_license_number": agent["license"],
            "agent_office_location": agent["office"],
            "agent_manager_name": agent["manager"],

            # Customer info
            "customer_id": f"CUST-{random.randint(10000, 99999)}",
            "customer_age_at_purchase": customer_age,
            "customer_gender": gender,
            "customer_postal_code": random.choice(ZIP_CODES),
            "customer_smoker_status": str(is_smoker),

            # Product info
            "product_code": product["code"],
            "product_name": product["name"],
            "product_type": product["type"],
            "product_subtype": product["subtype"],

            # Financials
            "monthly_premium": monthly_premium,
            "annualized_premium": annualized_premium,
            "payment_frequency": payment_freq,
            "commission_rate": product["commission"],
            "commission_earned_first_year": commission_earned
        }

        records.append(record)

    return records

def save_to_csv(records, filename="agent_sales_ledger_denormalized.csv"):
    """Save records to CSV file."""
    if not records:
        print("No records to save!")
        return

    filepath = Path(__file__).parent / filename

    # Get field names from first record
    fieldnames = list(records[0].keys())

    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"✓ Generated {len(records)} records")
    print(f"✓ Saved to: {filepath}")

    # Print statistics
    print("\n" + "="*80)
    print("DATA STATISTICS")
    print("="*80)

    total_premium = sum(r['annualized_premium'] for r in records)
    total_commission = sum(r['commission_earned_first_year'] for r in records)
    active_policies = sum(1 for r in records if r['policy_status'] == 'Active')

    print(f"Total Records: {len(records)}")
    print(f"Active Policies: {active_policies} ({active_policies/len(records)*100:.1f}%)")
    print(f"Total Annual Premium: ${total_premium:,.2f}")
    print(f"Total Commission: ${total_commission:,.2f}")
    print(f"\nUnique Agents: {len(set(r['agent_id'] for r in records))}")
    print(f"Unique Customers: {len(set(r['customer_id'] for r in records))}")
    print(f"Unique Products: {len(set(r['product_code'] for r in records))}")

    # Top performing agents
    print("\n" + "="*80)
    print("TOP 3 AGENTS BY COMMISSION")
    print("="*80)

    agent_commissions = {}
    for record in records:
        agent_id = record['agent_id']
        agent_name = record['agent_full_name']
        commission = record['commission_earned_first_year']

        if agent_id not in agent_commissions:
            agent_commissions[agent_id] = {"name": agent_name, "commission": 0, "sales": 0}
        agent_commissions[agent_id]["commission"] += commission
        agent_commissions[agent_id]["sales"] += 1

    top_agents = sorted(agent_commissions.items(),
                       key=lambda x: x[1]["commission"],
                       reverse=True)[:3]

    for i, (agent_id, data) in enumerate(top_agents, 1):
        print(f"{i}. {data['name']} ({agent_id})")
        print(f"   Sales: {data['sales']} | Commission: ${data['commission']:,.2f}")

if __name__ == "__main__":
    print("Generating Insurance Sales Data...")
    print("="*80 + "\n")

    # Generate 500 records
    records = generate_records(500)

    # Save to CSV
    save_to_csv(records)

    print("\n✓ Data generation complete!")
