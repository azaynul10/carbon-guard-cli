#!/usr/bin/env python3
"""
Simple EC2 CO2 Calculator - Basic example using boto3 and CloudWatch
"""

import boto3
from datetime import datetime, timedelta

def calculate_ec2_co2_simple():
    """Simple function to calculate EC2 CO2 emissions for us-east-1"""
    
    # Configuration
    REGION = 'us-east-1'
    CARBON_INTENSITY = 0.3  # 300g/kWh = 0.3 kg/kWh
    DAYS_BACK = 7
    
    # Instance power consumption estimates (watts)
    POWER_ESTIMATES = {
        't2.micro': 10, 't2.small': 20, 't2.medium': 40, 't2.large': 80,
        't3.micro': 10, 't3.small': 20, 't3.medium': 40, 't3.large': 80,
        'm5.large': 80, 'm5.xlarge': 160, 'm5.2xlarge': 320,
        'c5.large': 70, 'c5.xlarge': 140, 'c5.2xlarge': 280,
        'r5.large': 90, 'r5.xlarge': 180, 'r5.2xlarge': 360,
    }
    
    print(f"🌍 Calculating EC2 CO2 emissions for {REGION}")
    print(f"📅 Analyzing last {DAYS_BACK} days")
    print(f"🔬 Using {CARBON_INTENSITY} kg CO2/kWh carbon intensity")
    print("-" * 60)
    
    # Initialize AWS clients
    ec2 = boto3.client('ec2', region_name=REGION)
    cloudwatch = boto3.client('cloudwatch', region_name=REGION)
    
    # Time range for analysis
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=DAYS_BACK)
    
    try:
        # Get running EC2 instances
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
        
        if not instances:
            print("ℹ️  No running instances found")
            return
        
        total_co2_kg = 0
        total_energy_kwh = 0
        
        # Analyze each instance
        for instance in instances:
            instance_id = instance['id']
            instance_type = instance['type']
            
            # Get power estimate (default 50W if unknown)
            power_watts = POWER_ESTIMATES.get(instance_type, 50)
            
            # Calculate running hours
            # Simple approach: assume instance ran for the full period
            running_hours = DAYS_BACK * 24
            
            # Try to get more accurate data from CloudWatch
            try:
                cw_response = cloudwatch.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName='CPUUtilization',
                    Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,  # 1 hour
                    Statistics=['Average']
                )
                
                # If we have datapoints, use that count as running hours
                datapoints = cw_response.get('Datapoints', [])
                if datapoints:
                    running_hours = len(datapoints)
                    
            except Exception as e:
                print(f"⚠️  CloudWatch error for {instance_id}: {e}")
                # Keep the default calculation
            
            # Calculate energy and CO2
            energy_kwh = (power_watts / 1000) * running_hours
            co2_kg = energy_kwh * CARBON_INTENSITY
            co2_g = co2_kg * 1000
            
            # Update totals
            total_energy_kwh += energy_kwh
            total_co2_kg += co2_kg
            
            # Print instance details
            print(f"🖥️  {instance_id} ({instance_type})")
            print(f"   💡 Power: {power_watts}W | Hours: {running_hours:.1f} | CO2: {co2_g:.1f}g")
        
        print("-" * 60)
        print(f"📈 SUMMARY:")
        print(f"   ⚡ Total Energy: {total_energy_kwh:.2f} kWh")
        print(f"   🌿 Total CO2: {total_co2_kg:.3f} kg ({total_co2_kg * 1000:.1f}g)")
        print(f"   📊 Average per day: {total_co2_kg / DAYS_BACK:.3f} kg/day")
        print(f"   🏭 Average per instance: {total_co2_kg / len(instances):.3f} kg")
        
        # CO2 equivalents for context
        print(f"\n🌍 CO2 EQUIVALENTS:")
        km_driven = total_co2_kg / 0.21  # Assume 210g CO2/km for average car
        print(f"   🚗 Equivalent to driving {km_driven:.1f} km")
        
        trees_needed = total_co2_kg / 21.77  # One tree absorbs ~22kg CO2/year
        print(f"   🌳 Would need {trees_needed:.2f} trees for 1 year to offset")
        
        return {
            'total_instances': len(instances),
            'total_energy_kwh': total_energy_kwh,
            'total_co2_kg': total_co2_kg,
            'daily_average_kg': total_co2_kg / DAYS_BACK,
            'instances': instances
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    result = calculate_ec2_co2_simple()
