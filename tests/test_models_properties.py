"""Property-based tests for core data models.

This module uses hypothesis to test universal properties that should hold
across all valid inputs for the data models.

**Feature: python-code-analyzer, Property 1: Analysis Completeness** (partial - model structure)
**Validates: Requirements 1.3**
"""

import datetime
import hypothesis
import hypothesis.strategies

import modules.core.models


# Strategies for generating valid model instances
severity_strategy = hypothesis.strategies.sampled_from(modules.core.models.Severity)
category_strategy = hypothesis.strategies.sampled_from(modules.core.models.IssueCategory)
# Simple file path strategy that always produces valid paths
file_path_strategy = (
    hypothesis.strategies.just("test.py")
    | hypothesis.strategies.just("src/main.py")
    | hypothesis.strategies.just("./module.py")
)
code_strategy = hypothesis.strategies.text(
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    min_size=1,
    max_size=10,
)
message_strategy = hypothesis.strategies.text(
    alphabet=hypothesis.strategies.characters(blacklist_categories=("Cc", "Cs")),
    min_size=1,
    max_size=100,
)
line_strategy = hypothesis.strategies.integers(min_value=1, max_value=100000)
column_strategy = hypothesis.strategies.integers(min_value=1, max_value=1000)
source_strategy = hypothesis.strategies.sampled_from(["pyright", "ruff"])


@hypothesis.strategies.composite
def issue_strategy(draw):
    """Generate valid Issue instances."""
    return modules.core.models.Issue(
        file_path=draw(file_path_strategy),
        line=draw(line_strategy),
        column=draw(column_strategy),
        severity=draw(severity_strategy),
        category=draw(category_strategy),
        code=draw(code_strategy),
        message=draw(message_strategy),
        suggestion=draw(
            hypothesis.strategies.none() | message_strategy
        ),
        source=draw(source_strategy),
    )


@hypothesis.strategies.composite
def fix_strategy(draw):
    """Generate valid Fix instances."""
    issue = draw(issue_strategy())
    original_code = draw(hypothesis.strategies.text(min_size=1, max_size=50))
    # Ensure fixed_code is different from original_code
    fixed_code = draw(
        hypothesis.strategies.text(min_size=1, max_size=50).filter(
            lambda x: x != original_code
        )
    )
    return modules.core.models.Fix(
        file_path=draw(file_path_strategy),
        original_code=original_code,
        fixed_code=fixed_code,
        issue=issue,
        explanation=draw(message_strategy),
        safe=draw(hypothesis.strategies.booleans()),
    )


@hypothesis.strategies.composite
def report_summary_strategy(draw):
    """Generate valid ReportSummary instances."""
    errors = draw(hypothesis.strategies.integers(min_value=0, max_value=100))
    warnings = draw(hypothesis.strategies.integers(min_value=0, max_value=100))
    infos = draw(hypothesis.strategies.integers(min_value=0, max_value=100))
    total = errors + warnings + infos
    return modules.core.models.ReportSummary(
        total_issues=total,
        errors=errors,
        warnings=warnings,
        infos=infos,
        by_category={},
        by_file={},
    )


@hypothesis.strategies.composite
def config_strategy(draw):
    """Generate valid Config instances."""
    return modules.core.models.Config(
        project_path=draw(file_path_strategy),
        pyright_config=draw(
            hypothesis.strategies.dictionaries(
                hypothesis.strategies.text(
                    min_size=1,
                    max_size=20,
                    alphabet=hypothesis.strategies.characters(
                        blacklist_categories=("Cc", "Cs")
                    ),
                ),
                hypothesis.strategies.text(max_size=50),
                max_size=5,
            )
        ),
        ruff_config=draw(
            hypothesis.strategies.dictionaries(
                hypothesis.strategies.text(
                    min_size=1,
                    max_size=20,
                    alphabet=hypothesis.strategies.characters(
                        blacklist_categories=("Cc", "Cs")
                    ),
                ),
                hypothesis.strategies.text(max_size=50),
                max_size=5,
            )
        ),
        exclusions=draw(
            hypothesis.strategies.lists(
                hypothesis.strategies.text(min_size=1, max_size=20), max_size=5
            )
        ),
        google_style_guide=draw(hypothesis.strategies.booleans()),
        auto_fix_enabled=draw(hypothesis.strategies.booleans()),
        backup_enabled=draw(hypothesis.strategies.booleans()),
        dry_run=draw(hypothesis.strategies.booleans()),
    )


class TestIssueRoundTrip:
    """Property-based tests for Issue serialization round-trip."""

    @hypothesis.given(issue_strategy())
    def test_issue_serialization_round_trip(
        self, issue: modules.core.models.Issue
    ) -> None:
        """Property: Issue serialization round-trip preserves all data.

        For any valid Issue, serializing to dict and deserializing should
        produce an equivalent Issue with identical field values.

        **Feature: python-code-analyzer, Property 1: Analysis Completeness** (partial - model structure)
        **Validates: Requirements 1.3**
        """
        # Serialize to dict
        data = issue.to_dict()

        # Deserialize back
        restored = modules.core.models.Issue.from_dict(data)

        # Verify all fields match
        assert restored.file_path == issue.file_path
        assert restored.line == issue.line
        assert restored.column == issue.column
        assert restored.severity == issue.severity
        assert restored.category == issue.category
        assert restored.code == issue.code
        assert restored.message == issue.message
        assert restored.suggestion == issue.suggestion
        assert restored.source == issue.source


class TestFixRoundTrip:
    """Property-based tests for Fix serialization round-trip."""

    @hypothesis.given(fix_strategy())
    def test_fix_serialization_round_trip(
        self, fix: modules.core.models.Fix
    ) -> None:
        """Property: Fix serialization round-trip preserves all data.

        For any valid Fix, serializing to dict and deserializing should
        produce an equivalent Fix with identical field values.

        **Feature: python-code-analyzer, Property 1: Analysis Completeness** (partial - model structure)
        **Validates: Requirements 1.3**
        """
        # Serialize to dict
        data = fix.to_dict()

        # Deserialize back
        restored = modules.core.models.Fix.from_dict(data)

        # Verify all fields match
        assert restored.file_path == fix.file_path
        assert restored.original_code == fix.original_code
        assert restored.fixed_code == fix.fixed_code
        assert restored.explanation == fix.explanation
        assert restored.safe == fix.safe
        # Verify nested Issue is preserved
        assert restored.issue.file_path == fix.issue.file_path
        assert restored.issue.line == fix.issue.line
        assert restored.issue.column == fix.issue.column


class TestReportSummaryRoundTrip:
    """Property-based tests for ReportSummary serialization round-trip."""

    @hypothesis.given(report_summary_strategy())
    def test_report_summary_serialization_round_trip(
        self, summary: modules.core.models.ReportSummary
    ) -> None:
        """Property: ReportSummary serialization round-trip preserves all data.

        For any valid ReportSummary, serializing to dict and deserializing
        should produce an equivalent ReportSummary with identical field values.

        **Feature: python-code-analyzer, Property 1: Analysis Completeness** (partial - model structure)
        **Validates: Requirements 1.3**
        """
        # Serialize to dict
        data = summary.to_dict()

        # Deserialize back
        restored = modules.core.models.ReportSummary.from_dict(data)

        # Verify all fields match
        assert restored.total_issues == summary.total_issues
        assert restored.errors == summary.errors
        assert restored.warnings == summary.warnings
        assert restored.infos == summary.infos
        assert restored.by_category == summary.by_category
        assert restored.by_file == summary.by_file


class TestConfigRoundTrip:
    """Property-based tests for Config serialization round-trip."""

    @hypothesis.given(config_strategy())
    def test_config_serialization_round_trip(
        self, config: modules.core.models.Config
    ) -> None:
        """Property: Config serialization round-trip preserves all data.

        For any valid Config, serializing to dict and deserializing should
        produce an equivalent Config with identical field values.

        **Feature: python-code-analyzer, Property 1: Analysis Completeness** (partial - model structure)
        **Validates: Requirements 1.3**
        """
        # Serialize to dict
        data = config.to_dict()

        # Deserialize back
        restored = modules.core.models.Config.from_dict(data)

        # Verify all fields match
        assert restored.project_path == config.project_path
        assert restored.pyright_config == config.pyright_config
        assert restored.ruff_config == config.ruff_config
        assert restored.exclusions == config.exclusions
        assert restored.google_style_guide == config.google_style_guide
        assert restored.auto_fix_enabled == config.auto_fix_enabled
        assert restored.backup_enabled == config.backup_enabled
        assert restored.dry_run == config.dry_run
