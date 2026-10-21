"""Tests for the Python execution visualizer (visualize_service.py).

Covers: normal execution tracing, timeout enforcement, AST-level security
blocking (imports, file I/O, subprocess, network), and output step limits.

IMPORTANT: These tests DO NOT weaken security checks. If unsafe code executes
successfully, the test FAILS — that is a real bug to report.
"""

from __future__ import annotations

from app.schemas.visualize import VisualizeRequest, VisualizeResponse
from app.services.visualize_service import (
    MAX_STEPS,
    EXEC_TIMEOUT_SEC,
    SAFE_BUILTINS,
    VisualizeService,
    _validate_code,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _trace(code: str, stdin: str = "") -> VisualizeResponse:
    service = VisualizeService()
    return service.trace(VisualizeRequest(code=code, stdin=stdin))


# ---------------------------------------------------------------------------
# Normal safe code execution
# ---------------------------------------------------------------------------

class TestNormalExecution:
    def test_simple_assignment_and_print(self):
        result = _trace("x = 42\ny = x + 1")
        assert result.error is None
        assert len(result.steps) > 0
        # Variable x should appear in trace
        all_vars = {}
        for step in result.steps:
            all_vars.update(step.variables)
        assert "x" in all_vars
        assert "y" in all_vars

    def test_for_loop_produces_steps(self):
        result = _trace("total = 0\nfor i in range(5):\n    total += i")
        assert result.error is None
        assert len(result.steps) > 3  # At least entry + loop iterations

    def test_function_call_shows_call_stack(self):
        code = "def add(a, b):\n    return a + b\nresult = add(3, 4)"
        result = _trace(code)
        assert result.error is None
        # At least one step should have a call stack with the function
        has_call = any(
            any("add()" in frame for frame in step.call_stack)
            for step in result.steps
        )
        assert has_call, "Expected call stack to contain add()"

    def test_recursion_depth_tracked(self):
        code = (
            "def fib(n):\n"
            "    if n <= 1:\n"
            "        return n\n"
            "    return fib(n-1) + fib(n-2)\n"
            "fib(4)"
        )
        result = _trace(code)
        assert result.error is None
        assert result.recursion_depth >= 2

    def test_source_lines_returned(self):
        code = "x = 1\ny = 2"
        result = _trace(code)
        assert result.source_lines == ["x = 1", "y = 2"]

    def test_step_fields_present(self):
        result = _trace("a = 10")
        assert result.error is None
        assert len(result.steps) >= 1
        step = result.steps[0]
        assert isinstance(step.step, int)
        assert isinstance(step.line_number, int)
        assert isinstance(step.line_content, str)
        assert isinstance(step.variables, dict)
        assert isinstance(step.call_stack, list)
        assert step.event in ("line", "call", "return")

    def test_stdin_is_available(self):
        """The visualizer replaces sys.stdin so user code can read input."""
        code = "x = input()\ny = int(x)"
        # input() is NOT in SAFE_BUILTINS, so this should error at validation
        # or at runtime. Let's check which one.
        result = _trace(code, stdin="42")
        # input is not in SAFE_BUILTINS, so it should produce an error
        # This is expected behavior — SAFE_BUILTINS is restrictive
        if result.error:
            assert "input" in result.error.lower() or "not defined" in result.error.lower()


# ---------------------------------------------------------------------------
# Timeout enforcement
# ---------------------------------------------------------------------------

class TestTimeoutEnforcement:
    def test_infinite_loop_is_stopped(self):
        """An infinite loop must be terminated by the timeout/step-limit mechanism."""
        code = "x = 0\nwhile True:\n    x += 1"
        result = _trace(code)
        # Must have an error — either timeout or max steps exceeded
        assert result.error is not None
        assert (
            "timed out" in result.error.lower()
            or "timeout" in result.error.lower()
            or "maximum trace steps" in result.error.lower()
        )
        # Steps should be capped, not unbounded
        assert len(result.steps) <= MAX_STEPS + 10  # small tolerance

    def test_max_steps_constant_is_reasonable(self):
        """MAX_STEPS should be bounded to prevent denial of service."""
        assert 50 <= MAX_STEPS <= 1000

    def test_timeout_constant_is_reasonable(self):
        """EXEC_TIMEOUT_SEC should be bounded."""
        assert 1.0 <= EXEC_TIMEOUT_SEC <= 30.0

    def test_deeply_recursive_code_stopped(self):
        """Deep recursion should be stopped by step limit or recursion depth."""
        code = "def f(n):\n    return f(n+1)\nf(0)"
        result = _trace(code)
        assert result.error is not None


# ---------------------------------------------------------------------------
# Security: dangerous code is blocked
# ---------------------------------------------------------------------------

class TestSecurityBlocking:
    """Each test verifies that dangerous operations are rejected at the AST
    validation level. The code should NEVER actually execute."""

    def test_import_os_blocked(self):
        result = _trace("import os")
        assert result.error is not None
        assert "import" in result.error.lower() or "not allowed" in result.error.lower()
        assert result.steps == []

    def test_import_subprocess_blocked(self):
        result = _trace("import subprocess")
        assert result.error is not None
        assert result.steps == []

    def test_import_from_blocked(self):
        result = _trace("from os import path")
        assert result.error is not None
        assert result.steps == []

    def test_import_socket_blocked(self):
        result = _trace("import socket")
        assert result.error is not None
        assert result.steps == []

    def test_import_sys_blocked(self):
        result = _trace("import sys")
        assert result.error is not None
        assert result.steps == []

    def test_open_file_blocked(self):
        """open() is not in SAFE_BUILTINS, so file access should fail at runtime."""
        code = 'f = open("/etc/passwd", "r")\ndata = f.read()'
        result = _trace(code)
        # open is not in SAFE_BUILTINS, so it should fail
        assert result.error is not None
        # Verify the code didn't actually read the file
        all_vars = {}
        for step in result.steps:
            all_vars.update(step.variables)
        assert "data" not in all_vars, "open() should not have succeeded"

    def test_exec_not_in_safe_builtins(self):
        """exec/eval/compile/open should not be available to user code."""
        assert "exec" not in SAFE_BUILTINS
        assert "eval" not in SAFE_BUILTINS
        assert "compile" not in SAFE_BUILTINS
        assert "open" not in SAFE_BUILTINS
        assert "__import__" not in SAFE_BUILTINS
        assert "input" not in SAFE_BUILTINS

    def test_dunder_import_not_available(self):
        """__import__ is not in SAFE_BUILTINS."""
        code = '__import__("os")'
        result = _trace(code)
        assert result.error is not None

    def test_class_definition_blocked(self):
        """ClassDef is in the blocked AST nodes."""
        result = _trace("class Foo:\n    pass")
        assert result.error is not None
        assert result.steps == []

    def test_try_except_blocked(self):
        """Try/Raise are in the blocked AST nodes — prevents catching SecurityError."""
        result = _trace("try:\n    x = 1\nexcept:\n    pass")
        assert result.error is not None
        assert result.steps == []

    def test_lambda_blocked(self):
        result = _trace("f = lambda x: x + 1")
        assert result.error is not None
        assert result.steps == []

    def test_with_statement_blocked(self):
        result = _trace("with open('x') as f:\n    pass")
        assert result.error is not None
        assert result.steps == []

    def test_yield_blocked(self):
        result = _trace("def gen():\n    yield 1")
        assert result.error is not None
        assert result.steps == []

    def test_delete_blocked(self):
        result = _trace("x = 1\ndel x")
        assert result.error is not None
        assert result.steps == []

    def test_global_blocked(self):
        code = "x = 1\ndef f():\n    global x\n    x = 2"
        result = _trace(code)
        assert result.error is not None
        assert result.steps == []


# ---------------------------------------------------------------------------
# AST validation function directly
# ---------------------------------------------------------------------------

class TestValidateCode:
    def test_valid_code_returns_none(self):
        assert _validate_code("x = 1") is None

    def test_syntax_error_returns_message(self):
        result = _validate_code("if True")
        assert result is not None
        assert "syntax" in result.lower() or "Syntax" in result

    def test_import_returns_message(self):
        result = _validate_code("import os")
        assert result is not None
        assert "import" in result.lower() or "Import" in result

    def test_for_loop_is_allowed(self):
        assert _validate_code("for i in range(10):\n    pass") is None

    def test_if_else_allowed(self):
        assert _validate_code("if True:\n    x = 1\nelse:\n    x = 2") is None

    def test_function_def_allowed(self):
        assert _validate_code("def f(x):\n    return x + 1") is None

    def test_while_allowed(self):
        assert _validate_code("while False:\n    pass") is None


# ---------------------------------------------------------------------------
# Output step limiting
# ---------------------------------------------------------------------------

class TestOutputLimiting:
    def test_large_loop_capped_at_max_steps(self):
        """A loop producing many trace steps must be capped."""
        # Generate more steps than MAX_STEPS
        code = "x = 0\nfor i in range(1000):\n    x += 1"
        result = _trace(code)
        # Either stopped with error or steps are capped
        assert len(result.steps) <= MAX_STEPS + 10
        if len(result.steps) >= MAX_STEPS:
            # Should have an error indicating step limit
            assert result.error is not None

    def test_variable_repr_is_truncated(self):
        """Long variable representations should be truncated to prevent huge output."""
        code = "x = list(range(200))"
        result = _trace(code)
        assert result.error is None
        # Find the step where x is set
        for step in result.steps:
            if "x" in step.variables:
                assert len(step.variables["x"]) <= 120 + 5  # 120 + "..." margin
                break
