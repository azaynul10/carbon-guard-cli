#!/usr/bin/env python3
"""
EC2 CO2 Calculator - Fetch instance hours from CloudWatch and estimate CO2 emissions
"""

import boto3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Carbon intensity factor (kg CO2 per kWh)
CARBON_INTENSITY_KG_PER_KWH = 0.3  # 300g/kWh = 0.3 kg/kWh

# Estimated power consumption for different EC2 instance types (watts)
INSTANCE_POWER_CONSUMPTION = {
    # General Purpose
    't2.nano': 5, 't2.micro': 10, 't2.small': 20, 't2.medium': 40, 't2.large': 80,
    't3.nano': 5, 't3.micro': 10, 't3.small': 20, 't3.medium': 40, 't3.large': 80,
    't3.xlarge': 160, 't3.2xlarge': 320,
    't4g.nano': 4, 't4g.micro': 8, 't4g.small': 16, 't4g.medium': 32, 't4g.large': 64,
    
    # Compute Optimized
    'c5.large': 70, 'c5.xlarge': 140, 'c5.2xlarge': 280, 'c5.4xlarge': 560,
    'c5.9xlarge': 1260, 'c5.12xlarge': 1680, 'c5.18xlarge': 2520, 'c5.24xlarge': 3360,
    'c6i.large': 65, 'c6i.xlarge': 130, 'c6i.2xlarge': 260, 'c6i.4xlarge': 520,
    
    # Memory Optimized
    'r5.large': 90, 'r5.xlarge': 180, 'r5.2xlarge': 360, 'r5.4xlarge': 720,
    'r5.8xlarge': 1440, 'r5.12xlarge': 2160, 'r5.16xlarge': 2880, 'r5.24xlarge': 4320,
    'r6i.large': 85, 'r6i.xlarge': 170, 'r6i.2xlarge': 340, 'r6i.4xlarge': 680,
    
    # Storage Optimized
    'i3.large': 100, 'i3.xlarge': 200, 'i3.2xlarge': 400, 'i3.4xlarge': 800,
    'i3.8xlarge': 1600, 'i3.16xlarge': 3200,
    
    # GPU Instances
    'p3.2xlarge': 3000, 'p3.8xlarge': 7000, 'p3.16xlarge': 14000,
    'g4dn.xlarge': 500, 'g4dn.2xlarge': 750, 'g4dn.4xlarge': 1200,
    
    # High Performance Computing
    'hpc6a.48xlarge': 5000,
}

def get_ec2_instances(region: str = 'us-east-1') -> List[Dict[str, Any]]:
    """
    Fetch all running EC2 instances in the specified region.
    
    Args:
        region: AWS region to query
        
    Returns:
        List of instance dictionaries with relevant information
    """
    ec2 = boto3.client('ec2', region_name=region)
    
    try:
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        )
        
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_info = {
                    'instance_id': instance['InstanceId'],
                    'instance_type': instance['InstanceType'],
                    'launch_time': instance['LaunchTime'],
                    'availability_zone': instance['Placement']['AvailabilityZone'],
                    'state': instance['State']['Name'],
                    'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                }
                instances.append(instance_info)
        
        return instances
        
    except Exception as e:
        print(f"Error fetching EC2 instances: {e}")
        return []

def get_instance_hours_from_cloudwatch(instance_id: str, start_time: datetime, 
                                     end_time: datetime, region: str = 'us-east-1') -> float:
    """
    Get instance running hours from CloudWatch metrics.
    
    Args:
        instance_id: EC2 instance ID
        start_time: Start time for the query
        end_time: End time for the query
        region: AWS region
        
    Returns:
        Number of hours the instance was running
    """
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    
    try:
        # Get StatusCheckFailed metric to determine if instance was running
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='StatusCheckFailed',
            Dimensions=[
                {'Name': 'InstanceId', 'Value': instance_id}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,  # 1 hour periods
            Statistics=['Average']
        )
        
        # If we have datapoints, the instance was running for those hours
        datapoints = response.get('Datapoints', [])
        running_hours = len(datapoints)
        
        # If no datapoints, try to calculate based on launch time
        if running_hours == 0:
            # Fallback: calculate hours based on time difference
            time_diff = end_time - start_time
            running_hours = time_diff.total_seconds() / 3600
        
        return running_hours
        
    except Exception as e:
        print(f"Error fetching CloudWatch data for {instance_id}: {e}")
        # Fallback calculation
        time_diff = end_time - start_time
        return time_diff.total_seconds() / 3600

def calculate_co2_emissions(instance_type: str, running_hours: float) -> Dict[str, float]:
    """
    Calculate CO2 emissions for an instance based on type and running hours.
    
    Args:
        instance_type: EC2 instance type
        running_hours: Number of hours the instance was running
        
    Returns:
        Dictionary with power consumption and CO2 emissions data
    """
    # Get power consumption for instance type (default to 50W if unknown)
    power_watts = INSTANCE_POWER_CONSUMPTION.get(instance_type, 50)
    
    # Convert to kWh
    power_kwh_per_hour = power_watts / 1000
    
    # Calculate total energy consumption
    total_energy_kwh = power_kwh_per_hour * running_hours
    
    # Calculate CO2 emissions
    co2_emissions_kg = total_energy_kwh * CARBON_INTENSITY_KG_PER_KWH
    
    return {
        'power_watts': power_watts,
        'power_kwh_per_hour': power_kwh_per_hour,
        'running_hours': running_hours,
        'total_energy_kwh': total_energy_kwh,
        'co2_emissions_kg': co2_emissions_kg,
        'co2_emissions_g': co2_emissions_kg * 1000
    }

def get_ec2_co2_report(region: str = 'us-east-1', days_back: int = 7) -> Dict[str, Any]:
    """
    Generate a comprehensive CO2 emissions report for EC2 instances.
    
    Args:
        region: AWS region to analyze
        days_back: Number of days to look back for usage data
        
    Returns:
        Dictionary containing the complete CO2 emissions report
    """
    print(f"🌍 Analyzing EC2 CO2 emissions in {region} for the last {days_back} days...")
    
    # Define time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days_back)
    
    # Get all running instances
    instances = get_ec2_instances(region)
    print(f"📊 Found {len(instances)} running EC2 instances")
    
    if not instances:
        return {
            'region': region,
            'time_period': {'start': start_time.isoformat(), 'end': end_time.isoformat()},
            'instances': [],
            'summary': {
                'total_instances': 0,
                'total_running_hours': 0,
                'total_energy_kwh': 0,
                'total_co2_kg': 0,
                'total_co2_g': 0
            }
        }
    
    # Analyze each instance
    instance_reports = []
    total_running_hours = 0
    total_energy_kwh = 0
    total_co2_kg = 0
    
    for i, instance in enumerate(instances, 1):
        print(f"⚡ Analyzing instance {i}/{len(instances)}: {instance['instance_id']} ({instance['instance_type']})")
        
        # Get running hours from CloudWatch
        running_hours = get_instance_hours_from_cloudwatch(
            instance['instance_id'], start_time, end_time, region
        )
        
        # Calculate CO2 emissions
        emissions_data = calculate_co2_emissions(instance['instance_type'], running_hours)
        
        # Combine instance info with emissions data
        instance_report = {
            **instance,
            **emissions_data,
            'analysis_period': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'days': days_back
            }
        }
        
        instance_reports.append(instance_report)
        
        # Update totals
        total_running_hours += running_hours
        total_energy_kwh += emissions_data['total_energy_kwh']
        total_co2_kg += emissions_data['co2_emissions_kg']
        
        print(f"  💡 Power: {emissions_data['power_watts']}W | "
              f"Hours: {running_hours:.1f} | "
              f"CO2: {emissions_data['co2_emissions_g']:.1f}g")
    
    # Create summary
    summary = {
        'total_instances': len(instances),
        'total_running_hours': total_running_hours,
        'total_energy_kwh': total_energy_kwh,
        'total_co2_kg': total_co2_kg,
        'total_co2_g': total_co2_kg * 1000,
        'carbon_intensity_kg_per_kwh': CARBON_INTENSITY_KG_PER_KWH,
        'average_co2_per_instance_kg': total_co2_kg / len(instances) if instances else 0
    }
    
    # Sort instances by CO2 emissions (highest first)
    instance_reports.sort(key=lambda x: x['co2_emissions_kg'], reverse=True)
    
    return {
        'region': region,
        'time_period': {
            'start': start_time.isoformat(),
            'end': end_time.isoformat(),
            'days_analyzed': days_back
        },
        'instances': instance_reports,
        'summary': summary,
        'carbon_intensity_note': f"Using {CARBON_INTENSITY_KG_PER_KWH} kg CO2/kWh (300g/kWh)"
    }

def print_co2_report(report: Dict[str, Any]) -> None:
    """Print a formatted CO2 emissions report."""
    print("\n" + "="*80)
    print("🌍 EC2 CO2 EMISSIONS REPORT")
    print("="*80)
    
    summary = report['summary']
    print(f"📍 Region: {report['region']}")
    print(f"📅 Period: {report['time_period']['days_analyzed']} days")
    print(f"🏭 Total Instances: {summary['total_instances']}")
    print(f"⏰ Total Running Hours: {summary['total_running_hours']:.1f}")
    print(f"⚡ Total Energy: {summary['total_energy_kwh']:.2f} kWh")
    print(f"🌿 Total CO2 Emissions: {summary['total_co2_kg']:.3f} kg ({summary['total_co2_g']:.1f}g)")
    print(f"📊 Average CO2 per Instance: {summary['average_co2_per_instance_kg']:.3f} kg")
    print(f"🔬 {report['carbon_intensity_note']}")
    
    print(f"\n📋 TOP CO2 EMITTERS:")
    print("-" * 80)
    print(f"{'Instance ID':<20} {'Type':<15} {'Hours':<8} {'Power':<8} {'CO2 (g)':<10}")
    print("-" * 80)
    
    for instance in report['instances'][:10]:  # Show top 10
        print(f"{instance['instance_id']:<20} "
              f"{instance['instance_type']:<15} "
              f"{instance['running_hours']:<8.1f} "
              f"{instance['power_watts']:<8}W "
              f"{instance['co2_emissions_g']:<10.1f}")
    
    if len(report['instances']) > 10:
        print(f"... and {len(report['instances']) - 10} more instances")

def save_report_to_file(report: Dict[str, Any], filename: str = None) -> str:
    """Save the CO2 report to a JSON file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ec2_co2_report_{report['region']}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n💾 Report saved to: {filename}")
    return filename

def main():
    """Main function to run the EC2 CO2 analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate CO2 emissions for EC2 instances')
    parser.add_argument('--region', default='us-east-1', help='AWS region (default: us-east-1)')
    parser.add_argument('--days', type=int, default=7, help='Days to analyze (default: 7)')
    parser.add_argument('--output', help='Output JSON file path')
    parser.add_argument('--quiet', action='store_true', help='Suppress detailed output')
    
    args = parser.parse_args()
    
    try:
        # Generate the CO2 report
        report = get_ec2_co2_report(region=args.region, days_back=args.days)
        
        # Print the report (unless quiet mode)
        if not args.quiet:
            print_co2_report(report)
        
        # Save to file
        output_file = save_report_to_file(report, args.output)
        
        # Print summary
        summary = report['summary']
        print(f"\n✅ Analysis complete!")
        print(f"🌿 Total CO2 emissions: {summary['total_co2_kg']:.3f} kg over {args.days} days")
        print(f"📊 Average per day: {summary['total_co2_kg']/args.days:.3f} kg/day")
        
        return report
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return None

if __name__ == "__main__":
    main()
