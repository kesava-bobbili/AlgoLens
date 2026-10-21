"""Tests for GitHub URL parsing and validation (github_service.py).

These test the pure URL-parsing logic without making any real HTTP requests.
"""

from __future__ import annotations

import pytest

from app.services.github_service import (
    _normalize_github_url,
    _parse_repo_url,
    _format_languages,
)


class TestNormalizeGitHubUrl:
    def test_full_https_url(self):
        result = _normalize_github_url("https://github.com/owner/repo")
        assert result == "https://github.com/owner/repo"

    def test_adds_https_prefix(self):
        result = _normalize_github_url("github.com/owner/repo")
        assert result == "https://github.com/owner/repo"

    def test_strips_whitespace(self):
        result = _normalize_github_url("  https://github.com/owner/repo  ")
        assert result == "https://github.com/owner/repo"

    def test_empty_url_raises(self):
        with pytest.raises(ValueError, match="empty"):
            _normalize_github_url("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="empty"):
            _normalize_github_url("   ")


class TestParseRepoUrl:
    def test_standard_url(self):
        owner, repo = _parse_repo_url("https://github.com/facebook/react")
        assert owner == "facebook"
        assert repo == "react"

    def test_url_with_git_suffix(self):
        owner, repo = _parse_repo_url("https://github.com/owner/repo.git")
        assert owner == "owner"
        assert repo == "repo"

    def test_url_with_trailing_slash(self):
        owner, repo = _parse_repo_url("https://github.com/owner/repo/")
        assert owner == "owner"
        assert repo == "repo"

    def test_url_with_extra_path(self):
        # URLs like github.com/owner/repo/tree/main should still parse owner/repo
        owner, repo = _parse_repo_url(
            "https://github.com/owner/repo/tree/main"
        )
        assert owner == "owner"
        assert repo == "repo"

    def test_www_prefix_accepted(self):
        owner, repo = _parse_repo_url("https://www.github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_non_github_host_rejected(self):
        with pytest.raises(ValueError, match="github.com"):
            _parse_repo_url("https://gitlab.com/owner/repo")

    def test_missing_repo_name_rejected(self):
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            _parse_repo_url("https://github.com/owner")

    def test_bare_domain_rejected(self):
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            _parse_repo_url("https://github.com/")

    def test_http_protocol_accepted(self):
        owner, repo = _parse_repo_url("http://github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_owner_with_hyphens(self):
        owner, repo = _parse_repo_url("https://github.com/my-org/my-repo")
        assert owner == "my-org"
        assert repo == "my-repo"

    def test_owner_with_dots(self):
        owner, repo = _parse_repo_url("https://github.com/my.org/repo.js")
        assert owner == "my.org"
        assert repo == "repo.js"


class TestFormatLanguages:
    def test_formats_languages(self):
        langs = {"Python": 50000, "JavaScript": 30000, "CSS": 5000}
        result = _format_languages(langs)
        assert "Python" in result
        assert "JavaScript" in result
        assert "bytes" in result

    def test_empty_languages(self):
        result = _format_languages({})
        assert "None" in result

    def test_sorted_by_bytes_descending(self):
        langs = {"CSS": 100, "Python": 50000, "JS": 30000}
        result = _format_languages(langs)
        lines = result.strip().split("\n")
        assert "Python" in lines[0]
