# Plugins

This repository contains a curated collection of Codex plugin examples.

Each plugin lives under `plugins/<name>/` with a required
`.codex-plugin/plugin.json` manifest and optional companion surfaces such as
`skills/`, `.app.json`, `.mcp.json`, plugin-level `agents/`, `commands/`,
`hooks.json`, `assets/`, and other supporting files.

## Quick Start: Install Plugins via Marketplace

The easiest way to use these plugins is through the Claude Code marketplace:

```bash
# Add the marketplace (one-time, in Claude Code)
/plugin marketplace add yangtzech/openai-plugins

# Then install any plugin
/plugin install figma
/plugin install notion
/plugin install github
```

Alternatively, using the command line:

```bash
claude marketplace add yangtzech/openai-plugins
claude plugin install figma@openai-plugins
```

For more details, see [scripts/MARKETPLACE.md](scripts/MARKETPLACE.md) and the marketplace manifest at [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json).

## Highlighted Examples

Highlighted richer examples in this repo include:

- `plugins/figma` for `use_figma`, Code to Canvas, Code Connect, and design system rules
- `plugins/notion` for planning, research, meetings, and knowledge capture
- `plugins/build-ios-apps` for SwiftUI implementation, refactors, performance, and debugging
- `plugins/build-macos-apps` for macOS SwiftUI/AppKit workflows, build/run/debug loops, and packaging guidance
- `plugins/build-web-apps` for deployment, UI, payments, and database workflows
- `plugins/expo` for Expo and React Native apps, SDK upgrades, EAS workflows, and Codex Run actions
- `plugins/netlify`, `plugins/remotion`, and `plugins/google-slides` for additional public skill- and MCP-backed plugin bundles

## Available Plugins

This repository contains **174 plugins** across various categories:

- **Developer Tools**: github, circleci, cloudflare, vercel, netlify, render, supabase, neon-postgres, etc.
- **Productivity**: notion, asana, linear, clickup, monday-com, teamwork-com, etc.
- **Communication**: slack, teams, zoom, intercom, help-scout, etc.
- **Finance & CRM**: stripe, hubspot, pipedrive, salesforce, quickbooks, etc.
- **Design & Media**: figma, canva, picsart, shutterstock, remotion, etc.
- **Data & Analytics**: datadog, mixpanel, posthog, amplitude, etc.
- **AI & ML**: hugging-face, nvidia, openai-developers, etc.
- **And many more...**

See [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json) for the full list.

## Scripts

- `scripts/generate-marketplace-json.py` - Regenerate marketplace.json manifest
- `scripts/codex2claude.py` - Adapt Codex plugins to work with Claude Code
