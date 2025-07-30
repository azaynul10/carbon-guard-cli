"""Local script CO2 auditing module."""

import psutil
import subprocess
import time
import threading
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class LocalAuditor:
    """Audits local scripts for CO2 emissions estimation."""
    
    # Power consumption estimates
    DEFAULT_CPU_TDP = 65  # Watts (typical desktop CPU)
    DEFAULT_MEMORY_POWER_PER_GB = 3  # Watts per GB
    DEFAULT_DISK_POWER = 10  # Watts for typical SSD
    DEFAULT_NETWORK_POWER_PER_MB = 0.001  # Watts per MB transferred
    
    # Carbon intensity (kg CO2 per kWh) - global average
    DEFAULT_CARBON_INTENSITY = 0.000475
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize local auditor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.carbon_intensity = self.config.get('carbon_intensity', self.DEFAULT_CARBON_INTENSITY)
        self.cpu_tdp = self.config.get('cpu_tdp_watts', self.DEFAULT_CPU_TDP)
        self.memory_power_per_gb = self.config.get('memory_power_per_gb', self.DEFAULT_MEMORY_POWER_PER_GB)
        
        # Get system information
        self.cpu_count = psutil.cpu_count()
        self.total_memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Monitoring data
        self.monitoring_data = []
        self.monitoring_active = False
    def _calculate_co2_from_metrics(self, monitoring_data, duration, carbon_intensity, cpu_tdp):
        if not monitoring_data:
            return {'total_co2_kg': 0.0, 'power_breakdown': {'cpu': 0, 'memory': 0, 'disk': 0, 'network': 0}}
        
        n = len(monitoring_data)
        avg_system_cpu = sum(d['system_cpu_percent'] for d in monitoring_data) / n
        avg_memory_gb = sum(d['memory_used_gb'] for d in monitoring_data) / n
        total_disk_gb = sum((d['disk_read_bytes'] + d['disk_write_bytes']) / (1024**3) for d in monitoring_data)
        total_network_gb = sum((d['network_bytes_sent'] + d['network_bytes_recv']) / (1024**3) for d in monitoring_data)
        
        cpu_power = (avg_system_cpu / 100) * cpu_tdp
        memory_power = avg_memory_gb * 3  # 3W/GB
        disk_power = min(total_disk_gb * 2, 10)  # 2W/GB IO, cap 10W
        network_power = total_network_gb * 0.1  # 0.1W/GB
        total_power = cpu_power + memory_power + disk_power + network_power
        
        energy_kwh = (total_power * duration / 3600) / 1000
        total_co2_kg = energy_kwh * carbon_intensity
        
        return {
            'total_co2_kg': total_co2_kg,
            'power_breakdown': {
                'cpu': cpu_power,
                'memory': memory_power,
                'disk': disk_power,
                'network': network_power
            }
        }
    def audit_script(self, script_path: str, duration: int = 60, 
                    include_network: bool = False) -> Dict[str, Any]:
        """Audit a script's resource usage and estimate CO2 emissions.
        
        Args:
            script_path: Path to the script to audit
            duration: Monitoring duration in seconds
            include_network: Whether to include network usage in calculations
            
        Returns:
            Dictionary containing audit results
        """
        script_path = Path(script_path)
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        logger.info(f"Starting audit of script: {script_path}")
        logger.info(f"Monitoring duration: {duration} seconds")
        
        # Reset monitoring data
        self.monitoring_data = []
        self.monitoring_active = True
        
        # Get initial system state
        initial_stats = self._get_system_stats(include_network)
        
        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=self._monitor_resources,
            args=(duration, include_network)
        )
        monitor_thread.start()
        
        # Execute the script
        start_time = time.time()
        try:
            result = subprocess.run(
                ['python', str(script_path)],
                capture_output=True,
                text=True,
                timeout=duration + 10  # Allow some buffer
            )
            execution_successful = result.returncode == 0
            script_output = result.stdout
            script_errors = result.stderr
        except subprocess.TimeoutExpired:
            execution_successful = False
            script_output = ""
            script_errors = "Script execution timed out"
        except Exception as e:
            execution_successful = False
            script_output = ""
            script_errors = str(e)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        # Stop monitoring
        self.monitoring_active = False
        monitor_thread.join()
        
        # Get final system state
        final_stats = self._get_system_stats(include_network)
        
        # Calculate results
        results = self._calculate_emissions(
            initial_stats, final_stats, actual_duration, include_network
        )
        
        # Add script execution info
        results.update({
            'script_path': str(script_path),
            'execution_duration_seconds': actual_duration,
            'execution_successful': execution_successful,
            'script_output': script_output[:1000] if script_output else "",  # Limit output size
            'script_errors': script_errors[:1000] if script_errors else "",
            'monitoring_samples': len(self.monitoring_data),
            'audit_timestamp': time.time()
        })
        
        return results
    
    def _monitor_resources(self, duration: int, include_network: bool):
        """Monitor system resources during script execution."""
        start_time = time.time()
        sample_interval = 1.0  # Sample every second
        
        while self.monitoring_active and (time.time() - start_time) < duration:
            try:
                stats = self._get_system_stats(include_network)
                stats['timestamp'] = time.time()
                self.monitoring_data.append(stats)
                time.sleep(sample_interval)
            except Exception as e:
                logger.warning(f"Error collecting monitoring data: {e}")
                time.sleep(sample_interval)
    
    def _get_system_stats(self, include_network: bool = False) -> Dict[str, Any]:
        """Get current system resource statistics."""
        stats = {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_used_gb': psutil.virtual_memory().used / (1024**3),
            'disk_io_read_bytes': psutil.disk_io_counters().read_bytes if psutil.disk_io_counters() else 0,
            'disk_io_write_bytes': psutil.disk_io_counters().write_bytes if psutil.disk_io_counters() else 0,
        }
        
        if include_network:
            net_io = psutil.net_io_counters()
            stats.update({
                'network_bytes_sent': net_io.bytes_sent,
                'network_bytes_recv': net_io.bytes_recv,
            })
        
        return stats
    
    def _calculate_emissions(self, initial_stats: Dict, final_stats: Dict, 
                           duration: float, include_network: bool) -> Dict[str, Any]:
        """Calculate CO2 emissions based on resource usage."""
        
        # Calculate average resource usage from monitoring data
        if self.monitoring_data:
            avg_cpu_percent = sum(d['cpu_percent'] for d in self.monitoring_data) / len(self.monitoring_data)
            peak_memory_gb = max(d['memory_used_gb'] for d in self.monitoring_data)
            avg_memory_gb = sum(d['memory_used_gb'] for d in self.monitoring_data) / len(self.monitoring_data)
        else:
            # Fallback to simple calculation
            avg_cpu_percent = (initial_stats['cpu_percent'] + final_stats['cpu_percent']) / 2
            peak_memory_gb = max(initial_stats['memory_used_gb'], final_stats['memory_used_gb'])
            avg_memory_gb = (initial_stats['memory_used_gb'] + final_stats['memory_used_gb']) / 2
        
        # Calculate power consumption
        
        # CPU power (proportional to usage)
        cpu_power_watts = (avg_cpu_percent / 100) * self.cpu_tdp
        
        # Memory power (proportional to usage)
        memory_power_watts = avg_memory_gb * self.memory_power_per_gb
        
        # Disk I/O power (simplified)
        disk_read_diff = final_stats['disk_io_read_bytes'] - initial_stats['disk_io_read_bytes']
        disk_write_diff = final_stats['disk_io_write_bytes'] - initial_stats['disk_io_write_bytes']
        total_disk_io_gb = (disk_read_diff + disk_write_diff) / (1024**3)
        disk_power_watts = min(total_disk_io_gb * 2, self.DEFAULT_DISK_POWER)  # Cap at default
        
        # Network power (if included)
        network_power_watts = 0
        network_mb = 0
        if include_network:
            network_sent_diff = final_stats['network_bytes_sent'] - initial_stats['network_bytes_sent']
            network_recv_diff = final_stats['network_bytes_recv'] - initial_stats['network_bytes_recv']
            network_mb = (network_sent_diff + network_recv_diff) / (1024**2)
            network_power_watts = network_mb * self.DEFAULT_NETWORK_POWER_PER_MB
        
        # Total power consumption
        total_power_watts = cpu_power_watts + memory_power_watts + disk_power_watts + network_power_watts
        
        # Convert to energy consumption (kWh)
        duration_hours = duration / 3600
        total_energy_kwh = (total_power_watts / 1000) * duration_hours
        
        # Calculate CO2 emissions
        total_co2_kg = total_energy_kwh * self.carbon_intensity
        
        # Prepare detailed breakdown
        power_breakdown = {
            'cpu_watts': cpu_power_watts,
            'memory_watts': memory_power_watts,
            'disk_watts': disk_power_watts,
            'network_watts': network_power_watts,
            'total_watts': total_power_watts
        }
        
        return {
            'total_co2_kg': total_co2_kg,
            'total_energy_kwh': total_energy_kwh,
            'avg_cpu_percent': avg_cpu_percent,
            'peak_memory_mb': peak_memory_gb * 1024,
            'avg_memory_mb': avg_memory_gb * 1024,
            'disk_io_gb': total_disk_io_gb,
            'network_mb': network_mb,
            'power_breakdown': power_breakdown,
            'carbon_intensity_kg_per_kwh': self.carbon_intensity,
            'system_info': {
                'cpu_count': self.cpu_count,
                'total_memory_gb': self.total_memory_gb,
                'cpu_tdp_watts': self.cpu_tdp
            }
        }
    
    def audit_multiple_scripts(self, script_paths: List[str], duration_per_script: int = 60,
                              include_network: bool = False) -> Dict[str, Any]:
        """Audit multiple scripts and compare their emissions.
        
        Args:
            script_paths: List of script paths to audit
            duration_per_script: Monitoring duration per script
            include_network: Whether to include network usage
            
        Returns:
            Dictionary containing comparative audit results
        """
        results = {}
        total_co2 = 0
        
        for script_path in script_paths:
            try:
                script_result = self.audit_script(script_path, duration_per_script, include_network)
                results[script_path] = script_result
                total_co2 += script_result['total_co2_kg']
            except Exception as e:
                logger.error(f"Failed to audit script {script_path}: {e}")
                results[script_path] = {
                    'error': str(e),
                    'total_co2_kg': 0
                }
        
        # Add summary
        results['summary'] = {
            'total_scripts': len(script_paths),
            'successful_audits': sum(1 for r in results.values() 
                                   if isinstance(r, dict) and 'error' not in r),
            'total_co2_kg': total_co2,
            'average_co2_per_script': total_co2 / len(script_paths) if script_paths else 0,
            'audit_timestamp': time.time()
        }
        
        return results
    
    def get_system_baseline(self, duration: int = 60) -> Dict[str, Any]:
        """Get baseline system resource usage without running any scripts.
        
        Args:
            duration: Monitoring duration in seconds
            
        Returns:
            Dictionary containing baseline measurements
        """
        logger.info(f"Measuring system baseline for {duration} seconds")
        
        self.monitoring_data = []
        self.monitoring_active = True
        
        # Start monitoring
        monitor_thread = threading.Thread(
            target=self._monitor_resources,
            args=(duration, True)
        )
        monitor_thread.start()
        
        # Wait for monitoring to complete
        time.sleep(duration)
        self.monitoring_active = False
        monitor_thread.join()
        
        if not self.monitoring_data:
            raise RuntimeError("No baseline data collected")
        
        # Calculate baseline statistics
        avg_cpu = sum(d['cpu_percent'] for d in self.monitoring_data) / len(self.monitoring_data)
        avg_memory_gb = sum(d['memory_used_gb'] for d in self.monitoring_data) / len(self.monitoring_data)
        
        # Estimate baseline power consumption
        baseline_cpu_power = (avg_cpu / 100) * self.cpu_tdp
        baseline_memory_power = avg_memory_gb * self.memory_power_per_gb
        baseline_total_power = baseline_cpu_power + baseline_memory_power + 20  # Add base system power
        
        # Calculate baseline CO2
        duration_hours = duration / 3600
        baseline_energy_kwh = (baseline_total_power / 1000) * duration_hours
        baseline_co2_kg = baseline_energy_kwh * self.carbon_intensity
        
        return {
            'duration_seconds': duration,
            'avg_cpu_percent': avg_cpu,
            'avg_memory_gb': avg_memory_gb,
            'baseline_power_watts': baseline_total_power,
            'baseline_energy_kwh': baseline_energy_kwh,
            'baseline_co2_kg': baseline_co2_kg,
            'samples_collected': len(self.monitoring_data),
            'timestamp': time.time()
        }
    
    def _calculate_co2_from_metrics(self, monitoring_data: List[Dict], duration: float, 
                                   carbon_intensity: float, cpu_tdp: float) -> Dict[str, Any]:
        """Calculate CO2 emissions from monitoring metrics data.
        
        This method takes a list of monitoring data points and calculates total CO2 emissions
        based on average resource usage over the monitoring period.
        
        Args:
            monitoring_data: List of dictionaries containing monitoring metrics.
                           Each dict should have keys like:
                           - timestamp: Unix timestamp
                           - system_cpu_percent: Overall system CPU usage (0-100)
                           - script_cpu_percent: Script-specific CPU usage (0-100) [optional]
                           - memory_used_gb: Memory usage in GB
                           - script_memory_mb: Script-specific memory in MB [optional]
                           - disk_read_bytes: Cumulative disk read bytes
                           - disk_write_bytes: Cumulative disk write bytes
                           - network_bytes_sent: Cumulative network bytes sent [optional]
                           - network_bytes_recv: Cumulative network bytes received [optional]
            duration: Total monitoring duration in seconds
            carbon_intensity: Carbon intensity factor (kg CO2 per kWh)
            cpu_tdp: CPU Thermal Design Power in watts
            
        Returns:
            Dictionary containing CO2 calculation results with detailed breakdown
        """
        if not monitoring_data:
            logger.warning("No monitoring data provided for CO2 calculation")
            return {
                'error': 'No monitoring data available',
                'total_co2_kg': 0,
                'total_energy_kwh': 0,
                'avg_system_cpu_percent': 0,
                'avg_script_cpu_percent': 0,
                'peak_memory_gb': 0,
                'avg_memory_gb': 0,
                'total_disk_io_gb': 0,
                'total_network_gb': 0,
                'power_breakdown': {
                    'cpu_watts': 0,
                    'memory_watts': 0,
                    'disk_watts': 0,
                    'network_watts': 0,
                    'total_watts': 0
                },
                'duration_hours': duration / 3600,
                'carbon_intensity': carbon_intensity,
                'cpu_tdp': cpu_tdp
            }
        
        try:
            # Calculate average CPU usage
            system_cpu_values = [d.get('system_cpu_percent', 0) for d in monitoring_data]
            script_cpu_values = [d.get('script_cpu_percent', 0) for d in monitoring_data]
            
            avg_system_cpu_percent = sum(system_cpu_values) / len(system_cpu_values)
            avg_script_cpu_percent = sum(script_cpu_values) / len(script_cpu_values) if any(script_cpu_values) else 0
            
            # Calculate memory usage statistics
            memory_gb_values = [d.get('memory_used_gb', 0) for d in monitoring_data]
            script_memory_mb_values = [d.get('script_memory_mb', 0) for d in monitoring_data]
            
            avg_memory_gb = sum(memory_gb_values) / len(memory_gb_values)
            peak_memory_gb = max(memory_gb_values)
            avg_script_memory_mb = sum(script_memory_mb_values) / len(script_memory_mb_values) if any(script_memory_mb_values) else 0
            
            # Calculate disk I/O (difference between first and last readings)
            if len(monitoring_data) > 1:
                first_sample = monitoring_data[0]
                last_sample = monitoring_data[-1]
                
                disk_read_diff = last_sample.get('disk_read_bytes', 0) - first_sample.get('disk_read_bytes', 0)
                disk_write_diff = last_sample.get('disk_write_bytes', 0) - first_sample.get('disk_write_bytes', 0)
                total_disk_io_bytes = max(0, disk_read_diff + disk_write_diff)
                total_disk_io_gb = total_disk_io_bytes / (1024**3)
                
                # Calculate network usage if available
                network_sent_diff = last_sample.get('network_bytes_sent', 0) - first_sample.get('network_bytes_sent', 0)
                network_recv_diff = last_sample.get('network_bytes_recv', 0) - first_sample.get('network_bytes_recv', 0)
                total_network_bytes = max(0, network_sent_diff + network_recv_diff)
                total_network_gb = total_network_bytes / (1024**3)
            else:
                total_disk_io_gb = 0
                total_network_gb = 0
            
            # Calculate power consumption components
            
            # CPU Power: Use system CPU percentage as it represents actual load
            # For script-specific analysis, you could use script_cpu_percent if available
            cpu_utilization = avg_system_cpu_percent / 100.0
            cpu_power_watts = cpu_utilization * cpu_tdp
            
            # Memory Power: Based on average memory usage
            memory_power_watts = avg_memory_gb * self.memory_power_per_gb
            
            # Disk Power: Estimate based on I/O volume
            # Assume 2W per GB of I/O, capped at reasonable maximum
            disk_power_watts = min(total_disk_io_gb * 2.0, self.DEFAULT_DISK_POWER)
            
            # Network Power: Estimate based on data transfer
            # Assume 0.1W per GB of network traffic
            network_power_watts = total_network_gb * 0.1
            
            # Total power consumption
            total_power_watts = cpu_power_watts + memory_power_watts + disk_power_watts + network_power_watts
            
            # Convert to energy consumption
            duration_hours = duration / 3600.0
            total_energy_kwh = (total_power_watts / 1000.0) * duration_hours
            
            # Calculate CO2 emissions
            total_co2_kg = total_energy_kwh * carbon_intensity
            
            # Create detailed power breakdown
            power_breakdown = {
                'cpu_watts': round(cpu_power_watts, 2),
                'memory_watts': round(memory_power_watts, 2),
                'disk_watts': round(disk_power_watts, 2),
                'network_watts': round(network_power_watts, 2),
                'total_watts': round(total_power_watts, 2)
            }
            
            # Calculate efficiency metrics
            co2_per_cpu_percent = total_co2_kg / avg_system_cpu_percent if avg_system_cpu_percent > 0 else 0
            co2_per_gb_memory = total_co2_kg / avg_memory_gb if avg_memory_gb > 0 else 0
            
            return {
                'total_co2_kg': round(total_co2_kg, 8),
                'total_energy_kwh': round(total_energy_kwh, 6),
                'avg_system_cpu_percent': round(avg_system_cpu_percent, 2),
                'avg_script_cpu_percent': round(avg_script_cpu_percent, 2),
                'peak_memory_gb': round(peak_memory_gb, 3),
                'avg_memory_gb': round(avg_memory_gb, 3),
                'avg_script_memory_mb': round(avg_script_memory_mb, 1),
                'total_disk_io_gb': round(total_disk_io_gb, 3),
                'total_network_gb': round(total_network_gb, 3),
                'power_breakdown': power_breakdown,
                'duration_hours': round(duration_hours, 4),
                'carbon_intensity': carbon_intensity,
                'cpu_tdp': cpu_tdp,
                'samples_analyzed': len(monitoring_data),
                'efficiency_metrics': {
                    'co2_per_cpu_percent': round(co2_per_cpu_percent, 10),
                    'co2_per_gb_memory': round(co2_per_gb_memory, 8),
                    'watts_per_cpu_percent': round(total_power_watts / avg_system_cpu_percent, 3) if avg_system_cpu_percent > 0 else 0
                },
                'resource_utilization': {
                    'cpu_efficiency': round((avg_script_cpu_percent / avg_system_cpu_percent) * 100, 1) if avg_system_cpu_percent > 0 else 0,
                    'memory_utilization_percent': round((avg_memory_gb / self.total_memory_gb) * 100, 1),
                    'power_distribution': {
                        'cpu_percent': round((cpu_power_watts / total_power_watts) * 100, 1) if total_power_watts > 0 else 0,
                        'memory_percent': round((memory_power_watts / total_power_watts) * 100, 1) if total_power_watts > 0 else 0,
                        'disk_percent': round((disk_power_watts / total_power_watts) * 100, 1) if total_power_watts > 0 else 0,
                        'network_percent': round((network_power_watts / total_power_watts) * 100, 1) if total_power_watts > 0 else 0
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating CO2 from metrics: {e}")
            return {
                'error': f'Calculation error: {str(e)}',
                'total_co2_kg': 0,
                'total_energy_kwh': 0,
                'avg_system_cpu_percent': 0,
                'avg_script_cpu_percent': 0,
                'peak_memory_gb': 0,
                'avg_memory_gb': 0,
                'power_breakdown': {
                    'cpu_watts': 0,
                    'memory_watts': 0,
                    'disk_watts': 0,
                    'network_watts': 0,
                    'total_watts': 0
                },
                'duration_hours': duration / 3600,
                'carbon_intensity': carbon_intensity,
                'cpu_tdp': cpu_tdp
            }
