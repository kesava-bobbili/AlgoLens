from __future__ import annotations

import ast
import signal
import sys
import traceback
from types import CodeType
from typing import Any, Optional

from app.schemas.visualize import TraceStep, VisualizeRequest, VisualizeResponse

# Restricted builtins for safe educational execution
SAFE_BUILTINS: dict[str, Any] = {
    "True": True,
    "False": False,
    "None": None,
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "print": print,
    "range": range,
    "reversed": reversed,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
}

MAX_STEPS = 200
EXEC_TIMEOUT_SEC = 3


class _ExecutionTracer:
    def __init__(self, source_lines: list[str]) -> None:
        self.source_lines = source_lines
        self.steps: list[TraceStep] = []
        self._step_count = 0
        self._max_depth = 0

    def trace(self, frame, event, arg):  # noqa: ANN001
        if event not in ("line", "call", "return"):
            return self.trace

        filename = frame.f_code.co_filename
        if filename != "<user_code>":
            return self.trace

        if self._step_count >= MAX_STEPS:
            raise TimeoutError("Maximum trace steps exceeded")

        lineno = frame.f_lineno
        if lineno < 1 or lineno > len(self.source_lines):
            line_content = ""
        else:
            line_content = self.source_lines[lineno - 1].rstrip()

        variables = self._capture_locals(frame)
        call_stack = self._build_call_stack(frame)
        depth = len(call_stack)
        self._max_depth = max(self._max_depth, depth)

        self.steps.append(
            TraceStep(
                step=self._step_count,
                line_number=lineno,
                line_content=line_content,
                variables=variables,
                call_stack=call_stack,
                event=event,
            )
        )
        self._step_count += 1
        return self.trace

    def _capture_locals(self, frame) -> dict[str, str]:  # noqa: ANN001
        result: dict[str, str] = {}
        for key, value in frame.f_locals.items():
            if key.startswith("_"):
                continue
            try:
                text = repr(value)
                if len(text) > 120:
                    text = text[:117] + "..."
                result[key] = text
            except Exception:
                result[key] = "<unrepresentable>"
        return result

    def _build_call_stack(self, frame) -> list[str]:  # noqa: ANN001
        stack: list[str] = []
        current = frame
        while current:
            name = current.f_code.co_name
            lineno = current.f_lineno
            stack.append(f"{name}():{lineno}")
            current = current.f_back
        return list(reversed(stack))


def _validate_code(code: str) -> str | None:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return f"Syntax error: {exc}"

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return "Imports are not allowed in visualization mode."
        if isinstance(
            node,
            (
                ast.Global,
                ast.Nonlocal,
                ast.With,
                ast.AsyncWith,
                ast.AsyncFunctionDef,
                ast.ClassDef,
                ast.Lambda,
                ast.Try,
                ast.Raise,
                ast.Delete,
                ast.Yield,
                ast.YieldFrom,
            ),
        ):
            return f"Unsupported construct: {type(node).__name__}"
    return None


def _run_traced(
    code_obj: CodeType,
    globals_dict: dict[str, Any],
    stdin: str,
) -> Optional[str]:
    def _timeout_handler(signum, frame):  # noqa: ANN001
        raise TimeoutError("Execution timed out (3s limit).")

    old_stdin = sys.stdin
    sys.stdin = __import__("io").StringIO(stdin)
    previous_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(EXEC_TIMEOUT_SEC)
    try:
        exec(code_obj, globals_dict)  # noqa: S102
        return None
    except TimeoutError as exc:
        return str(exc)
    except Exception:
        return traceback.format_exc(limit=3)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)
        sys.stdin = old_stdin


class VisualizeService:
    def trace(self, request: VisualizeRequest) -> VisualizeResponse:
        code = request.code.strip()
        source_lines = code.splitlines()

        validation_error = _validate_code(code)
        if validation_error:
            return VisualizeResponse(
                steps=[],
                source_lines=source_lines,
                error=validation_error,
            )

        tracer = _ExecutionTracer(source_lines)
        globals_dict: dict[str, Any] = {
            "__builtins__": SAFE_BUILTINS,
            "__name__": "__main__",
        }

        try:
            compiled = compile(
                code, "<user_code>", "exec", dont_inherit=True
            )
        except SyntaxError as exc:
            return VisualizeResponse(
                steps=[],
                source_lines=source_lines,
                error=str(exc),
            )

        sys.settrace(tracer.trace)
        try:
            runtime_error = _run_traced(compiled, globals_dict, request.stdin)
        finally:
            sys.settrace(None)

        return VisualizeResponse(
            steps=tracer.steps,
            source_lines=source_lines,
            error=runtime_error,
            recursion_depth=tracer._max_depth,
        )
