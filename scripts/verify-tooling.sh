#!/bin/bash
set -e

echo "Verifying project tooling..."

# GitHub CLI
if command -v gh &> /dev/null; then
  if gh auth status &> /dev/null; then
    echo "✓ GitHub CLI authenticated"
  else
    echo "✗ GitHub CLI not authenticated. Run: gh auth login"
  fi
else
  echo "⚠ GitHub CLI not installed. Run: brew install gh"
fi

# Python / ruff
if command -v python3 &> /dev/null; then
  echo "✓ Python3 $(python3 --version 2>&1 | cut -d' ' -f2)"
else
  echo "✗ Python3 not installed"
fi

if command -v ruff &> /dev/null; then
  echo "✓ ruff $(ruff --version 2>&1)"
else
  echo "⚠ ruff not installed. Run: pip install ruff"
fi

# Node / npm
if command -v node &> /dev/null; then
  echo "✓ Node $(node --version)"
else
  echo "✗ Node not installed"
fi

if command -v npm &> /dev/null; then
  echo "✓ npm $(npm --version)"
else
  echo "✗ npm not installed"
fi

# pre-commit
if command -v pre-commit &> /dev/null; then
  echo "✓ pre-commit $(pre-commit --version 2>&1)"
else
  echo "⚠ pre-commit not installed. Run: pip install pre-commit"
fi

# Docker
if command -v docker &> /dev/null; then
  echo "✓ Docker $(docker --version 2>&1 | cut -d' ' -f3 | tr -d ',')"
else
  echo "⚠ Docker not installed"
fi

echo ""
echo "Tooling verification complete!"
