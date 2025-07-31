"""Utility functions for carbon-guard-cli."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration.

    Args:
        verbose: Enable verbose logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Reduce noise from external libraries
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    default_config = {
        "carbon_intensity": 0.000475,  # kg CO2 per kWh (global average)
        "cpu_tdp_watts": 65,
        "memory_power_per_gb": 3,
        "data_directory": "carbon_data",
        "aws": {
            "default_region": "us-east-1",
            "carbon_intensity_by_region": {
                "us-east-1": 0.000415,
                "us-east-2": 0.000523,
                "us-west-1": 0.000351,
                "us-west-2": 0.000351,
                "eu-west-1": 0.000316,
                "eu-central-1": 0.000338,
                "ap-southeast-1": 0.000493,
                "ap-northeast-1": 0.000506,
            },
        },
        "local": {"default_monitoring_duration": 60, "sample_interval": 1.0},
        "personal": {"default_category_filter": "all", "ocr_preprocessing": True},
        "dashboard": {"default_export_format": "csv", "include_raw_data": False},
    }

    if not config_path:
        # Look for config file in common locations
        possible_paths = [
            "carbon-guard.yaml",
            "carbon-guard.yml",
            "~/.carbon-guard.yaml",
            "~/.carbon-guard.yml",
            "/etc/carbon-guard/config.yaml",
        ]

        for path in possible_paths:
            expanded_path = Path(path).expanduser()
            if expanded_path.exists():
                config_path = str(expanded_path)
                break

    if config_path and os.path.exists(config_path):
        try:
            with open(config_path) as f:
                if config_path.endswith((".yaml", ".yml")):
                    user_config = yaml.safe_load(f)
                else:
                    user_config = json.load(f)

            # Merge with default config
            merged_config = deep_merge(default_config, user_config)
            return merged_config

        except Exception as e:
            logging.warning(f"Could not load config from {config_path}: {e}")

    return default_config


def deep_merge(
    base_dict: Dict[str, Any], update_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Deep merge two dictionaries.

    Args:
        base_dict: Base dictionary
        update_dict: Dictionary with updates

    Returns:
        Merged dictionary
    """
    result = base_dict.copy()

    for key, value in update_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def ensure_data_directory(data_dir: str) -> str:
    """Ensure data directory exists.

    Args:
        data_dir: Data directory path

    Returns:
        Absolute path to data directory
    """
    data_path = Path(data_dir).expanduser().resolve()
    data_path.mkdir(parents=True, exist_ok=True)
    return str(data_path)


def format_co2_amount(co2_kg: float) -> str:
    """Format CO2 amount with appropriate units.

    Args:
        co2_kg: CO2 amount in kilograms

    Returns:
        Formatted string with appropriate units
    """
    if co2_kg >= 1000:
        return f"{co2_kg / 1000:.2f} tonnes"
    elif co2_kg >= 1:
        return f"{co2_kg:.3f} kg"
    else:
        return f"{co2_kg * 1000:.1f} g"


def format_energy_amount(energy_kwh: float) -> str:
    """Format energy amount with appropriate units.

    Args:
        energy_kwh: Energy amount in kWh

    Returns:
        Formatted string with appropriate units
    """
    if energy_kwh >= 1:
        return f"{energy_kwh:.3f} kWh"
    else:
        return f"{energy_kwh * 1000:.1f} Wh"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds >= 3600:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{int(hours)}h {int(minutes)}m"
    elif seconds >= 60:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{int(minutes)}m {int(secs)}s"
    else:
        return f"{seconds:.1f}s"


def calculate_carbon_intensity(region: str, config: Dict[str, Any]) -> float:
    """Get carbon intensity for a specific region.

    Args:
        region: AWS region or location
        config: Configuration dictionary

    Returns:
        Carbon intensity in kg CO2 per kWh
    """
    aws_config = config.get("aws", {})
    region_intensities = aws_config.get("carbon_intensity_by_region", {})

    return region_intensities.get(region, config.get("carbon_intensity", 0.000475))


def validate_file_path(file_path: str, must_exist: bool = True) -> Path:
    """Validate and return Path object for file.

    Args:
        file_path: File path string
        must_exist: Whether file must exist

    Returns:
        Path object

    Raises:
        FileNotFoundError: If file must exist but doesn't
        ValueError: If path is invalid
    """
    try:
        path = Path(file_path).expanduser().resolve()

        if must_exist and not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        return path

    except Exception as e:
        raise ValueError(f"Invalid file path '{file_path}': {e}")


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero.

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero

    Returns:
        Division result or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes.

    Args:
        file_path: Path to file

    Returns:
        File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0


def create_sample_config() -> str:
    """Create a sample configuration file.

    Returns:
        Sample configuration content
    """
    sample_config = """# Carbon Guard CLI Configuration

# Global carbon intensity (kg CO2 per kWh)
carbon_intensity: 0.000475

# Local system parameters
cpu_tdp_watts: 65
memory_power_per_gb: 3

# Data storage directory
data_directory: "carbon_data"

# AWS-specific settings
aws:
  default_region: "us-east-1"
  carbon_intensity_by_region:
    us-east-1: 0.000415    # US East (N. Virginia)
    us-east-2: 0.000523    # US East (Ohio)
    us-west-1: 0.000351    # US West (N. California)
    us-west-2: 0.000351    # US West (Oregon)
    eu-west-1: 0.000316    # Europe (Ireland)
    eu-central-1: 0.000338 # Europe (Frankfurt)
    ap-southeast-1: 0.000493  # Asia Pacific (Singapore)
    ap-northeast-1: 0.000506  # Asia Pacific (Tokyo)

# Local auditing settings
local:
  default_monitoring_duration: 60
  sample_interval: 1.0

# Personal carbon tracking settings
personal:
  default_category_filter: "all"
  ocr_preprocessing: true

# Dashboard export settings
dashboard:
  default_export_format: "csv"
  include_raw_data: false
"""
    return sample_config


def save_sample_config(output_path: str = "carbon-guard.yaml") -> str:
    """Save sample configuration to file.

    Args:
        output_path: Output file path

    Returns:
        Path to saved config file
    """
    config_content = create_sample_config()

    with open(output_path, "w") as f:
        f.write(config_content)

    return output_path


class ProgressTracker:
    """Simple progress tracker for long-running operations."""

    def __init__(self, total_steps: int, description: str = "Processing"):
        """Initialize progress tracker.

        Args:
            total_steps: Total number of steps
            description: Description of the operation
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description

    def update(self, step: int = 1, message: str = "") -> None:
        """Update progress.

        Args:
            step: Number of steps to advance
            message: Optional status message
        """
        self.current_step += step
        percentage = (self.current_step / self.total_steps) * 100

        status = f"{self.description}: {self.current_step}/{self.total_steps} ({percentage:.1f}%)"
        if message:
            status += f" - {message}"

        print(f"\r{status}", end="", flush=True)

        if self.current_step >= self.total_steps:
            print()  # New line when complete

    def finish(self, message: str = "Complete") -> None:
        """Mark progress as finished.

        Args:
            message: Completion message
        """
        self.current_step = self.total_steps
        print(f"\r{self.description}: {message}")


def estimate_co2_equivalent(activity: str, amount: float, unit: str = "kg") -> float:
    """Estimate CO2 equivalent for common activities.

    Args:
        activity: Type of activity
        amount: Amount of activity
        unit: Unit of measurement

    Returns:
        CO2 equivalent in kg
    """
    # CO2 equivalent factors for common activities (synced intensity for electricity to 0.475)
    factors = {
        "electricity_kwh": 0.475,  # kg CO2 per kWh (global average, synced to test)
        "gasoline_liter": 2.31,  # kg CO2 per liter
        "natural_gas_m3": 2.0,  # kg CO2 per cubic meter
        "beef_kg": 27.0,  # kg CO2 per kg
        "chicken_kg": 6.9,  # kg CO2 per kg
        "milk_liter": 3.2,  # kg CO2 per liter
        "cheese_kg": 13.5,  # kg CO2 per kg
        "flight_km": 0.255,  # kg CO2 per passenger-km
        "car_km": 0.21,  # kg CO2 per km (average car)
        "train_km": 0.041,  # kg CO2 per passenger-km
        "bus_km": 0.089,  # kg CO2 per passenger-km
    }

    factor_key = f"{activity}_{unit}"
    factor = factors.get(factor_key, 0.0)
    return amount * factor
