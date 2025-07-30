#!/usr/bin/env python3
"""
Clean boto3 example for EC2 CO2 calculation
Fetches EC2 instance hours from CloudWatch and estimates CO2 using 300g/kWh
"""

import boto3
from datetime import datetime, timedelta

def get_ec2_co2_emissions(region='us-east-1', days=7):
    """
    Fetch EC2 instance hours from CloudWatch and estimate CO2 emissions
    
    Args:
        region: AWS region (default: us-east-1)
        days: Number of days to analyze (default: 7)
    
    Returns:
        Dictionary with CO2 emissions data
    """
    
    # Configuration
    CARBON_INTENSITY = 0.3  # 300g/kWh = 0.3 kg CO2/kWh
    
    # Instance power consumption (watts)
    POWER_CONSUMPTION = {
        't2.micro': 10, 't2.small': 20, 't2.medium': 40, 't2.large': 80,
        't3.micro': 10, 't3.small': 20, 't3.medium': 40, 't3.large': 80,
        'm5.large': 80, 'm5.xlarge': 160, 'm5.2xlarge': 320,
        'c5.large': 70, 'c5.xlarge': 140, 'c5.2xlarge': 280,
        'r5.large': 90, 'r5.xlarge': 180, 'r5.2xlarge': 360,
    }
    
    # Initialize boto3 clients
    ec2 = boto3.client('ec2', region_name=region)
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    
    # Time range for analysis
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    print(f"🌍 Analyzing EC2 CO2 emissions in {region}")
    print(f"📅 Period: {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}")
    
    # Step 1: Get running EC2 instances
    try:
        response = ec2.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
        )
        
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({
                    'id': instance['InstanceId'],
                    'type': instance['InstanceType'],
                    'launch_time': instance['LaunchTime']
                })
        
        print(f"📊 Found {len(instances)} running instances")
        
    except Exception as e:
        print(f"❌ Error fetching instances: {e}")
        return None
    
    # Step 2: Get instance hours from CloudWatch and calculate CO2
    total_co2_kg = 0
    total_energy_kwh = 0
    results = []
    
    for instance in instances:
        instance_id = instance['id']
        instance_type = instance['type']
        
        try:
            # Get CloudWatch metrics to determine running hours
            cw_response = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour periods
                Statistics=['Average']
            )
            
            # Calculate running hours from datapoints
            datapoints = cw_response.get('Datapoints', [])
            running_hours = len(datapoints) if datapoints else days * 24
            
        except Exception as e:
            print(f"⚠️  CloudWatch error for {instance_id}: {e}")
            running_hours = days * 24  # Fallback: assume always running
        
        # Get power consumption (default 50W if unknown)
        power_watts = POWER_CONSUMPTION.get(instance_type, 50)
        
        # Calculate energy and CO2
        energy_kwh = (power_watts / 1000) * running_hours
        co2_kg = energy_kwh * CARBON_INTENSITY
        
        # Store results
        result = {
            'instance_id': instance_id,
            'instance_type': instance_type,
            'running_hours': running_hours,
            'power_watts': power_watts,
            'energy_kwh': energy_kwh,
            'co2_kg': co2_kg,
            'co2_g': co2_kg * 1000
        }
        results.append(result)
        
        # Update totals
        total_energy_kwh += energy_kwh
        total_co2_kg += co2_kg
        
        print(f"⚡ {instance_id} ({instance_type}): {power_watts}W × {running_hours:.1f}h = {co2_kg*1000:.1f}g CO2")
    
    # Step 3: Return summary
    return {
        'region': region,
        'days_analyzed': days,
        'carbon_intensity_kg_per_kwh': CARBON_INTENSITY,
        'total_instances': len(instances),
        'total_energy_kwh': total_energy_kwh,
        'total_co2_kg': total_co2_kg,
        'total_co2_g': total_co2_kg * 1000,
        'daily_average_kg': total_co2_kg / days,
        'instances': results
    }

# Example usage
if __name__ == "__main__":
    print("🚀 boto3 EC2 CO2 Calculator")
    print("📋 Key boto3 calls:")
    print("   • ec2.describe_instances() - Get running instances")
    print("   • cloudwatch.get_metric_statistics() - Get instance hours")
    print("   • Calculate CO2 using 300g/kWh carbon intensity")
    print()
    
    # To run with real AWS data, uncomment:
    # result = get_ec2_co2_emissions('us-east-1', 7)
    # if result:
    #     print(f"🌿 Total CO2: {result['total_co2_kg']:.3f} kg")
    #     print(f"📊 {result['total_instances']} instances over {result['days_analyzed']} days")
