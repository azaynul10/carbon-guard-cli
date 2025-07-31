#!/usr/bin/env python3
"""
Core psutil example for CPU monitoring and CO2 estimation
Shows the essential psutil functions for monitoring Python script CPU usage
"""

import subprocess
import sys
import time

import psutil


def monitor_python_script_co2(script_path: str, duration: int = 60):
    """
    Monitor Python script CPU usage and estimate CO2 with 300g/kWh

    Core psutil functions demonstrated:
    - psutil.cpu_percent() - Get CPU usage percentage
    - psutil.Process() - Monitor specific process
    - psutil.virtual_memory() - Get memory usage
    - psutil.cpu_count() - Get CPU core count
    """

    # Configuration
    CARBON_INTENSITY = 0.3  # 300g/kWh = 0.3 kg CO2/kWh
    CPU_TDP_WATTS = 65  # Typical CPU power consumption

    print(f"🔍 Monitoring script: {script_path}")
    print(f"⏱️  Duration: {duration} seconds")
    print(f"🔬 Using 300g CO2/kWh carbon intensity")

    # Get system information using psutil
    cpu_count = psutil.cpu_count()
    total_memory_gb = psutil.virtual_memory().total / (1024**3)
    print(f"💻 System: {cpu_count} CPUs, {total_memory_gb:.1f}GB RAM")

    # Start the Python script
    print(f"\n🚀 Starting script execution...")
    start_time = time.time()

    try:
        # Launch script as subprocess
        process = subprocess.Popen([sys.executable, script_path])

        # Monitor CPU usage while script runs
        cpu_samples = []
        script_cpu_samples = []

        while process.poll() is None and (time.time() - start_time) < duration:
            # Get system-wide CPU usage
            system_cpu = psutil.cpu_percent(interval=1.0)
            cpu_samples.append(system_cpu)

            # Get script-specific CPU usage
            script_cpu = 0
            try:
                script_proc = psutil.Process(process.pid)
                script_cpu = script_proc.cpu_percent()
                script_cpu_samples.append(script_cpu)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                script_cpu_samples.append(0)

            print(f"📊 System CPU: {system_cpu:5.1f}% | Script CPU: {script_cpu:5.1f}%")

        # Wait for script completion
        if process.poll() is None:
            process.terminate()

        process.wait()

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

    execution_time = time.time() - start_time
    print(f"✅ Script completed in {execution_time:.2f} seconds")

    # Calculate CO2 emissions from CPU usage
    if not cpu_samples:
        print("⚠️  No CPU data collected")
        return None

    # Calculate average CPU usage
    avg_system_cpu = sum(cpu_samples) / len(cpu_samples)
    avg_script_cpu = (
        sum(script_cpu_samples) / len(script_cpu_samples) if script_cpu_samples else 0
    )

    print(f"\n📊 CPU USAGE ANALYSIS:")
    print(f"   🖥️  Average system CPU: {avg_system_cpu:.1f}%")
    print(f"   📝 Average script CPU: {avg_script_cpu:.1f}%")
    print(f"   📈 Peak system CPU: {max(cpu_samples):.1f}%")

    # Power consumption calculation
    # CPU power is proportional to usage percentage
    system_cpu_power_watts = (avg_system_cpu / 100) * CPU_TDP_WATTS
    script_cpu_power_watts = (avg_script_cpu / 100) * CPU_TDP_WATTS

    # Convert to energy (kWh)
    execution_hours = execution_time / 3600
    system_energy_kwh = (system_cpu_power_watts / 1000) * execution_hours
    script_energy_kwh = (script_cpu_power_watts / 1000) * execution_hours

    # Calculate CO2 emissions using 300g/kWh
    system_co2_kg = system_energy_kwh * CARBON_INTENSITY
    script_co2_kg = script_energy_kwh * CARBON_INTENSITY

    print(f"\n⚡ POWER & ENERGY:")
    print(f"   🔌 System CPU power: {system_cpu_power_watts:.1f} W")
    print(f"   📝 Script CPU power: {script_cpu_power_watts:.1f} W")
    print(f"   🔋 System energy: {system_energy_kwh:.6f} kWh")
    print(f"   📱 Script energy: {script_energy_kwh:.6f} kWh")

    print(f"\n🌿 CO2 EMISSIONS (300g/kWh):")
    print(f"   🌍 System CO2: {system_co2_kg:.6f} kg ({system_co2_kg*1000:.3f}g)")
    print(f"   📝 Script CO2: {script_co2_kg:.6f} kg ({script_co2_kg*1000:.3f}g)")

    # CO2 equivalents for context
    if script_co2_kg > 0:
        km_driven = script_co2_kg / 0.21  # 210g CO2/km for average car
        phone_charges = script_co2_kg / 0.008  # ~8g CO2 per smartphone charge

        print(f"\n🌍 SCRIPT CO2 EQUIVALENTS:")
        print(f"   🚗 Driving: {km_driven:.4f} km")
        print(f"   📱 Phone charges: {phone_charges:.2f}")

    return {
        "script_path": script_path,
        "execution_time_seconds": execution_time,
        "avg_system_cpu_percent": avg_system_cpu,
        "avg_script_cpu_percent": avg_script_cpu,
        "system_cpu_power_watts": system_cpu_power_watts,
        "script_cpu_power_watts": script_cpu_power_watts,
        "system_energy_kwh": system_energy_kwh,
        "script_energy_kwh": script_energy_kwh,
        "system_co2_kg": system_co2_kg,
        "script_co2_kg": script_co2_kg,
        "carbon_intensity_kg_per_kwh": CARBON_INTENSITY,
        "samples_collected": len(cpu_samples),
    }


def demo_cpu_monitoring():
    """
    Demonstrate psutil CPU monitoring without running external script
    """

    print("🔥 CPU Monitoring Demo")
    print("Running CPU-intensive task for 10 seconds...")

    # Get initial CPU state
    initial_cpu = psutil.cpu_percent()
    print(f"📊 Initial CPU: {initial_cpu:.1f}%")

    # Run CPU-intensive task
    import math

    start_time = time.time()
    cpu_samples = []

    # Monitor CPU while doing intensive computation
    result = 0
    while (time.time() - start_time) < 10:
        # Do some CPU work
        for i in range(10000):
            result += math.sqrt(i)

        # Sample CPU usage
        cpu_usage = psutil.cpu_percent(interval=0.1)
        cpu_samples.append(cpu_usage)

        print(f"📊 CPU: {cpu_usage:5.1f}% | Computation result: {result:.0f}")

    duration = time.time() - start_time
    avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0

    # Calculate CO2 for this demo
    cpu_power_watts = (avg_cpu / 100) * 65  # 65W TDP
    energy_kwh = (cpu_power_watts / 1000) * (duration / 3600)
    co2_kg = energy_kwh * 0.3  # 300g/kWh

    print(f"\n📈 DEMO RESULTS:")
    print(f"   ⏱️  Duration: {duration:.2f} seconds")
    print(f"   📊 Average CPU: {avg_cpu:.1f}%")
    print(f"   ⚡ Power: {cpu_power_watts:.1f} W")
    print(f"   🔋 Energy: {energy_kwh:.6f} kWh")
    print(f"   🌿 CO2: {co2_kg:.6f} kg ({co2_kg*1000:.3f}g)")


# Key psutil functions summary
def show_psutil_functions():
    """Show the key psutil functions used for CPU monitoring"""

    print("🔧 KEY PSUTIL FUNCTIONS FOR CPU MONITORING:")
    print("=" * 50)

    print("\n1. psutil.cpu_percent() - Get CPU usage percentage")
    cpu_usage = psutil.cpu_percent(interval=1)
    print(f"   Current CPU usage: {cpu_usage:.1f}%")

    print("\n2. psutil.cpu_count() - Get number of CPU cores")
    cpu_cores = psutil.cpu_count()
    print(f"   CPU cores: {cpu_cores}")

    print("\n3. psutil.virtual_memory() - Get memory information")
    memory = psutil.virtual_memory()
    print(f"   Total memory: {memory.total / (1024**3):.1f} GB")
    print(f"   Used memory: {memory.used / (1024**3):.1f} GB ({memory.percent:.1f}%)")

    print("\n4. psutil.Process(pid) - Monitor specific process")
    current_proc = psutil.Process()
    print(f"   Current process CPU: {current_proc.cpu_percent():.1f}%")
    print(
        f"   Current process memory: {current_proc.memory_info().rss / (1024**2):.1f} MB"
    )

    print("\n5. CO2 Calculation Formula:")
    print("   Power (W) = (CPU% / 100) × CPU_TDP_WATTS")
    print("   Energy (kWh) = Power (W) / 1000 × Hours")
    print("   CO2 (kg) = Energy (kWh) × 0.3 kg/kWh")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="psutil CPU monitoring for CO2 estimation"
    )
    parser.add_argument("script", nargs="?", help="Python script to monitor")
    parser.add_argument(
        "--duration", "-d", type=int, default=30, help="Duration in seconds"
    )
    parser.add_argument("--demo", action="store_true", help="Run CPU monitoring demo")
    parser.add_argument(
        "--functions", action="store_true", help="Show psutil functions"
    )

    args = parser.parse_args()

    if args.functions:
        show_psutil_functions()
    elif args.demo:
        demo_cpu_monitoring()
    elif args.script:
        result = monitor_python_script_co2(args.script, args.duration)
        if result:
            print(f"\n✅ Monitoring complete!")
            print(f"🌿 Script CO2 emissions: {result['script_co2_kg']:.6f} kg")
    else:
        print("🚀 psutil CPU Monitoring for CO2 Estimation")
        print("\nUsage examples:")
        print("  python3 psutil_core_example.py script.py --duration 60")
        print("  python3 psutil_core_example.py --demo")
        print("  python3 psutil_core_example.py --functions")
        print("\n💡 This demonstrates using psutil to:")
        print("  • Monitor CPU usage with psutil.cpu_percent()")
        print("  • Track specific processes with psutil.Process()")
        print("  • Calculate CO2 emissions using 300g/kWh carbon intensity")
