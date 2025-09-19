"""Entry point for the ResearchDownload native messaging host.

This module is a placeholder implementation that demonstrates how the
native messaging host could be launched.  The real project should
replace the ``main`` function with the actual host logic that
communicates with the browser extension over stdin/stdout.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments for the host launcher."""
    parser = argparse.ArgumentParser(
        description=(
            "Launch the ResearchDownload native messaging host. "
            "This placeholder implementation simply echoes JSON input."
        )
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Optional path to a manifest file to display when starting.",
    )
    return parser.parse_args(argv)


def load_manifest(manifest_path: Path | None) -> dict[str, Any] | None:
    """Load a manifest if it exists.

    Parameters
    ----------
    manifest_path:
        The manifest file path that should be displayed.
    """
    if manifest_path is None:
        return None
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}", file=sys.stderr)
        return None
    try:
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Failed to decode manifest JSON: {exc}", file=sys.stderr)
        return None
    return manifest_data


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    manifest = load_manifest(args.manifest)
    if manifest:
        manifest_path = args.manifest if args.manifest else "(provided manifest)"
        print(f"Loaded manifest from {manifest_path}")
        print(json.dumps(manifest, indent=2))

    print(
        "ResearchDownload native host placeholder running. "
        "Provide implementation in native/researchdownload_host.py."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
