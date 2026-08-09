# Magic Hour API reference (text-to-video)

Source: https://docs.magichour.ai/api-reference/video-projects/text-to-video

**Re-check official docs before each session** — models, durations, and pricing change.

## Endpoints

| Action | Method | URL |
|--------|--------|-----|
| Create | POST | `https://api.magichour.ai/v1/text-to-video` |
| Poll | GET | `https://api.magichour.ai/v1/video-projects/{id}` |

## Authentication

```
Authorization: Bearer <MAGIC_HOUR_API_KEY>
Content-Type: application/json
```

## Create request

```json
{
  "name": "My video",
  "end_seconds": 8,
  "aspect_ratio": "9:16",
  "resolution": "720p",
  "model": "default",
  "audio": true,
  "style": {
    "prompt": "Your detailed visual prompt here"
  }
}
```

## Create response

```json
{
  "id": "project-id",
  "credits_charged": 450
}
```

`credits_charged` is an initial estimate; final value after completion may differ.

## Poll response (complete)

Key fields: `status` (`queued` | `rendering` | `complete` | `error` | `canceled`), `credits_charged`, `downloads[].url`, `downloads[].expires_at`.

## Model constraints (verify dynamically)

Models have discrete duration values, not continuous ranges. Examples (Aug 2026):

| Model | Durations | Ratios | Audio |
|-------|-----------|--------|-------|
| kling-3.0 | 3–15 | 16:9, 9:16, 1:1 | Extra credits |
| ltx-2.3 | 1–10, 15, 20, 25, 30 | all three | No extra |
| sora-2 | 4, 8, 12, 24, 36, 48, 60 | 16:9, 9:16 | No extra |

`default` model varies by account tier.

## Credit estimation

- No official preflight/estimate-only endpoint.
- Best-effort: use `credits_charged` from create response after submission, or Magic Hour web calculator: https://magichour.ai/api#api-cost-calculator
- Label all pre-submit estimates as **best-effort**.
- Failed jobs are refunded.

## Polling guidance

- Interval: ~5 seconds (10s for longer videos)
- Always set a max timeout (e.g. 10 minutes)
- Exponential backoff on 429/rate limits
- Download URLs expire ~24h — download immediately

## MCP (documentation only)

```json
{
  "mcpServers": {
    "Magic Hour": {
      "url": "https://docs.magichour.ai/mcp"
    }
  }
}
```

Use MCP to look up current model list and pricing — not for generation.

## SDK alternative

Magic Hour provides SDKs (Python, Node). This project uses direct HTTP via `scripts/magichour_video.py` for zero-dependency portability.
