#!/usr/bin/env python3
"""
psutil CPU Monitoring for CO2 Estimation - Clean Summary
Key functions for monitoring Python script CPU usage and estimating CO2 with 300g/kWh
"""

import psutil
import time
import subprocess
import sys

def monitor_script_co2_simple(script_path: str, duration: int = 60) -> dict:
    """
    Simple function to monitor Python script CPU usage and estimate CO2
    
    Key psutil functions used:
    - psutil.cpu_percent() - Get system CPU usage
    - psutil.Process(pid) - Monitor specific process
    - psutil.virtual_memory() - Get memory info
    - psutil.cpu_count() - Get CPU core count
    
    Args:
        script_path: Path to Python script
        duration: Monitoring duration in seconds
        
    Returns:
        Dictionary with CPU usage and CO2 estimation
    """
    
    # Configuration
    CARBON_INTENSITY = 0.3  # 300g/kWh = 0.3 kg CO2/kWh
    CPU_TDP_WATTS = 65      # Typical CPU power
    
    print(f"🔍 Monitoring: {script_path}")
    print(f"🔬 Using 300g CO2/kWh carbon intensity")
    
    # Get system info using psutil
    cpu_count = psutil.cpu_count()
    memory_gb = psutil.virtual_memory().total / (1024**3)
    print(f"💻 {cpu_count} CPUs, {memory_gb:.1f}GB RAM")
    
    # Start script and monitor
    start_time = time.time()
    process = subprocess.Popen([sys.executable, script_path])
    
    cpu_samples = []
    
    # Monitor CPU while script runs
    while process.poll() is None and (time.time() - start_time) < duration:
        # System CPU usage
        system_cpu = psutil.cpu_percent(interval=1.0)
        
        # Script-specific CPU usage
        script_cpu = 0
        try:
            script_proc = psutil.Process(process.pid)
            script_cpu = script_proc.cpu_percent()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        cpu_samples.append({'system': system_cpu, 'script': script_cpu})
        print(f"📊 System: {system_cpu:4.1f}% | Script: {script_cpu:4.1f}%")
    
    # Wait for completion
    if process.poll() is None:
        process.terminate()
    process.wait()
    
    execution_time = time.time() - start_time
    
    # Calculate averages
    if not cpu_samples:
        return {'error': 'No data collected'}
    
    avg_system_cpu = sum(s['system'] for s in cpu_samples) / len(cpu_samples)
    avg_script_cpu = sum(s['script'] for s in cpu_samples) / len(cpu_samples)
    
    # Calculate power and CO2
    system_power_watts = (avg_system_cpu / 100) * CPU_TDP_WATTS
    script_power_watts = (avg_script_cpu / 100) * CPU_TDP_WATTS
    
    execution_hours = execution_time / 3600
    system_energy_kwh = (system_power_watts / 1000) * execution_hours
    script_energy_kwh = (script_power_watts / 1000) * execution_hours
    
    system_co2_kg = system_energy_kwh * CARBON_INTENSITY
    script_co2_kg = script_energy_kwh * CARBON_INTENSITY
    
    return {
        'script_path': script_path,
        'execution_time_seconds': execution_time,
        'avg_system_cpu_percent': avg_system_cpu,
        'avg_script_cpu_percent': avg_script_cpu,
        'system_power_watts': system_power_watts,
        'script_power_watts': script_power_watts,
        'system_energy_kwh': system_energy_kwh,
        'script_energy_kwh': script_energy_kwh,
        'system_co2_kg': system_co2_kg,
        'script_co2_kg': script_co2_kg,
        'carbon_intensity': CARBON_INTENSITY,
        'samples': len(cpu_samples)
    }

def get_current_system_metrics():
    """
    Get current system metrics using psutil
    Demonstrates key psutil functions
    """
    
    print("🔧 Current System Metrics (psutil functions):")
    print("=" * 50)
    
    # 1. CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"📊 CPU Usage: {cpu_percent:.1f}% (psutil.cpu_percent())")
    
    # 2. CPU count
    cpu_count = psutil.cpu_count()
    print(f"🖥️  CPU Cores: {cpu_count} (psutil.cpu_count())")
    
    # 3. Memory info
    memory = psutil.virtual_memory()
    print(f"🧠 Memory: {memory.used/(1024**3):.1f}GB / {memory.total/(1024**3):.1f}GB "
          f"({memory.percent:.1f}%) (psutil.virtual_memory())")
    
    # 4. Current process
    current_proc = psutil.Process()
    proc_cpu = current_proc.cpu_percent()
    proc_memory_mb = current_proc.memory_info().rss / (1024**2)
    print(f"📝 This Process: {proc_cpu:.1f}% CPU, {proc_memory_mb:.1f}MB RAM (psutil.Process())")
    
    # 5. CO2 calculation example
    power_watts = (cpu_percent / 100) * 65  # 65W TDP
    print(f"⚡ Estimated Power: {power_watts:.1f}W")
    print(f"🌿 CO2 Rate: {power_watts * 0.3 / 1000:.6f} kg/hour @ 300g/kWh")

def calculate_co2_from_cpu(cpu_percent: float, duration_seconds: float) -> dict:
    """
    Calculate CO2 emissions from CPU usage percentage
    
    Args:
        cpu_percent: Average CPU usage percentage
        duration_seconds: Duration in seconds
        
    Returns:
        Dictionary with CO2 calculation
    """
    
    CPU_TDP_WATTS = 65
    CARBON_INTENSITY = 0.3  # 300g/kWh
    
    # Power calculation
    power_watts = (cpu_percent / 100) * CPU_TDP_WATTS
    
    # Energy calculation
    duration_hours = duration_seconds / 3600
    energy_kwh = (power_watts / 1000) * duration_hours
    
    # CO2 calculation
    co2_kg = energy_kwh * CARBON_INTENSITY
    
    return {
        'cpu_percent': cpu_percent,
        'duration_seconds': duration_seconds,
        'power_watts': power_watts,
        'energy_kwh': energy_kwh,
        'co2_kg': co2_kg,
        'co2_g': co2_kg * 1000,
        'formula': 'CO2 = (CPU% / 100) × TDP_W / 1000 × Hours × 0.3 kg/kWh'
    }

# Example usage
if __name__ == "__main__":
    print("🌍 psutil CPU Monitoring for CO2 Estimation")
    print("=" * 50)
    
    # Show current system metrics
    get_current_system_metrics()
    
    print(f"\n💡 Key psutil Functions for CPU Monitoring:")
    print("   • psutil.cpu_percent() - Get CPU usage percentage")
    print("   • psutil.Process(pid) - Monitor specific process")
    print("   • psutil.virtual_memory() - Get memory information")
    print("   • psutil.cpu_count() - Get number of CPU cores")
    
    print(f"\n🧮 CO2 Calculation Formula:")
    print("   Power (W) = (CPU% ÷ 100) × CPU_TDP_WATTS")
    print("   Energy (kWh) = Power (W) ÷ 1000 × Hours")
    print("   CO2 (kg) = Energy (kWh) × 0.3 kg/kWh")
    
    # Example calculation
    print(f"\n📊 Example CO2 Calculation:")
    example = calculate_co2_from_cpu(50.0, 3600)  # 50% CPU for 1 hour
    print(f"   50% CPU for 1 hour:")
    print(f"   Power: {example['power_watts']:.1f}W")
    print(f"   Energy: {example['energy_kwh']:.3f} kWh")
    print(f"   CO2: {example['co2_kg']:.3f} kg ({example['co2_g']:.1f}g)")
    
    print(f"\n🚀 Usage:")
    print("   python3 psutil_summary.py")
    print("   # Shows current system metrics and CO2 calculation examples")
    
    print(f"\n📝 To monitor a script:")
    print("   result = monitor_script_co2_simple('script.py', 60)")
    print("   print(f'CO2: {result[\"script_co2_kg\"]:.6f} kg')")
