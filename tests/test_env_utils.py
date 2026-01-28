"""Tests for environment utilities.

This module tests virtual environment detection, project configuration,
and tool availability checking.
"""

import pathlib
import sys
import tempfile
from typing import Generator

import pytest

from modules.utils import env_utils


@pytest.fixture
def temp_dir() -> Generator[pathlib.Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield pathlib.Path(tmpdir)


class TestDetectUvVenv:
    """Tests for the detect_uv_venv function."""

    def test_detect_uv_venv_returns_string_or_none(self) -> None:
        """Test that detect_uv_venv returns string or None."""
        result = env_utils.detect_uv_venv()
        assert result is None or isinstance(result, str)

    def test_detect_uv_venv_in_venv(self) -> None:
        """Test venv detection when in a virtual environment."""
        # This test checks that the function works correctly
        # The actual result depends on the test environment
        result = env_utils.detect_uv_venv()
        # If we're in a venv, it should return a path
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            assert result is not None


class TestGetUvLockPath:
    """Tests for the get_uv_lock_path function."""

    def test_get_uv_lock_path_found(self, temp_dir: pathlib.Path) -> None:
        """Test finding uv.lock file."""
        lock_file = temp_dir / "uv.lock"
        lock_file.write_text("")

        result = env_utils.get_uv_lock_path(str(temp_dir))

        assert result == str(lock_file)

    def test_get_uv_lock_path_not_found(self, temp_dir: pathlib.Path) -> None:
        """Test when uv.lock is not found."""
        result = env_utils.get_uv_lock_path(str(temp_dir))

        assert result is None


class TestGetPyprojectTomlPath:
    """Tests for the get_pyproject_toml_path function."""

    def test_get_pyproject_toml_path_found(self, temp_dir: pathlib.Path) -> None:
        """Test finding pyproject.toml file."""
        pyproject = temp_dir / "pyproject.toml"
        pyproject.write_text("")

        result = env_utils.get_pyproject_toml_path(str(temp_dir))

        assert result == str(pyproject)

    def test_get_pyproject_toml_path_not_found(self, temp_dir: pathlib.Path) -> None:
        """Test when pyproject.toml is not found."""
        result = env_utils.get_pyproject_toml_path(str(temp_dir))

        assert result is None


class TestIsUvProject:
    """Tests for the is_uv_project function."""

    def test_is_uv_project_with_lock_file(self, temp_dir: pathlib.Path) -> None:
        """Test UV project detection with uv.lock."""
        lock_file = temp_dir / "uv.lock"
        lock_file.write_text("")

        assert env_utils.is_uv_project(str(temp_dir)) is True

    def test_is_uv_project_with_pyproject(self, temp_dir: pathlib.Path) -> None:
        """Test UV project detection with pyproject.toml."""
        pyproject = temp_dir / "pyproject.toml"
        pyproject.write_text("")

        assert env_utils.is_uv_project(str(temp_dir)) is True

    def test_is_uv_project_not_uv(self, temp_dir: pathlib.Path) -> None:
        """Test UV project detection when not a UV project."""
        assert env_utils.is_uv_project(str(temp_dir)) is False


class TestGetProjectDependencies:
    """Tests for the get_project_dependencies function."""

    def test_get_project_dependencies_not_found(self, temp_dir: pathlib.Path) -> None:
        """Test getting dependencies when uv.lock is not found."""
        with pytest.raises(FileNotFoundError):
            env_utils.get_project_dependencies(str(temp_dir))

    def test_get_project_dependencies_success(self, temp_dir: pathlib.Path) -> None:
        """Test getting dependencies from uv.lock."""
        lock_file = temp_dir / "uv.lock"
        lock_content = """
[[package]]
name = "pytest"
version = "7.0.0"

[[package]]
name = "hypothesis"
version = "6.0.0"
"""
        lock_file.write_text(lock_content)

        result = env_utils.get_project_dependencies(str(temp_dir))

        assert isinstance(result, dict)
        assert "pytest" in result
        assert "hypothesis" in result


class TestIsMonorepo:
    """Tests for the is_monorepo function."""

    def test_is_monorepo_true(self, temp_dir: pathlib.Path) -> None:
        """Test monorepo detection when true."""
        # Create nested pyproject.toml files
        subdir1 = temp_dir / "package1"
        subdir1.mkdir()
        (subdir1 / "pyproject.toml").write_text("")

        assert env_utils.is_monorepo(str(temp_dir)) is True

    def test_is_monorepo_false(self, temp_dir: pathlib.Path) -> None:
        """Test monorepo detection when false."""
        # Create only root pyproject.toml
        (temp_dir / "pyproject.toml").write_text("")

        assert env_utils.is_monorepo(str(temp_dir)) is False

    def test_is_monorepo_not_directory(self, temp_dir: pathlib.Path) -> None:
        """Test monorepo detection with non-directory path."""
        test_file = temp_dir / "test.py"
        test_file.write_text("")

        assert env_utils.is_monorepo(str(test_file)) is False


class TestGetMonorepoPackages:
    """Tests for the get_monorepo_packages function."""

    def test_get_monorepo_packages_success(self, temp_dir: pathlib.Path) -> None:
        """Test getting monorepo packages."""
        # Create nested structure
        pkg1 = temp_dir / "package1"
        pkg2 = temp_dir / "package2"
        pkg1.mkdir()
        pkg2.mkdir()
        (pkg1 / "pyproject.toml").write_text("")
        (pkg2 / "pyproject.toml").write_text("")

        result = env_utils.get_monorepo_packages(str(temp_dir))

        assert len(result) == 2
        assert any("package1" in p for p in result)
        assert any("package2" in p for p in result)

    def test_get_monorepo_packages_not_monorepo(self, temp_dir: pathlib.Path) -> None:
        """Test getting packages when not a monorepo."""
        with pytest.raises(ValueError, match="is not a monorepo"):
            env_utils.get_monorepo_packages(str(temp_dir))


class TestGetPythonExecutable:
    """Tests for the get_python_executable function."""

    def test_get_python_executable(self) -> None:
        """Test getting Python executable path."""
        result = env_utils.get_python_executable()

        assert isinstance(result, str)
        assert len(result) > 0
        assert result == sys.executable


class TestGetPythonVersion:
    """Tests for the get_python_version function."""

    def test_get_python_version(self) -> None:
        """Test getting Python version."""
        result = env_utils.get_python_version()

        assert isinstance(result, str)
        assert len(result) > 0
        # Should be in format X.Y.Z
        parts = result.split(".")
        assert len(parts) == 3


class TestCheckToolInstalled:
    """Tests for the check_tool_installed function."""

    def test_check_tool_installed_python(self) -> None:
        """Test checking if Python is installed."""
        # Python should always be available
        result = env_utils.check_tool_installed("python")

        assert isinstance(result, bool)

    def test_check_tool_installed_nonexistent(self) -> None:
        """Test checking for non-existent tool."""
        result = env_utils.check_tool_installed("nonexistent_tool_xyz")

        assert result is False


class TestGetToolVersion:
    """Tests for the get_tool_version function."""

    def test_get_tool_version_python(self) -> None:
        """Test getting Python version via tool."""
        result = env_utils.get_tool_version("python")

        assert result is None or isinstance(result, str)

    def test_get_tool_version_nonexistent(self) -> None:
        """Test getting version of non-existent tool."""
        result = env_utils.get_tool_version("nonexistent_tool_xyz")

        assert result is None
