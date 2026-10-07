# Profile notes

Dragon Ball Z themed profile for @deanyadid09-cmyk.

The README is a stack of full-width images:

| File | What it is |
|---|---|
| `assets/ticker.svg` | Scrolling scouter feed with Repositories / Follow buttons |
| `assets/banner.gif` | Animated pixel-art island banner |
| `assets/hero.svg` | Name in a ki aura, roles cycling above it, power level |
| `assets/file.svg` | Saiyan file: mission, status, training and motto, beside a dragon radar |
| `assets/techniques.svg` | Three techniques on scouter lenses, plus the arsenal |
| `assets/footer.svg` | Seven star orbs, a ki blast, "To be continued" |

The SVG panels are generated. Text is converted to vector outlines, so the panels look the same on every
device without loading fonts. Every motif is drawn from scratch; no official artwork is used.

## Edit / rebuild

Change `PROFILE` in `_src/build.py`, then run:

```bash
pip install fonttools
python _src/build.py
```

Every SVG in `assets/` is regenerated; the banner GIF is left alone. Open `_src/preview.html` in a browser
to see the whole profile before pushing.
