"""File utilities for the Python Code Analyzer.

This module provides functions for file operations including:
- Creating backups of files before modification
- Reading and writing files safely
- Validating file paths and permissions
"""

import datetime
import pathlib
import shutil


def create_backup(file_path: str) -> str:
    """Create a backup of a file before modification.

    Creates a backup file with a timestamp suffix in the same directory as the
    original file. The backup contains byte-for-byte identical content to the
    original file.

    Args:
        file_path: Path to the file to backup

    Returns:
        Path to the created backup file

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read or backup cannot be created
        OSError: If backup creation fails for other reasons
    """
    file_path_obj = pathlib.Path(file_path)

    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path_obj.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    # Create backup filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path_obj.parent / f"{file_path_obj.stem}.backup_{timestamp}{file_path_obj.suffix}"

    try:
        shutil.copy2(file_path, str(backup_path))
    except PermissionError as e:
        raise PermissionError(f"Permission denied creating backup for {file_path}") from e
    except OSError as e:
        raise OSError(f"Failed to create backup for {file_path}: {e}") from e

    return str(backup_path)


def read_file(file_path: str) -> str:
    """Read the contents of a file.

    Args:
        file_path: Path to the file to read

    Returns:
        Contents of the file as a string

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be read
        OSError: If reading fails for other reasons
    """
    file_path_obj = pathlib.Path(file_path)

    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path_obj.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    try:
        return file_path_obj.read_text(encoding="utf-8")
    except PermissionError as e:
        raise PermissionError(f"Permission denied reading {file_path}") from e
    except OSError as e:
        raise OSError(f"Failed to read {file_path}: {e}") from e


def write_file(file_path: str, content: str) -> None:
    """Write content to a file.

    Creates the file if it doesn't exist. Overwrites the file if it does exist.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file

    Raises:
        PermissionError: If the file cannot be written
        OSError: If writing fails for other reasons
    """
    file_path_obj = pathlib.Path(file_path)

    # Create parent directories if they don't exist
    file_path_obj.parent.mkdir(parents=True, exist_ok=True)

    try:
        file_path_obj.write_text(content, encoding="utf-8")
    except PermissionError as e:
        raise PermissionError(f"Permission denied writing to {file_path}") from e
    except OSError as e:
        raise OSError(f"Failed to write to {file_path}: {e}") from e


def file_exists(file_path: str) -> bool:
    """Check if a file exists.

    Args:
        file_path: Path to check

    Returns:
        True if the file exists, False otherwise
    """
    return pathlib.Path(file_path).is_file()


def get_file_size(file_path: str) -> int:
    """Get the size of a file in bytes.

    Args:
        file_path: Path to the file

    Returns:
        Size of the file in bytes

    Raises:
        FileNotFoundError: If the file does not exist
    """
    file_path_obj = pathlib.Path(file_path)

    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return file_path_obj.stat().st_size


def get_file_modification_time(file_path: str) -> datetime.datetime:
    """Get the modification time of a file.

    Args:
        file_path: Path to the file

    Returns:
        Modification time as a datetime object

    Raises:
        FileNotFoundError: If the file does not exist
    """
    file_path_obj = pathlib.Path(file_path)

    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    mtime = file_path_obj.stat().st_mtime
    return datetime.datetime.fromtimestamp(mtime)


def is_python_file(file_path: str) -> bool:
    """Check if a file is a Python file.

    Args:
        file_path: Path to check

    Returns:
        True if the file has a .py extension, False otherwise
    """
    return pathlib.Path(file_path).suffix == ".py"


def find_python_files(directory: str) -> list[str]:
    """Find all Python files in a directory recursively.

    Args:
        directory: Path to the directory to search

    Returns:
        List of paths to Python files found

    Raises:
        NotADirectoryError: If the path is not a directory
    """
    dir_path = pathlib.Path(directory)

    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")

    return [str(f) for f in dir_path.rglob("*.py")]


def delete_file(file_path: str) -> None:
    """Delete a file.

    Args:
        file_path: Path to the file to delete

    Raises:
        FileNotFoundError: If the file does not exist
        PermissionError: If the file cannot be deleted
        OSError: If deletion fails for other reasons
    """
    file_path_obj = pathlib.Path(file_path)

    if not file_path_obj.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        file_path_obj.unlink()
    except PermissionError as e:
        raise PermissionError(f"Permission denied deleting {file_path}") from e
    except OSError as e:
        raise OSError(f"Failed to delete {file_path}: {e}") from e
