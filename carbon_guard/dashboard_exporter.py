"""Dashboard data export module for carbon footprint visualization."""

import csv
import glob
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logging.warning("Pandas not available. Excel export functionality disabled.")

logger = logging.getLogger(__name__)


class DashboardExporter:
    """Exports carbon footprint data for dashboard creation."""

    def __init__(self, config: Optional[Dict] = None):
        """Initialize dashboard exporter.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

    def export_dashboard_data(
        self,
        data_directory: str,
        output_path: str,
        export_format: str = "csv",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[str]:
        """Export carbon footprint data for dashboard creation.

        Args:
            data_directory: Directory containing audit data files
            output_path: Output file path (without extension)
            export_format: Export format ('csv', 'excel', 'json')
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)

        Returns:
            List of exported file paths
        """
        logger.info(f"Exporting dashboard data from {data_directory}")

        # Load and process all data files
        consolidated_data = self._load_and_consolidate_data(
            data_directory, start_date, end_date
        )

        exported_files = []

        if export_format == "csv":
            exported_files.extend(self._export_csv(consolidated_data, output_path))
        elif export_format == "excel":
            if PANDAS_AVAILABLE:
                exported_files.extend(
                    self._export_excel(consolidated_data, output_path)
                )
            else:
                logger.error("Pandas not available. Cannot export to Excel format.")
                raise RuntimeError("Pandas required for Excel export")
        elif export_format == "json":
            exported_files.extend(self._export_json(consolidated_data, output_path))
        else:
            raise ValueError(f"Unsupported export format: {export_format}")

        return exported_files

    def _load_and_consolidate_data(
        self,
        data_directory: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Load and consolidate data from all audit files."""
        consolidated_data = {
            "aws_audits": [],
            "local_audits": [],
            "personal_audits": [],
            "plans": [],
            "summary_metrics": [],
        }

        if not os.path.exists(data_directory):
            logger.warning(f"Data directory does not exist: {data_directory}")
            return consolidated_data

        # Parse date filters
        start_dt = self._parse_date(start_date) if start_date else None
        end_dt = self._parse_date(end_date) if end_date else None

        # Process all JSON files in the directory
        json_files = glob.glob(os.path.join(data_directory, "*.json"))

        for file_path in json_files:
            try:
                with open(file_path) as f:
                    data = json.load(f)

                # Extract timestamp for filtering
                file_timestamp = self._extract_timestamp(data, file_path)

                # Apply date filtering
                if self._should_include_file(file_timestamp, start_dt, end_dt):
                    self._categorize_and_add_data(data, file_path, consolidated_data)

            except Exception as e:
                logger.warning(f"Could not process file {file_path}: {e}")

        # Generate summary metrics
        consolidated_data["summary_metrics"] = self._generate_summary_metrics(
            consolidated_data
        )

        return consolidated_data

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            logger.warning(f"Invalid date format: {date_str}")
            return datetime.now()

    def _extract_timestamp(self, data: Dict[str, Any], file_path: str) -> datetime:
        """Extract timestamp from data or file."""
        # Try to get timestamp from data
        timestamp_fields = [
            "audit_timestamp",
            "created_at",
            "timestamp",
            "parsing_timestamp",
        ]

        for field in timestamp_fields:
            if field in data:
                try:
                    if isinstance(data[field], str):
                        # Try different timestamp formats
                        for fmt in [
                            "%Y-%m-%dT%H:%M:%S.%f",
                            "%Y-%m-%dT%H:%M:%S",
                            "%Y-%m-%d %H:%M:%S",
                        ]:
                            try:
                                return datetime.strptime(data[field], fmt)
                            except ValueError:
                                continue
                    elif isinstance(data[field], (int, float)):
                        return datetime.fromtimestamp(data[field])
                except Exception:
                    continue

        # Fallback to file modification time
        try:
            return datetime.fromtimestamp(os.path.getmtime(file_path))
        except Exception:
            return datetime.now()

    def _should_include_file(
        self,
        file_timestamp: datetime,
        start_dt: Optional[datetime],
        end_dt: Optional[datetime],
    ) -> bool:
        """Check if file should be included based on date filters."""
        if start_dt and file_timestamp < start_dt:
            return False
        if end_dt and file_timestamp > end_dt:
            return False
        return True

    def _categorize_and_add_data(
        self,
        data: Dict[str, Any],
        file_path: str,
        consolidated_data: Dict[str, List[Dict[str, Any]]],
    ):
        """Categorize data and add to appropriate list."""
        filename = os.path.basename(file_path).lower()

        # Add common metadata
        data_with_metadata = data.copy()
        data_with_metadata["source_file"] = file_path
        data_with_metadata["file_timestamp"] = self._extract_timestamp(
            data, file_path
        ).isoformat()

        # Categorize based on content and filename
        if "service" in data and data.get("service") in ["ec2", "rds", "lambda", "s3"]:
            consolidated_data["aws_audits"].append(data_with_metadata)
        elif "aws" in filename or any(
            service in data for service in ["ec2", "rds", "lambda", "s3"]
        ):
            consolidated_data["aws_audits"].append(data_with_metadata)
        elif "script_path" in data or "local" in filename:
            consolidated_data["local_audits"].append(data_with_metadata)
        elif "receipts" in data or "personal" in filename or "receipt" in filename:
            consolidated_data["personal_audits"].append(data_with_metadata)
        elif "plan_id" in data or "actions" in data:
            consolidated_data["plans"].append(data_with_metadata)
        else:
            # Try to infer from content
            if "co2_kg_per_hour" in data:
                consolidated_data["aws_audits"].append(data_with_metadata)
            elif "total_co2_kg" in data:
                consolidated_data["local_audits"].append(data_with_metadata)
            else:
                logger.warning(f"Could not categorize data from {file_path}")

    def _generate_summary_metrics(
        self, consolidated_data: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Generate summary metrics from consolidated data."""
        summary_metrics = []

        # AWS summary
        aws_data = consolidated_data["aws_audits"]
        if aws_data:
            total_aws_co2 = sum(item.get("co2_kg_per_hour", 0) for item in aws_data)
            total_aws_cost = sum(item.get("estimated_cost_usd", 0) for item in aws_data)

            summary_metrics.append(
                {
                    "category": "aws",
                    "metric": "total_co2_kg_per_hour",
                    "value": total_aws_co2,
                    "unit": "kg/hour",
                    "count": len(aws_data),
                }
            )

            summary_metrics.append(
                {
                    "category": "aws",
                    "metric": "total_estimated_cost_usd",
                    "value": total_aws_cost,
                    "unit": "USD/hour",
                    "count": len(aws_data),
                }
            )

        # Local summary
        local_data = consolidated_data["local_audits"]
        if local_data:
            total_local_co2 = sum(item.get("total_co2_kg", 0) for item in local_data)
            avg_execution_time = sum(
                item.get("execution_duration_seconds", 0) for item in local_data
            ) / len(local_data)

            summary_metrics.append(
                {
                    "category": "local",
                    "metric": "total_co2_kg",
                    "value": total_local_co2,
                    "unit": "kg",
                    "count": len(local_data),
                }
            )

            summary_metrics.append(
                {
                    "category": "local",
                    "metric": "avg_execution_time_seconds",
                    "value": avg_execution_time,
                    "unit": "seconds",
                    "count": len(local_data),
                }
            )

        # Personal summary
        personal_data = consolidated_data["personal_audits"]
        if personal_data:
            total_personal_co2 = 0
            for item in personal_data:
                if "summary" in item:
                    total_personal_co2 += item["summary"].get("total_co2_kg", 0)
                elif "carbon_footprint" in item:
                    total_personal_co2 += item["carbon_footprint"].get(
                        "total_co2_kg", 0
                    )

            summary_metrics.append(
                {
                    "category": "personal",
                    "metric": "total_co2_kg",
                    "value": total_personal_co2,
                    "unit": "kg",
                    "count": len(personal_data),
                }
            )

        return summary_metrics

    def _export_csv(
        self, consolidated_data: Dict[str, List[Dict[str, Any]]], output_path: str
    ) -> List[str]:
        """Export data to CSV files."""
        exported_files = []

        # Export AWS audits
        if consolidated_data["aws_audits"]:
            aws_file = f"{output_path}_aws_audits.csv"
            self._export_aws_csv(consolidated_data["aws_audits"], aws_file)
            exported_files.append(aws_file)

        # Export local audits
        if consolidated_data["local_audits"]:
            local_file = f"{output_path}_local_audits.csv"
            self._export_local_csv(consolidated_data["local_audits"], local_file)
            exported_files.append(local_file)

        # Export personal audits
        if consolidated_data["personal_audits"]:
            personal_file = f"{output_path}_personal_audits.csv"
            self._export_personal_csv(
                consolidated_data["personal_audits"], personal_file
            )
            exported_files.append(personal_file)

        # Export summary metrics
        if consolidated_data["summary_metrics"]:
            summary_file = f"{output_path}_summary.csv"
            self._export_summary_csv(consolidated_data["summary_metrics"], summary_file)
            exported_files.append(summary_file)

        return exported_files

    def _export_aws_csv(self, aws_data: List[Dict[str, Any]], output_file: str):
        """Export AWS audit data to CSV."""
        with open(output_file, "w", newline="") as csvfile:
            fieldnames = [
                "timestamp",
                "service",
                "region",
                "total_instances",
                "co2_kg_per_hour",
                "estimated_cost_usd",
                "source_file",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for item in aws_data:
                row = {
                    "timestamp": item.get("file_timestamp", ""),
                    "service": item.get("service", ""),
                    "region": item.get("region", ""),
                    "total_instances": item.get("total_instances", 0),
                    "co2_kg_per_hour": item.get("co2_kg_per_hour", 0),
                    "estimated_cost_usd": item.get("estimated_cost_usd", 0),
                    "source_file": item.get("source_file", ""),
                }
                writer.writerow(row)

    def _export_local_csv(self, local_data: List[Dict[str, Any]], output_file: str):
        """Export local audit data to CSV."""
        with open(output_file, "w", newline="") as csvfile:
            fieldnames = [
                "timestamp",
                "script_path",
                "execution_duration_seconds",
                "total_co2_kg",
                "total_energy_kwh",
                "avg_cpu_percent",
                "peak_memory_mb",
                "source_file",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for item in local_data:
                row = {
                    "timestamp": item.get("file_timestamp", ""),
                    "script_path": item.get("script_path", ""),
                    "execution_duration_seconds": item.get(
                        "execution_duration_seconds", 0
                    ),
                    "total_co2_kg": item.get("total_co2_kg", 0),
                    "total_energy_kwh": item.get("total_energy_kwh", 0),
                    "avg_cpu_percent": item.get("avg_cpu_percent", 0),
                    "peak_memory_mb": item.get("peak_memory_mb", 0),
                    "source_file": item.get("source_file", ""),
                }
                writer.writerow(row)

    def _export_personal_csv(
        self, personal_data: List[Dict[str, Any]], output_file: str
    ):
        """Export personal audit data to CSV."""
        with open(output_file, "w", newline="") as csvfile:
            fieldnames = [
                "timestamp",
                "total_receipts",
                "total_co2_kg",
                "food_co2_kg",
                "transport_co2_kg",
                "goods_co2_kg",
                "source_file",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for item in personal_data:
                # Handle different data structures
                if "summary" in item:
                    summary = item["summary"]
                    category_breakdown = summary.get("category_breakdown", {})
                else:
                    summary = item
                    category_breakdown = item.get("category_breakdown", {})

                row = {
                    "timestamp": item.get("file_timestamp", ""),
                    "total_receipts": summary.get("total_receipts", 1),
                    "total_co2_kg": summary.get("total_co2_kg", 0),
                    "food_co2_kg": category_breakdown.get("food", 0),
                    "transport_co2_kg": category_breakdown.get("transport", 0),
                    "goods_co2_kg": category_breakdown.get("goods", 0),
                    "source_file": item.get("source_file", ""),
                }
                writer.writerow(row)

    def _export_summary_csv(self, summary_data: List[Dict[str, Any]], output_file: str):
        """Export summary metrics to CSV."""
        with open(output_file, "w", newline="") as csvfile:
            fieldnames = ["category", "metric", "value", "unit", "count"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for item in summary_data:
                writer.writerow(item)

    def _export_excel(
        self, consolidated_data: Dict[str, List[Dict[str, Any]]], output_path: str
    ) -> List[str]:
        """Export data to Excel file with multiple sheets."""
        excel_file = f"{output_path}.xlsx"

        with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
            # AWS audits sheet
            if consolidated_data["aws_audits"]:
                aws_df = pd.DataFrame(consolidated_data["aws_audits"])
                aws_df.to_excel(writer, sheet_name="AWS_Audits", index=False)

            # Local audits sheet
            if consolidated_data["local_audits"]:
                local_df = pd.DataFrame(consolidated_data["local_audits"])
                local_df.to_excel(writer, sheet_name="Local_Audits", index=False)

            # Personal audits sheet
            if consolidated_data["personal_audits"]:
                personal_df = pd.DataFrame(consolidated_data["personal_audits"])
                personal_df.to_excel(writer, sheet_name="Personal_Audits", index=False)

            # Summary sheet
            if consolidated_data["summary_metrics"]:
                summary_df = pd.DataFrame(consolidated_data["summary_metrics"])
                summary_df.to_excel(writer, sheet_name="Summary", index=False)

        return [excel_file]

    def _export_json(
        self, consolidated_data: Dict[str, List[Dict[str, Any]]], output_path: str
    ) -> List[str]:
        """Export data to JSON file."""
        json_file = f"{output_path}.json"

        with open(json_file, "w") as f:
            json.dump(consolidated_data, f, indent=2, default=str)

        return [json_file]

    def get_summary_statistics(
        self,
        data_directory: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get summary statistics for the data directory.

        Args:
            data_directory: Directory containing audit data
            start_date: Start date filter
            end_date: End date filter

        Returns:
            Dictionary containing summary statistics
        """
        consolidated_data = self._load_and_consolidate_data(
            data_directory, start_date, end_date
        )

        total_records = (
            len(consolidated_data["aws_audits"])
            + len(consolidated_data["local_audits"])
            + len(consolidated_data["personal_audits"])
        )

        # Calculate total CO2
        total_co2_kg = 0

        # AWS CO2 (convert hourly to daily estimate)
        aws_co2_hourly = sum(
            item.get("co2_kg_per_hour", 0) for item in consolidated_data["aws_audits"]
        )
        total_co2_kg += aws_co2_hourly * 24  # Daily estimate

        # Local CO2
        total_co2_kg += sum(
            item.get("total_co2_kg", 0) for item in consolidated_data["local_audits"]
        )

        # Personal CO2
        for item in consolidated_data["personal_audits"]:
            if "summary" in item:
                total_co2_kg += item["summary"].get("total_co2_kg", 0)
            elif "carbon_footprint" in item:
                total_co2_kg += item["carbon_footprint"].get("total_co2_kg", 0)

        # Get date range
        all_timestamps = []
        for category_data in [
            consolidated_data["aws_audits"],
            consolidated_data["local_audits"],
            consolidated_data["personal_audits"],
        ]:
            for item in category_data:
                if "file_timestamp" in item:
                    all_timestamps.append(item["file_timestamp"])

        date_range = "N/A"
        if all_timestamps:
            all_timestamps.sort()
            start = all_timestamps[0][:10]  # Extract date part
            end = all_timestamps[-1][:10]
            date_range = f"{start} to {end}" if start != end else start

        return {
            "total_records": total_records,
            "aws_audits": len(consolidated_data["aws_audits"]),
            "local_audits": len(consolidated_data["local_audits"]),
            "personal_audits": len(consolidated_data["personal_audits"]),
            "plans": len(consolidated_data["plans"]),
            "date_range": date_range,
            "total_co2_kg": total_co2_kg,
            "avg_daily_co2_kg": (
                total_co2_kg / max(1, len({ts[:10] for ts in all_timestamps}))
                if all_timestamps
                else 0
            ),
        }

    def create_dashboard_template(self, output_path: str) -> str:
        """Create a basic dashboard template file.

        Args:
            output_path: Path for the dashboard template

        Returns:
            Path to created template file
        """
        template_content = """# Carbon Guard Dashboard Template

This template provides a starting point for creating visualizations from your carbon footprint data.

## Data Files

The following CSV files are generated by the dashboard export:

- `*_aws_audits.csv`: AWS infrastructure carbon emissions
- `*_local_audits.csv`: Local script execution emissions
- `*_personal_audits.csv`: Personal carbon footprint from receipts
- `*_summary.csv`: Summary metrics across all categories

## Recommended Visualizations

### 1. Time Series Charts
- Total CO2 emissions over time
- AWS vs Local vs Personal emissions trends
- Cost vs Carbon emissions correlation

### 2. Category Breakdowns
- Pie chart of emissions by category (AWS/Local/Personal)
- Bar chart of AWS services by emissions
- Personal emissions by category (food, transport, goods)

### 3. Efficiency Metrics
- CO2 per dollar spent (AWS)
- CO2 per execution (Local scripts)
- Emissions intensity trends

### 4. Goal Tracking
- Progress toward reduction targets
- Plan implementation status
- Actual vs projected reductions

## Tools for Visualization

- **Excel/Google Sheets**: Basic charts and pivot tables
- **Tableau/Power BI**: Advanced dashboards
- **Python (matplotlib/plotly)**: Custom visualizations
- **R (ggplot2)**: Statistical analysis and plots

## Sample Python Code

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load data
aws_data = pd.read_csv('dashboard_aws_audits.csv')
local_data = pd.read_csv('dashboard_local_audits.csv')

# Create time series plot
plt.figure(figsize=(12, 6))
plt.plot(aws_data['timestamp'], aws_data['co2_kg_per_hour'], label='AWS')
plt.plot(local_data['timestamp'], local_data['total_co2_kg'], label='Local')
plt.xlabel('Date')
plt.ylabel('CO2 Emissions (kg)')
plt.title('Carbon Emissions Over Time')
plt.legend()
plt.show()
```

## Next Steps

1. Import the CSV files into your preferred visualization tool
2. Create charts based on your specific needs
3. Set up automated reporting if desired
4. Share insights with your team or organization
"""

        template_file = f"{output_path}_dashboard_template.md"
        with open(template_file, "w") as f:
            f.write(template_content)

        return template_file
