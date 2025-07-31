#!/usr/bin/env python3
"""
Simple psutil CPU monitoring function for CO2 estimation
Monitors Python script CPU usage and estimates CO2 with 300g/kWh
"""

import subprocess
import sys
import time
from typing import Dict

import psutil


def monitor_script_cpu_co2(script_path: str, duration: int = 60) -> Dict:
    """
    Monitor a Python script's CPU usage and estimate CO2 emissions

    Args:
        script_path: Path to Python script to monitor
        duration: Monitoring duration in seconds

    Returns:
        Dictionary with CPU usage and CO2 estimation
    """

    # Configuration
    CARBON_INTENSITY = 0.3  # 300g/kWh = 0.3 kg CO2/kWh
    CPU_TDP_WATTS = 65  # Typical desktop CPU power
    MEMORY_POWER_PER_GB = 3  # Watts per GB of RAM

    print(f"🔍 Monitoring: {script_path}")
    print(f"⏱️  Duration: {duration} seconds")
    print(f"🔬 Carbon intensity: {CARBON_INTENSITY} kg CO2/kWh")

    # Get system info
    cpu_count = psutil.cpu_count()
    total_memory_gb = psutil.virtual_memory().total / (1024**3)

    print(f"💻 System: {cpu_count} CPUs, {total_memory_gb:.1f}GB RAM")

    # Storage for monitoring data
    cpu_samples = []
    memory_samples = []

    # Start the script
    print(f"\n🚀 Starting script...")
    start_time = time.time()

    try:
        # Launch the script process
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Monitor while script runs
        while process.poll() is None and (time.time() - start_time) < duration:
            # Get system-wide CPU usage
            cpu_percent = psutil.cpu_percent(interval=1.0)

            # Get memory usage
            memory = psutil.virtual_memory()
            memory_used_gb = memory.used / (1024**3)

            # Try to get script-specific metrics
            script_cpu = 0
            script_memory_mb = 0
            try:
                script_proc = psutil.Process(process.pid)
                script_cpu = script_proc.cpu_percent()
                script_memory_mb = script_proc.memory_info().rss / (1024**2)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

            # Store samples
            cpu_samples.append(
                {
                    "timestamp": time.time(),
                    "system_cpu": cpu_percent,
                    "script_cpu": script_cpu,
                }
            )

            memory_samples.append(
                {
                    "timestamp": time.time(),
                    "system_memory_gb": memory_used_gb,
                    "script_memory_mb": script_memory_mb,
                }
            )

            print(
                f"📊 CPU: {cpu_percent:5.1f}% (script: {script_cpu:5.1f}%) | "
                f"Memory: {memory_used_gb:5.1f}GB (script: {script_memory_mb:5.1f}MB)"
            )

        # Wait for script completion
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)

        stdout, stderr = process.communicate()
        execution_successful = process.returncode == 0

    except Exception as e:
        print(f"❌ Error running script: {e}")
        execution_successful = False
        stdout, stderr = "", str(e)

    actual_duration = time.time() - start_time
    print(f"✅ Monitoring completed in {actual_duration:.2f} seconds")

    # Calculate CO2 emissions
    if not cpu_samples:
        return {"error": "No monitoring data collected", "total_co2_kg": 0}

    # Calculate averages
    avg_system_cpu = sum(s["system_cpu"] for s in cpu_samples) / len(cpu_samples)
    avg_script_cpu = sum(s["script_cpu"] for s in cpu_samples) / len(cpu_samples)
    avg_memory_gb = sum(s["system_memory_gb"] for s in memory_samples) / len(
        memory_samples
    )
    peak_script_memory_mb = max(s["script_memory_mb"] for s in memory_samples)

    # Power calculations
    # CPU power proportional to usage
    system_cpu_power_watts = (avg_system_cpu / 100) * CPU_TDP_WATTS
    script_cpu_power_watts = (avg_script_cpu / 100) * CPU_TDP_WATTS

    # Memory power
    memory_power_watts = avg_memory_gb * MEMORY_POWER_PER_GB

    # Total power consumption
    total_power_watts = system_cpu_power_watts + memory_power_watts
    script_power_watts = (
        script_cpu_power_watts + (peak_script_memory_mb / 1024) * MEMORY_POWER_PER_GB
    )

    # Convert to energy (kWh)
    duration_hours = actual_duration / 3600
    total_energy_kwh = (total_power_watts / 1000) * duration_hours
    script_energy_kwh = (script_power_watts / 1000) * duration_hours

    # Calculate CO2 emissions
    total_co2_kg = total_energy_kwh * CARBON_INTENSITY
    script_co2_kg = script_energy_kwh * CARBON_INTENSITY

    return {
        "script_path": script_path,
        "execution_duration_seconds": actual_duration,
        "execution_successful": execution_successful,
        "samples_collected": len(cpu_samples),
        # CPU metrics
        "avg_system_cpu_percent": avg_system_cpu,
        "avg_script_cpu_percent": avg_script_cpu,
        "max_cpu_sample": max(s["system_cpu"] for s in cpu_samples),
        # Memory metrics
        "avg_system_memory_gb": avg_memory_gb,
        "peak_script_memory_mb": peak_script_memory_mb,
        # Power metrics
        "system_cpu_power_watts": system_cpu_power_watts,
        "script_cpu_power_watts": script_cpu_power_watts,
        "memory_power_watts": memory_power_watts,
        "total_power_watts": total_power_watts,
        "script_power_watts": script_power_watts,
        # Energy and CO2
        "total_energy_kwh": total_energy_kwh,
        "script_energy_kwh": script_energy_kwh,
        "total_co2_kg": total_co2_kg,
        "script_co2_kg": script_co2_kg,
        "total_co2_g": total_co2_kg * 1000,
        "script_co2_g": script_co2_kg * 1000,
        # Configuration used
        "carbon_intensity_kg_per_kwh": CARBON_INTENSITY,
        "cpu_tdp_watts": CPU_TDP_WATTS,
        # System info
        "system_cpu_count": cpu_count,
        "system_memory_total_gb": total_memory_gb,
    }


def monitor_current_process(duration: int = 30) -> Dict:
    """
    Monitor the current Python process for CO2 emissions

    Args:
        duration: Monitoring duration in seconds

    Returns:
        Dictionary with monitoring results
    """

    CARBON_INTENSITY = 0.3
    CPU_TDP_WATTS = 65

    print(f"🔍 Monitoring current process for {duration} seconds...")

    # Get current process
    current_proc = psutil.Process()
    start_time = time.time()

    cpu_samples = []
    memory_samples = []

    # Monitor for specified duration
    while (time.time() - start_time) < duration:
        try:
            # Process-specific metrics
            proc_cpu = current_proc.cpu_percent()
            proc_memory_mb = current_proc.memory_info().rss / (1024**2)

            # System metrics
            system_cpu = psutil.cpu_percent(interval=0.1)
            psutil.virtual_memory().used / (1024**3)

            cpu_samples.append(proc_cpu)
            memory_samples.append(proc_memory_mb)

            print(
                f"📊 Process CPU: {proc_cpu:5.1f}% | Memory: {proc_memory_mb:6.1f}MB | System CPU: {system_cpu:5.1f}%"
            )

            time.sleep(1.0)

        except Exception as e:
            print(f"⚠️  Error: {e}")
            break

    actual_duration = time.time() - start_time

    if not cpu_samples:
        return {"error": "No data collected"}

    # Calculate metrics
    avg_cpu = sum(cpu_samples) / len(cpu_samples)
    peak_cpu = max(cpu_samples)
    avg_memory_mb = sum(memory_samples) / len(memory_samples)
    peak_memory_mb = max(memory_samples)

    # Power and CO2 calculations
    cpu_power_watts = (avg_cpu / 100) * CPU_TDP_WATTS
    memory_power_watts = (avg_memory_mb / 1024) * 3  # 3W per GB
    total_power_watts = cpu_power_watts + memory_power_watts

    duration_hours = actual_duration / 3600
    energy_kwh = (total_power_watts / 1000) * duration_hours
    co2_kg = energy_kwh * CARBON_INTENSITY

    return {
        "monitoring_duration_seconds": actual_duration,
        "samples_collected": len(cpu_samples),
        "avg_cpu_percent": avg_cpu,
        "peak_cpu_percent": peak_cpu,
        "avg_memory_mb": avg_memory_mb,
        "peak_memory_mb": peak_memory_mb,
        "cpu_power_watts": cpu_power_watts,
        "memory_power_watts": memory_power_watts,
        "total_power_watts": total_power_watts,
        "total_energy_kwh": energy_kwh,
        "total_co2_kg": co2_kg,
        "total_co2_g": co2_kg * 1000,
        "carbon_intensity_kg_per_kwh": CARBON_INTENSITY,
    }


def print_results(results: Dict) -> None:
    """Print monitoring results in a formatted way"""

    print("\n" + "=" * 50)
    print("🌍 CO2 MONITORING RESULTS")
    print("=" * 50)

    if "error" in results:
        print(f"❌ {results['error']}")
        return

    # Basic info
    duration = results.get(
        "execution_duration_seconds", results.get("monitoring_duration_seconds", 0)
    )
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print(f"📊 Samples: {results.get('samples_collected', 0)}")

    # CPU metrics
    if "avg_script_cpu_percent" in results:
        print(f"🖥️  System CPU: {results['avg_system_cpu_percent']:.1f}% (avg)")
        print(f"📝 Script CPU: {results['avg_script_cpu_percent']:.1f}% (avg)")
    else:
        print(
            f"🖥️  Process CPU: {results['avg_cpu_percent']:.1f}% (avg), {results.get('peak_cpu_percent', 0):.1f}% (peak)"
        )

    # Memory metrics
    if "peak_script_memory_mb" in results:
        print(f"🧠 Script Memory: {results['peak_script_memory_mb']:.1f} MB (peak)")
    else:
        print(
            f"🧠 Process Memory: {results['avg_memory_mb']:.1f} MB (avg), {results.get('peak_memory_mb', 0):.1f} MB (peak)"
        )

    # Power and energy
    total_power = results.get("total_power_watts", 0)
    energy = results.get("total_energy_kwh", 0)
    print(f"⚡ Power: {total_power:.1f} W")
    print(f"🔋 Energy: {energy:.6f} kWh ({energy*1000:.3f} Wh)")

    # CO2 emissions
    if "script_co2_kg" in results:
        script_co2 = results["script_co2_kg"]
        total_co2 = results["total_co2_kg"]
        print(f"🌿 Script CO2: {script_co2:.6f} kg ({script_co2*1000:.3f} g)")
        print(f"🌍 Total CO2: {total_co2:.6f} kg ({total_co2*1000:.3f} g)")
    else:
        co2 = results["total_co2_kg"]
        print(f"🌿 CO2 Emissions: {co2:.6f} kg ({co2*1000:.3f} g)")

    # Equivalents
    co2_for_equiv = results.get("script_co2_kg", results["total_co2_kg"])
    if co2_for_equiv > 0:
        print(f"\n🌍 EQUIVALENTS:")
        km_driven = co2_for_equiv / 0.21  # 210g CO2/km
        print(f"🚗 Driving: {km_driven:.4f} km")

        phone_charges = co2_for_equiv / 0.008  # ~8g per charge
        print(f"📱 Phone charges: {phone_charges:.2f}")


# Example usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Monitor Python script CO2 with psutil"
    )
    parser.add_argument("script", nargs="?", help="Python script to monitor")
    parser.add_argument(
        "--duration", "-d", type=int, default=30, help="Duration in seconds"
    )
    parser.add_argument("--self", action="store_true", help="Monitor current process")

    args = parser.parse_args()

    if args.self or not args.script:
        # Monitor current process with a simple CPU task
        print("🔥 Running CPU demo task...")

        def demo_task():
            import math

            result = 0
            for i in range(1000000):
                result += math.sqrt(i)
            return result

        # Start monitoring current process
        import threading

        # Run demo task in background
        task_thread = threading.Thread(target=demo_task)
        task_thread.start()

        # Monitor the process
        results = monitor_current_process(args.duration)

        task_thread.join()

    else:
        # Monitor specified script
        results = monitor_script_cpu_co2(args.script, args.duration)

    print_results(results)
