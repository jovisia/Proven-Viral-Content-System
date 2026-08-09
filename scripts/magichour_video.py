#!/usr/bin/env python3
"""Magic Hour text-to-video generation helper."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import REPO_ROOT, get_api_key, project_dir, read_json, rel_path, utc_now_iso, write_json_atomic

API_BASE = "https://api.magichour.ai/v1"
CREATE_URL = f"{API_BASE}/text-to-video"

# Best-effort constraints — verify against official docs before production use.
MODEL_DURATIONS: dict[str, list[int]] = {
    "default": list(range(3, 16)),
    "kling-3.0": list(range(3, 16)),
    "ltx-2.3": list(range(1, 11)) + [15, 20, 25, 30],
    "sora-2": [4, 8, 12, 24, 36, 48, 60],
    "wan-2.2": list(range(3, 11)) + [15],
    "kling-2.5": [5, 10],
    "veo3.1": [4, 6, 8] + list(range(16, 57, 8)),
    "veo3.1-lite": [4, 6, 8] + list(range(16, 57, 8)),
    "seedance-1.5": list(range(4, 13)),
    "seedance-2.0": list(range(4, 16)),
    "seedance-2.0-mini": list(range(4, 16)),
}

VALID_ASPECT_RATIOS = {"16:9", "9:16", "1:1"}
VALID_RESOLUTIONS = {"480p", "720p", "1080p", "4k"}

POLL_INTERVAL_SEC = 5
POLL_TIMEOUT_SEC = 600


class MagicHourError(Exception):
    pass


def _request(
    method: str,
    url: str,
    *,
    api_key: str,
    payload: dict[str, Any] | None = None,
    timeout: int = 60,
) -> tuple[int, dict[str, Any] | str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            if body:
                return resp.status, json.loads(body)
            return resp.status, {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = body
        return exc.code, parsed


def validate_params(params: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prompt = params.get("prompt", "")
    if not prompt or not isinstance(prompt, str):
        errors.append("prompt is required")
    elif len(prompt) > 2000:
        errors.append("prompt must be at most 2000 characters")
    model = params.get("model", "default")
    end_seconds = params.get("end_seconds")
    if end_seconds is None:
        errors.append("end_seconds is required")
    else:
        allowed = MODEL_DURATIONS.get(model, MODEL_DURATIONS["default"])
        if int(end_seconds) not in allowed:
            errors.append(
                f"end_seconds {end_seconds} not supported for model {model}. "
                f"Allowed (best-effort): {allowed[:10]}{'...' if len(allowed) > 10 else ''}"
            )
    aspect = params.get("aspect_ratio", "16:9")
    if aspect not in VALID_ASPECT_RATIOS:
        errors.append(f"aspect_ratio must be one of {sorted(VALID_ASPECT_RATIOS)}")
    resolution = params.get("resolution", "720p")
    if resolution not in VALID_RESOLUTIONS:
        errors.append(f"resolution must be one of {sorted(VALID_RESOLUTIONS)}")
    return errors


def build_request_body(idea: dict[str, Any], profile: dict[str, Any] | None = None) -> dict[str, Any]:
    params = dict(idea.get("magichour_params") or {})
    prompt = idea.get("magichour_prompt") or idea.get("concept") or idea.get("title", "")
    name = idea.get("title") or f"Generate - {idea.get('id', 'idea')}"
    body: dict[str, Any] = {
        "name": name[:200],
        "end_seconds": params.get("end_seconds", 8),
        "aspect_ratio": params.get("aspect_ratio", "9:16"),
        "resolution": params.get("resolution", "720p"),
        "model": params.get("model", "default"),
        "audio": bool(params.get("audio", True)),
        "style": {"prompt": prompt},
    }
    return body


def build_preview_manifest(
    slug: str,
    idea_path: Path,
    idea: dict[str, Any],
    profile: dict[str, Any] | None,
) -> dict[str, Any]:
    body = build_request_body(idea, profile)
    validation_errors = validate_params(
        {
            "prompt": body["style"]["prompt"],
            "end_seconds": body["end_seconds"],
            "aspect_ratio": body["aspect_ratio"],
            "resolution": body["resolution"],
            "model": body["model"],
        }
    )
    requires_input = idea.get("requires_input") or []
    missing_inputs = []
    if requires_input:
        input_dir = project_dir(slug) / "input"
        for filename in requires_input:
            if not (input_dir / filename).exists():
                missing_inputs.append(filename)
    return {
        "mode": "preview",
        "project_slug": slug,
        "idea_path": rel_path(idea_path),
        "request": body,
        "validation_errors": validation_errors,
        "missing_inputs": missing_inputs,
        "credit_estimate": {
            "value": None,
            "confidence": "unknown",
            "note": (
                "Best-effort: Magic Hour has no estimate-only API. "
                "Exact credits are returned on job creation and may adjust after render. "
                "See https://magichour.ai/api#api-cost-calculator"
            ),
        },
        "generated_at": utc_now_iso(),
    }


def create_video(api_key: str, body: dict[str, Any]) -> dict[str, Any]:
    status, data = _request("POST", CREATE_URL, api_key=api_key, payload=body)
    if status >= 400:
        raise MagicHourError(f"Create failed ({status}): {data}")
    if not isinstance(data, dict):
        raise MagicHourError(f"Unexpected create response: {data}")
    return data


def get_video_details(api_key: str, project_id: str) -> dict[str, Any]:
    url = f"{API_BASE}/video-projects/{project_id}"
    status, data = _request("GET", url, api_key=api_key)
    if status >= 400:
        raise MagicHourError(f"Poll failed ({status}): {data}")
    if not isinstance(data, dict):
        raise MagicHourError(f"Unexpected poll response: {data}")
    return data


def poll_until_complete(
    api_key: str,
    project_id: str,
    *,
    interval: float = POLL_INTERVAL_SEC,
    timeout: float = POLL_TIMEOUT_SEC,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    history: list[dict[str, Any]] = []
    deadline = time.time() + timeout
    while time.time() < deadline:
        details = get_video_details(api_key, project_id)
        history.append(
            {
                "at": utc_now_iso(),
                "status": details.get("status"),
                "credits_charged": details.get("credits_charged"),
            }
        )
        status = details.get("status")
        if status == "complete":
            return details, history
        if status in {"error", "canceled"}:
            raise MagicHourError(f"Job ended with status {status}: {details}")
        time.sleep(interval)
    raise MagicHourError(f"Polling timed out after {timeout}s for project {project_id}")


def download_file(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())
    return dest


def output_run_dir(slug: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return project_dir(slug) / "output" / stamp


def cmd_check_key(_: argparse.Namespace) -> int:
    key = get_api_key()
    if not key or key == "your_api_key_here":
        print("MAGIC_HOUR_API_KEY is not configured.")
        print("Copy .env.example to .env and set your API key.")
        print("Get your Magic Hour API key: https://manicule.link/srp")
        print("Use coupon code FIRSTAPI for free credits.")
        return 1
    print("MAGIC_HOUR_API_KEY is configured.")
    return 0


def _resolve_idea(slug: str, idea_arg: str) -> tuple[Path, dict[str, Any]]:
    idea_path = Path(idea_arg)
    if not idea_path.is_absolute():
        candidate = project_dir(slug) / idea_arg
        if candidate.exists():
            idea_path = candidate
        elif (REPO_ROOT / idea_arg).exists():
            idea_path = REPO_ROOT / idea_arg
    if not idea_path.exists():
        raise FileNotFoundError(f"Idea file not found: {idea_arg}")
    return idea_path, read_json(idea_path)


def cmd_preview(args: argparse.Namespace) -> int:
    idea_path, idea = _resolve_idea(args.project, args.idea)
    profile = None
    profile_file = project_dir(args.project) / "profile.json"
    if profile_file.exists():
        profile = read_json(profile_file)
    manifest = build_preview_manifest(args.project, idea_path, idea, profile)
    print(json.dumps(manifest, indent=2))
    if manifest["validation_errors"]:
        return 1
    if manifest["missing_inputs"]:
        print("\nMissing input files:", ", ".join(manifest["missing_inputs"]))
        return 1
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    if not args.confirm_spend:
        print("Refusing to generate without --confirm-spend (explicit spend confirmation required).")
        return 1
    api_key = get_api_key()
    if not api_key or api_key == "your_api_key_here":
        print("MAGIC_HOUR_API_KEY is not configured. See: python scripts/magichour_video.py check-key")
        return 1
    idea_path, idea = _resolve_idea(args.project, args.idea)
    profile = None
    profile_file = project_dir(args.project) / "profile.json"
    if profile_file.exists():
        profile = read_json(profile_file)
    preview = build_preview_manifest(args.project, idea_path, idea, profile)
    if preview["validation_errors"]:
        print("Validation errors:")
        for err in preview["validation_errors"]:
            print(f"  - {err}")
        return 1
    if preview["missing_inputs"]:
        print("Missing input files:", ", ".join(preview["missing_inputs"]))
        return 1
    body = preview["request"]
    run_dir = output_run_dir(args.project)
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "mode": "generate",
        "project_slug": args.project,
        "idea_path": rel_path(idea_path),
        "request": body,
        "started_at": utc_now_iso(),
        "status_history": [],
    }
    try:
        create_resp = create_video(api_key, body)
    except MagicHourError as exc:
        print(str(exc))
        return 1
    project_id = create_resp.get("id")
    initial_credits = create_resp.get("credits_charged")
    manifest["create_response"] = {
        "id": project_id,
        "credits_charged_initial": initial_credits,
    }
    print(f"Job created: {project_id} (initial credits: {initial_credits})")
    try:
        details, history = poll_until_complete(api_key, project_id)
    except MagicHourError as exc:
        manifest["error"] = str(exc)
        manifest["status_history"] = manifest.get("status_history", [])
        write_json_atomic(run_dir / "manifest.json", manifest)
        print(str(exc))
        return 1
    manifest["status_history"] = history
    manifest["final_response"] = {
        "status": details.get("status"),
        "credits_charged_final": details.get("credits_charged"),
    }
    downloads = details.get("downloads") or []
    downloaded: list[str] = []
    for idx, item in enumerate(downloads):
        url = item.get("url")
        if not url:
            continue
        suffix = ".mp4" if idx == 0 else f"-{idx}.mp4"
        dest = run_dir / f"output{suffix}"
        download_file(url, dest)
        downloaded.append(rel_path(dest))
    manifest["downloads"] = downloaded
    manifest["completed_at"] = utc_now_iso()
    write_json_atomic(run_dir / "manifest.json", manifest)
    print(json.dumps(manifest, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Magic Hour text-to-video helper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_key = sub.add_parser("check-key", help="Verify MAGIC_HOUR_API_KEY is set")
    p_key.set_defaults(func=cmd_check_key)

    p_preview = sub.add_parser("preview", help="Preview generation manifest (no API call)")
    p_preview.add_argument("--project", required=True)
    p_preview.add_argument("--idea", required=True, help="Path to idea JSON under project ideas/")
    p_preview.set_defaults(func=cmd_preview)

    p_gen = sub.add_parser("generate", help="Submit generation job (billable)")
    p_gen.add_argument("--project", required=True)
    p_gen.add_argument("--idea", required=True)
    p_gen.add_argument(
        "--confirm-spend",
        action="store_true",
        help="Required flag confirming user approved credit spend",
    )
    p_gen.set_defaults(func=cmd_generate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
