"""Carbon Guard CLI - Monitor and optimize your carbon footprint."""

__version__ = "1.0.0"
__author__ = "Carbon Guard Team"
__email__ = "team@carbonguard.com"

from .aws_auditor import AWSAuditor
from .local_auditor import LocalAuditor
from .dockerfile_optimizer import DockerfileOptimizer
from .receipt_parser import ReceiptParser
from .plan_generator import PlanGenerator
from .dashboard_exporter import DashboardExporter
from .utils import setup_logging, load_config

__all__ = [
    'AWSAuditor',
    'LocalAuditor', 
    'DockerfileOptimizer',
    'ReceiptParser',
    'PlanGenerator',
    'DashboardExporter',
    'setup_logging',
    'load_config'
]
