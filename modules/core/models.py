"""Data models for the Python Code Analyzer.

This module defines the core data structures used throughout the analyzer:
- Issue: Represents a single code issue found during analysis
- Fix: Represents a fix that can be applied to resolve an issue
- Report: Represents the complete analysis results
- ReportSummary: Summary statistics for a report
- Config: Configuration settings for the analyzer
"""

import dataclasses
import datetime
import enum


class Severity(str, enum.Enum):
    """Severity levels for issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IssueCategory(str, enum.Enum):
    """Categories for issues."""

    TYPE_ERROR = "type-error"
    STYLE_VIOLATION = "style-violation"
    IMPORT_ISSUE = "import-issue"


@dataclasses.dataclass
class Issue:
    """Represents a single code issue found during analysis.

    Attributes:
        file_path: Path to the file containing the issue
        line: Line number where the issue occurs (1-indexed)
        column: Column number where the issue occurs (1-indexed)
        severity: Severity level of the issue (error, warning, info)
        category: Category of the issue (type-error, style-violation, import-issue)
        code: Issue code identifier (e.g., E501, W291)
        message: Human-readable description of the issue
        suggestion: Optional suggested fix or improvement
        source: Source of the issue (pyright, ruff)
    """

    file_path: str
    line: int
    column: int
    severity: Severity
    category: IssueCategory
    code: str
    message: str
    suggestion: str | None = None
    source: str = ""

    def __post_init__(self) -> None:
        """Validate Issue fields after initialization."""
        if self.line < 1:
            raise ValueError("Line number must be >= 1")
        if self.column < 1:
            raise ValueError("Column number must be >= 1")
        if not self.file_path:
            raise ValueError("file_path cannot be empty")
        if not self.code:
            raise ValueError("code cannot be empty")
        if not self.message:
            raise ValueError("message cannot be empty")
        if self.source not in ("pyright", "ruff"):
            raise ValueError("source must be 'pyright' or 'ruff'")

    def to_dict(self) -> dict[str, object]:
        """Convert Issue to dictionary.

        Returns:
            Dictionary representation of the Issue
        """
        return {
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "severity": self.severity.value,
            "category": self.category.value,
            "code": self.code,
            "message": self.message,
            "suggestion": self.suggestion,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Issue":
        """Create Issue from dictionary.

        Args:
            data: Dictionary containing Issue data

        Returns:
            Issue instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        return cls(
            file_path=data["file_path"],
            line=data["line"],
            column=data["column"],
            severity=Severity(data["severity"]),
            category=IssueCategory(data["category"]),
            code=data["code"],
            message=data["message"],
            suggestion=data.get("suggestion"),
            source=data.get("source", ""),
        )


@dataclasses.dataclass
class Fix:
    """Represents a fix that can be applied to resolve an issue.

    Attributes:
        file_path: Path to the file to be fixed
        original_code: Original code before the fix
        fixed_code: Code after applying the fix
        issue: The Issue object this fix addresses
        explanation: Explanation of what the fix does
        safe: Whether the fix is guaranteed to preserve functionality
    """

    file_path: str
    original_code: str
    fixed_code: str
    issue: Issue
    explanation: str
    safe: bool = True

    def __post_init__(self) -> None:
        """Validate Fix fields after initialization."""
        if not self.file_path:
            raise ValueError("file_path cannot be empty")
        if not self.explanation:
            raise ValueError("explanation cannot be empty")
        if self.original_code == self.fixed_code:
            raise ValueError("original_code and fixed_code cannot be identical")

    def to_dict(self) -> dict[str, object]:
        """Convert Fix to dictionary.

        Returns:
            Dictionary representation of the Fix
        """
        return {
            "file_path": self.file_path,
            "original_code": self.original_code,
            "fixed_code": self.fixed_code,
            "issue": self.issue.to_dict(),
            "explanation": self.explanation,
            "safe": self.safe,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Fix":
        """Create Fix from dictionary.

        Args:
            data: Dictionary containing Fix data

        Returns:
            Fix instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        return cls(
            file_path=data["file_path"],
            original_code=data["original_code"],
            fixed_code=data["fixed_code"],
            issue=Issue.from_dict(data["issue"]),
            explanation=data["explanation"],
            safe=data.get("safe", True),
        )


@dataclasses.dataclass
class ReportSummary:
    """Summary statistics for a report.

    Attributes:
        total_issues: Total number of issues found
        errors: Number of error-level issues
        warnings: Number of warning-level issues
        infos: Number of info-level issues
        by_category: Count of issues by category
        by_file: Count of issues by file
    """

    total_issues: int
    errors: int
    warnings: int
    infos: int
    by_category: dict[str, int] = dataclasses.field(default_factory=dict)
    by_file: dict[str, int] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate ReportSummary fields after initialization."""
        if self.total_issues < 0:
            raise ValueError("total_issues cannot be negative")
        if self.errors < 0:
            raise ValueError("errors cannot be negative")
        if self.warnings < 0:
            raise ValueError("warnings cannot be negative")
        if self.infos < 0:
            raise ValueError("infos cannot be negative")
        if self.errors + self.warnings + self.infos != self.total_issues:
            raise ValueError(
                "Sum of errors, warnings, and infos must equal total_issues"
            )

    def to_dict(self) -> dict[str, object]:
        """Convert ReportSummary to dictionary.

        Returns:
            Dictionary representation of the ReportSummary
        """
        return {
            "total_issues": self.total_issues,
            "errors": self.errors,
            "warnings": self.warnings,
            "infos": self.infos,
            "by_category": self.by_category,
            "by_file": self.by_file,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ReportSummary":
        """Create ReportSummary from dictionary.

        Args:
            data: Dictionary containing ReportSummary data

        Returns:
            ReportSummary instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        return cls(
            total_issues=data["total_issues"],
            errors=data["errors"],
            warnings=data["warnings"],
            infos=data["infos"],
            by_category=data.get("by_category", {}),
            by_file=data.get("by_file", {}),
        )


@dataclasses.dataclass
class Report:
    """Represents the complete analysis results.

    Attributes:
        issues: List of all issues found
        fixes: List of all fixes available
        summary: Summary statistics for the report
        timestamp: When the report was generated
        project_path: Path to the analyzed project
    """

    issues: list[Issue]
    fixes: list[Fix]
    summary: ReportSummary
    timestamp: datetime.datetime
    project_path: str

    def __post_init__(self) -> None:
        """Validate Report fields after initialization."""
        if not self.project_path:
            raise ValueError("project_path cannot be empty")

    def to_dict(self) -> dict[str, object]:
        """Convert Report to dictionary.

        Returns:
            Dictionary representation of the Report
        """
        return {
            "issues": [issue.to_dict() for issue in self.issues],
            "fixes": [fix.to_dict() for fix in self.fixes],
            "summary": self.summary.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "project_path": self.project_path,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Report":
        """Create Report from dictionary.

        Args:
            data: Dictionary containing Report data

        Returns:
            Report instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        return cls(
            issues=[Issue.from_dict(issue) for issue in data.get("issues", [])],
            fixes=[Fix.from_dict(fix) for fix in data.get("fixes", [])],
            summary=ReportSummary.from_dict(data["summary"]),
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
            project_path=data["project_path"],
        )


@dataclasses.dataclass
class Config:
    """Configuration settings for the analyzer.

    Attributes:
        project_path: Path to the project being analyzed
        pyright_config: Pyright-specific configuration options
        ruff_config: Ruff-specific configuration options
        exclusions: List of file/directory patterns to exclude from analysis
        google_style_guide: Whether to enforce Google Style Guide conventions
        auto_fix_enabled: Whether automatic fixes are enabled
        backup_enabled: Whether to create backups before applying fixes
        dry_run: Whether to preview changes without applying them
    """

    project_path: str
    pyright_config: dict[str, object] = dataclasses.field(default_factory=dict)
    ruff_config: dict[str, object] = dataclasses.field(default_factory=dict)
    exclusions: list[str] = dataclasses.field(default_factory=list)
    google_style_guide: bool = True
    auto_fix_enabled: bool = True
    backup_enabled: bool = True
    dry_run: bool = False

    def __post_init__(self) -> None:
        """Validate Config fields after initialization."""
        if not self.project_path:
            raise ValueError("project_path cannot be empty")

    def to_dict(self) -> dict[str, object]:
        """Convert Config to dictionary.

        Returns:
            Dictionary representation of the Config
        """
        return {
            "project_path": self.project_path,
            "pyright_config": self.pyright_config,
            "ruff_config": self.ruff_config,
            "exclusions": self.exclusions,
            "google_style_guide": self.google_style_guide,
            "auto_fix_enabled": self.auto_fix_enabled,
            "backup_enabled": self.backup_enabled,
            "dry_run": self.dry_run,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Config":
        """Create Config from dictionary.

        Args:
            data: Dictionary containing Config data

        Returns:
            Config instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        return cls(
            project_path=data["project_path"],
            pyright_config=data.get("pyright_config", {}),
            ruff_config=data.get("ruff_config", {}),
            exclusions=data.get("exclusions", []),
            google_style_guide=data.get("google_style_guide", True),
            auto_fix_enabled=data.get("auto_fix_enabled", True),
            backup_enabled=data.get("backup_enabled", True),
            dry_run=data.get("dry_run", False),
        )
