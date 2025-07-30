# 🎭 Mock Flag Troubleshooting Guide

## Issue: "❌ Mock mode requires moto library. Install with: pip install moto"

### Root Cause
The `moto` library was missing from the `requirements.txt` and `setup.py` files, causing fresh installations to lack the required dependency for the `--mock` flag.

### ✅ **FIXED**: Added moto to dependencies

The issue has been resolved by adding `moto>=4.2.0` to both:
- `requirements.txt`
- `setup.py` install_requires

## Installation Solutions

### 1. **Fresh Installation** (Recommended)
```bash
# Clone the repository
git clone https://github.com/carbonguard/carbon-guard-cli.git
cd carbon-guard-cli

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with all dependencies (including moto)
pip install -e .

# Test mock flag
carbon-guard audit-aws --mock --region us-east-1
```

### 2. **Existing Installation Fix**
```bash
# Activate your existing environment
cd carbon-guard-cli
source venv/bin/activate

# Install moto manually
pip install moto>=4.2.0

# Test mock flag
carbon-guard audit-aws --mock --region us-east-1
```

### 3. **Reinstall from Requirements**
```bash
# Activate environment
source venv/bin/activate

# Install all requirements (now includes moto)
pip install -r requirements.txt

# Test mock flag
carbon-guard audit-aws --mock --region us-east-1
```

## Verification Steps

### 1. **Check Moto Installation**
```bash
source venv/bin/activate
pip show moto
```

Expected output:
```
Name: moto
Version: 5.1.9 (or higher)
Summary: A library that allows you to easily mock out tests based on AWS infrastructure
```

### 2. **Test Moto Import**
```bash
python3 -c "
try:
    import moto
    from moto import mock_aws
    print('✅ moto import successful')
    print(f'moto version: {moto.__version__}')
except ImportError as e:
    print(f'❌ moto import failed: {e}')
"
```

### 3. **Test Mock Flag**
```bash
# Basic test
carbon-guard audit-aws --mock --region us-east-1

# With JSON output
carbon-guard audit-aws --mock --region us-east-1 --output test-mock.json
ls -la test-mock.json  # Should exist
```

## Common Issues and Solutions

### Issue 1: "ModuleNotFoundError: No module named 'moto'"
**Solution**: Install moto
```bash
pip install moto>=4.2.0
```

### Issue 2: "ImportError: cannot import name 'mock_aws' from 'moto'"
**Solution**: Update moto to newer version
```bash
pip install --upgrade moto>=4.2.0
```

### Issue 3: Mock flag works but no JSON file created
**Solution**: Use the `--output` flag
```bash
# ❌ No file created
carbon-guard audit-aws --mock

# ✅ File created
carbon-guard audit-aws --mock --output analysis.json
```

### Issue 4: Different Python environment
**Solution**: Ensure you're using the correct environment
```bash
# Check which carbon-guard you're using
which carbon-guard

# Should point to your venv:
# /path/to/carbon-guard-cli/venv/bin/carbon-guard

# If not, activate the correct environment
source /path/to/carbon-guard-cli/venv/bin/activate
```

## Mock Flag Features (Working)

### 1. **Basic Mock Audit**
```bash
carbon-guard audit-aws --mock --region us-east-1
```

Creates:
- 2 EC2 instances (t2.micro, m5.large)
- 3 S3 buckets with test data
- 2 Lambda functions (128MB, 1024MB)
- 1 RDS instance (db.t3.micro)

### 2. **Mock with JSON Output**
```bash
carbon-guard audit-aws --mock --region us-east-1 --output mock-analysis.json
```

Generates complete JSON file with:
- Detailed resource information
- CO2 calculations (precise values in scientific notation)
- Cost estimates
- Timestamps and metadata

### 3. **Mock with Specific Services**
```bash
carbon-guard audit-aws --mock --services ec2 --region us-west-2
```

### 4. **Mock Different Regions**
```bash
carbon-guard audit-aws --mock --region eu-west-1 --output eu-mock.json
```

## Expected Mock Output

### Console Output:
```
🎭 Auditing MOCK AWS infrastructure in region: us-east-1
🎭 Mock AWS resources created successfully!
  • 2 EC2 instances (t2.micro, m5.large)
  • 3 S3 buckets with test data
  • 2 Lambda functions (128MB, 1024MB)
  • 1 RDS instance (db.t3.micro)

📊 Total estimated CO2: 0.0000 kg/hour
  • ec2: 0.0000 kg/hour ($0.11/hour)
  • rds: 0.0000 kg/hour ($0.02/hour)
  • lambda: 0.0000 kg/hour ($0.01/hour)
  • s3: 0.0000 kg/hour ($0.00/hour)

💾 Results saved to: mock-analysis.json
🎭 Note: Results are from mock AWS resources, not real infrastructure
```

### JSON Output Structure:
```json
{
  "ec2": {
    "total_instances": 2,
    "instances": [
      {
        "instance_type": "t2.micro",
        "power_watts": 10,
        "co2_kg_per_hour": 4.15e-06,
        "estimated_cost_per_hour": 0.0116
      }
    ]
  },
  "rds": { /* RDS data */ },
  "lambda": { /* Lambda data */ },
  "s3": { /* S3 data */ }
}
```

## Benefits of Mock Flag

✅ **No AWS costs** during development and testing  
✅ **Consistent test data** for reproducible results  
✅ **Fast execution** - No network calls to AWS  
✅ **Safe testing** - No risk of affecting real infrastructure  
✅ **CI/CD friendly** - Can run in automated pipelines without AWS credentials  
✅ **Complete JSON output** - Full data analysis capabilities  
✅ **Algorithm validation** - Test CO2 calculations with known data  

## Status: ✅ RESOLVED

The mock flag is now fully functional with proper moto dependency management. Fresh installations will automatically include moto, and existing installations can be fixed by installing moto manually or reinstalling from the updated requirements.txt.
