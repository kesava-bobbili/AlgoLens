"""Tests for the DSA pattern classifier (core/classifier.py).

These test the real keyword-matching logic and complexity map —
no mocking needed since the classifier is pure computation.
"""

from __future__ import annotations

from app.core.classifier import (
    COMPLEXITY_MAP,
    PATTERNS,
    classify_problem,
    get_complexity_hint,
    list_patterns,
)


class TestClassifyProblem:
    def test_dynamic_programming_keywords(self):
        result = classify_problem(
            "Find the maximum sum subsequence with optimal substructure"
        )
        assert result["pattern"] == "Dynamic Programming"
        assert result["confidence"] in ("High", "Medium", "Low")
        assert result["all_matches"]["Dynamic Programming"] >= 2

    def test_sliding_window_detection(self):
        result = classify_problem(
            "Find the maximum sum subarray of size k in a contiguous window"
        )
        assert result["pattern"] == "Sliding Window"

    def test_two_pointers_detection(self):
        result = classify_problem(
            "Given a sorted array, find two numbers that add up to a target sum"
        )
        # Two Pointers or Hashing are both valid — both have overlapping keywords
        assert result["pattern"] in ("Two Pointers", "Hashing")

    def test_binary_search_detection(self):
        result = classify_problem(
            "Search for a target in a rotated sorted array in log n time"
        )
        assert result["pattern"] == "Binary Search"

    def test_graph_bfs_dfs_detection(self):
        result = classify_problem(
            "Find all connected islands in a matrix using bfs traversal"
        )
        assert result["pattern"] == "Graph / BFS / DFS"

    def test_unknown_pattern(self):
        result = classify_problem("Tell me about quantum physics")
        assert result["pattern"] == "General / Unknown"
        assert result["confidence"] == "Low"
        assert result["all_matches"] == {}

    def test_empty_string_returns_unknown(self):
        # Schema enforces min_length=1 but classifier itself should handle empty
        result = classify_problem("")
        assert result["pattern"] == "General / Unknown"

    def test_confidence_high_with_many_keywords(self):
        # Hits multiple DP keywords: maximum, longest, subsequence, optimal
        result = classify_problem(
            "Find the longest subsequence with maximum optimal fibonacci value"
        )
        assert result["confidence"] == "High"

    def test_confidence_low_with_one_keyword(self):
        result = classify_problem("Find the minimum value")
        assert result["confidence"] == "Low"

    def test_all_matches_contains_competing_patterns(self):
        # "sorted array, search" triggers both Binary Search and Two Pointers
        result = classify_problem("search in a sorted array for a pair")
        assert len(result["all_matches"]) >= 2

    def test_case_insensitive(self):
        result = classify_problem("FIND THE MAXIMUM SUBSEQUENCE FIBONACCI")
        assert result["pattern"] == "Dynamic Programming"


class TestGetComplexityHint:
    def test_known_pattern(self):
        hint = get_complexity_hint("Dynamic Programming")
        assert "time" in hint
        assert "space" in hint
        assert hint["time"] == "O(n²) or O(n)"

    def test_sliding_window_complexity(self):
        hint = get_complexity_hint("Sliding Window")
        assert hint["time"] == "O(n)"
        assert hint["space"] == "O(1)"

    def test_unknown_pattern_returns_default(self):
        hint = get_complexity_hint("Nonexistent Pattern")
        assert hint["time"] == "O(n)"
        assert hint["space"] == "O(n)"

    def test_all_patterns_have_complexity(self):
        for pattern in PATTERNS:
            hint = get_complexity_hint(pattern)
            assert "time" in hint and "space" in hint


class TestListPatterns:
    def test_returns_all_pattern_names(self):
        patterns = list_patterns()
        assert len(patterns) == len(PATTERNS)
        assert "Dynamic Programming" in patterns
        assert "Sliding Window" in patterns

    def test_returns_list_of_strings(self):
        patterns = list_patterns()
        assert all(isinstance(p, str) for p in patterns)
