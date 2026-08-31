#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_piccolo.py — Piccolo Fiore ラインの画像を追加する
En Rilievo NEJICO / satomi-web 用

【使い方】
  1. デスクトップに「piccolo-fiore」フォルダを作り、写真を入れる
  2. ファイル名を 英名_和名.jpg にする（例: Camellia_椿.jpg）
  3. ターミナルで satomi-web フォルダに移動して:
       python3 add_piccolo.py
"""
import shutil
import subprocess
import unicodedata
from pathlib import Path

SRC_DIR = Path.home() / "Desktop" / "piccolo-fiore"
MAX_PX = 1200
JPEG_QUALITY = 80
PUSH = True

REPO = Path(__file__).resolve().parent
IMG_DIR = REPO / "images"
MARKER = "<!-- PICCOLO_FIORE_HERE -->"


def make_card(src_path, jp, en, lang):
    name = f"{jp}　{en}" if lang == "ja" else en
    alt = f"{en} — Piccolo Fiore"
    return (
        '          <div class="piccolo-card">\n'
        f'            <img src="{src_path}" alt="{alt}" class="piccolo-card-img">\n'
        f'            <p class="piccolo-card-name">{name}</p>\n'
        '          </div>\n'
    )


def main():
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
        print(f"⚠️ {SRC_DIR} に画像が見つかりません。")
        return

    entries = []
    for p in photos:
        stem = unicodedata.normalize("NFC", p.stem)
        if "_" not in stem:
            print(f"⏭ スキップ: {p.name} ← 名前を「英名_和名.jpg」にしてください")
            continue
        en, jp = stem.split("_", 1)
        en, jp = en.strip(), jp.strip()
        dest = IMG_DIR / f"piccolo-{en.lower()}.jpg"

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
        print(f"✅ {p.name} → images/{dest.name} ({kb} KB)")

    if not entries:
        print("追加できる画像がありませんでした。")
        return

    targets = [(REPO / "satomi_index.html", "ja"), (REPO / "satomi_en.html", "en")]
    for html, lang in targets:
        if not html.exists():
            continue
        text = html.read_text(encoding="utf-8")
        if MARKER not in text:
            print(f"❌ {html.name} に Piccolo Fiore のセクションがまだありません。"
                  f" 先に setup_piccolo_section.py を実行してください。")
            continue
        shutil.copy(html, html.with_suffix(html.suffix + ".bak"))
        block = "".join(make_card(src, jp, en, lang) for src, jp, en in entries)
        text = text.replace(MARKER, MARKER + "\n" + block, 1)
        html.write_text(text, encoding="utf-8")
        print(f"📝 {html.name} を更新しました")

    if not PUSH:
        print("\n🛑 PUSH=False のため git は実行していません。")
        return

    names = "・".join(jp for _, jp, _ in entries)
    print("\n🚀 GitHubへ反映します…")
    subprocess.run(["git", "add", "-A"], cwd=REPO)
    subprocess.run(["git", "commit", "-m", f"Piccolo Fiore 追加: {names}"], cwd=REPO)
    result = subprocess.run(["git", "push"], cwd=REPO)
    if result.returncode == 0:
        print("\n🌸 完了しました。1〜2分後にサイトへ反映されます。")
    else:
        print("\n⚠️ push に失敗しました。エラーメッセージを確認してください。")


if __name__ == "__main__":
    main()
