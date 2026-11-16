#!/usr/bin/env python3
"""Fetch openly-licensed images for wildncc.com missing-photo species.

Sources: 1) Wikidata P18 via enwiki title, 2) Commons fulltext search.
License filter: PD/CC0/CC BY/CC BY-SA only. Output: images/<slug>-290x290.jpg
Resumable: skips slugs already present in manifest.
"""
import json, os, re, time, urllib.request, urllib.parse, html, sys
from PIL import Image, ImageOps

REPO = os.environ.get("WILDNCC_REPO", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAN   = "/home/marshalmiller/.hermes/profiles/sysadmin/cache/scratch/wildncc_plan.json"
MF     = "/home/marshalmiller/.hermes/profiles/sysadmin/cache/scratch/wildncc_image_manifest.json"
UA     = "WildNCC-image-backfill/1.0 (static site maintenance; contact marshalmiller at northampton.edu) python-urllib/3"

plan = json.load(open(PLAN))
manifest = {}
if os.path.exists(MF):
    manifest = json.load(open(MF))

# ---- name fixes where clone/page taxonomy is stale or ambiguous
OVERRIDES = {
    "birds-avians":        "Agelaius phoeniceus",
    "starling":            "Sturnus vulgaris",
    "pine-warbler":        "Setophaga pinus",
    "green-ash":           "Fraxinus pennsylvanica",
    "zelkova":             "Zelkova serrata",
    "mulberry":            "Morus alba",
    "honey-locust":        "Gleditsia triacanthos",
    "house-sparrow":       "Passer domesticus",
    "homo-sapien":         "Homo sapiens",
    "black-willow":        "Salix nigra",
    "carolina-chickadee":  "Poecile carolinensis",
    "viburnum":            "Viburnum",
    "crimson-king-maple":  "Acer platanoides Crimson King",
    "crab-apple":          "crabapple blossoms",
    "homo-sapien":         "Vitruvian Man",
}
ALLOW = re.compile(r"^(CC0|CC BY(?:[- ]SA)? ?[1-4](?:\.\d)?|CC ?BY(?:-SA)?\b|Public domain|PD|Attribution)", re.I)
DENY  = re.compile(r"(NC|ND|GFDL|non-free|Fair use)", re.I)

def api(host, params):
    params = dict(params, format="json", formatversion=2)
    url = f"https://{host}/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            if attempt == 3:
                print(f"    ! API fail {url[:90]}: {e}")
                return None
            time.sleep(2 + 4 * attempt)

def wikidata_p18(term):
    d = api("www.wikidata.org", {"action": "wbgetentities", "sites": "enwiki",
                                 "titles": term, "props": "claims"})
    ents = (d or {}).get("entities", {})
    for qid, ent in ents.items():
        for c in ent.get("claims", {}).get("P18", []):
            v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
            if v:
                return qid, v
    # fallback: entity search
    d = api("www.wikidata.org", {"action": "wbsearchentities", "search": term,
                                 "type": "item", "language": "en", "limit": 2})
    for r in (d or {}).get("search", []):
        d2 = api("www.wikidata.org", {"action": "wbgetentities", "ids": r["id"], "props": "claims"})
        for ent in (d2 or {}).get("entities", {}).values():
            for c in ent.get("claims", {}).get("P18", []):
                v = c.get("mainsnak", {}).get("datavalue", {}).get("value")
                if v:
                    return r["id"], v
    return None, None

def commons_fileinfo(title, width=900):
    d = api("commons.wikimedia.org", {"action": "query", "titles": title,
                                      "prop": "imageinfo", "iiprop": "url|extmetadata|mime|size",
                                      "iiurlwidth": width})
    for pg in (d or {}).get("query", {}).get("pages", []):
        ii = pg.get("imageinfo")
        if ii:
            return pg["title"], ii[0]
    return None, None

def license_ok(extmd):
    lic = (extmd.get("LicenseShortName", {}) or {}).get("value", "") or ""
    return bool(lic) and bool(ALLOW.match(lic.strip())) and not DENY.search(lic.strip()), lic.strip()

def strip_html(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", "", s or ""))).strip()

def commons_search(term, limit=8):
    d = api("commons.wikimedia.org", {
        "action": "query", "generator": "search", "gsrnamespace": 6,
        "gsrsearch": f"{term} filetype:bitmap", "gsrlimit": limit,
        "prop": "imageinfo", "iiprop": "url|extmetadata|mime|size", "iiurlwidth": 900})
    out = []
    for pg in sorted((d or {}).get("query", {}).get("pages", []), key=lambda p: p.get("index", 99)):
        ii = pg.get("imageinfo")
        if ii:
            out.append((pg["title"], ii[0]))
    return out

def try_ii(slug, title, ii, via, src_title):
    ok, lic = license_ok(ii.get("extmetadata", {}))
    mime = ii.get("mime", "")
    if not ok:
        return None
    if mime not in ("image/jpeg", "image/png"):
        return None
    url = ii.get("thumburl") or ii.get("url")
    extmd = ii.get("extmetadata", {})
    ent = {
        "slug": slug, "file": None, "via": via, "source_title": src_title,
        "descriptionurl": ii.get("descriptionurl", ""),
        "license": lic,
        "license_url": (extmd.get("LicenseUrl", {}) or {}).get("value", ""),
        "artist": strip_html((extmd.get("Artist", {}) or {}).get("value", "")),
        "credit": strip_html((extmd.get("Credit", {}) or {}).get("value", ""))[:200],
        "mime": mime,
    }
    if ent["artist"].startswith("Unknown") or not ent["artist"]:
        ent["artist"] = "see file page"
    return ent if url else None

def center_crop_290(path_raw, path_out):
    im = Image.open(path_raw)
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
    im = im.resize((290, 290), Image.LANCZOS)
    im.save(path_out, "JPEG", quality=88)

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10 ** 9
done = 0
for item in plan["fetch"]:
    slug = item["slug"]
    if done >= N:
        break
    if slug in manifest and manifest[slug].get("file") and os.path.exists(f"{REPO}/images/{manifest[slug]['file']}"):
        done += 1
        continue
    terms = []
    if OVERRIDES.get(slug): terms.append((OVERRIDES[slug], "override"))
    if item.get("sci"):     terms.append((item["sci"], "sci"))
    terms.append((item["title"], "common"))
    ent, raw_path = None, None
    for term, kind in terms:
        time.sleep(0.35)
        qid, p18 = wikidata_p18(term)
        if p18 and not p18.lower().startswith("file:"):
            p18 = "File:" + p18
        if p18:
            time.sleep(0.35)
            t, ii = commons_fileinfo(p18)
            if ii:
                cand = try_ii(slug, t, ii, f"wikidata:{qid}({kind})", t)
                if cand:
                    dl = urllib.request.Request(cand_desc := ii.get("thumburl") or ii.get("url"),
                                                headers={"User-Agent": UA})
                    raw_path = os.path.join(__import__("tempfile").gettempdir(), f"{slug}.raw")
                    try:
                        with urllib.request.urlopen(dl, timeout=60) as r, open(raw_path, "wb") as f:
                            f.write(r.read())
                        ent = cand
                        print(f"  {slug}: WD P18 [{t}] lic={ent['license']}")
                        break
                    except Exception as e:
                        print(f"    ! dl fail {slug}: {e}")
                        raw_path = None
        if not ent:
            time.sleep(0.35)
            for t, ii in commons_search(term):
                cand = try_ii(slug, t, ii, f"commons-search({kind})", t)
                if not cand:
                    continue
                dl = urllib.request.Request(ii.get("thumburl") or ii.get("url"),
                                            headers={"User-Agent": UA})
                raw_path = os.path.join(__import__("tempfile").gettempdir(), f"{slug}.raw")
                try:
                    with urllib.request.urlopen(dl, timeout=60) as r, open(raw_path, "wb") as f:
                        f.write(r.read())
                    ent = cand
                    print(f"  {slug}: SEARCH [{t}] lic={ent['license']}")
                    break
                except Exception as e:
                    print(f"    ! dl fail {slug}: {e}")
                    raw_path = None
            if ent:
                break
    if not ent:
        print(f"  {slug}: NO CANDIDATE FOUND (terms: {[(k, t) for t, k in terms]})")
        manifest[slug] = {"failed": True}
        continue
    fname = f"{slug}-290x290.jpg"
    center_crop_290(raw_path, os.path.join(REPO, "images", fname))
    os.remove(raw_path)
    ent["file"] = fname
    manifest[slug] = ent
    json.dump(manifest, open(MF, "w"), indent=1)
    done += 1

json.dump(manifest, open(MF, "w"), indent=1)
got = [k for k, v in manifest.items() if v.get("file")]
print(f"\nMANIFEST: {len(got)} images ready, {len(manifest) - len(got)} unresolved")

# Usage: python3 tools/fetch-missing-images.py [N]  (repo auto-located from tools/ parent)
