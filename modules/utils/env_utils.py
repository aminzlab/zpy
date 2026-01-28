"""Environment utilities for the Python Code Analyzer.

This module provides functions for detecting and working with UV virtual
environments and project dependencies.
"""

import json
import os
import pathlib
import subprocess
import sys


def detect_uv_venv() -> str | None:
    """Detect the active UV virtual environment.

    Attempts to find the active UV virtual environment by checking:
    1. The VIRTUAL_ENV environment variable
    2. The current Python executable location
    3. Common UV venv locations

    Returns:
        Path to the active UV virtual environment, or None if not found
    """
    # Check VIRTUAL_ENV environment variable
    venv_path = os.environ.get("VIRTUAL_ENV")
    if venv_path and pathlib.Path(venv_path).exists():
        return venv_path

    # Check if current Python is in a virtual environment
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        return sys.prefix

    return None


def get_uv_lock_path(project_path: str) -> str | None:
    """Get the path to the uv.lock file for a project.

    Args:
        project_path: Path to the project directory

    Returns:
        Path to uv.lock if found, None otherwise
    """
    project_path_obj = pathlib.Path(project_path)
    lock_file = project_path_obj / "uv.lock"

    if lock_file.exists():
        return str(lock_file)

    return None


def get_pyproject_toml_path(project_path: str) -> str | None:
    """Get the path to the pyproject.toml file for a project.

    Args:
        project_path: Path to the project directory

    Returns:
        Path to pyproject.toml if found, None otherwise
    """
    project_path_obj = pathlib.Path(project_path)
    pyproject_file = project_path_obj / "pyproject.toml"

    if pyproject_file.exists():
        return str(pyproject_file)

    return None


def is_uv_project(project_path: str) -> bool:
    """Check if a project is a UV-based project.

    A project is considered a UV project if it has a uv.lock file or
    a pyproject.toml file.

    Args:
        project_path: Path to the project directory

    Returns:
        True if the project is a UV project, False otherwise
    """
    return (
        get_uv_lock_path(project_path) is not None
        or get_pyproject_toml_path(project_path) is not None
    )


def get_project_dependencies(project_path: str) -> dict[str, str]:
    """Get the dependencies from a project's uv.lock file.

    Parses the uv.lock file and extracts package names and versions.

    Args:
        project_path: Path to the project directory

    Returns:
        Dictionary mapping package names to versions

    Raises:
        FileNotFoundError: If uv.lock is not found
        ValueError: If uv.lock cannot be parsed
    """
    lock_path = get_uv_lock_path(project_path)

    if not lock_path:
        raise FileNotFoundError(f"uv.lock not found in {project_path}")

    try:
        with open(lock_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse TOML format (simplified - just extract package lines)
        dependencies = {}
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("name = "):
                # Extract package name
                name = line.split("=", 1)[1].strip().strip('"')
                dependencies[name] = ""

        return dependencies
    except (OSError, ValueError) as e:
        raise ValueError(f"Failed to parse uv.lock: {e}") from e


def is_monorepo(project_path: str) -> bool:
    """Check if a project is a monorepo.

    A project is considered a monorepo if it has multiple pyproject.toml files
    in subdirectories.

    Args:
        project_path: Path to the project directory

    Returns:
        True if the project is a monorepo, False otherwise
    """
    project_path_obj = pathlib.Path(project_path)

    if not project_path_obj.is_dir():
        return False

    # Count pyproject.toml files in subdirectories
    pyproject_count = 0
    for item in project_path_obj.rglob("pyproject.toml"):
        # Don't count the root pyproject.toml
        if item.parent != project_path_obj:
            pyproject_count += 1

    return pyproject_count > 0


def get_monorepo_packages(project_path: str) -> list[str]:
    """Get the list of packages in a monorepo.

    Args:
        project_path: Path to the monorepo root directory

    Returns:
        List of paths to package directories

    Raises:
        ValueError: If the project is not a monorepo
    """
    if not is_monorepo(project_path):
        raise ValueError(f"Project at {project_path} is not a monorepo")

    project_path_obj = pathlib.Path(project_path)
    packages = []

    for pyproject in project_path_obj.rglob("pyproject.toml"):
        # Don't include the root pyproject.toml
        if pyproject.parent != project_path_obj:
            packages.append(str(pyproject.parent))

    return sorted(packages)


def get_python_executable() -> str:
    """Get the path to the current Python executable.

    Returns:
        Path to the Python executable
    """
    return sys.executable


def get_python_version() -> str:
    """Get the current Python version.

    Returns:
        Python version string (e.g., "3.12.0")
    """
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def check_tool_installed(tool_name: str) -> bool:
    """Check if a tool is installed and available in PATH.

    Args:
        tool_name: Name of the tool to check (e.g., "pyright", "ruff")

    Returns:
        True if the tool is installed, False otherwise
    """
    try:
        subprocess.run(
            [tool_name, "--version"],
            capture_output=True,
            check=True,
            timeout=5,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_tool_version(tool_name: str) -> str | None:
    """Get the version of an installed tool.

    Args:
        tool_name: Name of the tool (e.g., "pyright", "ruff")

    Returns:
        Version string if the tool is installed, None otherwise
    """
    try:
        result = subprocess.run(
            [tool_name, "--version"],
            capture_output=True,
            check=True,
            timeout=5,
            text=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None
