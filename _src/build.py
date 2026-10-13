#!/usr/bin/env python3
"""Builds the Dragon Ball themed SVG panels of the profile README, in two themes.

Edit PROFILE below, then run:

    pip install fonttools pillow
    python _src/build.py

Every panel is written twice, to assets/black/ (README.md, the live profile) and
assets/white/ (README-white.md, a sand-coloured alternative). The images the
panels use live in assets/source/ and are embedded into the SVGs at build time,
because GitHub shows README images in a sandbox that cannot load anything else.
Text is converted to vector outlines (Barlow Condensed + JetBrains Mono, both OFL;
see _src/fonts), so it looks the same on every device without loading fonts.
"""
import base64
import html
import io
import math
import random
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageSequence

SRC = Path(__file__).resolve().parent
ASSETS = SRC.parent / "assets"
IMG = ASSETS / "source"

# ---------------------------------------------------------------- content ---
PROFILE = {
    "name": "SUNDAYS",
    "handle": "DEANYADID09-CMYK",
    "roles": ["PRODUCT BUILDER", "AI SYSTEMS", "AUTOMATION"],
    "tagline": "BUILD SYSTEMS. SHIP FAST. KEEP TRAINING.",
    "power": "9,001+",
    # (label, value) rows of the scouter readout beside the name.
    "scouter": [("FIGHTER", "DEANYADID09-CMYK"), ("CLASS", "BUILDER"), ("STATUS", "TRAINING")],
    # The current mission: the name is split so the second half lights up.
    "mission": {
        "name": ("DEAL", "ENGINE"),
        "lead": "A CRM and deal flow system.",
        "detail": "A focused operating layer for Draw Forward LLC.",
        "status": "ACTIVE BUILD",
        "button": "VIEW MISSION",
    },
    # (name, detail, looping clip in assets/source/techniques)
    "techniques": [
        ("AGENT ARCHITECTURE", "REASON · ROUTE · EXECUTE", "technique-1-agent-architecture.gif", (.5, .4)),
        ("AUTOMATION", "REPETITIVE WORK → LEVERAGE", "technique-2-automation.gif", (.45, .5)),
        ("PRODUCT SYSTEMS", "INTERFACES PEOPLE RUN WITH", "technique-3-product-systems.gif", (.46, .4)),
    ],
    "techniques_note": "TRAINING // AGENTS · AUTOMATION · PRODUCT",
    "arsenal": ["REACT", "JAVASCRIPT", "VITE", "TAILWIND", "MUI", "FRAMER MOTION", "GITHUB", "AI WORKFLOWS"],
    "ticker": [
        "SUNDAYS — PRODUCT BUILDER · AI SYSTEMS · AUTOMATION",
        "CURRENT MISSION: DEALENGINE",
        "BUILD SYSTEMS. SHIP FAST. KEEP TRAINING.",
        "POWER LEVEL: 9,001+",
    ],
    "ticker_buttons": ["REPOSITORIES", "FOLLOW"],
    "footer": {"left": "© 2026 SUNDAYS & SATURDAYS", "right": "TO BE CONTINUED"},
}

# ----------------------------------------------------------------- themes ---
# Black: gi orange and ki gold on a night sky. White: the same, on warm sand.
THEMES = {
    "black": dict(
        BG="#09070A", PANEL="#120D0B", PANEL2="#1C140E", LINE="#3A2818", TILE="#0C0907",
        ORANGE="#FF8A1F", GOLD="#FFD23F", GREEN="#5CFF7A", RED="#E8352C",
        TEXT="#FFF3E3", MUTED="#B59C84", DIM="#6E5A47",
        ON_ORANGE="#09070A", BTN_BG="#1C140E", BTN_FG="#FFF3E3", TICK_BG="#09070A",
        CARD="#0E0A09", CARD_ALPHA=(.42, .68), EDGE="#FFD23F", EDGE_ALPHA=.35,
        HALO=("#FFD23F", ".55"), GRID_VEIL=.55, GLOW=True,
    ),
    "white": dict(
        BG="#F1E4CC", PANEL="#F6ECDA", PANEL2="#EADBC0", LINE="#D9C4A0", TILE="#FBF5EA",
        ORANGE="#E2650A", GOLD="#A86F00", GREEN="#1F8F3E", RED="#C8281F",
        TEXT="#2A1B10", MUTED="#7B634A", DIM="#A08A6E",
        ON_ORANGE="#FFFFFF", BTN_BG="#2A1B10", BTN_FG="#F6ECDA", TICK_BG="#EADBC0",
        CARD="#F8EFE0", CARD_ALPHA=(.38, .62), EDGE="#FFFFFF", EDGE_ALPHA=.75,
        HALO=("#FFF8EB", ".8"), GRID_VEIL=.72, GLOW=False,
    ),
}

W = 1000
# Theme colours; set_theme() fills these in before each build.
BG = PANEL = PANEL2 = LINE = TILE = ORANGE = GOLD = GREEN = RED = TEXT = MUTED = DIM = ""
ON_ORANGE = BTN_BG = BTN_FG = TICK_BG = CARD = EDGE = ""
CARD_ALPHA = HALO = None
EDGE_ALPHA = GRID_VEIL = 0.0
GLOW = False
OUT = ASSETS


def set_theme(name):
    globals().update(THEMES[name])
    globals()["OUT"] = ASSETS / name


BASE_CSS = """
.rise{animation:rise 1.2s cubic-bezier(.16,1,.3,1) both}
@keyframes rise{from{transform:translateY(200px)}}
.fade{animation:fade 1s ease both}
@keyframes fade{from{opacity:0}}
.up{animation:up 1s cubic-bezier(.16,1,.3,1) both}
@keyframes up{from{opacity:0;transform:translateY(14px)}}
.blink{animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
@media (prefers-reduced-motion: reduce){*{animation:none!important}}
"""


class Font:
    """A font whose glyphs are drawn as SVG outlines.

    GitHub serves repo images under a CSP that can block embedded web fonts, so
    all text is converted to paths at build time and renders identically everywhere.
    """

    def __init__(self, key, filename, wght=None):
        tt = TTFont(SRC / "fonts" / filename)
        if wght is not None and "fvar" in tt:
            tt = instantiateVariableFont(tt, {"wght": wght})
        self.key = key
        self.tt = tt
        self.glyphs = tt.getGlyphSet()
        self.upm = tt["head"].unitsPerEm
        self.cmap = tt.getBestCmap()
        self.adv = {g: m[0] for g, m in tt["hmtx"].metrics.items()}

    def glyph(self, ch):
        name = self.cmap.get(ord(ch))
        if name is None:
            raise ValueError(f"{self.key} has no glyph for {ch!r}")
        return name

    def width(self, text, size, ls=0.0):
        units = sum(self.adv[self.glyph(ch)] for ch in text)
        return units / self.upm * size + ls * max(len(text) - 1, 0)

    def path(self, name):
        pen = SVGPathPen(self.glyphs, ntos=lambda v: f"{v:.0f}")
        self.glyphs[name].draw(pen)
        return pen.getCommands()


BOLD = Font("b", "BarlowCondensed-Bold.ttf")
MED = Font("m", "BarlowCondensed-Medium.ttf")
MONO_B = Font("mb", "JetBrainsMono.ttf", wght=700)
MONO = Font("mr", "JetBrainsMono.ttf", wght=400)


def esc(s):
    return html.escape(s, quote=True)


class SVG:
    def __init__(self, name, h, title, corners="none"):
        self.name, self.h, self.title, self.corners = name, h, title, corners
        self.defs, self.body, self.css = [], [], [BASE_CSS]
        self.glyph_ids = {}
        self.n = 0

    def uid(self, prefix):
        self.n += 1
        return f"{prefix}{self.n}"

    def add(self, *parts):
        self.body.extend(parts)

    def glyph_ref(self, font, name):
        key = (font.key, name)
        if key not in self.glyph_ids:
            gid = f"{font.key}{font.tt.getGlyphID(name)}"
            self.glyph_ids[key] = gid
            self.defs.append(f'<path id="{gid}" d="{font.path(name)}"/>')
        return self.glyph_ids[key]

    def text(self, x, y, s, font, size, fill, anchor="start", ls=0, cls="", style=""):
        """Lay out `s` as outlined glyphs with its baseline at (x, y)."""
        if anchor == "middle":
            x -= font.width(s, size, ls) / 2
        elif anchor == "end":
            x -= font.width(s, size, ls)
        k = size / font.upm
        uses, pen = [], 0.0
        for ch in s:
            name = font.glyph(ch)
            if not ch.isspace():
                uses.append(f'<use href="#{self.glyph_ref(font, name)}" x="{pen:.0f}"/>')
            pen += font.adv[name] + ls / k
        out = (f'<g transform="translate({x:.2f} {y:.2f}) scale({k:.5f} {-k:.5f})" '
               f'fill="{fill}">{"".join(uses)}</g>')
        # Animations own `transform`, so they go on a wrapper, never on the placed group.
        if cls or style:
            c = f' class="{cls}"' if cls else ""
            st = f' style="{style}"' if style else ""
            out = f"<g{c}{st}>{out}</g>"
        return out

    def clip_rect(self, x, y, w, h, rx=0):
        cid = self.uid("c")
        self.defs.append(f'<clipPath id="{cid}"><rect x="{x:g}" y="{y:g}" width="{w:g}" '
                         f'height="{h:g}" rx="{rx:g}"/></clipPath>')
        return cid

    def glow_filter(self, dev=8):
        fid = self.uid("glow")
        self.defs.append(f'<filter id="{fid}" x="-30%" y="-60%" width="160%" height="220%">'
                         f'<feGaussianBlur stdDeviation="{dev}"/></filter>')
        return fid

    def card_path(self):
        # Ticker rounds the top, footer the bottom; the panels in between are
        # square, so the stack reads as one screen.
        h, r = self.h, 14
        if self.corners == "top":
            return f"M0 {h}V{r}A{r} {r} 0 0 1 {r} 0H{W - r}A{r} {r} 0 0 1 {W} {r}V{h}Z"
        if self.corners == "bottom":
            return f"M0 0H{W}V{h - r}A{r} {r} 0 0 1 {W - r} {h}H{r}A{r} {r} 0 0 1 0 {h - r}Z"
        return f"M0 0H{W}V{h}H0Z"

    def render(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{self.h}" '
                f'viewBox="0 0 {W} {self.h}" role="img" aria-labelledby="t">'
                f'<title id="t">{esc(self.title)}</title>'
                f'<defs><clipPath id="card"><path d="{self.card_path()}"/></clipPath>'
                f'{"".join(self.defs)}</defs><style>{"".join(self.css)}</style>'
                f'<g clip-path="url(#card)"><rect width="{W}" height="{self.h}" fill="{BG}"/>'
                f'{"".join(self.body)}</g></svg>')

    def save(self):
        OUT.mkdir(parents=True, exist_ok=True)
        path = OUT / f"{self.name}.svg"
        path.write_text(self.render(), encoding="utf-8")
        print(f"  {OUT.name}/{path.name:16} {path.stat().st_size / 1024:7.1f} KB")


# ----------------------------------------------------------------- images ---
_cache = {}


def data_uri(key, make):
    """Encode an image once and reuse it for both themes."""
    if key not in _cache:
        mime, raw = make()
        _cache[key] = f"data:{mime};base64,{base64.b64encode(raw).decode()}"
    return _cache[key]


def jpeg(im, quality=80):
    buf = io.BytesIO()
    im.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return "image/jpeg", buf.getvalue()


def png(im, colors=None):
    if colors:
        im = im.quantize(colors, method=Image.Quantize.FASTOCTREE)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "image/png", buf.getvalue()


def banner_uri():
    def make():
        im = Image.open(IMG / "banner-goku-vegeta.png")
        return jpeg(im.resize((1600, 900), Image.LANCZOS), 80)
    return data_uri("banner", make)


def dome_uri(px):
    """The radar's green screen, cut from the reference frame (the case is drawn)."""
    def make():
        im = Image.open(IMG / "dragon-radar-reference.png")
        cx, cy, r = 607, 332, 189
        return jpeg(im.crop((cx - r, cy - r, cx + r, cy + r)).resize((px, px), Image.LANCZOS), 84)
    return data_uri(("dome", px), make)


def orb_uri(stars, px):
    def make():
        im = Image.open(IMG / "orbs" / f"orb-{stars}-star.png").convert("RGBA")
        return png(im.resize((px, px), Image.LANCZOS), 128)
    return data_uri(("orb", stars, px), make)


def sprite(filename, px, focus):
    """A looping clip as a vertical strip of square frames, plus its loop length.

    GIFs inside an SVG image do not reliably animate, so the frames are stacked
    into one JPEG and stepped through with CSS instead.
    """
    def make():
        gif = Image.open(IMG / "techniques" / filename)
        frames, durs = [], []
        for fr in ImageSequence.Iterator(gif):
            frames.append(fr.convert("RGB"))
            durs.append(fr.info.get("duration", 100) or 100)
        step = 2 if sum(durs) / len(durs) < 60 else 1  # very fast clips keep every other frame
        frames, durs = frames[::step], [sum(durs[i:i + step]) for i in range(0, len(durs), step)]
        w, h = frames[0].size
        s = min(w, h)
        x0 = round((w - s) * focus[0])
        y0 = round((h - s) * focus[1])
        strip = Image.new("RGB", (px, px * len(frames)))
        for i, fr in enumerate(frames):
            strip.paste(fr.crop((x0, y0, x0 + s, y0 + s)).resize((px, px), Image.LANCZOS), (0, i * px))
        mime, raw = jpeg(strip, 74)
        sprite.meta[filename] = (len(frames), sum(durs) / 1000)
        return mime, raw
    uri = data_uri(("sprite", filename, px), make)
    return uri, sprite.meta[filename]


sprite.meta = {}


# ---------------------------------------------------------------- helpers ---
def wrap(font, text, size, maxw, ls=0.0):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and font.width(trial, size, ls) > maxw:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur] if cur else lines


def fit(font, lines, maxw, maxsize, ls_em=0.0):
    size = min(maxw / (font.width(l, 1) + ls_em * (len(l) - 1)) for l in lines)
    return min(maxsize, size)


def bracket(d, x, y, label, size=13):
    d.add(d.text(x, y, f"[ {label} ]", MONO_B, size, GREEN, ls=0.6))


def grid(d, x, y, w, h, step=40):
    pid = d.uid("grid")
    d.defs.append(f'<pattern id="{pid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse" '
                  f'x="{x:g}" y="{y:g}"><path d="M{step} 0H0V{step}" fill="none" stroke="{LINE}" '
                  f'stroke-width="1"/></pattern>')
    d.add(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{PANEL}"/>'
          f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="url(#{pid})"/>'
          f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="{PANEL}" opacity="{GRID_VEIL}"/>')


def status_dot(d, x, y, color):
    return (f'<g class="blink"><circle cx="{x}" cy="{y}" r="4" fill="{color}"/>'
            f'<circle cx="{x}" cy="{y}" r="8" fill="{color}" opacity=".25"/></g>')


def pill(d, x, y, label, h=34, fg=None, bg=None, stroke=None, dot=None):
    """A rounded label; returns its width."""
    fg, bg, stroke = fg or TEXT, bg or TILE, stroke or LINE
    pad = 16
    tw = MONO_B.width(label, 13, 0.8)
    w = tw + pad * 2 + (18 if dot else 0)
    out = [f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h / 2}" fill="{bg}" stroke="{stroke}"/>']
    tx = x + pad
    if dot:
        out.append(status_dot(d, tx + 4, y + h / 2, dot))
        tx += 18
    out.append(d.text(tx, y + h / 2 + 4.6, label, MONO_B, 13, fg, ls=0.8))
    d.add("".join(out))
    return w


# --------------------------------------------------------------- sections ---
def ticker():
    H = 46
    d = SVG("ticker", H, "Scouter feed: " + " / ".join(PROFILE["ticker"]), corners="top")
    d.add(f'<rect width="{W}" height="{H}" fill="{TICK_BG}"/>')
    size = 12
    labels = PROFILE["ticker_buttons"]
    arrow = MONO_B.width("→ ", size) + 6
    lit_w = 40 + arrow + MONO_B.width(labels[1], size, 0.6)
    dark_w = 40 + MONO_B.width(labels[0], size, 0.6)
    area = W - lit_w - dark_w
    seg, x = [], 0.0
    for msg in PROFILE["ticker"]:
        seg.append(f'<rect x="{x:g}" y="{H / 2 - 3:g}" width="6" height="6" fill="{GREEN}"/>')
        x += 14
        seg.append(d.text(x, H / 2 + 4.3, "SCOUTER FEED", MONO_B, size - 1, GREEN, ls=0.4))
        x += MONO_B.width("SCOUTER FEED", size - 1, 0.4) + 22
        seg.append(d.text(x, H / 2 + 4.3, msg, MONO, size, MUTED))
        x += MONO.width(msg, size) + 56
    period = x
    copies = int(area // period) + 2
    group = "".join(f'<g transform="translate({i * period:.1f} 0)">{"".join(seg)}</g>' for i in range(copies))
    d.css.append(f".mq{{animation:mq {period / 38:.1f}s linear infinite}}"
                 f"@keyframes mq{{to{{transform:translateX(-{period:.1f}px)}}}}")
    cid = d.clip_rect(0, 0, area, H)
    d.add(f'<g clip-path="url(#{cid})"><g transform="translate(22 0)"><g class="mq">{group}</g></g></g>')
    d.add(f'<rect x="{area:g}" y="0" width="{dark_w:g}" height="{H}" fill="{BTN_BG}"/>')
    d.add(d.text(area + 20, H / 2 + 4.6, labels[0], MONO_B, size, BTN_FG, ls=0.6))
    bx = area + dark_w
    d.add(f'<rect x="{bx:g}" y="0" width="{lit_w:g}" height="{H}" fill="{ORANGE}"/>')
    d.css.append(".nudge{animation:nudge 1.6s ease-in-out infinite}@keyframes nudge{50%{transform:translateX(4px)}}")
    d.add(f'<g class="nudge">{d.text(bx + 20, H / 2 + 4.6, "→", MONO_B, size, ON_ORANGE)}</g>')
    d.add(d.text(bx + 20 + arrow, H / 2 + 4.6, labels[1], MONO_B, size, ON_ORANGE, ls=0.6))
    d.add(f'<rect y="{H - 1}" width="{W}" height="1" fill="{LINE}"/>')
    d.save()


def fight(d, ih):
    """The banner art, alive: a slow push-in, speed lines, and a punch landing every few seconds."""
    ix, iy = 318, 318  # where the fist meets the face
    rng = random.Random(9)
    d.css.append(
        f".zoom{{transform-origin:{ix}px {iy}px;animation:zoom 9s ease-in-out infinite alternate}}"
        "@keyframes zoom{from{transform:scale(1.02)}to{transform:scale(1.09)}}"
        ".shake{animation:shake 3.2s linear infinite}"
        "@keyframes shake{0%,78%,92%,100%{transform:translate(0,0)}80%{transform:translate(-9px,5px)}"
        "82%{transform:translate(7px,-6px)}84%{transform:translate(-5px,3px)}86%{transform:translate(4px,-2px)}"
        "88%{transform:translate(-2px,1px)}}"
        ".flash{animation:flash 3.2s linear infinite}"
        "@keyframes flash{0%,78%{opacity:0}80%{opacity:.85}90%,100%{opacity:0}}"
        f".ring{{transform-origin:{ix}px {iy}px;animation:ring 3.2s ease-out infinite}}"
        "@keyframes ring{0%,79%{transform:scale(.1);opacity:0}80%{opacity:.9}100%{transform:scale(2.6);opacity:0}}"
        ".kiaura{animation:kiaura .5s steps(2) infinite}@keyframes kiaura{50%{opacity:.35}}"
        ".sl{animation:sl linear infinite}@keyframes sl{to{stroke-dashoffset:-1400}}"
        ".pt{animation:pt linear infinite}"
        "@keyframes pt{from{transform:translate(0,0);opacity:0}10%{opacity:1}to{transform:translate(-700px,-255px);opacity:0}}")
    d.defs.append(
        '<radialGradient id="fl"><stop offset="0" stop-color="#fff"/>'
        '<stop offset=".35" stop-color="#FFF4C8" stop-opacity=".85"/>'
        '<stop offset="1" stop-color="#FFD23F" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="au"><stop offset="0" stop-color="#FF2A14" stop-opacity=".3"/>'
        '<stop offset="1" stop-color="#FF2A14" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="fadeb" x1="0" y1="0" x2="0" y2="1"><stop offset=".5" stop-color="{BG}" stop-opacity="0"/>'
        f'<stop offset=".85" stop-color="{BG}" stop-opacity=".7"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
        '<filter id="mb" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>'
        '<mask id="calm"><rect x="-200" y="-200" width="1400" height="1000" fill="#fff"/>'
        '<ellipse cx="560" cy="250" rx="330" ry="200" fill="#000" filter="url(#mb)"/></mask>')
    lines = []
    for _ in range(46):
        off = rng.uniform(-620, 620)
        lines.append(f'<line x1="-900" y1="{off:.0f}" x2="900" y2="{off:.0f}" stroke="#fff" '
                     f'stroke-width="{rng.choice([1, 1.5, 2, 2, 3, 4])}" '
                     f'stroke-dasharray="{rng.uniform(80, 260):.0f} {rng.uniform(300, 900):.0f}" '
                     f'stroke-linecap="round" opacity="{rng.uniform(.25, .7):.2f}" class="sl" '
                     f'style="animation-duration:{rng.uniform(.45, 1.1):.2f}s;animation-delay:-{rng.uniform(0, 1):.2f}s"/>')
    sparks = "".join(
        f'<circle cx="{rng.uniform(500, 1100):.0f}" cy="{rng.uniform(150, 650):.0f}" r="{rng.uniform(1.5, 3.5):.1f}" '
        f'fill="{rng.choice(["#FFF2C2", "#FFD23F", "#FF6A3D"])}" class="pt" '
        f'style="animation-duration:{rng.uniform(1.6, 3.2):.2f}s;animation-delay:-{rng.uniform(0, 3):.2f}s"/>'
        for _ in range(26))
    cid = d.clip_rect(0, 0, W, ih)
    d.add(f'<g clip-path="url(#{cid})"><g class="shake"><g class="zoom">'
          f'<image href="{banner_uri()}" x="-10" y="-6" width="{W + 20}" height="{(W + 20) * 9 / 16:.1f}"/>'
          f'<ellipse cx="820" cy="420" rx="260" ry="200" fill="url(#au)" class="kiaura"/>'
          f'<g style="mix-blend-mode:screen" mask="url(#calm)"><g transform="translate(560 300) rotate(20)">'
          f'{"".join(lines)}</g></g></g></g>'
          f'<g style="mix-blend-mode:screen">{sparks}</g>'
          f'<circle cx="{ix}" cy="{iy}" r="150" fill="url(#fl)" class="flash"/>'
          f'<circle cx="{ix}" cy="{iy}" r="60" fill="none" stroke="#FFF4C8" stroke-width="6" class="ring"/>'
          f'<rect width="{W}" height="{ih}" fill="url(#fadeb)"/></g>')


def hero():
    """The fight banner with the Saiyan ID card resting over its lower edge."""
    p = PROFILE
    ih = round(W * 9 / 16)
    cx0, cx1, ctop, H = 26, W - 26, 376, 708
    d = SVG("hero", H, f"{p['name']}: {', '.join(r.lower() for r in p['roles'])}. "
            f"{p['tagline'].capitalize()} Power level {p['power']}.")
    fight(d, ih)

    # The card: see-through at the top, fading into the page at the bottom.
    a0, a1 = CARD_ALPHA
    d.defs.append(f'<linearGradient id="cardg" x1="0" y1="0" x2="0" y2="1">'
                  f'<stop offset="0" stop-color="{CARD}" stop-opacity="{a0}"/>'
                  f'<stop offset=".6" stop-color="{CARD}" stop-opacity="{a1}"/>'
                  f'<stop offset="1" stop-color="{BG}"/></linearGradient>'
                  f'<linearGradient id="edgeg" x1="0" y1="0" x2="0" y2="1">'
                  f'<stop offset="0" stop-color="{EDGE}" stop-opacity="{EDGE_ALPHA}"/>'
                  f'<stop offset=".75" stop-color="{EDGE}" stop-opacity="0"/></linearGradient>')
    r = 14
    shape = (f"M{cx0} {H}V{ctop + r}A{r} {r} 0 0 1 {cx0 + r} {ctop}H{cx1 - r}"
             f"A{r} {r} 0 0 1 {cx1} {ctop + r}V{H}")
    d.add(f'<rect x="{cx0}" y="{ih}" width="{cx1 - cx0}" height="{H - ih}" fill="{BG}"/>')
    d.add(f'<path d="{shape}Z" fill="url(#cardg)"/>')
    d.add(f'<path d="{shape}" fill="none" stroke="url(#edgeg)" stroke-width="1.5"/>')

    x = 70
    d.add(f'<g class="up" style="animation-delay:.2s">')
    bracket(d, x, ctop + 50, "SAIYAN ID")
    d.add("</g>")
    size = fit(BOLD, [p["name"]], 560, 150, -0.01)
    base = ctop + 60 + size * 0.74
    ls = -0.01 * size
    halo_col, halo_op = HALO
    if GLOW:
        aura = d.glow_filter(size / 7)
        d.css.append(".aura{transform-box:fill-box;transform-origin:50% 70%;animation:aura 1.4s ease-in-out infinite}"
                     "@keyframes aura{0%,100%{opacity:.3;transform:scale(1)}50%{opacity:.6;transform:scale(1.03,1.07)}}")
        d.add(f'<g filter="url(#{aura})"><g class="aura">{d.text(x - 4, base, p["name"], BOLD, size, ORANGE, ls=ls)}</g></g>')
    halo = d.glow_filter(size / 14)
    d.add(f'<g class="up" style="animation-delay:.3s"><g filter="url(#{halo})" opacity="{halo_op}">'
          f'{d.text(x - 4, base, p["name"], BOLD, size, halo_col, ls=ls)}</g>'
          f'{d.text(x - 4, base, p["name"], BOLD, size, TEXT, ls=ls)}</g>')
    roles = " · ".join(p["roles"])
    rsize = fit(MED, [roles], 560, 27, 0.1)
    d.add(d.text(x, base + 52, roles, MED, rsize, GOLD, ls=rsize * 0.1, cls="up", style="animation-delay:.5s"))
    tag = p["tagline"]
    tw = MONO_B.width(tag, 15, 0.9)
    d.add(d.text(x, base + 96, tag, MONO_B, 15, MUTED if GLOW else TEXT, ls=0.9, cls="up", style="animation-delay:.6s"))
    d.add(f'<rect x="{x + tw + 10:.1f}" y="{base + 82}" width="10" height="17" fill="{GREEN}" class="blink"/>')

    # Scouter readout.
    sx, sy, sw, sh = 664, ctop + 56, 270, 222
    d.add(f'<g class="up" style="animation-delay:.45s">'
          f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="8" fill="{CARD}" fill-opacity="{a0 * .55:.2f}" '
          f'stroke="{EDGE}" stroke-opacity="{EDGE_ALPHA * .9:.2f}"/>')
    d.add(d.text(sx + 20, sy + 34, "SCOUTER // READING", MONO_B, 13, MUTED, ls=0.8))
    psize = 64
    if GLOW:
        pf = d.glow_filter(8)
        d.add(f'<g filter="url(#{pf})" opacity=".6">{d.text(sx + 18, sy + 100, p["power"], BOLD, psize, GREEN)}</g>')
    d.add(d.text(sx + 18, sy + 100, p["power"], BOLD, psize, GREEN))
    bw = sw - 40
    d.css.append(".charge{animation:charge 2.4s cubic-bezier(.16,1,.3,1) both}"
                 "@keyframes charge{from{transform:scaleX(0)}}")
    d.add(f'<rect x="{sx + 20}" y="{sy + 118}" width="{bw}" height="9" rx="4.5" fill="{GREEN}" opacity=".18"/>'
          f'<rect x="{sx + 20}" y="{sy + 118}" width="{bw * .92:.0f}" height="9" rx="4.5" fill="{GREEN}" '
          f'class="charge" style="transform-origin:{sx + 20}px 0"/>')
    for i, (k, v) in enumerate(p["scouter"]):
        yy = sy + 156 + i * 24
        d.add(d.text(sx + 20, yy, k, MONO_B, 12, MUTED, ls=0.8))
        d.add(d.text(sx + sw - 20, yy, v, MONO_B, 12, GREEN if k == "STATUS" else TEXT, "end", 0.8))
    d.add("</g>")
    d.save()


def radar(d, cx, cy, R):
    """A dragon radar: drawn silver case, the reference's green screen, a live sweep."""
    r = R - 26
    period = 3.6
    d.defs.append(
        '<linearGradient id="caseG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4F6F8"/>'
        '<stop offset=".45" stop-color="#C9CFD4"/><stop offset=".75" stop-color="#9AA3AA"/>'
        '<stop offset="1" stop-color="#D7DCE0"/></linearGradient>'
        '<linearGradient id="bezelG" x1="1" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#F7F9FA"/>'
        '<stop offset="1" stop-color="#8E979E"/></linearGradient>'
        '<linearGradient id="crownG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8E979E"/>'
        '<stop offset=".35" stop-color="#F2F4F6"/><stop offset="1" stop-color="#7D868D"/></linearGradient>'
        '<radialGradient id="vigG" cx=".5" cy=".5" r=".5"><stop offset=".78" stop-color="#000" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#03250A" stop-opacity=".33"/></radialGradient>'
        '<radialGradient id="blipG"><stop offset="0" stop-color="#FFE08A"/><stop offset=".5" stop-color="#FFA21F"/>'
        '<stop offset="1" stop-color="#FFA21F" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="domeC"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
        '<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>')
    d.css.append(
        f".rsweep{{transform-origin:{cx}px {cy}px;animation:rsweep {period}s linear infinite}}"
        "@keyframes rsweep{to{transform:rotate(360deg)}}"
        f".rpulse{{transform-origin:{cx}px {cy}px;animation:rpulse {period}s ease-out infinite}}"
        "@keyframes rpulse{from{transform:scale(.05);opacity:.9}to{transform:scale(1);opacity:0}}"
        f".rblip{{animation:rblip {period}s linear infinite}}"
        "@keyframes rblip{0%,8%{opacity:1}60%{opacity:.25}100%{opacity:1}}"
        f".rglow{{animation:rglow {period}s ease-in-out infinite}}@keyframes rglow{{50%{{opacity:.38}}}}")
    out = [f'<circle cx="{cx}" cy="{cy}" r="{R - 6}" fill="#3CFF5A" opacity=".22" filter="url(#soft)" class="rglow"/>',
           f'<rect x="{cx - 16}" y="{cy - R - 22}" width="32" height="30" fill="url(#crownG)" stroke="#2B3035" stroke-width="3"/>',
           f'<rect x="{cx - 30}" y="{cy - R - 50}" width="60" height="34" rx="6" fill="url(#crownG)" stroke="#2B3035" stroke-width="3"/>',
           '<g stroke="#5E676E" stroke-width="2" opacity=".7">'
           + "".join(f'<line x1="{cx - 24 + i * 6}" y1="{cy - R - 45}" x2="{cx - 24 + i * 6}" y2="{cy - R - 21}"/>'
                     for i in range(9)) + "</g>",
           f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#caseG)" stroke="#2B3035" stroke-width="4"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{R - 12}" fill="none" stroke="url(#bezelG)" stroke-width="10"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{r + 3}" fill="#1E2428"/>']
    inner = [f'<image href="{dome_uri(400)}" x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}"/>']
    wedges = []
    for i in range(18):
        b0, b1 = math.radians(-i * 3.5), math.radians(-(i + 1) * 3.5)
        wedges.append(f'<path d="M{cx} {cy}L{cx + r * math.cos(b0):.1f} {cy + r * math.sin(b0):.1f}'
                      f'A{r} {r} 0 0 0 {cx + r * math.cos(b1):.1f} {cy + r * math.sin(b1):.1f}Z" '
                      f'opacity="{.5 * (1 - i / 18):.2f}"/>')
    inner.append(f'<g class="rsweep" fill="#fff">{"".join(wedges)}'
                 f'<line x1="{cx}" y1="{cy}" x2="{cx + r}" y2="{cy}" stroke="#fff" stroke-width="2" opacity=".85"/></g>')
    inner.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#F4FFE6" stroke-width="3" class="rpulse"/>')
    # The blips already on the reference screen, as fractions of its radius.
    for bx, by in [(.27, -.48), (-.49, -.22), (-.77, -.04), (-.07, -.09), (.81, -.15), (-.49, .44), (.28, .7)]:
        x, y = cx + bx * r, cy + by * r
        ang = math.degrees(math.atan2(by, bx)) % 360
        inner.append(f'<g class="rblip" style="animation-delay:{ang / 360 * period - period:.2f}s">'
                     f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * .085:.1f}" fill="url(#blipG)"/>'
                     f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * .026:.1f}" fill="#FFD27A"/></g>')
    inner.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#vigG)"/>')
    out.append(f'<g clip-path="url(#domeC)">{"".join(inner)}</g>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#0E1A10" stroke-width="3"/>')
    d.add(f'<g class="fade" style="animation-delay:.3s">{"".join(out)}</g>')


def mission():
    m = PROFILE["mission"]
    H = 410
    d = SVG("mission", H, f"Current mission: {''.join(m['name'])}. {m['lead']} {m['detail']} Status: {m['status'].lower()}.")
    grid(d, 0, 0, W, H)
    d.add(f'<rect width="{W}" height="1" fill="{LINE}"/>')
    x = 56
    bracket(d, x, 62, "CURRENT MISSION")

    size, base = 96, 156
    a, b = m["name"]
    aw = BOLD.width(a, size, -0.01 * size)
    cid = d.clip_rect(0, base - size, W, size * 1.25)
    glow = ""
    if GLOW:
        f = d.glow_filter(7)
        glow = (f'<g filter="url(#{f})" opacity=".5">{d.text(x - 4, base, a, BOLD, size, ORANGE, ls=-0.01 * size)}'
                f'{d.text(x - 4 + aw, base, b, BOLD, size, ORANGE, ls=-0.01 * size)}</g>')
    d.add(f'<g clip-path="url(#{cid})"><g class="rise" style="animation-delay:.1s">{glow}'
          f'{d.text(x - 4, base, a, BOLD, size, TEXT, ls=-0.01 * size)}'
          f'{d.text(x - 4 + aw, base, b, BOLD, size, ORANGE, ls=-0.01 * size)}</g></g>')

    # Lead sentence in full colour, the detail muted, wrapped together.
    tsize, lh, maxw = 27, 35, 560
    words = [(w, TEXT) for w in m["lead"].split()] + [(w, MUTED) for w in m["detail"].split()]
    lines, cur, cw = [], [], 0.0
    space = MED.width(" ", tsize)
    for wd, col in words:
        ww = MED.width(wd, tsize)
        if cur and cw + space + ww > maxw:
            lines.append(cur)
            cur, cw = [], 0.0
        cur.append((wd, col, ww))
        cw += (space if cw else 0) + ww
    lines.append(cur)
    y = 212
    parts = []
    for line in lines:
        lx = x
        for wd, col, ww in line:
            parts.append(d.text(lx, y, wd, MED, tsize, col))
            lx += ww + space
        y += lh
    d.add(f'<g class="up" style="animation-delay:.3s">{"".join(parts)}</g>')

    py = y + 8
    d.add('<g class="up" style="animation-delay:.45s">')
    pw = pill(d, x, py, m["status"], dot=GREEN, fg=GREEN)
    bx = x + pw + 12
    label = f'{m["button"]} →'
    bw = MONO_B.width(label, 13, 0.8) + 32
    d.add(f'<rect x="{bx:.1f}" y="{py}" width="{bw:.1f}" height="34" rx="5" fill="{ORANGE}"/>'
          + d.text(bx + 16, py + 21.6, label, MONO_B, 13, ON_ORANGE, ls=0.8))
    d.add("</g>")

    rcx, rcy, rr = 806, 218, 128
    radar(d, rcx, rcy, rr)
    d.add(d.text(rcx, rcy + rr + 46, "SIGNALS IN RANGE // 07", MONO_B, 12, DIM, "middle", 0.8))
    d.save()


def techniques():
    items = PROFILE["techniques"]
    arsenal = PROFILE["arsenal"]
    x, gap = 56, 20
    tw = (W - 2 * x - gap * (len(items) - 1)) / len(items)
    ty, th = 92, 136
    ic = 80

    chip_h, chip_gap, csize = 34, 10, 13
    chip_rows, cur, cur_w = [], [], 0.0
    for t in arsenal:
        cw = MONO_B.width(t, csize, 0.8) + 30
        if cur and cur_w + chip_gap + cw > W - 2 * x:
            chip_rows.append(cur)
            cur, cur_w = [], 0.0
        cur.append((t, cw))
        cur_w += (chip_gap if cur_w else 0) + cw
    chip_rows.append(cur)
    ay = ty + th + 52
    H = round(ay + 22 + len(chip_rows) * (chip_h + chip_gap) + 34)

    d = SVG("techniques", H, "Techniques: " + ", ".join(f"{n.lower()} ({w.lower()})" for n, w, _, _ in items)
            + ". Arsenal: " + ", ".join(t.lower() for t in arsenal) + ".")
    grid(d, 0, 0, W, H)
    d.add(f'<rect width="{W}" height="1" fill="{LINE}"/>')
    bracket(d, x, 60, "TECHNIQUES")
    d.add(d.text(W - x, 60, PROFILE["techniques_note"], MONO_B, 13, MUTED, "end", 0.8))

    nsize = 30
    for i, (name, what, clip, focus) in enumerate(items):
        mx = x + i * (tw + gap)
        uri, (n, dur) = sprite(clip, 160, focus)
        k = f"sp{i}"
        d.css.append(f".{k}{{animation:{k} {dur:.2f}s steps({n}) infinite}}"
                     f"@keyframes {k}{{to{{transform:translateY(-{n * ic}px)}}}}")
        ix, iy = mx + 16, ty + (th - ic) / 2
        cid = d.clip_rect(ix, iy, ic, ic, 6)
        tx = ix + ic + 16
        maxw = mx + tw - 14 - tx
        nlines = wrap(BOLD, name, nsize, maxw)
        wlines = wrap(MONO_B, what, 11, maxw, 0.6)
        block = len(nlines) * nsize * 0.9 + 8 + len(wlines) * 15
        by = ty + (th - block) / 2 + nsize * 0.74
        parts = [f'<rect x="{mx}" y="{ty}" width="{tw:.1f}" height="{th}" rx="8" fill="{TILE}" stroke="{LINE}"/>',
                 f'<g clip-path="url(#{cid})"><g class="{k}"><image href="{uri}" x="{ix}" y="{iy:.1f}" '
                 f'width="{ic}" height="{n * ic}" preserveAspectRatio="none"/></g></g>',
                 f'<rect x="{ix}" y="{iy:.1f}" width="{ic}" height="{ic}" rx="6" fill="none" stroke="{LINE}"/>']
        for j, ln in enumerate(nlines):
            parts.append(d.text(tx, by + j * nsize * 0.9, ln, BOLD, nsize, TEXT, ls=-0.2))
        wy = by + (len(nlines) - 1) * nsize * 0.9 + 24
        for j, ln in enumerate(wlines):
            parts.append(d.text(tx, wy + j * 15, ln, MONO_B, 11, MUTED, ls=0.6))
        d.add(f'<g class="up" style="animation-delay:{0.2 + i * 0.15:.2f}s">{"".join(parts)}</g>')

    d.add(d.text(x, ay, "ARSENAL", MONO_B, 13, GOLD, ls=0.8))
    cy = ay + 20
    for r, row in enumerate(chip_rows):
        cx = x
        for j, (t, cw) in enumerate(row):
            d.add(f'<g class="up" style="animation-delay:{0.6 + (r * len(row) + j) * 0.05:.2f}s">'
                  f'<rect x="{cx:.1f}" y="{cy}" width="{cw:.1f}" height="{chip_h}" rx="{chip_h / 2}" fill="{TILE}" stroke="{LINE}"/>'
                  + d.text(cx + 15, cy + chip_h / 2 + 4.6, t, MONO_B, csize, TEXT, ls=0.8) + "</g>")
            cx += cw + chip_gap
        cy += chip_h + chip_gap
    d.save()


def footer():
    H = 112
    c = PROFILE["footer"]
    d = SVG("footer", H, f"{PROFILE['name']}. {c['right'].capitalize()}.", corners="bottom")
    d.add(f'<rect width="{W}" height="{H}" fill="{PANEL2 if not GLOW else BG}"/>')
    d.add(f'<rect width="{W}" height="1" fill="{LINE}"/>')
    y = H / 2
    d.add(d.text(56, y + 5, c["left"], MONO_B, 13, MUTED, ls=0.8))
    rw = MONO_B.width(c["right"], 13, 0.8)
    d.add(f'<rect x="{W - 56 - rw - 18:.1f}" y="{y - 4}" width="9" height="9" fill="{GOLD}" class="blink"/>'
          + d.text(W - 56, y + 5, c["right"], MONO_B, 13, GOLD, "end", 0.8))
    d.css.append(".bob{animation:bob 2.6s ease-in-out infinite}@keyframes bob{50%{transform:translateY(-6px)}}")
    size, step = 42, 56
    glow = d.glow_filter(7)
    x0 = W / 2 - step * 3
    for i in range(7):
        ox = x0 + i * step
        d.add(f'<g class="bob" style="animation-delay:{i * .18:.2f}s">'
              f'<circle cx="{ox}" cy="{y + 2}" r="{size * .5}" fill="{ORANGE}" opacity=".45" filter="url(#{glow})"/>'
              f'<image href="{orb_uri(i + 1, 96)}" x="{ox - size / 2}" y="{y - size / 2}" width="{size}" height="{size}"/></g>')
    d.save()


if __name__ == "__main__":
    for theme in THEMES:
        set_theme(theme)
        print(f"Writing {theme} panels to {OUT}")
        ticker()
        hero()
        mission()
        techniques()
        footer()
