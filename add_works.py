#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
add_works.py — 新作画像を Selected Works に追加する
En Rilievo NEJICO / satomi-web 用
============================================================

【使い方】
  1. デスクトップに「new-works」フォルダを作り、追加したい写真を入れる
  2. ファイル名を  英名_和名.jpg  にする（例: Camellia_椿.jpg）
  3. ターミナルで satomi-web フォルダに移動して、次を実行:

       python3 add_works.py

  これだけで以下が全部走ります:
    - 写真を長辺1600pxに縮小＆軽量化（macOS標準の sips を使用）
    - images/ フォルダにコピー（ファイル名は半角英数に整形）
    - satomi_index.html / satomi_en.html の Selected Works に差し込み
    - git add → commit → push（GitHub Pages に反映）

【安全装置】
  - HTML編集前に .bak バックアップを自動作成します
  - 初回だけ <!-- NEW_WORKS_HERE --> という目印をHTMLに埋め込みます
    （2回目以降はその位置に追記されるので、構造が壊れません）

【元に戻したいとき】
  cp satomi_index.html.bak satomi_index.html
============================================================
"""

import shutil
import subprocess
import unicodedata
from pathlib import Path

# ------- 設定（ここだけ触ればOK）-------
SRC_DIR = Path.home() / "Desktop" / "new-works"   # 写真を置く場所
SUB_LABEL = "Dimensional · Silk thread"           # カード下の小さい英字
MAX_PX = 1600                                     # 長辺の最大ピクセル
JPEG_QUALITY = 80                                 # 画質（60〜90くらい）
PUSH = True                                       # False にすると git push しない
# --------------------------------------

REPO = Path(__file__).resolve().parent
IMG_DIR = REPO / "images"
MARKER = "<!-- NEW_WORKS_HERE -->"
ANCHOR = '<div class="works-grid">'


def make_card(src_path, jp, en, lang):
    """work-card 1枚分のHTMLを組み立てる"""
    name = f"{jp}　{en}" if lang == "ja" else en
    alt = f"{en} — Dimensional Embroidery"
    return (
        '        <div class="work-card">\n'
        f'          <img src="{src_path}" alt="{alt}" class="work-card-img">\n'
        '          <div class="work-card-overlay">\n'
        '            <div class="work-card-info">\n'
        f'              <div class="work-card-name">{name}</div>\n'
        f'              <div class="work-card-sub">{SUB_LABEL}</div>\n'
        '            </div>\n'
        '          </div>\n'
        '        </div>\n'
    )


def main():
    # --- 0. 置き場所の確認 ---
    if not SRC_DIR.exists():
        SRC_DIR.mkdir(parents=True)
        print(f"📁 {SRC_DIR} を作りました。ここに写真を入れて、もう一度実行してください。")
        return

    IMG_DIR.mkdir(exist_ok=True)

    photos = sorted(
        p for p in SRC_DIR.iterdir()
        if p.suffix.lower() in (".jpg", ".jpeg", ".png") and not p.name.startswith(".")
    )
    if not photos:
        print(f"⚠️  {SRC_DIR} に画像が見つかりません。")
        return

    # --- 1. 画像の整形とコピー ---
    entries = []
    for p in photos:
        stem = unicodedata.normalize("NFC", p.stem)  # Macの日本語ファイル名対策
        if "_" not in stem:
            print(f"⏭  スキップ: {p.name}  ← 名前を「英名_和名.jpg」にしてください")
            continue

        en, jp = stem.split("_", 1)
        en = en.strip()
        jp = jp.strip()
        dest = IMG_DIR / f"{en.lower()}.jpg"

        shutil.copy(p, dest)
        subprocess.run(
            ["sips", "-Z", str(MAX_PX),
             "-s", "format", "jpeg",
             "-s", "formatOptions", str(JPEG_QUALITY),
             str(dest), "--out", str(dest)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        kb = dest.stat().st_size // 1024
        entries.append((f"images/{dest.name}", jp, en))
        print(f"✅ {p.name}  →  images/{dest.name}  ({kb} KB)")

    if not entries:
        print("追加できる画像がありませんでした。")
        return

    # --- 2. HTMLへ差し込み ---
    targets = [(REPO / "satomi_index.html", "ja"), (REPO / "satomi_en.html", "en")]
    for html, lang in targets:
        if not html.exists():
            print(f"⏭  {html.name} が見つかりません（スキップ）")
            continue

        text = html.read_text(encoding="utf-8")
        shutil.copy(html, html.with_suffix(html.suffix + ".bak"))

        if MARKER not in text:
            if ANCHOR not in text:
                print(f"❌ {html.name} に Selected Works のグリッドが見つかりません。中断します。")
                continue
            text = text.replace(ANCHOR, ANCHOR + "\n" + MARKER, 1)

        block = "".join(make_card(src, jp, en, lang) for src, jp, en in entries)
        text = text.replace(MARKER, MARKER + "\n" + block, 1)
        html.write_text(text, encoding="utf-8")
        print(f"📝 {html.name} を更新しました（バックアップ: {html.name}.bak）")

    # --- 3. GitHubへ反映 ---
    if not PUSH:
        print("\n🛑 PUSH=False のため、gitは実行していません。")
        return

    names = "・".join(jp for _, jp, _ in entries)
    print("\n🚀 GitHubへ反映します…")
    subprocess.run(["git", "add", "-A"], cwd=REPO)
    subprocess.run(["git", "commit", "-m", f"新作を追加: {names}"], cwd=REPO)
    result = subprocess.run(["git", "push"], cwd=REPO)

    if result.returncode == 0:
        print("\n🌸 完了しました。1〜2分後にサイトへ反映されます。")
        print("   https://waka0211s.github.io/satomi-web/satomi_index.html")
    else:
        print("\n⚠️ push に失敗しました。上のエラーメッセージを確認してください。")


if __name__ == "__main__":
    main()
