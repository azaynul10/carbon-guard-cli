#!/bin/bash
# Pre-commit helper script for Carbon Guard CLI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Carbon Guard CLI Pre-commit Helper${NC}"
echo "======================================"

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${RED}❌ Virtual environment not found. Please run: python -m venv venv${NC}"
    exit 1
fi

# Function to run pre-commit
run_precommit() {
    echo -e "${YELLOW}🚀 Running pre-commit checks...${NC}"
    if pre-commit run --all-files; then
        echo -e "${GREEN}✅ All pre-commit checks passed!${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Some files were modified by pre-commit hooks${NC}"
        echo -e "${YELLOW}🔄 Running checks again to verify...${NC}"
        if pre-commit run --all-files; then
            echo -e "${GREEN}✅ All checks now pass!${NC}"
            return 0
        else
            echo -e "${RED}❌ Some checks still failing${NC}"
            return 1
        fi
    fi
}

# Function to update pre-commit hooks
update_hooks() {
    echo -e "${YELLOW}🔄 Updating pre-commit hooks...${NC}"
    pre-commit autoupdate
    echo -e "${GREEN}✅ Hooks updated!${NC}"
}

# Function to install pre-commit
install_precommit() {
    echo -e "${YELLOW}📥 Installing pre-commit hooks...${NC}"
    pre-commit install
    pre-commit install --hook-type commit-msg
    echo -e "${GREEN}✅ Pre-commit hooks installed!${NC}"
}

# Main menu
case "${1:-run}" in
    "run")
        run_precommit
        ;;
    "install")
        install_precommit
        ;;
    "update")
        update_hooks
        ;;
    "fix")
        echo -e "${YELLOW}🔧 Running auto-fixes...${NC}"
        # Run black to format code
        black --line-length=88 carbon_guard/ || true
        # Run isort to sort imports
        isort --profile=black carbon_guard/ || true
        # Run autoflake to remove unused imports
        autoflake --in-place --remove-all-unused-imports --remove-unused-variables carbon_guard/*.py || true
        echo -e "${GREEN}✅ Auto-fixes applied!${NC}"
        run_precommit
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  run     - Run all pre-commit checks (default)"
        echo "  install - Install pre-commit hooks"
        echo "  update  - Update pre-commit hooks to latest versions"
        echo "  fix     - Apply auto-fixes and run checks"
        echo "  help    - Show this help message"
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
