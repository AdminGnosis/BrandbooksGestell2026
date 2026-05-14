#!/usr/bin/env python3
"""
GESTELL · BOS — build pipeline
==============================
Wraps the raw, untouched HTML masters of each volume with a navigation chrome:
  · injects <link rel="stylesheet" href="assets/chrome.css">
  · injects window.__GBOS__ per-volume config (sections, color, roman)
  · injects <script defer src="assets/chrome.js">
  · injects id="cover" on the master-cover page
  · injects id="sec-N" on every section-title-page
  · adds a <div id="gbos-mount"> right after <body>

The original master markup is otherwise NOT modified.

This script is idempotent. Running it twice produces the same output.

Usage:
    python3 build.py
"""

import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

# ─── VOLUME REGISTRY — single source of truth ─────────────────────────────
# `master` is the raw HTML filename. `out` is the deploy filename.
# `title` is the human title, `roman` the numeral. `color` is the accent.
VOLUMES = [
    {
        "master":  "Gestell_BOS_130426_Vol1.html",
        "out":     "vol-1.html",
        "vol":     "vol-1",
        "roman":   "I",
        "title":   "ADN Estratégico",
        "color":   "#00D4FF",   # gnosis
        "stp_h":   "h1",        # selector for the section-title-page heading tag
    },
    {
        "master":  "Gestell_BOS_130426_Vol2.html",
        "out":     "vol-2.html",
        "vol":     "vol-2",
        "roman":   "II",
        "title":   "Arquitectura de Marca",
        "color":   "#B99BD6",   # dasein-text
        "stp_h":   "h1",
    },
    {
        "master":  "BRANDBOOK_VOL__3_-_IDENTIDAD_VISUAL___MASTER_DATA_GESTELL_2026__FINAL_.html",
        "out":     "vol-3.html",
        "vol":     "vol-3",
        "roman":   "III",
        "title":   "Identidad Visual",
        "color":   "#FF0066",   # umwelt
        "stp_h":   "h1",
    },
    {
        "master":  "GESTELL_2026_MASTER_BRANDBOOK_VOLUMEN_IV_-_IDENTIDAD_VERBAL__FINAL_.html",
        "out":     "vol-4.html",
        "vol":     "vol-4",
        "roman":   "IV",
        "title":   "Identidad Verbal",
        "color":   "#F26B8A",   # telos-text
        "stp_h":   "h2",        # Vol IV uses h2 for section titles
    },
    {
        "master":  "gestell-vol5-master.html",
        "out":     "vol-5.html",
        "vol":     "vol-5",
        "roman":   "V",
        "title":   "Identidad Dinámica & Sensorial",
        "color":   "#FF0066",   # umwelt — matches master --vol-accent
        "stp_h":   "h1",
    },
    {
        "master":  "gestell-vol6-master.html",
        "out":     "vol-6.html",
        "vol":     "vol-6",
        "roman":   "VI",
        "title":   "Infraestructura Digital",
        "color":   "#B99BD6",   # dasein-text on dark — readable purple
        "stp_h":   "h1",
    },
]

# ─── REGEXES ──────────────────────────────────────────────────────────────
# Match section-title pages — non-greedy until next "</section>"
RE_MASTER_COVER = re.compile(
    r'<section\s+class="page master-cover"', re.IGNORECASE)
RE_SECTION_TITLE_PAGE = re.compile(
    r'<section\s+class="page section-title-page"', re.IGNORECASE)
RE_HEAD_END = re.compile(r'</head>', re.IGNORECASE)
RE_BODY_OPEN = re.compile(r'<body[^>]*>', re.IGNORECASE)
RE_TAGS = re.compile(r'<[^>]+>')
RE_BR = re.compile(r'<br\s*/?>', re.IGNORECASE)


def strip_tags(s: str) -> str:
    """Strip all HTML tags, decode entities, collapse whitespace."""
    s = RE_BR.sub(' ', s)
    s = RE_TAGS.sub('', s)
    s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def extract_section_metadata(stp_block: str, h_tag: str):
    """
    Pull (code, title, subtitle) from a section-title-page block.
    Returns a dict; missing fields default to empty strings.
    """
    code_m = re.search(
        r'class="stp__code"[^>]*>(.*?)</div>',
        stp_block, re.DOTALL | re.IGNORECASE)
    title_m = re.search(
        rf'<{h_tag}\s+class="stp__title"[^>]*>(.*?)</{h_tag}>',
        stp_block, re.DOTALL | re.IGNORECASE)
    subtitle_m = re.search(
        r'class="stp__subtitle"[^>]*>(.*?)</p>',
        stp_block, re.DOTALL | re.IGNORECASE)
    return {
        "code":     strip_tags(code_m.group(1))     if code_m     else "",
        "title":    strip_tags(title_m.group(1))    if title_m    else "",
        "subtitle": strip_tags(subtitle_m.group(1)) if subtitle_m else "",
    }


def build_volume(spec: dict):
    src = (ROOT / spec["master"]).read_text(encoding="utf-8")

    # ── 1. Inject id="cover" on the first master-cover ─────────────────
    src, n_cover = RE_MASTER_COVER.subn(
        '<section id="cover" class="page master-cover"', src, count=1)
    if n_cover != 1:
        raise RuntimeError(
            f"[{spec['out']}] expected exactly 1 master-cover; got {n_cover}")

    # ── 2. Walk each section-title-page; inject sec-N + capture metadata ─
    sections = []
    idx_counter = [0]

    def replace_stp(_m):
        i = idx_counter[0]
        idx_counter[0] += 1
        return f'<section id="sec-{i}" class="page section-title-page"'

    src_new = RE_SECTION_TITLE_PAGE.sub(replace_stp, src)

    # Extract section metadata by re-finding every now-anchored block
    stp_re = re.compile(
        r'<section\s+id="sec-(\d+)"\s+class="page section-title-page".*?</section>',
        re.DOTALL | re.IGNORECASE)
    for m in stp_re.finditer(src_new):
        i = int(m.group(1))
        meta = extract_section_metadata(m.group(0), spec["stp_h"])
        meta["id"] = f"sec-{i}"
        sections.append(meta)

    # Validate continuity (sec-0 .. sec-N-1)
    for i, sec in enumerate(sections):
        if sec["id"] != f"sec-{i}":
            raise RuntimeError(
                f"[{spec['out']}] section index drift at position {i}: "
                f"got {sec['id']}")

    # ── 3. Inject chrome.css + __GBOS__ config + chrome.js + favicon ───
    cfg = {
        "vol":      spec["vol"],
        "roman":    spec["roman"],
        "title":    spec["title"],
        "color":    spec["color"],
        "sections": sections,
    }
    head_inject = (
        '<link rel="stylesheet" href="assets/chrome.css">\n'
        '<script>window.__GBOS__=' + json.dumps(cfg, ensure_ascii=False) + ';</script>\n'
        '<script defer src="assets/chrome.js"></script>\n'
        '<link rel="icon" type="image/svg+xml" href="favicon.svg">\n'
        '</head>'
    )
    src_new, n_head = RE_HEAD_END.subn(head_inject, src_new, count=1)
    if n_head != 1:
        raise RuntimeError(f"[{spec['out']}] no </head> tag found")

    # ── 4. Mount point right after <body> ──────────────────────────────
    src_new, n_body = RE_BODY_OPEN.subn(
        lambda m: m.group(0) + '\n<div id="gbos-mount"></div>\n',
        src_new, count=1)
    if n_body != 1:
        raise RuntimeError(f"[{spec['out']}] no <body> tag found")

    out_path = ROOT / spec["out"]
    out_path.write_text(src_new, encoding="utf-8")
    print(f"  ✓ {spec['out']:14s} · {len(sections):2d} sections · "
          f"{len(src_new) // 1024} KB")
    return sections


def main():
    print("┌─────────────────────────────────────────────────────────")
    print("│ GESTELL · BOS — building static volumes")
    print("├─────────────────────────────────────────────────────────")
    for spec in VOLUMES:
        master_path = ROOT / spec["master"]
        if not master_path.exists():
            print(f"  ✗ {spec['out']:14s} · MISSING master ({spec['master']})")
            continue
        build_volume(spec)
    print("└─────────────────────────────────────────────────────────")


if __name__ == "__main__":
    main()
