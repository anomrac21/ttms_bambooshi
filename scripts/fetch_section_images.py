#!/usr/bin/env python3
"""Download copyright-free section images (Pexels) and update content/*/_index.md."""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = ROOT / "static" / "images"
CONTENT = ROOT / "content"

PEX = "https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w=900"

DOWNLOADS: dict[str, tuple[str, str]] = {
    "sushi-rolls.webp": (PEX.format(id="699953"), "Pexels #699953"),
    "sides.webp": (PEX.format(id="2098089"), "Pexels #2098089"),
    "special-deals.webp": (PEX.format(id="958545"), "Pexels #958545"),
    "promotions.webp": (PEX.format(id="2233348"), "Pexels #2233348"),
    "hero.webp": (PEX.format(id="357756"), "Pexels #357756"),
    "slideshow-rolls.webp": (PEX.format(id="2484443"), "Pexels #2484443"),
    "slideshow-sides.webp": (PEX.format(id="410648"), "Pexels #410648"),
    "slideshow-deals.webp": (PEX.format(id="2097099"), "Pexels #2097099"),
}

SECTIONS: dict[str, str] = {
    "promotions": "promotions.webp",
    "sushi-rolls": "sushi-rolls.webp",
    "sides": "sides.webp",
    "special-deals": "special-deals.webp",
}


def img(name: str) -> str:
    return f"images/{name}"


def download_one(filename: str, url: str) -> bool:
    from PIL import Image

    webp = IMAGES_DIR / filename
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        print(f"SKIP {filename}: HTTP {e.code}")
        return webp.exists()
    Image.open(BytesIO(data)).save(webp, "WEBP", quality=85)
    print(f"OK {filename}")
    return True


def body_after_frontmatter(raw: str) -> str:
    if raw.count("---") < 2:
        return raw.strip()
    return raw.split("---", 2)[2].strip()


def update_section_index(section: str, image_file: str) -> None:
    path = CONTENT / section / "_index.md"
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    title_m = re.search(r"^title:\s*(.+)$", raw, re.M)
    weight_m = re.search(r"^weight:\s*(.+)$", raw, re.M)
    title = title_m.group(1).strip().strip('"') if title_m else section.replace("-", " ").title()
    weight = weight_m.group(1).strip().strip('"') if weight_m else "1"
    body = body_after_frontmatter(raw)

    lines = [
        "---",
        f"title: {title}",
        f"weight: {weight}",
        f"icon: {img(image_file)}",
        "images:",
        f"    primary: {img(image_file)}",
        "---",
    ]
    if body:
        lines.extend(["", body])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def update_home_index() -> None:
    path = CONTENT / "_index.md"
    body = body_after_frontmatter(path.read_text(encoding="utf-8"))
    if not body.strip():
        body = (
            "<p>Halal certified sushi rolls in Chaguanas. Signature rolls, sides, "
            "and weekday lunch specials.</p>"
        )
    text = (
        "---\n"
        'title: "Bambooshi"\n'
        f"image: {img('hero.webp')}\n"
        "images:\n"
        f"    - image: {img('hero.webp')}\n"
        f"    - image: {img('sushi-rolls.webp')}\n"
        f"    - image: {img('special-deals.webp')}\n"
        "slideshow:\n"
        f"    - image: {img('slideshow-rolls.webp')}\n"
        f"    - image: {img('slideshow-sides.webp')}\n"
        f"    - image: {img('slideshow-deals.webp')}\n"
        f"    - image: {img('promotions.webp')}\n"
        "---"
    )
    text += f"\n\n{body}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    credits: list[str] = []
    for filename, (url, credit) in DOWNLOADS.items():
        if download_one(filename, url):
            credits.append(f"- {filename} — {credit}")

    for section, image_file in SECTIONS.items():
        if (IMAGES_DIR / image_file).exists():
            update_section_index(section, image_file)
        else:
            print(f"WARN: missing {image_file} for {section}")

    if (IMAGES_DIR / "hero.webp").exists():
        update_home_index()

    (IMAGES_DIR / "IMAGE_CREDITS.txt").write_text(
        "Section photos (Pexels License — free to use):\n" + "\n".join(credits) + "\n",
        encoding="utf-8",
    )
    print("Section headers updated.")


if __name__ == "__main__":
    main()
