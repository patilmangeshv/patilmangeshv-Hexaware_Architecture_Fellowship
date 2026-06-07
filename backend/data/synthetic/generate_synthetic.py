"""
Synthetic Data Generator
========================
Generates fake compliance-related documents using Faker.
Used for augmenting the test dataset without exposing real customer data.
"""
from __future__ import annotations

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

fake = Faker()

OUTPUT_DIR = Path(__file__).parent

# ── Compliance-domain word banks ──────────────────────────────────────────────

POLICIES = ["AML", "KYC", "Data Privacy", "IT Security", "Credit Risk", "Operational Risk"]
RISK_LEVELS = ["Low", "Medium", "High", "Critical"]
STATUSES = ["Open", "In Progress", "Closed", "Overdue"]
REGULATORS = ["Financial Conduct Authority", "Prudential Regulation Authority",
              "Basel Committee", "FATF", "GDPR Supervisory Authority"]
FINDING_TYPES = [
    "Inadequate controls", "Policy non-compliance", "Data quality issue",
    "Access control weakness", "Missing documentation", "Process gap",
    "Segregation of duties failure", "Monitoring deficiency",
]


# ── Generators ────────────────────────────────────────────────────────────────

def generate_audit_findings(n: int = 20) -> list:
    findings = []
    for i in range(n):
        due = fake.date_between(start_date="-6m", end_date="+3m")
        findings.append({
            "id": f"AF-{2025}-{i+1:04d}",
            "date": fake.date_between(start_date="-12m", end_date="today").isoformat(),
            "policy_area": random.choice(POLICIES),
            "finding_type": random.choice(FINDING_TYPES),
            "description": fake.paragraph(nb_sentences=3),
            "risk_level": random.choice(RISK_LEVELS),
            "status": random.choice(STATUSES),
            "owner": fake.name(),
            "due_date": due.isoformat(),
            "remediation_plan": fake.sentence(nb_words=15),
        })
    return findings


def generate_policy_summaries(n: int = 10) -> list:
    summaries = []
    for policy in POLICIES[:n]:
        summaries.append({
            "policy_name": f"{policy} Policy",
            "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}",
            "effective_date": fake.date_between(start_date="-2y", end_date="-1m").isoformat(),
            "next_review": fake.date_between(start_date="+3m", end_date="+12m").isoformat(),
            "owner": f"{fake.name()} — Chief Compliance Officer",
            "scope": fake.sentence(nb_words=20),
            "key_requirements": [fake.sentence(nb_words=12) for _ in range(5)],
            "approved_by": fake.name(),
        })
    return summaries


def generate_regulatory_notices(n: int = 10) -> list:
    notices = []
    for i in range(n):
        notices.append({
            "id": f"REG-{2025}-{i+1:03d}",
            "regulator": random.choice(REGULATORS),
            "date": fake.date_between(start_date="-18m", end_date="today").isoformat(),
            "subject": fake.sentence(nb_words=10),
            "summary": fake.paragraph(nb_sentences=4),
            "compliance_deadline": fake.date_between(start_date="+30d", end_date="+180d").isoformat(),
            "impact_area": random.choice(POLICIES),
            "priority": random.choice(RISK_LEVELS),
        })
    return notices


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    datasets = {
        "synthetic_audit_findings.json": generate_audit_findings(30),
        "synthetic_policy_summaries.json": generate_policy_summaries(6),
        "synthetic_regulatory_notices.json": generate_regulatory_notices(15),
    }

    for filename, data in datasets.items():
        out_path = OUTPUT_DIR / filename
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"✓ Generated {len(data)} records → {out_path}")


if __name__ == "__main__":
    main()
