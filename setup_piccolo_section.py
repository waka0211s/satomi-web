#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_piccolo_section.py
Piccolo Fiore 用の新セクションを両HTMLに一度だけ追加します。
既に追加済みの場合は何もしません（二重実行しても安全）。
"""
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent
MARKER = "<!-- PICCOLO_FIORE_HERE -->"

CSS_BLOCK = """
    .piccolo-section {
      margin-top: 6rem;
      padding-top: 5rem;
      border-top: 1px solid rgba(184,150,46,0.15);
    }
    .piccolo-header {
      text-align: center;
      margin-bottom: 3rem;
    }
    .piccolo-eyebrow {
      font-family: 'Cormorant Garamond', serif;
      font-style: italic;
      font-weight: 300;
      font-size: 1.3rem;
      letter-spacing: 0.12em;
      color: var(--gold-lt);
    }
    .piccolo-sub {
      font-size: 0.85rem;
      letter-spacing: 0.1em;
      color: var(--ash);
      margin-top: 0.6rem;
    }
    .piccolo-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1.8rem;
    }
    .piccolo-card { text-align: center; }
    .piccolo-card-img {
      width: 100%;
      aspect-ratio: 1 / 1;
      object-fit: cover;
      border-radius: 2px;
      display: block;
    }
    .piccolo-card-name {
      font-family: 'Cormorant Garamond', serif;
      font-style: italic;
      font-size: 0.78rem;
      letter-spacing: 0.1em;
      color: var(--ash);
      margin-top: 0.8rem;
    }
    @media (max-width: 900px) {
      .piccolo-grid { grid-template-columns: repeat(2, 1fr); }
    }
"""

JA_SECTION = f"""
      <div class="piccolo-section">
        <div class="piccolo-header">
          <p class="piccolo-eyebrow">Piccolo Fiore</p>
          <p class="piccolo-sub" style="font-family:'Zen Old Mincho', serif;">一輪、あるいは、ひとにぎりの花。</p>
        </div>
        <div class="piccolo-grid">
          {MARKER}
        </div>
      </div>

"""

EN_SECTION_INNER = f"""
      <div class="piccolo-section">
        <div class="piccolo-header">
          <p class="piccolo-eyebrow">Piccolo Fiore</p>
          <p class="piccolo-sub">A single bloom, or a handful.</p>
        </div>
        <div class="piccolo-grid">
          {MARKER}
        </div>
      </div>
"""


def patch_css(text):
    if ".piccolo-section" in text:
        return text
    return text.replace("</style>", CSS_BLOCK + "  </style>", 1)


def patch_ja(text):
    if MARKER in text:
        return text
    anchor = '<div class="works-divider-header">'
    if anchor not in text:
        print("⚠️ satomi_index.html: 挿入位置が見つかりませんでした（変更なし）")
        return text
    return text.replace(anchor, JA_SECTION + anchor, 1)


def patch_en(text):
    if MARKER in text:
        return text
    anchor = '</div>\n  </section>\n\n  <section class="philosophy" id="philosophy">'
    if anchor not in text:
        print("⚠️ satomi_en.html: 挿入位置が見つかりませんでした（変更なし）")
        return text
    replacement = '</div>' + EN_SECTION_INNER + '\n  </section>\n\n  <section class="philosophy" id="philosophy">'
    return text.replace(anchor, replacement, 1)


def process(filename, patch_body_fn):
    path = REPO / filename
    if not path.exists():
        print(f"⏭ {filename} が見つかりません")
        return
    text = path.read_text(encoding="utf-8")
    shutil.copy(path, path.with_suffix(path.suffix + ".bak"))
    before = text
    text = patch_css(text)
    text = patch_body_fn(text)
    if text == before:
        print(f"ℹ️ {filename} は変更なし（既に追加済み、または位置未検出）")
    else:
        path.write_text(text, encoding="utf-8")
        print(f"✅ {filename} に Piccolo Fiore セクションを追加しました")


process("satomi_index.html", patch_ja)
process("satomi_en.html", patch_en)
