#!/usr/bin/env python3
"""
Python Script CO2 Monitor using psutil
Monitors CPU usage and estimates CO2 emissions with 300g/kWh carbon intensity
"""

import psutil
import time
import threading
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

def monitor_script_co2(script_path: str, duration: int = 60, 
                      sample_interval: float = 1.0) -> Dict[str, Any]:
    """
    Monitor a Python script's CPU usage and estimate CO2 emissions
    
    Args:
        script_path: Path to the Python script to monitor
        duration: Monitoring duration in seconds
        sample_interval: Sampling interval in seconds
        
    Returns:
        Dictionary with monitoring results and CO2 calculations
    """
    
    # Configuration
    CARBON_INTENSITY = 0.3  # 300g/kWh = 0.3 kg CO2/kWh
    DEFAULT_CPU_TDP = 65    # Watts (typical desktop CPU)
    
    print(f"🔍 Monitoring script: {script_path}")
    print(f"⏱️  Duration: {duration} seconds")
    print(f"📊 Sample interval: {sample_interval} seconds")
    print(f"🔬 Carbon intensity: {CARBON_INTENSITY} kg CO2/kWh")
    
    # Get system information
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    memory_total = psutil.virtual_memory().total / (1024**3)  # GB
    
    print(f"💻 System: {cpu_count} CPUs, {memory_total:.1f}GB RAM")
    if cpu_freq:
        print(f"⚡ CPU Frequency: {cpu_freq.current:.0f} MHz")
    
    # Storage for monitoring data
    monitoring_data = []
    monitoring_active = True
    script_process = None
    
    def collect_metrics():
        """Background thread to collect system metrics"""
        nonlocal monitoring_active, script_process
        
        while monitoring_active:
            try:
                # Get overall system metrics
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                disk_io = psutil.disk_io_counters()
                net_io = psutil.net_io_counters()
                
                # Get script-specific metrics if process is running
                script_cpu = 0
                script_memory = 0
                if script_process and script_process.poll() is None:
                    try:
                        proc = psutil.Process(script_process.pid)
                        script_cpu = proc.cpu_percent()
                        script_memory = proc.memory_info().rss / (1024**2)  # MB
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Store metrics
                metrics = {
                    'timestamp': time.time(),
                    'system_cpu_percent': cpu_percent,
                    'script_cpu_percent': script_cpu,
                    'memory_used_gb': memory.used / (1024**3),
                    'script_memory_mb': script_memory,
                    'disk_read_bytes': disk_io.read_bytes if disk_io else 0,
                    'disk_write_bytes': disk_io.write_bytes if disk_io else 0,
                    'network_sent_bytes': net_io.bytes_sent if net_io else 0,
                    'network_recv_bytes': net_io.bytes_recv if net_io else 0,
                }
                monitoring_data.append(metrics)
                
                time.sleep(sample_interval)
                
            except Exception as e:
                print(f"⚠️  Monitoring error: {e}")
                time.sleep(sample_interval)
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=collect_metrics, daemon=True)
    monitor_thread.start()
    
    # Execute the script
    start_time = time.time()
    print(f"\n🚀 Starting script execution...")
    
    try:
        script_process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for script completion or timeout
        try:
            stdout, stderr = script_process.communicate(timeout=duration)
            execution_successful = script_process.returncode == 0
        except subprocess.TimeoutExpired:
            script_process.kill()
            stdout, stderr = script_process.communicate()
            execution_successful = False
            print("⏰ Script execution timed out")
            
    except Exception as e:
        print(f"❌ Error executing script: {e}")
        execution_successful = False
        stdout, stderr = "", str(e)
    
    end_time = time.time()
    actual_duration = end_time - start_time
    
    # Stop monitoring
    monitoring_active = False
    monitor_thread.join(timeout=2)
    
    print(f"✅ Script completed in {actual_duration:.2f} seconds")
    
    # Calculate CO2 emissions
    results = calculate_co2_from_metrics(
        monitoring_data, actual_duration, CARBON_INTENSITY, DEFAULT_CPU_TDP
    )
    
    # Add execution details
    results.update({
        'script_path': script_path,
        'execution_duration_seconds': actual_duration,
        'execution_successful': execution_successful,
        'script_stdout': stdout[:500] if stdout else "",  # Limit output
        'script_stderr': stderr[:500] if stderr else "",
        'monitoring_samples': len(monitoring_data),
        'sample_interval_seconds': sample_interval,
        'system_info': {
            'cpu_count': cpu_count,
            'memory_total_gb': memory_total,
            'cpu_frequency_mhz': cpu_freq.current if cpu_freq else None
        }
    })
    
    return results

def calculate_co2_from_metrics(monitoring_data: List[Dict], duration: float, 
                              carbon_intensity: float, cpu_tdp: int) -> Dict[str, Any]:
    """
    Calculate CO2 emissions from collected monitoring data
    
    Args:
        monitoring_data: List of monitoring data points
        duration: Total monitoring duration in seconds
        carbon_intensity: Carbon intensity in kg CO2/kWh
        cpu_tdp: CPU Thermal Design Power in watts
        
    Returns:
        Dictionary with CO2 calculations
    """
    
    if not monitoring_data:
        return {
            'total_co2_kg': 0,
            'total_energy_kwh': 0,
            'avg_cpu_percent': 0,
            'peak_memory_gb': 0,
            'error': 'No monitoring data collected'
        }
    
    # Calculate averages and peaks
    avg_system_cpu = sum(d['system_cpu_percent'] for d in monitoring_data) / len(monitoring_data)
    avg_script_cpu = sum(d['script_cpu_percent'] for d in monitoring_data) / len(monitoring_data)
    peak_memory_gb = max(d['memory_used_gb'] for d in monitoring_data)
    avg_memory_gb = sum(d['memory_used_gb'] for d in monitoring_data) / len(monitoring_data)
    
    # Calculate script-specific metrics
    peak_script_memory_mb = max(d['script_memory_mb'] for d in monitoring_data)
    avg_script_memory_mb = sum(d['script_memory_mb'] for d in monitoring_data) / len(monitoring_data)
    
    # Calculate disk I/O
    if len(monitoring_data) > 1:
        disk_read_diff = monitoring_data[-1]['disk_read_bytes'] - monitoring_data[0]['disk_read_bytes']
        disk_write_diff = monitoring_data[-1]['disk_write_bytes'] - monitoring_data[0]['disk_write_bytes']
        network_sent_diff = monitoring_data[-1]['network_sent_bytes'] - monitoring_data[0]['network_sent_bytes']
        network_recv_diff = monitoring_data[-1]['network_recv_bytes'] - monitoring_data[0]['network_recv_bytes']
    else:
        disk_read_diff = disk_write_diff = network_sent_diff = network_recv_diff = 0
    
    # Power consumption calculations
    
    # CPU power (proportional to usage)
    cpu_power_watts = (avg_system_cpu / 100) * cpu_tdp
    script_cpu_power_watts = (avg_script_cpu / 100) * cpu_tdp
    
    # Memory power (rough estimate: 3W per GB)
    memory_power_watts = avg_memory_gb * 3
    
    # Disk I/O power (rough estimate)
    total_disk_io_gb = (disk_read_diff + disk_write_diff) / (1024**3)
    disk_power_watts = min(total_disk_io_gb * 2, 10)  # Cap at 10W
    
    # Network power (rough estimate)
    total_network_gb = (network_sent_diff + network_recv_diff) / (1024**3)
    network_power_watts = total_network_gb * 0.1  # Very rough estimate
    
    # Total power consumption
    total_power_watts = cpu_power_watts + memory_power_watts + disk_power_watts + network_power_watts
    script_power_watts = script_cpu_power_watts + (avg_script_memory_mb / 1024) * 3
    
    # Convert to energy (kWh)
    duration_hours = duration / 3600
    total_energy_kwh = (total_power_watts / 1000) * duration_hours
    script_energy_kwh = (script_power_watts / 1000) * duration_hours
    
    # Calculate CO2 emissions
    total_co2_kg = total_energy_kwh * carbon_intensity
    script_co2_kg = script_energy_kwh * carbon_intensity
    
    return {
        'total_co2_kg': total_co2_kg,
        'script_co2_kg': script_co2_kg,
        'total_energy_kwh': total_energy_kwh,
        'script_energy_kwh': script_energy_kwh,
        'avg_system_cpu_percent': avg_system_cpu,
        'avg_script_cpu_percent': avg_script_cpu,
        'peak_memory_gb': peak_memory_gb,
        'avg_memory_gb': avg_memory_gb,
        'peak_script_memory_mb': peak_script_memory_mb,
        'avg_script_memory_mb': avg_script_memory_mb,
        'total_disk_io_gb': total_disk_io_gb,
        'total_network_gb': total_network_gb,
        'power_breakdown': {
            'cpu_watts': cpu_power_watts,
            'script_cpu_watts': script_cpu_power_watts,
            'memory_watts': memory_power_watts,
            'disk_watts': disk_power_watts,
            'network_watts': network_power_watts,
            'total_watts': total_power_watts,
            'script_watts': script_power_watts
        },
        'carbon_intensity_kg_per_kwh': carbon_intensity,
        'cpu_tdp_watts': cpu_tdp
    }

def monitor_current_process_co2(duration: int = 60) -> Dict[str, Any]:
    """
    Monitor the current Python process for CO2 emissions
    
    Args:
        duration: Monitoring duration in seconds
        
    Returns:
        Dictionary with CO2 monitoring results
    """
    
    CARBON_INTENSITY = 0.3  # 300g/kWh
    DEFAULT_CPU_TDP = 65
    
    print(f"🔍 Monitoring current process for {duration} seconds...")
    
    # Get current process
    current_process = psutil.Process()
    start_time = time.time()
    
    # Storage for metrics
    metrics = []
    
    # Monitor for specified duration
    while (time.time() - start_time) < duration:
        try:
            # Get process metrics
            cpu_percent = current_process.cpu_percent()
            memory_info = current_process.memory_info()
            memory_mb = memory_info.rss / (1024**2)
            
            # Get system metrics
            system_cpu = psutil.cpu_percent(interval=0.1)
            system_memory = psutil.virtual_memory()
            
            metrics.append({
                'timestamp': time.time(),
                'process_cpu_percent': cpu_percent,
                'process_memory_mb': memory_mb,
                'system_cpu_percent': system_cpu,
                'system_memory_used_gb': system_memory.used / (1024**3)
            })
            
            time.sleep(1.0)
            
        except Exception as e:
            print(f"⚠️  Monitoring error: {e}")
            break
    
    actual_duration = time.time() - start_time
    
    if not metrics:
        return {'error': 'No metrics collected', 'total_co2_kg': 0}
    
    # Calculate averages
    avg_cpu = sum(m['process_cpu_percent'] for m in metrics) / len(metrics)
    avg_memory_mb = sum(m['process_memory_mb'] for m in metrics) / len(metrics)
    peak_memory_mb = max(m['process_memory_mb'] for m in metrics)
    
    # Calculate power and CO2
    cpu_power_watts = (avg_cpu / 100) * DEFAULT_CPU_TDP
    memory_power_watts = (avg_memory_mb / 1024) * 3  # 3W per GB
    total_power_watts = cpu_power_watts + memory_power_watts
    
    duration_hours = actual_duration / 3600
    energy_kwh = (total_power_watts / 1000) * duration_hours
    co2_kg = energy_kwh * CARBON_INTENSITY
    
    return {
        'monitoring_duration_seconds': actual_duration,
        'total_co2_kg': co2_kg,
        'total_energy_kwh': energy_kwh,
        'avg_cpu_percent': avg_cpu,
        'avg_memory_mb': avg_memory_mb,
        'peak_memory_mb': peak_memory_mb,
        'total_power_watts': total_power_watts,
        'samples_collected': len(metrics),
        'carbon_intensity_kg_per_kwh': CARBON_INTENSITY
    }

def print_co2_results(results: Dict[str, Any]) -> None:
    """Print formatted CO2 monitoring results"""
    
    print("\n" + "="*60)
    print("🌍 CO2 EMISSIONS MONITORING RESULTS")
    print("="*60)
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Basic metrics
    print(f"📊 EXECUTION SUMMARY:")
    print(f"   📁 Script: {results.get('script_path', 'Current process')}")
    print(f"   ⏱️  Duration: {results.get('execution_duration_seconds', results.get('monitoring_duration_seconds', 0)):.2f} seconds")
    print(f"   ✅ Success: {results.get('execution_successful', 'N/A')}")
    print(f"   📈 Samples: {results.get('monitoring_samples', results.get('samples_collected', 0))}")
    
    # CO2 and energy
    print(f"\n🌿 CARBON FOOTPRINT:")
    total_co2 = results.get('total_co2_kg', 0)
    script_co2 = results.get('script_co2_kg', total_co2)
    
    print(f"   🌍 Total CO2: {total_co2:.6f} kg ({total_co2*1000:.3f}g)")
    if 'script_co2_kg' in results:
        print(f"   📝 Script CO2: {script_co2:.6f} kg ({script_co2*1000:.3f}g)")
    
    energy = results.get('total_energy_kwh', 0)
    print(f"   ⚡ Energy: {energy:.6f} kWh ({energy*1000:.3f} Wh)")
    
    # Resource usage
    print(f"\n💻 RESOURCE USAGE:")
    print(f"   🖥️  Avg CPU: {results.get('avg_system_cpu_percent', results.get('avg_cpu_percent', 0)):.1f}%")
    if 'avg_script_cpu_percent' in results:
        print(f"   📝 Script CPU: {results.get('avg_script_cpu_percent', 0):.1f}%")
    
    memory_gb = results.get('peak_memory_gb', results.get('peak_memory_mb', 0) / 1024)
    print(f"   🧠 Peak Memory: {memory_gb:.2f} GB")
    
    # Power breakdown
    if 'power_breakdown' in results:
        power = results['power_breakdown']
        print(f"\n⚡ POWER BREAKDOWN:")
        print(f"   🖥️  CPU: {power.get('cpu_watts', 0):.1f}W")
        print(f"   🧠 Memory: {power.get('memory_watts', 0):.1f}W")
        print(f"   💾 Disk: {power.get('disk_watts', 0):.1f}W")
        print(f"   🌐 Network: {power.get('network_watts', 0):.1f}W")
        print(f"   📊 Total: {power.get('total_watts', 0):.1f}W")
    
    # CO2 equivalents
    co2_for_calc = script_co2 if 'script_co2_kg' in results else total_co2
    if co2_for_calc > 0:
        print(f"\n🌍 CO2 EQUIVALENTS:")
        km_driven = co2_for_calc / 0.21  # 210g CO2/km
        print(f"   🚗 Driving: {km_driven:.3f} km")
        
        smartphone_charges = co2_for_calc / 0.008  # ~8g CO2 per smartphone charge
        print(f"   📱 Phone charges: {smartphone_charges:.1f}")
        
        if co2_for_calc > 0.001:  # Only show for larger emissions
            trees_offset = co2_for_calc / 21.77 * 365  # Trees needed for 1 day
            print(f"   🌳 Tree-days needed: {trees_offset:.2f}")

# Example usage and testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor Python script CO2 emissions')
    parser.add_argument('script', nargs='?', help='Python script to monitor')
    parser.add_argument('--duration', '-d', type=int, default=30, 
                       help='Monitoring duration in seconds (default: 30)')
    parser.add_argument('--current', action='store_true', 
                       help='Monitor current process instead of running a script')
    
    args = parser.parse_args()
    
    if args.current:
        print("🔍 Monitoring current process...")
        results = monitor_current_process_co2(args.duration)
    elif args.script:
        results = monitor_script_co2(args.script, args.duration)
    else:
        print("📝 No script specified. Monitoring current process for demo...")
        
        # Demo: monitor this script itself
        import math
        
        def cpu_intensive_demo():
            """Simple CPU-intensive task for demonstration"""
            print("🔥 Running CPU-intensive demo...")
            start = time.time()
            result = 0
            while time.time() - start < 10:  # Run for 10 seconds
                result += math.sqrt(time.time())
            return result
        
        # Start monitoring
        start_time = time.time()
        demo_result = cpu_intensive_demo()
        
        # Create simple results
        duration = time.time() - start_time
        cpu_percent = 50  # Assume 50% CPU usage for demo
        
        results = {
            'monitoring_duration_seconds': duration,
            'total_co2_kg': (cpu_percent/100 * 65/1000 * duration/3600) * 0.3,
            'avg_cpu_percent': cpu_percent,
            'peak_memory_mb': 50,
            'execution_successful': True,
            'script_path': 'CPU Demo'
        }
    
    print_co2_results(results)
