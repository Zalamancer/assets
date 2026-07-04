#!/usr/bin/env python3
"""Walk the assets folder, build a manifest, and emit a self-contained index.html.
Re-run this any time you add or remove assets:  python3 _viewer/build.py
"""
import os, json, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the assets/ dir
TEMPLATE = os.path.join(ROOT, "_viewer", "template.html")
OUT = os.path.join(ROOT, "index.html")

IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
FILE_EXT = {".pdf", ".txt", ".tsx", ".tmx", ".aseprite", ".tif", ".tiff", ".json", ".md"}
SKIP_DIRS = {"_viewer", "__MACOSX"}
SKIP_NAMES = {".DS_Store"}


def natural(s):
    import re
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def build(dpath, rel):
    """Return a node dict for directory dpath (rel = posix path from ROOT)."""
    imgs, files, dirs = [], [], []
    try:
        entries = sorted(os.listdir(dpath), key=natural)
    except OSError:
        entries = []
    for name in entries:
        if name in SKIP_NAMES or name.startswith("._"):
            continue
        full = os.path.join(dpath, name)
        if os.path.isdir(full):
            if name in SKIP_DIRS:
                continue
            child = build(full, (rel + "/" + name) if rel else name)
            # keep dir only if it has any assets somewhere
            if child["tot"] > 0 or child["files"] or child["dirs"]:
                dirs.append(child)
        else:
            ext = os.path.splitext(name)[1].lower()
            if ext in IMG_EXT:
                imgs.append(name)
            elif ext in FILE_EXT:
                files.append({"n": name, "t": ext.lstrip(".")})
    tot = len(imgs) + sum(d["tot"] for d in dirs)
    return {
        "name": os.path.basename(dpath) or "assets",
        "path": rel,
        "imgs": imgs,
        "files": files,
        "dirs": dirs,
        "tot": tot,
    }


def collect(top, match):
    """Flat collection node: all image paths under top whose posix path matches `match`."""
    out = []

    def walk(node):
        for n in node.get("imgs", []):
            p = node["path"] + "/" + n
            if match(p.lower()):
                out.append(p)
        for d in node.get("dirs", []):
            walk(d)

    for t in top:
        walk(t)
    out.sort(key=natural)
    return out


def collection_node(name, paths):
    return {"name": name, "path": name, "imgs": paths, "files": [],
            "dirs": [], "tot": len(paths), "flat": True}


def main():
    top = []
    for name in sorted(os.listdir(ROOT), key=natural):
        full = os.path.join(ROOT, name)
        if not os.path.isdir(full) or name in SKIP_DIRS or name.startswith("."):
            continue
        node = build(full, name)
        if node["tot"] > 0:
            top.append(node)

    # synthetic "all of a kind" filter packs gathered from every pack — TILESHEETS
    # only (the packed Tileset_*/Atlas_* sheets, like the rock-slope sheets), never
    # individual object sprites. Each entry = (display name, predicate over the
    # lowercased posix path). Matching is folder-based to stay robust.
    def is_sheet(p):
        b = p.rsplit("/", 1)[-1]
        return (b.startswith("tileset_") or b.startswith("atlas_")
                or b in ("castle_grass.png", "castle_floor.png"))

    COLLECTIONS = [
        ("🌱 All Grass",
         lambda p: is_sheet(p) and "grass" in p),
        ("🟫 All Ground & Roads",
         lambda p: is_sheet(p) and "/ground tilesets/" in p and "grass" not in p),
        ("🏖 All Water & Sand",
         lambda p: is_sheet(p) and "/water and sand/" in p),
        ("⛰ All Rock Slopes",
         lambda p: is_sheet(p) and "/rock slopes/" in p),
        ("🧱 All Fences & Walls",
         lambda p: is_sheet(p) and "/fences and walls/" in p),
        # The artist's green/red layout key — green = a real tile sits in that
        # grid slot, red = empty. One per pack ("Layout" or "Example").
        ("📋 Tile Layout Guides",
         lambda p: is_sheet(p) and ("layout" in p or "example" in p)),
        ("🗺 All Tilemaps",
         lambda p: "/tiled/tilemaps/" in p),
    ]

    collections = []
    coll_counts = []
    for name, pred in COLLECTIONS:
        paths = collect(top, pred)
        coll_counts.append((name, len(paths)))
        if paths:
            collections.append(collection_node(name, paths))

    manifest = {"dirs": collections + top}
    total = sum(d["tot"] for d in top)

    with open(TEMPLATE, "r", encoding="utf-8") as f:
        tpl = f.read()
    payload = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
    html = tpl.replace("__MANIFEST_JSON__", payload)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)

    print("filters:")
    for name, c in coll_counts:
        print(f"  {c:>5}  {name}")
    print(f"packs: {len(top)}")
    for d in top:
        print(f"  {d['tot']:>5}  {d['name']}")
    print(f"total images: {total}")
    print(f"manifest bytes: {len(payload):,}")
    print(f"wrote: {OUT}  ({os.path.getsize(OUT):,} bytes)")


if __name__ == "__main__":
    main()
