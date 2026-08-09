#!/usr/bin/env python3
"""Validate repository structure, skill frontmatter, and example JSON."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_SKILLS = ["onboarding", "research-ideas", "brainstorm", "generate"]
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def check_skills(errors: list[str]) -> None:
    for name in REQUIRED_SKILLS:
        skill_path = REPO_ROOT / ".agents" / "skills" / name / "SKILL.md"
        if not skill_path.exists():
            errors.append(f"Missing skill: {skill_path}")
            continue
        meta = parse_frontmatter(skill_path.read_text(encoding="utf-8"))
        if meta.get("name") != name:
            errors.append(f"Skill name mismatch in {skill_path}: {meta.get('name')}")
        if not meta.get("description"):
            errors.append(f"Missing description in {skill_path}")


def check_adapters(errors: list[str]) -> None:
    for name in REQUIRED_SKILLS:
        claude = REPO_ROOT / ".claude" / "skills" / name / "SKILL.md"
        workflow = REPO_ROOT / ".agents" / "workflows" / f"{name}.md"
        opencode = REPO_ROOT / ".opencode" / "commands" / f"{name}.md"
        for path in (claude, workflow, opencode):
            if not path.exists():
                errors.append(f"Missing adapter: {path}")


def check_example_json(errors: list[str]) -> None:
    profile = REPO_ROOT / "projects" / "_example" / "profile.json"
    idea = REPO_ROOT / "projects" / "_example" / "ideas" / "idea-001.json"
    for path in (profile, idea):
        if not path.exists():
            errors.append(f"Missing example file: {path}")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in {path}: {exc}")


def main() -> int:
    errors: list[str] = []
    check_skills(errors)
    check_adapters(errors)
    check_example_json(errors)
    required_files = [
        "AGENTS.md",
        "CLAUDE.md",
        ".env.example",
        "schemas/profile.schema.json",
        "scripts/profile_store.py",
        "scripts/magichour_video.py",
        "docs/setup.md",
    ]
    for rel in required_files:
        if not (REPO_ROOT / rel).exists():
            errors.append(f"Missing required file: {rel}")
    if errors:
        print("Structure validation failed:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("Structure validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
