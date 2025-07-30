#!/usr/bin/env python3
"""
Simple example showing how to use the _calculate_co2_from_metrics method.
"""

import time
from carbon_guard.local_auditor import LocalAuditor


def example_usage():
    """Example of how to use _calculate_co2_from_metrics method."""
    
    print("📊 Example: Using _calculate_co2_from_metrics method")
    print("=" * 60)
    
    # Create LocalAuditor instance
    auditor = LocalAuditor(config={
        'carbon_intensity': 0.3,  # 300g CO2/kWh
        'cpu_tdp_watts': 65,      # 65W CPU TDP
        'memory_power_per_gb': 3  # 3W per GB memory
    })
    
    # Example monitoring data (what you might collect from psutil)
    monitoring_data = [
        {
            'timestamp': time.time(),
            'system_cpu_percent': 45.2,
            'script_cpu_percent': 25.1,
            'memory_used_gb': 4.5,
            'script_memory_mb': 512,
            'disk_read_bytes': 1000000,
            'disk_write_bytes': 500000,
            'network_bytes_sent': 100000,
            'network_bytes_recv': 50000
        },
        {
            'timestamp': time.time() + 30,
            'system_cpu_percent': 52.8,
            'script_cpu_percent': 31.4,
            'memory_used_gb': 4.8,
            'script_memory_mb': 640,
            'disk_read_bytes': 1500000,
            'disk_write_bytes': 750000,
            'network_bytes_sent': 150000,
            'network_bytes_recv': 75000
        },
        {
            'timestamp': time.time() + 60,
            'system_cpu_percent': 38.1,
            'script_cpu_percent': 18.7,
            'memory_used_gb': 4.2,
            'script_memory_mb': 480,
            'disk_read_bytes': 1800000,
            'disk_write_bytes': 900000,
            'network_bytes_sent': 180000,
            'network_bytes_recv': 90000
        }
    ]
    
    # Calculate CO2 emissions
    result = auditor._calculate_co2_from_metrics(
        monitoring_data=monitoring_data,
        duration=60,  # 60 seconds
        carbon_intensity=0.3,  # 300g CO2/kWh
        cpu_tdp=65  # 65W CPU
    )
    
    # Display results
    print(f"🔋 Power Consumption:")
    print(f"   CPU: {result['power_breakdown']['cpu_watts']}W")
    print(f"   Memory: {result['power_breakdown']['memory_watts']}W")
    print(f"   Disk: {result['power_breakdown']['disk_watts']}W")
    print(f"   Network: {result['power_breakdown']['network_watts']}W")
    print(f"   Total: {result['power_breakdown']['total_watts']}W")
    
    print(f"\n📈 Resource Averages:")
    print(f"   System CPU: {result['avg_system_cpu_percent']}%")
    print(f"   Script CPU: {result['avg_script_cpu_percent']}%")
    print(f"   Memory: {result['avg_memory_gb']} GB")
    print(f"   Peak Memory: {result['peak_memory_gb']} GB")
    
    print(f"\n🌱 Carbon Footprint:")
    print(f"   Energy: {result['total_energy_kwh']} kWh")
    print(f"   CO2: {result['total_co2_kg']} kg")
    print(f"   CO2 per hour: {result['total_co2_kg'] / result['duration_hours']:.6f} kg/hour")
    
    print(f"\n⚡ Efficiency:")
    print(f"   CO2 per CPU%: {result['efficiency_metrics']['co2_per_cpu_percent']:.10f} kg")
    print(f"   Watts per CPU%: {result['efficiency_metrics']['watts_per_cpu_percent']} W")
    
    return result


def minimal_example():
    """Minimal example with just the required fields."""
    
    print(f"\n📊 Minimal Example:")
    print("=" * 30)
    
    auditor = LocalAuditor()
    
    # Minimal monitoring data
    minimal_data = [
        {
            'timestamp': time.time(),
            'system_cpu_percent': 30.0,
            'memory_used_gb': 3.0,
            'disk_read_bytes': 1000000,
            'disk_write_bytes': 500000
        },
        {
            'timestamp': time.time() + 30,
            'system_cpu_percent': 35.0,
            'memory_used_gb': 3.2,
            'disk_read_bytes': 1200000,
            'disk_write_bytes': 600000
        }
    ]
    
    result = auditor._calculate_co2_from_metrics(
        monitoring_data=minimal_data,
        duration=30,
        carbon_intensity=0.475,  # Default grid mix
        cpu_tdp=65
    )
    
    print(f"   Total CO2: {result['total_co2_kg']} kg")
    print(f"   Total Power: {result['power_breakdown']['total_watts']}W")
    print(f"   Avg CPU: {result['avg_system_cpu_percent']}%")
    
    return result


if __name__ == '__main__':
    # Run examples
    result1 = example_usage()
    result2 = minimal_example()
    
    print(f"\n✅ Examples completed!")
    print(f"💡 The method handles both detailed and minimal monitoring data")
