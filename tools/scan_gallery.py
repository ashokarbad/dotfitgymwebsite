#!/usr/bin/env python3
"""
Dotfit gallery scanner
======================

Reads every folder under  site/images/gallery/  and rewrites
site/assets/js/gallery-manifest.js  to match.

    python3 tools/scan_gallery.py

That is the whole workflow. Drop photos into the right folder, run this,
upload. No page editing, no HTML.

Why a script and not "the website reads the folder"
---------------------------------------------------
A browser cannot list the contents of a folder on a web server. It can
only request files it already knows the names of. Netlify, GitHub Pages,
Hostinger and cPanel all refuse directory listings by default, and the
ones that allow it return HTML meant for humans, not an API. So the file
list has to be written down somewhere at some point. This script is that
point. It writes a .js file rather than .json on purpose: a .js file
still loads when you double-click a page straight off the disk, while
fetching .json from file:// is blocked by the browser.

Optional extras
---------------
* Titles, dates and captions: put a captions.json next to the photos.

      site/images/gallery/trekking/captions.json
      {
        "trekking-01.webp": {
          "title":   "Sinhagad sunrise",
          "date":    "March 2026",
          "caption": "Twenty-two of us, up before the sun."
        }
      }

  Anything not listed falls back to a title derived from the filename.

* Thumbnails: if Pillow is installed the script writes a 640px-wide
  thumbnail into a  thumb/  subfolder and the gallery serves that in the
  grid, loading the full image only in the lightbox. Without Pillow it
  still works, it just serves full-size images in the grid.
      pip install Pillow
"""

import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GALLERY_DIR = os.path.join(ROOT, "site", "images", "gallery")
OUT_FILE = os.path.join(ROOT, "site", "assets", "js", "gallery-manifest.js")

EXT = (".webp", ".jpg", ".jpeg", ".png", ".avif")
THUMB_WIDTH = 640

# Order and display names of the categories. Add a line here and create the
# matching folder to introduce a new one.
CATEGORIES = [
    ("yoga", "Yoga"),
    ("zumba", "Zumba"),
    ("crossfit", "CrossFit"),
    ("hiit", "HIIT"),
    ("cycling", "Cycling"),
    ("aerobics", "Aerobics"),
    ("personal-training", "Personal Training"),
    ("weight-training", "Weight Training"),
    ("sports-training", "Sports Training"),
    ("trekking", "Trekking"),
    ("dpl", "DPL"),
    ("fitness-challenges", "Fitness Challenges"),
    ("outdoor", "Outdoor Activities"),
    ("events", "Events"),
    ("community", "Community"),
    ("nutrition", "Nutrition"),
    ("sports-wear", "Sports Wear"),
]

try:
    from PIL import Image  # type: ignore
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False


def title_from(filename: str) -> str:
    """yoga-morning-flow-02.webp -> Yoga morning flow"""
    stem = os.path.splitext(filename)[0]
    stem = re.sub(r"[-_]\d+$", "", stem)
    stem = stem.replace("-", " ").replace("_", " ").strip()
    return stem[:1].upper() + stem[1:] if stem else "Dotfit Fitness"


def make_thumb(src_path: str, folder: str, filename: str):
    """Returns (thumb_relative_name_or_None, width, height)."""
    if not HAVE_PIL:
        return None, None, None
    try:
        with Image.open(src_path) as im:
            w, h = im.size
            if w <= THUMB_WIDTH:
                return None, w, h
            thumb_dir = os.path.join(folder, "thumb")
            os.makedirs(thumb_dir, exist_ok=True)
            out_name = os.path.splitext(filename)[0] + ".webp"
            out_path = os.path.join(thumb_dir, out_name)
            if not os.path.exists(out_path) or \
               os.path.getmtime(out_path) < os.path.getmtime(src_path):
                im2 = im.convert("RGB")
                im2.thumbnail((THUMB_WIDTH, THUMB_WIDTH * 3), Image.LANCZOS)
                im2.save(out_path, "WEBP", quality=82, method=5)
            return "thumb/" + out_name, w, h
    except Exception as exc:  # a corrupt file should not stop the whole run
        print("  ! could not read %s (%s)" % (filename, exc))
        return None, None, None


def scan():
    if not os.path.isdir(GALLERY_DIR):
        sys.exit("No folder at %s — create it first." % GALLERY_DIR)

    if not HAVE_PIL:
        print("Pillow not installed: no thumbnails, no dimensions.")
        print("  pip install Pillow    (recommended — cuts gallery weight a lot)\n")

    data, total, oversized = {}, 0, []

    for key, _name in CATEGORIES:
        folder = os.path.join(GALLERY_DIR, key)
        if not os.path.isdir(folder):
            continue

        captions = {}
        cap_path = os.path.join(folder, "captions.json")
        if os.path.exists(cap_path):
            try:
                with open(cap_path, encoding="utf-8") as fh:
                    captions = json.load(fh)
            except json.JSONDecodeError as exc:
                print("  ! captions.json in %s is not valid JSON (%s) — ignored"
                      % (key, exc))

        files = sorted(f for f in os.listdir(folder)
                       if f.lower().endswith(EXT) and not f.startswith("."))

        photos = []
        for f in files:
            path = os.path.join(folder, f)
            size_kb = os.path.getsize(path) // 1024
            if size_kb > 400:
                oversized.append("%s/%s (%d KB)" % (key, f, size_kb))

            thumb_rel, w, h = make_thumb(path, folder, f)
            base = "images/gallery/%s/" % key
            meta = captions.get(f, {})

            entry = {
                "src": base + f,
                "title": meta.get("title") or title_from(f),
            }
            if thumb_rel:
                entry["thumb"] = base + thumb_rel
            if w and h:
                entry["w"], entry["h"] = w, h
            if meta.get("date"):
                entry["date"] = meta["date"]
            if meta.get("caption"):
                entry["caption"] = meta["caption"]
            photos.append(entry)

        data[key] = photos
        total += len(photos)
        print("  %-20s %d" % (key, len(photos)))

    labels = {k: n for k, n in CATEGORIES}
    order = [k for k, _ in CATEGORIES]

    payload = {
        "generated": date.today().isoformat(),
        "order": order,
        "labels": labels,
        "categories": data,
    }

    body = json.dumps(payload, indent=2, ensure_ascii=False)
    with open(OUT_FILE, "w", encoding="utf-8") as fh:
        fh.write(
            "/* Generated by tools/scan_gallery.py — do not edit by hand.\n"
            "   Add photos to site/images/gallery/<category>/ and run the\n"
            "   script again. */\n"
            "window.DOTFIT_GALLERY = " + body + ";\n"
        )

    print("\n%d photos across %d categories -> %s"
          % (total, sum(1 for v in data.values() if v),
             os.path.relpath(OUT_FILE, ROOT)))

    if oversized:
        print("\nToo heavy for a phone connection — compress these at squoosh.app:")
        for line in oversized[:15]:
            print("  " + line)
        if len(oversized) > 15:
            print("  ...and %d more" % (len(oversized) - 15))


if __name__ == "__main__":
    scan()
