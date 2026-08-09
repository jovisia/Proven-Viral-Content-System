# Content types mapped to Magic Hour text-to-video

Source: https://docs.magichour.ai/tools/video/text-to-video

Always verify current model capabilities from official docs before generation. Do not hardcode pricing.

## Platform defaults

| Platform | Aspect ratio | Typical duration | Notes |
|----------|--------------|------------------|-------|
| Instagram Reels | 9:16 | 5–15s | Hook in first 3s |
| TikTok | 9:16 | 5–15s | Trend-native hooks |
| YouTube Shorts | 9:16 | 5–15s | Clear payoff |
| YouTube (long) | 16:9 | 10–60s | B-roll / intro clips |
| X / Twitter | 16:9 or 1:1 | 5–15s | Autoplay-friendly |

## Suggested content types

Present these during onboarding (user picks ≥1):

### 1. short-form-hook
- **Label:** Short-form hook video (Reels / TikTok / Shorts)
- **Platforms:** instagram, tiktok, youtube
- **Magic Hour:** `aspect_ratio: 9:16`, `end_seconds: 5-8`, `audio: true`

### 2. product-demo
- **Label:** Product demo / feature showcase
- **Platforms:** youtube, x
- **Magic Hour:** `aspect_ratio: 16:9`, `end_seconds: 10-15`, `audio: true`

### 3. cinematic-broll
- **Label:** Cinematic B-roll / mood clip
- **Platforms:** youtube, instagram
- **Magic Hour:** `aspect_ratio: 16:9`, `end_seconds: 8-15`, `audio: false`

### 4. meme-reaction
- **Label:** Meme / reaction-style clip
- **Platforms:** tiktok, x, instagram
- **Magic Hour:** `aspect_ratio: 9:16` or `1:1`, `end_seconds: 4-8`, `audio: true`

### 5. testimonial-visual
- **Label:** Visual backdrop for testimonial / quote
- **Platforms:** instagram, youtube
- **Magic Hour:** `aspect_ratio: 9:16`, `end_seconds: 8-12`, `audio: false`

## Model selection guidance

- Use `model: "default"` unless user specifies otherwise.
- `default` resolves per account tier (check docs at generation time).
- Enable `audio: true` for social-native content; disable for silent B-roll.
- Match `end_seconds` to model-specific allowed durations (see Magic Hour API reference).

## Resolution guidance

- Free tier: typically 480p
- Paid tiers: 720p default; 1080p/4k where model + account allow
- Recommend 720p for drafts, 1080p for final posts
