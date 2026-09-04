#!/usr/bin/env python3
"""Remove untyped blocks and reorder selected ARCHE entity blocks.

This keeps the existing Turtle block formatting intact by moving complete
subject blocks in text form instead of reparsing and reserializing the graph.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


TARGET_TYPES = ("Person", "Organisation", "Place")
TARGET_PATTERN = re.compile(
    r"(^|\n)\S+\s+a\s+arche:(?:Person|Organisation|Place)\s*;",
    re.MULTILINE,
)
TYPE_PATTERN = re.compile(r"(^|\n)\S+\s+(?:a|rdf:type)\s+\S+", re.MULTILINE)


def split_prefix_and_body(content: str) -> tuple[str, str]:
    marker = "\n\n"
    prefix_end = 0

    while content.startswith("@prefix ", prefix_end):
        line_end = content.find("\n", prefix_end)
        if line_end == -1:
            return content, ""
        prefix_end = line_end + 1

    while prefix_end < len(content) and content[prefix_end] in "\n\r":
        prefix_end += 1

    prefix = content[:prefix_end]
    body = content[prefix_end:]
    if prefix and not prefix.endswith(marker):
        prefix = prefix.rstrip("\n") + marker
    return prefix, body


def split_blocks(body: str) -> list[str]:
    stripped_body = body.strip()
    if not stripped_body:
        return []
    return re.split(r"\n\s*\n", stripped_body)


def is_target_block(block: str) -> bool:
    return bool(TARGET_PATTERN.search(block))


def has_rdf_type(block: str) -> bool:
    return bool(TYPE_PATTERN.search(block))


def remove_blocks_without_rdf_type(blocks: list[str]) -> tuple[list[str], int]:
    typed_blocks = [block for block in blocks if has_rdf_type(block)]
    removed_count = len(blocks) - len(typed_blocks)
    return typed_blocks, removed_count


def reorder_blocks(blocks: list[str]) -> list[str]:
    prioritized = [block for block in blocks if is_target_block(block)]
    remaining = [block for block in blocks if not is_target_block(block)]
    return prioritized + remaining


def reorder_turtle(content: str) -> tuple[str, int, int]:
    prefix, body = split_prefix_and_body(content)
    blocks = split_blocks(body)
    typed_blocks, removed_count = remove_blocks_without_rdf_type(blocks)
    ordered_blocks = reorder_blocks(typed_blocks)
    serialized_body = "\n\n".join(ordered_blocks)
    if serialized_body:
        serialized_body += "\n"
    moved_count = len([block for block in typed_blocks if is_target_block(block)])
    return f"{prefix}{serialized_body}", moved_count, removed_count


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description=(
            "Remove Turtle subject blocks without rdf:type and move blocks with "
            "rdf:type arche:Person, arche:Organisation, or arche:Place to the top."
        )
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=str(project_root / "rdf" / "arche_constants.ttl"),
        help="Input Turtle file. Defaults to rdf/arche_constants.ttl.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output Turtle file. Defaults to the input file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path

    content = input_path.read_text(encoding="utf-8")
    reordered, moved_count, removed_count = reorder_turtle(content)
    output_path.write_text(reordered, encoding="utf-8")

    print(
        f"Removed {removed_count} untyped blocks and moved {moved_count} blocks "
        f"with arche:{', arche:'.join(TARGET_TYPES)} to the top of {output_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
