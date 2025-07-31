#!/usr/bin/env python3

from carbon_guard.aws_auditor import AWSAuditor

# Create auditor and check values
auditor = AWSAuditor(region="us-east-1")
print(f"Carbon intensity: {auditor.carbon_intensity}")
print(f'M5.large power: {auditor.INSTANCE_POWER_CONSUMPTION["m5.large"]}')

# Calculate expected CO2 per hour for 1 instance
power_kwh = 80 / 1000  # 80W converted to kWh
co2_per_hour = power_kwh * auditor.carbon_intensity
print(f"Expected CO2 per hour for 1 instance: {co2_per_hour}")
print(f"Expected CO2 per hour for 2 instances: {co2_per_hour * 2}")
print(f"Expected CO2 per hour for 4 instances: {co2_per_hour * 4}")
print(f"Expected CO2 per hour for 8 instances: {co2_per_hour * 8}")
