# Asset Library

A self-contained browser-based gallery for organizing and browsing game assets. Walk through indexed sprite packs, tilesets, and media files with tag-based filtering, search, and multiple view modes.

## Run

1. **Build the manifest** (run after adding/removing assets):
   ```bash
   python3 _viewer/build.py
   ```

2. **Start the server**:
   ```bash
   python3 _viewer/serve.py 8099
   ```

3. **Open in browser**:
   ```
   http://127.0.0.1:8099
   ```

The server defaults to port 8099 and binds to localhost.

## Structure

- **index.html** — Main gallery UI (auto-generated from template + manifest); includes dark theme, search, filtering, and thumbnail browsing
- **_viewer/** — Build and serve infrastructure:
  - `build.py` — Scans asset directories, creates JSON manifest of images/files, injects into template
  - `serve.py` — Tiny Python HTTP server for localhost viewing
  - `template.html` — HTML/CSS/JS template with embedded manifest
- **gameassets/** — Fantasy tilesets (grass, castles, deserts, medieval interiors, snow, seasons)
- **22.10a - Mana Seed Farmer Sprite System v1.6/** — Farmer sprite animations and effects
- **RockSlopes AUTO Renders/** — Auto-generated rock slope tilesheet renders

## Notes

The build system:
- Recursively scans subdirectories for images (.png, .jpg, .jpeg, .gif, .webp, .bmp) and documents (.pdf, .txt, .tsx, .tmx, .aseprite, .tif, .tiff, .json, .md)
- Skips `_viewer/`, `__MACOSX/`, and `.DS_Store` files by default
- Creates synthetic filter collections (All Grass, All Rock Slopes, All Water & Sand, etc.) by matching folder names and filenames
- Auto-builds a flat "All Tilemaps" filter from any Tiled .tmx files
- The generated `index.html` is self-contained (no external dependencies); manifest is JSON-embedded in the template