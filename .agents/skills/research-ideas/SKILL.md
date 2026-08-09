---
name: research-ideas
description: >-
  Research viral content ideas from a project profile for Instagram, YouTube,
  X, and TikTok. Saves dated research and candidate ideas; appends confirmed
  content preferences to profile.json. Use when the user runs /research-ideas.
disable-model-invocation: true
---

# Research Ideas

Perform thorough, source-backed viral content research based on the project profile.

## Before you start

1. List projects: `python scripts/profile_store.py list`
2. If multiple projects exist, ask which one to research.
3. Load `projects/<slug>/profile.json`.
4. Read existing `content_preferences` — avoid duplicating confirmed preferences.

## Workflow

```
Research Progress:
- [ ] Select project
- [ ] Load profile + preferences
- [ ] Research per content type / platform
- [ ] Present ideas for feedback
- [ ] Save research report
- [ ] Update preferences (if confirmed)
- [ ] Suggest next step
```

## Research process

For each selected `content_type` in the profile:

1. **Trend scan** — Search for current viral formats in the niche (web search, platform trends).
2. **Competitor scan** — If competitors exist, note what formats they use (without violating exclude rules).
3. **Profile alignment** — Match ideas to audience, positioning, include/exclude rules.
4. **Magic Hour feasibility** — Each idea must be achievable via text-to-video. See [platform-guide.md](references/platform-guide.md).

Generate **3–5 ideas per content type**, each with:
- Title
- Hook (first 3 seconds)
- Concept (1–2 sentences)
- Target platform(s)
- Why it could go viral (1 sentence)
- Suggested Magic Hour params (aspect_ratio, duration, audio)

## Present ideas

Format as a numbered list. After each batch:

> Do these ideas fit your vision? You can:
> - **Keep** specific ideas (e.g. "keep 1 and 3")
> - **Change** an idea (describe what to adjust)
> - **Reject all** and I'll refine

## Follow-up on feedback

When user likes or changes ideas, ask:

> Should I save this as a **content preference** for future sessions?
> Example: "Prefer transformation hooks with humor" — save this? (yes / edit / skip)

If yes, show the preference text before saving. Append to `content_preferences` only after confirmation:

```bash
python scripts/profile_store.py add-preference \
  --slug <slug> \
  --preference "<text>" \
  --source research-ideas \
  --topics "topic1,topic2"
```

## Save research

Write dated report to `projects/<slug>/research/YYYY-MM-DD-research.md`.

Save approved ideas as JSON in `projects/<slug>/ideas/`:

```json
{
  "id": "idea-001",
  "title": "...",
  "hook": "...",
  "concept": "...",
  "platforms": ["tiktok"],
  "content_type_id": "short-form-hook",
  "magichour_prompt": "...",
  "magichour_params": { "aspect_ratio": "9:16", "end_seconds": 8, "audio": true },
  "requires_input": [],
  "status": "ready",
  "created_at": "ISO8601"
}
```

## After research

Ask:

> Research saved to `projects/<slug>/research/`.
>
> What next?
> 1. **Create content calendar** — I'll draft a posting schedule from these ideas
> 2. **Generate content** — `/generate` to create videos with Magic Hour
> 3. **Research more** — different topics or platforms
> 4. **Brainstorm** — `/brainstorm` for interactive ideation

## Rules

- Cite sources when claiming trends (link or platform name).
- Respect `content_rules.exclude` — never suggest excluded topics.
- Emphasize `content_rules.include` when relevant.
- Do not call Magic Hour API during research.
- Show existing preferences before proposing new ones that overlap.

## References

- [Platform research guide](references/platform-guide.md)
- [Source policy](references/source-policy.md)
