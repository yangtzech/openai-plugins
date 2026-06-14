#!/usr/bin/env python3
"""
Codex -> Claude Code plugin adapter.

Reads a Codex plugin (.codex-plugin/plugin.json) and generates the corresponding
Claude Code artifacts (.claude-plugin/plugin.json, agent frontmatter, hooks/)
in-place, so the same plugin directory works with both runtimes.

Usage:
    python3 scripts/codex2claude.py <plugin-path>            # adapt one plugin
    python3 scripts/codex2claude.py --all                     # adapt all plugins/
    python3 scripts/codex2claude.py <plugin-path> --dry-run   # preview only
    python3 scripts/codex2claude.py <plugin-path> --check     # check sync status
    python3 scripts/codex2claude.py --all --check             # batch check
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CODEX_MANIFEST = ".codex-plugin/plugin.json"
CLAUDE_MANIFEST = ".claude-plugin/plugin.json"
CODEX_HOOKS = "hooks.json"
CLAUDE_HOOKS_DIR = "hooks"
CLAUDE_HOOKS_FILE = "hooks/hooks.json"

# Fields from Codex plugin.json that map directly to Claude plugin.json
DIRECT_FIELDS = [
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "skills",
    "mcpServers",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def has_frontmatter(text: str) -> bool:
    """Check if a markdown file starts with YAML frontmatter (---)."""
    return text.lstrip().startswith("---")


def derive_agent_name(filename: str) -> str:
    """Derive a kebab-case agent name from a filename."""
    return Path(filename).stem


def infer_description_from_content(content: str, max_lines: int = 5) -> str:
    """Try to extract a short description from the first few lines of an agent .md file."""
    lines = content.strip().split("\n")
    for line in lines[:max_lines]:
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("Purpose:") or line.startswith("-"):
            continue
        desc = line.rstrip(".")
        if len(desc) > 120:
            desc = desc[:117] + "..."
        return desc
    return "Agent from Codex plugin"


def build_claude_manifest(codex: dict[str, Any], plugin_dir: Path) -> dict[str, Any]:
    """Build a Claude Code plugin.json from a Codex plugin.json."""
    claude: dict[str, Any] = {}

    for field in DIRECT_FIELDS:
        if field in codex:
            claude[field] = codex[field]

    # Fix hooks path: Codex uses hooks.json at root, Claude uses hooks/hooks.json
    if "hooks" in codex or (plugin_dir / CODEX_HOOKS).exists():
        claude["hooks"] = f"./{CLAUDE_HOOKS_FILE}"

    return claude


def add_agent_frontmatter(
    md_path: Path,
    openai_yaml: dict[str, Any] | None,
    dry_run: bool = False,
) -> str:
    """Add YAML frontmatter to an agent .md file if it doesn't have one."""
    content = md_path.read_text(encoding="utf-8")

    if has_frontmatter(content):
        return "skipped"

    agent_name = derive_agent_name(md_path.name)

    # Try to get description from openai.yaml
    description = ""
    if openai_yaml:
        iface = openai_yaml.get("interface", {})
        description = iface.get("short_description", "")

    if not description:
        description = infer_description_from_content(content)

    # Escape quotes in description
    description = description.replace('"', '\\"')

    frontmatter_lines = [
        "---",
        f"name: {agent_name}",
        f'description: "{description}"',
        "---",
        "",
    ]
    new_content = "\n".join(frontmatter_lines) + content

    if not dry_run:
        md_path.write_text(new_content, encoding="utf-8")

    return "updated"


def _simple_yaml_parse(path: Path) -> dict[str, Any]:
    """Minimal YAML parser for the simple openai.yaml structure."""
    text = path.read_text(encoding="utf-8")
    result: dict[str, Any] = {}
    current_section: dict[str, Any] | None = None

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())

        if indent == 0 and ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val:
                result[key] = val
            else:
                current_section = {}
                result[key] = current_section
        elif indent > 0 and current_section is not None and ":" in stripped:
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            current_section[key] = val

    iface = result.get("interface", {})
    if isinstance(iface, dict):
        return {"interface": iface}
    return {}


def process_agents(plugin_dir: Path, dry_run: bool = False) -> list[tuple[str, str]]:
    """Process agents/ directory: add frontmatter to .md files."""
    agents_dir = plugin_dir / "agents"
    if not agents_dir.is_dir():
        return []

    # Read openai.yaml if present
    openai_yaml_path = agents_dir / "openai.yaml"
    openai_yaml = None
    if openai_yaml_path.exists():
        try:
            import yaml  # type: ignore
            openai_yaml = yaml.safe_load(openai_yaml_path.read_text(encoding="utf-8"))
        except ImportError:
            openai_yaml = _simple_yaml_parse(openai_yaml_path)
        except Exception:
            openai_yaml = None

    results: list[tuple[str, str]] = []
    for md_file in sorted(agents_dir.glob("*.md")):
        status = add_agent_frontmatter(md_file, openai_yaml, dry_run)
        results.append((md_file.name, status))

    return results


def process_hooks(plugin_dir: Path, dry_run: bool = False) -> str:
    """Copy hooks.json to hooks/hooks.json if it exists."""
    src = plugin_dir / CODEX_HOOKS
    if not src.exists():
        return "none"

    dst_dir = plugin_dir / CLAUDE_HOOKS_DIR
    dst = plugin_dir / CLAUDE_HOOKS_FILE

    src_content = src.read_text(encoding="utf-8")
    # Replace ./scripts/ paths with ${CLAUDE_PLUGIN_ROOT}/scripts/
    adapted = src_content.replace('"./scripts/', '"${CLAUDE_PLUGIN_ROOT}/scripts/')

    if dst.exists():
        existing = dst.read_text(encoding="utf-8")
        if existing == adapted:
            return "skipped"
        if not dry_run:
            dst.write_text(adapted, encoding="utf-8")
        return "updated"
    else:
        if not dry_run:
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst.write_text(adapted, encoding="utf-8")
        return "created"


def adapt_plugin(plugin_dir: Path, dry_run: bool = False) -> dict[str, Any]:
    """Adapt a single Codex plugin to also work as a Claude Code plugin."""
    plugin_dir = plugin_dir.resolve()
    codex_manifest_path = plugin_dir / CODEX_MANIFEST
    claude_manifest_path = plugin_dir / CLAUDE_MANIFEST

    report: dict[str, Any] = {
        "plugin": plugin_dir.name,
        "path": str(plugin_dir),
        "manifest": None,
        "agents": [],
        "hooks": None,
    }

    if not codex_manifest_path.exists():
        report["error"] = f"No Codex manifest found at {codex_manifest_path}"
        return report

    codex = read_json(codex_manifest_path)
    claude = build_claude_manifest(codex, plugin_dir)

    if claude_manifest_path.exists():
        existing = read_json(claude_manifest_path)
        if existing == claude:
            report["manifest"] = "unchanged"
        else:
            report["manifest"] = "updated"
            if not dry_run:
                write_json(claude_manifest_path, claude)
    else:
        report["manifest"] = "created"
        if not dry_run:
            write_json(claude_manifest_path, claude)

    report["agents"] = process_agents(plugin_dir, dry_run)
    report["hooks"] = process_hooks(plugin_dir, dry_run)

    return report


def check_plugin_sync(plugin_dir: Path) -> dict[str, Any]:
    """Check if a plugin's Claude artifacts are in sync with its Codex source."""
    plugin_dir = plugin_dir.resolve()
    codex_manifest_path = plugin_dir / CODEX_MANIFEST
    claude_manifest_path = plugin_dir / CLAUDE_MANIFEST

    report: dict[str, Any] = {
        "plugin": plugin_dir.name,
        "in_sync": True,
        "issues": [],
    }

    if not codex_manifest_path.exists():
        report["issues"].append("No Codex manifest")
        report["in_sync"] = False
        return report

    if not claude_manifest_path.exists():
        report["issues"].append("No Claude manifest (not adapted)")
        report["in_sync"] = False
        return report

    codex = read_json(codex_manifest_path)
    claude = read_json(claude_manifest_path)
    expected = build_claude_manifest(codex, plugin_dir)

    if claude != expected:
        report["issues"].append("Claude manifest differs from expected")
        report["in_sync"] = False

    # Check agents
    agents_dir = plugin_dir / "agents"
    if agents_dir.is_dir():
        for md_file in agents_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            if not has_frontmatter(content):
                report["issues"].append(f"Agent {md_file.name} lacks frontmatter")
                report["in_sync"] = False

    # Check hooks
    src_hooks = plugin_dir / CODEX_HOOKS
    dst_hooks = plugin_dir / CLAUDE_HOOKS_FILE
    if src_hooks.exists() and not dst_hooks.exists():
        report["issues"].append("hooks.json not migrated to hooks/hooks.json")
        report["in_sync"] = False

    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def find_all_plugins(repo_root: Path) -> list[Path]:
    """Find all plugin directories under plugins/."""
    plugins_dir = repo_root / "plugins"
    if not plugins_dir.is_dir():
        return []
    return sorted(
        p for p in plugins_dir.iterdir()
        if p.is_dir() and (p / CODEX_MANIFEST).exists()
    )


def print_report(report: dict[str, Any]) -> None:
    """Print an adaptation report."""
    name = report.get("plugin", "?")

    if "error" in report:
        print(f"  [{name}] ERROR: {report['error']}")
        return

    manifest_status = report.get("manifest", "?")
    symbols = {"created": "[+]", "updated": "[~]", "unchanged": "[=]"}
    print(f"  {symbols.get(manifest_status, '[?]')} manifest: {manifest_status}")

    for agent_name, status in report.get("agents", []):
        sym = {"updated": "[+]", "skipped": "[=]"}.get(status, "[?]")
        print(f"  {sym} agent {agent_name}: {status}")

    hooks_status = report.get("hooks")
    if hooks_status and hooks_status != "none":
        sym = {"created": "[+]", "updated": "[~]", "skipped": "[=]"}.get(hooks_status, "[?]")
        print(f"  {sym} hooks: {hooks_status}")


def print_check_report(report: dict[str, Any]) -> None:
    """Print a sync check report."""
    name = report.get("plugin", "?")
    if report["in_sync"]:
        print(f"  [ok] {name}")
    else:
        print(f"  [!!] {name}")
        for issue in report["issues"]:
            print(f"       - {issue}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Adapt Codex plugins to also work as Claude Code plugins.",
    )
    parser.add_argument(
        "plugin_path",
        nargs="?",
        help="Path to a single plugin directory",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all plugins under plugins/",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check sync status instead of adapting",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: auto-detect from script location)",
    )

    args = parser.parse_args()

    # Determine repo root
    if args.repo_root:
        repo_root = args.repo_root.resolve()
    else:
        repo_root = Path(__file__).resolve().parent.parent

    if not args.plugin_path and not args.all:
        parser.error("Provide a plugin path or use --all")

    # Collect plugin directories
    if args.all:
        plugins = find_all_plugins(repo_root)
        if not plugins:
            print(f"No plugins found under {repo_root / 'plugins'}")
            sys.exit(1)
        print(f"Found {len(plugins)} plugins\n")
    else:
        plugins = [Path(args.plugin_path).resolve()]

    # Process
    adapted = 0
    errors = 0
    in_sync = 0
    out_of_sync = 0

    for plugin_dir in plugins:
        name = plugin_dir.name

        if args.check:
            report = check_plugin_sync(plugin_dir)
            print_check_report(report)
            if report["in_sync"]:
                in_sync += 1
            else:
                out_of_sync += 1
        else:
            print(f"{'[dry-run] ' if args.dry_run else ''}{name}")
            report = adapt_plugin(plugin_dir, dry_run=args.dry_run)
            print_report(report)

            if "error" in report:
                errors += 1
            else:
                adapted += 1
            print()

    # Summary
    print("---")
    if args.check:
        print(f"In sync: {in_sync}, Out of sync: {out_of_sync}, Total: {len(plugins)}")
    else:
        mode = "dry-run" if args.dry_run else "adapted"
        print(f"{mode}: {adapted}, errors: {errors}, total: {len(plugins)}")


if __name__ == "__main__":
    main()
