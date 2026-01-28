"""Tests for file utilities.

This module tests file operations including backup creation, reading/writing,
and file discovery.
"""

import pathlib
import tempfile
from typing import Generator

import pytest

from modules.utils import file_utils


@pytest.fixture
def temp_dir() -> Generator[pathlib.Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield pathlib.Path(tmpdir)


class TestCreateBackup:
    """Tests for the create_backup function."""

    def test_create_backup_success(self, temp_dir: pathlib.Path) -> None:
        """Test successful backup creation."""
        # Create a test file
        test_file = temp_dir / "test.py"
        test_file.write_text("original content")

        # Create backup
        backup_path = file_utils.create_backup(str(test_file))

        # Verify backup exists and has identical content
        assert pathlib.Path(backup_path).exists()
        assert pathlib.Path(backup_path).read_text() == "original content"

    def test_create_backup_file_not_found(self, temp_dir: pathlib.Path) -> None:
        """Test backup creation with non-existent file."""
        non_existent = temp_dir / "non_existent.py"
        with pytest.raises(FileNotFoundError):
            file_utils.create_backup(str(non_existent))

    def test_create_backup_is_directory(self, temp_dir: pathlib.Path) -> None:
        """Test backup creation with directory path."""
        with pytest.raises(ValueError, match="Path is not a file"):
            file_utils.create_backup(str(temp_dir))

    def test_create_backup_preserves_content(self, temp_dir: pathlib.Path) -> None:
        """Test that backup preserves exact file content."""
        test_file = temp_dir / "test.py"
        content = "def hello():\n    print('world')\n"
        test_file.write_text(content)

        backup_path = file_utils.create_backup(str(test_file))

        assert pathlib.Path(backup_path).read_text() == content


class TestReadFile:
    """Tests for the read_file function."""

    def test_read_file_success(self, temp_dir: pathlib.Path) -> None:
        """Test successful file reading."""
        test_file = temp_dir / "test.py"
        content = "x = 1"
        test_file.write_text(content)

        result = file_utils.read_file(str(test_file))

        assert result == content

    def test_read_file_not_found(self, temp_dir: pathlib.Path) -> None:
        """Test reading non-existent file."""
        non_existent = temp_dir / "non_existent.py"
        with pytest.raises(FileNotFoundError):
            file_utils.read_file(str(non_existent))

    def test_read_file_is_directory(self, temp_dir: pathlib.Path) -> None:
        """Test reading directory as file."""
        with pytest.raises(ValueError, match="Path is not a file"):
            file_utils.read_file(str(temp_dir))

    def test_read_file_multiline(self, temp_dir: pathlib.Path) -> None:
        """Test reading multiline file."""
        test_file = temp_dir / "test.py"
        content = "line1\nline2\nline3\n"
        test_file.write_text(content)

        result = file_utils.read_file(str(test_file))

        assert result == content


class TestWriteFile:
    """Tests for the write_file function."""

    def test_write_file_success(self, temp_dir: pathlib.Path) -> None:
        """Test successful file writing."""
        test_file = temp_dir / "test.py"
        content = "x = 1"

        file_utils.write_file(str(test_file), content)

        assert test_file.read_text() == content

    def test_write_file_creates_parent_dirs(self, temp_dir: pathlib.Path) -> None:
        """Test that write_file creates parent directories."""
        test_file = temp_dir / "subdir" / "nested" / "test.py"
        content = "x = 1"

        file_utils.write_file(str(test_file), content)

        assert test_file.read_text() == content

    def test_write_file_overwrites_existing(self, temp_dir: pathlib.Path) -> None:
        """Test that write_file overwrites existing files."""
        test_file = temp_dir / "test.py"
        test_file.write_text("old content")

        file_utils.write_file(str(test_file), "new content")

        assert test_file.read_text() == "new content"

    def test_write_file_empty_content(self, temp_dir: pathlib.Path) -> None:
        """Test writing empty content."""
        test_file = temp_dir / "test.py"

        file_utils.write_file(str(test_file), "")

        assert test_file.read_text() == ""


class TestFileExists:
    """Tests for the file_exists function."""

    def test_file_exists_true(self, temp_dir: pathlib.Path) -> None:
        """Test file_exists returns True for existing file."""
        test_file = temp_dir / "test.py"
        test_file.write_text("content")

        assert file_utils.file_exists(str(test_file)) is True

    def test_file_exists_false(self, temp_dir: pathlib.Path) -> None:
        """Test file_exists returns False for non-existent file."""
        non_existent = temp_dir / "non_existent.py"

        assert file_utils.file_exists(str(non_existent)) is False

    def test_file_exists_directory(self, temp_dir: pathlib.Path) -> None:
        """Test file_exists returns False for directory."""
        assert file_utils.file_exists(str(temp_dir)) is False


class TestGetFileSize:
    """Tests for the get_file_size function."""

    def test_get_file_size_success(self, temp_dir: pathlib.Path) -> None:
        """Test getting file size."""
        test_file = temp_dir / "test.py"
        content = "x = 1"
        test_file.write_text(content)

        size = file_utils.get_file_size(str(test_file))

        assert size == len(content)

    def test_get_file_size_not_found(self, temp_dir: pathlib.Path) -> None:
        """Test getting size of non-existent file."""
        non_existent = temp_dir / "non_existent.py"
        with pytest.raises(FileNotFoundError):
            file_utils.get_file_size(str(non_existent))

    def test_get_file_size_empty_file(self, temp_dir: pathlib.Path) -> None:
        """Test getting size of empty file."""
        test_file = temp_dir / "test.py"
        test_file.write_text("")

        size = file_utils.get_file_size(str(test_file))

        assert size == 0


class TestGetFileModificationTime:
    """Tests for the get_file_modification_time function."""

    def test_get_file_modification_time_success(self, temp_dir: pathlib.Path) -> None:
        """Test getting file modification time."""
        test_file = temp_dir / "test.py"
        test_file.write_text("content")

        mtime = file_utils.get_file_modification_time(str(test_file))

        assert mtime is not None

    def test_get_file_modification_time_not_found(self, temp_dir: pathlib.Path) -> None:
        """Test getting modification time of non-existent file."""
        non_existent = temp_dir / "non_existent.py"
        with pytest.raises(FileNotFoundError):
            file_utils.get_file_modification_time(str(non_existent))


class TestIsPythonFile:
    """Tests for the is_python_file function."""

    def test_is_python_file_true(self) -> None:
        """Test is_python_file returns True for .py files."""
        assert file_utils.is_python_file("test.py") is True

    def test_is_python_file_false(self) -> None:
        """Test is_python_file returns False for non-.py files."""
        assert file_utils.is_python_file("test.txt") is False

    def test_is_python_file_no_extension(self) -> None:
        """Test is_python_file returns False for files without extension."""
        assert file_utils.is_python_file("test") is False


class TestFindPythonFiles:
    """Tests for the find_python_files function."""

    def test_find_python_files_success(self, temp_dir: pathlib.Path) -> None:
        """Test finding Python files."""
        # Create test files
        (temp_dir / "test1.py").write_text("x = 1")
        (temp_dir / "test2.py").write_text("y = 2")
        (temp_dir / "test.txt").write_text("not python")

        files = file_utils.find_python_files(str(temp_dir))

        assert len(files) == 2
        assert any("test1.py" in f for f in files)
        assert any("test2.py" in f for f in files)

    def test_find_python_files_recursive(self, temp_dir: pathlib.Path) -> None:
        """Test finding Python files recursively."""
        # Create nested structure
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (temp_dir / "test1.py").write_text("x = 1")
        (subdir / "test2.py").write_text("y = 2")

        files = file_utils.find_python_files(str(temp_dir))

        assert len(files) == 2

    def test_find_python_files_empty_directory(self, temp_dir: pathlib.Path) -> None:
        """Test finding Python files in empty directory."""
        files = file_utils.find_python_files(str(temp_dir))

        assert len(files) == 0

    def test_find_python_files_not_directory(self, temp_dir: pathlib.Path) -> None:
        """Test finding Python files with non-directory path."""
        test_file = temp_dir / "test.py"
        test_file.write_text("x = 1")

        with pytest.raises(NotADirectoryError):
            file_utils.find_python_files(str(test_file))


class TestDeleteFile:
    """Tests for the delete_file function."""

    def test_delete_file_success(self, temp_dir: pathlib.Path) -> None:
        """Test successful file deletion."""
        test_file = temp_dir / "test.py"
        test_file.write_text("content")

        file_utils.delete_file(str(test_file))

        assert not test_file.exists()

    def test_delete_file_not_found(self, temp_dir: pathlib.Path) -> None:
        """Test deleting non-existent file."""
        non_existent = temp_dir / "non_existent.py"
        with pytest.raises(FileNotFoundError):
            file_utils.delete_file(str(non_existent))
