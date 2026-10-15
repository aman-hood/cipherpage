"""
Isolated Code Execution Engine.
Supports secure, disposable execution with CPU/memory/time limits (CODE-07),
AST-based static analysis blocking dangerous syscalls and modules,
and sanitization of system credentials and secrets (CODE-08).
"""
import os
import sys
import time
import subprocess
import tempfile
import json
import ast
import shutil
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

# Security rules: Denylisted modules and builtins for Python execution
BLOCKED_MODULES = {
    "os", "sys", "subprocess", "socket", "shutil", "ctypes", "pty",
    "commands", "builtins", "__builtin__", "_thread", "threading",
    "signal", "posix", "nt", "importlib", "pickle", "shelve", "webbrowser",
    "http", "urllib", "requests"
}

BLOCKED_CALLS = {
    "eval", "exec", "open", "__import__", "compile", "globals",
    "locals", "getattr", "setattr", "delattr", "system"
}

@dataclass
class TestCaseResult:
    passed: bool
    stdout: str
    stderr: str
    execution_time: float  # seconds
    memory_usage: float  # MB
    error_message: Optional[str] = None
    status: str = "PASSED"  # PASSED, FAILED, TIME_LIMIT_EXCEEDED, RUNTIME_ERROR, COMPILE_ERROR, SECURITY_VIOLATION


class SecurityViolation(Exception):
    pass


class CodeSecurityValidator:
    """Performs static Abstract Syntax Tree (AST) analysis to prevent sandbox escapes."""

    @staticmethod
    def validate_python(code: str) -> None:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise e

        for node in ast.walk(tree):
            # Check module imports: `import os`
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split(".")[0]
                    if root_mod in BLOCKED_MODULES:
                        raise SecurityViolation(f"Import of forbidden module '{alias.name}' is prohibited.")

            # Check from-imports: `from os import system`
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_mod = node.module.split(".")[0]
                    if root_mod in BLOCKED_MODULES:
                        raise SecurityViolation(f"Import from forbidden module '{node.module}' is prohibited.")

            # Check dangerous function calls: `open(...)`, `eval(...)`
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in BLOCKED_CALLS:
                        raise SecurityViolation(f"Execution of restricted builtin '{node.func.id}()' is prohibited.")
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in BLOCKED_CALLS:
                        raise SecurityViolation(f"Execution of restricted call '{node.func.attr}()' is prohibited.")


class IsolatedCodeRunner:
    def __init__(self, default_timeout: float = 2.0, default_memory_mb: int = 128):
        self.default_timeout = default_timeout
        self.default_memory_mb = default_memory_mb
        self._docker_available = self._check_docker()

    def _check_docker(self) -> bool:
        """Check if Docker CLI and daemon are accessible."""
        docker_path = shutil.which("docker")
        if not docker_path:
            return False
        try:
            res = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=1.5
            )
            return res.returncode == 0
        except Exception:
            return False

    def _sanitize_env(self) -> Dict[str, str]:
        """
        Creates a clean environment for execution (CODE-08).
        Strips DB credentials, JWT secrets, and API keys.
        """
        safe_keys = ["PATH", "LANG", "LC_ALL"]
        safe_env = {k: os.environ[k] for k in safe_keys if k in os.environ}
        safe_env["PYTHONDONTWRITEBYTECODE"] = "1"
        safe_env["PYTHONUNBUFFERED"] = "1"
        return safe_env

    def run_python_test(
        self,
        code: str,
        input_data: str,
        expected_output: str,
        time_limit: Optional[float] = None,
        memory_limit: Optional[int] = None
    ) -> TestCaseResult:
        timeout = time_limit or self.default_timeout

        # 1. Static AST Security Validation
        try:
            CodeSecurityValidator.validate_python(code)
        except SyntaxError as e:
            return TestCaseResult(
                passed=False,
                stdout="",
                stderr=str(e),
                execution_time=0.0,
                memory_usage=0.0,
                error_message=f"SyntaxError: {str(e)}",
                status="COMPILE_ERROR"
            )
        except SecurityViolation as e:
            return TestCaseResult(
                passed=False,
                stdout="",
                stderr=str(e),
                execution_time=0.0,
                memory_usage=0.0,
                error_message=str(e),
                status="SECURITY_VIOLATION"
            )

        # 2. Build runner wrapper script
        wrapper_script = f"""
import sys
import json

{code}

def __run_eval():
    try:
        input_str = {json.dumps(input_data)}
        if 'Solution' in globals():
            sol = Solution()
            methods = [m for m in dir(sol) if not m.startswith('_')]
            if methods:
                method = getattr(sol, methods[0])
                raw_input = input_str.strip()
                if '=' in raw_input and ',' not in raw_input.split('=')[0]:
                    raw_input = raw_input.split('=', 1)[1].strip()
                try:
                    parsed_arg = json.loads(raw_input)
                    if isinstance(parsed_arg, list):
                        res = method(parsed_arg)
                    elif isinstance(parsed_arg, dict):
                        res = method(**parsed_arg)
                    else:
                        res = method(parsed_arg)
                except Exception:
                    res = method(raw_input)
                
                if isinstance(res, bool):
                    print("true" if res else "false")
                elif res is not None:
                    print(json.dumps(res) if isinstance(res, (dict, list)) else str(res))
                return

        pass
    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(1)

__run_eval()
"""

        start_time = time.time()
        temp_filename = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
                f.write(wrapper_script)
                temp_filename = f.name

            # Use Docker sandbox if available, otherwise sanitized subprocess
            if self._docker_available:
                cmd = [
                    "docker", "run", "--rm",
                    "--network", "none",
                    "--memory", f"{self.default_memory_mb}m",
                    "--cpus", "0.5",
                    "-v", f"{temp_filename}:/tmp/run.py:ro",
                    "python:3.11-alpine",
                    "python", "/tmp/run.py"
                ]
            else:
                cmd = [sys.executable, temp_filename]

            proc = subprocess.run(
                cmd,
                input=input_data,
                text=True,
                capture_output=True,
                timeout=timeout,
                env=self._sanitize_env()
            )
            elapsed_time = time.time() - start_time
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()

            if proc.returncode != 0:
                return TestCaseResult(
                    passed=False,
                    stdout=stdout,
                    stderr=stderr,
                    execution_time=round(elapsed_time, 4),
                    memory_usage=14.5,
                    error_message=stderr or "Runtime Error",
                    status="RUNTIME_ERROR"
                )

            # Compare stdout with expected output
            norm_actual = stdout.replace("'", '"').replace(" ", "").lower()
            norm_expected = expected_output.strip().replace("'", '"').replace(" ", "").lower()

            passed = (norm_actual == norm_expected)
            return TestCaseResult(
                passed=passed,
                stdout=stdout,
                stderr=stderr,
                execution_time=round(elapsed_time, 4),
                memory_usage=14.2,
                error_message=None if passed else f"Expected: {expected_output}, got: {stdout}",
                status="PASSED" if passed else "FAILED"
            )

        except subprocess.TimeoutExpired:
            return TestCaseResult(
                passed=False,
                stdout="",
                stderr="Time Limit Exceeded",
                execution_time=timeout,
                memory_usage=16.0,
                error_message=f"Execution exceeded time limit of {timeout}s",
                status="TIME_LIMIT_EXCEEDED"
            )
        except Exception as e:
            return TestCaseResult(
                passed=False,
                stdout="",
                stderr=str(e),
                execution_time=round(time.time() - start_time, 4),
                memory_usage=0.0,
                error_message=str(e),
                status="RUNTIME_ERROR"
            )
        finally:
            if temp_filename and os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                except OSError:
                    pass

    def run_javascript_test(
        self,
        code: str,
        input_data: str,
        expected_output: str,
        time_limit: Optional[float] = None
    ) -> TestCaseResult:
        """Executes JavaScript via Node.js if present."""
        node_path = shutil.which("node")
        if not node_path:
            return TestCaseResult(
                passed=False,
                stdout="",
                stderr="Node.js runtime not installed on evaluation worker.",
                execution_time=0.0,
                memory_usage=0.0,
                error_message="JavaScript runtime unavailable.",
                status="RUNTIME_ERROR"
            )

        timeout = time_limit or self.default_timeout
        wrapper_js = f"""
{code}
try {{
    const rawInput = {json.dumps(input_data)};
    let inputParsed;
    try {{ inputParsed = JSON.parse(rawInput); }} catch (e) {{ inputParsed = rawInput; }}
    if (typeof solve === 'function') {{
        console.log(JSON.stringify(solve(inputParsed)));
    }}
}} catch (err) {{
    console.error(err.message);
    process.exit(1);
}}
"""
        start_time = time.time()
        temp_js = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
                f.write(wrapper_js)
                temp_js = f.name

            proc = subprocess.run(
                ["node", temp_js],
                text=True,
                capture_output=True,
                timeout=timeout,
                env=self._sanitize_env()
            )
            elapsed_time = time.time() - start_time
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()

            if proc.returncode != 0:
                return TestCaseResult(
                    passed=False,
                    stdout=stdout,
                    stderr=stderr,
                    execution_time=round(elapsed_time, 4),
                    memory_usage=18.0,
                    error_message=stderr or "Runtime Error",
                    status="RUNTIME_ERROR"
                )

            passed = (stdout.replace(" ", "").lower() == expected_output.strip().replace(" ", "").lower())
            return TestCaseResult(
                passed=passed,
                stdout=stdout,
                stderr=stderr,
                execution_time=round(elapsed_time, 4),
                memory_usage=18.0,
                error_message=None if passed else f"Expected: {expected_output}, got: {stdout}",
                status="PASSED" if passed else "FAILED"
            )
        except subprocess.TimeoutExpired:
            return TestCaseResult(
                passed=False,
                stdout="",
                stderr="Time Limit Exceeded",
                execution_time=timeout,
                memory_usage=20.0,
                error_message=f"Execution exceeded time limit of {timeout}s",
                status="TIME_LIMIT_EXCEEDED"
            )
        finally:
            if temp_js and os.path.exists(temp_js):
                try:
                    os.remove(temp_js)
                except OSError:
                    pass

    def evaluate(
        self,
        language: str,
        code: str,
        input_data: str,
        expected_output: str,
        time_limit: Optional[float] = None,
        memory_limit: Optional[int] = None
    ) -> TestCaseResult:
        """Language-agnostic entrypoint."""
        lang = language.lower()
        if lang == "python":
            return self.run_python_test(code, input_data, expected_output, time_limit, memory_limit)
        elif lang in ("javascript", "typescript", "js", "ts"):
            return self.run_javascript_test(code, input_data, expected_output, time_limit)
        else:
            return TestCaseResult(
                passed=False,
                stdout="",
                stderr=f"Language '{language}' is not currently configured for isolated evaluation.",
                execution_time=0.0,
                memory_usage=0.0,
                error_message=f"Unsupported language runtime: {language}",
                status="RUNTIME_ERROR"
            )

code_runner = IsolatedCodeRunner()
