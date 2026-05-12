#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GESTELL · Brand Operating System · Web Build
─────────────────────────────────────────────
Regenerates vol-N.html from raw HTML masters.

What this script does — and ONLY this:
  1. Read raw brandbook volume from disk (non-destructive, never writes back).
  2. Detect every section-title-page (Vol IV uses <h2>; others use <h1>).
  3. Inject anchor IDs:
        - first  master-cover  → id="cover"
        - Nth    section-title-page  → id="sec-{N-1}"  (0-indexed)
  4. Extract per-section { code, title, subtitle } from .stp__code / .stp__title / .stp__subtitle.
  5. Inject chrome layer just before </head>:
        <link rel="stylesheet" href="assets/chrome.css">
        <script>window.__GBOS__ = {...};</script>
        <script defer src="assets/chrome.js"></script>
  6. Write to vol-{N}.html.

Source HTML content is NEVER modified except for the surgical
additions above. No CSS, no copy, no images are touched.

Determinism: same input ⇒ same output, byte-for-byte.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

# ─── Configuration ────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent

# Source files (raw masters) and their per-volume metadata
@dataclass(frozen=True)
class VolumeSpec:
    slug: str              # output filename stem (e.g. "vol-1")
    roman: str             # "I" | "II" | ...
    title: str             # display title
    color: str             # text-safe accent hex (used in chrome)
    source: str            # raw HTML filename in ROOT
    title_tag: str = "h1"  # which heading the source uses inside .section-title-page

VOLUMES: List[VolumeSpec] = [
    VolumeSpec(
        slug="vol-1",
        roman="I",
        title="ADN Estratégico",
        color="#00D4FF",
        source="Gestell_BOS_130426_Vol1.html",
        title_tag="h1",
    ),
    VolumeSpec(
        slug="vol-2",
        roman="II",
        title="Arquitectura de Marca",
        color="#B99BD6",
        source="Gestell_BOS_130426_Vol2.html",
        title_tag="h1",
    ),
    VolumeSpec(
        slug="vol-3",
        roman="III",
        title="Identidad Visual",
        color="#FF0066",
        source="BRANDBOOK_VOL__3_-_IDENTIDAD_VISUAL___MASTER_DATA_GESTELL_2026__FINAL_.html",
        title_tag="h1",
    ),
    VolumeSpec(
        slug="vol-4",
        roman="IV",
        title="Identidad Verbal",
        color="#F26B8A",
        source="GESTELL_2026_MASTER_BRANDBOOK_VOLUMEN_IV_-_IDENTIDAD_VERBAL__FINAL_.html",
        title_tag="h2",   # ← Vol IV uses <h2 class="stp__title">
    ),
    VolumeSpec(
        slug="vol-6",
        roman="VI",
        title="Infraestructura Digital",
        color="#B99BD6",   # dasein text-safe; matches Vol VI source --vol-accent-text
        source="gestell-vol6-master.html",
        title_tag="h1",
    ),
]

# ─── Regex helpers ────────────────────────────────────────────────────────────

# A <section> opening that already has class="page master-cover" (any attribute order).
# We only target the FIRST one and add id="cover" if it doesn't already carry an id.
RE_MASTER_COVER = re.compile(
    r'<section\b([^>]*?\bclass\s*=\s*"[^"]*\bmaster-cover\b[^"]*"[^>]*)>',
    re.IGNORECASE,
)

# A <section> opening that has class="page section-title-page".
RE_SECTION_TITLE = re.compile(
    r'<section\b([^>]*?\bclass\s*=\s*"[^"]*\bsection-title-page\b[^"]*"[^>]*)>',
    re.IGNORECASE,
)

RE_HAS_ID = re.compile(r'\bid\s*=\s*"', re.IGNORECASE)

# </head> insertion point
RE_HEAD_CLOSE = re.compile(r'</head\s*>', re.IGNORECASE)


def _strip_html(text: str) -> str:
    """Flatten inline HTML inside a title block (e.g. <br>) to a single line."""
    # Replace <br>, <br/>, <br /> with a literal space
    text = re.sub(r'<br\s*/?\s*>', ' ', text, flags=re.IGNORECASE)
    # Strip any remaining tags
    text = re.sub(r'<[^>]+>', '', text)
    # Collapse whitespace
    return re.sub(r'\s+', ' ', text).strip()


@dataclass
class Section:
    id: str
    code: str
    title: str
    subtitle: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "title": self.title,
            "subtitle": self.subtitle,
        }


def _extract_section_meta(block: str, title_tag: str) -> Section:
    """
    Given the HTML between a <section class="page section-title-page"> opening
    and its </section>, pull out code, title, subtitle.
    """
    code_m = re.search(
        r'<div\s+class\s*=\s*"[^"]*\bstp__code\b[^"]*"\s*>(.*?)</div>',
        block, re.IGNORECASE | re.DOTALL,
    )
    title_m = re.search(
        rf'<{title_tag}\s+class\s*=\s*"[^"]*\bstp__title\b[^"]*"\s*>(.*?)</{title_tag}>',
        block, re.IGNORECASE | re.DOTALL,
    )
    sub_m = re.search(
        r'<p\s+class\s*=\s*"[^"]*\bstp__subtitle\b[^"]*"\s*>(.*?)</p>',
        block, re.IGNORECASE | re.DOTALL,
    )
    return Section(
        id="",  # filled in by caller
        code=_strip_html(code_m.group(1)) if code_m else "",
        title=_strip_html(title_m.group(1)) if title_m else "",
        subtitle=_strip_html(sub_m.group(1)) if sub_m else "",
    )


def _inject_cover_id(html: str) -> str:
    """Add id='cover' to the first <section class="...master-cover...">."""
    def repl(m: re.Match) -> str:
        attrs = m.group(1)
        if RE_HAS_ID.search(attrs):
            return m.group(0)
        return f'<section{attrs} id="cover">'
    # Only the first occurrence
    return RE_MASTER_COVER.sub(repl, html, count=1)


def _inject_section_ids_and_collect(
    html: str, title_tag: str
) -> tuple[str, List[Section]]:
    """
    Walk through every section-title-page in source order. Inject id="sec-N"
    on each (skipping any that already have an id) and collect its metadata.

    Returns: (modified_html, [sections])
    """
    sections: List[Section] = []
    out_parts: List[str] = []
    cursor = 0
    idx = 0

    for m in RE_SECTION_TITLE.finditer(html):
        attrs = m.group(1)
        section_start = m.start()
        section_open_end = m.end()

        # Emit everything before this section opening, untouched
        out_parts.append(html[cursor:section_start])

        # Find the matching </section> for this opening to extract its inner block.
        # Sections in these files are FLAT (no nesting), so the next </section>
        # is the correct closer.
        close = html.find('</section>', section_open_end)
        if close == -1:
            raise ValueError(
                f'Could not find </section> after section-title-page #{idx} '
                f'(starting at char {section_start}).'
            )

        inner = html[section_open_end:close]
        sec_meta = _extract_section_meta(inner, title_tag)
        sec_meta.id = f"sec-{idx}"
        sections.append(sec_meta)

        # Emit the modified opening
        if RE_HAS_ID.search(attrs):
            out_parts.append(m.group(0))
        else:
            out_parts.append(f'<section{attrs} id="{sec_meta.id}">')

        cursor = section_open_end
        idx += 1

    out_parts.append(html[cursor:])
    return "".join(out_parts), sections


def _inject_chrome(html: str, spec: VolumeSpec, sections: List[Section]) -> str:
    """Insert chrome <link> / <script> just before </head>."""
    payload = {
        "vol":   spec.slug,
        "roman": spec.roman,
        "title": spec.title,
        "color": spec.color,
        "sections": [s.to_dict() for s in sections],
    }
    # ensure_ascii=False so accented characters render naturally; this file is utf-8.
    cfg_json = json.dumps(payload, ensure_ascii=False)

    injection = (
        '<link rel="stylesheet" href="assets/chrome.css">\n'
        f'<script>window.__GBOS__={cfg_json};</script>\n'
        '<script defer src="assets/chrome.js"></script>\n'
    )

    new_html, n = RE_HEAD_CLOSE.subn(injection + r'</head>', html, count=1)
    if n != 1:
        raise ValueError("No </head> found — cannot inject chrome.")
    return new_html


# ─── Driver ───────────────────────────────────────────────────────────────────

def build_volume(spec: VolumeSpec, out_dir: Path) -> dict:
    src_path = ROOT / spec.source
    if not src_path.exists():
        raise FileNotFoundError(f"Source missing: {src_path}")

    raw = src_path.read_text(encoding="utf-8")

    # 1. Inject cover anchor
    step1 = _inject_cover_id(raw)
    # 2. Inject section anchors + collect metadata
    step2, sections = _inject_section_ids_and_collect(step1, spec.title_tag)
    # 3. Inject chrome
    final = _inject_chrome(step2, spec, sections)

    out_path = out_dir / f"{spec.slug}.html"
    out_path.write_text(final, encoding="utf-8")

    return {
        "slug": spec.slug,
        "roman": spec.roman,
        "title": spec.title,
        "sections_found": len(sections),
        "bytes_in":  len(raw),
        "bytes_out": len(final),
        "out": str(out_path.relative_to(ROOT.parent) if out_path.is_relative_to(ROOT.parent) else out_path),
    }


def main(only: Optional[List[str]] = None) -> int:
    out_dir = ROOT
    targets = VOLUMES if not only else [v for v in VOLUMES if v.slug in only]
    if not targets:
        print("No matching volumes.", file=sys.stderr)
        return 1

    print(f"GESTELL · Build · {len(targets)} volume(s)")
    print("─" * 60)
    for spec in targets:
        try:
            r = build_volume(spec, out_dir)
        except Exception as e:
            print(f"  ✗ {spec.slug} — {type(e).__name__}: {e}", file=sys.stderr)
            return 2
        print(
            f"  ✓ {r['slug']:<7} · Vol. {r['roman']:<3} · "
            f"{r['sections_found']:>2} secs · "
            f"{r['bytes_in']:>7} → {r['bytes_out']:>7} bytes"
        )
    print("─" * 60)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or None))
