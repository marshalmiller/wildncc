#!/usr/bin/env python3
"""Contact sheet of fetched wildncc images (slug + license annotated) for visual QA."""
import json, math, os
from PIL import Image, ImageDraw, ImageOps

REPO = "/home/marshalmiller/wildncc"
MF   = "/home/marshalmiller/.hermes/profiles/sysadmin/cache/scratch/wildncc_image_manifest.json"
OUT  = "/home/marshalmiller/.hermes/profiles/sysadmin/cache/scratch/wildncc_contact_sheet.jpg"

mf = json.load(open(MF))
items = [(s, m) for s, m in sorted(mf.items()) if m.get("file") and m["file"].endswith("290x290.jpg")
         and os.path.exists(f"{REPO}/images/{m['file']}")]
T = 148
cols = 6
rows = math.ceil(len(items) / cols)
sheet = Image.new("RGB", (cols * T, rows * (T + 26)), (240, 240, 235))
d = ImageDraw.Draw(sheet)
for i, (slug, m) in enumerate(items):
    x, y = (i % cols) * T, (i // cols) * (T + 26)
    im = ImageOps.fit(Image.open(f"{REPO}/images/{m['file']}"), (T - 8, T - 8))
    sheet.paste(im, (x + 4, y + 2))
    lic = (m.get("license") or "").replace("Commons", "")[:22]
    d.text((x + 4, y + T - 2), f"{slug[:20]} | {lic}", fill=(30, 30, 30))
sheet.save(OUT, "JPEG", quality=85)
print(f"{OUT}: {len(items)} images, {sheet.size}")
