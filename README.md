# 🌍 Carbon Guard CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-65%20passed-green.svg)](#testing)
[![GitHub Issues](https://img.shields.io/github/issues/azaynul10/carbon-guard-cli)](https://github.com/azaynul10/carbon-guard-cli/issues)
[![GitHub Stars](https://img.shields.io/github/stars/azaynul10/carbon-guard-cli)](https://github.com/azaynul10/carbon-guard-cli/stargazers)

A comprehensive command-line tool for monitoring, analyzing, and optimizing your carbon footprint across AWS infrastructure, local development environments, and personal consumption patterns.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/azaynul10/carbon-guard-cli.git
cd carbon-guard-cli

# Install dependencies
pip install -r requirements.txt

# Install the CLI tool
pip install -e .

# Run your first audit
carbon-guard audit-aws --mock
```

## 🚀 Features

### 🏗️ Infrastructure Monitoring
- **AWS Infrastructure Auditing**: Real-time CO2 emissions estimation for EC2, RDS, Lambda, and S3 services
- **Multi-Region Support**: Accurate carbon intensity calculations for different AWS regions
- **Cost Analysis**: Parallel cost estimation alongside carbon footprint analysis
- **Mock Testing**: Test functionality without real AWS calls using `--mock` flag

### 💻 Development Environment
- **Local Script Monitoring**: Track carbon footprint of script execution with detailed resource usage
- **Dockerfile Optimization**: AI-powered Dockerfile rewriting for reduced carbon impact
- **Real-time Metrics**: CPU, memory, disk I/O, and network usage monitoring

### 📊 Personal Impact Tracking
- **Receipt Image Parsing**: OCR-powered receipt analysis for personal carbon tracking
- **Category-based Analysis**: Food, transport, energy, and goods emission calculations
- **Trend Analysis**: Historical tracking and pattern identification

### 📈 Planning & Optimization
- **AI-Powered Reduction Plans**: Generate actionable CO2 reduction strategies
- **Dashboard Export**: Export data to CSV/Excel/JSON for visualization tools
- **Comprehensive Reporting**: Detailed audit trails and compliance reporting

## 📦 Installation

### Prerequisites

- **Python 3.8+** (Python 3.9+ recommended)
- **AWS CLI v2** (for AWS auditing features)
- **Tesseract OCR** (for receipt image processing)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/azaynul10/carbon-guard-cli.git
cd carbon-guard-cli

# Install in development mode
pip install -e .

# Or install from PyPI (when available)
pip install carbon-guard-cli
```

### System Dependencies

#### Ubuntu/Debian
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng python3-dev

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

#### macOS
```bash
# Install using Homebrew
brew install tesseract python@3.9

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

#### Windows
```bash
# Install Python dependencies
pip install carbon-guard-cli

# Download and install:
# - Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
# - AWS CLI v2: https://awscli.amazonaws.com/AWSCLIV2.msi
```

### Development Installation

```bash
# Clone and set up development environment
git clone https://github.com/azaynul10/carbon-guard-cli.git
cd carbon-guard-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests to verify installation
pytest
```

### Docker Installation

```bash
# Build Docker image
docker build -t carbon-guard-cli .

# Run with Docker
docker run --rm -v $(pwd):/workspace carbon-guard-cli audit-aws --mock
```

### Verification

```bash
# Verify installation
carbon-guard --version
carbon-guard --help

# Test with mock data (no AWS credentials required)
carbon-guard audit-aws --mock --region us-east-1
```

## 🚀 Quick Start

### 1. AWS Infrastructure Audit

```bash
# Basic audit of all AWS services
carbon-guard audit-aws --region us-east-1

# Audit specific services with output
carbon-guard audit-aws --region us-west-2 --services ec2,s3 --output aws_audit.json

# Test with mock data (no AWS account required)
carbon-guard audit-aws --mock --region us-east-1

# Estimate-only mode (faster, less detailed)
carbon-guard audit-aws --estimate-only --region eu-west-1
```

**Example Output:**
```
🌍 Auditing AWS infrastructure in region: us-east-1

📊 Total estimated CO2: 0.0042 kg/hour
  • ec2: 0.0041 kg/hour ($0.12/hour)
  • rds: 0.0001 kg/hour ($0.02/hour)
  • lambda: 0.0000 kg/hour ($0.01/hour)
  • s3: 0.0000 kg/hour ($0.00/hour)

💾 Results saved to: aws_audit.json
```

### 2. Local Script Monitoring

```bash
# Monitor a Python script
carbon-guard audit-local my_script.py --duration 60

# Include network monitoring
carbon-guard audit-local data_processing.py --duration 300 --include-network --output local_audit.json

# Monitor with custom configuration
carbon-guard audit-local --config my-config.yaml training_script.py
```

**Example Output:**
```
🖥️  Monitoring script: my_script.py (60 seconds)

📊 Resource Usage Summary:
  • Average CPU: 45.2%
  • Peak Memory: 2.1 GB
  • Disk I/O: 150 MB read, 75 MB write
  • Network: 25 MB sent, 10 MB received

🌍 Carbon Footprint:
  • Total CO2: 0.0125 kg
  • Power consumption: 42.3 watts average
  • Energy used: 0.0007 kWh

💾 Results saved to: local_audit.json
```

### 3. Personal Carbon Tracking

```bash
# Parse receipt images
carbon-guard track-personal receipt1.jpg receipt2.png

# Filter by category and save results
carbon-guard track-personal grocery_receipts/*.jpg --category food --output personal_audit.json

# Batch process with specific settings
carbon-guard track-personal --config personal-config.yaml receipts/*.png
```

**Example Output:**
```
📄 Processing receipt images...

🛒 Receipt Analysis Results:
  • Total items processed: 15
  • Total cost: $47.83
  • Total CO2 emissions: 12.4 kg

📊 Category Breakdown:
  • Food (meat): 8.2 kg CO2 (66%)
  • Food (dairy): 2.1 kg CO2 (17%)
  • Food (vegetables): 1.8 kg CO2 (15%)
  • Other: 0.3 kg CO2 (2%)

💾 Results saved to: personal_audit.json
```

### 4. Generate Reduction Plans

```bash
# Generate a 20% reduction plan over 12 months
carbon-guard plan --target-reduction 20 --timeframe 12

# Focus on AWS infrastructure with custom target
carbon-guard plan --focus aws --target-reduction 30 --output reduction_plan.json

# Generate comprehensive plan for all areas
carbon-guard plan --focus all --target-reduction 25 --timeframe 6
```

**Example Output:**
```
📋 Generating CO2 reduction plan
🎯 Target reduction: 20.0%
⏰ Timeframe: 12 months

📊 Reduction Plan Summary:
  • Total actions: 5
  • Estimated total reduction: 22.3%
  • Implementation cost: $-450.00 (savings)

🎯 Key Actions:
  1. Optimize EC2 Instance Types
     Impact: 8.5% | Effort: medium | Timeline: 2 weeks
  2. Implement S3 Lifecycle Policies
     Impact: 4.2% | Effort: low | Timeline: 1 week
  3. Right-size RDS Instances
     Impact: 6.1% | Effort: high | Timeline: 4 weeks
  4. Optimize Lambda Memory Allocation
     Impact: 2.8% | Effort: low | Timeline: 1 week
  5. Schedule Non-critical Workloads
     Impact: 0.7% | Effort: medium | Timeline: 3 weeks

💾 Plan saved to: reduction_plan.json
```

### 5. Dashboard Export

```bash
# Export all data to CSV for dashboard creation
carbon-guard dashboard --output dashboard_data.csv

# Export to Excel with date filtering
carbon-guard dashboard --output monthly_report --format excel --date-range 2024-01-01:2024-01-31

# Export specific data types
carbon-guard dashboard --data-dir ./custom_data --output custom_dashboard.json --format json
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=carbon_guard --cov-report=html

# Run specific test categories
pytest tests/test_aws_auditor.py -v
pytest tests/test_local_auditor.py -v
pytest tests/test_cli.py -v

# Run integration tests
pytest tests/integration/ -v

# Run tests with mock AWS resources
pytest tests/test_aws_auditor.py::test_mock_resources -v
```

### Test Categories

#### Unit Tests
- **AWS Auditor Tests**: Test CO2 calculations for all AWS services
- **Local Auditor Tests**: Test system monitoring and resource tracking
- **Receipt Parser Tests**: Test OCR and emission factor calculations
- **CLI Tests**: Test command-line interface functionality
- **Utils Tests**: Test utility functions and configurations

#### Integration Tests
- **End-to-End AWS Auditing**: Test complete AWS audit workflow
- **Mock Resource Testing**: Test with simulated AWS resources
- **File I/O Tests**: Test data persistence and retrieval
- **Configuration Tests**: Test various configuration scenarios

#### Performance Tests
- **Large Dataset Processing**: Test with extensive AWS resources
- **Memory Usage Tests**: Monitor memory consumption during audits
- **Concurrent Processing**: Test parallel audit capabilities

### Mock Testing

The CLI includes comprehensive mock testing capabilities using the `--mock` flag:

```bash
# Test AWS auditing without real AWS resources
carbon-guard audit-aws --mock --region us-east-1

# Test with specific services
carbon-guard audit-aws --mock --services ec2,s3 --region eu-west-1

# Generate test data for development
carbon-guard audit-aws --mock --output test_data.json
```

**Mock Resources Created:**
- 2 EC2 instances (t2.micro, m5.large)
- 3 S3 buckets with varying data sizes
- 2 Lambda functions (128MB, 1024MB memory)
- 1 RDS instance (db.t3.micro)

### Test Data

Sample test data is available in the `tests/data/` directory:

```
tests/data/
├── sample_aws_audit.json
├── sample_local_audit.json
├── sample_personal_audit.json
├── sample_receipts/
│   ├── grocery_receipt.jpg
│   ├── gas_station_receipt.png
│   └── restaurant_receipt.jpg
└── sample_dockerfiles/
    ├── basic_dockerfile
    ├── multi_stage_dockerfile
    └── optimized_dockerfile
```

### Continuous Integration

The project includes GitHub Actions workflows for:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          sudo apt-get install tesseract-ocr
      - name: Run tests
        run: pytest --cov=carbon_guard
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Test Configuration

Create a `pytest.ini` file for test configuration:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    aws: Tests requiring AWS credentials
    mock: Tests using mock resources
```

### Manual Testing Checklist

#### AWS Auditing
- [ ] Test with real AWS credentials
- [ ] Test with mock resources (`--mock` flag)
- [ ] Test different regions
- [ ] Test service-specific auditing
- [ ] Test output file generation
- [ ] Test error handling for invalid credentials

#### Local Auditing
- [ ] Test with different script types (Python, Node.js, etc.)
- [ ] Test various monitoring durations
- [ ] Test network monitoring inclusion
- [ ] Test resource-intensive scripts
- [ ] Test error handling for invalid scripts

#### Personal Tracking
- [ ] Test with various receipt image formats
- [ ] Test OCR accuracy with different image qualities
- [ ] Test category filtering
- [ ] Test batch processing
- [ ] Test error handling for invalid images

#### CLI Interface
- [ ] Test all command help outputs
- [ ] Test global options (--config, --verbose)
- [ ] Test output file formats
- [ ] Test error messages and user feedback
- [ ] Test command completion and suggestions

## ⚙️ Configuration

### Configuration File

Create a configuration file `carbon-guard.yaml` in your project directory or `~/.carbon-guard/config.yaml`:

```yaml
# Global Settings
version: "1.0"
data_directory: "carbon_data"
log_level: "INFO"

# Global carbon intensity (kg CO2 per kWh)
carbon_intensity: 0.000475

# Local system parameters
local:
  cpu_tdp_watts: 65
  memory_power_per_gb: 3
  default_monitoring_duration: 60
  sample_interval: 1.0
  include_network_by_default: false

# AWS-specific settings
aws:
  default_region: "us-east-1"
  default_profile: "default"
  estimate_only_by_default: false
  
  # Regional carbon intensity values (kg CO2 per kWh)
  carbon_intensity_by_region:
    us-east-1: 0.000415    # US East (N. Virginia)
    us-east-2: 0.000523    # US East (Ohio)
    us-west-1: 0.000351    # US West (N. California)
    us-west-2: 0.000351    # US West (Oregon)
    eu-west-1: 0.000316    # Europe (Ireland)
    eu-central-1: 0.000338 # Europe (Frankfurt)
    ap-southeast-1: 0.000493 # Asia Pacific (Singapore)
    ap-northeast-1: 0.000506 # Asia Pacific (Tokyo)
  
  # Service-specific settings
  services:
    ec2:
      include_stopped_instances: false
      detailed_monitoring: true
    rds:
      include_aurora_serverless: true
    lambda:
      utilization_assumption: 0.1  # 10% utilization
    s3:
      include_glacier: true
      storage_class_factors:
        standard: 1.0
        ia: 0.8
        glacier: 0.3

# Personal carbon tracking settings
personal:
  ocr:
    preprocessing: true
    language: "eng"
    confidence_threshold: 60
  
  categories:
    default_filter: "all"
    custom_emission_factors:
      # Custom factors in kg CO2 per unit
      local_beef: 25.0
      organic_vegetables: 1.5
  
  receipt_processing:
    auto_categorize: true
    save_processed_images: false

# Dashboard export settings
dashboard:
  default_format: "csv"
  include_raw_data: false
  date_format: "%Y-%m-%d"
  
  export_options:
    include_metadata: true
    compress_output: false
    split_by_service: true

# Optimization settings
optimization:
  dockerfile:
    default_strategy: "all"
    preserve_comments: true
    backup_original: true
  
  reduction_plans:
    default_target: 20.0
    default_timeframe: 12
    include_cost_analysis: true
    prioritize_quick_wins: true

# Notification settings (optional)
notifications:
  enabled: false
  email:
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your-email@gmail.com"
    # Use environment variable for password: CARBON_GUARD_EMAIL_PASSWORD
  
  thresholds:
    high_co2_alert: 1.0  # kg CO2 per hour
    cost_alert: 100.0    # USD per month
```

### Environment Variables

Set environment variables for sensitive information:

```bash
# AWS Configuration
export AWS_PROFILE=your-profile
export AWS_DEFAULT_REGION=us-east-1

# Carbon Guard Configuration
export CARBON_GUARD_CONFIG_PATH=/path/to/config.yaml
export CARBON_GUARD_DATA_DIR=/path/to/data
export CARBON_GUARD_LOG_LEVEL=DEBUG

# Email notifications (if enabled)
export CARBON_GUARD_EMAIL_PASSWORD=your-app-password

# API Keys (for future integrations)
export CARBON_GUARD_API_KEY=your-api-key
```

### AWS Configuration

#### Credentials Setup

```bash
# Configure AWS CLI
aws configure

# Or use environment variables
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1

# Or use IAM roles (recommended for EC2/Lambda)
# No additional configuration needed
```

#### Required IAM Permissions

Create an IAM policy with the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CarbonGuardAuditPermissions",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceTypes",
                "ec2:DescribeRegions",
                "rds:DescribeDBInstances",
                "rds:DescribeDBClusters",
                "lambda:ListFunctions",
                "lambda:GetFunction",
                "s3:ListAllMyBuckets",
                "s3:GetBucketLocation",
                "s3:GetBucketTagging",
                "cloudwatch:GetMetricStatistics",
                "cloudwatch:ListMetrics",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

### Advanced Configuration

#### Custom Emission Factors

```yaml
# Add custom emission factors for specific items
personal:
  custom_emission_factors:
    # Food items (kg CO2 per kg)
    grass_fed_beef: 22.0
    plant_based_milk: 0.9
    local_vegetables: 1.2
    
    # Transport (kg CO2 per km)
    electric_car: 0.05
    hybrid_car: 0.12
    
    # Energy (kg CO2 per kWh)
    solar_energy: 0.041
    wind_energy: 0.011
```

#### Regional Customization

```yaml
# Customize for specific regions or countries
regional_settings:
  europe:
    carbon_intensity: 0.000295
    currency: "EUR"
    date_format: "%d/%m/%Y"
  
  asia_pacific:
    carbon_intensity: 0.000520
    currency: "USD"
    date_format: "%Y-%m-%d"
```

#### Integration Settings

```yaml
# Integration with external tools
integrations:
  grafana:
    enabled: false
    endpoint: "http://localhost:3000"
    api_key: "${GRAFANA_API_KEY}"
  
  slack:
    enabled: false
    webhook_url: "${SLACK_WEBHOOK_URL}"
    channel: "#carbon-alerts"
  
  jira:
    enabled: false
    server: "https://your-domain.atlassian.net"
    username: "your-email@company.com"
    api_token: "${JIRA_API_TOKEN}"
```

## 📚 Command Reference

### Global Options

Available for all commands:

- `--config, -c PATH`: Path to configuration file
- `--verbose, -v`: Enable verbose logging
- `--help`: Show help message and exit

### audit-aws

Estimate AWS infrastructure CO2 emissions via boto3.

```bash
carbon-guard audit-aws [OPTIONS]
```

**Options:**
- `--region, -r TEXT`: AWS region to audit (default: us-east-1)
- `--services, -s TEXT`: Specific AWS services to audit (ec2, s3, rds, lambda)
- `--profile, -p TEXT`: AWS profile to use
- `--output, -o PATH`: Output file for results (JSON format)
- `--estimate-only`: Only estimate CO2, don't fetch detailed metrics
- `--mock`: Use mock AWS resources for testing (no real AWS calls)

**Examples:**
```bash
# Basic audit
carbon-guard audit-aws

# Multi-region audit
carbon-guard audit-aws --region us-west-2

# Specific services only
carbon-guard audit-aws --services ec2,s3

# Mock testing
carbon-guard audit-aws --mock --region us-east-1

# With custom profile and output
carbon-guard audit-aws --profile production --output prod_audit.json
```

### audit-local

Monitor local script CO2 emissions by tracking system resources.

```bash
carbon-guard audit-local SCRIPT_PATH [OPTIONS]
```

**Arguments:**
- `SCRIPT_PATH`: Path to the script to monitor (required)

**Options:**
- `--duration, -d INTEGER`: Monitoring duration in seconds (default: 60)
- `--output, -o PATH`: Output file for results (JSON format)
- `--include-network`: Include network usage in calculations

**Examples:**
```bash
# Basic monitoring
carbon-guard audit-local my_script.py

# Extended monitoring with network
carbon-guard audit-local data_processor.py --duration 300 --include-network

# Save results
carbon-guard audit-local ml_training.py --output training_audit.json
```

### optimize

Optimize Dockerfiles for reduced carbon footprint.

```bash
carbon-guard optimize DOCKERFILE_PATH [OPTIONS]
```

**Arguments:**
- `DOCKERFILE_PATH`: Path to the Dockerfile to optimize (required)

**Options:**
- `--output, -o PATH`: Output path for optimized Dockerfile
- `--strategy, -s CHOICE`: Optimization strategy (size/layers/cache/all)
- `--dry-run`: Show optimizations without applying changes

**Examples:**
```bash
# Basic optimization
carbon-guard optimize Dockerfile

# Specific strategy
carbon-guard optimize Dockerfile --strategy size

# Preview changes
carbon-guard optimize Dockerfile --dry-run

# Save optimized version
carbon-guard optimize Dockerfile --output Dockerfile.optimized
```

### track-personal

Parse receipt images to track personal carbon footprint.

```bash
carbon-guard track-personal RECEIPT_IMAGES... [OPTIONS]
```

**Arguments:**
- `RECEIPT_IMAGES`: One or more receipt image files (required)

**Options:**
- `--output, -o PATH`: Output file for parsed data (JSON format)
- `--category, -c CHOICE`: Filter by category (transport/energy/food/goods/all)

**Examples:**
```bash
# Single receipt
carbon-guard track-personal receipt.jpg

# Multiple receipts
carbon-guard track-personal receipt1.jpg receipt2.png receipt3.pdf

# Filter by category
carbon-guard track-personal grocery_receipt.jpg --category food

# Batch processing
carbon-guard track-personal receipts/*.jpg --output personal_audit.json
```

### plan

Generate CO2 reduction plans based on audit data.

```bash
carbon-guard plan [OPTIONS]
```

**Options:**
- `--target-reduction, -t FLOAT`: Target CO2 reduction percentage (default: 20.0)
- `--timeframe, -f INTEGER`: Timeframe in months (default: 12)
- `--focus CHOICE`: Focus area for optimization (aws/local/personal/all)
- `--output, -o PATH`: Output file for the plan (JSON format)

**Examples:**
```bash
# Basic plan
carbon-guard plan

# Aggressive reduction target
carbon-guard plan --target-reduction 30 --timeframe 6

# Focus on AWS infrastructure
carbon-guard plan --focus aws --target-reduction 25

# Save plan
carbon-guard plan --output reduction_plan.json
```

### dashboard

Export carbon footprint data to CSV/Excel for dashboard creation.

```bash
carbon-guard dashboard [OPTIONS]
```

**Options:**
- `--data-dir, -d PATH`: Directory containing audit data files
- `--output, -o PATH`: Output file path (required)
- `--format, -f CHOICE`: Export format (csv/excel/json)
- `--date-range TEXT`: Date range filter (YYYY-MM-DD:YYYY-MM-DD)

**Examples:**
```bash
# Basic export
carbon-guard dashboard --output dashboard_data.csv

# Excel format
carbon-guard dashboard --output monthly_report.xlsx --format excel

# Date range filtering
carbon-guard dashboard --output q1_data.csv --date-range 2024-01-01:2024-03-31

# Custom data directory
carbon-guard dashboard --data-dir ./custom_audits --output custom_dashboard.json --format json
```

## 💡 Usage Examples

### Scenario 1: New Project Setup

```bash
# 1. Initialize configuration
mkdir my-carbon-project
cd my-carbon-project
carbon-guard --config init  # Creates default config file

# 2. Test with mock data
carbon-guard audit-aws --mock --output baseline_mock.json

# 3. Run real AWS audit
carbon-guard audit-aws --output baseline_real.json

# 4. Generate initial reduction plan
carbon-guard plan --target-reduction 15 --output initial_plan.json
```

### Scenario 2: Continuous Monitoring

```bash
#!/bin/bash
# daily_audit.sh - Daily carbon footprint monitoring

DATE=$(date +%Y%m%d)
OUTPUT_DIR="audits/$DATE"
mkdir -p "$OUTPUT_DIR"

# AWS audit
carbon-guard audit-aws --output "$OUTPUT_DIR/aws_audit.json"

# Local development audit
carbon-guard audit-local ./daily_scripts/data_sync.py --output "$OUTPUT_DIR/local_audit.json"

# Generate dashboard data
carbon-guard dashboard --output "$OUTPUT_DIR/dashboard.csv"

# Check if reduction targets are met
carbon-guard plan --target-reduction 20 --output "$OUTPUT_DIR/progress_check.json"

echo "Daily audit completed: $OUTPUT_DIR"
```

### Scenario 3: CI/CD Integration

```yaml
# .github/workflows/carbon-audit.yml
name: Carbon Footprint Audit
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 9 * * 1'  # Weekly on Monday

jobs:
  carbon-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install Carbon Guard CLI
        run: pip install carbon-guard-cli
      
      - name: Run Mock Audit (for testing)
        run: carbon-guard audit-aws --mock --output mock_audit.json
      
      - name: Run Real AWS Audit
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: carbon-guard audit-aws --output aws_audit.json
      
      - name: Generate Reduction Plan
        run: carbon-guard plan --target-reduction 25 --output reduction_plan.json
      
      - name: Upload Audit Results
        uses: actions/upload-artifact@v3
        with:
          name: carbon-audit-results
          path: |
            aws_audit.json
            reduction_plan.json
```

### Scenario 4: Multi-Environment Monitoring

```bash
# multi_env_audit.sh - Monitor multiple environments

ENVIRONMENTS=("development" "staging" "production")
REGIONS=("us-east-1" "us-west-2" "eu-west-1")

for env in "${ENVIRONMENTS[@]}"; do
    for region in "${REGIONS[@]}"; do
        echo "Auditing $env environment in $region..."
        
        carbon-guard audit-aws \
            --profile "$env" \
            --region "$region" \
            --output "audits/${env}_${region}_$(date +%Y%m%d).json"
    done
done

# Aggregate results
carbon-guard dashboard \
    --data-dir audits \
    --output "consolidated_report_$(date +%Y%m%d).xlsx" \
    --format excel
```

### Scenario 5: Personal Carbon Tracking Workflow

```bash
# personal_tracking.sh - Monthly personal carbon audit

MONTH=$(date +%Y%m)
RECEIPTS_DIR="receipts/$MONTH"

# Process all receipt images
carbon-guard track-personal "$RECEIPTS_DIR"/*.jpg "$RECEIPTS_DIR"/*.png \
    --output "personal_audits/personal_$MONTH.json"

# Generate personal reduction plan
carbon-guard plan \
    --focus personal \
    --target-reduction 10 \
    --timeframe 3 \
    --output "plans/personal_plan_$MONTH.json"

# Create monthly dashboard
carbon-guard dashboard \
    --data-dir personal_audits \
    --output "dashboards/personal_dashboard_$MONTH.csv" \
    --date-range "$(date -d 'first day of this month' +%Y-%m-%d):$(date -d 'last day of this month' +%Y-%m-%d)"
```

## Data Storage

Carbon Guard CLI stores audit data in JSON format in the `carbon_data` directory (configurable). Each audit creates a timestamped file:

```
carbon_data/
├── aws_audit_20240129_143022.json
├── local_audit_20240129_143155.json
├── personal_audit_20240129_143301.json
└── reduction_plan_20240129_143445.json
```

## AWS Permissions

For AWS auditing, ensure your AWS credentials have the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "rds:DescribeDBInstances",
                "lambda:ListFunctions",
                "s3:ListBuckets",
                "cloudwatch:GetMetricStatistics"
            ],
            "Resource": "*"
        }
    ]
}
```

## Carbon Calculation Methodology

### AWS Infrastructure

- **EC2**: Based on instance type power consumption and regional carbon intensity
- **RDS**: EC2 equivalent with database overhead factor
- **Lambda**: Memory-based power estimation with utilization assumptions
- **S3**: Storage-based power consumption (0.5W per TB)

### Local Scripts

- **CPU**: Proportional to usage percentage and TDP
- **Memory**: Power per GB of allocated memory
- **Disk I/O**: Based on read/write operations
- **Network**: Optional network transfer calculations

### Personal Consumption

- **Food**: Category-based emission factors (kg CO2 per kg)
- **Transport**: Fuel consumption and distance estimates
- **Goods**: Material and manufacturing emission factors

## Optimization Strategies

### Dockerfile Optimization

1. **Base Image**: Recommend smaller, more efficient base images
2. **Layer Reduction**: Combine RUN instructions to reduce layers
3. **Package Management**: Optimize package installation and cleanup
4. **Multi-stage Builds**: Separate build and runtime environments
5. **Caching**: Improve layer caching for faster builds

### AWS Optimization

1. **Right-sizing**: Match instance types to actual usage
2. **Auto Scaling**: Implement demand-based scaling
3. **Scheduling**: Run workloads during low-carbon periods
4. **Storage Optimization**: Use appropriate S3 storage classes
5. **Regional Selection**: Choose regions with cleaner energy

## Dashboard Integration

Export data to popular visualization tools:

- **Excel/Google Sheets**: Basic charts and pivot tables
- **Tableau/Power BI**: Advanced dashboards
- **Grafana**: Time-series monitoring
- **Custom Python/R**: Matplotlib, plotly, ggplot2

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: https://github.com/carbonguard/carbon-guard-cli/issues
- Documentation: https://carbonguard.github.io/carbon-guard-cli/
- Email: support@carbonguard.com

## Changelog

### v1.0.0
- Initial release
- AWS infrastructure auditing
- Local script monitoring
- Dockerfile optimization
- Personal carbon tracking
- Reduction planning
- Dashboard export functionality
