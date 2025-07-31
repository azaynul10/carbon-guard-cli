# Pre-commit Setup for Carbon Guard CLI

This document explains the pre-commit configuration for the Carbon Guard CLI project.

## 🚀 Quick Start

```bash
# Install pre-commit hooks
./pre-commit-helper.sh install

# Run all checks
./pre-commit-helper.sh run

# Apply auto-fixes and run checks
./pre-commit-helper.sh fix
```

## 📋 What's Included

Our pre-commit configuration includes the following checks:

### Built-in Hooks
- **trailing-whitespace**: Removes trailing whitespace
- **end-of-file-fixer**: Ensures files end with a newline
- **check-yaml**: Validates YAML syntax
- **check-json**: Validates JSON syntax
- **check-added-large-files**: Prevents large files from being committed
- **check-case-conflict**: Prevents case-sensitive filename conflicts
- **check-merge-conflict**: Detects merge conflict markers
- **mixed-line-ending**: Fixes mixed line endings
- **requirements-txt-fixer**: Sorts requirements.txt files

### Python Code Quality
- **Black**: Code formatting with 88-character line length
- **isort**: Import sorting compatible with Black
- **autoflake**: Removes unused imports and variables

## 🔧 Configuration Files

### `.pre-commit-config.yaml`
Main configuration file defining all hooks and their settings.

### `.flake8`
Configuration for flake8 linting (used for reference, not in pre-commit):
- Line length: 88 characters
- Ignores common formatting issues handled by Black
- Excludes test files and examples from strict rules

## 📁 Excluded Files

The following files/directories are excluded from pre-commit checks:
- `venv/` and `.venv/` - Virtual environments
- `build/`, `dist/` - Build artifacts
- `__pycache__/`, `.pytest_cache/` - Python cache directories
- `*.egg-info/` - Package metadata
- `.history/` - History files
- `boto3_ec2_co2_example.py` - Example file with intentional formatting

## 🛠️ Manual Usage

### Install Pre-commit
```bash
# Activate virtual environment
source venv/bin/activate

# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
pre-commit install --hook-type commit-msg
```

### Run Checks
```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run black
pre-commit run isort
```

### Update Hooks
```bash
# Update to latest versions
pre-commit autoupdate
```

## 🔍 Troubleshooting

### Common Issues

#### 1. "No module named 'pre_commit'"
```bash
# Solution: Install pre-commit in virtual environment
source venv/bin/activate
pip install pre-commit
```

#### 2. "Files were modified by this hook"
This is normal behavior. Pre-commit automatically fixes formatting issues. Simply run the checks again:
```bash
pre-commit run --all-files
```

#### 3. Syntax errors in Python files
Fix the syntax errors manually, then run pre-commit again. Files with syntax errors are excluded from formatting.

#### 4. Large files detected
Either:
- Remove the large file: `git rm large_file.txt`
- Add to `.gitignore` if it shouldn't be tracked
- Use Git LFS for legitimate large files

### Bypassing Pre-commit (Not Recommended)
```bash
# Skip pre-commit hooks (emergency only)
git commit --no-verify -m "Emergency commit"
```

## 📊 Integration with CI/CD

The pre-commit configuration works seamlessly with GitHub Actions:

```yaml
# .github/workflows/pre-commit.yml
name: Pre-commit
on: [push, pull_request]
jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - uses: pre-commit/action@v3.0.0
```

## 🎯 Best Practices

1. **Run pre-commit before committing**:
   ```bash
   ./pre-commit-helper.sh run
   git add .
   git commit -m "Your commit message"
   ```

2. **Use the helper script** for common tasks:
   ```bash
   ./pre-commit-helper.sh fix  # Auto-fix and check
   ```

3. **Keep hooks updated**:
   ```bash
   ./pre-commit-helper.sh update
   ```

4. **Add comments for intentional violations**:
   ```python
   print("Debug info")  # OK: print - intentional debug output
   ```

## 📈 Benefits

- **Consistent Code Style**: All contributors follow the same formatting rules
- **Catch Issues Early**: Problems are caught before they reach the repository
- **Automated Fixes**: Many issues are automatically resolved
- **Improved Code Quality**: Removes unused imports, fixes formatting
- **Faster Reviews**: Less time spent on style discussions in PRs

## 🔄 Workflow Integration

Pre-commit hooks run automatically:
1. **On commit**: Checks staged files
2. **On push**: Can be configured for additional checks
3. **In CI/CD**: Validates all changes in pull requests

This ensures code quality is maintained throughout the development process.

## 📞 Support

If you encounter issues with pre-commit:
1. Check this documentation
2. Run `./pre-commit-helper.sh help`
3. Check the pre-commit logs: `~/.cache/pre-commit/pre-commit.log`
4. Create an issue in the project repository
