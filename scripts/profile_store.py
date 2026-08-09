#!/usr/bin/env python3
"""Profile persistence for viral content projects."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (
    ensure_project_dirs,
    list_projects,
    profile_path,
    read_json,
    unique_slug,
    utc_now_iso,
    validate_profile,
    write_json_atomic,
)


def cmd_list(args: argparse.Namespace) -> int:
    projects = list_projects(include_examples=args.include_examples)
    if args.json:
        print(json.dumps(projects, indent=2))
        return 0
    if not projects:
        print("No projects found. Run /onboarding to create one.")
        return 0
    print(f"{'Slug':<24} {'Name':<30} Updated")
    print("-" * 70)
    for p in projects:
        print(f"{p['slug']:<24} {p['name']:<30} {p['updated_at']}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.path)
    data = read_json(path)
    errors = validate_profile(data)
    if errors:
        print("Validation failed:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(f"Valid profile: {path}")
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    if args.profile_json:
        payload = read_json(Path(args.profile_json))
    else:
        payload = json.loads(args.profile_inline or "{}")
    slug = payload.get("project_slug") or unique_slug(args.name)
    if not payload.get("project_slug"):
        slug = unique_slug(args.name)
        payload["project_slug"] = slug
    payload.setdefault("project_name", args.name)
    payload.setdefault("schema_version", "1.0.0")
    now = utc_now_iso()
    payload.setdefault("created_at", now)
    payload["updated_at"] = now
    payload.setdefault("content_preferences", [])
    errors = validate_profile(payload)
    if errors:
        print("Cannot create project — validation errors:")
        for err in errors:
            print(f"  - {err}")
        return 1
    ensure_project_dirs(slug)
    out = profile_path(slug)
    write_json_atomic(out, payload)
    print(json.dumps({"slug": slug, "path": str(out)}, indent=2))
    return 0


def _load_profile(slug: str) -> dict[str, Any]:
    path = profile_path(slug)
    if not path.exists():
        raise FileNotFoundError(f"Project not found: {slug}")
    return read_json(path)


def cmd_add_preference(args: argparse.Namespace) -> int:
    profile = _load_profile(args.slug)
    pref_id = args.id or f"pref-{uuid.uuid4().hex[:8]}"
    entry = {
        "id": pref_id,
        "source": args.source,
        "created_at": utc_now_iso(),
        "preference": args.preference,
    }
    if args.topics:
        entry["topics"] = [t.strip() for t in args.topics.split(",") if t.strip()]
    if args.formats:
        entry["formats"] = [f.strip() for f in args.formats.split(",") if f.strip()]
    if args.notes:
        entry["notes"] = args.notes
    prefs = profile.setdefault("content_preferences", [])
    prefs.append(entry)
    profile["updated_at"] = utc_now_iso()
    errors = validate_profile(profile)
    if errors:
        print("Validation failed after update:")
        for err in errors:
            print(f"  - {err}")
        return 1
    write_json_atomic(profile_path(args.slug), profile)
    print(json.dumps(entry, indent=2))
    return 0


def cmd_update_preference(args: argparse.Namespace) -> int:
    profile = _load_profile(args.slug)
    prefs = profile.get("content_preferences", [])
    found = False
    for pref in prefs:
        if pref.get("id") == args.id:
            if args.preference:
                pref["preference"] = args.preference
            if args.topics:
                pref["topics"] = [t.strip() for t in args.topics.split(",") if t.strip()]
            if args.formats:
                pref["formats"] = [f.strip() for f in args.formats.split(",") if f.strip()]
            if args.notes:
                pref["notes"] = args.notes
            pref["updated_at"] = utc_now_iso()
            found = True
            break
    if not found:
        print(f"Preference not found: {args.id}")
        return 1
    profile["updated_at"] = utc_now_iso()
    write_json_atomic(profile_path(args.slug), profile)
    print(json.dumps({"updated": args.id}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage viral content project profiles")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List projects")
    p_list.add_argument("--json", action="store_true")
    p_list.add_argument("--include-examples", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_validate = sub.add_parser("validate", help="Validate a profile.json")
    p_validate.add_argument("path")
    p_validate.set_defaults(func=cmd_validate)

    p_create = sub.add_parser("create", help="Create a project from profile JSON")
    p_create.add_argument("--name", required=True, help="Human-readable project name")
    p_create.add_argument("--profile-json", help="Path to full profile payload JSON")
    p_create.add_argument("--profile-inline", help="Inline JSON string for profile payload")
    p_create.set_defaults(func=cmd_create)

    p_add = sub.add_parser("add-preference", help="Append a content preference")
    p_add.add_argument("--slug", required=True)
    p_add.add_argument("--preference", required=True)
    p_add.add_argument("--source", default="research-ideas", choices=["research-ideas", "brainstorm", "onboarding"])
    p_add.add_argument("--id")
    p_add.add_argument("--topics")
    p_add.add_argument("--formats")
    p_add.add_argument("--notes")
    p_add.set_defaults(func=cmd_add_preference)

    p_upd = sub.add_parser("update-preference", help="Update an existing preference")
    p_upd.add_argument("--slug", required=True)
    p_upd.add_argument("--id", required=True)
    p_upd.add_argument("--preference")
    p_upd.add_argument("--topics")
    p_upd.add_argument("--formats")
    p_upd.add_argument("--notes")
    p_upd.set_defaults(func=cmd_update_preference)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
