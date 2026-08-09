---
name: brainstorm
description: >-
  Interactive brainstorming for viral video content ideas from a project profile.
  Builds on or diverges from existing content preferences; updates profile only
  after user confirmation. Use when the user runs /brainstorm.
disable-model-invocation: true
---

# Brainstorm

Interactive creative session to develop viral content ideas beyond or alongside research.

## Before you start

1. List projects: `python scripts/profile_store.py list`
2. If multiple, ask which project.
3. Load `projects/<slug>/profile.json` and existing ideas in `ideas/`.

## Opening question

If `content_preferences` exist:

> You have **N content preferences** saved. Would you like to:
> 1. **Similar ideas** — more content like your existing preferences
> 2. **Different topics** — explore new angles away from current preferences
> 3. **Mix** — some familiar, some new

If no preferences yet:

> Let's brainstorm! I'll ask a few questions to find angles that fit **[product]** for **[audience]**. Ready?

## Brainstorm flow

Ask adaptive follow-ups (2–4 rounds):

- "What's a pain point your audience feels daily?" (offer 2–3 from profile)
- "Which platform do you want to prioritize this session?" (from profile platforms)
- "Any trending topic you want to ride?" (offer to search if unsure)
- "Fun or serious tone for this batch?" (from positioning)

After each round, propose 2–3 raw ideas. Refine based on reactions.

## Idea format

Each brainstormed idea should include:
- Title, hook, concept
- Platform(s) and content_type_id
- Draft Magic Hour prompt
- `requires_input` if assets needed

Save drafts to `projects/<slug>/ideas/` with `"status": "draft"` until user approves.

## Update preferences

Before ending, if user expressed clear direction:

> **Existing preferences:**
> 1. [pref-001] "Prefer transformation hooks..."
>
> Should I:
> - **Update** an existing preference (show before/after)
> - **Add** a new preference (show text first)
> - **Skip** — no profile changes

Only persist after explicit confirmation:

```bash
python scripts/profile_store.py add-preference --slug <slug> --preference "..." --source brainstorm
```

For updates/replacements:

```bash
python scripts/profile_store.py update-preference --slug <slug> --id <pref-id> --preference "..."
```

## After brainstorm

> Brainstorm complete! **N ideas** saved to `projects/<slug>/ideas/`.
>
> What next?
> 1. **Generate content** — `/generate` to create videos
> 2. **Research more** — `/research-ideas` for data-backed ideas
> 3. **Keep brainstorming** — another round

## Rules

- Show existing preferences before proposing changes.
- Never overwrite preferences without confirmation.
- Respect include/exclude rules.
- Do not call Magic Hour API during brainstorm.
