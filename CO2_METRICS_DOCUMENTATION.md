# _calculate_co2_from_metrics Method Documentation

## Overview

The `_calculate_co2_from_metrics` method in the `LocalAuditor` class calculates CO2 emissions from monitoring data collected during script execution. It takes a list of monitoring data points and computes total CO2 emissions based on average resource usage over the monitoring period.

## Method Signature

```python
def _calculate_co2_from_metrics(self, monitoring_data: List[Dict], duration: float, 
                               carbon_intensity: float, cpu_tdp: float) -> Dict[str, Any]:
```

## Parameters

### monitoring_data: List[Dict]
A list of dictionaries containing monitoring metrics. Each dictionary should contain:

**Required Fields:**
- `timestamp`: Unix timestamp (float)
- `system_cpu_percent`: Overall system CPU usage (0-100)
- `memory_used_gb`: Memory usage in GB

**Optional Fields:**
- `script_cpu_percent`: Script-specific CPU usage (0-100)
- `script_memory_mb`: Script-specific memory in MB
- `disk_read_bytes`: Cumulative disk read bytes
- `disk_write_bytes`: Cumulative disk write bytes
- `network_bytes_sent`: Cumulative network bytes sent
- `network_bytes_recv`: Cumulative network bytes received

### duration: float
Total monitoring duration in seconds

### carbon_intensity: float
Carbon intensity factor (kg CO2 per kWh)

### cpu_tdp: float
CPU Thermal Design Power in watts

## Return Value

Returns a dictionary containing detailed CO2 calculation results:

```python
{
    'total_co2_kg': float,              # Total CO2 emissions in kg
    'total_energy_kwh': float,          # Total energy consumption in kWh
    'avg_system_cpu_percent': float,    # Average system CPU usage
    'avg_script_cpu_percent': float,    # Average script CPU usage
    'peak_memory_gb': float,            # Peak memory usage in GB
    'avg_memory_gb': float,             # Average memory usage in GB
    'avg_script_memory_mb': float,      # Average script memory in MB
    'total_disk_io_gb': float,          # Total disk I/O in GB
    'total_network_gb': float,          # Total network usage in GB
    'power_breakdown': {                # Power consumption breakdown
        'cpu_watts': float,
        'memory_watts': float,
        'disk_watts': float,
        'network_watts': float,
        'total_watts': float
    },
    'duration_hours': float,            # Duration in hours
    'carbon_intensity': float,          # Carbon intensity used
    'cpu_tdp': float,                   # CPU TDP used
    'samples_analyzed': int,            # Number of samples processed
    'efficiency_metrics': {             # Efficiency calculations
        'co2_per_cpu_percent': float,
        'co2_per_gb_memory': float,
        'watts_per_cpu_percent': float
    },
    'resource_utilization': {           # Resource utilization analysis
        'cpu_efficiency': float,
        'memory_utilization_percent': float,
        'power_distribution': {
            'cpu_percent': float,
            'memory_percent': float,
            'disk_percent': float,
            'network_percent': float
        }
    }
}
```

## Calculation Methodology

### 1. CPU Power Consumption
```python
cpu_power_watts = (avg_system_cpu_percent / 100.0) * cpu_tdp
```
- Uses average system CPU percentage over the monitoring period
- Multiplies by CPU TDP to get power consumption

### 2. Memory Power Consumption
```python
memory_power_watts = avg_memory_gb * memory_power_per_gb
```
- Uses average memory usage in GB
- Multiplies by power per GB (default: 3W/GB)

### 3. Disk I/O Power Consumption
```python
total_disk_io_gb = (disk_read_diff + disk_write_diff) / (1024**3)
disk_power_watts = min(total_disk_io_gb * 2.0, DEFAULT_DISK_POWER)
```
- Calculates total disk I/O from first to last sample
- Estimates 2W per GB of I/O, capped at 10W

### 4. Network Power Consumption
```python
total_network_gb = (network_sent_diff + network_recv_diff) / (1024**3)
network_power_watts = total_network_gb * 0.1
```
- Calculates total network usage from first to last sample
- Estimates 0.1W per GB of network traffic

### 5. Total Energy and CO2
```python
total_power_watts = cpu_power + memory_power + disk_power + network_power
total_energy_kwh = (total_power_watts / 1000.0) * (duration / 3600.0)
total_co2_kg = total_energy_kwh * carbon_intensity
```

## Usage Examples

### Basic Usage
```python
from carbon_guard.local_auditor import LocalAuditor

auditor = LocalAuditor(config={
    'carbon_intensity': 0.3,  # 300g CO2/kWh
    'cpu_tdp_watts': 65,
    'memory_power_per_gb': 3
})

monitoring_data = [
    {
        'timestamp': 1234567890,
        'system_cpu_percent': 45.0,
        'memory_used_gb': 4.0,
        'disk_read_bytes': 1000000,
        'disk_write_bytes': 500000
    },
    # ... more samples
]

result = auditor._calculate_co2_from_metrics(
    monitoring_data=monitoring_data,
    duration=60,
    carbon_intensity=0.3,
    cpu_tdp=65
)

print(f"CO2 emissions: {result['total_co2_kg']} kg")
print(f"Power consumption: {result['power_breakdown']['total_watts']} W")
```

### With Script-Specific Metrics
```python
monitoring_data = [
    {
        'timestamp': 1234567890,
        'system_cpu_percent': 50.0,
        'script_cpu_percent': 25.0,      # Script-specific CPU
        'memory_used_gb': 4.0,
        'script_memory_mb': 512,         # Script-specific memory
        'disk_read_bytes': 1000000,
        'disk_write_bytes': 500000,
        'network_bytes_sent': 100000,    # Network usage
        'network_bytes_recv': 50000
    },
    # ... more samples
]

result = auditor._calculate_co2_from_metrics(
    monitoring_data, 60, 0.3, 65
)

# Access script-specific metrics
print(f"Script CPU efficiency: {result['resource_utilization']['cpu_efficiency']}%")
print(f"Script memory: {result['avg_script_memory_mb']} MB")
```

## Test Results

Based on our comprehensive testing:

### Lightweight Script (30 seconds)
- **Power**: 14.44W (45% CPU, 55% Memory)
- **CO2**: 0.000036 kg
- **Efficiency**: 21.97x more efficient than intensive scripts

### Moderate Script (60 seconds)
- **Power**: 50.69W (67.6% CPU, 32.4% Memory)
- **CO2**: 0.000253 kg
- **CPU Usage**: 52.7% system, 29.1% script

### Intensive Script (120 seconds)
- **Power**: 79.28W (65.2% CPU, 34.8% Memory)
- **CO2**: 0.000793 kg
- **High Resource Usage**: 79.5% CPU, 9.19 GB memory

## Error Handling

The method handles various edge cases:

1. **Empty Data**: Returns error message and zero values
2. **Single Sample**: Uses that sample for calculations
3. **Missing Fields**: Uses defaults or skips optional calculations
4. **Calculation Errors**: Returns error information

## Integration with LocalAuditor

This method is used internally by the `LocalAuditor` class but can also be called directly for custom monitoring scenarios. It's particularly useful for:

- Analyzing pre-collected monitoring data
- Comparing different scripts' efficiency
- Custom monitoring implementations
- Batch processing of historical data

## Performance Considerations

- **Memory Usage**: Minimal - processes data in a single pass
- **CPU Usage**: O(n) where n is the number of samples
- **Accuracy**: Improves with more frequent sampling (recommended: 1-second intervals)

## Carbon Intensity Values

Common carbon intensity values by region:
- **EU West (Ireland)**: 0.000316 kg CO2/kWh
- **US West (Oregon)**: 0.000351 kg CO2/kWh  
- **US East (Virginia)**: 0.000415 kg CO2/kWh
- **Global Average**: 0.000475 kg CO2/kWh

## Best Practices

1. **Sampling Frequency**: Collect samples every 1-2 seconds for accuracy
2. **Duration**: Monitor for at least 30 seconds for meaningful averages
3. **Baseline**: Consider measuring system baseline before script execution
4. **Validation**: Compare results across similar scripts for consistency
5. **Documentation**: Record monitoring conditions and system specifications
