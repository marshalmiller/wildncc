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
