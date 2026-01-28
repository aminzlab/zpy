"""Tests for Git utilities.

This module tests Git integration including repository detection,
changed file detection, and status checking.
"""

import pathlib
import subprocess
import tempfile
from typing import Generator

import pytest

from modules.utils import git_utils


@pytest.fixture
def temp_git_repo() -> Generator[pathlib.Path, None, None]:
    """Create a temporary Git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = pathlib.Path(tmpdir)
        # Initialize git repo
        subprocess.run(
            ["git", "init"],
            cwd=str(repo_path),
            capture_output=True,
            check=True,
        )
        # Configure git user for commits
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=str(repo_path),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=str(repo_path),
            capture_output=True,
            check=True,
        )
        yield repo_path


@pytest.fixture
def temp_dir() -> Generator[pathlib.Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield pathlib.Path(tmpdir)


class TestIsGitRepository:
    """Tests for the is_git_repository function."""

    def test_is_git_repository_true(self, temp_git_repo: pathlib.Path) -> None:
        """Test Git repository detection when true."""
        assert git_utils.is_git_repository(str(temp_git_repo)) is True

    def test_is_git_repository_false(self, temp_dir: pathlib.Path) -> None:
        """Test Git repository detection when false."""
        assert git_utils.is_git_repository(str(temp_dir)) is False


class TestGetChangedFiles:
    """Tests for the get_changed_files function."""

    def test_get_changed_files_not_git_repo(self, temp_dir: pathlib.Path) -> None:
        """Test getting changed files when not in a Git repo."""
        with pytest.raises(ValueError, match="is not a Git repository"):
            git_utils.get_changed_files(str(temp_dir))

    def test_get_changed_files_no_changes(self, temp_git_repo: pathlib.Path) -> None:
        """Test getting changed files when there are no changes."""
        # Create and commit a file
        test_file = temp_git_repo / "test.py"
        test_file.write_text("x = 1")
        subprocess.run(
            ["git", "add", "test.py"],
            cwd=str(temp_git_repo),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=str(temp_git_repo),
            capture_output=True,
            check=True,
        )

        # Get changed files
        files = git_utils.get_changed_files(str(temp_git_repo))

        assert len(files) == 0

    def test_get_changed_files_with_changes(self, temp_git_repo: pathlib.Path) -> None:
        """Test getting changed files when there are changes."""
        # Create and commit a file
        test_file = temp_git_repo / "test.py"
        test_file.write_text("x = 1")
        subprocess.run(
            ["git", "add", "test.py"],
            cwd=str(temp_git_repo),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=str(temp_git_repo),
            capture_output=True,
            check=True,
        )

        # Modify the file
        test_file.write_text("x = 2")

        # Get changed files
        files = git_utils.get_changed_files(str(temp_git_repo))

        assert len(files) == 1
        assert "test.py" in files[0]


class TestGetStagedFiles:
    """Tests for the get_staged_files function."""

    def test_get_staged_files_not_git_repo(self, temp_dir: pathlib.Path) -> None:
        """Test getting staged files when not in a Git repo."""
        with pytest.raises(ValueError, match="is not a Git repository"):
            git_utils.get_staged_files(str(temp_dir))

    def test_get_staged_files_no_staged(self, temp_git_repo: pathlib.Path) -> None:
        """Test getting staged files when there are none."""
        files = git_utils.get_staged_files(str(temp_git_repo))

        assert len(files) == 0

    def test_get_staged_files_with_staged(self, temp_git_repo: pathlib.Path) -> None:
        """Test getting staged files when there are staged changes."""
        # Create and stage a file
        test_file = temp_git_repo / "test.py"
        test_file.write_text("x = 1")
        subprocess.run(
            ["git", "add", "test.py"],
            cwd=str(temp_git_repo),
            capture_output=True,
            check=True,
        )

        # Get staged files
        files = git_utils.get_staged_files(str(temp_git_repo))

        assert len(files) == 1
        assert "test.py" in files[0]


class TestGetUnstagedFiles:
    """Tests for the get_unstaged_files function."""

    def test_get_unstaged_files_not_git_repo(self, temp_dir: pathlib.Path) -> None:
        """Test getting unstaged files when not in a Git repo."""
        with pytest.raises(ValueError, match="is not a Git repository"):
            git_utils.get_unstaged_files(str(temp_dir))

    def test_get_unstaged_files_no_unstaged(self, temp_git_repo: pathlib.Path) -> None:
        """Test getting unstaged files when there are none."""
        files = git_utils.get_unstaged_files(str(temp_git_repo))

        assert len(files) == 0

    def test_get_unstaged_files_with_unstaged(self, temp_git_repo: pathlib.Path) -> None:
        """Test getting unstaged files when there are unstaged changes."""
        # Create, commit, then modify a file
        test_file = temp_git_repo / "test.py"
        test_file.write_text("x = 1")
        subprocess.run(
            ["git", "add", "test.py"],
            cwd=str(temp_git_repo),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=str(temp_git_repo),
            capture_output=True,
            check=True,
        )

        # Modify the file
        test_file.write_text("x = 2")

        # Get unstaged files
        files = git_utils.get_unstaged_files(str(temp_git_repo))

        assert len(files) == 1
        assert "test.py" in files[0]


class TestGetUntrackedFiles:
    """Tests for the get_untracked_files function."""

    def test_get_untracked_files_not_git_repo(self, temp_dir: pathlib.Path) -> None:
        """Test getting untracked files when not in a Git repo."""
        with pytest.raises(ValueError, match="is not a Git repository"):
            git_utils.get_untracked_files(str(temp_dir))

    def test_get_untracked_files_no_untracked(self, temp_git_repo: pathlib.Path) -> None:
        """Test getting untracked files when there are none."""
        files = git_utils.get_untracked_files(str(temp_git_repo))

        assert len(files) == 0

    def test_get_untracked_files_with_untracked(self, temp_git_repo: pathlib.Path) -> None:
        """Test getting untracked files when there are untracked files."""
        # Create an untracked file
        test_file = temp_git_repo / "test.py"
        test_file.write_text("x = 1")

        # Get untracked files
        files = git_utils.get_untracked_files(str(temp_git_repo))

        assert len(files) == 1
        assert "test.py" in files[0]


class TestGetFileStatus:
    """Tests for the get_file_status function."""

    def test_get_file_status_not_git_repo(self, temp_dir: pathlib.Path) -> None:
        """Test getting file status when not in a Git repo."""
        with pytest.raises(ValueError, match="is not a Git repository"):
            git_utils.get_file_status(str(temp_dir), "test.py")

    def test_get_file_status_untracked(self, temp_git_repo: pathlib.Path) -> None:
        """Test getting status of untracked file."""
        # Create an untracked file
        test_file = temp_git_repo / "test.py"
        test_file.write_text("x = 1")

        # Get file status
        status = git_utils.get_file_status(str(temp_git_repo), "test.py")

        assert status == "??"

    def test_get_file_status_modified(self, temp_git_repo: pathlib.Path) -> None:
        """Test getting status of modified file."""
        # Create, commit, then modify a file
        test_file = temp_git_repo / "test.py"
        test_file.write_text("x = 1")
        subprocess.run(
            ["git", "add", "test.py"],
            cwd=str(temp_git_repo),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=str(temp_git_repo),
            capture_output=True,
            check=True,
        )

        # Modify the file
        test_file.write_text("x = 2")

        # Get file status
        status = git_utils.get_file_status(str(temp_git_repo), "test.py")

        # Status can be " M" or "M " depending on git version
        assert status in (" M", "M ")


class TestGetRepositoryRoot:
    """Tests for the get_repository_root function."""

    def test_get_repository_root_success(self, temp_git_repo: pathlib.Path) -> None:
        """Test getting repository root."""
        root = git_utils.get_repository_root(str(temp_git_repo))

        assert root == str(temp_git_repo)

    def test_get_repository_root_not_git_repo(self, temp_dir: pathlib.Path) -> None:
        """Test getting repository root when not in a Git repo."""
        root = git_utils.get_repository_root(str(temp_dir))

        assert root is None


class TestGetCurrentBranch:
    """Tests for the get_current_branch function."""

    def test_get_current_branch_success(self, temp_git_repo: pathlib.Path) -> None:
        """Test getting current branch."""
        # Create and commit a file to establish a branch
        test_file = temp_git_repo / "test.py"
        test_file.write_text("x = 1")
        subprocess.run(
            ["git", "add", "test.py"],
            cwd=str(temp_git_repo),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=str(temp_git_repo),
            capture_output=True,
            check=True,
        )

        branch = git_utils.get_current_branch(str(temp_git_repo))

        # Should be master or main depending on git config
        assert branch in ("master", "main")

    def test_get_current_branch_not_git_repo(self, temp_dir: pathlib.Path) -> None:
        """Test getting current branch when not in a Git repo."""
        branch = git_utils.get_current_branch(str(temp_dir))

        assert branch is None


class TestGetCommitHash:
    """Tests for the get_commit_hash function."""

    def test_get_commit_hash_not_git_repo(self, temp_dir: pathlib.Path) -> None:
        """Test getting commit hash when not in a Git repo."""
        commit = git_utils.get_commit_hash(str(temp_dir))

        assert commit is None

    def test_get_commit_hash_with_commit(self, temp_git_repo: pathlib.Path) -> None:
        """Test getting commit hash when there is a commit."""
        # Create and commit a file
        test_file = temp_git_repo / "test.py"
        test_file.write_text("x = 1")
        subprocess.run(
            ["git", "add", "test.py"],
            cwd=str(temp_git_repo),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=str(temp_git_repo),
            capture_output=True,
            check=True,
        )

        # Get commit hash
        commit = git_utils.get_commit_hash(str(temp_git_repo))

        assert commit is not None
        assert len(commit) == 40  # Full SHA-1 hash

    def test_get_commit_hash_short(self, temp_git_repo: pathlib.Path) -> None:
        """Test getting short commit hash."""
        # Create and commit a file
        test_file = temp_git_repo / "test.py"
        test_file.write_text("x = 1")
        subprocess.run(
            ["git", "add", "test.py"],
            cwd=str(temp_git_repo),
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=str(temp_git_repo),
            capture_output=True,
            check=True,
        )

        # Get short commit hash
        commit = git_utils.get_commit_hash(str(temp_git_repo), short=True)

        assert commit is not None
        assert len(commit) == 7  # Short SHA-1 hash
