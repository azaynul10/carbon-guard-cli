#!/usr/bin/env python3
"""
Test runner script to demonstrate moto mocks for EC2 CO2 calculations.
This script shows how the moto mocks work with sample EC2 data.
"""

import json

import boto3
from moto import mock_aws

# Import our AWS auditor
from carbon_guard.aws_auditor import AWSAuditor


@mock_aws
def demo_ec2_co2_calculation_with_moto():
    """Demonstrate EC2 CO2 calculation using moto mocks."""
    print("🧪 Demonstrating EC2 CO2 Calculation with Moto Mocks")
    print("=" * 60)

    # Set up AWS credentials for moto
    import os

    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

    # Create EC2 client and launch mock instances
    ec2_client = boto3.client("ec2", region_name="us-east-1")

    print("\n1. Launching mock EC2 instances...")

    # Launch different types of instances
    instances_to_launch = [
        {"type": "t2.micro", "count": 2, "name": "test-micro"},
        {"type": "m5.large", "count": 1, "name": "web-server"},
        {"type": "c5.xlarge", "count": 1, "name": "compute-server"},
    ]

    launched_instances = []

    for config in instances_to_launch:
        print(f"   Launching {config['count']}x {config['type']} instances...")

        response = ec2_client.run_instances(
            ImageId="ami-12345678",
            MinCount=config["count"],
            MaxCount=config["count"],
            InstanceType=config["type"],
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "Name", "Value": config["name"]},
                        {"Key": "Environment", "Value": "testing"},
                        {"Key": "MotoDemo", "Value": "true"},
                    ],
                }
            ],
        )

        for instance in response["Instances"]:
            launched_instances.append(
                {
                    "id": instance["InstanceId"],
                    "type": instance["InstanceType"],
                    "state": instance["State"]["Name"],
                }
            )

    print(f"   ✅ Successfully launched {len(launched_instances)} instances")

    # Stop one instance to test filtering
    print(f"\n2. Stopping one instance to test state filtering...")
    ec2_client.stop_instances(InstanceIds=[launched_instances[0]["id"]])
    print(f"   ✅ Stopped instance {launched_instances[0]['id']}")

    # Create AWS auditor and calculate CO2
    print(f"\n3. Calculating CO2 emissions using AWS Auditor...")
    auditor = AWSAuditor(region="us-east-1")

    # Perform CO2 audit
    result = auditor.audit_ec2(estimate_only=True)

    print(f"\n📊 CO2 Calculation Results:")
    print(f"   Total instances found: {result['total_instances']}")
    print(f"   Total CO2 emissions: {result['co2_kg_per_hour']:.8f} kg/hour")
    print(f"   Carbon intensity (us-east-1): {auditor.carbon_intensity} kg CO2/kWh")

    # Show detailed breakdown
    print(f"\n📋 Instance Details:")
    running_count = 0
    total_power = 0

    for instance in result["instances"]:
        # All instances returned by the auditor are running (it filters for running only)
        state_emoji = "🟢"  # All returned instances are running
        print(
            f"   {state_emoji} {instance['instance_id']} ({instance['instance_type']})"
        )
        print(f"      State: running")  # AWS auditor only returns running instances
        print(f"      Power: {instance['power_watts']}W")
        print(f"      CO2: {instance['co2_kg_per_hour']:.8f} kg/hour")
        print(f"      Cost: ${instance['estimated_cost_per_hour']:.4f}/hour")

        running_count += 1
        total_power += instance["power_watts"]

        # Show launch time if available
        if instance.get("launch_time"):
            print(f"      Launch time: {instance['launch_time']}")
        print()

    # Note about stopped instances
    stopped_count = len(launched_instances) - running_count
    if stopped_count > 0:
        print(
            f"   🔴 {stopped_count} stopped instance(s) not shown (filtered out by auditor)"
        )
        print()

    print(f"📈 Summary:")
    print(f"   Running instances: {running_count}")
    print(f"   Stopped instances: {stopped_count} (not included in CO2 calculation)")
    print(f"   Total power consumption: {total_power}W")
    print(f"   Total energy consumption: {total_power/1000:.3f} kWh/hour")
    print(f"   Total CO2 emissions: {result['co2_kg_per_hour']:.8f} kg/hour")
    print(f"   Daily CO2 emissions: {result['co2_kg_per_hour'] * 24:.6f} kg/day")
    print(
        f"   Annual CO2 emissions: {result['co2_kg_per_hour'] * 24 * 365:.4f} kg/year"
    )

    # Show power consumption by instance type
    print(f"\n⚡ Power Consumption by Instance Type:")
    power_by_type = {}
    for instance in result["instances"]:
        # All instances in result are running
        instance_type = instance["instance_type"]
        if instance_type not in power_by_type:
            power_by_type[instance_type] = {"count": 0, "total_power": 0}
        power_by_type[instance_type]["count"] += 1
        power_by_type[instance_type]["total_power"] += instance["power_watts"]

    for instance_type, data in power_by_type.items():
        avg_power = data["total_power"] / data["count"]
        print(
            f"   {instance_type}: {data['count']} instances, {avg_power}W each, {data['total_power']}W total"
        )

    # Calculate cost implications (example)
    print(f"\n💰 Estimated Cost Implications:")
    # Assuming $0.10 per kWh electricity cost
    electricity_cost_per_kwh = 0.10
    hourly_energy_cost = (total_power / 1000) * electricity_cost_per_kwh
    print(f"   Hourly electricity cost: ${hourly_energy_cost:.4f}")
    print(f"   Daily electricity cost: ${hourly_energy_cost * 24:.2f}")
    print(f"   Monthly electricity cost: ${hourly_energy_cost * 24 * 30:.2f}")

    # Carbon offset cost (example: $20 per ton CO2)
    carbon_offset_cost_per_kg = 0.02  # $20/1000kg
    hourly_offset_cost = result["co2_kg_per_hour"] * carbon_offset_cost_per_kg
    print(f"   Hourly carbon offset cost: ${hourly_offset_cost:.6f}")
    print(f"   Annual carbon offset cost: ${hourly_offset_cost * 24 * 365:.2f}")

    return result


@mock_aws
def demo_regional_carbon_intensity():
    """Demonstrate how different AWS regions affect CO2 calculations."""
    print(f"\n🌍 Regional Carbon Intensity Comparison")
    print("=" * 60)

    # Set up credentials
    import os

    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"

    regions_to_test = [
        ("us-east-1", "US East (N. Virginia)"),
        ("us-west-2", "US West (Oregon)"),
        ("eu-west-1", "Europe (Ireland)"),
        ("ap-southeast-1", "Asia Pacific (Singapore)"),
    ]

    instance_type = "m5.large"

    print(f"Comparing CO2 emissions for 1x {instance_type} instance across regions:\n")

    results = []

    for region, region_name in regions_to_test:
        # Create EC2 client for this region
        ec2_client = boto3.client("ec2", region_name=region)

        # Launch instance
        response = ec2_client.run_instances(
            ImageId="ami-12345678", MinCount=1, MaxCount=1, InstanceType=instance_type
        )

        # Create auditor for this region
        auditor = AWSAuditor(region=region)
        result = auditor.audit_ec2(estimate_only=True)

        results.append(
            {
                "region": region,
                "region_name": region_name,
                "carbon_intensity": auditor.carbon_intensity,
                "co2_kg_per_hour": result["co2_kg_per_hour"],
                "co2_kg_per_year": result["co2_kg_per_hour"] * 24 * 365,
            }
        )

    # Sort by CO2 emissions (lowest to highest)
    results.sort(key=lambda x: x["co2_kg_per_hour"])

    print(
        f"{'Region':<20} {'Carbon Intensity':<18} {'CO2/hour':<12} {'CO2/year':<12} {'Rank'}"
    )
    print("-" * 80)

    for i, result in enumerate(results, 1):
        rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "📍"
        print(
            f"{result['region']:<20} {result['carbon_intensity']:<18.6f} "
            f"{result['co2_kg_per_hour']:<12.8f} {result['co2_kg_per_year']:<12.4f} {rank_emoji}"
        )

    # Show savings potential
    highest_co2 = results[-1]["co2_kg_per_year"]
    lowest_co2 = results[0]["co2_kg_per_year"]
    savings_kg = highest_co2 - lowest_co2
    savings_percent = (savings_kg / highest_co2) * 100

    print(f"\n💡 Optimization Potential:")
    print(f"   Best region: {results[0]['region']} ({results[0]['region_name']})")
    print(f"   Worst region: {results[-1]['region']} ({results[-1]['region_name']})")
    print(
        f"   Annual CO2 savings: {savings_kg:.4f} kg ({savings_percent:.1f}% reduction)"
    )
    print(f"   Carbon offset value: ${savings_kg * 0.02:.2f}/year")


def main():
    """Run all demo functions."""
    print("🌱 Carbon Guard CLI - EC2 CO2 Calculation Demo with Moto Mocks")
    print("=" * 80)

    try:
        # Run main demo
        result = demo_ec2_co2_calculation_with_moto()

        # Run regional comparison
        demo_regional_carbon_intensity()

        print(f"\n✅ Demo completed successfully!")
        print(f"📝 The moto mocks provided realistic AWS responses for testing")
        print(f"🧪 All CO2 calculations were performed on mock data")

        # Save results to file
        output_file = "moto_demo_results.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"💾 Results saved to {output_file}")

    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
