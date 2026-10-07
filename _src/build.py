#!/usr/bin/env python3
"""Builds the Dragon Ball Z themed SVG panels around the banner in the profile README.

Edit PROFILE below, then run:

    pip install fonttools
    python _src/build.py

Every SVG in ../assets is regenerated (the banner, assets/banner.gif, is left
alone). Text is converted to vector outlines (Barlow Condensed + JetBrains Mono,
both OFL — see _src/fonts), so it looks the same on every device without
loading any fonts. Only original motifs are drawn here: scouter readouts, a
dragon radar, ki auras and star orbs. No official artwork is used.
"""
import html
import math
import random
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

SRC = Path(__file__).resolve().parent
OUT = SRC.parent / "assets"

# ---------------------------------------------------------------- content ---
PROFILE = {
    "name": "SUNDAYS",
    "handle": "DEANYADID09-CMYK",
    "url": "GITHUB.COM/DEANYADID09-CMYK",
    # Cycles above the name in the identity panel.
    "roles": ["PRODUCT BUILDER", "AI SYSTEMS", "AUTOMATION"],
    "tagline": "BUILD SYSTEMS. SHIP FAST. KEEP TRAINING.",
    "power": "9,001+",
    # (label, line) rows of the Saiyan file; the motto closes it.
    "file": [
        ("MISSION", "DealEngine: a CRM and deal flow system."),
        ("STATUS", "Active build. A focused operating layer for modern deal flow."),
        ("TRAINING", "Agent architecture, automation and product systems."),
    ],
    "motto": "BUILD SYSTEMS. SHIP FAST. KEEP TRAINING.",
    # (name, detail, panel art: "orb" | "beam" | "graph")
    "techniques": [
        ("AGENT ARCHITECTURE", "REASON · ROUTE · EXECUTE", "graph"),
        ("AUTOMATION", "REPETITIVE WORK → LEVERAGE", "beam"),
        ("PRODUCT SYSTEMS", "INTERFACES PEOPLE RUN WITH", "orb"),
    ],
    "arsenal": ["REACT", "JAVASCRIPT", "VITE", "TAILWIND", "MUI", "FRAMER MOTION", "GITHUB", "AI WORKFLOWS"],
    "ticker": [
        "SUNDAYS — PRODUCT BUILDER · AI SYSTEMS · AUTOMATION",
        "CURRENT MISSION: DEALENGINE",
        "BUILD SYSTEMS. SHIP FAST. KEEP TRAINING.",
        "POWER LEVEL: 9,001+",
    ],
    "ticker_buttons": ["REPOSITORIES", "FOLLOW"],
    "footer": {
        "left": "© 2026 SUNDAYS",
        "mid": "TO BE CONTINUED",
    },
}

# ------------------------------------------------------------------ style ---
# Gi orange, ki gold, Saiyan blue, scouter green on a near-black night sky.
W = 1000
BG, PANEL, PANEL2, LINE = "#09070A", "#120D0B", "#1C140E", "#3A2818"
ORANGE, GOLD, BLUE, GREEN, RED = "#FF8A1F", "#FFD23F", "#4F86FF", "#5CFF7A", "#E8352C"
TEXT, MUTED, DIM = "#FFF3E3", "#B59C84", "#6E5A47"

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
        # Ticker rounds the top, footer the bottom; together with the square
        # banner in between they read as one screen.
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
        path = OUT / f"{self.name}.svg"
        path.write_text(self.render(), encoding="utf-8")
        print(f"  {path.name:16} {path.stat().st_size / 1024:6.1f} KB")


# ---------------------------------------------------------------- helpers ---
def wrap(font, text, size, maxw):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and font.width(trial, size) > maxw:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur] if cur else lines


def fit(font, lines, maxw, maxsize, ls_em=0.0):
    size = min(maxw / (font.width(l, 1) + ls_em * (len(l) - 1)) for l in lines)
    return min(maxsize, size)


def headline(d, lines, x, y, size, fill, anchor="start", delay=0.1, step=0.12, lh=0.86, glow=None):
    """Big condensed caps that rise into place line by line, with an optional ki glow."""
    ls = -0.01 * size
    fid = d.glow_filter(size / 14) if glow else None
    for i, line in enumerate(lines):
        base = y + i * size * lh
        cid = d.clip_rect(0, base - size * 1.1, W, size * 1.4)
        t = d.text(x, base, line, BOLD, size, fill, anchor, ls)
        halo = (f'<g filter="url(#{fid})" opacity=".55">{d.text(x, base, line, BOLD, size, glow, anchor, ls)}</g>'
                if glow else "")
        d.add(f'<g clip-path="url(#{cid})"><g class="rise" style="animation-delay:{delay + i * step:.2f}s">'
              f'{halo}{t}</g></g>')
    return y + (len(lines) - 1) * size * lh


def bracket(d, x, y, label, fill=MUTED, size=12, anchor="start"):
    d.add(d.text(x, y, f"[ {label} ]", MONO_B, size, fill, anchor, ls=0.5))


def hud_corners(d, x, y, w, h, arm=18, color=GREEN):
    """Scouter targeting brackets at each corner of a box."""
    pts = [(x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)]
    path = "".join(f"M{cx + sx * arm} {cy}H{cx}V{cy + sy * arm}" for cx, cy, sx, sy in pts)
    d.add(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2" opacity=".75"/>')


def scanlines(d, x, y, w, h, band=True, color=GREEN):
    """Scouter-lens scanlines plus a slow sweep of light."""
    pid = d.uid("scan")
    d.defs.append(f'<pattern id="{pid}" width="4" height="4" patternUnits="userSpaceOnUse">'
                  f'<rect width="4" height="1" fill="#fff" opacity=".035"/></pattern>')
    d.add(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="url(#{pid})"/>')
    if band:
        gid, name = d.uid("band"), d.uid("sweep")
        d.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
                      f'<stop offset="0" stop-color="{color}" stop-opacity="0"/>'
                      f'<stop offset=".5" stop-color="{color}" stop-opacity=".06"/>'
                      f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient>')
        d.css.append(f".{name}{{animation:{name} 6s linear infinite}}"
                     f"@keyframes {name}{{from{{transform:translateY(-120px)}}to{{transform:translateY({h + 120:.0f}px)}}}}")
        cid = d.clip_rect(x, y, w, h)
        d.add(f'<g clip-path="url(#{cid})"><rect x="{x:g}" y="{y:g}" width="{w:g}" height="120" '
              f'fill="url(#{gid})" class="{name}"/></g>')


def grid(d, x, y, w, h, step=40):
    pid = d.uid("grid")
    d.defs.append(f'<pattern id="{pid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse" '
                  f'x="{x:g}" y="{y:g}"><path d="M{step} 0H0V{step}" fill="none" stroke="{LINE}" '
                  f'stroke-width="1" opacity=".45"/></pattern>')
    d.add(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="url(#{pid})"/>')


def star_path(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append(f"{cx + r * math.cos(a):.1f} {cy + r * math.sin(a):.1f}")
    return "M" + "L".join(pts) + "Z"


# Star positions inside an orb, as fractions of its radius, for 1 to 7 stars.
STAR_LAYOUT = {
    1: [(0, 0)],
    2: [(-.3, -.15), (.3, .15)],
    3: [(0, -.32), (-.3, .2), (.3, .2)],
    4: [(-.28, -.28), (.28, -.28), (-.28, .28), (.28, .28)],
    5: [(0, -.38), (-.36, -.08), (.36, -.08), (-.22, .34), (.22, .34)],
    6: [(-.3, -.34), (.3, -.34), (-.4, 0), (.4, 0), (-.3, .34), (.3, .34)],
    7: [(0, 0), (0, -.42), (0, .42), (-.38, -.2), (.38, -.2), (-.38, .2), (.38, .2)],
}


def orb(d, cx, cy, r, stars=4, glow=False):
    """An original star orb: a glossy orange sphere with red stars inside."""
    gid = d.uid("orb")
    d.defs.append(f'<radialGradient id="{gid}" cx=".38" cy=".32" r=".75">'
                  f'<stop offset="0" stop-color="#FFE3A3"/><stop offset=".35" stop-color="{GOLD}"/>'
                  f'<stop offset=".75" stop-color="{ORANGE}"/><stop offset="1" stop-color="#B24A08"/>'
                  f'</radialGradient>')
    sr = r * (0.22 if stars > 4 else 0.28)
    starp = "".join(f'<path d="{star_path(cx + fx * r, cy + fy * r, sr, sr * .42)}"/>'
                    for fx, fy in STAR_LAYOUT[stars])
    halo = ""
    if glow:
        halo = (f'<circle cx="{cx}" cy="{cy}" r="{r * 1.25:.1f}" fill="{ORANGE}" opacity=".5" '
                f'filter="url(#{d.glow_filter(r / 2.5)})"/>')
    return (f'{halo}<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{gid})"/>'
            f'<g fill="{RED}">{starp}</g>'
            f'<ellipse cx="{cx - r * .32:.1f}" cy="{cy - r * .38:.1f}" rx="{r * .3:.1f}" ry="{r * .16:.1f}" '
            f'fill="#fff" opacity=".55" transform="rotate(-30 {cx - r * .32:.1f} {cy - r * .38:.1f})"/>')


def status_dot(d, x, y, color=GREEN):
    d.add(f'<g class="blink"><circle cx="{x}" cy="{y}" r="4" fill="{color}"/>'
          f'<circle cx="{x}" cy="{y}" r="8" fill="{color}" opacity=".25"/></g>')


def ki_particles(d, x, y, w, h, n, seed, color=GOLD):
    """Sparks of ki drifting upward out of an aura."""
    rng = random.Random(seed)
    d.css.append(".kp{animation:kp linear infinite both}"
                 "@keyframes kp{0%{opacity:0;transform:translateY(0)}15%{opacity:.9}"
                 "100%{opacity:0;transform:translateY(-120px)}}")
    out = []
    for _ in range(n):
        px, py = x + rng.uniform(0, w), y + rng.uniform(h * .3, h)
        out.append(f'<rect x="{px:.0f}" y="{py:.0f}" width="2" height="{rng.uniform(6, 14):.0f}" rx="1" '
                   f'fill="{color}" class="kp" style="animation-duration:{rng.uniform(1.6, 3.2):.2f}s;'
                   f'animation-delay:{rng.uniform(0, 3):.2f}s"/>')
    d.add("".join(out))


# --------------------------------------------------------------- sections ---
def ticker():
    H = 46
    d = SVG("ticker", H, "Scouter feed: " + " / ".join(PROFILE["ticker"]), corners="top")
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
    d.add(f'<rect x="{area:g}" y="0" width="{dark_w:g}" height="{H}" fill="{PANEL2}"/>')
    d.add(d.text(area + 20, H / 2 + 4.6, labels[0], MONO_B, size, TEXT, ls=0.6))
    bx = area + dark_w
    d.add(f'<rect x="{bx:g}" y="0" width="{lit_w:g}" height="{H}" fill="{ORANGE}"/>')
    d.css.append(".nudge{animation:nudge 1.6s ease-in-out infinite}@keyframes nudge{50%{transform:translateX(4px)}}")
    d.add(f'<g class="nudge">{d.text(bx + 20, H / 2 + 4.6, "→", MONO_B, size, BG)}</g>')
    d.add(d.text(bx + 20 + arrow, H / 2 + 4.6, labels[1], MONO_B, size, BG, ls=0.6))
    d.add(f'<rect y="{H - 1}" width="{W}" height="1" fill="{LINE}"/>')
    d.save()


def hero():
    """Saiyan identity under the banner: roles, name in a ki aura, power level."""
    H = 440
    p = PROFILE
    roles = ", ".join(r.lower() for r in p["roles"])
    d = SVG("hero", H, f"{p['name']}: {roles}. {p['tagline'].capitalize()} Power level {p['power']}.")
    px, py, pw, ph = 12, 12, W - 24, H - 24
    d.add(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="{PANEL}"/>')
    grid(d, px, py, pw, ph)
    pool = d.uid("pool")
    d.defs.append(f'<radialGradient id="{pool}" cx=".5" cy=".55" r=".55">'
                  f'<stop offset="0" stop-color="{ORANGE}" stop-opacity=".18"/>'
                  f'<stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>')
    d.add(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="url(#{pool})"/>')
    scanlines(d, px, py, pw, ph)
    d.add(f'<rect x="{px + .5}" y="{py + .5}" width="{pw - 1}" height="{ph - 1}" fill="none" stroke="{LINE}"/>')
    hud_corners(d, 32, 32, W - 64, H - 64)

    bracket(d, 56, 70, "SAIYAN ID", GREEN)
    d.add(d.text(W - 56, 70, f"FIGHTER ID // {p['handle']}", MONO_B, 12, MUTED, "end", 0.5))

    cx = W / 2
    d.add(f'<g class="fade">{orb(d, cx, 104, 18, stars=4, glow=True)}</g>')
    # Roles take turns sliding through a slot above the name.
    n, hold = len(p["roles"]), 3
    cycle = n * hold
    step = 100 / n
    d.css.append(f".role{{animation:role {cycle}s cubic-bezier(.16,1,.3,1) infinite both}}"
                 f"@keyframes role{{0%{{transform:translateY(34px);opacity:0}}"
                 f"{step * .15:.1f}%,{step * .85:.1f}%{{transform:translateY(0);opacity:1}}"
                 f"{step:.1f}%,100%{{transform:translateY(-34px);opacity:0}}}}")
    cid = d.clip_rect(0, 128, W, 42)
    slots = "".join(d.text(cx, 160, role, MED, 30, GOLD, "middle", 4, cls="role",
                           style=f"animation-delay:{i * hold}s") for i, role in enumerate(p["roles"]))
    d.add(f'<g clip-path="url(#{cid})">{slots}</g>')

    # The name, wrapped in a flickering ki aura.
    size = fit(BOLD, [p["name"]], 760, 176, -0.01)
    base_y = 178 + size * 0.72
    aura = d.glow_filter(size / 6)
    d.css.append(".aura{transform-box:fill-box;transform-origin:50% 70%;animation:aura 1.4s ease-in-out infinite}"
                 "@keyframes aura{0%,100%{opacity:.35;transform:scale(1)}50%{opacity:.75;transform:scale(1.04,1.08)}}"
                 ".aura2{animation-duration:.9s;animation-delay:.3s}")
    for cls, col in (("aura", GOLD), ("aura aura2", ORANGE)):
        d.add(f'<g filter="url(#{aura})"><g class="{cls}">'
              f'{d.text(cx, base_y, p["name"], BOLD, size, col, "middle", -0.01 * size)}</g></g>')
    ki_particles(d, cx - 380, base_y - size * 0.9, 760, size, 34, seed=7)
    base = headline(d, [p["name"]], cx, base_y, size, TEXT, "middle", delay=0.15, glow=GOLD)

    sub = p["tagline"]
    sw = MONO_B.width(sub, 13, 0.8)
    d.add(d.text(cx - 8, base + 50, sub, MONO_B, 13, MUTED, "middle", 0.8, cls="up", style="animation-delay:.6s"))
    d.add(f'<rect x="{cx - 8 + sw / 2 + 8:.1f}" y="{base + 38}" width="9" height="15" fill="{GREEN}" class="blink"/>')

    status_dot(d, 60, H - 57)
    d.add(d.text(76, H - 52, f"POWER LEVEL // {p['power']}", MONO_B, 12, GREEN, ls=0.5))
    d.add(d.text(W - 56, H - 52, "SCOUTER: LOCKED", MONO_B, 12, MUTED, "end", 0.5))
    d.save()


def art_orb(d, x, y, w, h):
    """A ki ball charging: a pulsing core inside spinning rings of energy."""
    cx, cy = x + w / 2, y + h / 2
    d.css.append(".charge{transform-box:fill-box;transform-origin:center;animation:charge 1.2s ease-in-out infinite}"
                 "@keyframes charge{50%{transform:scale(1.18)}}"
                 ".spin{transform-box:fill-box;transform-origin:center;animation:spin 3s linear infinite}"
                 "@keyframes spin{to{transform:rotate(360deg)}}")
    rings = "".join(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r}" fill="none" stroke="{GOLD}" '
                    f'stroke-width="2" stroke-dasharray="{r * .9:.0f} {r * .6:.0f}" opacity="{o}"/>'
                    for r, o in ((44, .5), (32, .8)))
    return (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="34" fill="{ORANGE}" opacity=".5" '
            f'filter="url(#{d.glow_filter(12)})" class="charge"/>'
            f'<g class="spin">{rings}</g>'
            f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="18" fill="{GOLD}" class="charge"/>'
            f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="9" fill="#FFF8E0"/>')


def art_beam(d, x, y, w, h):
    """An energy beam firing across the screen from a charged hand-height orb."""
    cy = y + h / 2
    x0, x1 = x + 34, x + w - 18
    d.css.append(".beam{stroke-dasharray:40 18;animation:beam .6s linear infinite}"
                 "@keyframes beam{to{stroke-dashoffset:-58}}"
                 ".fire{transform-box:fill-box;transform-origin:left center;animation:fire 2.4s cubic-bezier(.6,0,.2,1) infinite}"
                 "@keyframes fire{0%,10%{transform:scaleX(0)}45%,85%{transform:scaleX(1)}100%{transform:scaleX(0);opacity:0}}")
    return (f'<g class="fire">'
            f'<line x1="{x0}" y1="{cy}" x2="{x1}" y2="{cy}" stroke="{BLUE}" stroke-width="30" stroke-linecap="round" '
            f'opacity=".55" filter="url(#{d.glow_filter(9)})"/>'
            f'<line x1="{x0}" y1="{cy}" x2="{x1}" y2="{cy}" stroke="#BFD3FF" stroke-width="14" stroke-linecap="round"/>'
            f'<line x1="{x0}" y1="{cy}" x2="{x1}" y2="{cy}" stroke="#fff" stroke-width="5" class="beam"/></g>'
            f'<circle cx="{x0}" cy="{cy}" r="22" fill="{BLUE}" opacity=".6" filter="url(#{d.glow_filter(8)})"/>'
            f'<circle cx="{x0}" cy="{cy}" r="13" fill="#E6EEFF"/>')


def art_graph(d, x, y, w, h):
    """An agent graph: ki pulses routing between nodes to an output."""
    pos = [(.16, .3), (.16, .72), (.5, .2), (.5, .5), (.5, .8), (.84, .5)]
    pts = [(x + w * px, y + h * py) for px, py in pos]
    edges = [(0, 2), (0, 3), (1, 3), (1, 4), (2, 5), (3, 5), (4, 5)]
    d.css.append(".flow{stroke-dasharray:3 9;animation:flow 1.2s linear infinite}"
                 "@keyframes flow{to{stroke-dashoffset:-24}}"
                 ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 1.6s ease-in-out infinite}"
                 "@keyframes pulse{50%{transform:scale(1.35)}}")
    lines = "".join(f'<line x1="{pts[a][0]:.0f}" y1="{pts[a][1]:.0f}" x2="{pts[b][0]:.0f}" y2="{pts[b][1]:.0f}"/>'
                    for a, b in edges)
    nodes = "".join(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="7"/>' for px, py in pts[:-1])
    ox, oy = pts[-1]
    return (f'<g stroke="{ORANGE}" stroke-width="1.5" opacity=".35">{lines}</g>'
            f'<g stroke="{GOLD}" stroke-width="2.5" class="flow">{lines}</g>'
            f'<g fill="{PANEL}" stroke="{GOLD}" stroke-width="2">{nodes}</g>'
            f'<circle cx="{ox:.0f}" cy="{oy:.0f}" r="14" fill="{GREEN}" opacity=".25" class="pulse"/>'
            f'<circle cx="{ox:.0f}" cy="{oy:.0f}" r="8" fill="{GREEN}"/>')


ARTS = {"orb": art_orb, "beam": art_beam, "graph": art_graph}


def lens(d, x, y, w, h, art, seed, delay):
    """One scouter lens: scrolling readout, a technique charging up, scanlines."""
    rng = random.Random(seed)
    d.add(f'<ellipse cx="{x + w / 2}" cy="{y + h + 26}" rx="{w * 0.45}" ry="10" fill="{ORANGE}" '
          f'opacity=".18" filter="url(#{d.glow_filter(10)})"/>')
    d.add(f'<rect x="{x - 7}" y="{y - 7}" width="{w + 14}" height="{h + 14}" rx="6" fill="#0C0907" stroke="{LINE}"/>')
    sg = d.uid("scr")
    d.defs.append(f'<linearGradient id="{sg}" x1="0" y1="0" x2="1" y2="1">'
                  f'<stop offset="0" stop-color="#0E3A1C"/><stop offset="1" stop-color="#061409"/></linearGradient>')
    cid = d.clip_rect(x, y, w, h, 2)
    rows_h = 13
    rows = math.ceil(h / rows_h) + 1
    period = rows * rows_h
    bars = []
    for r in range(rows):
        indent = rng.choice([0, 0, 14, 14, 28, 42])
        cx = x + 14 + indent
        for _ in range(rng.randint(1, 3)):
            bw = rng.uniform(14, w * 0.32)
            if cx + bw > x + w - 14:
                break
            col = rng.choice([GREEN, GREEN, GREEN, MUTED, GOLD if rng.random() < .2 else GREEN])
            for off in (0, period):
                bars.append(f'<rect x="{cx:.1f}" y="{y + 10 + r * rows_h + off:.1f}" width="{bw:.1f}" height="5" '
                            f'rx="2.5" fill="{col}" opacity="{rng.uniform(.2, .45):.2f}"/>')
            cx += bw + 7
    name = d.uid("code")
    d.css.append(f".{name}{{animation:{name} {8 + seed % 3}s linear infinite}}"
                 f"@keyframes {name}{{to{{transform:translateY(-{period}px)}}}}")
    d.add(f'<g clip-path="url(#{cid})" class="fade" style="animation-delay:{delay:.2f}s">'
          f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{sg})"/>'
          f'<g class="{name}">{"".join(bars)}</g>'
          f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{BG}" opacity=".5"/></g>')
    d.add(f'<g clip-path="url(#{cid})"><g class="up" style="animation-delay:{delay + .2:.2f}s">'
          f'{ARTS[art](d, x, y, w, h)}</g></g>')
    scanlines(d, x, y, w, h, band=False)


def dragon_radar(d, cx, cy, r):
    """A dragon radar: green gridded scope, a sweep, and orbs blinking in range."""
    gid = d.uid("rad")
    d.defs.append(f'<radialGradient id="{gid}" cx=".5" cy=".5" r=".5">'
                  f'<stop offset="0" stop-color="#1C5A2A"/><stop offset="1" stop-color="#0A2412"/></radialGradient>')
    d.add(f'<circle cx="{cx}" cy="{cy}" r="{r + 14}" fill="#2A2F33" stroke="#4A5257" stroke-width="2"/>')
    d.add(f'<rect x="{cx - 14}" y="{cy - r - 30}" width="28" height="20" rx="5" fill="#4A5257"/>')
    d.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{gid})"/>')
    cid = d.uid("radclip")
    d.defs.append(f'<clipPath id="{cid}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>')
    step = r / 4
    gl = "".join(f'<line x1="{cx - r}" x2="{cx + r}" y1="{cy + k * step:.1f}" y2="{cy + k * step:.1f}"/>'
                 f'<line y1="{cy - r}" y2="{cy + r}" x1="{cx + k * step:.1f}" x2="{cx + k * step:.1f}"/>'
                 for k in range(-4, 5))
    d.add(f'<g clip-path="url(#{cid})" stroke="{GREEN}" stroke-width="1" opacity=".35">{gl}</g>')
    wedges = []
    for i in range(14):
        a0, a1 = math.radians(-i * 4), math.radians(-(i + 1) * 4)
        wedges.append(f'<path d="M{cx} {cy}L{cx + r * math.cos(a0):.1f} {cy + r * math.sin(a0):.1f}'
                      f'A{r} {r} 0 0 0 {cx + r * math.cos(a1):.1f} {cy + r * math.sin(a1):.1f}Z" '
                      f'opacity="{0.35 * (1 - i / 14):.2f}"/>')
    d.css.append(f".sweep{{transform-origin:{cx}px {cy}px;animation:sweep 4s linear infinite}}"
                 f"@keyframes sweep{{to{{transform:rotate(360deg)}}}}")
    d.add(f'<g class="sweep" fill="{GREEN}">{"".join(wedges)}</g>')
    d.add(f'<path d="{star_path(cx, cy, 7, 3, rot=-90)}" fill="{RED}"/>')
    for i, (bx, by) in enumerate([(.45, -.32), (-.52, .3), (.18, .58), (-.2, -.6), (.62, .22)]):
        d.add(f'<g class="blink" style="animation-delay:{i * .3:.2f}s">'
              f'<circle cx="{cx + r * bx:.1f}" cy="{cy + r * by:.1f}" r="5.5" fill="{GOLD}"/>'
              f'<circle cx="{cx + r * bx:.1f}" cy="{cy + r * by:.1f}" r="10" fill="{GOLD}" opacity=".25"/></g>')
    d.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#0A0F0C" stroke-width="3"/>')


def saiyan_file():
    """Fighter file: mission, status and training, beside a dragon radar."""
    p = PROFILE
    rows = p["file"]
    x0, x1 = 440, W - 56
    size, lh = 25, 32
    wrapped = [wrap(MED, line, size, x1 - x0) for _, line in rows]
    msize = fit(BOLD, ["SHIP FAST. KEEP TRAINING."], x1 - x0, 44)
    motto = wrap(BOLD, p["motto"], msize, x1 - x0)
    H = 70 + sum(56 + len(ls) * lh for ls in wrapped) + 60 + len(motto) * msize * 0.95 + 56
    H = max(H, 560)
    d = SVG("file", round(H), "Saiyan file: " + " ".join(f"{label.capitalize()}: {l}" for label, l in rows)
            + f" Motto: {p['motto'].capitalize()}")
    grid(d, 0, 0, W, H)
    d.add(f'<rect x="12" y="0" width="{W - 24}" height="{H}" fill="{PANEL}" opacity=".55"/>')

    x = 56
    bracket(d, x, 64, "SAIYAN FILE", GREEN)
    headline(d, ["SAIYAN", "FILE"], x - 4, 150, 84, TEXT, glow=ORANGE)
    dragon_radar(d, 196, 380, 104)
    d.add(d.text(x, H - 52, f"FILE // {p['name']}", MONO_B, 12, MUTED, ls=0.5))
    d.add(d.text(x, H - 32, "SIGNALS IN RANGE // 05", MONO_B, 12, DIM, ls=0.5))

    y = 64
    for i, ((label, _), lines) in enumerate(zip(rows, wrapped)):
        delay = 0.3 + i * 0.15
        parts = [f'<line x1="{x0}" x2="{x1}" y1="{y - 18}" y2="{y - 18}" stroke="{LINE}"/>',
                 d.text(x0, y + 8, f"{i + 1:02d} // {label}", MONO_B, 12, ORANGE, ls=0.6)]
        for j, line in enumerate(lines):
            parts.append(d.text(x0, y + 44 + j * lh, line, MED, size, TEXT))
        d.add(f'<g class="up" style="animation-delay:{delay:.2f}s">{"".join(parts)}</g>')
        y += 56 + len(lines) * lh + 8

    y += 10
    parts = [f'<line x1="{x0}" x2="{x1}" y1="{y - 18}" y2="{y - 18}" stroke="{GOLD}" opacity=".6"/>',
             d.text(x0, y + 8, f"{len(rows) + 1:02d} // MOTTO", MONO_B, 12, GOLD, ls=0.6)]
    d.add(f'<g class="up" style="animation-delay:{0.3 + len(rows) * 0.15:.2f}s">{"".join(parts)}</g>')
    headline(d, motto, x0 - 2, y + 22 + msize * 0.72, msize, GOLD,
             delay=0.4 + len(rows) * 0.15, lh=0.95, glow=ORANGE)
    d.save()


def techniques():
    items = PROFILE["techniques"]
    arsenal = PROFILE["arsenal"]
    x = 56
    gap = 28
    mw = (W - 2 * x - gap * (len(items) - 1)) / len(items)
    my, mh = 200, 160

    # Arsenal chips, wrapped into rows under the lenses.
    chip_h, chip_gap, size = 30, 10, 12
    chip_rows, cur, cur_w = [], [], 0.0
    for t in arsenal:
        cw = MONO_B.width(t, size, 0.6) + 28
        if cur and cur_w + chip_gap + cw > W - 2 * x:
            chip_rows.append(cur)
            cur, cur_w = [], 0.0
        cur.append((t, cw))
        cur_w += (chip_gap if cur_w else 0) + cw
    chip_rows.append(cur)
    ay = my + mh + 140
    H = round(ay + 40 + len(chip_rows) * (chip_h + chip_gap) + 40)

    d = SVG("techniques", H, "Techniques: " + ", ".join(f"{n.lower()} ({what.lower()})" for n, what, _ in items)
            + ". Arsenal: " + ", ".join(t.lower() for t in arsenal) + ".")
    grid(d, 0, 0, W, H)
    bracket(d, x, 64, "TECHNIQUES", GREEN)
    headline(d, ["TECHNIQUES"], x - 4, 150, 96, TEXT, delay=0.1, glow=ORANGE)
    online = f"{len(items):02d} TECHNIQUES MASTERED"
    status_dot(d, W - 56 - MONO_B.width(online, 12, 0.5) - 16, 139)
    d.add(d.text(W - 56, 144, online, MONO_B, 12, MUTED, "end", 0.5))

    nsize = fit(BOLD, [n for n, _, _ in items], mw, 44)
    for i, (name, what, art) in enumerate(items):
        mx = x + i * (mw + gap)
        lens(d, mx, my, mw, mh, art, seed=i + 3, delay=0.2 + i * 0.15)
        ly = my + mh + 26
        d.add(f'<g class="up" style="animation-delay:{0.4 + i * 0.15:.2f}s">'
              f'<line x1="{mx - 7}" x2="{mx + mw + 7}" y1="{ly}" y2="{ly}" stroke="{LINE}"/>'
              + d.text(mx - 6, ly + 26, f"{i + 1:02d} / {what}", MONO_B, 12, MUTED, ls=0.5)
              + d.text(mx - 8, ly + 72, name, BOLD, nsize, TEXT, ls=-0.4)
              + "</g>")

    d.add(f'<line x1="{x}" x2="{W - x}" y1="{ay - 4}" y2="{ay - 4}" stroke="{LINE}"/>')
    d.add(d.text(x, ay + 22, "ARSENAL", MONO_B, 12, GOLD, ls=0.6))
    cy = ay + 40
    for r, row in enumerate(chip_rows):
        cx = x
        for j, (t, cw) in enumerate(row):
            delay = 0.6 + (r * len(row) + j) * 0.05
            d.add(f'<g class="up" style="animation-delay:{delay:.2f}s">'
                  f'<rect x="{cx:.1f}" y="{cy}" width="{cw:.1f}" height="{chip_h}" rx="15" fill="{PANEL2}" stroke="{LINE}"/>'
                  + d.text(cx + 14, cy + chip_h / 2 + 4.4, t, MONO_B, size, TEXT, ls=0.6) + "</g>")
            cx += cw + chip_gap
        cy += chip_h + chip_gap
    d.save()


def footer():
    H = 200
    p = PROFILE
    c = p["footer"]
    d = SVG("footer", H, f"{p['name']}. {c['mid'].capitalize()}.", corners="bottom")
    d.add(f'<rect width="{W}" height="1" fill="{LINE}"/>')
    # Seven star orbs floating in a row.
    d.css.append(".bob{animation:bob 2.6s ease-in-out infinite}@keyframes bob{50%{transform:translateY(-7px)}}")
    span = 560
    for i in range(7):
        ox = W / 2 - span / 2 + i * span / 6
        d.add(f'<g class="bob" style="animation-delay:{i * .18:.2f}s">{orb(d, ox, 72, 17, stars=i + 1)}</g>')
    # A ki blast streaking across.
    d.css.append(".fly{animation:fly 6s cubic-bezier(.5,0,.5,1) infinite}"
                 "@keyframes fly{from{transform:translate(-160px,34px)}to{transform:translate(1160px,34px)}}")
    tail = d.uid("tail")
    d.defs.append(f'<linearGradient id="{tail}" x1="0" y1="0" x2="1" y2="0">'
                  f'<stop offset="0" stop-color="{GOLD}" stop-opacity="0"/>'
                  f'<stop offset="1" stop-color="{GOLD}" stop-opacity=".9"/></linearGradient>')
    d.add(f'<g class="fly"><rect x="-120" y="-3" width="120" height="6" rx="3" fill="url(#{tail})"/>'
          f'<circle r="11" fill="{GOLD}" opacity=".6" filter="url(#{d.glow_filter(5)})"/>'
          f'<circle r="6" fill="#FFF8E0"/></g>')
    y = H - 34
    d.add(f'<line x1="56" x2="{W - 56}" y1="{y - 30}" y2="{y - 30}" stroke="{LINE}"/>')
    d.add(d.text(56, y, c["left"], MONO_B, 12, MUTED, ls=0.6))
    mw = MONO_B.width(c["mid"], 12, 0.6)
    d.add(f'<rect x="{W / 2 - mw / 2 - 16}" y="{y - 9}" width="7" height="7" fill="{GOLD}" class="blink"/>'
          + d.text(W / 2 + 6, y, c["mid"], MONO_B, 12, GOLD, "middle", 0.6))
    d.add(d.text(W - 56, y, p["url"], MONO_B, 12, MUTED, "end", 0.6))
    d.save()


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    print(f"Writing SVGs to {OUT}")
    ticker()
    hero()
    saiyan_file()
    techniques()
    footer()
