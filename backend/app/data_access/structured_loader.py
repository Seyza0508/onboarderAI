import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "structured"


def _load_json(filename: str) -> Any:
    filepath = DATA_DIR / filename
    return json.loads(filepath.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def get_role_requirements() -> dict[str, dict]:
    """Return role requirements keyed by role name."""
    raw = _load_json("role_requirements.json")
    return {entry["role"]: entry for entry in raw["roles"]}


@lru_cache(maxsize=1)
def get_team_requirements() -> dict[str, dict]:
    """Return team requirements keyed by team name."""
    raw = _load_json("team_requirements.json")
    return {entry["team"]: entry for entry in raw["teams"]}


@lru_cache(maxsize=1)
def get_task_templates() -> list[dict]:
    """Return the full list of task template definitions."""
    raw = _load_json("task_templates.json")
    return raw["templates"]


def find_matching_templates(role: str, team: str) -> list[dict]:
    """Find all task templates that match the given role and team."""
    return [t for t in get_task_templates() if t["role"] == role and t["team"] == team]
