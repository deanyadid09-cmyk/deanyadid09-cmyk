from pathlib import Path
import html, math, shutil, zipfile, os

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT/'assets'
SRC = ROOT/'_src'
ROOT.mkdir(parents=True, exist_ok=True)
ASSETS.mkdir(parents=True, exist_ok=True)
SRC.mkdir(parents=True, exist_ok=True)
for _pattern in ('*.svg','*.png'):
    for _old in ASSETS.glob(_pattern):
        _old.unlink()

PROFILE = {
    'name':'SUNDAYS',
    'handle':'deanyadid09-cmyk',
    'roles':['PRODUCT BUILDER','AI SYSTEMS','AUTOMATION'],
    'tagline':'BUILD SYSTEMS. SHIP FAST. KEEP TRAINING.',
    'power':'9,001+',
    'mission':{
        'name':'DEALENGINE',
        'type':'CRM / DEAL FLOW SYSTEM',
        'status':'ACTIVE BUILD',
        'link':'https://github.com/deanyadid09-cmyk/dealengine',
        'note':'A focused operating layer for modern deal flow.'
    },
    'stack':[('REACT','UI SYSTEMS'),('JAVASCRIPT','CORE LOGIC'),('VITE','BUILD ENGINE'),('TAILWIND','STYLE LAYER'),('MUI','COMPONENTS'),('FRAMER','MOTION'),('GITHUB','SHIP / ITERATE'),('AI','AGENTS / WORKFLOWS')],
    'training':[('AGENT ARCHITECTURE','Design specialized systems that reason, route and execute.'),('AUTOMATION','Turn repetitive work into reliable operating leverage.'),('PRODUCT SYSTEMS','Build interfaces and tools people can actually run with.')],
}

W=1200
BG='#030507'; BG2='#06100b'; PANEL='#09110e'; PANEL2='#0d1813'; LINE='#163126'
GREEN='#7BFF72'; GREEN2='#14D85C'; GOLD='#FFD447'; ORANGE='#FF8B18'; RED='#FF453A'; BLUE='#43C9FF'; PURPLE='#B581FF'; TEXT='#F7F8EF'; MUTED='#98A79F'; DIM='#52645A'
FONT="Impact, 'Arial Black', Arial, sans-serif"; MONO="'Courier New', monospace"

CSS=f'''
@keyframes blink{{0%,46%,54%,100%{{opacity:1}}50%{{opacity:.12}}}}
@keyframes pulse{{0%,100%{{opacity:.45}}50%{{opacity:1}}}}
@keyframes sweep{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
@keyframes scan{{from{{transform:translateY(-140px)}}to{{transform:translateY(800px)}}}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-9px)}}}}
@keyframes aura{{0%,100%{{opacity:.28;transform:scale(.985)}}50%{{opacity:.76;transform:scale(1.025)}}}}
@keyframes dash{{to{{stroke-dashoffset:-140}}}}
@keyframes glitch{{0%,92%,100%{{transform:translate(0)}}93%{{transform:translate(-5px,2px)}}95%{{transform:translate(4px,-2px)}}97%{{transform:translate(-2px,1px)}}}}
@keyframes ping{{0%{{r:9;opacity:.9}}100%{{r:42;opacity:0}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes spark{{0%{{opacity:0;stroke-dashoffset:90}}20%{{opacity:1}}70%{{opacity:.7}}100%{{opacity:0;stroke-dashoffset:-90}}}}
@keyframes breathe{{0%,100%{{opacity:.18}}50%{{opacity:.42}}}}
@keyframes bars{{0%,100%{{transform:scaleY(.35)}}50%{{transform:scaleY(1)}}}}
@keyframes orb{{from{{transform:rotate(0)}}to{{transform:rotate(360deg)}}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
'''

def esc(s): return html.escape(str(s), quote=True)
def txt(x,y,s,size=20,color=TEXT,anchor='start',weight=700,family=MONO,spacing=0,opacity=1):
    return f'<text x="{x}" y="{y}" fill="{color}" opacity="{opacity}" font-family="{family}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" letter-spacing="{spacing}">{esc(s)}</text>'
def line(x1,y1,x2,y2,color=LINE,width=1,opacity=1,dash=None):
    da=f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" opacity="{opacity}"{da}/>'
def star_points(cx,cy,r1,r2,n=5,rot=-90):
    out=[]
    for i in range(n*2):
        a=math.radians(rot+i*180/n); r=r1 if i%2==0 else r2
        out.append(f'{cx+math.cos(a)*r:.1f},{cy+math.sin(a)*r:.1f}')
    return ' '.join(out)
def ball(cx,cy,r,stars=1,delay=0,active=True):
    if active:
        base=f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#gOrange)" stroke="#FFC65A" stroke-width="3" filter="url(#glowO)"/>'
    else:
        base=f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#111614" stroke="{DIM}" stroke-width="2" opacity=".8"/>'
    p=[f'<g style="animation:float 3.7s ease-in-out {delay}s infinite">',base]
    if active: p.append(f'<ellipse cx="{cx-r*.28}" cy="{cy-r*.30}" rx="{r*.20}" ry="{r*.11}" fill="#fff" opacity=".32" transform="rotate(-28 {cx-r*.28} {cy-r*.30})"/>')
    rr=r*.42
    pos=[(cx,cy)] if stars==1 else [(cx+math.cos(math.radians(-90+i*360/stars))*rr,cy+math.sin(math.radians(-90+i*360/stars))*rr) for i in range(stars)]
    for sx,sy in pos: p.append(f'<polygon points="{star_points(sx,sy,r*.14,r*.06)}" fill="{RED if active else DIM}" opacity="{1 if active else .65}"/>')
    p.append('</g>'); return ''.join(p)

def defs(title,h):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-labelledby="title desc">
<title id="title">{esc(title)}</title><desc id="desc">Dragon Ball inspired developer interface for {esc(PROFILE['name'])}. Original vector artwork.</desc>
<defs>
<filter id="glowG" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="glowO" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="10" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="22"/></filter>
<linearGradient id="gGreen" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{GREEN}"/><stop offset="1" stop-color="{GREEN2}"/></linearGradient>
<linearGradient id="gSky" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#02050A"/><stop offset=".58" stop-color="#07120D"/><stop offset="1" stop-color="#020403"/></linearGradient>
<radialGradient id="gOrange"><stop offset="0" stop-color="#FFE59A"/><stop offset=".5" stop-color="{ORANGE}"/><stop offset="1" stop-color="#A83A00"/></radialGradient>
<radialGradient id="gMoon"><stop offset="0" stop-color="#FFEFB2" stop-opacity=".9"/><stop offset=".58" stop-color="{GOLD}" stop-opacity=".4"/><stop offset="1" stop-color="{ORANGE}" stop-opacity="0"/></radialGradient>
<pattern id="grid" width="44" height="44" patternUnits="userSpaceOnUse"><path d="M44 0H0V44" fill="none" stroke="{LINE}" stroke-width="1" opacity=".55"/></pattern>
<pattern id="micro" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M10 0H0V10" fill="none" stroke="{GREEN}" stroke-width=".4" opacity=".08"/></pattern>
</defs><style>{CSS}</style>'''

def frame(h,title=None,sub=None,accent=GREEN):
    p=[f'<rect width="{W}" height="{h}" fill="{BG}"/>',f'<rect x="14" y="14" width="1172" height="{h-28}" rx="22" fill="none" stroke="{LINE}" stroke-width="2"/>',f'<path d="M14 82H1186" stroke="{LINE}"/>']
    p.append(f'<path d="M34 61V34H61 M1139 34H1166V61 M34 {h-61}V{h-34}H61 M1139 {h-34}H1166V{h-61}" fill="none" stroke="{accent}" stroke-width="3" opacity=".82"/>')
    if title: p.append(txt(54,58,title,18,GOLD,weight=900,spacing=2))
    if sub: p.append(txt(1148,58,sub,12,accent,'end',800,MONO,1.4))
    return ''.join(p)

def save(name,h,title,body):
    (ASSETS/name).write_text(defs(title,h)+body+'</svg>',encoding='utf-8')

# 00 TRANSMISSION ------------------------------------------------------------
h=112; b=[f'<rect width="{W}" height="{h}" rx="18" fill="{BG}"/>',f'<rect x="1" y="1" width="1198" height="110" rx="17" fill="none" stroke="{LINE}"/>',f'<circle cx="30" cy="39" r="7" fill="{GREEN}" filter="url(#glowG)" style="animation:blink 1.25s steps(1) infinite"/>',txt(51,35,'SCOUTER NETWORK // SECURE LINK',14,GREEN,spacing=1.4),txt(51,58,'EARTH NODE · GITHUB SECTOR · CHANNEL 09-Z',11,MUTED,weight=700),txt(600,47,'KI SIGNATURE LOCKED',18,TEXT,'middle',900,MONO,2.6),txt(1164,35,'CODENAME: SUNDAYS',12,GOLD,'end',800),txt(1164,58,'STATUS: BUILDING',12,GREEN,'end',800)]
for i,x in enumerate(range(240,972,54)):
    col=GREEN if i in (1,5,10,13) else LINE
    b.append(f'<rect x="{x}" y="82" width="34" height="4" rx="2" fill="{col}" opacity="{.92 if col==GREEN else .65}"/>')
# animated analyzer bars
for i in range(12):
    x=475+i*20; ht=8+(i%5)*3
    b.append(f'<rect x="{x}" y="{99-ht}" width="8" height="{ht}" rx="3" fill="{GREEN}" opacity=".55" style="transform-origin:{x+4}px 99px;animation:bars {1.1+i*.08:.2f}s ease-in-out {i*.04:.2f}s infinite"/>')
save('00-transmission.svg',h,'Scouter transmission', ''.join(b))

# 01 AWAKEN / CINEMATIC HERO ---------------------------------------------------
h=680; b=[frame(h),f'<rect x="34" y="100" width="1132" height="544" rx="18" fill="url(#gSky)"/>',f'<rect x="34" y="100" width="1132" height="544" rx="18" fill="url(#grid)" opacity=".7"/>']
# moon / sky orbs
b += [f'<circle cx="948" cy="236" r="196" fill="url(#gMoon)" opacity=".75"/>',f'<circle cx="948" cy="236" r="102" fill="none" stroke="{ORANGE}" stroke-width="2" opacity=".35"/>',f'<circle cx="948" cy="236" r="138" fill="none" stroke="{GOLD}" stroke-width="1" stroke-dasharray="8 14" opacity=".26" style="transform-origin:948px 236px;animation:orb 18s linear infinite"/>']
# distant mountains
b += [f'<path d="M34 482 L128 400 L196 448 L292 350 L372 440 L468 382 L548 462 L654 356 L739 430 L840 330 L936 421 L1010 370 L1166 472 V644 H34Z" fill="#06100B" opacity=".95"/>',f'<path d="M34 548 C176 506 286 566 406 525 C556 474 716 575 860 508 C970 457 1067 492 1166 462 V644H34Z" fill="#020403"/>']
# radial speed lines from fighter
for ang in range(-80,81,8):
    a=math.radians(ang); x2=920+math.cos(a)*325; y2=325+math.sin(a)*325
    b.append(f'<line x1="920" y1="325" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{GOLD}" stroke-width="2" opacity=".055"/>')
# aura body and sparks
b += [f'<g style="transform-origin:930px 380px;animation:aura 1.5s ease-in-out infinite"><path d="M811 592 C754 513 779 430 808 385 C783 349 805 302 842 275 C835 333 870 324 876 268 C898 319 910 303 923 244 C944 306 956 302 986 263 C982 319 1007 315 1034 286 C1027 353 1061 363 1045 408 C1070 454 1055 526 1019 592Z" fill="{GOLD}" opacity=".21" filter="url(#glowO)"/></g>']
# fighter silhouette
fighter='M842 578 C824 548 820 511 831 479 C805 465 795 441 806 418 C819 389 850 378 868 378 L844 326 L884 350 L878 299 L912 337 L930 279 L946 338 L978 294 L973 348 L1014 324 L991 380 C1018 389 1039 415 1040 444 C1042 472 1028 493 1012 502 C1018 532 1005 559 984 582 L984 626 L862 626 L862 586Z'
b += [f'<path d="{fighter}" fill="#020303" stroke="{GREEN}" stroke-width="2.5"/>',f'<path d="M949 411 Q994 399 1021 421 L1009 463 Q984 472 953 458Z" fill="{GREEN}" opacity=".20" stroke="{GREEN}" stroke-width="2"/>',f'<path d="M1011 438H1050V478" fill="none" stroke="{GREEN}" stroke-width="4"/><circle cx="982" cy="436" r="3.5" fill="{GREEN}"/>']
# sparks
sparks=[(825,300,782,232),(1045,344,1095,292),(814,444,760,462),(1038,510,1097,543),(881,258,865,200),(996,270,1021,210)]
for i,(x1,y1,x2,y2) in enumerate(sparks):
    b.append(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{GOLD}" stroke-width="3" stroke-dasharray="16 12" opacity=".7" style="animation:spark {1.5+i*.15:.2f}s ease-in-out {i*.12:.2f}s infinite"/>')
# big hero copy
b += [txt(72,139,'SCOUTER BREACH // TARGET ACQUIRED',13,GREEN,weight=900,spacing=2.2),txt(70,246,PROFILE['name'],108,TEXT,weight=900,family=FONT,spacing=4),txt(74,288,' / '.join(PROFILE['roles']),17,GOLD,weight=900,spacing=1.7),txt(74,329,PROFILE['tagline'],15,MUTED,weight=800,spacing=1.2),txt(74,390,'POWER LEVEL',12,GREEN,weight=900,spacing=2.4),f'<g style="animation:glitch 5.4s steps(1) infinite">{txt(70,477,PROFILE["power"],88,GOLD,weight=900,family=FONT,spacing=2)}</g>',txt(363,435,'SCOUTER LIMIT',12,RED,weight=900,spacing=1.5),txt(363,459,'EXCEEDED',20,RED,weight=900,family=FONT,spacing=1.3),f'<rect x="74" y="510" width="422" height="9" rx="4.5" fill="{LINE}"/><rect x="74" y="510" width="397" height="9" rx="4.5" fill="url(#gGreen)" filter="url(#glowG)"/>',txt(74,552,'BUILD MODE',11,DIM,weight=900,spacing=1.4),txt(196,552,'ONLINE',12,GREEN,weight=900),txt(74,580,'MISSION',11,DIM,weight=900,spacing=1.4),txt(196,580,'DEALENGINE',12,TEXT,weight=900),txt(74,608,'NEXT FORM',11,DIM,weight=900,spacing=1.4),txt(196,608,'SYSTEMS → AUTOMATION',12,GOLD,weight=900)]
# target brackets and scanner
b += [f'<path d="M760 128h95v26 M1128 128h-95v26 M760 598h95v26 M1128 598h-95v26" fill="none" stroke="{GREEN}" stroke-width="2.3" opacity=".7"/>',f'<g style="animation:scan 5.5s linear infinite"><rect x="34" y="100" width="1132" height="72" fill="{GREEN}" opacity=".034"/></g>']
save('01-awaken.svg',h,'Sundays power level hero',''.join(b))

# 02 CURRENT ARC / SAGA MAP ----------------------------------------------------
h=400; b=[frame(h,'CURRENT ARC // SYSTEMS SAGA','ARC 02 // IN PROGRESS')]
b += [txt(58,120,'FROM RAW SIGNAL → RELIABLE SYSTEM',30,TEXT,weight=900,family=FONT,spacing=1.8),txt(58,151,'Every build is another training arc.',13,MUTED,weight=700)]
# timeline
x0=92; y=255; gap=282
stages=[('01','SIGNAL','IDENTIFY THE REAL PROBLEM',GREEN,'COMPLETE'),('02','BUILD','SHIP THE WORKING SYSTEM',GOLD,'ACTIVE'),('03','AUTOMATE','TURN MOTION INTO LEVERAGE',BLUE,'TRAINING'),('04','SCALE','HARDEN / MEASURE / EXPAND',ORANGE,'LOCKED')]
b.append(f'<path d="M{x0} {y} H{x0+gap*3}" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>')
for i,(num,name,detail,col,status) in enumerate(stages):
    x=x0+i*gap
    b += [f'<circle cx="{x}" cy="{y}" r="34" fill="{PANEL}" stroke="{col}" stroke-width="3"/>',f'<circle cx="{x}" cy="{y}" r="49" fill="none" stroke="{col}" stroke-width="1" stroke-dasharray="5 10" opacity=".35" style="transform-origin:{x}px {y}px;animation:orb {11+i*2}s linear infinite"/>',txt(x,y+6,num,19,col,'middle',900,MONO),txt(x,y+80,name,22,TEXT,'middle',900,FONT,1.2),txt(x,y+106,detail,10,MUTED,'middle',700,MONO,.6),txt(x,y-61,status,10,col,'middle',900,MONO,1.4)]
# active pulse on stage 2
b += [f'<circle cx="{x0+gap}" cy="{y}" r="35" fill="none" stroke="{GOLD}" stroke-width="2" style="animation:ping 2s ease-out infinite"/>']
save('02-saga.svg',h,'Current systems saga',''.join(b))

# 03 FIGHTER DOSSIER -----------------------------------------------------------
h=430; b=[frame(h,'FIGHTER DOSSIER','FILE // S-9001')]
# identity coin
b += [f'<rect x="54" y="105" width="292" height="274" rx="20" fill="{PANEL}" stroke="{LINE}"/>',f'<circle cx="200" cy="213" r="88" fill="#051009" stroke="{GREEN}" stroke-width="2"/>',f'<circle cx="200" cy="213" r="112" fill="none" stroke="{GREEN}" stroke-width="1" stroke-dasharray="8 11" opacity=".32" style="transform-origin:200px 213px;animation:orb 15s linear infinite"/>',f'<path d="M148 255 C152 216 169 195 188 188 L170 153 L201 173 L210 137 L228 175 L255 150 L249 191 C273 198 286 222 284 253 C261 282 169 282 148 255Z" fill="#020403" stroke="{GREEN}" stroke-width="2"/>',txt(200,350,'CODENAME // SUNDAYS',12,GREEN,'middle',900,MONO,1.3)]
rows=[('ORIGIN','EARTH'),('CLASS','BUILDER'),('CURRENT FORM','SYSTEMS MODE'),('STYLE','SHIP → TEST → EVOLVE'),('ACTIVE MISSION','DEALENGINE')]
y=124
for k,v in rows:
    b += [txt(397,y,k,11,DIM,weight=900,spacing=1.4),txt(635,y,v,17,TEXT,weight=900,spacing=.5),line(397,y+18,1132,y+18,LINE,1,.7)]; y+=47
# philosophies / metrics
cards=[('BUILD','WORKING > PERFECT',GREEN),('DESIGN','CLARITY > NOISE',BLUE),('AUTOMATE','SYSTEMS > REPETITION',GOLD)]
for i,(a,d,c) in enumerate(cards):
    x=397+i*246
    b += [f'<rect x="{x}" y="329" width="225" height="52" rx="12" fill="{PANEL2}" stroke="{LINE}"/>',txt(x+14,350,a,10,c,weight=900,spacing=1.3),txt(x+14,371,d,11,TEXT,weight=900)]
save('03-dossier.svg',h,'Fighter dossier',''.join(b))

# 04 MISSION / DEALENGINE ------------------------------------------------------
h=560; b=[frame(h,'MISSION 01 // DEALENGINE','PRIMARY SIGNAL // ACTIVE',ORANGE)]
# left project ball / orbital system
cx,cy=248,302
b += [f'<circle cx="{cx}" cy="{cy}" r="165" fill="#06100B" stroke="{ORANGE}" stroke-width="2"/>',f'<circle cx="{cx}" cy="{cy}" r="132" fill="none" stroke="{GREEN}" stroke-width="1" opacity=".26"/>',f'<circle cx="{cx}" cy="{cy}" r="93" fill="none" stroke="{GREEN}" stroke-width="1" opacity=".22"/>',f'<path d="M{cx} {cy}L{cx} {cy-165}A165 165 0 0 1 {cx+165} {cy}Z" fill="{GREEN}" opacity=".075" style="transform-origin:{cx}px {cy}px;animation:sweep 5s linear infinite"/>']
b.append(ball(cx,cy,61,1,0))
# nodes around it
for i,a in enumerate([20,92,164,236,308]):
    rad=math.radians(a); x=cx+math.cos(rad)*132; y=cy+math.sin(rad)*132
    b += [f'<circle cx="{x:.0f}" cy="{y:.0f}" r="7" fill="{GREEN}"/>',f'<circle cx="{x:.0f}" cy="{y:.0f}" r="15" fill="none" stroke="{GREEN}" stroke-width="1" opacity=".6" style="animation:pulse {1.2+i*.1:.1f}s ease infinite"/>']
# project panel
b += [f'<rect x="458" y="105" width="688" height="402" rx="22" fill="{PANEL}" stroke="{LINE}"/>',txt(494,142,'1-STAR PROJECT // ACTIVE BUILD',12,GREEN,weight=900,spacing=1.5),txt(492,212,'DEALENGINE',58,TEXT,weight=900,family=FONT,spacing=2.4),txt(495,246,PROFILE['mission']['type'],14,GOLD,weight=900,spacing=1.4),txt(495,289,PROFILE['mission']['note'],14,MUTED,weight=700),line(495,314,1107,314,LINE,1,.9),txt(495,349,'LOADOUT',10,DIM,weight=900,spacing=1.4),txt(607,349,'REACT · JAVASCRIPT · VITE · TAILWIND · MUI · FRAMER',12,TEXT,weight=900),txt(495,385,'STATUS',10,DIM,weight=900,spacing=1.4),txt(607,385,'ACTIVE BUILD',12,GREEN,weight=900),txt(495,421,'MISSION LOOP',10,DIM,weight=900,spacing=1.4),txt(607,421,'SHIP → OBSERVE → IMPROVE → REPEAT',12,GOLD,weight=900),f'<rect x="495" y="454" width="610" height="9" rx="4.5" fill="{LINE}"/><rect x="495" y="454" width="526" height="9" rx="4.5" fill="{ORANGE}" filter="url(#glowO)"/>',txt(1107,488,'OPEN MISSION  →',12,ORANGE,'end',900,MONO,1.2)]
save('04-mission.svg',h,'DealEngine active mission',''.join(b))

# 05 DRAGON RADAR / PROJECT SLOTS ---------------------------------------------
h=430; b=[frame(h,'DRAGON RADAR // PROJECT SIGNALS','1 ACTIVE // 6 UNRESOLVED')]
# Radar left compact
cx,cy=232,257
b += [f'<circle cx="{cx}" cy="{cy}" r="134" fill="#041009" stroke="{GREEN}" stroke-width="2.5"/>',f'<circle cx="{cx}" cy="{cy}" r="100" fill="none" stroke="{GREEN}" opacity=".28"/>',f'<circle cx="{cx}" cy="{cy}" r="64" fill="none" stroke="{GREEN}" opacity=".28"/>',line(cx-134,cy,cx+134,cy,GREEN,1,.24),line(cx,cy-134,cx,cy+134,GREEN,1,.24),f'<path d="M{cx} {cy}L{cx} {cy-134}A134 134 0 0 1 {cx+134} {cy}Z" fill="{GREEN}" opacity=".08" style="transform-origin:{cx}px {cy}px;animation:sweep 4.4s linear infinite"/>']
positions=[(192,174),(274,187),(320,245),(283,330),(191,345),(125,290),(134,215)]
for i,(x,y) in enumerate(positions,1):
    active=i==1
    b.append(ball(x,y,15,i,i*.1,active=active))
    if active: b.append(f'<circle cx="{x}" cy="{y}" r="8" fill="none" stroke="{GREEN}" stroke-width="2" style="animation:ping 2s ease-out infinite"/>')
# slots on right
slotx=424; slotw=336; sloth=95; coords=[(slotx,116),(slotx+356,116),(slotx,231),(slotx+356,231)]
slots=[('01','DEALENGINE','ACTIVE',ORANGE),('02','SIGNAL UNKNOWN','LOCKED',DIM),('03','SIGNAL UNKNOWN','LOCKED',DIM),('04','SIGNAL UNKNOWN','LOCKED',DIM)]
for (x,y),(n,name,status,c) in zip(coords,slots):
    b += [f'<rect x="{x}" y="{y}" width="{slotw}" height="{sloth}" rx="16" fill="{PANEL}" stroke="{c if status=="ACTIVE" else LINE}"/>',txt(x+18,y+27,f'SIGNAL {n}',10,c,weight=900,spacing=1.2),txt(x+18,y+58,name,18,TEXT if status=='ACTIVE' else MUTED,weight=900,family=FONT,spacing=1),txt(x+318,y+79,status,10,c,'end',900,MONO,1.2)]
# bottom remaining balls legend
b += [txt(424,373,'FUTURE MISSIONS',10,DIM,weight=900,spacing=1.4)]
for j in range(3): b.append(ball(578+j*115,366,14,5+j,0.2*j,active=False))
b += [txt(1039,373,'WAITING FOR NEXT SIGNAL',11,MUTED,'end',800)]
save('05-radar.svg',h,'Dragon Radar project signals',''.join(b))

# 06 KI ACTIVITY / PRIVACY-SAFE SIGNAL -----------------------------------------
h=400; b=[frame(h,'KI ACTIVITY // GITHUB SIGNAL','TELEMETRY // PRIVACY-SAFE')]
# Big oscilloscope panel
b += [f'<rect x="54" y="106" width="765" height="230" rx="18" fill="#050A08" stroke="{LINE}"/>',f'<rect x="54" y="106" width="765" height="230" rx="18" fill="url(#micro)"/>']
# waveform deterministic
pts=[]
for i in range(70):
    x=72+i*10.5
    amp=28+14*math.sin(i*.33)+9*math.sin(i*.91)
    y=225 - math.sin(i*.52)*amp - math.sin(i*.11)*18
    pts.append(f'{x:.1f},{y:.1f}')
b += [f'<polyline points="{" ".join(pts)}" fill="none" stroke="{GREEN}" stroke-width="3" filter="url(#glowG)"/>',f'<polyline points="{" ".join(pts)}" fill="none" stroke="{GREEN}" stroke-width="1.2"/>']
# scanner sweep line
b += [f'<rect x="54" y="106" width="90" height="230" fill="{GREEN}" opacity=".035" style="animation:scan 4.8s linear infinite"/>']
# right status
b += [f'<rect x="845" y="106" width="301" height="230" rx="18" fill="{PANEL}" stroke="{LINE}"/>',txt(874,140,'BUILD SIGNAL',11,DIM,weight=900,spacing=1.4),txt(874,187,'ACTIVE',34,GREEN,weight=900,family=FONT,spacing=1.6),txt(874,221,'PUBLIC DISPLAY MODE',10,GOLD,weight=900,spacing=1.2),txt(874,249,'PRIVATE MISSION DETAILS',11,MUTED,weight=800),txt(874,269,'REMAIN REDACTED.',11,MUTED,weight=800),f'<rect x="874" y="298" width="238" height="8" rx="4" fill="{LINE}"/><rect x="874" y="298" width="206" height="8" rx="4" fill="url(#gGreen)"/>']
# bottom small status labels
labels=[('SHIP','ONLINE',GREEN),('TEST','ONLINE',BLUE),('ITERATE','ONLINE',GOLD),('REPEAT','∞',ORANGE)]
for i,(a,v,c) in enumerate(labels):
    x=64+i*189
    b += [txt(x,367,a,9,DIM,weight=900,spacing=1.1),txt(x+78,367,v,10,c,weight=900)]
b += [txt(1144,367,'SCANNER VISUALIZES BUILD MOMENTUM — NOT PRIVATE REPO CONTENT',9,MUTED,'end',700,MONO,.5)]
save('06-activity.svg',h,'GitHub build signal',''.join(b))

# 07 CAPSULE ARSENAL -----------------------------------------------------------
h=520; b=[frame(h,'COMBAT ARSENAL // CAPSULE LOADOUT','8 CAPSULES // VERIFIED',BLUE)]
# large Capsule-style core at right
b += [f'<circle cx="1045" cy="292" r="124" fill="#06110E" stroke="{BLUE}" stroke-width="2"/>',f'<circle cx="1045" cy="292" r="86" fill="none" stroke="{BLUE}" stroke-width="13" opacity=".14"/>',f'<circle cx="1045" cy="292" r="103" fill="none" stroke="{BLUE}" stroke-width="1" stroke-dasharray="6 12" opacity=".38" style="transform-origin:1045px 292px;animation:orb 14s linear infinite"/>',txt(1045,281,'C',106,BLUE,'middle',900,FONT),txt(1045,336,'CORP',20,TEXT,'middle',900,MONO,5),txt(1045,367,'LOADOUT CORE',10,MUTED,'middle',900,MONO,2)]
# 2x4 cards left
for i,(name,detail) in enumerate(PROFILE['stack']):
    row=i//4; col=i%4; x=54+col*215; y=108+row*174; accent=[GREEN,GOLD,BLUE,ORANGE][col]
    b += [f'<g style="animation:rise .65s ease {i*.08}s both"><rect x="{x}" y="{y}" width="195" height="146" rx="19" fill="{PANEL}" stroke="{LINE}"/>',f'<rect x="{x+14}" y="{y+14}" width="46" height="46" rx="14" fill="{accent}" opacity=".12" stroke="{accent}"/>',txt(x+37,y+44,f'{i+1:02}',13,accent,'middle',900),txt(x+16,y+93,name,20,TEXT,weight=900,family=FONT,spacing=1),txt(x+16,y+119,detail,10,MUTED,weight=900,spacing=.7),f'<path d="M{x+16} {y+133}H{x+178}" stroke="{accent}" stroke-width="3" opacity=".75"/></g>']
save('07-arsenal.svg',h,'Combat arsenal',''.join(b))

# 08 TRAINING CHAMBER ----------------------------------------------------------
h=440; b=[frame(h,'HYPERBOLIC TRAINING ROOM','TIME LIMIT // DISABLED')]
# left chamber door
b += [f'<rect x="56" y="111" width="286" height="277" rx="22" fill="#F5EFD9" stroke="#FFF" stroke-width="2"/>',f'<circle cx="199" cy="236" r="99" fill="#E7E1CF" stroke="#BBB5A5" stroke-width="3"/>',f'<rect x="151" y="150" width="96" height="168" rx="48" fill="#050707"/>',f'<ellipse cx="199" cy="314" rx="72" ry="15" fill="#CFC9B8" opacity=".72"/>',txt(199,359,'TIME ≠ LIMIT',11,'#333','middle',900,MONO,2)]
# rows
x=386;y=112
for i,(name,detail) in enumerate(PROFILE['training'],1):
    b += [f'<rect x="{x}" y="{y}" width="760" height="87" rx="17" fill="{PANEL}" stroke="{LINE}"/>',txt(x+24,y+29,f'TRAINING 0{i}',10,GREEN,weight=900,spacing=1.4),txt(x+24,y+59,name,20,TEXT,weight=900,family=FONT,spacing=1),txt(x+325,y+40,detail,11,MUTED,weight=800),f'<circle cx="{x+721}" cy="{y+43}" r="11" fill="none" stroke="{GREEN}" stroke-width="2"/><circle cx="{x+721}" cy="{y+43}" r="4" fill="{GREEN}" style="animation:pulse 1.4s ease infinite"/>']
    y+=101
save('08-training.svg',h,'Hyperbolic training room',''.join(b))

# 09 FINALE --------------------------------------------------------------------
h=380; b=[f'<rect width="{W}" height="{h}" rx="22" fill="{BG}"/>',f'<rect x="14" y="14" width="1172" height="352" rx="22" fill="#06110B" stroke="{LINE}"/>']
# abstract dragon-energy serpent plus head
path='M66 282 C170 160 266 300 366 194 C454 101 540 228 632 134 C720 49 810 184 914 112 C1004 52 1095 96 1148 171'
b += [f'<path d="{path}" fill="none" stroke="{GREEN}" stroke-width="26" opacity=".07" filter="url(#glowG)"/>',f'<path d="{path}" fill="none" stroke="{GREEN}" stroke-width="3" stroke-dasharray="20 13" style="animation:dash 3s linear infinite"/>',f'<path d="M1086 94 l34 -24 -5 31 30 -7 -18 25 25 10 -34 10 -11 29 -12 -29 -31 -8 25 -15Z" fill="#07150D" stroke="{GREEN}" stroke-width="2" opacity=".9"/>',f'<circle cx="1116" cy="118" r="3.5" fill="{GOLD}" filter="url(#glowO)"/>']
# headline
b += [txt(600,75,'ALL 7 SIGNALS ACCOUNTED FOR',13,GREEN,'middle',900,MONO,3),txt(600,140,'WISH GRANTED.',62,TEXT,'middle',900,FONT,3),txt(600,178,'BUILD SOMETHING LEGENDARY.',16,GOLD,'middle',900,MONO,2.2)]
# balls
xs=[210,340,470,600,730,860,990]
for i,x in enumerate(xs,1): b.append(ball(x,270,22,i,i*.08,active=True))
b += [txt(42,346,'© 2026 SUNDAYS',10,DIM),txt(600,346,'END OF TRANSMISSION // POWER NEVER STOPS',10,MUTED,'middle',900,MONO,1.5),txt(1158,346,'GITHUB.COM/DEANYADID09-CMYK',10,DIM,'end')]
save('09-finale.svg',h,'Wish granted finale',''.join(b))

# README -----------------------------------------------------------------------

# 01R CANON MEDIA LOCK ----------------------------------------------------------
h=206; b=[frame(h,'OFFICIAL VISUAL FEED // TRANSFORMATION ARCHIVE','OFFICIAL MEDIA LAYER // ARMED',GOLD)]
b += [txt(60,124,'TARGET // SUNDAYS',13,GREEN,weight=900,spacing=2),txt(60,170,'POWER LEVEL 9,001+',34,GOLD,weight=900,family=FONT,spacing=1.8),txt(1138,126,'SOURCE FEED',10,DIM,'end',900,MONO,1.4),txt(1138,151,'BANDAI NAMCO / GIPHY',12,TEXT,'end',900),txt(1138,178,'SCOUTER OVERLAY: LOCAL SVG',10,MUTED,'end',800)]
save('01-media-lock.svg',h,'Official media target lock',''.join(b))

# 03R CANON DOSSIER LABEL ------------------------------------------------------
h=128; b=[f'<rect width="{W}" height="{h}" rx="18" fill="{BG}"/>',f'<rect x="1" y="1" width="1198" height="126" rx="17" fill="none" stroke="{LINE}"/>',txt(42,43,'FIGHTER DOSSIER // OFFICIAL REFERENCE',12,GREEN,weight=900,spacing=1.7),txt(42,84,'VEGETA // SCOUTER ERA',28,TEXT,weight=900,family=FONT,spacing=2),txt(1158,43,'POWER LEVEL ARCHIVE',11,GOLD,'end',900,MONO,1.5),txt(1158,84,'24,000 // REFERENCE FEED',14,GREEN,'end',900)]
save('03-media-label.svg',h,'Vegeta official reference label',''.join(b))

# 06R KI MEDIA LABEL -----------------------------------------------------------
h=128; b=[f'<rect width="{W}" height="{h}" rx="18" fill="{BG}"/>',f'<rect x="1" y="1" width="1198" height="126" rx="17" fill="none" stroke="{LINE}"/>',txt(42,43,'KI OUTPUT // MOTION FEED',12,BLUE,weight=900,spacing=1.7),txt(42,84,'CHARGE → STRIKE → ITERATE',26,TEXT,weight=900,family=FONT,spacing=1.6),txt(1158,43,'SECONDARY OFFICIAL MOTION',11,GOLD,'end',900,MONO,1.3),txt(1158,84,'BANDAI NAMCO / GIPHY',12,BLUE,'end',900)]
save('06-media-label.svg',h,'Ki motion feed label',''.join(b))

# 09R SHENRON MEDIA LABEL ------------------------------------------------------
h=145; b=[f'<rect width="{W}" height="{h}" rx="18" fill="{BG}"/>',f'<rect x="1" y="1" width="1198" height="143" rx="17" fill="none" stroke="{LINE}"/>',txt(600,48,'FINAL SUMMON // SHENRON SIGNAL',12,GREEN,'middle',900,MONO,2.4),txt(600,100,'ALL 7 SIGNALS ACQUIRED',32,GOLD,'middle',900,FONT,2.0),txt(600,126,'OFFICIAL VISUAL FEED BELOW',10,MUTED,'middle',900,MONO,1.8)]
save('09-media-label.svg',h,'Shenron summon label',''.join(b))

# README -----------------------------------------------------------------------
HERO_GIPHY_ID='EjLTU9HAnnskywtJ9j'
KI_GIPHY_ID='cB7Ea7Y0Soe55gCbDd'
HERO_GIPHY_PAGE=f'https://giphy.com/gifs/bandainamco-dbz-dragon-ball-z-{HERO_GIPHY_ID}'
KI_GIPHY_PAGE=f'https://giphy.com/gifs/bandainamco-dbz-dragon-ball-z-{KI_GIPHY_ID}'
HERO_GIF=f'https://media.giphy.com/media/{HERO_GIPHY_ID}/giphy.gif'
KI_GIF=f'https://media.giphy.com/media/{KI_GIPHY_ID}/giphy.gif'
VEGETA_PAGE='https://en.dragon-ball-official.com/news/01_2195.html'
VEGETA_JPG='https://en.dragon-ball-official.com/dragonball/jp/news/2023/10/SHF%20%E3%83%99%E3%82%B8%E3%83%BC%E3%82%BF24000P%2001_2.JPG'
SHENRON_PAGE='https://en.dragon-ball-official.com/news/01_4048.html'
SHENRON_JPG='https://en.dragon-ball-official.com/dragonball/jp/news/2026/02/2785672.jpg?_=1789580040'

readme=f'''<!-- DRAGON CODE Z V3 // OFFICIAL MEDIA CUT // Profile README for @{PROFILE['handle']} -->
<div align="center">
  <a href="https://github.com/{PROFILE['handle']}?tab=repositories">
    <img src="assets/00-transmission.svg" width="100%" alt="Scouter network secure link. Sundays identified on GitHub." />
  </a>

  <img src="assets/01-media-lock.svg" width="100%" alt="Official visual feed target lock. Sundays power level 9001 plus." />
  <a href="{HERO_GIPHY_PAGE}">
    <img src="{HERO_GIF}" width="100%" alt="Official BANDAI NAMCO Dragon Ball Z transformation GIF used as the V3 hero media layer." />
  </a>

  <img src="assets/02-saga.svg" width="100%" alt="Current systems saga: signal, build, automate, scale." />

  <img src="assets/03-media-label.svg" width="100%" alt="Vegeta scouter era official reference label." />
  <a href="{VEGETA_PAGE}">
    <img src="{VEGETA_JPG}" width="72%" alt="Official Dragon Ball site image of Vegeta in battle armor with a scouter." />
  </a>
  <img src="assets/03-dossier.svg" width="100%" alt="Fighter dossier for Sundays." />

  <a href="{PROFILE['mission']['link']}">
    <img src="assets/04-mission.svg" width="100%" alt="Active mission: DealEngine CRM and deal flow system. Open the mission repository." />
  </a>
  <img src="assets/05-radar.svg" width="100%" alt="Dragon Radar project signals: DealEngine active and six future mission signals unresolved." />

  <img src="assets/06-media-label.svg" width="100%" alt="Ki output secondary motion feed." />
  <a href="{KI_GIPHY_PAGE}">
    <img src="{KI_GIF}" width="88%" alt="Official BANDAI NAMCO Dragon Ball Z animated GIF used as a secondary Ki motion feed." />
  </a>
  <img src="assets/06-activity.svg" width="100%" alt="Privacy-safe GitHub build signal visualizer. Private repository details are redacted." />

  <img src="assets/07-arsenal.svg" width="100%" alt="Combat arsenal: React, JavaScript, Vite, Tailwind, MUI, Framer Motion, GitHub and AI workflows." />
  <img src="assets/08-training.svg" width="100%" alt="Hyperbolic training room: agent architecture, automation and product systems." />

  <img src="assets/09-media-label.svg" width="100%" alt="Final summon Shenron official visual feed." />
  <a href="{SHENRON_PAGE}">
    <img src="{SHENRON_JPG}" width="82%" alt="Official Dragon Ball site Shenron image used for the final summon." />
  </a>
  <a href="https://github.com/{PROFILE['handle']}">
    <img src="assets/09-finale.svg" width="100%" alt="All seven signals accounted for. Wish granted: build something legendary." />
  </a>
</div>

<!--
  DRAGON CODE Z V3 // OFFICIAL MEDIA CUT
  Edit PROFILE in _src/build.py, then run: python _src/build.py
  Custom UI/HUD panels are local SVGs. Canon Dragon Ball media is referenced from official
  BANDAI NAMCO GIPHY and Dragon Ball Official Site sources listed in ASSET_SOURCES.md.
  This is a non-commercial fan profile. Dragon Ball media/characters belong to their respective rights holders.
  The activity panel intentionally does NOT expose private repository telemetry.
-->
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')

sources=f'''# Dragon Code Z V3 — Media Sources

V3 intentionally mixes the original local HUD/SVG system with a small number of externally hosted official Dragon Ball media assets.

## Hero GIF — Dragon Ball Z transformation
- Publisher/channel: BANDAI NAMCO on GIPHY
- Page: {HERO_GIPHY_PAGE}
- Direct render: {HERO_GIF}

## Vegeta dossier image
- Source: Dragon Ball Official Site
- Page: {VEGETA_PAGE}
- Image: {VEGETA_JPG}

## Ki motion GIF
- Publisher/channel: BANDAI NAMCO on GIPHY
- Page: {KI_GIPHY_PAGE}
- Direct render: {KI_GIF}

## Shenron finale image
- Source: Dragon Ball Official Site
- Page: {SHENRON_PAGE}
- Image: {SHENRON_JPG}

## Notes
- Remote media is intentionally limited so the profile still reads as a polished developer interface rather than a collage.
- External media can be swapped without touching the local SVG system; update the constants at the bottom of `_src/build.py`.
- Dragon Ball characters and media remain property of their respective rights holders. This repository is a fan-made, non-commercial profile presentation.
'''
(ROOT/'ASSET_SOURCES.md').write_text(sources,encoding='utf-8')

notes='''# Dragon Code Z V3 — Canon Media Cut

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
'''
(ROOT/'PROFILE_NOTES.md').write_text(notes,encoding='utf-8')

# validate local SVG assets
import xml.etree.ElementTree as ET
for f in sorted(ASSETS.glob('*.svg')):
    ET.parse(f)
print('built V3', len(list(ASSETS.glob('*.svg'))), 'local svg assets in', ROOT)
