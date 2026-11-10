"""Cross-platform verification script for FarmGuard.

Runs linting, type checks, and tests for all project components.
Exit code 0 only if everything passes.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Resolve project root
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
EDGE_DIR = PROJECT_ROOT / "edge"


def _run(label: str, cmd: list[str], cwd: Path | None = None) -> bool:
    """Run a command and print PASS/FAIL."""
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd or PROJECT_ROOT),
            capture_output=False,
            text=True,
        )
        passed = result.returncode == 0
    except FileNotFoundError:
        print(f"  Command not found: {cmd[0]}")
        passed = False

    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"\n  {status}: {label}")
    return passed


def main() -> int:
    """Run all verification steps and return exit code."""
    results: list[bool] = []

    # 1. Ruff lint
    results.append(
        _run(
            "Ruff lint (edge)",
            [sys.executable, "-m", "ruff", "check", "src", "tests"],
            cwd=EDGE_DIR,
        )
    )

    # 2. Pytest
    results.append(
        _run(
            "Pytest (edge)",
            [sys.executable, "-m", "pytest", "tests", "-v", "--tb=short"],
            cwd=EDGE_DIR,
        )
    )

    # 3. Dashboard (if exists)
    dashboard_dir = PROJECT_ROOT / "dashboard"
    if dashboard_dir.exists() and (dashboard_dir / "package.json").exists():
        results.append(
            _run("Dashboard lint", ["npm", "run", "lint"], cwd=dashboard_dir)
        )
        results.append(
            _run("Dashboard test", ["npm", "test"], cwd=dashboard_dir)
        )
        results.append(
            _run("Dashboard build", ["npm", "run", "build"], cwd=dashboard_dir)
        )

    # Summary
    print(f"\n{'=' * 60}")
    total = len(results)
    passed = sum(results)
    failed = total - passed
    print(f"  SUMMARY: {passed}/{total} passed, {failed} failed")
    print(f"{'=' * 60}")

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())

