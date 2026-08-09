# Proven Viral Content Automation

**Research**, **brainstorm**, and **generate** viral video content for Instagram, YouTube, X, and TikTok.

Works with **Cursor**, **Claude Code**, **Codex**, **Antigravity**, **OpenCode**, **Hermes**, and **OpenClaw**.

## What you get

Four conversational skills that guide you from brand setup to published-ready video:

| Skill | What it does |
|-------|--------------|
| `/onboarding` | Conversational Q&A → saves `projects/<slug>/profile.json` |
| `/research-ideas` | Source-backed viral content research per platform |
| `/brainstorm` | Interactive ideation; updates content preferences |
| `/generate` | Detailed prompts → Magic Hour API → downloaded MP4 |

## Quick start

```bash
git clone https://github.com/swaroop2004/Proven-Viral-Content-System.git
cd Proven-Viral-Content-Automation
cp .env.example .env
python scripts/magichour_video.py check-key
```

Open in your AI agent and run `/onboarding`.

Full setup: **[docs/setup.md](docs/setup.md)**

## Example workflow

```
/onboarding  →  /research-ideas  →  /generate
/onboarding  →  /brainstorm      →  /generate
/research-ideas  →  /generate
/generate  →  /generate  (create more)
```

## Preview without spending credits

```bash
python scripts/magichour_video.py preview \
  --project _example \
  --idea ideas/idea-001.json
```

## Project structure

```
.agents/skills/          # Canonical skills (onboarding, research-ideas, brainstorm, generate)
.claude/skills/          # Claude Code adapters
.agents/workflows/       # Antigravity slash workflows
.opencode/commands/      # OpenCode slash commands
scripts/                 # Python helpers (profile + Magic Hour API)
projects/                # User project workspaces (gitignored except _example)
schemas/                 # profile.json JSON schema
docs/                    # Setup and compatibility guide
AGENTS.md                # Persistent agent instructions
```

## Magic Hour

Get your [Magic Hour](https://manicule.link/srp) API key for video generation. Use coupon code **`FIRSTAPI`** for free credits.

- Copy the key into `.env` as `MAGIC_HOUR_API_KEY`
- **Docs MCP** (optional, documentation only): `https://docs.magichour.ai/mcp`

## License

MIT — Free to use and distribute
