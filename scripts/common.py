"""Shared utilities for Proven Viral Content Automation."""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_DIR = REPO_ROOT / "projects"
SCHEMA_PATH = REPO_ROOT / "schemas" / "profile.schema.json"
ENV_PATH = REPO_ROOT / ".env"

SLUG_PATTERN = re.compile(r"^_?[a-z0-9]+(?:-[a-z0-9]+)*$")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug or "project"


def load_env(path: Path | None = None) -> dict[str, str]:
    env: dict[str, str] = {}
    env_file = path or ENV_PATH
    if not env_file.exists():
        return env
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def get_api_key() -> str | None:
    key = os.environ.get("MAGIC_HOUR_API_KEY")
    if key:
        return key
    return load_env().get("MAGIC_HOUR_API_KEY")


def rel_path(path: Path, base: Path = REPO_ROOT) -> str:
    try:
        return str(path.relative_to(base)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def write_json_atomic(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
        suffix=".tmp",
    ) as tmp:
        json.dump(data, tmp, indent=2, ensure_ascii=False)
        tmp.write("\n")
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def project_dir(slug: str) -> Path:
    if not SLUG_PATTERN.match(slug):
        raise ValueError(f"Invalid project slug: {slug}")
    return PROJECTS_DIR / slug


def profile_path(slug: str) -> Path:
    return project_dir(slug) / "profile.json"


def list_projects(*, include_examples: bool = False) -> list[dict[str, str]]:
    projects: list[dict[str, str]] = []
    if not PROJECTS_DIR.exists():
        return projects
    for entry in sorted(PROJECTS_DIR.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("_") and not include_examples:
            continue
        profile = entry / "profile.json"
        if not profile.exists():
            continue
        data = read_json(profile)
        projects.append(
            {
                "slug": data.get("project_slug", entry.name),
                "name": data.get("project_name", entry.name),
                "updated_at": data.get("updated_at", ""),
                "path": rel_path(profile),
            }
        )
    return projects


def ensure_project_dirs(slug: str) -> Path:
    root = project_dir(slug)
    for sub in ("research", "ideas", "calendar", "input", "output"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    return root


def unique_slug(base: str) -> str:
    slug = slugify(base)
    if not (PROJECTS_DIR / slug / "profile.json").exists():
        return slug
    counter = 2
    while (PROJECTS_DIR / f"{slug}-{counter}" / "profile.json").exists():
        counter += 1
    return f"{slug}-{counter}"


def validate_profile(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ["schema_version", "project_slug", "created_at", "updated_at", "product", "content_types"]
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    if data.get("schema_version") != "1.0.0":
        errors.append("schema_version must be 1.0.0")
    slug = data.get("project_slug", "")
    if slug and not SLUG_PATTERN.match(slug):
        errors.append(f"Invalid project_slug: {slug}")
    product = data.get("product")
    if isinstance(product, dict):
        if not product.get("description"):
            errors.append("product.description is required")
        if product.get("type") not in {"product", "service", "project", "other"}:
            errors.append("product.type must be product, service, project, or other")
    content_types = data.get("content_types")
    if not isinstance(content_types, list) or len(content_types) == 0:
        errors.append("content_types must be a non-empty array")
    return errors
