import ast
import importlib
import subprocess
import sys

class PackageChecker:
    @staticmethod
    def get_missing_packages(code):
        required = set()
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    required.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    required.add(node.module.split('.')[0])
        missing = []
        for mod in required:
            try:
                importlib.import_module(mod)
            except ImportError:
                missing.append(mod)
        return missing

    @staticmethod
    def install_package(pkg):
        subprocess.call([sys.executable, "-m", "pip", "install", pkg])

    @staticmethod
    def find_missing_packages_with_positions(code):
        missing = []
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return missing
        required = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    required.append((alias.name.split('.')[0], node.lineno))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    required.append((node.module.split('.')[0], node.lineno))
        import importlib
        for pkg, lineno in required:
            try:
                importlib.import_module(pkg)
            except ImportError:
                missing.append((pkg, lineno))
        return missing
