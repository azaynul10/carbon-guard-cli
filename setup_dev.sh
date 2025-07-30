#!/bin/bash

# Carbon Guard CLI Development Setup Script

echo "🌱 Setting up Carbon Guard CLI development environment..."

# Check if Python 3.8+ is available
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
echo "✅ Python version: $python_version"

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    echo "🗑️ Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Check if virtual environment was created successfully
if [ ! -f "venv/bin/activate" ]; then
    echo "❌ Failed to create virtual environment"
    echo "Please ensure python3-venv is installed: sudo apt install python3-venv"
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "📥 Installing requirements..."
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt not found, installing basic dependencies..."
    pip install click boto3 psutil pillow pytesseract pandas pyyaml rich requests docker openpyxl python-dateutil colorama
fi

# Install development requirements
if [ -f "requirements-dev.txt" ]; then
    echo "🛠️ Installing development requirements..."
    pip install -r requirements-dev.txt
else
    echo "⚠️ requirements-dev.txt not found, installing basic dev dependencies..."
    pip install pytest pytest-cov black flake8 mypy
fi

# Install tesseract for OCR functionality
echo "🔍 Installing tesseract OCR..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
elif command -v brew &> /dev/null; then
    brew install tesseract
else
    echo "⚠️ Please install tesseract manually for OCR functionality"
fi

# Create data directory
echo "📁 Creating data directory..."
mkdir -p carbon_data

# Create a simple setup.py if it doesn't exist
if [ ! -f "setup.py" ]; then
    echo "📝 Creating setup.py..."
    cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="carbon-guard-cli",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "boto3>=1.26.0",
        "psutil>=5.9.0",
        "Pillow>=9.0.0",
        "pytesseract>=0.3.10",
        "pandas>=1.5.0",
        "PyYAML>=6.0",
        "rich>=12.0.0",
        "requests>=2.28.0",
        "docker>=6.0.0",
        "openpyxl>=3.0.0",
        "python-dateutil>=2.8.0",
        "colorama>=0.4.0",
    ],
    entry_points={
        "console_scripts": [
            "carbon-guard=carbon_guard.cli:main",
        ],
    },
    python_requires=">=3.8",
)
EOF
fi

# Install the package in development mode
echo "🔧 Installing Carbon Guard CLI in development mode..."
pip install -e .

# Set up pre-commit hooks (if available)
if command -v pre-commit &> /dev/null; then
    echo "🪝 Setting up pre-commit hooks..."
    pre-commit install
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To get started:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run tests: pytest"
echo "3. Try the CLI: python -m carbon_guard.cli --help"
echo "4. Open in VS Code: code ."
echo ""
echo "For AWS functionality, make sure to configure your AWS credentials:"
echo "aws configure"
echo ""
echo "Happy coding! 🚀"
