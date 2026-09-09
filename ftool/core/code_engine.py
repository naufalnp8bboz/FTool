import ast
import base64
import hashlib
import json
import re
import sys
import io
import time
import urllib.parse
from typing import Dict, Any, List, Optional
import requests

class CodeEngine:
    @staticmethod
    def execute_python_code(code_str: str) -> Dict[str, Any]:
        """Executes python code safely and captures stdout, stderr, and elapsed time."""
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_out = io.StringIO()
        redirected_err = io.StringIO()
        sys.stdout = redirected_out
        sys.stderr = redirected_err

        start_time = time.perf_counter()
        success = True
        error_msg = ""

        try:
            # Local namespace for execution
            exec_globals = {"__builtins__": __builtins__}
            exec_locals = {}
            exec(code_str, exec_globals, exec_locals)
        except Exception as e:
            success = False
            error_msg = str(e)
            print(f"Error: {e}", file=sys.stderr)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        elapsed = (time.perf_counter() - start_time) * 1000.0

        return {
            "success": success,
            "stdout": redirected_out.getvalue(),
            "stderr": redirected_err.getvalue() or error_msg,
            "execution_time_ms": round(elapsed, 2)
        }

    @staticmethod
    def analyze_python_ast(code_str: str) -> Dict[str, Any]:
        """Inspects AST structure to extract classes, functions, and imports for beginners."""
        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return {"error": f"Syntax Error on line {e.lineno}: {e.msg}"}

        imports = []
        functions = []
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.append(n.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for n in node.names:
                    imports.append(f"{module}.{n.name}")
            elif isinstance(node, ast.FunctionDef):
                args = [arg.arg for arg in node.args.args]
                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "args": args,
                    "docstring": ast.get_docstring(node) or "No docstring"
                })
            elif isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "methods": methods,
                    "docstring": ast.get_docstring(node) or "No docstring"
                })

        return {
            "imports": sorted(list(set(imports))),
            "functions": functions,
            "classes": classes,
            "total_lines": len(code_str.splitlines())
        }

    @staticmethod
    def format_json(raw_text: str, indent: int = 4) -> Dict[str, Any]:
        try:
            parsed = json.loads(raw_text)
            formatted = json.dumps(parsed, indent=indent)
            return {"success": True, "result": formatted}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def test_regex(pattern: str, text: str, ignore_case: bool = False, multiline: bool = False) -> Dict[str, Any]:
        flags = 0
        if ignore_case:
            flags |= re.IGNORECASE
        if multiline:
            flags |= re.MULTILINE

        try:
            compiled = re.compile(pattern, flags)
        except re.error as e:
            return {"success": False, "error": str(e), "matches": []}

        matches = []
        for m in compiled.finditer(text):
            matches.append({
                "match": m.group(0),
                "start": m.start(),
                "end": m.end(),
                "groups": m.groups()
            })

        return {
            "success": True,
            "match_count": len(matches),
            "matches": matches
        }

    @staticmethod
    def convert_string(text: str, op_type: str) -> str:
        try:
            if op_type == "base64_encode":
                return base64.b64encode(text.encode("utf-8")).decode("utf-8")
            elif op_type == "base64_decode":
                return base64.b64decode(text.encode("utf-8")).decode("utf-8", errors="replace")
            elif op_type == "md5":
                return hashlib.md5(text.encode("utf-8")).hexdigest()
            elif op_type == "sha256":
                return hashlib.sha256(text.encode("utf-8")).hexdigest()
            elif op_type == "url_encode":
                return urllib.parse.quote(text)
            elif op_type == "url_decode":
                return urllib.parse.unquote(text)
            elif op_type == "hex_encode":
                return text.encode("utf-8").hex()
            elif op_type == "hex_decode":
                return bytes.fromhex(text).decode("utf-8", errors="replace")
            elif op_type == "jwt_decode":
                parts = text.split(".")
                if len(parts) >= 2:
                    header = base64.urlsafe_b64decode(parts[0] + "==").decode("utf-8", errors="replace")
                    payload = base64.urlsafe_b64decode(parts[1] + "==").decode("utf-8", errors="replace")
                    return f"HEADER:\n{json.dumps(json.loads(header), indent=2)}\n\nPAYLOAD:\n{json.dumps(json.loads(payload), indent=2)}"
                return "Invalid JWT token structure."
            return text
        except Exception as e:
            return f"Conversion Error: {e}"

    @staticmethod
    def send_http_request(url: str, method: str = "GET", headers_dict: Optional[dict] = None, data_str: Optional[str] = None) -> Dict[str, Any]:
        start = time.perf_counter()
        try:
            resp = requests.request(
                method=method.upper(),
                url=url,
                headers=headers_dict or {},
                data=data_str if data_str else None,
                timeout=10
            )
            elapsed_ms = round((time.perf_counter() - start) * 1000.0, 2)
            
            try:
                body_formatted = json.dumps(resp.json(), indent=2)
            except Exception:
                body_formatted = resp.text

            return {
                "success": True,
                "status_code": resp.status_code,
                "latency_ms": elapsed_ms,
                "headers": dict(resp.headers),
                "body": body_formatted
            }
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start) * 1000.0, 2)
            return {
                "success": False,
                "status_code": 0,
                "latency_ms": elapsed_ms,
                "headers": {},
                "body": f"Request Failed: {e}"
            }
