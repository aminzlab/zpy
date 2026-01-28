# Python Code Analyzer

A comprehensive tool that integrates Pyright and Ruff to analyze, improve, and fix issues in UV-based Python projects according to PEP standards and Google Style Guide conventions.

## Features

- **Type Checking**: Integrated Pyright for comprehensive type analysis
- **Linting**: Integrated Ruff for fast style and quality checks
- **Automatic Fixes**: Apply automatic corrections with dry-run support
- **Type Hints**: Suggest and add type annotations
- **Docstrings**: Validate and improve docstrings per Google Style Guide
- **Multiple Reports**: Terminal, JSON, HTML, and SARIF output formats
- **CI/CD Integration**: Built-in support for GitHub Actions and other CI platforms
- **IDE Integration**: VS Code and PyCharm compatibility
- **Pre-commit Hooks**: Automated checks before commits

## Installation

```bash
uv pip install python-code-analyzer
```

## Quick Start

```bash
# Analyze your project
python-code-analyzer analyze

# Apply automatic fixes
python-code-analyzer fix

# Review suggestions
python-code-analyzer suggest

# Configure your project
python-code-analyzer configure
```

## Documentation

For detailed documentation, see the [docs](./docs) directory.
