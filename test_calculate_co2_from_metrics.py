#!/usr/bin/env python3
"""
Test script to demonstrate the _calculate_co2_from_metrics method in LocalAuditor.
"""

import json
import time
from datetime import datetime

from carbon_guard.local_auditor import LocalAuditor


def create_sample_monitoring_data():
    """Create sample monitoring data for testing."""

    # Simulate 60 seconds of monitoring data with 1-second intervals
    base_time = time.time()
    monitoring_data = []

    for i in range(60):
        # Simulate varying resource usage over time
        timestamp = base_time + i

        # CPU usage varies (simulating a script that starts light, gets heavy, then finishes)
        if i < 10:
            system_cpu = 15 + (i * 2)  # Ramp up from 15% to 35%
            script_cpu = 5 + (i * 1.5)  # Script starts using CPU
        elif i < 40:
            system_cpu = 35 + (i - 10) * 1.5  # Peak usage period
            script_cpu = 15 + (i - 10) * 1.2
        else:
            system_cpu = max(10, 80 - (i - 40) * 2)  # Wind down
            script_cpu = max(2, 50 - (i - 40) * 1.8)

        # Memory usage gradually increases
        memory_used_gb = 4.0 + (i * 0.05)  # Starts at 4GB, increases to 7GB
        script_memory_mb = 100 + (i * 10)  # Script memory grows from 100MB to 700MB

        # Disk I/O accumulates over time
        disk_read_bytes = 1000000 + (i * 50000)  # 1MB + 50KB per second
        disk_write_bytes = 500000 + (i * 25000)  # 500KB + 25KB per second

        # Network usage (optional)
        network_bytes_sent = 100000 + (i * 5000)  # 100KB + 5KB per second
        network_bytes_recv = 50000 + (i * 2500)  # 50KB + 2.5KB per second

        sample = {
            "timestamp": timestamp,
            "system_cpu_percent": round(system_cpu, 1),
            "script_cpu_percent": round(script_cpu, 1),
            "memory_used_gb": round(memory_used_gb, 2),
            "script_memory_mb": round(script_memory_mb, 1),
            "disk_read_bytes": disk_read_bytes,
            "disk_write_bytes": disk_write_bytes,
            "network_bytes_sent": network_bytes_sent,
            "network_bytes_recv": network_bytes_recv,
        }

        monitoring_data.append(sample)

    return monitoring_data


def create_lightweight_monitoring_data():
    """Create sample data for a lightweight script."""

    base_time = time.time()
    monitoring_data = []

    for i in range(30):  # 30 seconds of light usage
        timestamp = base_time + i

        # Low resource usage
        system_cpu = 8 + (i % 5)  # Varies between 8-12%
        script_cpu = 2 + (i % 3)  # Script uses 2-4% CPU
        memory_used_gb = 2.5 + (i * 0.01)  # Minimal memory growth
        script_memory_mb = 50 + (i * 2)  # Small script memory

        # Minimal I/O
        disk_read_bytes = 100000 + (i * 1000)
        disk_write_bytes = 50000 + (i * 500)
        network_bytes_sent = 10000 + (i * 100)
        network_bytes_recv = 5000 + (i * 50)

        sample = {
            "timestamp": timestamp,
            "system_cpu_percent": round(system_cpu, 1),
            "script_cpu_percent": round(script_cpu, 1),
            "memory_used_gb": round(memory_used_gb, 2),
            "script_memory_mb": round(script_memory_mb, 1),
            "disk_read_bytes": disk_read_bytes,
            "disk_write_bytes": disk_write_bytes,
            "network_bytes_sent": network_bytes_sent,
            "network_bytes_recv": network_bytes_recv,
        }

        monitoring_data.append(sample)

    return monitoring_data


def create_intensive_monitoring_data():
    """Create sample data for a CPU-intensive script."""

    base_time = time.time()
    monitoring_data = []

    for i in range(120):  # 2 minutes of intensive usage
        timestamp = base_time + i

        # High resource usage
        system_cpu = 70 + (i % 20)  # High CPU usage 70-90%
        script_cpu = 60 + (i % 15)  # Script is the main consumer
        memory_used_gb = 8.0 + (i * 0.02)  # Memory grows significantly
        script_memory_mb = 500 + (i * 15)  # Large script memory footprint

        # Heavy I/O
        disk_read_bytes = 5000000 + (i * 100000)  # 5MB + 100KB per second
        disk_write_bytes = 2000000 + (i * 50000)  # 2MB + 50KB per second
        network_bytes_sent = 500000 + (i * 10000)  # Heavy network usage
        network_bytes_recv = 250000 + (i * 5000)

        sample = {
            "timestamp": timestamp,
            "system_cpu_percent": round(system_cpu, 1),
            "script_cpu_percent": round(script_cpu, 1),
            "memory_used_gb": round(memory_used_gb, 2),
            "script_memory_mb": round(script_memory_mb, 1),
            "disk_read_bytes": disk_read_bytes,
            "disk_write_bytes": disk_write_bytes,
            "network_bytes_sent": network_bytes_sent,
            "network_bytes_recv": network_bytes_recv,
        }

        monitoring_data.append(sample)

    return monitoring_data


def test_calculate_co2_from_metrics():
    """Test the _calculate_co2_from_metrics method with different scenarios."""

    print("🧪 Testing _calculate_co2_from_metrics method")
    print("=" * 60)

    # Create LocalAuditor instance
    config = {
        "carbon_intensity": 0.3,  # 300g CO2/kWh (typical grid mix)
        "cpu_tdp_watts": 65,  # Typical desktop CPU
        "memory_power_per_gb": 3,  # 3W per GB of memory
    }

    auditor = LocalAuditor(config=config)

    # Test scenarios
    scenarios = [
        {
            "name": "Lightweight Script",
            "data": create_lightweight_monitoring_data(),
            "duration": 30,
            "description": "Low CPU, minimal memory, light I/O",
        },
        {
            "name": "Moderate Script",
            "data": create_sample_monitoring_data(),
            "duration": 60,
            "description": "Variable CPU usage, growing memory, moderate I/O",
        },
        {
            "name": "Intensive Script",
            "data": create_intensive_monitoring_data(),
            "duration": 120,
            "description": "High CPU, large memory footprint, heavy I/O",
        },
    ]

    results = {}

    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        print(f"   Duration: {scenario['duration']} seconds")
        print(f"   Samples: {len(scenario['data'])}")

        # Calculate CO2 emissions
        result = auditor._calculate_co2_from_metrics(
            monitoring_data=scenario["data"],
            duration=scenario["duration"],
            carbon_intensity=config["carbon_intensity"],
            cpu_tdp=config["cpu_tdp_watts"],
        )

        results[scenario["name"]] = result

        # Display results
        if "error" in result:
            print(f"   ❌ Error: {result['error']}")
            continue

        print(f"\n   🔋 Power Consumption:")
        print(f"      CPU: {result['power_breakdown']['cpu_watts']}W")
        print(f"      Memory: {result['power_breakdown']['memory_watts']}W")
        print(f"      Disk: {result['power_breakdown']['disk_watts']}W")
        print(f"      Network: {result['power_breakdown']['network_watts']}W")
        print(f"      Total: {result['power_breakdown']['total_watts']}W")

        print(f"\n   📈 Resource Usage:")
        print(f"      Avg System CPU: {result['avg_system_cpu_percent']}%")
        print(f"      Avg Script CPU: {result['avg_script_cpu_percent']}%")
        print(f"      Avg Memory: {result['avg_memory_gb']} GB")
        print(f"      Peak Memory: {result['peak_memory_gb']} GB")
        print(f"      Disk I/O: {result['total_disk_io_gb']} GB")
        print(f"      Network: {result['total_network_gb']} GB")

        print(f"\n   🌱 Carbon Footprint:")
        print(f"      Energy: {result['total_energy_kwh']} kWh")
        print(f"      CO2: {result['total_co2_kg']} kg")
        print(
            f"      CO2 per hour: {result['total_co2_kg'] / result['duration_hours']:.6f} kg/hour"
        )
        print(
            f"      Annual CO2 (if run daily): {result['total_co2_kg'] * 365:.4f} kg/year"
        )

        print(f"\n   ⚡ Efficiency Metrics:")
        print(
            f"      CO2 per CPU%: {result['efficiency_metrics']['co2_per_cpu_percent']:.10f} kg"
        )
        print(
            f"      CO2 per GB memory: {result['efficiency_metrics']['co2_per_gb_memory']:.8f} kg"
        )
        print(
            f"      Watts per CPU%: {result['efficiency_metrics']['watts_per_cpu_percent']} W"
        )

        print(f"\n   📊 Power Distribution:")
        power_dist = result["resource_utilization"]["power_distribution"]
        print(f"      CPU: {power_dist['cpu_percent']}%")
        print(f"      Memory: {power_dist['memory_percent']}%")
        print(f"      Disk: {power_dist['disk_percent']}%")
        print(f"      Network: {power_dist['network_percent']}%")

    # Comparison analysis
    print(f"\n🔍 Comparative Analysis:")
    print("=" * 60)

    if len(results) > 1:
        # Sort by CO2 emissions
        sorted_results = sorted(
            results.items(), key=lambda x: x[1].get("total_co2_kg", 0)
        )

        print(f"   CO2 Emissions Ranking (lowest to highest):")
        for i, (name, result) in enumerate(sorted_results, 1):
            if "error" not in result:
                co2_per_hour = result["total_co2_kg"] / result["duration_hours"]
                print(
                    f"      {i}. {name}: {result['total_co2_kg']:.8f} kg ({co2_per_hour:.6f} kg/hour)"
                )

        # Calculate efficiency ratios
        if len(sorted_results) >= 2:
            most_efficient = sorted_results[0][1]
            least_efficient = sorted_results[-1][1]

            if most_efficient.get("total_co2_kg", 0) > 0:
                efficiency_ratio = least_efficient.get(
                    "total_co2_kg", 0
                ) / most_efficient.get("total_co2_kg", 1)
                print(f"\n   Efficiency Ratio: {efficiency_ratio:.2f}x")
                print(
                    f"   The least efficient script produces {efficiency_ratio:.2f}x more CO2"
                )

    # Save detailed results
    output_file = "co2_metrics_test_results.json"
    with open(output_file, "w") as f:
        json.dump(
            {
                "test_timestamp": datetime.now().isoformat(),
                "config": config,
                "scenarios": {name: result for name, result in results.items()},
                "summary": {
                    "total_scenarios": len(scenarios),
                    "successful_calculations": len(
                        [r for r in results.values() if "error" not in r]
                    ),
                    "total_samples_analyzed": sum(
                        r.get("samples_analyzed", 0) for r in results.values()
                    ),
                },
            },
            f,
            indent=2,
        )

    print(f"\n💾 Detailed results saved to: {output_file}")

    return results


def test_edge_cases():
    """Test edge cases for the _calculate_co2_from_metrics method."""

    print(f"\n🧪 Testing Edge Cases")
    print("=" * 40)

    auditor = LocalAuditor()

    # Test with empty data
    print("   Testing with empty monitoring data...")
    result = auditor._calculate_co2_from_metrics([], 60, 0.3, 65)
    assert "error" in result
    print(f"   ✅ Empty data handled correctly: {result['error']}")

    # Test with single data point
    print("   Testing with single data point...")
    single_point = [
        {
            "timestamp": time.time(),
            "system_cpu_percent": 50.0,
            "memory_used_gb": 4.0,
            "disk_read_bytes": 1000000,
            "disk_write_bytes": 500000,
        }
    ]
    result = auditor._calculate_co2_from_metrics(single_point, 60, 0.3, 65)
    assert result["total_co2_kg"] >= 0
    print(f"   ✅ Single point handled: {result['total_co2_kg']:.8f} kg CO2")

    # Test with zero carbon intensity
    print("   Testing with zero carbon intensity...")
    result = auditor._calculate_co2_from_metrics(single_point, 60, 0.0, 65)
    assert result["total_co2_kg"] == 0
    print(f"   ✅ Zero carbon intensity: {result['total_co2_kg']} kg CO2")

    # Test with missing optional fields
    print("   Testing with minimal data fields...")
    minimal_data = [
        {
            "timestamp": time.time(),
            "system_cpu_percent": 25.0,
            "memory_used_gb": 2.0
            # Missing disk and network data
        }
    ]
    result = auditor._calculate_co2_from_metrics(minimal_data, 30, 0.3, 65)
    assert result["total_co2_kg"] >= 0
    print(f"   ✅ Minimal data handled: {result['total_co2_kg']:.8f} kg CO2")

    print("   ✅ All edge cases passed!")


if __name__ == "__main__":
    print("🌱 Carbon Guard CLI - CO2 Metrics Calculation Test")
    print("=" * 80)

    # Run main tests
    results = test_calculate_co2_from_metrics()

    # Run edge case tests
    test_edge_cases()

    print(f"\n✅ All tests completed successfully!")
    print(f"📊 Check 'co2_metrics_test_results.json' for detailed results")
