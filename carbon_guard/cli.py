#!/usr/bin/env python3
"""Main CLI module for carbon-guard-cli."""

import json
import os
from typing import Optional

import boto3
import click

try:
    from moto import mock_aws

    MOTO_AVAILABLE = True
except ImportError:
    MOTO_AVAILABLE = False

from .aws_auditor import AWSAuditor
from .dashboard_exporter import DashboardExporter
from .dockerfile_optimizer import DockerfileOptimizer
from .local_auditor import LocalAuditor
from .plan_generator import PlanGenerator
from .receipt_parser import ReceiptParser
from .utils import load_config, setup_logging


def setup_mock_aws_resources(region: str = "us-east-1"):
    """Create mock AWS resources for testing without real AWS calls."""
    if not MOTO_AVAILABLE:
        raise click.ClickException(
            "moto library is required for mock mode. Install with: pip install moto"
        )

    # Create mock EC2 instances
    ec2 = boto3.client("ec2", region_name=region)

    # Create a VPC and subnet for the instances
    vpc_response = ec2.create_vpc(CidrBlock="10.0.0.0/16")
    vpc_id = vpc_response["Vpc"]["VpcId"]

    subnet_response = ec2.create_subnet(VpcId=vpc_id, CidrBlock="10.0.1.0/24")
    subnet_id = subnet_response["Subnet"]["SubnetId"]

    # Create security group
    sg_response = ec2.create_security_group(
        GroupName="mock-sg", Description="Mock security group for testing", VpcId=vpc_id
    )
    sg_id = sg_response["GroupId"]

    # Launch mock EC2 instances
    ec2.run_instances(
        ImageId="ami-12345678",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        SecurityGroupIds=[sg_id],
        SubnetId=subnet_id,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": "mock-instance-1"},
                    {"Key": "Environment", "Value": "test"},
                ],
            }
        ],
    )

    ec2.run_instances(
        ImageId="ami-12345678",
        MinCount=1,
        MaxCount=1,
        InstanceType="m5.large",
        SecurityGroupIds=[sg_id],
        SubnetId=subnet_id,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": "mock-instance-2"},
                    {"Key": "Environment", "Value": "production"},
                ],
            }
        ],
    )

    # Create mock S3 buckets
    s3 = boto3.client("s3", region_name=region)

    # Create buckets with different sizes
    bucket_names = ["mock-bucket-small", "mock-bucket-large", "mock-bucket-empty"]
    for bucket_name in bucket_names:
        if region == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )

    # Add some objects to simulate storage usage
    s3.put_object(
        Bucket="mock-bucket-small", Key="small-file.txt", Body=b"Small test content"
    )
    s3.put_object(
        Bucket="mock-bucket-large",
        Key="large-file.txt",
        Body=b"Large test content" * 1000,
    )

    # Create mock Lambda functions
    lambda_client = boto3.client("lambda", region_name=region)

    # Create IAM role for Lambda (moto requirement)
    iam = boto3.client("iam", region_name=region)
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }

    iam.create_role(
        RoleName="mock-lambda-role", AssumeRolePolicyDocument=json.dumps(trust_policy)
    )

    # Create Lambda functions
    lambda_client.create_function(
        FunctionName="mock-function-small",
        Runtime="python3.9",
        Role="arn:aws:iam::123456789012:role/mock-lambda-role",
        Handler="lambda_function.lambda_handler",
        Code={"ZipFile": b"mock code"},
        MemorySize=128,
        Tags={"Environment": "test"},
    )

    lambda_client.create_function(
        FunctionName="mock-function-large",
        Runtime="python3.9",
        Role="arn:aws:iam::123456789012:role/mock-lambda-role",
        Handler="lambda_function.lambda_handler",
        Code={"ZipFile": b"mock code"},
        MemorySize=1024,
        Tags={"Environment": "production"},
    )

    # Create mock RDS instances
    rds = boto3.client("rds", region_name=region)

    rds.create_db_instance(
        DBInstanceIdentifier="mock-db-small",
        DBInstanceClass="db.t3.micro",
        Engine="mysql",
        MasterUsername="admin",
        MasterUserPassword="password123",
        AllocatedStorage=20,
        Tags=[
            {"Key": "Environment", "Value": "test"},
            {"Key": "Name", "Value": "mock-database"},
        ],
    )

    click.echo("🎭 Mock AWS resources created successfully!")
    click.echo("  • 2 EC2 instances (t2.micro, m5.large)")
    click.echo("  • 3 S3 buckets with test data")
    click.echo("  • 2 Lambda functions (128MB, 1024MB)")
    click.echo("  • 1 RDS instance (db.t3.micro)")


@click.group()
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Path to configuration file"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def main(ctx, config: Optional[str], verbose: bool):
    """Carbon Guard CLI - Monitor and optimize your carbon footprint."""
    ctx.ensure_object(dict)

    # Setup logging
    setup_logging(verbose)

    # Load configuration
    if config:
        ctx.obj["config"] = load_config(config)
    else:
        ctx.obj["config"] = load_config()

    ctx.obj["verbose"] = verbose


@main.command()
@click.option(
    "--region",
    "-r",
    default="us-east-1",
    help="AWS region to audit (default: us-east-1)",
)
@click.option(
    "--services",
    "-s",
    multiple=True,
    help="Specific AWS services to audit (e.g., ec2, s3, rds)",
)
@click.option("--profile", "-p", help="AWS profile to use")
@click.option(
    "--output", "-o", type=click.Path(), help="Output file for results (JSON format)"
)
@click.option(
    "--estimate-only",
    is_flag=True,
    help="Only estimate CO2, don't fetch detailed metrics",
)
@click.option(
    "--mock",
    is_flag=True,
    help="Use mock AWS resources for testing (no real AWS calls)",
)
@click.pass_context
def audit_aws(
    ctx,
    region: str,
    services: tuple,
    profile: Optional[str],
    output: Optional[str],
    estimate_only: bool,
    mock: bool,
):
    """Estimate AWS infrastructure CO2 emissions via boto3."""

    if mock:
        if not MOTO_AVAILABLE:
            click.echo(
                "❌ Mock mode requires moto library. Install with: pip install moto",
                err=True,
            )
            raise click.Abort()

        click.echo(f"🎭 Auditing MOCK AWS infrastructure in region: {region}")

        # Use moto mock_aws decorator context
        with mock_aws():
            # Create mock resources
            setup_mock_aws_resources(region)

            # Create auditor and run audit
            auditor = AWSAuditor(
                region=region, profile=profile, config=ctx.obj.get("config", {})
            )

            # Perform audit on mock resources
            if services:
                results = auditor.audit_services(list(services), estimate_only)
            else:
                results = auditor.audit_all_services(estimate_only)
    else:
        click.echo(f"🌍 Auditing AWS infrastructure in region: {region}")

        try:
            auditor = AWSAuditor(
                region=region, profile=profile, config=ctx.obj.get("config", {})
            )

            # Perform audit
            if services:
                results = auditor.audit_services(list(services), estimate_only)
            else:
                results = auditor.audit_all_services(estimate_only)

        except Exception as e:
            click.echo(f"❌ Error auditing AWS: {str(e)}", err=True)
            raise click.Abort()

    # Display results (common for both mock and real)
    total_co2 = sum(service.get("co2_kg_per_hour", 0) for service in results.values())

    # Format CO2 values appropriately for small numbers
    def format_co2(value):
        if value == 0:
            return "0.0000"
        elif value < 0.0001:
            return f"{value:.2e}"  # Scientific notation for very small numbers
        else:
            return f"{value:.4f}"

    click.echo(f"\n📊 Total estimated CO2: {format_co2(total_co2)} kg/hour")

    for service_name, data in results.items():
        co2 = data.get("co2_kg_per_hour", 0)
        cost = data.get("estimated_cost_usd", 0)
        click.echo(f"  • {service_name}: {format_co2(co2)} kg/hour (${cost:.2f}/hour)")

    # Save to file if requested
    if output:
        with open(output, "w") as f:
            json.dump(results, f, indent=2, default=str)
        click.echo(f"\n💾 Results saved to: {output}")

        if mock:
            click.echo(
                "🎭 Note: Results are from mock AWS resources, not real infrastructure"
            )


@main.command()
@click.argument("script_path", type=click.Path(exists=True))
@click.option(
    "--duration",
    "-d",
    type=int,
    default=60,
    help="Monitoring duration in seconds (default: 60)",
)
@click.option(
    "--output", "-o", type=click.Path(), help="Output file for results (JSON format)"
)
@click.option(
    "--include-network", is_flag=True, help="Include network usage in calculations"
)
@click.pass_context
def audit_local(
    ctx, script_path: str, duration: int, output: Optional[str], include_network: bool
):
    """Estimate local script CO2 emissions by monitoring resource usage."""
    click.echo(f"🔍 Auditing local script: {script_path}")
    click.echo(f"⏱️  Monitoring duration: {duration} seconds")

    try:
        auditor = LocalAuditor(config=ctx.obj.get("config", {}))

        # Run audit
        results = auditor.audit_script(
            script_path=script_path, duration=duration, include_network=include_network
        )

        # Display results
        click.echo(f"\n📊 Audit Results:")
        click.echo(f"  • Total CO2 emissions: {results['total_co2_kg']:.6f} kg")
        click.echo(f"  • Average CPU usage: {results['avg_cpu_percent']:.1f}%")
        click.echo(f"  • Peak memory usage: {results['peak_memory_mb']:.1f} MB")
        click.echo(f"  • Total energy consumed: {results['total_energy_kwh']:.6f} kWh")

        if include_network:
            click.echo(f"  • Network data transferred: {results['network_mb']:.2f} MB")

        # Save to file if requested
        if output:
            with open(output, "w") as f:
                json.dump(results, f, indent=2, default=str)
            click.echo(f"\n💾 Results saved to: {output}")

    except Exception as e:
        click.echo(f"❌ Error auditing script: {str(e)}", err=True)
        raise click.Abort()


@main.command()
@click.argument("dockerfile_path", type=click.Path(exists=True))
@click.option(
    "--output", "-o", type=click.Path(), help="Output path for optimized Dockerfile"
)
@click.option(
    "--strategy",
    "-s",
    type=click.Choice(["size", "layers", "cache", "all"]),
    default="all",
    help="Optimization strategy",
)
@click.option(
    "--dry-run", is_flag=True, help="Show optimizations without applying them"
)
@click.pass_context
def optimize(
    ctx, dockerfile_path: str, output: Optional[str], strategy: str, dry_run: bool
):
    """Rewrite Dockerfiles for reduced carbon footprint."""
    click.echo(f"🐳 Optimizing Dockerfile: {dockerfile_path}")
    click.echo(f"📋 Strategy: {strategy}")

    try:
        optimizer = DockerfileOptimizer(config=ctx.obj.get("config", {}))

        # Analyze current Dockerfile
        analysis = optimizer.analyze_dockerfile(dockerfile_path)
        click.echo(f"\n📊 Current Dockerfile Analysis:")
        click.echo(f"  • Estimated layers: {analysis['layer_count']}")
        click.echo(f"  • Potential issues: {len(analysis['issues'])}")

        for issue in analysis["issues"]:
            click.echo(f"    - {issue}")

        # Generate optimizations
        optimizations = optimizer.generate_optimizations(dockerfile_path, strategy)

        if dry_run:
            click.echo(f"\n🔍 Proposed Optimizations:")
            for opt in optimizations:
                click.echo(f"  • {opt['description']}")
                click.echo(f"    Impact: {opt['impact']}")
        else:
            # Apply optimizations
            optimized_content = optimizer.apply_optimizations(
                dockerfile_path, optimizations
            )

            # Save optimized Dockerfile
            output_path = output or f"{dockerfile_path}.optimized"
            with open(output_path, "w") as f:
                f.write(optimized_content)

            click.echo(f"\n✅ Optimized Dockerfile saved to: {output_path}")
            click.echo(
                f"📉 Estimated CO2 reduction: {optimizer.estimate_savings(optimizations):.2f}%"
            )

    except Exception as e:
        click.echo(f"❌ Error optimizing Dockerfile: {str(e)}", err=True)
        raise click.Abort()


@main.command()
@click.argument("receipt_images", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file for parsed data (JSON format)",
)
@click.option(
    "--category",
    "-c",
    type=click.Choice(["transport", "energy", "food", "goods", "all"]),
    default="all",
    help="Filter by category",
)
@click.pass_context
def track_personal(ctx, receipt_images: tuple, output: Optional[str], category: str):
    """Parse receipt images to track personal carbon footprint."""
    if not receipt_images:
        click.echo("❌ Please provide at least one receipt image", err=True)
        raise click.Abort()

    click.echo(f"📸 Processing {len(receipt_images)} receipt image(s)")

    try:
        parser = ReceiptParser(config=ctx.obj.get("config", {}))
        all_results = []

        for image_path in receipt_images:
            click.echo(f"  Processing: {os.path.basename(image_path)}")

            # Parse receipt
            receipt_data = parser.parse_receipt(image_path)

            # Calculate carbon footprint
            carbon_data = parser.calculate_carbon_footprint(receipt_data, category)

            result = {
                "image_path": image_path,
                "receipt_data": receipt_data,
                "carbon_footprint": carbon_data,
            }
            all_results.append(result)

            # Display summary
            total_co2 = carbon_data.get("total_co2_kg", 0)
            click.echo(f"    CO2 footprint: {total_co2:.4f} kg")

        # Calculate totals
        total_co2 = sum(
            r["carbon_footprint"].get("total_co2_kg", 0) for r in all_results
        )
        click.echo(f"\n📊 Total CO2 footprint: {total_co2:.4f} kg")

        # Save results if requested
        if output:
            with open(output, "w") as f:
                json.dump(all_results, f, indent=2, default=str)
            click.echo(f"💾 Results saved to: {output}")

    except Exception as e:
        click.echo(f"❌ Error processing receipts: {str(e)}", err=True)
        raise click.Abort()


@main.command()
@click.option(
    "--target-reduction",
    "-t",
    type=float,
    default=20.0,
    help="Target CO2 reduction percentage (default: 20%)",
)
@click.option(
    "--timeframe", "-f", type=int, default=12, help="Timeframe in months (default: 12)"
)
@click.option(
    "--focus",
    type=click.Choice(["aws", "local", "personal", "all"]),
    default="all",
    help="Focus area for optimization",
)
@click.option(
    "--output", "-o", type=click.Path(), help="Output file for the plan (JSON format)"
)
@click.pass_context
def plan(
    ctx, target_reduction: float, timeframe: int, focus: str, output: Optional[str]
):
    """Generate CO2 reduction plans based on audit data."""
    click.echo(f"📋 Generating CO2 reduction plan")
    click.echo(f"🎯 Target reduction: {target_reduction}%")
    click.echo(f"⏰ Timeframe: {timeframe} months")

    try:
        generator = PlanGenerator(config=ctx.obj.get("config", {}))

        # Generate plan
        plan_data = generator.generate_plan(
            target_reduction=target_reduction,
            timeframe_months=timeframe,
            focus_area=focus,
        )

        # Display plan summary
        click.echo(f"\n📊 Reduction Plan Summary:")
        click.echo(f"  • Total actions: {len(plan_data['actions'])}")
        click.echo(
            f"  • Estimated total reduction: {plan_data['estimated_reduction']:.1f}%"
        )
        click.echo(f"  • Implementation cost: ${plan_data['estimated_cost']:.2f}")

        click.echo(f"\n🎯 Key Actions:")
        for i, action in enumerate(plan_data["actions"][:5], 1):
            click.echo(f"  {i}. {action['title']}")
            click.echo(
                f"     Impact: {action['co2_reduction']:.1f}% | "
                f"Effort: {action['effort_level']} | "
                f"Timeline: {action['timeline_weeks']} weeks"
            )

        if len(plan_data["actions"]) > 5:
            click.echo(f"     ... and {len(plan_data['actions']) - 5} more actions")

        # Save plan if requested
        if output:
            with open(output, "w") as f:
                json.dump(plan_data, f, indent=2, default=str)
            click.echo(f"\n💾 Plan saved to: {output}")

    except Exception as e:
        click.echo(f"❌ Error generating plan: {str(e)}", err=True)
        raise click.Abort()


@main.command()
@click.option(
    "--data-dir",
    "-d",
    type=click.Path(exists=True),
    help="Directory containing audit data files",
)
@click.option(
    "--output", "-o", type=click.Path(), required=True, help="Output CSV file path"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "excel", "json"]),
    default="csv",
    help="Export format",
)
@click.option("--date-range", help="Date range filter (YYYY-MM-DD:YYYY-MM-DD)")
@click.pass_context
def dashboard(
    ctx, data_dir: Optional[str], output: str, format: str, date_range: Optional[str]
):
    """Export carbon footprint data to CSV/Excel for dashboard creation."""
    click.echo(f"📊 Exporting dashboard data")
    click.echo(f"📁 Format: {format.upper()}")

    try:
        exporter = DashboardExporter(config=ctx.obj.get("config", {}))

        # Set data directory
        if not data_dir:
            data_dir = os.path.join(os.getcwd(), "carbon_data")

        # Parse date range if provided
        start_date, end_date = None, None
        if date_range:
            try:
                start_str, end_str = date_range.split(":")
                start_date = start_str
                end_date = end_str
            except ValueError:
                click.echo(
                    "❌ Invalid date range format. Use YYYY-MM-DD:YYYY-MM-DD", err=True
                )
                raise click.Abort()

        # Export data
        exported_files = exporter.export_dashboard_data(
            data_directory=data_dir,
            output_path=output,
            export_format=format,
            start_date=start_date,
            end_date=end_date,
        )

        click.echo(f"\n✅ Dashboard data exported successfully!")
        for file_path in exported_files:
            click.echo(f"  📄 {file_path}")

        # Display summary statistics
        stats = exporter.get_summary_statistics(data_dir, start_date, end_date)
        if stats:
            click.echo(f"\n📈 Summary Statistics:")
            click.echo(f"  • Total records: {stats.get('total_records', 0)}")
            click.echo(f"  • Date range: {stats.get('date_range', 'N/A')}")
            click.echo(f"  • Total CO2: {stats.get('total_co2_kg', 0):.4f} kg")
            click.echo(
                f"  • Average daily CO2: {stats.get('avg_daily_co2_kg', 0):.4f} kg"
            )

    except Exception as e:
        click.echo(f"❌ Error exporting dashboard data: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
