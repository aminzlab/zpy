"""Tests for core data models.

This module tests the Issue, Fix, Report, ReportSummary, and Config models
to ensure they properly validate data, serialize/deserialize correctly,
and maintain data integrity.
"""

import datetime
import pytest

import modules.core.models


class TestIssue:
    """Tests for the Issue model."""

    def test_issue_creation_valid(self) -> None:
        """Test creating a valid Issue."""
        issue = modules.core.models.Issue(
            file_path="test.py",
            line=10,
            column=5,
            severity=modules.core.models.Severity.ERROR,
            category=modules.core.models.IssueCategory.TYPE_ERROR,
            code="E501",
            message="Line too long",
            suggestion="Break the line",
            source="ruff",
        )
        assert issue.file_path == "test.py"
        assert issue.line == 10
        assert issue.column == 5
        assert issue.severity == modules.core.models.Severity.ERROR
        assert issue.category == modules.core.models.IssueCategory.TYPE_ERROR
        assert issue.code == "E501"
        assert issue.message == "Line too long"
        assert issue.suggestion == "Break the line"
        assert issue.source == "ruff"

    def test_issue_invalid_line_number(self) -> None:
        """Test that Issue rejects invalid line numbers."""
        with pytest.raises(ValueError, match="Line number must be >= 1"):
            modules.core.models.Issue(
                file_path="test.py",
                line=0,
                column=5,
                severity=modules.core.models.Severity.ERROR,
                category=modules.core.models.IssueCategory.TYPE_ERROR,
                code="E501",
                message="Line too long",
                source="ruff",
            )

    def test_issue_invalid_column_number(self) -> None:
        """Test that Issue rejects invalid column numbers."""
        with pytest.raises(ValueError, match="Column number must be >= 1"):
            modules.core.models.Issue(
                file_path="test.py",
                line=10,
                column=0,
                severity=modules.core.models.Severity.ERROR,
                category=modules.core.models.IssueCategory.TYPE_ERROR,
                code="E501",
                message="Line too long",
                source="ruff",
            )

    def test_issue_empty_file_path(self) -> None:
        """Test that Issue rejects empty file paths."""
        with pytest.raises(ValueError, match="file_path cannot be empty"):
            modules.core.models.Issue(
                file_path="",
                line=10,
                column=5,
                severity=modules.core.models.Severity.ERROR,
                category=modules.core.models.IssueCategory.TYPE_ERROR,
                code="E501",
                message="Line too long",
                source="ruff",
            )

    def test_issue_empty_code(self) -> None:
        """Test that Issue rejects empty codes."""
        with pytest.raises(ValueError, match="code cannot be empty"):
            modules.core.models.Issue(
                file_path="test.py",
                line=10,
                column=5,
                severity=modules.core.models.Severity.ERROR,
                category=modules.core.models.IssueCategory.TYPE_ERROR,
                code="",
                message="Line too long",
                source="ruff",
            )

    def test_issue_empty_message(self) -> None:
        """Test that Issue rejects empty messages."""
        with pytest.raises(ValueError, match="message cannot be empty"):
            modules.core.models.Issue(
                file_path="test.py",
                line=10,
                column=5,
                severity=modules.core.models.Severity.ERROR,
                category=modules.core.models.IssueCategory.TYPE_ERROR,
                code="E501",
                message="",
                source="ruff",
            )

    def test_issue_invalid_source(self) -> None:
        """Test that Issue rejects invalid sources."""
        with pytest.raises(ValueError, match="source must be 'pyright' or 'ruff'"):
            modules.core.models.Issue(
                file_path="test.py",
                line=10,
                column=5,
                severity=modules.core.models.Severity.ERROR,
                category=modules.core.models.IssueCategory.TYPE_ERROR,
                code="E501",
                message="Line too long",
                source="invalid",
            )

    def test_issue_to_dict(self) -> None:
        """Test Issue serialization to dictionary."""
        issue = modules.core.models.Issue(
            file_path="test.py",
            line=10,
            column=5,
            severity=modules.core.models.Severity.ERROR,
            category=modules.core.models.IssueCategory.TYPE_ERROR,
            code="E501",
            message="Line too long",
            suggestion="Break the line",
            source="ruff",
        )
        data = issue.to_dict()
        assert data["file_path"] == "test.py"
        assert data["line"] == 10
        assert data["column"] == 5
        assert data["severity"] == "error"
        assert data["category"] == "type-error"
        assert data["code"] == "E501"
        assert data["message"] == "Line too long"
        assert data["suggestion"] == "Break the line"
        assert data["source"] == "ruff"

    def test_issue_from_dict(self) -> None:
        """Test Issue deserialization from dictionary."""
        data = {
            "file_path": "test.py",
            "line": 10,
            "column": 5,
            "severity": "error",
            "category": "type-error",
            "code": "E501",
            "message": "Line too long",
            "suggestion": "Break the line",
            "source": "ruff",
        }
        issue = modules.core.models.Issue.from_dict(data)
        assert issue.file_path == "test.py"
        assert issue.line == 10
        assert issue.column == 5
        assert issue.severity == modules.core.models.Severity.ERROR
        assert issue.category == modules.core.models.IssueCategory.TYPE_ERROR
        assert issue.code == "E501"
        assert issue.message == "Line too long"
        assert issue.suggestion == "Break the line"
        assert issue.source == "ruff"

    def test_issue_round_trip(self) -> None:
        """Test Issue serialization round-trip."""
        original = modules.core.models.Issue(
            file_path="test.py",
            line=10,
            column=5,
            severity=modules.core.models.Severity.WARNING,
            category=modules.core.models.IssueCategory.STYLE_VIOLATION,
            code="W291",
            message="Trailing whitespace",
            source="ruff",
        )
        data = original.to_dict()
        restored = modules.core.models.Issue.from_dict(data)
        assert restored.file_path == original.file_path
        assert restored.line == original.line
        assert restored.column == original.column
        assert restored.severity == original.severity
        assert restored.category == original.category
        assert restored.code == original.code
        assert restored.message == original.message
        assert restored.source == original.source


class TestFix:
    """Tests for the Fix model."""

    def test_fix_creation_valid(self) -> None:
        """Test creating a valid Fix."""
        issue = modules.core.models.Issue(
            file_path="test.py",
            line=10,
            column=5,
            severity=modules.core.models.Severity.ERROR,
            category=modules.core.models.IssueCategory.TYPE_ERROR,
            code="E501",
            message="Line too long",
            source="ruff",
        )
        fix = modules.core.models.Fix(
            file_path="test.py",
            original_code="x = 1",
            fixed_code="x = 1  # fixed",
            issue=issue,
            explanation="Added comment",
            safe=True,
        )
        assert fix.file_path == "test.py"
        assert fix.original_code == "x = 1"
        assert fix.fixed_code == "x = 1  # fixed"
        assert fix.issue == issue
        assert fix.explanation == "Added comment"
        assert fix.safe is True

    def test_fix_empty_file_path(self) -> None:
        """Test that Fix rejects empty file paths."""
        issue = modules.core.models.Issue(
            file_path="test.py",
            line=10,
            column=5,
            severity=modules.core.models.Severity.ERROR,
            category=modules.core.models.IssueCategory.TYPE_ERROR,
            code="E501",
            message="Line too long",
            source="ruff",
        )
        with pytest.raises(ValueError, match="file_path cannot be empty"):
            modules.core.models.Fix(
                file_path="",
                original_code="x = 1",
                fixed_code="x = 1  # fixed",
                issue=issue,
                explanation="Added comment",
            )

    def test_fix_empty_explanation(self) -> None:
        """Test that Fix rejects empty explanations."""
        issue = modules.core.models.Issue(
            file_path="test.py",
            line=10,
            column=5,
            severity=modules.core.models.Severity.ERROR,
            category=modules.core.models.IssueCategory.TYPE_ERROR,
            code="E501",
            message="Line too long",
            source="ruff",
        )
        with pytest.raises(ValueError, match="explanation cannot be empty"):
            modules.core.models.Fix(
                file_path="test.py",
                original_code="x = 1",
                fixed_code="x = 1  # fixed",
                issue=issue,
                explanation="",
            )

    def test_fix_identical_code(self) -> None:
        """Test that Fix rejects identical original and fixed code."""
        issue = modules.core.models.Issue(
            file_path="test.py",
            line=10,
            column=5,
            severity=modules.core.models.Severity.ERROR,
            category=modules.core.models.IssueCategory.TYPE_ERROR,
            code="E501",
            message="Line too long",
            source="ruff",
        )
        with pytest.raises(ValueError, match="original_code and fixed_code cannot be identical"):
            modules.core.models.Fix(
                file_path="test.py",
                original_code="x = 1",
                fixed_code="x = 1",
                issue=issue,
                explanation="No change",
            )

    def test_fix_to_dict(self) -> None:
        """Test Fix serialization to dictionary."""
        issue = modules.core.models.Issue(
            file_path="test.py",
            line=10,
            column=5,
            severity=modules.core.models.Severity.ERROR,
            category=modules.core.models.IssueCategory.TYPE_ERROR,
            code="E501",
            message="Line too long",
            source="ruff",
        )
        fix = modules.core.models.Fix(
            file_path="test.py",
            original_code="x = 1",
            fixed_code="x = 1  # fixed",
            issue=issue,
            explanation="Added comment",
            safe=True,
        )
        data = fix.to_dict()
        assert data["file_path"] == "test.py"
        assert data["original_code"] == "x = 1"
        assert data["fixed_code"] == "x = 1  # fixed"
        assert data["explanation"] == "Added comment"
        assert data["safe"] is True
        assert "issue" in data

    def test_fix_from_dict(self) -> None:
        """Test Fix deserialization from dictionary."""
        data = {
            "file_path": "test.py",
            "original_code": "x = 1",
            "fixed_code": "x = 1  # fixed",
            "issue": {
                "file_path": "test.py",
                "line": 10,
                "column": 5,
                "severity": "error",
                "category": "type-error",
                "code": "E501",
                "message": "Line too long",
                "source": "ruff",
            },
            "explanation": "Added comment",
            "safe": True,
        }
        fix = modules.core.models.Fix.from_dict(data)
        assert fix.file_path == "test.py"
        assert fix.original_code == "x = 1"
        assert fix.fixed_code == "x = 1  # fixed"
        assert fix.explanation == "Added comment"
        assert fix.safe is True

    def test_fix_round_trip(self) -> None:
        """Test Fix serialization round-trip."""
        issue = modules.core.models.Issue(
            file_path="test.py",
            line=10,
            column=5,
            severity=modules.core.models.Severity.ERROR,
            category=modules.core.models.IssueCategory.TYPE_ERROR,
            code="E501",
            message="Line too long",
            source="ruff",
        )
        original = modules.core.models.Fix(
            file_path="test.py",
            original_code="x = 1",
            fixed_code="x = 1  # fixed",
            issue=issue,
            explanation="Added comment",
            safe=True,
        )
        data = original.to_dict()
        restored = modules.core.models.Fix.from_dict(data)
        assert restored.file_path == original.file_path
        assert restored.original_code == original.original_code
        assert restored.fixed_code == original.fixed_code
        assert restored.explanation == original.explanation
        assert restored.safe == original.safe


class TestReportSummary:
    """Tests for the ReportSummary model."""

    def test_report_summary_creation_valid(self) -> None:
        """Test creating a valid ReportSummary."""
        summary = modules.core.models.ReportSummary(
            total_issues=10,
            errors=3,
            warnings=5,
            infos=2,
            by_category={"type-error": 3, "style-violation": 7},
            by_file={"test.py": 5, "main.py": 5},
        )
        assert summary.total_issues == 10
        assert summary.errors == 3
        assert summary.warnings == 5
        assert summary.infos == 2

    def test_report_summary_negative_total(self) -> None:
        """Test that ReportSummary rejects negative total_issues."""
        with pytest.raises(ValueError, match="total_issues cannot be negative"):
            modules.core.models.ReportSummary(
                total_issues=-1,
                errors=0,
                warnings=0,
                infos=0,
            )

    def test_report_summary_negative_errors(self) -> None:
        """Test that ReportSummary rejects negative errors."""
        with pytest.raises(ValueError, match="errors cannot be negative"):
            modules.core.models.ReportSummary(
                total_issues=0,
                errors=-1,
                warnings=0,
                infos=0,
            )

    def test_report_summary_mismatched_counts(self) -> None:
        """Test that ReportSummary validates count consistency."""
        with pytest.raises(ValueError, match="Sum of errors, warnings, and infos must equal total_issues"):
            modules.core.models.ReportSummary(
                total_issues=10,
                errors=3,
                warnings=5,
                infos=1,  # Should be 2
            )

    def test_report_summary_to_dict(self) -> None:
        """Test ReportSummary serialization to dictionary."""
        summary = modules.core.models.ReportSummary(
            total_issues=10,
            errors=3,
            warnings=5,
            infos=2,
            by_category={"type-error": 3},
            by_file={"test.py": 5},
        )
        data = summary.to_dict()
        assert data["total_issues"] == 10
        assert data["errors"] == 3
        assert data["warnings"] == 5
        assert data["infos"] == 2
        assert data["by_category"] == {"type-error": 3}
        assert data["by_file"] == {"test.py": 5}

    def test_report_summary_from_dict(self) -> None:
        """Test ReportSummary deserialization from dictionary."""
        data = {
            "total_issues": 10,
            "errors": 3,
            "warnings": 5,
            "infos": 2,
            "by_category": {"type-error": 3},
            "by_file": {"test.py": 5},
        }
        summary = modules.core.models.ReportSummary.from_dict(data)
        assert summary.total_issues == 10
        assert summary.errors == 3
        assert summary.warnings == 5
        assert summary.infos == 2

    def test_report_summary_round_trip(self) -> None:
        """Test ReportSummary serialization round-trip."""
        original = modules.core.models.ReportSummary(
            total_issues=10,
            errors=3,
            warnings=5,
            infos=2,
            by_category={"type-error": 3, "style-violation": 7},
            by_file={"test.py": 5, "main.py": 5},
        )
        data = original.to_dict()
        restored = modules.core.models.ReportSummary.from_dict(data)
        assert restored.total_issues == original.total_issues
        assert restored.errors == original.errors
        assert restored.warnings == original.warnings
        assert restored.infos == original.infos
        assert restored.by_category == original.by_category
        assert restored.by_file == original.by_file


class TestReport:
    """Tests for the Report model."""

    def test_report_creation_valid(self) -> None:
        """Test creating a valid Report."""
        issue = modules.core.models.Issue(
            file_path="test.py",
            line=10,
            column=5,
            severity=modules.core.models.Severity.ERROR,
            category=modules.core.models.IssueCategory.TYPE_ERROR,
            code="E501",
            message="Line too long",
            source="ruff",
        )
        summary = modules.core.models.ReportSummary(
            total_issues=1,
            errors=1,
            warnings=0,
            infos=0,
        )
        now = datetime.datetime.now()
        report = modules.core.models.Report(
            issues=[issue],
            fixes=[],
            summary=summary,
            timestamp=now,
            project_path="/project",
        )
        assert len(report.issues) == 1
        assert len(report.fixes) == 0
        assert report.summary == summary
        assert report.timestamp == now
        assert report.project_path == "/project"

    def test_report_empty_project_path(self) -> None:
        """Test that Report rejects empty project paths."""
        summary = modules.core.models.ReportSummary(
            total_issues=0,
            errors=0,
            warnings=0,
            infos=0,
        )
        with pytest.raises(ValueError, match="project_path cannot be empty"):
            modules.core.models.Report(
                issues=[],
                fixes=[],
                summary=summary,
                timestamp=datetime.datetime.now(),
                project_path="",
            )

    def test_report_to_dict(self) -> None:
        """Test Report serialization to dictionary."""
        issue = modules.core.models.Issue(
            file_path="test.py",
            line=10,
            column=5,
            severity=modules.core.models.Severity.ERROR,
            category=modules.core.models.IssueCategory.TYPE_ERROR,
            code="E501",
            message="Line too long",
            source="ruff",
        )
        summary = modules.core.models.ReportSummary(
            total_issues=1,
            errors=1,
            warnings=0,
            infos=0,
        )
        now = datetime.datetime.now()
        report = modules.core.models.Report(
            issues=[issue],
            fixes=[],
            summary=summary,
            timestamp=now,
            project_path="/project",
        )
        data = report.to_dict()
        assert len(data["issues"]) == 1
        assert len(data["fixes"]) == 0
        assert data["project_path"] == "/project"
        assert data["timestamp"] == now.isoformat()

    def test_report_from_dict(self) -> None:
        """Test Report deserialization from dictionary."""
        now = datetime.datetime.now()
        data = {
            "issues": [
                {
                    "file_path": "test.py",
                    "line": 10,
                    "column": 5,
                    "severity": "error",
                    "category": "type-error",
                    "code": "E501",
                    "message": "Line too long",
                    "source": "ruff",
                }
            ],
            "fixes": [],
            "summary": {
                "total_issues": 1,
                "errors": 1,
                "warnings": 0,
                "infos": 0,
            },
            "timestamp": now.isoformat(),
            "project_path": "/project",
        }
        report = modules.core.models.Report.from_dict(data)
        assert len(report.issues) == 1
        assert len(report.fixes) == 0
        assert report.project_path == "/project"

    def test_report_round_trip(self) -> None:
        """Test Report serialization round-trip."""
        issue = modules.core.models.Issue(
            file_path="test.py",
            line=10,
            column=5,
            severity=modules.core.models.Severity.ERROR,
            category=modules.core.models.IssueCategory.TYPE_ERROR,
            code="E501",
            message="Line too long",
            source="ruff",
        )
        summary = modules.core.models.ReportSummary(
            total_issues=1,
            errors=1,
            warnings=0,
            infos=0,
        )
        now = datetime.datetime.now()
        original = modules.core.models.Report(
            issues=[issue],
            fixes=[],
            summary=summary,
            timestamp=now,
            project_path="/project",
        )
        data = original.to_dict()
        restored = modules.core.models.Report.from_dict(data)
        assert len(restored.issues) == len(original.issues)
        assert len(restored.fixes) == len(original.fixes)
        assert restored.project_path == original.project_path


class TestConfig:
    """Tests for the Config model."""

    def test_config_creation_valid(self) -> None:
        """Test creating a valid Config."""
        config = modules.core.models.Config(
            project_path="/project",
            pyright_config={"typeCheckingMode": "standard"},
            ruff_config={"line-length": 100},
            exclusions=["*.pyc", "__pycache__"],
            google_style_guide=True,
            auto_fix_enabled=True,
            backup_enabled=True,
            dry_run=False,
        )
        assert config.project_path == "/project"
        assert config.pyright_config == {"typeCheckingMode": "standard"}
        assert config.ruff_config == {"line-length": 100}
        assert config.exclusions == ["*.pyc", "__pycache__"]
        assert config.google_style_guide is True
        assert config.auto_fix_enabled is True
        assert config.backup_enabled is True
        assert config.dry_run is False

    def test_config_empty_project_path(self) -> None:
        """Test that Config rejects empty project paths."""
        with pytest.raises(ValueError, match="project_path cannot be empty"):
            modules.core.models.Config(project_path="")

    def test_config_defaults(self) -> None:
        """Test Config default values."""
        config = modules.core.models.Config(project_path="/project")
        assert config.pyright_config == {}
        assert config.ruff_config == {}
        assert config.exclusions == []
        assert config.google_style_guide is True
        assert config.auto_fix_enabled is True
        assert config.backup_enabled is True
        assert config.dry_run is False

    def test_config_to_dict(self) -> None:
        """Test Config serialization to dictionary."""
        config = modules.core.models.Config(
            project_path="/project",
            pyright_config={"typeCheckingMode": "standard"},
            ruff_config={"line-length": 100},
            exclusions=["*.pyc"],
            google_style_guide=True,
            auto_fix_enabled=True,
            backup_enabled=True,
            dry_run=False,
        )
        data = config.to_dict()
        assert data["project_path"] == "/project"
        assert data["pyright_config"] == {"typeCheckingMode": "standard"}
        assert data["ruff_config"] == {"line-length": 100}
        assert data["exclusions"] == ["*.pyc"]
        assert data["google_style_guide"] is True
        assert data["auto_fix_enabled"] is True
        assert data["backup_enabled"] is True
        assert data["dry_run"] is False

    def test_config_from_dict(self) -> None:
        """Test Config deserialization from dictionary."""
        data = {
            "project_path": "/project",
            "pyright_config": {"typeCheckingMode": "standard"},
            "ruff_config": {"line-length": 100},
            "exclusions": ["*.pyc"],
            "google_style_guide": True,
            "auto_fix_enabled": True,
            "backup_enabled": True,
            "dry_run": False,
        }
        config = modules.core.models.Config.from_dict(data)
        assert config.project_path == "/project"
        assert config.pyright_config == {"typeCheckingMode": "standard"}
        assert config.ruff_config == {"line-length": 100}
        assert config.exclusions == ["*.pyc"]
        assert config.google_style_guide is True
        assert config.auto_fix_enabled is True
        assert config.backup_enabled is True
        assert config.dry_run is False

    def test_config_round_trip(self) -> None:
        """Test Config serialization round-trip."""
        original = modules.core.models.Config(
            project_path="/project",
            pyright_config={"typeCheckingMode": "standard"},
            ruff_config={"line-length": 100},
            exclusions=["*.pyc", "__pycache__"],
            google_style_guide=True,
            auto_fix_enabled=True,
            backup_enabled=True,
            dry_run=False,
        )
        data = original.to_dict()
        restored = modules.core.models.Config.from_dict(data)
        assert restored.project_path == original.project_path
        assert restored.pyright_config == original.pyright_config
        assert restored.ruff_config == original.ruff_config
        assert restored.exclusions == original.exclusions
        assert restored.google_style_guide == original.google_style_guide
        assert restored.auto_fix_enabled == original.auto_fix_enabled
        assert restored.backup_enabled == original.backup_enabled
        assert restored.dry_run == original.dry_run
