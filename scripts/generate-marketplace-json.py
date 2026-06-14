#!/usr/bin/env python3
"""
Generate .claude-plugin/marketplace.json for the openai-plugins repository.

This script scans all plugins and generates a marketplace.json file that
Claude Code can consume natively via:
    /plugin marketplace add yangtzech/openai-plugins

Usage:
    python3 scripts/generate-marketplace-json.py
    python3 scripts/generate-marketplace-json.py --dry-run
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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def read_json(path: Path) -> dict[str, Any]:
    """Read and parse a JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def extract_plugin_metadata(plugin_dir: Path) -> dict[str, Any] | None:
    """Extract metadata from a plugin directory.

    Only reads .claude-plugin/plugin.json. If only .codex-plugin exists,
    returns None so the caller can log an actionable error.
    """
    claude_path = plugin_dir / CLAUDE_MANIFEST

    if claude_path.exists():
        return read_json(claude_path)
    else:
        return None


def generate_marketplace_json(
    repo_root: Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Generate the marketplace.json content from all plugins."""
    plugins_dir = repo_root / "plugins"
    if not plugins_dir.is_dir():
        print(f"Error: plugins/ directory not found at {plugins_dir}")
        sys.exit(1)

    marketplace: dict[str, Any] = {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": "openai-plugins",
        "description": "Curated collection of 174+ Codex plugins for Claude Code — covering developer tools, productivity, communication, finance, design, data analytics, AI/ML, and more.",
        "owner": {
            "name": "OpenAI",
            "url": "https://openai.com"
        },
        "plugins": [],
    }

    stats = {
        "total": 0,
        "processed": 0,
        "skipped": 0,
        "errors": [],
    }

    # Process each plugin
    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue

        stats["total"] += 1
        metadata = extract_plugin_metadata(plugin_dir)

        if metadata is None:
            stats["skipped"] += 1
            codex_path = plugin_dir / CODEX_MANIFEST
            if codex_path.exists():
                stats["errors"].append(
                    f"{plugin_dir.name}: Only .codex-plugin found, run `codex2claude.py` first"
                )
            else:
                stats["errors"].append(f"{plugin_dir.name}: No manifest found")
            continue

        plugin_name = metadata.get("name", plugin_dir.name)

        try:
            # Extract interface metadata
            interface = metadata.get("interface", {})

            # Build plugin entry
            entry: dict[str, Any] = {
                "name": plugin_name,
                "description": metadata.get("description", ""),
                "source": f"./plugins/{plugin_dir.name}",
            }

            # Add optional fields if present
            if metadata.get("version"):
                entry["version"] = metadata["version"]

            if metadata.get("author"):
                entry["author"] = metadata["author"]

            if metadata.get("keywords"):
                entry["keywords"] = metadata["keywords"]

            if interface.get("category"):
                entry["category"] = interface["category"].lower().replace(" ", "-")

            if metadata.get("homepage"):
                entry["homepage"] = metadata["homepage"]

            if interface.get("brandColor"):
                entry["brandColor"] = interface["brandColor"]

            marketplace["plugins"].append(entry)
            stats["processed"] += 1

        except Exception as e:
            stats["skipped"] += 1
            stats["errors"].append(f"{plugin_name}: {e}")

    return marketplace, stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate .claude-plugin/marketplace.json for openai-plugins.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root (default: auto-detect from script location)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be generated without writing files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path (default: <repo-root>/.claude-plugin/marketplace.json)",
    )

    args = parser.parse_args()

    # Determine repo root
    if args.repo_root:
        repo_root = args.repo_root.resolve()
    else:
        repo_root = Path(__file__).resolve().parent.parent

    # Determine output path
    if args.output:
        output_path = args.output.resolve()
    else:
        output_path = repo_root / ".claude-plugin" / "marketplace.json"

    print(f"Repository root: {repo_root}")
    print(f"Output file: {output_path}")
    print(f"Mode: {'dry-run' if args.dry_run else 'generate'}")
    print()

    marketplace, stats = generate_marketplace_json(repo_root, dry_run=args.dry_run)

    print(f"Found {stats['total']} plugins")
    print(f"  - Processed: {stats['processed']}")
    print(f"  - Skipped: {stats['skipped']}")

    if stats["errors"]:
        print(f"\nErrors:")
        for error in stats["errors"]:
            print(f"  - {error}")

    if args.dry_run:
        print(f"\n[DRY-RUN] Would generate marketplace.json with {len(marketplace['plugins'])} plugins")
        print("\nFirst 5 plugins:")
        for plugin in marketplace["plugins"][:5]:
            print(f"  - {plugin['name']}: {plugin['description'][:60]}...")
        print(f"  ... and {len(marketplace['plugins']) - 5} more")
    else:
        write_json(output_path, marketplace)
        print(f"\n✓ Generated marketplace.json with {len(marketplace['plugins'])} plugins")
        print(f"  Written to: {output_path}")
        print()
        print("Users can now add this marketplace with:")
        print("  /plugin marketplace add yangtzech/openai-plugins")


if __name__ == "__main__":
    main()
