#!/usr/bin/env python3
"""Render RDF turtle files as a graph image.

This script loads the RDF files in the project, combines them into a single graph,
converts them to a DOT graph, and either renders a PNG/PDF image with Graphviz or
writes the DOT file as a fallback.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

from rdflib import BNode, Graph, Literal, URIRef


def default_rdf_files(project_root: Path) -> list[Path]:
    return [
        project_root / "meta" / "crawler.ttl",
        project_root / "rdf" / "test-arche_constants.ttl",
    ]


def safe_label(value: str) -> str:
    return value.replace('"', '\\"').replace('\\', '\\\\')


def term_id(term: object) -> str:
    raw = str(term)
    digest = hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]
    return f"n_{digest}"


def graph_to_dot(graph: Graph) -> str:
    lines = [
        "digraph RDFGraph {",
        "  rankdir=LR;",
        "  node [fontname=\"Helvetica\", fontsize=10];",
        "  edge [fontname=\"Helvetica\", fontsize=9];",
    ]

    nodes: set[str] = set()
    for subject, predicate, obj in graph:
        s_id = term_id(subject)
        p_id = term_id(predicate)
        o_id = term_id(obj)

        nodes.add(s_id)
        nodes.add(o_id)
        nodes.add(p_id)

        lines.append(f'  {s_id} [label="{safe_label(str(subject))}", shape="box"];')
        lines.append(f'  {p_id} [label="{safe_label(str(predicate))}", shape="ellipse", style="filled", fillcolor="lightgray"];')
        lines.append(f'  {o_id} [label="{safe_label(str(obj))}", shape="oval"];')
        lines.append(f'  {s_id} -> {o_id} [label="{safe_label(str(predicate))}"];')

    for node in sorted(nodes):
        if node.startswith("n_"):
            continue

    lines.append("}")
    return "\n".join(lines)


def load_graph(file_paths: list[Path]) -> Graph:
    graph = Graph()
    for file_path in file_paths:
        if not file_path.exists():
            raise FileNotFoundError(f"RDF file not found: {file_path}")
        graph.parse(str(file_path), format="turtle")
    return graph


def render_graph(graph: Graph, output_path: Path) -> Path:
    dot_path = output_path.with_suffix(".dot")
    dot_path.write_text(graph_to_dot(graph), encoding="utf-8")

    dot_executable = shutil.which("dot")
    if dot_executable:
        render_target = output_path
        subprocess.run(
            [dot_executable, "-Tpng", "-o", str(render_target), str(dot_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"Rendered graph to {render_target}")
        return render_target

    print(f"Graphviz 'dot' executable not found; DOT file written to {dot_path}")
    return dot_path


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Visualize RDF Turtle files as a graph.")
    parser.add_argument(
        "--input",
        nargs="*",
        default=[str(path) for path in default_rdf_files(repo_root)],
        help="RDF Turtle files to load. Defaults to meta/crawler.ttl and rdf/test-arche_constants.ttl.",
    )
    parser.add_argument(
        "--output",
        default=str(repo_root / "rdf_graph.png"),
        help="Output image path. Defaults to rdf_graph.png in the project root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_paths = [Path(arg) for arg in args.input]
    output_path = Path(args.output)

    try:
        graph = load_graph(input_paths)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - defensive parsing error
        print(f"Error parsing RDF files: {exc}", file=sys.stderr)
        return 1

    try:
        render_graph(graph, output_path)
    except subprocess.CalledProcessError as exc:
        print(f"Graphviz rendering failed: {exc.stderr.strip() or exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
