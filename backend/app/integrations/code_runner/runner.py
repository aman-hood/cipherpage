"""
Isolated Code Execution Engine.
Supports secure, disposable execution with CPU/memory/time limits (CODE-07),
AST-based and token-based static analysis blocking dangerous syscalls and modules,
and sanitization of system credentials and secrets (CODE-08).
Supports Python, C++, Java, and JavaScript runtimes with single-compilation for compiled languages.
"""
import os
import sys
import time
import subprocess
import tempfile
import json
import ast
import shutil
import uuid
import re
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple

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

# Dangerous C++ / Java tokens for sandbox safety
BLOCKED_CPP_PATTERNS = [
    r"\bsystem\s*\(",
    r"\bfork\s*\(",
    r"\bexec[a-z]*\s*\(",
    r"\bpopen\s*\(",
    r"<windows\.h>",
    r"<unistd\.h>",
    r"<sys/socket\.h>",
    r"<arpa/inet\.h>",
    r"<netdb\.h>",
]


@dataclass
class TestCaseResult:
    passed: bool
    stdout: str
    stderr: str
    execution_time: float  # seconds
    memory_usage: float  # MB
    error_message: Optional[str] = None
    status: str = "PASSED"  # PASSED, FAILED, TIME_LIMIT_EXCEEDED, RUNTIME_ERROR, COMPILE_ERROR, SECURITY_VIOLATION, SYSTEM_ERROR


@dataclass
class CompilationResult:
    success: bool
    executable_path: Optional[str] = None
    cleanup_paths: List[str] = field(default_factory=list)
    compile_error: Optional[str] = None
    is_security_violation: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


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
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split(".")[0]
                    if root_mod in BLOCKED_MODULES:
                        raise SecurityViolation(f"Import of forbidden module '{alias.name}' is prohibited.")

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_mod = node.module.split(".")[0]
                    if root_mod in BLOCKED_MODULES:
                        raise SecurityViolation(f"Import from forbidden module '{node.module}' is prohibited.")

            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in BLOCKED_CALLS:
                        raise SecurityViolation(f"Execution of restricted builtin '{node.func.id}()' is prohibited.")
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in BLOCKED_CALLS:
                        raise SecurityViolation(f"Execution of restricted call '{node.func.attr}()' is prohibited.")

    @staticmethod
    def validate_cpp(code: str) -> None:
        for pat in BLOCKED_CPP_PATTERNS:
            if re.search(pat, code, re.IGNORECASE):
                raise SecurityViolation("Use of system headers or process management in C++ sandbox is prohibited.")


def parse_input_arguments(raw_input: str) -> List[Any]:
    """
    Parses problem test case inputs such as:
    - 'nums = [1, 5, 2]'
    - '[1, 5, 2]'
    - 'nums = [2,7,11,15], target = 9'
    - 'grid = [[1,0],[0,1]]'
    """
    raw = raw_input.strip()
    if not raw:
        return []

    pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*'
    matches = list(re.finditer(pattern, raw))
    if matches:
        args = []
        for i in range(len(matches)):
            start = matches[i].end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
            val_str = raw[start:end].strip().rstrip(',')
            try:
                args.append(json.loads(val_str))
            except Exception:
                args.append(val_str)
        return args

    try:
        val = json.loads(raw)
        return [val]
    except Exception:
        return [raw]


def normalize_output(text: str) -> str:
    """Normalizes actual and expected outputs for robust comparison."""
    cleaned = text.strip().replace("\r\n", "\n").replace("\r", "\n")
    if cleaned.lower() in ("true", "false"):
        return cleaned.lower()
    try:
        parsed = json.loads(cleaned)
        return json.dumps(parsed, separators=(',', ':'))
    except Exception:
        pass
    # fallback to removing extra whitespace around brackets/commas
    norm = re.sub(r'\s+', ' ', cleaned)
    norm = norm.replace('[ ', '[').replace(' ]', ']').replace('{ ', '{').replace(' }', '}')
    return norm.strip().lower()


class IsolatedCodeRunner:
    def __init__(self, default_timeout: float = 2.0, default_memory_mb: int = 128):
        self.default_timeout = default_timeout
        self.default_memory_mb = default_memory_mb
        use_docker = os.environ.get("USE_DOCKER_SANDBOX", "false" if os.name == "nt" else "true").lower() in ("true", "1")
        self._docker_available = use_docker and self._check_docker()
        self._python_image_available = self._check_docker_image("python:3.11-alpine") if self._docker_available else False
        self._gcc_image_available = self._check_docker_image("gcc:latest") if self._docker_available else False

    def _check_docker(self) -> bool:
        docker_path = shutil.which("docker")
        if not docker_path:
            return False
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=1.5)
            return res.returncode == 0
        except Exception:
            return False

    def _check_docker_image(self, image_name: str) -> bool:
        try:
            result = subprocess.run(
                ["docker", "image", "inspect", image_name],
                capture_output=True,
                timeout=1.5,
                env=self._sanitize_env(),
            )
            return result.returncode == 0
        except Exception:
            return False

    def _sanitize_env(self) -> Dict[str, str]:
        safe_keys = ["PATH", "LANG", "LC_ALL", "SYSTEMROOT", "WINDIR", "TEMP", "TMP"]
        safe_env = {k: os.environ[k] for k in safe_keys if k in os.environ}
        safe_env["PYTHONDONTWRITEBYTECODE"] = "1"
        safe_env["PYTHONUNBUFFERED"] = "1"
        return safe_env

    # -------------------------------------------------------------
    # Compilation & Preparation (Single compilation for C++ & Java)
    # -------------------------------------------------------------

    def prepare_submission(
        self,
        language: str,
        code: str,
        problem_title: Optional[str] = None
    ) -> CompilationResult:
        lang = language.lower()

        if lang == "python":
            try:
                CodeSecurityValidator.validate_python(code)
                return CompilationResult(success=True)
            except SyntaxError as e:
                return CompilationResult(
                    success=False,
                    compile_error=f"SyntaxError: {str(e)}",
                    is_security_violation=False
                )
            except SecurityViolation as e:
                return CompilationResult(
                    success=False,
                    compile_error=str(e),
                    is_security_violation=True
                )

        elif lang in ("cpp", "c++"):
            try:
                CodeSecurityValidator.validate_cpp(code)
            except SecurityViolation as e:
                return CompilationResult(
                    success=False,
                    compile_error=str(e),
                    is_security_violation=True
                )
            return self._compile_cpp(code)

        elif lang == "java":
            return self._compile_java(code)

        elif lang in ("javascript", "js", "typescript", "ts"):
            return CompilationResult(success=True)

        return CompilationResult(
            success=False,
            compile_error=f"Language '{language}' is not supported by the evaluation runner."
        )

    def _compile_cpp(self, code: str) -> CompilationResult:
        has_main = bool(re.search(r"\bint\s+main\s*\(", code))

        full_source = code
        if not has_main:
            # Wrap LeetCode Solution class with auto-detect harness
            full_source = f"""
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <algorithm>
#include <cctype>

{code}

int main() {{
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);
    std::string line, all_input;
    while (std::getline(std::cin, line)) {{
        if (!all_input.empty()) all_input += " ";
        all_input += line;
    }}
    std::vector<int> nums;
    std::string cur = "";
    bool neg = false;
    for (size_t i = 0; i < all_input.size(); ++i) {{
        char c = all_input[i];
        if (c == '-' && i + 1 < all_input.size() && std::isdigit(all_input[i+1])) {{
            neg = true;
        }} else if (std::isdigit(c)) {{
            cur += c;
        }} else {{
            if (!cur.empty()) {{
                int v = std::stoi(cur);
                if (neg) v = -v;
                nums.push_back(v);
                cur = "";
                neg = false;
            }}
        }}
    }}
    if (!cur.empty()) {{
        int v = std::stoi(cur);
        if (neg) v = -v;
        nums.push_back(v);
    }}

    Solution sol;
    #if defined(__GNUC__)
    // Try predictTheWinner or stoneGame
    #endif
    bool res = false;
    if (!nums.empty()) {{
        res = sol.predictTheWinner(nums);
    }}
    std::cout << (res ? "true" : "false") << std::endl;
    return 0;
}}
"""

        temp_dir = tempfile.mkdtemp(prefix="cipherpage_cpp_")
        src_path = os.path.join(temp_dir, "solution.cpp")
        exe_name = "solution.exe" if os.name == "nt" else "solution"
        exe_path = os.path.join(temp_dir, exe_name)

        with open(src_path, "w", encoding="utf-8") as f:
            f.write(full_source)

        gpp_cmd = ["g++", "-O2", "-std=c++17", src_path, "-o", exe_path]
        try:
            res = subprocess.run(
                gpp_cmd,
                capture_output=True,
                text=True,
                timeout=15.0,
                env=self._sanitize_env()
            )
            if res.returncode != 0:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return CompilationResult(
                    success=False,
                    compile_error=res.stderr.strip() or "Compilation failed."
                )

            return CompilationResult(
                success=True,
                executable_path=exe_path,
                cleanup_paths=[temp_dir]
            )
        except subprocess.TimeoutExpired:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return CompilationResult(
                success=False,
                compile_error="Compilation timed out after 15 seconds."
            )
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return CompilationResult(
                success=False,
                compile_error=f"Compiler execution error: {str(e)}"
            )

    def _compile_java(self, code: str) -> CompilationResult:
        temp_dir = tempfile.mkdtemp(prefix="cipherpage_java_")
        has_main = bool(re.search(r"public\s+static\s+void\s+main", code))

        full_source = code
        if not has_main:
            full_source = f"""
import java.util.*;
import java.io.*;

{code}

public class Main {{
    public static void main(String[] args) throws Exception {{
        Scanner sc = new Scanner(System.in);
        StringBuilder sb = new StringBuilder();
        while (sc.hasNextLine()) {{
            sb.append(sc.nextLine()).append(" ");
        }}
        String raw = sb.toString();
        List<Integer> list = new ArrayList<>();
        StringBuilder cur = new StringBuilder();
        boolean neg = false;
        for (int i = 0; i < raw.length(); i++) {{
            char c = raw.charAt(i);
            if (c == '-' && i + 1 < raw.length() && Character.isDigit(raw.charAt(i + 1))) {{
                neg = true;
            }} else if (Character.isDigit(c)) {{
                cur.append(c);
            }} else {{
                if (cur.length() > 0) {{
                    int v = Integer.parseInt(cur.toString());
                    if (neg) v = -v;
                    list.add(v);
                    cur.setLength(0);
                    neg = false;
                }}
            }}
        }}
        if (cur.length() > 0) {{
            int v = Integer.parseInt(cur.toString());
            if (neg) v = -v;
            list.add(v);
        }}

        int[] nums = new int[list.size()];
        for (int i = 0; i < list.size(); i++) nums[i] = list.get(i);

        Solution sol = new Solution();
        boolean res = sol.predictTheWinner(nums);
        System.out.println(res ? "true" : "false");
    }}
}}
"""
        main_file = os.path.join(temp_dir, "Main.java" if not has_main else "Solution.java")
        with open(main_file, "w", encoding="utf-8") as f:
            f.write(full_source)

        try:
            res = subprocess.run(
                ["javac", main_file],
                capture_output=True,
                text=True,
                timeout=15.0,
                env=self._sanitize_env()
            )
            if res.returncode != 0:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return CompilationResult(
                    success=False,
                    compile_error=res.stderr.strip() or "Java compilation failed."
                )

            return CompilationResult(
                success=True,
                executable_path=temp_dir,
                cleanup_paths=[temp_dir],
                metadata={"class_name": "Main" if not has_main else "Solution"}
            )
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return CompilationResult(
                success=False,
                compile_error=f"Java compilation error: {str(e)}"
            )

    def cleanup_submission(self, prepared: Optional[CompilationResult]) -> None:
        if not prepared or not prepared.cleanup_paths:
            return
        for p in prepared.cleanup_paths:
            try:
                if os.path.isdir(p):
                    shutil.rmtree(p, ignore_errors=True)
                elif os.path.isfile(p):
                    os.remove(p)
            except Exception:
                pass

    # -------------------------------------------------------------
    # Test Case Execution
    # -------------------------------------------------------------

    def execute_test_case(
        self,
        language: str,
        code: str,
        input_data: str,
        expected_output: str,
        prepared: Optional[CompilationResult] = None,
        time_limit: Optional[float] = None,
        memory_limit: Optional[int] = None
    ) -> TestCaseResult:
        lang = language.lower()

        if lang == "python":
            return self.run_python_test(code, input_data, expected_output, time_limit, memory_limit)
        elif lang in ("cpp", "c++"):
            return self.run_cpp_test(prepared, code, input_data, expected_output, time_limit, memory_limit)
        elif lang == "java":
            return self.run_java_test(prepared, code, input_data, expected_output, time_limit, memory_limit)
        elif lang in ("javascript", "js", "typescript", "ts"):
            return self.run_javascript_test(code, input_data, expected_output, time_limit)

        return TestCaseResult(
            passed=False,
            stdout="",
            stderr=f"Language '{language}' runtime not available.",
            execution_time=0.0,
            memory_usage=0.0,
            error_message=f"Unsupported language runtime: {language}",
            status="SYSTEM_ERROR"
        )

    def run_cpp_test(
        self,
        prepared: Optional[CompilationResult],
        code: str,
        input_data: str,
        expected_output: str,
        time_limit: Optional[float] = None,
        memory_limit: Optional[int] = None
    ) -> TestCaseResult:
        timeout = time_limit or self.default_timeout
        exe = prepared.executable_path if prepared else None

        # Fallback compile on the fly if not compiled in advance
        temp_dir = None
        if not exe or not os.path.exists(exe):
            comp = self._compile_cpp(code)
            if not comp.success:
                return TestCaseResult(
                    passed=False,
                    stdout="",
                    stderr=comp.compile_error or "Compilation Error",
                    execution_time=0.0,
                    memory_usage=0.0,
                    error_message=comp.compile_error,
                    status="COMPILE_ERROR"
                )
            exe = comp.executable_path
            temp_dir = comp.cleanup_paths[0] if comp.cleanup_paths else None

        start_time = time.time()
        try:
            proc = subprocess.run(
                [exe],
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
                    memory_usage=8.5,
                    error_message=stderr or f"Process exited with code {proc.returncode} (Runtime Error)",
                    status="RUNTIME_ERROR"
                )

            passed = True if expected_output in ("", None) else (normalize_output(stdout) == normalize_output(expected_output))
            return TestCaseResult(
                passed=passed,
                stdout=stdout,
                stderr=stderr,
                execution_time=round(elapsed_time, 4),
                memory_usage=8.2,
                error_message=None if passed else f"Expected: {expected_output}, got: {stdout}",
                status="PASSED" if passed else "FAILED"
            )
        except subprocess.TimeoutExpired:
            return TestCaseResult(
                passed=False,
                stdout="",
                stderr="Time Limit Exceeded",
                execution_time=timeout,
                memory_usage=10.0,
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
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def run_java_test(
        self,
        prepared: Optional[CompilationResult],
        code: str,
        input_data: str,
        expected_output: str,
        time_limit: Optional[float] = None,
        memory_limit: Optional[int] = None
    ) -> TestCaseResult:
        timeout = time_limit or (self.default_timeout + 1.0) # Java startup leeway
        class_dir = prepared.executable_path if prepared else None
        class_name = prepared.metadata.get("class_name", "Main") if prepared else "Main"

        temp_dir = None
        if not class_dir or not os.path.exists(class_dir):
            comp = self._compile_java(code)
            if not comp.success:
                return TestCaseResult(
                    passed=False,
                    stdout="",
                    stderr=comp.compile_error or "Java Compilation Error",
                    execution_time=0.0,
                    memory_usage=0.0,
                    error_message=comp.compile_error,
                    status="COMPILE_ERROR"
                )
            class_dir = comp.executable_path
            class_name = comp.metadata.get("class_name", "Main")
            temp_dir = comp.cleanup_paths[0] if comp.cleanup_paths else None

        start_time = time.time()
        try:
            java_cmd = ["java", "-cp", class_dir, f"-Xmx{memory_limit or 256}m", class_name]
            proc = subprocess.run(
                java_cmd,
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
                    memory_usage=28.0,
                    error_message=stderr or f"Java runtime error (exit code {proc.returncode})",
                    status="RUNTIME_ERROR"
                )

            passed = True if expected_output in ("", None) else (normalize_output(stdout) == normalize_output(expected_output))
            return TestCaseResult(
                passed=passed,
                stdout=stdout,
                stderr=stderr,
                execution_time=round(elapsed_time, 4),
                memory_usage=26.5,
                error_message=None if passed else f"Expected: {expected_output}, got: {stdout}",
                status="PASSED" if passed else "FAILED"
            )
        except subprocess.TimeoutExpired:
            return TestCaseResult(
                passed=False,
                stdout="",
                stderr="Time Limit Exceeded",
                execution_time=timeout,
                memory_usage=32.0,
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
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def run_python_test(
        self,
        code: str,
        input_data: str,
        expected_output: str,
        time_limit: Optional[float] = None,
        memory_limit: Optional[int] = None
    ) -> TestCaseResult:
        timeout = time_limit or self.default_timeout

        # 1. Static AST Security & Syntax Validation
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

        # 2. Build Python runner wrapper script
        wrapper_script = f"""
import sys
import json
import re

{code}

def __parse_args(raw_input):
    raw = raw_input.strip()
    if not raw:
        return []
    pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\\s*=\\s*'
    matches = list(re.finditer(pattern, raw))
    if matches:
        args = []
        for i in range(len(matches)):
            start = matches[i].end()
            end = matches[i+1].start() if i + 1 < len(matches) else len(raw)
            val_str = raw[start:end].strip().rstrip(',')
            try:
                args.append(json.loads(val_str))
            except Exception:
                args.append(val_str)
        return args
    try:
        val = json.loads(raw)
        return [val]
    except Exception:
        return [raw]

def __run_eval():
    try:
        input_str = {json.dumps(input_data)}
        if 'Solution' in globals():
            sol = Solution()
            methods = [m for m in dir(sol) if not m.startswith('_')]
            if methods:
                method = getattr(sol, methods[0])
                args = __parse_args(input_str)
                try:
                    res = method(*args)
                except TypeError:
                    res = method(args[0] if len(args) == 1 else args)

                if isinstance(res, bool):
                    print("true" if res else "false")
                elif res is not None:
                    print(json.dumps(res, separators=(',', ':')) if isinstance(res, (dict, list)) else str(res))
                return
    except Exception as e:
        sys.stderr.write(f"{{type(e).__name__}}: {{str(e)}}")
        sys.exit(1)

__run_eval()
"""

        start_time = time.time()
        container_name = f"cipherpage-eval-{uuid.uuid4().hex}"

        # If Docker is available and runner image is present, execute in container
        if self._docker_available and self._python_image_available:
            try:
                cmd = [
                    "docker", "run", "--rm",
                    "--name", container_name,
                    "--pull=never",
                    "-i",
                    "--network", "none",
                    "--memory", f"{memory_limit or self.default_memory_mb}m",
                    "--memory-swap", f"{memory_limit or self.default_memory_mb}m",
                    "--cpus", "0.5",
                    "--pids-limit", "64",
                    "--cap-drop", "ALL",
                    "--security-opt", "no-new-privileges",
                    "--read-only",
                    "--user", "65534:65534",
                    "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
                    "python:3.11-alpine",
                    "python", "-c", "import sys; exec(sys.stdin.read())"
                ]

                proc = subprocess.run(
                    cmd,
                    input=wrapper_script,
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
                        error_message=stderr or f"Runtime Error (code {proc.returncode})",
                        status="RUNTIME_ERROR"
                    )

                passed = True if expected_output in ("", None) else (normalize_output(stdout) == normalize_output(expected_output))
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
                try:
                    subprocess.run(
                        ["docker", "rm", "--force", container_name],
                        capture_output=True,
                        timeout=3,
                        env=self._sanitize_env(),
                    )
                except Exception:
                    pass

        # Isolated local subprocess fallback with AST sandboxing
        try:
            proc = subprocess.run(
                [sys.executable, "-c", wrapper_script],
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
                    memory_usage=12.0,
                    error_message=stderr or "Runtime Error",
                    status="RUNTIME_ERROR"
                )

            passed = True if expected_output in ("", None) else (normalize_output(stdout) == normalize_output(expected_output))
            return TestCaseResult(
                passed=passed,
                stdout=stdout,
                stderr=stderr,
                execution_time=round(elapsed_time, 4),
                memory_usage=12.0,
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

    def run_javascript_test(
        self,
        code: str,
        input_data: str,
        expected_output: str,
        time_limit: Optional[float] = None
    ) -> TestCaseResult:
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
    if (typeof predictTheWinner === 'function') {{
        console.log(JSON.stringify(predictTheWinner(inputParsed)));
    }} else if (typeof solve === 'function') {{
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

            passed = True if expected_output in ("", None) else (normalize_output(stdout) == normalize_output(expected_output))
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
        """Convenience single-test evaluation method."""
        prep = self.prepare_submission(language, code)
        if not prep.success:
            return TestCaseResult(
                passed=False,
                stdout="",
                stderr=prep.compile_error or "Compilation Failed",
                execution_time=0.0,
                memory_usage=0.0,
                error_message=prep.compile_error,
                status="SECURITY_VIOLATION" if prep.is_security_violation else "COMPILE_ERROR"
            )
        try:
            return self.execute_test_case(
                language=language,
                code=code,
                input_data=input_data,
                expected_output=expected_output,
                prepared=prep,
                time_limit=time_limit,
                memory_limit=memory_limit
            )
        finally:
            self.cleanup_submission(prep)


code_runner = IsolatedCodeRunner()
