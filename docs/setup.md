# Setup Guide

Complete setup for **Proven Viral Content Automation** across supported AI coding agents.

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Python 3.10+** | For profile and generation helpers |
| **Magic Hour API key** | Required for `/generate` — [Magic Hour](https://manicule.link/srp) (coupon **`FIRSTAPI`** for free credits) |
| **Git** | Clone this repository |

No pip dependencies — helpers use Python standard library only.

## 1. Clone and configure

```bash
git clone <your-repo-url>
cd Proven-Viral-Content-Automation
cp .env.example .env   # Windows: copy .env.example .env
```

Edit `.env`:

```
MAGIC_HOUR_API_KEY=your_actual_key_here
```

Get your key from [Magic Hour](https://manicule.link/srp). Use coupon code **`FIRSTAPI`** for free credits.

Verify:

```bash
python scripts/magichour_video.py check-key
```

## 2. Explore the example project

An example profile and idea ship with the repo:

```
projects/_example/
├── profile.json
└── ideas/idea-001.json
```

Preview generation (no API call, no credits):

```bash
python scripts/magichour_video.py preview --project _example --idea ideas/idea-001.json
```

## 3. Run your first workflow

Open the repo in your AI agent and run:

1. **`/onboarding`** — create your brand profile
2. **`/research-ideas`** or **`/brainstorm`** — develop content ideas
3. **`/generate`** — create videos (requires API key + spend confirmation)

---

## Per-agent setup

### Cursor

Skills in `.agents/skills/` are discovered automatically.

```
/onboarding
/research-ideas
/brainstorm
/generate
```

Optional: add Magic Hour **docs MCP** in Cursor MCP settings:

```json
{
  "mcpServers": {
    "Magic Hour": {
      "url": "https://docs.magichour.ai/mcp"
    }
  }
}
```

This provides live API documentation — **not video generation**.

### Claude Code

1. Open repo root.
2. `CLAUDE.md` imports `AGENTS.md` automatically.
3. Skills available via `.claude/skills/` adapters → canonical `.agents/skills/`.

```bash
/onboarding
```

Add docs MCP:

```bash
claude mcp add --transport http MagicHour https://docs.magichour.ai/mcp
```

### OpenAI Codex

1. Open repo root — Codex reads `AGENTS.md`.
2. Skills discovered from `.agents/skills/`.
3. Invoke with `$onboarding`, `$research-ideas`, `$brainstorm`, `$generate`.

### Google Antigravity

1. Open repo root.
2. Rules: `.agents/rules/repository.md` → `AGENTS.md`.
3. Workflows: `.agents/workflows/*.md` for slash commands.
4. Skills: `.agents/skills/`.

### OpenCode

1. Open repo root — reads `AGENTS.md`.
2. Slash commands: `.opencode/commands/*.md`.
3. Skills also available via native skill tool from `.agents/skills/`.

### Hermes Agent

Add this repo's skills directory to `~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - /absolute/path/to/Proven-Viral-Content-Automation/.agents/skills
```

Persistent instructions: Hermes reads `AGENTS.md` from the repo.

### OpenClaw

Set this repository as your OpenClaw workspace. Skills discovered from `.agents/skills/` (or `skills/` with higher precedence).

Workspace files: `AGENTS.md` loaded automatically.

---

## Magic Hour integration

Get your [Magic Hour](https://manicule.link/srp) API key to enable `/generate`. Use coupon code **`FIRSTAPI`** for free credits.

### API (required for generation)

| Endpoint | Purpose |
|----------|---------|
| `POST /v1/text-to-video` | Create video job |
| `GET /v1/video-projects/{id}` | Poll status + download URL |

Generation flow:

```bash
# Preview (free)
python scripts/magichour_video.py preview --project <slug> --idea ideas/<file>.json

# Generate (billable — requires confirmation flag)
python scripts/magichour_video.py generate --project <slug> --idea ideas/<file>.json --confirm-spend
```

### MCP (optional — documentation only)

The official Magic Hour MCP server exposes **documentation**, not generation APIs.

Use it when you need current model lists, parameter constraints, or pricing docs during a session.

**Do not** configure MCP as a substitute for `MAGIC_HOUR_API_KEY`.

---

## Project data layout

```
projects/<slug>/
├── profile.json       # Brand profile + content preferences
├── research/          # Dated research reports (.md)
├── ideas/             # Content ideas (.json)
├── calendar/          # Optional posting calendar
├── input/             # User assets (logos, screenshots)
└── output/            # Generated videos + manifests
    └── 20260808T120000Z/
        ├── manifest.json
        └── output.mp4
```

User project folders (except `_example`) are gitignored by default.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `MAGIC_HOUR_API_KEY is not configured` | Copy `.env.example` → `.env`, get key from [Magic Hour](https://manicule.link/srp) (coupon **`FIRSTAPI`**) |
| `401 Unauthorized` | Invalid or expired API key |
| `402 Payment Required` | Insufficient credits — [add credits](https://magichour.ai/pricing) |
| `422 Unprocessable` | Invalid model/duration/resolution combo — check Magic Hour docs |
| `end_seconds not supported` | Pick a duration allowed for the selected model |
| `Refusing to generate without --confirm-spend` | Agent must get your explicit yes before calling generate |
| Skills not found | Ensure repo root is workspace; check `.agents/skills/` exists |
| Windows path issues | Use forward slashes in commands; avoid symlinks |

---

## Privacy

- `.env` and user `projects/*/` data stay local (gitignored).
- Never commit API keys.
- Website analysis during onboarding uses public page content only.
- Generation manifests exclude the API key.

---

## Credit usage transparency

- There is **no estimate-only API**. Pre-generation estimates are labeled **best-effort**.
- Initial credits appear in the create response; final credits may differ after render.
- Failed jobs are refunded per Magic Hour policy.
- Use the [API cost calculator](https://magichour.ai/api#api-cost-calculator) for planning.
