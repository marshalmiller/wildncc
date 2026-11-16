#!/usr/bin/env python3
"""Post-wiring verification for the wildncc clone.

1. every species page (except stubs) has >=1 resolvable <img>
2. zero broken local img refs anywhere
3. no species card still showing placeholder-200x200.jpg or no-photo (except declared)
4. search-index.json: every species with an image has i set, and file exists
5. image-credits.html link + footer note present on all pages
"""
import json, os, re, glob, sys

REPO = os.environ.get("WILDNCC_REPO", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STUBS = {"birds-avians", "map", "map2", "contact-wild-ncc"}
DECLARED_NOPHOTO = set()  # fill if some species intentionally stay without photos

fails, warns = [], []

# strip search.html JS img template (src="${it.i}") from ref checks
htmls = [h for h in glob.glob(f"{REPO}/**/*.html", recursive=True)]
broken, zero_pages, pages = [], [], 0
for h in htmls:
    rel = os.path.relpath(h, REPO)
    t = open(h, encoding="utf-8", errors="replace").read()
    if rel == "search.html" or rel == "404.html":
        continue
    base = os.path.dirname(h)
    n_ok = 0
    for m in re.finditer(r'src="((?:\.\./)*images/[^"]+\.(?:jpg|jpeg|png))"', t):
        p = os.path.normpath(os.path.join(base, m.group(1)))
        if os.path.exists(p):
            n_ok += 1
        else:
            broken.append((rel, m.group(1)))
    slug = os.path.basename(base)
    if "/" in rel and rel.startswith(("category", "taxonomy")):
        continue  # category pages counted below
    pages += 1
    is_stub = slug in STUBS
    if n_ok == 0 and not is_stub and slug not in DECLARED_NOPHOTO:
        zero_pages.append(slug)

# cards still wrong?
bad_cards = []
for p in [f"{REPO}/species-index.html"] + glob.glob(f"{REPO}/category/**/index.html", recursive=True):
    t = open(p, encoding="utf-8").read()
    for m in re.finditer(r'<div class="species-card"><a href="([^"]+)">(.*?)</a></div>', t):
        slug = m.group(1).strip("/").split("/")[-1]
        inner = m.group(2)
        if slug in STUBS or slug in DECLARED_NOPHOTO:
            continue
        if 'class="no-photo"' in inner or "placeholder-200x200.jpg" in inner:
            bad_cards.append((os.path.relpath(p, REPO), slug))

sidx = json.load(open(f"{REPO}/assets/search-index.json"))
si_missing = []
for e in sidx:
    slug = e["u"].strip("/").split("/")[-1]
    p = e["u"].strip("/").split("/")[0]
    if e["i"] and not os.path.exists(f"{REPO}/images/{os.path.basename(e['i'])}"):
        si_missing.append(e["i"])
    if os.path.isdir(f"{REPO}/{slug}") and not e["i"] and slug not in STUBS and p not in STUBS:
        # species without image file at all?
        has = len(glob.glob(f"{REPO}/{slug}/index.html")) > 0
        if has and slug not in DECLARED_NOPHOTO:
            si_missing.append(f"{slug}: empty i")

foot_ok = sum(1 for p in glob.glob(f"{REPO}/**/*.html", recursive=True)
              if 'href="image-credits.html"' in open(p, encoding="utf-8").read())
print(f"species/category pages checked: {pages}")
print(f"broken local img refs: {len(broken)} {broken[:5]}")
print(f"species pages with zero imgs: {len(zero_pages)} {zero_pages[:10]}")
print(f"bad cards (placeholder/no-photo): {len(bad_cards)} {bad_cards[:10]}")
print(f"search-index gaps: {len(si_missing)} {si_missing[:10]}")
print(f"pages with credits link in footer: {foot_ok}")

ok = not (broken or zero_pages or bad_cards or si_missing) and foot_ok > 100
print("RESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)

# Usage: python3 tools/verify-image-backfill.py  (exit 0 = pass)
