---
name: onboarding
description: >-
  Conversational onboarding for viral content projects. Collects product/service
  details, audience, features, competitors, positioning, content rules, and
  Magic Hour content types; creates projects/<slug>/profile.json. Use when the
  user runs /onboarding or starts a new viral content project.
disable-model-invocation: true
---

# Onboarding

Create a new project profile for viral content automation. Be conversational — offer yes/no confirmations and examples from prior answers or website analysis.

## Before you start

1. Check existing projects: `python scripts/profile_store.py list`
2. If user wants a new project, proceed. If they want to edit an existing one, load that profile instead.

## Workflow

Copy and track:

```
Onboarding Progress:
- [ ] i) Product / Service / project (required)
- [ ] ii) Target audience (optional)
- [ ] iii) Features or service types (optional)
- [ ] iv) Competitors (optional)
- [ ] v) Positioning (optional)
- [ ] vi) Content exclusions (optional)
- [ ] vii) Content inclusions (optional)
- [ ] viii) Content types (required)
- [ ] Save profile.json
- [ ] Suggest next step
```

## Questions (use verbatim wording)

Ask in order. After each answer, summarize and confirm before moving on.

### i) Describe your Product / Service / project or paste your website (required)

If website pasted:
- Fetch and analyze the site (title, tagline, features, audience signals).
- Present inferred product description: "Based on [url], your product looks like: **[summary]**. Correct? (yes / edit)"
- Wait for confirmation or edits.

If no website:
- Accept freeform description.
- Ask: "Is this a **product**, **service**, or **project**?" with examples from their description.

### ii) What is your Target audiance? (optional)

If website was analyzed previously:
- Show: "From your site, your audience looks like: **[inferred]**. Keep this, or describe your target audience?"
- Offer yes/no to accept inferred audience.

If website not provided:
- Ask directly with examples tied to their product (e.g. "Solopreneurs posting on TikTok?" / "B2B SaaS founders?").

### iii) What are the Features of the product / project (if product / project selected), Types of services (If services selected) (optional)

If website was analyzed:
- Show inferred features/services list. "These features stood out: **[list]**. Keep, add, or replace?"

If not:
- Ask with 2–3 suggested features based on their description.

### iv) What are the competitors (mention website or name) give them the option to research If theyre not sure (optional)

- Accept names/URLs, or "not sure".
- If not sure: use web search to suggest 3–5 potential competitors. Present as: "**Competitor A** (site) — brief reason. Add any of these? (yes/no/edit)"
- Do not save competitors until user confirms.

### v) positioning (how do they want to potray their brand) (give few examples like quirky, fun, serious, humorous and based on their website)

If website analyzed:
- Suggest 2–3 styles from site tone: "Your site feels **[style]**. Pick one: quirky / fun / serious / humorous / select for me"

If not sure:
- Offer "select for me" — pick the best fit from product + audience and confirm.

### vi) anything that they want to exclude in the content (for example do not talk about competitors or campare competitors)? (optional)

- Give examples from their niche. Accept skip.

### vii) anything they want to include in the content (for example mock compeititors and generate hilarious memes)

- Give examples aligned with positioning. Accept skip.

### viii) Type of content - based on https://docs.magichour.ai/tools/video/text-to-video capablities

- Present content types mapped to platforms and Magic Hour params. See [content-types.md](references/content-types.md).
- For each selected type, confirm: platform(s), aspect ratio, duration, audio yes/no.
- Minimum one content type required.

## Save profile

After all questions confirmed:

```bash
python scripts/profile_store.py create \
  --name "<Project Name>" \
  --profile-json /tmp/profile_payload.json
```

Or write directly to `projects/<slug>/profile.json` following [profile.schema.json](../../schemas/profile.schema.json).

Create project folders:
- `research/`, `ideas/`, `calendar/`, `input/`, `output/`

Set `schema_version: "1.0.0"`, timestamps in ISO 8601.

## After onboarding

Ask:

> Onboarding complete! Your profile is saved at `projects/<slug>/profile.json`.
>
> What would you like next?
> 1. **Research content ideas** — `/research-ideas` (data-backed viral ideas)
> 2. **Brainstorm ideas** — `/brainstorm` (interactive creative session)

## Rules

- Never save unconfirmed inferences from website analysis.
- Keep questions short; embed examples from prior answers.
- One project folder per completed onboarding.
- Do not call Magic Hour API during onboarding.

## References

- [Question examples](references/questions.md)
- [Content type mapping](references/content-types.md)
