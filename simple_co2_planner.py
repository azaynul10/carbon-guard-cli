#!/usr/bin/env python3
"""
Simple CO2 Reduction Plan Generator
Generates actionable CO2 reduction plans and exports anonymized data to CSV
"""

import csv
import hashlib
from datetime import datetime
from typing import Dict


def generate_co2_reduction_plan(target_reduction: float = 25.0) -> Dict:
    """Generate CO2 reduction plan with specific actions"""

    # Available reduction actions
    actions = [
        {
            "action": "Use Graviton instances",
            "description": "Migrate to ARM-based Graviton processors for 20% better energy efficiency",
            "category": "aws_infrastructure",
            "co2_reduction_percent": 20,
            "cost_savings_usd": 150,
            "effort": "medium",
            "timeline_weeks": 4,
            "steps": [
                "Test application compatibility with ARM architecture",
                "Update deployment scripts for Graviton instances",
                "Plan gradual migration schedule",
                "Execute migration in phases",
                "Monitor performance and cost savings",
            ],
        },
        {
            "action": "Eat plant-based",
            "description": "Replace high-carbon meat with plant-based alternatives",
            "category": "personal_lifestyle",
            "co2_reduction_percent": 40,
            "cost_savings_usd": 200,
            "effort": "medium",
            "timeline_weeks": 8,
            "steps": [
                "Research plant-based protein sources",
                "Plan weekly meal menus with plant alternatives",
                "Try new plant-based recipes gradually",
                "Track dietary changes and health impact",
                "Monitor CO2 reduction from food choices",
            ],
        },
        {
            "action": "Implement auto-scaling",
            "description": "Set up auto-scaling to match demand and reduce idle resources",
            "category": "aws_infrastructure",
            "co2_reduction_percent": 25,
            "cost_savings_usd": 300,
            "effort": "high",
            "timeline_weeks": 6,
            "steps": [
                "Create launch templates for auto-scaling",
                "Configure auto-scaling groups",
                "Set up scaling policies based on metrics",
                "Test scaling behavior under load",
                "Monitor and tune scaling thresholds",
            ],
        },
        {
            "action": "Right-size instances",
            "description": "Optimize EC2 instance types based on actual usage patterns",
            "category": "aws_infrastructure",
            "co2_reduction_percent": 15,
            "cost_savings_usd": 250,
            "effort": "low",
            "timeline_weeks": 2,
            "steps": [
                "Analyze CloudWatch CPU and memory metrics",
                "Identify over-provisioned instances",
                "Create rightsizing recommendations",
                "Schedule maintenance windows for changes",
                "Execute instance type modifications",
            ],
        },
        {
            "action": "Optimize transportation",
            "description": "Use public transport, cycling, or walking more frequently",
            "category": "personal_lifestyle",
            "co2_reduction_percent": 35,
            "cost_savings_usd": 500,
            "effort": "low",
            "timeline_weeks": 2,
            "steps": [
                "Map current transportation patterns",
                "Identify public transport alternatives",
                "Test cycling/walking routes for short trips",
                "Plan combined trips to reduce frequency",
                "Track transportation CO2 savings",
            ],
        },
        {
            "action": "Reduce energy consumption",
            "description": "Implement energy-saving practices at home and office",
            "category": "personal_lifestyle",
            "co2_reduction_percent": 20,
            "cost_savings_usd": 300,
            "effort": "low",
            "timeline_weeks": 1,
            "steps": [
                "Conduct home/office energy audit",
                "Replace inefficient appliances and lighting",
                "Improve insulation and weatherproofing",
                "Adjust thermostat settings for efficiency",
                "Monitor energy usage and savings",
            ],
        },
    ]

    # Select actions to meet target reduction
    selected_actions = []
    cumulative_reduction = 0

    # Sort by impact/effort ratio
    effort_scores = {"low": 1, "medium": 2, "high": 3}
    actions.sort(
        key=lambda x: x["co2_reduction_percent"] / effort_scores[x["effort"]],
        reverse=True,
    )

    for action in actions:
        if cumulative_reduction < target_reduction:
            selected_actions.append(action)
            cumulative_reduction += action["co2_reduction_percent"]

    # Calculate plan metrics
    total_cost_savings = sum(action["cost_savings_usd"] for action in selected_actions)
    total_timeline = (
        max(action["timeline_weeks"] for action in selected_actions)
        if selected_actions
        else 0
    )

    plan = {
        "plan_id": f"co2_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "created_at": datetime.now().isoformat(),
        "target_reduction_percent": target_reduction,
        "actual_reduction_percent": min(cumulative_reduction, 80),  # Cap at 80%
        "selected_actions": selected_actions,
        "total_cost_savings_usd": total_cost_savings,
        "implementation_timeline_weeks": total_timeline,
        "categories_covered": list({action["category"] for action in selected_actions}),
    }

    return plan


def print_reduction_plan(plan: Dict):
    """Print formatted CO2 reduction plan"""

    print("🌍 CO2 REDUCTION PLAN")
    print("=" * 60)

    print(f"📋 Plan ID: {plan['plan_id']}")
    print(f"🎯 Target Reduction: {plan['target_reduction_percent']}%")
    print(f"📊 Actual Reduction: {plan['actual_reduction_percent']:.1f}%")
    print(f"💰 Total Cost Savings: ${plan['total_cost_savings_usd']:,}")
    print(f"⏰ Implementation Timeline: {plan['implementation_timeline_weeks']} weeks")

    print(f"\n🎯 SELECTED ACTIONS ({len(plan['selected_actions'])}):")
    print("-" * 60)

    for i, action in enumerate(plan["selected_actions"], 1):
        print(f"\n{i}. {action['action']}")
        print(f"   📝 {action['description']}")
        print(f"   📊 CO2 Reduction: {action['co2_reduction_percent']}%")
        print(f"   💰 Cost Savings: ${action['cost_savings_usd']:,}")
        print(f"   ⚡ Effort Level: {action['effort'].title()}")
        print(f"   ⏱️  Timeline: {action['timeline_weeks']} weeks")

        print(f"   📋 Implementation Steps:")
        for step in action["steps"]:
            print(f"      • {step}")

    print(f"\n🚀 NEXT STEPS:")
    if plan["selected_actions"]:
        first_action = plan["selected_actions"][0]
        print(f"   1. Start with: {first_action['action']}")
        print(f"   2. First step: {first_action['steps'][0]}")
        print(f"   3. Timeline: {first_action['timeline_weeks']} weeks")

    print(f"\n💡 SUCCESS TIPS:")
    print(f"   • Start with low-effort, high-impact actions")
    print(f"   • Monitor progress monthly")
    print(f"   • Track both CO2 reduction and cost savings")
    print(f"   • Get team/family buy-in for lifestyle changes")


def export_plan_to_csv(plan: Dict, filename: str = None) -> str:
    """Export reduction plan to anonymized CSV"""

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"co2_reduction_plan_{timestamp}.csv"

    # Anonymize plan ID
    plan_hash = hashlib.sha256(plan["plan_id"].encode()).hexdigest()[:8]
    anonymized_plan_id = f"plan_{plan_hash}"

    with open(filename, "w", newline="") as csvfile:
        fieldnames = [
            "plan_id",
            "created_at",
            "target_reduction_percent",
            "actual_reduction_percent",
            "total_cost_savings_usd",
            "implementation_weeks",
            "actions_count",
            "categories",
            "action_1",
            "action_1_reduction",
            "action_1_effort",
            "action_2",
            "action_2_reduction",
            "action_2_effort",
            "action_3",
            "action_3_reduction",
            "action_3_effort",
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Prepare row data
        row = {
            "plan_id": anonymized_plan_id,
            "created_at": plan["created_at"],
            "target_reduction_percent": plan["target_reduction_percent"],
            "actual_reduction_percent": plan["actual_reduction_percent"],
            "total_cost_savings_usd": plan["total_cost_savings_usd"],
            "implementation_weeks": plan["implementation_timeline_weeks"],
            "actions_count": len(plan["selected_actions"]),
            "categories": ",".join(plan["categories_covered"]),
            "action_1": "",
            "action_1_reduction": "",
            "action_1_effort": "",
            "action_2": "",
            "action_2_reduction": "",
            "action_2_effort": "",
            "action_3": "",
            "action_3_reduction": "",
            "action_3_effort": "",
        }

        # Add up to 3 actions
        for i, action in enumerate(plan["selected_actions"][:3], 1):
            row[f"action_{i}"] = action["action"]
            row[f"action_{i}_reduction"] = action["co2_reduction_percent"]
            row[f"action_{i}_effort"] = action["effort"]

        writer.writerow(row)

    return filename


def create_sample_audit_data_csv(filename: str = "sample_audit_data.csv"):
    """Create sample audit data CSV for demonstration"""

    with open(filename, "w", newline="") as csvfile:
        fieldnames = [
            "audit_type",
            "timestamp",
            "service_or_category",
            "co2_value",
            "unit",
            "cost_or_savings",
            "optimization_potential",
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Sample data rows
        sample_rows = [
            {
                "audit_type": "aws",
                "timestamp": datetime.now().isoformat(),
                "service_or_category": "ec2",
                "co2_value": 2.5,
                "unit": "kg/hour",
                "cost_or_savings": 15.75,
                "optimization_potential": "high",
            },
            {
                "audit_type": "local",
                "timestamp": datetime.now().isoformat(),
                "service_or_category": "ml_training",
                "co2_value": 0.125,
                "unit": "kg",
                "cost_or_savings": 0,
                "optimization_potential": "medium",
            },
            {
                "audit_type": "personal",
                "timestamp": datetime.now().isoformat(),
                "service_or_category": "food",
                "co2_value": 45.2,
                "unit": "kg",
                "cost_or_savings": 200,
                "optimization_potential": "high",
            },
        ]

        writer.writerows(sample_rows)

    return filename


def main():
    """Main demonstration function"""

    print("🌍 CO2 REDUCTION PLANNER DEMO")
    print("=" * 50)
    print("Generates actionable plans with specific recommendations like:")
    print("• 'Use Graviton instances' (20% CO2 reduction)")
    print("• 'Eat plant-based' (40% CO2 reduction)")
    print("• 'Implement auto-scaling' (25% CO2 reduction)")
    print()

    # Generate reduction plan
    print("🎯 Generating CO2 reduction plan...")
    plan = generate_co2_reduction_plan(target_reduction=30.0)

    # Display plan
    print_reduction_plan(plan)

    # Export to CSV
    print(f"\n📊 Exporting anonymized data to CSV...")
    plan_csv = export_plan_to_csv(plan)
    print(f"✅ Plan exported to: {plan_csv}")

    # Create sample audit data
    audit_csv = create_sample_audit_data_csv()
    print(f"✅ Sample audit data: {audit_csv}")

    # Show CSV contents
    print(f"\n📋 CSV Export Sample:")
    with open(plan_csv) as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:3]):  # Show first 3 lines
            print(f"   {i+1}: {line.strip()}")

    print(f"\n🎉 DEMO COMPLETE!")
    print(f"📁 Files created:")
    print(f"   • {plan_csv} (reduction plan)")
    print(f"   • {audit_csv} (sample audit data)")
    print(f"🔐 Data anonymized for privacy")
    print(f"📈 Ready for analysis and implementation!")

    return plan, plan_csv, audit_csv


if __name__ == "__main__":
    main()
