---
name: generate
description: >-
  Generate viral video content via Magic Hour text-to-video API. Builds detailed
  prompts from project ideas, shows best-effort credit estimate, requires spend
  confirmation, polls job status, and saves outputs. Use when the user runs
  /generate or wants to create videos from saved ideas.
disable-model-invocation: true
---

# Generate Content

Turn saved content ideas into Magic Hour videos.

## Before you start

### 1. Verify API key

```bash
python scripts/magichour_video.py check-key
```

If missing, stop and instruct:

> Magic Hour API key not configured. Add to `.env`:
> ```
> MAGIC_HOUR_API_KEY=your_key_here
> ```
> Get your [Magic Hour](https://manicule.link/srp) API key. Use coupon code **`FIRSTAPI`** for free credits.

Optional: Magic Hour **docs MCP** (`https://docs.magichour.ai/mcp`) helps look up current models/pricing — it does **not** generate videos.

### 2. Select project

`python scripts/profile_store.py list` — ask if multiple.

### 3. Select idea

List ideas in `projects/<slug>/ideas/`. If none, offer to run `/research-ideas` or `/brainstorm` first.

## Generation workflow

```
Generate Progress:
- [ ] API key verified
- [ ] Project + idea selected
- [ ] Resolve input dependencies
- [ ] Build detailed prompt
- [ ] Preview + credit estimate
- [ ] User confirms spend
- [ ] Submit API job
- [ ] Poll + download
- [ ] Save manifest
- [ ] Offer generate more
```

## Build detailed prompt

Expand the idea into a production-ready Magic Hour prompt (1–2000 chars). See [prompt-templates.md](references/prompt-templates.md).

Include:
- Scene description (subject, action, environment)
- Camera movement
- Lighting / mood
- Style (cinematic, animated, etc.)

Map params from idea or content type defaults. Validate against current model constraints — see [magichour-api.md](references/magichour-api.md).

## Input dependencies

If `requires_input` is non-empty:

> This idea needs: **[logo.png, product-screenshot.png]**. Please add files to `projects/<slug>/input/` and confirm when ready.

For text-to-video, inputs are usually not required. If using image-to-video in future, handle uploads per Magic Hour docs.

## Preview and credit estimate

```bash
python scripts/magichour_video.py preview \
  --project <slug> \
  --idea ideas/<idea-file>.json
```

Present to user:

> **Generation preview**
> - Prompt: [truncated prompt]
> - Model: [model], [duration]s, [aspect_ratio], [resolution], audio: [on/off]
> - **Credit estimate (best-effort):** ~[X] credits *(final charge may differ after render)*
> - Source: Magic Hour pricing docs / create response
>
> Proceed? This will spend credits. **(yes / no / adjust params)**

**Never submit without explicit yes.**

## Submit generation

```bash
python scripts/magichour_video.py generate \
  --project <slug> \
  --idea ideas/<idea-file>.json \
  --confirm-spend
```

Script will:
1. POST `/v1/text-to-video`
2. Poll `GET /v1/video-projects/{id}` (~5s intervals, bounded timeout)
3. Download MP4 to `projects/<slug>/output/<timestamp>/`
4. Save manifest with prompts, params, credits_charged, download URL

## After generation

> Video saved to `projects/<slug>/output/<timestamp>/output.mp4`
> Credits charged: **[final]** (initial estimate was **[initial]**)
>
> What next?
> 1. **Generate another** — pick a different idea or tweak this one
> 2. **Brainstorm more** — `/brainstorm`
> 3. **Research more** — `/research-ideas`

## Error handling

| Status | Action |
|--------|--------|
| 401 | Invalid API key — check `.env` |
| 402 | Insufficient credits — link to https://magichour.ai/pricing |
| 422 | Invalid params — adjust model/duration/resolution |
| Job error | Show error from API; failed jobs are refunded |
| Timeout | Suggest checking Developer Hub; offer retry |

## Rules

- Always preview before generate.
- Always require `--confirm-spend` or explicit user yes.
- Download promptly — URLs expire (~24h).
- Do not expose API key in logs or manifests.
- Re-check model capabilities from docs when params fail validation.

## References

- [Prompt templates](references/prompt-templates.md)
- [Magic Hour API notes](references/magichour-api.md)
