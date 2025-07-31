"""Carbon Guard CLI - Monitor and optimize your carbon footprint."""

__version__ = "1.0.0"
__author__ = "Carbon Guard Team"
__email__ = "team@carbonguard.com"

from .aws_auditor import AWSAuditor
from .dashboard_exporter import DashboardExporter
from .dockerfile_optimizer import DockerfileOptimizer
from .local_auditor import LocalAuditor
from .plan_generator import PlanGenerator
from .receipt_parser import ReceiptParser
from .utils import load_config, setup_logging

__all__ = [
    "AWSAuditor",
    "LocalAuditor",
    "DockerfileOptimizer",
    "ReceiptParser",
    "PlanGenerator",
    "DashboardExporter",
    "setup_logging",
    "load_config",
]
