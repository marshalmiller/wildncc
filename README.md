# Wild NCC — A Field Guide for Northampton Community College (Static Clone)

Static HTML rebuild of **wildncc.com**, the student-built virtual field guide for
Northampton Community College's campus, recovered from the
[Wayback Machine archive](https://web.archive.org/web/20200814225044/http://wildncc.com/).

## The original project

Wild NCC began in 2010 as a collaboration between Charlie Rinehimer's Biology 2
class and Josh Miller's Advanced Web Site Design class. Biology students
photographed plants, insects and pond life around campus and developed
identification keys; web-design students built the guide. The winning design
was by **Chris J. Koelle**. Later, honors students **Daniel Stevens** and
**Jordan Bold** overhauled the site and extended the taxonomy tree and
Newcomb's-method key values. All keys, photos, locations and text are student
work — preserved here with the original footer credit.

## What this clone is

- Pure static site: HTML + one stylesheet (+ Leaflet for the map). No PHP, no WordPress.
- **110 species pages**, **59 category/field-key pages** (including the
  Newcomb's-method tree keys), Locations table, interactive campus map
  (OpenStreetMap), species index, and a client-side search.
- Original URLs mirrored: `/blue-jay/`, `/category/plants/trees/conifers/pines/`, …
- Photos and text served from the repo (downloaded from the archive).

## Serve it

Any static server works — locally:

    python3 -m http.server 8080

GitHub Pages: enable Pages (Deploy from branch → `main` / root) and the site
goes live as-is in this directory. Relative links make any project-site base
path (`/wildncc/`) work without configuration.

## Notes / limitations

- The original contact form was a PHP form builder; the clone keeps the page as
  static text (marked as disabled).
- The map's original KML overlay (`Wild-NCC.kml`) was never archived; markers
  are rebuilt from the guide's 16-row Location table.
- `/mapbubble/` and `/sample-page/` were not reproduced (mapbubble's archived
  capture is an unrecoverable redirect stub; sample-page was WordPress
  boilerplate).
- Search is client-side over `assets/search-index.json`.

## Image backfill (2026-11-16)

Many Wayback captures never archived the species thumbnails, so ~100 species
pages were shipped without photos and their index cards showed a placeholder.
This run filled every gap:

- **55 species pages** now show the **original archived student photo** recovered
  from the Wayback asset cache (previously used only on cards, or never wired).
- **46 species pages/badges** whose photo was never archived use openly-licensed
  images from **Wikimedia Commons / Wikidata**, square-cropped to
  `images/<slug>-290x290.jpg`. Licenses: Public domain / CC0 / CC BY / CC BY-SA
  only; per-image author + license are recorded in `image-credits.json` and
  rendered on **image-credits.html** (linked from every site footer).
- Species-index and category cards replaced their `placeholder-*.jpg` / no-photo
  states with the species' own image; `assets/search-index.json` was filled so
  the client-side search shows thumbnails too.
- Two text-less stub pages (Colorado Spruce, Ground Beetle) show their photo as
  the page body; the `birds-avians` stub (a leftover map page) stays photo-less
  on the page itself but its card uses the red-winged blackbird image.

## Rebuilding the backfill

- Tools live in `tools/`: `fetch-missing-images.py` (re-fetch/extend the openly-licensed set; writes `image-manifest.json`), `verify-image-backfill.py` (post-change gate), `backfill-contact-sheet.py` (visual QA sheet of fetched picks).
- Runbook: `~/runbooks/2026-11-16-wildncc-image-backfill.md` (method, license rules, verification transcript).
