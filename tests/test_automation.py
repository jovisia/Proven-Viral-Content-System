"""Tests for Proven Viral Content Automation."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from common import (  # noqa: E402
    PROJECTS_DIR,
    ensure_project_dirs,
    list_projects,
    profile_path,
    read_json,
    slugify,
    unique_slug,
    validate_profile,
    write_json_atomic,
)
from magichour_video import (  # noqa: E402
    build_preview_manifest,
    build_request_body,
    poll_until_complete,
    validate_params,
)


SAMPLE_PROFILE = {
    "schema_version": "1.0.0",
    "project_slug": "test-brand",
    "project_name": "Test Brand",
    "created_at": "2026-08-08T00:00:00Z",
    "updated_at": "2026-08-08T00:00:00Z",
    "product": {
        "description": "A test product for viral content",
        "type": "product",
    },
    "content_types": [
        {
            "id": "short-form-hook",
            "label": "Short hook",
            "platforms": ["tiktok"],
        }
    ],
}


SAMPLE_IDEA = {
    "id": "idea-test",
    "title": "Test idea",
    "magichour_prompt": "A cinematic sunset over the ocean with gentle waves",
    "magichour_params": {
        "aspect_ratio": "9:16",
        "end_seconds": 8,
        "resolution": "720p",
        "model": "default",
        "audio": True,
    },
}


class ProfileStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.projects_dir = Path(self._tmpdir.name) / "projects"
        self.projects_dir.mkdir()
        self._orig = PROJECTS_DIR
        import common

        common.PROJECTS_DIR = self.projects_dir

    def tearDown(self) -> None:
        import common

        common.PROJECTS_DIR = self._orig
        self._tmpdir.cleanup()

    def test_slugify(self) -> None:
        self.assertEqual(slugify("My Cool Brand!"), "my-cool-brand")

    def test_validate_profile_ok(self) -> None:
        self.assertEqual(validate_profile(SAMPLE_PROFILE), [])

    def test_validate_profile_missing_fields(self) -> None:
        bad = {"schema_version": "1.0.0"}
        errors = validate_profile(bad)
        self.assertTrue(any("project_slug" in e for e in errors))

    def test_create_and_list_project(self) -> None:
        slug = "test-brand"
        ensure_project_dirs(slug)
        write_json_atomic(profile_path(slug), SAMPLE_PROFILE)
        projects = list_projects()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["slug"], slug)

    def test_unique_slug_collision(self) -> None:
        slug = unique_slug("Acme Co")
        ensure_project_dirs(slug)
        write_json_atomic(profile_path(slug), {**SAMPLE_PROFILE, "project_slug": slug})
        slug2 = unique_slug("Acme Co")
        self.assertNotEqual(slug, slug2)

    def test_atomic_write(self) -> None:
        slug = "atomic-test"
        ensure_project_dirs(slug)
        path = profile_path(slug)
        write_json_atomic(path, SAMPLE_PROFILE)
        loaded = read_json(path)
        self.assertEqual(loaded["project_slug"], "test-brand")


class MagicHourVideoTests(unittest.TestCase):
    def test_validate_params_ok(self) -> None:
        errors = validate_params(
            {
                "prompt": "A test prompt",
                "end_seconds": 8,
                "aspect_ratio": "9:16",
                "resolution": "720p",
                "model": "default",
            }
        )
        self.assertEqual(errors, [])

    def test_validate_params_bad_duration(self) -> None:
        errors = validate_params(
            {
                "prompt": "Test",
                "end_seconds": 7,
                "aspect_ratio": "9:16",
                "resolution": "720p",
                "model": "kling-2.5",
            }
        )
        self.assertTrue(any("end_seconds" in e for e in errors))

    def test_build_request_body(self) -> None:
        body = build_request_body(SAMPLE_IDEA)
        self.assertEqual(body["aspect_ratio"], "9:16")
        self.assertIn("prompt", body["style"])

    def test_preview_manifest(self) -> None:
        idea_path = Path("ideas/idea-test.json")
        manifest = build_preview_manifest("_example", idea_path, SAMPLE_IDEA, None)
        self.assertEqual(manifest["mode"], "preview")
        self.assertIn("credit_estimate", manifest)

    def test_poll_complete(self) -> None:
        responses = [
            {"status": "queued", "credits_charged": 100},
            {"status": "rendering", "credits_charged": 100},
            {
                "status": "complete",
                "credits_charged": 120,
                "downloads": [{"url": "https://example.com/out.mp4"}],
            },
        ]

        def fake_get(_key: str, _pid: str) -> dict:
            return responses.pop(0)

        with mock.patch("magichour_video.get_video_details", side_effect=fake_get):
            with mock.patch("magichour_video.time.sleep"):
                details, history = poll_until_complete("key", "proj-1", interval=0, timeout=30)
        self.assertEqual(details["status"], "complete")
        self.assertEqual(len(history), 3)

    def test_poll_error_status(self) -> None:
        with mock.patch(
            "magichour_video.get_video_details",
            return_value={"status": "error", "error": "render failed"},
        ):
            with self.assertRaises(Exception):
                poll_until_complete("key", "proj-1", interval=0, timeout=5)


class ExampleProjectTests(unittest.TestCase):
    def test_example_profile_valid(self) -> None:
        path = REPO_ROOT / "projects" / "_example" / "profile.json"
        data = read_json(path)
        self.assertEqual(validate_profile(data), [])

    def test_example_idea_json(self) -> None:
        path = REPO_ROOT / "projects" / "_example" / "ideas" / "idea-001.json"
        data = read_json(path)
        self.assertIn("magichour_prompt", data)


if __name__ == "__main__":
    unittest.main()
