"""CLI entrypoint for ADG Prompt Assembly.

Usage:
    python -m tools.adg.prompt_assembly --packet executive_summary
    python -m tools.adg.prompt_assembly --packet determinism_rca --format markdown
    python -m tools.adg.prompt_assembly --all
    python -m tools.adg.prompt_assembly --packet hotspot --sqlite path/to/db.sqlite
    python -m tools.adg.prompt_assembly --list
    python -m tools.adg.prompt_assembly --packet ratchet_review --output artifacts/adg/packets/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.adg.prompt_assembly.packets.builders import build_packet
from tools.adg.prompt_assembly.packets.registry import list_packet_types


def _write_output(envelope_data: str, output_dir: Path | None, filename: str) -> None:
    """Write output to file or stdout."""
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / filename
        out_path.write_text(envelope_data, encoding="utf-8")
        print(f"[prompt_assembly] Written: {out_path}")
    else:
        print(envelope_data)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="prompt_assembly",
        description="ADG Prompt Assembly — build structured prompt packets from ADG results.",
    )
    parser.add_argument(
        "--packet",
        type=str,
        help="Packet type to build (e.g. executive_summary, determinism_rca).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Build all packet types for the latest ADG run.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all registered packet types and exit.",
    )
    parser.add_argument(
        "--sqlite",
        type=str,
        default=None,
        help="Path to ADG SQLite file (auto-detected if omitted).",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "markdown"],
        default="json",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory for packet files (stdout if omitted).",
    )
    parser.add_argument(
        "--from-node",
        type=str,
        default="",
        help="Source node for graph_path_explanation packet.",
    )
    parser.add_argument(
        "--to-node",
        type=str,
        default="",
        help="Target node for graph_path_explanation packet.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=15,
        help="Top-N count for hotspot_investigation packet (default: 15).",
    )

    args = parser.parse_args()

    # --list: print types and exit
    if args.list:
        types = list_packet_types()
        print("Registered packet types:")
        for t in types:
            print(f"  - {t}")
        sys.exit(0)

    # Validate args
    if not args.packet and not args.all:
        parser.error("Must specify --packet <type> or --all")

    sqlite_path = Path(args.sqlite) if args.sqlite else None
    output_dir = Path(args.output) if args.output else None

    # Determine which packets to build
    if args.all:
        types_to_build = list_packet_types()
    else:
        valid_types = list_packet_types()
        if args.packet not in valid_types:
            print(
                f"[ERROR] Unknown packet type: {args.packet!r}. Valid types: {valid_types}",
                file=sys.stderr,
            )
            sys.exit(1)
        types_to_build = [args.packet]

    # Build and output
    for ptype in types_to_build:
        try:
            kwargs: dict = {}
            if ptype == "graph_path_explanation":
                kwargs["from_node"] = args.from_node
                kwargs["to_node"] = args.to_node
            if ptype == "hotspot_investigation":
                kwargs["top_n"] = args.top_n

            envelope = build_packet(
                ptype,
                sqlite_path=sqlite_path,
                graph=None,
                **kwargs,
            )

            if args.format == "markdown":
                output = envelope.to_markdown()
                ext = "md"
            else:
                output = envelope.to_json(indent=2)
                ext = "json"

            _write_output(output, output_dir, f"packet_{ptype}.{ext}")

        except ValueError as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            sys.exit(1)
        except (
            Exception
        ) as e:  # guardian: allow-broad-exception -- CLI top-level catch for user-facing error messages
            print(f"[ERROR] Failed to build {ptype}: {e}", file=sys.stderr)
            sys.exit(1)

    if args.all:
        print(f"[prompt_assembly] Built {len(types_to_build)} packets.")


if __name__ == "__main__":
    main()
