#!/usr/bin/env python3
"""Add tags, ingredients, cookingmethods, types, and events to all menu items."""
from __future__ import annotations

import re
from pathlib import Path

from taxonomies import infer_taxonomies, yaml_list

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

FRONT_MATTER = re.compile(r"^---\n(.*?)\n---\n?(.*)", re.S)


def parse_inline_tags(line: str) -> list[str]:
    m = re.match(r'tags:\s*\[(.*)\]', line.strip())
    if not m:
        return []
    inner = m.group(1)
    return [t.strip().strip('"').strip("'") for t in inner.split(",") if t.strip()]


def parse_yaml_list_block(lines: list[str], start: int) -> tuple[list[str], int]:
    items = []
    i = start + 1
    while i < len(lines):
        m = re.match(r"^\s*-\s+(.+)$", lines[i])
        if not m:
            break
        items.append(m.group(1).strip().strip('"').strip("'"))
        i += 1
    return items, i


def read_item(path: Path) -> tuple[dict, str, str]:
    text = path.read_text(encoding="utf-8")
    m = FRONT_MATTER.match(text)
    if not m:
        return {}, text, ""
    fm_text, body = m.group(1), m.group(2)
    meta: dict = {"title": "", "tags": []}
    lines = fm_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("title:"):
            meta["title"] = line.split(":", 1)[1].strip()
        elif line.startswith("tags:"):
            if line.strip() == "tags: []":
                meta["tags"] = []
            elif line.strip().startswith("tags: ["):
                meta["tags"] = parse_inline_tags(line)
            else:
                meta["tags"], i = parse_yaml_list_block(lines, i)
        i += 1
    return meta, fm_text, body


def strip_taxonomy_fields(fm_text: str) -> str:
    lines = fm_text.splitlines()
    out = []
    skip_until = -1
    for i, line in enumerate(lines):
        if i < skip_until:
            continue
        if re.match(r"^(tags|ingredients|cookingmethods|types|events):", line):
            if line.strip().endswith("[]"):
                continue
            if not line.strip().endswith("]"):
                _, skip_until = parse_yaml_list_block(lines, i)
            continue
        out.append(line)
    return "\n".join(out)


def write_item(path: Path, section: str, fm_text: str, body: str, tax: dict) -> None:
    fm_text = strip_taxonomy_fields(fm_text)
    tax_lines = []
    tax_lines.extend(yaml_list("tags", tax["tags"]))
    tax_lines.extend(yaml_list("ingredients", tax["ingredients"]))
    tax_lines.extend(yaml_list("cookingmethods", tax["cookingmethods"]))
    tax_lines.extend(yaml_list("types", tax["types"]))
    tax_lines.extend(yaml_list("events", tax["events"]))
    text = "---\n" + fm_text + "\n" + "\n".join(tax_lines) + "\n---"
    if body:
        if not body.startswith("\n"):
            text += "\n"
        text += body
        if not text.endswith("\n"):
            text += "\n"
    else:
        text += "\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    count = 0
    for section_dir in sorted(CONTENT.iterdir()):
        if not section_dir.is_dir():
            continue
        section = section_dir.name
        for path in sorted(section_dir.glob("*.md")):
            if path.name == "_index.md":
                continue
            meta, fm_text, body = read_item(path)
            title = meta.get("title", path.stem.replace("_", " ").title())
            tags = meta.get("tags", [])
            tax = infer_taxonomies(section, title, body.strip(), tags)
            write_item(path, section, fm_text, body, tax)
            count += 1
    print(f"Enriched taxonomies on {count} items.")


if __name__ == "__main__":
    main()
