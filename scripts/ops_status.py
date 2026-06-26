#!/usr/bin/env python3
"""Print configured data-quality task status.

Reads ops/data-quality-tasks.yaml. Uses systemctl when present; otherwise prints
configured tasks only.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS = ROOT / "ops" / "data-quality-tasks.yaml"


def load_tasks(path: Path) -> list[dict[str, str | None]]:
    tasks: list[dict[str, str | None]] = []
    current: dict[str, str | None] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line == "tasks:" or line.startswith("#"):
            continue
        if line.startswith("- "):
            if current:
                tasks.append(current)
            current = {}
            line = line[2:]
        if current is None or ":" not in line:
            continue
        key, value = line.split(":", 1)
        current[key.strip()] = value.strip() or None
    if current:
        tasks.append(current)
    return tasks


def run_systemctl(*args: str) -> str:
    if not shutil.which("systemctl"):
        return "n/a"
    try:
        result = subprocess.run(
            ["systemctl", *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    stderr = result.stderr.strip()
    if result.returncode != 0 and (
        "not been booted" in stderr or "Failed to connect" in stderr
    ):
        return "unavailable"
    return (result.stdout or result.stderr).strip() or "unknown"


def timer_next(timer: str | None) -> str:
    if not timer:
        return "-"
    if not shutil.which("systemctl"):
        return "n/a"
    result = subprocess.run(
        ["systemctl", "list-timers", "--all", "--no-legend", timer],
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
    )
    if result.returncode != 0 and (
        "not been booted" in result.stderr or "Failed to connect" in result.stderr
    ):
        return "unavailable"
    line = result.stdout.strip().splitlines()
    if not line:
        return "unknown"
    return " ".join(line[0].split()[:5])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    args = parser.parse_args()

    tasks = load_tasks(args.tasks)

    print(f"{'task':28s} {'level':8s} {'enabled':12s} {'active':12s} next")
    print("-" * 80)
    for task in tasks:
        timer = task.get("systemd_timer")
        service = task.get("systemd_service")
        enabled = run_systemctl("is-enabled", timer) if timer else "manual"
        active_target = timer or service
        active = run_systemctl("is-active", active_target) if active_target else "manual"
        print(
            f"{task['id'][:28]:28s} "
            f"{task.get('level', '-')[:8]:8s} "
            f"{enabled[:12]:12s} "
            f"{active[:12]:12s} "
            f"{timer_next(timer)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
