#!/usr/bin/env python3
"""
Scaffold a new Claude Code plugin directory with manifest and optional components.

Usage:
    python3 create_plugin.py <plugin-name> [options]
    python3 create_plugin.py my-tool
    python3 create_plugin.py my-tool --path ./plugins --with skills agents hooks mcp
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

VALID_COMPONENTS = [
    "skills", "agents", "hooks", "scripts", "mcp", "lsp",
    "monitors", "assets", "bin", "settings",
]


def normalize_name(name: str) -> str:
    s = re.sub(r"[_\s\.　]+", "-", name)
    s = re.sub(r"[^a-zA-Z0-9\-]", "", s)
    s = re.sub(r"-{2,}", "-", s)
    s = s.strip("-").lower()
    if len(s) > 64:
        s = s[:64].rstrip("-")
    return s or "unnamed-plugin"


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_plugin(
    name: str,
    path: Path,
    description: str = "",
    author_name: str = "",
    author_email: str = "",
    components: list[str] | None = None,
    force: bool = False,
) -> Path:
    normalized = normalize_name(name)
    plugin_dir = path / normalized
    components = components or []

    if plugin_dir.exists() and not force:
        if (plugin_dir / ".claude-plugin" / "plugin.json").exists():
            print(f"Plugin already exists at {plugin_dir}. Use --force to overwrite.")
            sys.exit(1)

    plugin_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n{normalized}")

    # Manifest
    author: dict[str, str] = {}
    if author_name:
        author["name"] = author_name
    if author_email:
        author["email"] = author_email
    if not author:
        author["name"] = "[TODO: Author Name]"

    manifest = {
        "name": normalized,
        "version": "1.0.0",
        "description": description or f"[TODO: Describe {normalized}]",
        "author": author,
    }
    write_json(plugin_dir / ".claude-plugin" / "plugin.json", manifest)
    print("  [+] .claude-plugin/plugin.json")

    # Default skill
    write_file(plugin_dir / "skills" / normalized / "SKILL.md", f"""---
name: {normalized}
description: "[TODO: Describe what this skill does and when to use it]"
---

# {normalized.replace('-', ' ').title()}

[TODO: Write skill instructions here.]

Use $ARGUMENTS to accept user input after the skill name.
""")
    print(f"  [+] skills/{normalized}/SKILL.md")

    # Optional components
    if "skills" in components:
        write_file(plugin_dir / "skills" / "example" / "SKILL.md", f"""---
name: example
description: "[TODO: Describe the example skill]"
---

# Example Skill

This is an example skill for the {normalized} plugin.

[TODO: Write skill instructions here.]
""")
        print("  [+] skills/example/SKILL.md")

    if "agents" in components:
        write_file(plugin_dir / "agents" / "reviewer.md", """---
name: reviewer
description: "[TODO: Describe what this agent specializes in and when Claude should invoke it]"
model: sonnet
effort: medium
---

You are a code reviewer agent.

[TODO: Describe the agent's role, expertise, and behavior in detail.]
""")
        print("  [+] agents/reviewer.md")

    if "hooks" in components:
        write_json(plugin_dir / "hooks" / "hooks.json", {
            "hooks": {
                "PostToolUse": [{
                    "matcher": "Write|Edit",
                    "hooks": [{
                        "type": "command",
                        "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/lint.sh",
                    }],
                }]
            }
        })
        print("  [+] hooks/hooks.json")

    if "scripts" in components:
        lint = plugin_dir / "scripts" / "lint.sh"
        write_file(lint, """#!/usr/bin/env bash
# Example hook script: lint changed files.
# Input is provided as JSON on stdin via jq.
set -euo pipefail

FILE=$(jq -r '.tool_input.file_path // empty' 2>/dev/null || true)
if [ -n "$FILE" ]; then
  echo "Linting $FILE ..."
  # TODO: Add your lint command here
fi
""")
        lint.chmod(0o755)
        print("  [+] scripts/lint.sh")

    if "mcp" in components:
        write_json(plugin_dir / ".mcp.json", {
            "mcpServers": {
                f"{normalized}-server": {
                    "command": "${CLAUDE_PLUGIN_ROOT}/servers/my-server",
                    "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
                    "env": {"DATA_PATH": "${CLAUDE_PLUGIN_ROOT}/data"},
                }
            }
        })
        print("  [+] .mcp.json")

    if "lsp" in components:
        write_json(plugin_dir / ".lsp.json", {
            "example-language": {
                "command": "language-server",
                "args": ["serve"],
                "extensionToLanguage": {".ext": "example-language"},
            }
        })
        print("  [+] .lsp.json")

    if "monitors" in components:
        write_json(plugin_dir / "monitors" / "monitors.json", [{
            "name": "example-monitor",
            "command": "tail -F ./logs/app.log",
            "description": "[TODO: Describe what this monitor watches]",
        }])
        print("  [+] monitors/monitors.json")

    if "assets" in components:
        write_file(plugin_dir / "assets" / "README.md",
                    "# Assets\n\nPlace icons, logos, and screenshots here.\n")
        print("  [+] assets/")

    if "bin" in components:
        write_file(plugin_dir / "bin" / "README.md",
                    "# Bin\n\nPlace executables here. They are added to PATH while the plugin is enabled.\n")
        print("  [+] bin/")

    if "settings" in components:
        write_json(plugin_dir / "settings.json", {})
        print("  [+] settings.json")

    # README
    write_file(plugin_dir / "README.md", f"""# {normalized}

{description or '[TODO: Describe this plugin]'}

## Installation

```bash
claude --plugin-dir ./{normalized}
```

## Skills

<!-- List skills here -->

## Usage

<!-- Describe usage here -->
""")
    print("  [+] README.md")

    return plugin_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a new Claude Code plugin.")
    parser.add_argument("name", help="Plugin name (normalized to kebab-case)")
    parser.add_argument("--path", type=Path, default=Path.home() / "plugins",
                        help="Parent directory (default: ~/plugins)")
    parser.add_argument("--description", default="", help="Plugin description")
    parser.add_argument("--author-name", default="", help="Author name")
    parser.add_argument("--author-email", default="", help="Author email")
    parser.add_argument("--with", nargs="+", choices=VALID_COMPONENTS, default=[],
                        dest="components",
                        help=f"Components to scaffold: {', '.join(VALID_COMPONENTS)}")
    parser.add_argument("--force", action="store_true", help="Overwrite existing")
    args = parser.parse_args()

    plugin_dir = create_plugin(
        name=args.name, path=args.path, description=args.description,
        author_name=args.author_name, author_email=args.author_email,
        components=args.components, force=args.force,
    )

    print(f"\n---")
    print(f"Plugin created at: {plugin_dir}")
    print(f"\nNext steps:")
    print(f"  1. Edit {plugin_dir}/.claude-plugin/plugin.json")
    print(f"  2. Edit {plugin_dir}/skills/{normalize_name(args.name)}/SKILL.md")
    print(f"  3. Test: claude --plugin-dir {plugin_dir}")


if __name__ == "__main__":
    main()
