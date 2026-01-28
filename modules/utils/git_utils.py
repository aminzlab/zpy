"""Git utilities for the Python Code Analyzer.

This module provides functions for Git integration including:
- Detecting changed files
- Getting file status
- Checking if a directory is a Git repository
"""

import pathlib
import subprocess


def is_git_repository(directory: str) -> bool:
    """Check if a directory is a Git repository.

    Args:
        directory: Path to the directory to check

    Returns:
        True if the directory is a Git repository, False otherwise
    """
    try:
        subprocess.run(
            ["git", "-C", directory, "rev-parse", "--git-dir"],
            capture_output=True,
            check=True,
            timeout=5,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_changed_files(
    directory: str, base_ref: str | None = None
) -> list[str]:
    """Get the list of changed files in a Git repository.

    Gets files that have been modified, added, or deleted compared to the
    specified base reference (default: HEAD).

    Args:
        directory: Path to the Git repository
        base_ref: Git reference to compare against (default: HEAD)

    Returns:
        List of changed file paths relative to the repository root

    Raises:
        ValueError: If the directory is not a Git repository
        subprocess.CalledProcessError: If the Git command fails
    """
    if not is_git_repository(directory):
        raise ValueError(f"Directory is not a Git repository: {directory}")

    if base_ref is None:
        base_ref = "HEAD"

    try:
        result = subprocess.run(
            ["git", "-C", directory, "diff", "--name-only", base_ref],
            capture_output=True,
            check=True,
            timeout=10,
            text=True,
        )
        files = result.stdout.strip().split("\n")
        return [f for f in files if f]  # Filter out empty strings
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(
            e.returncode, e.cmd, e.output, e.stderr
        ) from e
    except subprocess.TimeoutExpired as e:
        raise subprocess.TimeoutExpired(e.cmd, e.timeout) from e


def get_staged_files(directory: str) -> list[str]:
    """Get the list of staged files in a Git repository.

    Gets files that have been added to the staging area.

    Args:
        directory: Path to the Git repository

    Returns:
        List of staged file paths relative to the repository root

    Raises:
        ValueError: If the directory is not a Git repository
        subprocess.CalledProcessError: If the Git command fails
    """
    if not is_git_repository(directory):
        raise ValueError(f"Directory is not a Git repository: {directory}")

    try:
        result = subprocess.run(
            ["git", "-C", directory, "diff", "--cached", "--name-only"],
            capture_output=True,
            check=True,
            timeout=10,
            text=True,
        )
        files = result.stdout.strip().split("\n")
        return [f for f in files if f]  # Filter out empty strings
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(
            e.returncode, e.cmd, e.output, e.stderr
        ) from e
    except subprocess.TimeoutExpired as e:
        raise subprocess.TimeoutExpired(e.cmd, e.timeout) from e


def get_unstaged_files(directory: str) -> list[str]:
    """Get the list of unstaged files in a Git repository.

    Gets files that have been modified but not staged.

    Args:
        directory: Path to the Git repository

    Returns:
        List of unstaged file paths relative to the repository root

    Raises:
        ValueError: If the directory is not a Git repository
        subprocess.CalledProcessError: If the Git command fails
    """
    if not is_git_repository(directory):
        raise ValueError(f"Directory is not a Git repository: {directory}")

    try:
        result = subprocess.run(
            ["git", "-C", directory, "diff", "--name-only"],
            capture_output=True,
            check=True,
            timeout=10,
            text=True,
        )
        files = result.stdout.strip().split("\n")
        return [f for f in files if f]  # Filter out empty strings
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(
            e.returncode, e.cmd, e.output, e.stderr
        ) from e
    except subprocess.TimeoutExpired as e:
        raise subprocess.TimeoutExpired(e.cmd, e.timeout) from e


def get_untracked_files(directory: str) -> list[str]:
    """Get the list of untracked files in a Git repository.

    Gets files that are not tracked by Git.

    Args:
        directory: Path to the Git repository

    Returns:
        List of untracked file paths relative to the repository root

    Raises:
        ValueError: If the directory is not a Git repository
        subprocess.CalledProcessError: If the Git command fails
    """
    if not is_git_repository(directory):
        raise ValueError(f"Directory is not a Git repository: {directory}")

    try:
        result = subprocess.run(
            ["git", "-C", directory, "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            check=True,
            timeout=10,
            text=True,
        )
        files = result.stdout.strip().split("\n")
        return [f for f in files if f]  # Filter out empty strings
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(
            e.returncode, e.cmd, e.output, e.stderr
        ) from e
    except subprocess.TimeoutExpired as e:
        raise subprocess.TimeoutExpired(e.cmd, e.timeout) from e


def get_file_status(directory: str, file_path: str) -> str | None:
    """Get the Git status of a specific file.

    Args:
        directory: Path to the Git repository
        file_path: Path to the file relative to the repository root

    Returns:
        Status code (M=modified, A=added, D=deleted, etc.) or None if not tracked

    Raises:
        ValueError: If the directory is not a Git repository
        subprocess.CalledProcessError: If the Git command fails
    """
    if not is_git_repository(directory):
        raise ValueError(f"Directory is not a Git repository: {directory}")

    try:
        result = subprocess.run(
            ["git", "-C", directory, "status", "--porcelain", file_path],
            capture_output=True,
            check=True,
            timeout=10,
            text=True,
        )
        output = result.stdout.strip()
        if output:
            return output[:2]  # Return the status code (first 2 characters)
        return None
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(
            e.returncode, e.cmd, e.output, e.stderr
        ) from e
    except subprocess.TimeoutExpired as e:
        raise subprocess.TimeoutExpired(e.cmd, e.timeout) from e


def get_repository_root(directory: str) -> str | None:
    """Get the root directory of a Git repository.

    Args:
        directory: Path within the Git repository

    Returns:
        Path to the repository root, or None if not in a Git repository

    Raises:
        subprocess.CalledProcessError: If the Git command fails
    """
    try:
        result = subprocess.run(
            ["git", "-C", directory, "rev-parse", "--show-toplevel"],
            capture_output=True,
            check=True,
            timeout=5,
            text=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def get_current_branch(directory: str) -> str | None:
    """Get the current Git branch name.

    Args:
        directory: Path within the Git repository

    Returns:
        Current branch name, or None if not in a Git repository

    Raises:
        subprocess.CalledProcessError: If the Git command fails
    """
    try:
        result = subprocess.run(
            ["git", "-C", directory, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            check=True,
            timeout=5,
            text=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def get_commit_hash(directory: str, short: bool = False) -> str | None:
    """Get the current Git commit hash.

    Args:
        directory: Path within the Git repository
        short: If True, return short commit hash (7 characters)

    Returns:
        Commit hash, or None if not in a Git repository

    Raises:
        subprocess.CalledProcessError: If the Git command fails
    """
    try:
        args = ["git", "-C", directory, "rev-parse", "HEAD"]
        result = subprocess.run(
            args,
            capture_output=True,
            check=False,
            timeout=5,
            text=True,
        )
        if result.returncode == 0:
            commit = result.stdout.strip()
            if short:
                return commit[:7]
            return commit
        return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
