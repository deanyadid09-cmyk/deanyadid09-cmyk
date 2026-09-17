# Dragon Code Z V3 — Canon Media Cut

The V2 scouter/HUD skeleton now uses real Dragon Ball media at four impact points:

- BANDAI NAMCO Dragon Ball Z transformation GIF as the full-width hero
- Official Vegeta + scouter image as the fighter dossier anchor
- Second BANDAI NAMCO DBZ GIF as the KI output motion feed
- Official Shenron image as the final summon

The UI panels, radar, mission screens, tech arsenal, training room, and overlays remain original self-contained SVG assets.

## Edit / rebuild
Change `PROFILE` or the media constants in `_src/build.py`, then run:

```bash
python _src/build.py
```

The build script overwrites generated SVGs and README content without deleting the repository directory.

## Publish
The GitHub profile repository must be public and named exactly `deanyadid09-cmyk`. Place `README.md`, `assets/`, `_src/`, and `ASSET_SOURCES.md` at the repository root.
