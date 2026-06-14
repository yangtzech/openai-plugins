# Claude Code Plugin Marketplace

This repository is also available as a [Claude Code](https://claude.ai/code) plugin marketplace.

## Quick Start

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
claude plugin marketplace add yangtzech/openai-plugins
claude plugin install figma@openai-plugins
```

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
