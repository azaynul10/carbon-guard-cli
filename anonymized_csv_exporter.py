#!/usr/bin/env python3
"""
Anonymized CSV Exporter
Exports CO2 audit data and reduction plans to CSV with anonymization
"""

import csv
import hashlib
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List


class AnonymizedCSVExporter:
    """Exports audit data to CSV with anonymization for privacy"""

    def __init__(self, anonymization_key: str = None):
        """Initialize exporter with anonymization settings"""
        self.anonymization_key = anonymization_key or str(uuid.uuid4())
        self.anonymized_mappings = {}

    def anonymize_identifier(self, identifier: str, prefix: str = "anon") -> str:
        """Anonymize identifiers using consistent hashing"""

        if identifier in self.anonymized_mappings:
            return self.anonymized_mappings[identifier]

        # Create consistent hash
        hash_input = f"{self.anonymization_key}:{identifier}"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:8]

        anonymized = f"{prefix}_{hash_value}"
        self.anonymized_mappings[identifier] = anonymized

        return anonymized

    def anonymize_location(self, location: str) -> str:
        """Anonymize location data"""

        # Map regions to generic identifiers
        region_mappings = {
            "us-east-1": "region_a",
            "us-west-2": "region_b",
            "eu-west-1": "region_c",
            "ap-southeast-1": "region_d",
        }

        return region_mappings.get(location, f"region_{hash(location) % 10}")

    def load_audit_data(self, data_directory: str = "carbon_data") -> Dict[str, List]:
        """Load all audit data from directory"""

        data = {
            "aws_audits": [],
            "local_audits": [],
            "personal_audits": [],
            "reduction_plans": [],
        }

        if not os.path.exists(data_directory):
            return data

        for filename in os.listdir(data_directory):
            if filename.endswith(".json"):
                filepath = os.path.join(data_directory, filename)
                try:
                    with open(filepath) as f:
                        file_data = json.load(f)

                    # Categorize data
                    if "service" in file_data or any(
                        s in file_data for s in ["ec2", "rds", "lambda", "s3"]
                    ):
                        data["aws_audits"].append(file_data)
                    elif "script_path" in file_data or "total_co2_kg" in file_data:
                        data["local_audits"].append(file_data)
                    elif "receipts" in file_data or "items" in file_data:
                        data["personal_audits"].append(file_data)
                    elif "selected_actions" in file_data or "plan_id" in file_data:
                        data["reduction_plans"].append(file_data)

                except Exception as e:
                    print(f"⚠️  Could not load {filename}: {e}")

        return data

    def export_aws_data_csv(self, aws_data: List[Dict], output_file: str) -> str:
        """Export AWS audit data to anonymized CSV"""

        with open(output_file, "w", newline="") as csvfile:
            fieldnames = [
                "audit_id",
                "timestamp",
                "region",
                "service_type",
                "resource_count",
                "co2_kg_per_hour",
                "estimated_cost_usd",
                "optimization_potential",
                "instance_types",
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for audit in aws_data:
                # Anonymize data
                audit_id = self.anonymize_identifier(
                    audit.get("audit_timestamp", str(datetime.now())), "aws_audit"
                )

                region = self.anonymize_location(audit.get("region", "unknown"))

                # Extract instance types without revealing specific configurations
                instance_types = []
                if "instances" in audit:
                    types = {
                        inst.get("instance_type", "unknown")
                        for inst in audit["instances"]
                    }
                    instance_types = [
                        t.split(".")[0] for t in types
                    ]  # Keep family, remove size

                row = {
                    "audit_id": audit_id,
                    "timestamp": audit.get("audit_timestamp", ""),
                    "region": region,
                    "service_type": audit.get("service", "unknown"),
                    "resource_count": audit.get("total_instances", 0),
                    "co2_kg_per_hour": round(audit.get("co2_kg_per_hour", 0), 6),
                    "estimated_cost_usd": round(audit.get("estimated_cost_usd", 0), 2),
                    "optimization_potential": self._calculate_optimization_potential(
                        audit
                    ),
                    "instance_types": ",".join(set(instance_types)),
                }

                writer.writerow(row)

        return output_file

    def export_local_data_csv(self, local_data: List[Dict], output_file: str) -> str:
        """Export local audit data to anonymized CSV"""

        with open(output_file, "w", newline="") as csvfile:
            fieldnames = [
                "audit_id",
                "timestamp",
                "execution_duration_seconds",
                "co2_kg",
                "energy_kwh",
                "avg_cpu_percent",
                "peak_memory_mb",
                "script_category",
                "optimization_applied",
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for audit in local_data:
                # Anonymize script path
                script_path = audit.get("script_path", "unknown")
                script_category = self._categorize_script(script_path)

                audit_id = self.anonymize_identifier(
                    f"{script_path}_{audit.get('audit_timestamp', '')}", "local_audit"
                )

                row = {
                    "audit_id": audit_id,
                    "timestamp": audit.get("audit_timestamp", ""),
                    "execution_duration_seconds": audit.get(
                        "execution_duration_seconds", 0
                    ),
                    "co2_kg": round(audit.get("total_co2_kg", 0), 8),
                    "energy_kwh": round(audit.get("total_energy_kwh", 0), 8),
                    "avg_cpu_percent": round(audit.get("avg_cpu_percent", 0), 2),
                    "peak_memory_mb": round(audit.get("peak_memory_mb", 0), 1),
                    "script_category": script_category,
                    "optimization_applied": audit.get("execution_successful", False),
                }

                writer.writerow(row)

        return output_file

    def export_personal_data_csv(
        self, personal_data: List[Dict], output_file: str
    ) -> str:
        """Export personal audit data to anonymized CSV"""

        with open(output_file, "w", newline="") as csvfile:
            fieldnames = [
                "audit_id",
                "timestamp",
                "total_items",
                "total_co2_kg",
                "food_co2_kg",
                "transport_co2_kg",
                "goods_co2_kg",
                "high_impact_categories",
                "reduction_potential",
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for audit in personal_data:
                audit_id = self.anonymize_identifier(
                    audit.get("analysis_timestamp", str(datetime.now())),
                    "personal_audit",
                )

                # Extract category data
                if "summary" in audit:
                    summary = audit["summary"]
                    category_breakdown = summary.get("category_breakdown", {})
                else:
                    summary = audit
                    category_breakdown = audit.get("category_breakdown", {})

                # Identify high-impact categories
                high_impact = []
                for category, co2 in category_breakdown.items():
                    if co2 > 5.0:  # More than 5kg CO2
                        high_impact.append(category)

                row = {
                    "audit_id": audit_id,
                    "timestamp": audit.get("analysis_timestamp", ""),
                    "total_items": summary.get("total_receipts", 0),
                    "total_co2_kg": round(summary.get("total_co2_kg", 0), 3),
                    "food_co2_kg": round(category_breakdown.get("food", 0), 3),
                    "transport_co2_kg": round(
                        category_breakdown.get("transport", 0), 3
                    ),
                    "goods_co2_kg": round(category_breakdown.get("goods", 0), 3),
                    "high_impact_categories": ",".join(high_impact),
                    "reduction_potential": self._calculate_personal_reduction_potential(
                        category_breakdown
                    ),
                }

                writer.writerow(row)

        return output_file

    def export_reduction_plans_csv(
        self, plans_data: List[Dict], output_file: str
    ) -> str:
        """Export reduction plans to anonymized CSV"""

        with open(output_file, "w", newline="") as csvfile:
            fieldnames = [
                "plan_id",
                "created_at",
                "target_reduction_percent",
                "timeframe_months",
                "focus_areas",
                "actions_count",
                "estimated_reduction_percent",
                "estimated_cost_impact",
                "success_probability",
                "top_actions",
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for plan in plans_data:
                plan_id = self.anonymize_identifier(plan.get("plan_id", ""), "plan")

                # Get top 3 actions
                actions = plan.get("selected_actions", [])
                top_actions = [action["action"] for action in actions[:3]]

                metrics = plan.get("estimated_metrics", {})

                row = {
                    "plan_id": plan_id,
                    "created_at": plan.get("created_at", ""),
                    "target_reduction_percent": plan.get("target_reduction_percent", 0),
                    "timeframe_months": plan.get("timeframe_months", 0),
                    "focus_areas": ",".join(plan.get("focus_areas", [])),
                    "actions_count": len(actions),
                    "estimated_reduction_percent": round(
                        metrics.get("total_reduction_percent", 0), 1
                    ),
                    "estimated_cost_impact": round(
                        metrics.get("total_cost_impact_usd", 0), 2
                    ),
                    "success_probability": round(
                        metrics.get("success_probability", 0), 3
                    ),
                    "top_actions": "; ".join(top_actions),
                }

                writer.writerow(row)

        return output_file

    def export_summary_csv(self, all_data: Dict, output_file: str) -> str:
        """Export summary statistics to CSV"""

        with open(output_file, "w", newline="") as csvfile:
            fieldnames = [
                "metric_category",
                "metric_name",
                "value",
                "unit",
                "data_points",
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # AWS summary
            aws_data = all_data["aws_audits"]
            if aws_data:
                total_aws_co2 = sum(
                    audit.get("co2_kg_per_hour", 0) for audit in aws_data
                )
                total_aws_cost = sum(
                    audit.get("estimated_cost_usd", 0) for audit in aws_data
                )

                writer.writerow(
                    {
                        "metric_category": "aws",
                        "metric_name": "total_co2_kg_per_hour",
                        "value": round(total_aws_co2, 6),
                        "unit": "kg/hour",
                        "data_points": len(aws_data),
                    }
                )

                writer.writerow(
                    {
                        "metric_category": "aws",
                        "metric_name": "total_cost_usd_per_hour",
                        "value": round(total_aws_cost, 2),
                        "unit": "USD/hour",
                        "data_points": len(aws_data),
                    }
                )

            # Local summary
            local_data = all_data["local_audits"]
            if local_data:
                total_local_co2 = sum(
                    audit.get("total_co2_kg", 0) for audit in local_data
                )
                avg_execution_time = sum(
                    audit.get("execution_duration_seconds", 0) for audit in local_data
                ) / len(local_data)

                writer.writerow(
                    {
                        "metric_category": "local",
                        "metric_name": "total_co2_kg",
                        "value": round(total_local_co2, 8),
                        "unit": "kg",
                        "data_points": len(local_data),
                    }
                )

                writer.writerow(
                    {
                        "metric_category": "local",
                        "metric_name": "avg_execution_time_seconds",
                        "value": round(avg_execution_time, 2),
                        "unit": "seconds",
                        "data_points": len(local_data),
                    }
                )

            # Personal summary
            personal_data = all_data["personal_audits"]
            if personal_data:
                total_personal_co2 = 0
                for audit in personal_data:
                    if "summary" in audit:
                        total_personal_co2 += audit["summary"].get("total_co2_kg", 0)
                    else:
                        total_personal_co2 += audit.get("total_co2_kg", 0)

                writer.writerow(
                    {
                        "metric_category": "personal",
                        "metric_name": "total_co2_kg",
                        "value": round(total_personal_co2, 3),
                        "unit": "kg",
                        "data_points": len(personal_data),
                    }
                )

        return output_file

    def export_all_data(
        self,
        output_prefix: str = "carbon_data_export",
        data_directory: str = "carbon_data",
    ) -> List[str]:
        """Export all data to anonymized CSV files"""

        print("📊 Loading audit data...")
        all_data = self.load_audit_data(data_directory)

        exported_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Export AWS data
        if all_data["aws_audits"]:
            aws_file = f"{output_prefix}_aws_{timestamp}.csv"
            self.export_aws_data_csv(all_data["aws_audits"], aws_file)
            exported_files.append(aws_file)
            print(f"✅ AWS data exported: {aws_file}")

        # Export local data
        if all_data["local_audits"]:
            local_file = f"{output_prefix}_local_{timestamp}.csv"
            self.export_local_data_csv(all_data["local_audits"], local_file)
            exported_files.append(local_file)
            print(f"✅ Local data exported: {local_file}")

        # Export personal data
        if all_data["personal_audits"]:
            personal_file = f"{output_prefix}_personal_{timestamp}.csv"
            self.export_personal_data_csv(all_data["personal_audits"], personal_file)
            exported_files.append(personal_file)
            print(f"✅ Personal data exported: {personal_file}")

        # Export reduction plans
        if all_data["reduction_plans"]:
            plans_file = f"{output_prefix}_plans_{timestamp}.csv"
            self.export_reduction_plans_csv(all_data["reduction_plans"], plans_file)
            exported_files.append(plans_file)
            print(f"✅ Reduction plans exported: {plans_file}")

        # Export summary
        summary_file = f"{output_prefix}_summary_{timestamp}.csv"
        self.export_summary_csv(all_data, summary_file)
        exported_files.append(summary_file)
        print(f"✅ Summary exported: {summary_file}")

        # Create anonymization key file
        key_file = f"{output_prefix}_anonymization_key_{timestamp}.txt"
        with open(key_file, "w") as f:
            f.write(f"Anonymization Key: {self.anonymization_key}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("Note: Keep this key secure for data de-anonymization if needed.\n")

        print(f"🔐 Anonymization key saved: {key_file}")

        return exported_files

    def _calculate_optimization_potential(self, audit: Dict) -> str:
        """Calculate optimization potential for AWS resources"""

        co2_per_hour = audit.get("co2_kg_per_hour", 0)

        if co2_per_hour > 10:
            return "high"
        elif co2_per_hour > 1:
            return "medium"
        else:
            return "low"

    def _categorize_script(self, script_path: str) -> str:
        """Categorize script based on path/name"""

        script_lower = script_path.lower()

        if any(word in script_lower for word in ["test", "demo", "example"]):
            return "test"
        elif any(word in script_lower for word in ["ml", "model", "train", "ai"]):
            return "machine_learning"
        elif any(word in script_lower for word in ["data", "process", "etl"]):
            return "data_processing"
        elif any(word in script_lower for word in ["web", "server", "api"]):
            return "web_service"
        else:
            return "general"

    def _calculate_personal_reduction_potential(self, category_breakdown: Dict) -> str:
        """Calculate reduction potential for personal emissions"""

        total_co2 = sum(category_breakdown.values())

        # High potential if meat/transport dominates
        meat_co2 = category_breakdown.get("meat", 0) + category_breakdown.get("beef", 0)
        transport_co2 = category_breakdown.get("transport", 0)

        if (meat_co2 + transport_co2) / total_co2 > 0.6 if total_co2 > 0 else False:
            return "high"
        elif total_co2 > 20:  # More than 20kg CO2
            return "medium"
        else:
            return "low"


def main():
    """Main function for CSV export"""

    import argparse

    parser = argparse.ArgumentParser(description="Export anonymized CO2 data to CSV")
    parser.add_argument(
        "--output-prefix", default="carbon_data_export", help="Prefix for output files"
    )
    parser.add_argument(
        "--data-dir", default="carbon_data", help="Directory containing audit data"
    )
    parser.add_argument(
        "--anonymization-key", help="Custom anonymization key (optional)"
    )

    args = parser.parse_args()

    print("🌍 CO2 Data Export with Anonymization")
    print("=" * 50)

    # Create exporter
    exporter = AnonymizedCSVExporter(args.anonymization_key)

    # Export all data
    exported_files = exporter.export_all_data(
        output_prefix=args.output_prefix, data_directory=args.data_dir
    )

    print(f"\n✅ Export complete!")
    print(f"📁 {len(exported_files)} files created")
    print(f"🔐 Data anonymized for privacy protection")

    # Show file sizes
    total_size = 0
    for file_path in exported_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            total_size += size
            print(f"   📄 {file_path}: {size:,} bytes")

    print(f"📊 Total export size: {total_size:,} bytes")


if __name__ == "__main__":
    main()
