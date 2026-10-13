# Profile notes

Dragon Ball themed profile for @deanyadid09-cmyk, designed by Sundays and Saturdays.

There are two themes. `README.md` (the live profile) uses **Black**; `README-white.md` keeps the
sand-coloured **White** version. To switch, copy `README-white.md` over `README.md`.

Each README is a stack of full-width animated SVGs from `assets/black/` or `assets/white/`:

| Panel | What it is |
|---|---|
| `ticker.svg` | Scrolling scouter feed with Repositories / Follow buttons |
| `hero.svg` | The Goku vs Vegeta banner (push-in, speed lines, punch flash) with the see-through SUNDAYS card and scouter reading over it |
| `mission.svg` | Current mission: DealEngine, beside an animated dragon radar |
| `techniques.svg` | Three technique cards, each with a looping clip, plus the arsenal |
| `footer.svg` | The seven dragon balls, "© 2026 Sundays & Saturdays", "To be continued" |

Every image the panels use is in `assets/source/`, and is embedded into the SVGs at build time
(GitHub shows README images in a sandbox that cannot load other files). The technique GIFs are
turned into frame strips stepped through with CSS, because GIFs inside an SVG don't reliably play.
Text is converted to vector outlines, so it looks the same everywhere without loading fonts.

`assets/source/` also keeps the assets that aren't in use right now: Shenron, the full dragon ball
sheet, the alternative Product Systems clip and the original island banner (`assets/banner.gif`).

## Edit / rebuild

Change `PROFILE` (text) or `THEMES` (colours) in `_src/build.py`, then run:

```bash
pip install fonttools pillow
python _src/build.py
```

Both themes are regenerated. Open `_src/preview.html` in a browser to see them side by side before pushing.
