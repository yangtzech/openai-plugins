---
name: claude-code-plugin-creator
description: "Create, scaffold, and validate Claude Code plugins with skills, agents, hooks, MCP servers, LSP servers, monitors, and more. Use when the user needs to create a new Claude Code plugin, add plugin structure, or convert standalone `.claude/` configuration into a distributable plugin."
---

# Claude Code Plugin Creator

Create, scaffold, and validate Claude Code plugins.

## Before you start

Run the doc-update script to ensure you have the latest Claude Code plugin documentation:

```bash
bash plugins/claude-code-plugin-creator/scripts/update-docs.sh
```

Then **read the relevant reference files** before writing any plugin code:

| Task | Read this |
|---|---|
| Create a plugin | `plugins/claude-code-plugin-creator/references/plugins.md` |
| Manifest fields | `plugins/claude-code-plugin-creator/references/plugins-reference.md` |
| Write skills | `plugins/claude-code-plugin-creator/references/skills.md` |
| Write agents | `plugins/claude-code-plugin-creator/references/sub-agents.md` |
| Write hooks | `plugins/claude-code-plugin-creator/references/hooks.md` |
| Set up MCP | `plugins/claude-code-plugin-creator/references/plugins-reference.md` |
| Distribute | `plugins/claude-code-plugin-creator/references/plugin-marketplaces.md` |
| Plugin dependencies | `plugins/claude-code-plugin-creator/references/plugin-dependencies.md` |

## Quick Start

### Scaffold a new plugin

```bash
python3 plugins/claude-code-plugin-creator/scripts/create_plugin.py <plugin-name>
```

Options:
- `--path <dir>` — Parent directory (default: `~/plugins`)
- `--description <text>` — Plugin description
- `--with <components...>` — `skills`, `agents`, `hooks`, `scripts`, `mcp`, `lsp`, `monitors`, `assets`, `bin`, `settings`
- `--force` — Overwrite existing

### Test locally

```bash
claude --plugin-dir ./plugins/<plugin-name>
```

### Validate

```bash
claude plugin validate ./plugins/<plugin-name>
claude plugin validate ./plugins/<plugin-name> --strict
```

## Plugin structure

```
<plugin-name>/
├── .claude-plugin/plugin.json  # Manifest (required)
├── skills/<name>/SKILL.md      # Skills
├── commands/*.md               # Flat .md skill files (legacy)
├── agents/*.md                 # Subagent definitions
├── hooks/hooks.json            # Event handlers
├── scripts/                    # Hook and utility scripts
├── bin/                        # Executables added to PATH
├── monitors/monitors.json      # Background monitors
├── themes/                     # Color themes
├── output-styles/              # Output style definitions
├── settings.json               # Default settings when enabled
├── .mcp.json                   # MCP server config
├── .lsp.json                   # LSP server config
└── assets/                     # Icons, logos
```

**Only `plugin.json` goes inside `.claude-plugin/`.** All other directories at plugin root.

## Manifest (`plugin.json`)

Only `name` is required. Read `plugins/claude-code-plugin-creator/references/plugins-reference.md` for all fields.

```json
{
  "name": "my-plugin",
  "displayName": "My Plugin",
  "version": "1.0.0",
  "description": "What it does",
  "author": { "name": "Author", "email": "email@example.com" },
  "skills": "./skills/",
  "agents": ["./agents/reviewer.md"],
  "hooks": "./hooks/hooks.json",
  "mcpServers": "./.mcp.json",
  "lspServers": "./.lsp.json",
  "experimental": { "monitors": "./monitors.json" },
  "userConfig": {},
  "dependencies": []
}
```

## Skills

Each skill is a folder with `SKILL.md`:

```markdown
---
name: skill-name
description: "What this skill does and when to use it"
---

Instructions here. Use $ARGUMENTS for user input.
```

- Folder name becomes skill name, prefixed with plugin namespace: `/plugin-name:skill-name`
- `description` is required for model-invoked skills
- `disable-model-invocation: true` makes it user-invoked only

## Agents

Markdown files with YAML frontmatter:

```markdown
---
name: agent-name
description: "What this agent does"
model: sonnet
effort: medium
maxTurns: 20
disallowedTools: Write, Edit
---

Agent system prompt.
```

## Hooks

`hooks/hooks.json` responds to lifecycle events:

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{ "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/lint.sh" }]
    }]
  }
}
```

Hook types: `command`, `http`, `mcp_tool`, `prompt`, `agent`.

## Environment variables

| Variable | Description |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}` | Plugin installation directory |
| `${CLAUDE_PLUGIN_DATA}` | Persistent data directory (survives updates) |
| `${CLAUDE_PROJECT_DIR}` | Project root |
| `${user_config.KEY}` | User-configured values |

## Testing and debugging

```bash
claude --plugin-dir ./my-plugin          # load for one session
/reload-plugins                          # reload after changes
claude --debug                           # see plugin loading details
claude plugin validate ./my-plugin       # validate structure
claude plugin validate ./my-plugin --strict  # strict mode
```

## CLI commands

```bash
claude plugin init <name> [--with ...]   # scaffold into ~/.claude/skills/
claude plugin install <plugin>           # from marketplace
claude plugin uninstall <plugin>
claude plugin list [--json]
claude plugin enable/disable <plugin>
claude plugin details <plugin>
claude plugin update <plugin>
claude plugin tag [--push]               # create release tag
claude plugin prune                      # remove orphaned dependencies
```

## Distribution

1. Validate: `claude plugin validate`
2. Create or use a marketplace (see `plugins/claude-code-plugin-creator/references/plugin-marketplaces.md`)
3. Submit to community marketplace via claude.ai or Console

## Convert standalone to plugin

1. Create plugin directory and manifest
2. Copy from `.claude/`: `commands/`, `agents/`, `skills/`
3. Migrate hooks from `settings.json` to `hooks/hooks.json`
4. Test with `claude --plugin-dir`
5. Remove originals from `.claude/`
