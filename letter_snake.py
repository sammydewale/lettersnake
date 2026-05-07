"""
  LETTER & NUMBER SNAKE  —  Professional Edition
  pip install pygame  →  python letter_snake.py
  Optional TTS: pip install pyttsx3
"""
import pygame, sys, random, math, json, os, time, array as _arr, threading

# ═══════════════════════════════════════════════════════════
#  BOOT
# ═══════════════════════════════════════════════════════════
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
SW, SH = 1920, 1080
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Letter & Number Snake")
clock  = pygame.time.Clock()

# ─── board ──────────────────────────────────────────────────
COLS, ROWS = 24, 17
CELL       = 40
BW, BH     = COLS*CELL, ROWS*CELL
HUD_H      = 142
BX         = (SW-BW)//2
BY         = HUD_H+20
LP         = BX//2
RP         = BX+BW+(SW-BX-BW)//2

# ═══════════════════════════════════════════════════════════
#  TTS
# ═══════════════════════════════════════════════════════════
_tts_engine = None
def _init_tts():
    global _tts_engine
    try:
        import pyttsx3
        _tts_engine = pyttsx3.init()
        _tts_engine.setProperty("rate", 160)
        _tts_engine.setProperty("volume", 1.0)
    except Exception:
        _tts_engine = None

threading.Thread(target=_init_tts, daemon=True).start()

def speak(text):
    def _speak():
        try:
            if _tts_engine:
                _tts_engine.say(str(text))
                _tts_engine.runAndWait()
        except Exception:
            pass
    threading.Thread(target=_speak, daemon=True).start()

# ═══════════════════════════════════════════════════════════
#  KEYWORD LEARNING SYSTEM
#  Every letter and number maps to a child-friendly keyword.
#  The HUD shows:  FIND  →  A  →  "Apple"
#  TTS says: "Find A … Apple" on new target, "A … Apple" on correct eat.
# ═══════════════════════════════════════════════════════════
LETTER_WORDS = {
    "A":"Apple",  "B":"Ball",   "C":"Cat",    "D":"Dog",
    "E":"Egg",    "F":"Fish",   "G":"Grape",  "H":"Hat",
    "I":"Ice",    "J":"Juice",  "K":"Kite",   "L":"Lion",
    "M":"Moon",   "N":"Nest",   "O":"Orange", "P":"Pig",
    "Q":"Queen",  "R":"Rain",   "S":"Sun",    "T":"Tree",
    "U":"Umbrella","V":"Van",   "W":"Water",  "X":"Box",
    "Y":"Yarn",   "Z":"Zebra",
}
NUMBER_WORDS = {
    "1":"One Star",   "2":"Two Eyes",  "3":"Three Cats",
    "4":"Four Legs",  "5":"Five Toes", "6":"Six Eggs",
    "7":"Seven Days", "8":"Eight Legs","9":"Nine Lives",
    "10":"Ten Fingers","11":"Eleven",  "12":"Twelve Months",
    "13":"Thirteen",  "14":"Fourteen", "15":"Fifteen",
    "16":"Sixteen",   "17":"Seventeen","18":"Eighteen",
    "19":"Nineteen",  "20":"Twenty",
}

def get_keyword(sym):
    """Return the learning keyword for a letter or number symbol."""
    if SETTINGS.get("mode","Letters")=="Letters":
        return LETTER_WORDS.get(sym,"")
    else:
        return NUMBER_WORDS.get(sym,"")

def speak_target(sym):
    """Say 'Find A … Apple' — called when a new target is set."""
    kw=get_keyword(sym)
    phrase=f"Find {sym}. {kw}" if kw else f"Find {sym}"
    speak(phrase)

def speak_correct(sym):
    """Say 'A … Apple  Well done!' — called on correct eat."""
    kw=get_keyword(sym)
    phrase=f"{sym}. {kw}. Well done!" if kw else f"{sym}. Well done!"
    speak(phrase)

# ═══════════════════════════════════════════════════════════
#  COLOURS  — Deep cosmic palette, no grunge
# ═══════════════════════════════════════════════════════════
C={
    # backgrounds
    "bg_deep":(4,3,18),"bg_mid":(10,7,38),"bg_top":(18,12,58),
    # UI accents
    "gold":(255,210,60),"gold_dim":(160,128,30),
    "silver":(195,200,215),"white":(255,255,255),"black":(0,0,0),
    "dim":(85,85,128),"dim2":(55,55,90),
    # game colours
    "red":(255,55,75),"heart":(255,45,90),
    "green":(45,220,110),"cyan":(40,215,255),
    "orange":(255,152,35),"purple":(185,65,255),
    "teal":(35,205,178),"lime":(135,245,55),
    "sky":(80,175,255),"pink":(255,85,160),
    "coral":(255,100,60),"yellow":(255,228,40),
    "indigo":(100,90,255),"magenta":(255,55,195),
    "mint":(55,250,178),"amber":(255,185,25),
    # tile palette — 12 vivid
    "t0":(255,65,130),"t1":(100,90,255),"t2":(255,162,50),
    "t3":(50,200,185),"t4":(145,225,70),"t5":(255,80,80),
    "t6":(50,170,215),"t7":(240,205,85),"t8":(175,122,215),
    "t9":(255,142,60),"t10":(55,250,172),"t11":(255,50,195),
    # HUD panel bg
    "hud_bg":(12,8,42),
}
TILES=[C[f"t{i}"] for i in range(12)]
RAINBOW=[(255,55,75),(255,135,0),(255,218,0),(55,215,75),
         (55,175,255),(115,55,255),(255,55,195)]

# ═══════════════════════════════════════════════════════════
#  FONTS  — clean, bold, game-appropriate
# ═══════════════════════════════════════════════════════════
def _f(sz, bold=False):
    for n in ["Bahnschrift","Segoe UI","Calibri","Verdana","Arial"]:
        try: return pygame.font.SysFont(n, sz, bold=bold)
        except: pass
    return pygame.font.Font(None, sz)

F={
    "hero":  _f(120, True),
    "xl":    _f(72,  True),
    "lg":    _f(52,  True),
    "md":    _f(38,  True),
    "sm":    _f(28,  False),
    "sm_b":  _f(28,  True),
    "xs":    _f(21,  False),
    "xs_b":  _f(21,  True),
    "tile":  _f(24,  True),
    "hud":   _f(48,  True),
    "hudl":  _f(19,  False),
    "menu":  _f(36,  True),
}

# ═══════════════════════════════════════════════════════════
#  SOUND  — richer tones
# ═══════════════════════════════════════════════════════════
def _beep(freq=440, dur=0.09, vol=0.22, shape="sine", harmonics=None):
    sr=44100; n=int(sr*dur); buf=_arr.array("h",[0]*(n*2))
    for i in range(n):
        t=i/sr
        v=math.sin(2*math.pi*freq*t)
        if harmonics:
            for hf,ha in harmonics:
                v+=math.sin(2*math.pi*freq*hf*t)*ha
            v/=(1+sum(ha for _,ha in harmonics))
        if shape=="square": v=1.0 if v>0 else -1.0
        # smooth attack/decay envelope
        att=min(i/(sr*0.012),1.0)
        dec=min((n-i)/(sr*0.025),1.0)
        fade=min(att,dec)
        s=int(v*fade*vol*32767)
        buf[i*2]=s; buf[i*2+1]=s
    return pygame.mixer.Sound(buffer=buf)

SND={}
try:
    SND["good"]   = _beep(880,  0.15, 0.24, "sine",  [(2,.3),(3,.15)])
    SND["wrong"]  = _beep(200,  0.22, 0.24, "square")
    SND["level"]  = _beep(1047, 0.32, 0.22, "sine",  [(1.5,.4),(2,.2)])
    SND["over"]   = _beep(110,  0.45, 0.24, "square")
    SND["click"]  = _beep(700,  0.07, 0.16, "sine")
    SND["500"]    = _beep(1320, 0.38, 0.28, "sine",  [(2,.5),(3,.25)])
    SND["menu"]   = _beep(528,  0.10, 0.14, "sine")
except: pass

def play(k):
    if SETTINGS.get("sound",True) and k in SND:
        try: SND[k].play()
        except: pass

# ═══════════════════════════════════════════════════════════
#  SAVE / LOAD
# ═══════════════════════════════════════════════════════════
SAVEF=os.path.join(os.path.dirname(os.path.abspath(__file__)),"snake_save.json")
DEFS={"sound":True,"difficulty":"Normal","player_name":"Player",
      "skin":0,"mode":"Letters","total_eaten":0,"games_played":0}

def load_save():
    global SETTINGS, SCORES
    SETTINGS=DEFS.copy(); SCORES=[]
    if os.path.exists(SAVEF):
        try:
            d=json.load(open(SAVEF))
            SETTINGS.update(d.get("settings",{}))
            SCORES=d.get("scores",[])
        except: pass

def save_data():
    try: json.dump({"settings":SETTINGS,"scores":SCORES},open(SAVEF,"w"),indent=2)
    except: pass

load_save()

SKINS=[
    {"name":"Cosmic",  "head":(100,90,255),  "tail":(90,215,190)},
    {"name":"Lava",    "head":(255,65,25),   "tail":(255,210,65)},
    {"name":"Forest",  "head":(30,170,50),   "tail":(170,250,115)},
    {"name":"Candy",   "head":(255,65,158),  "tail":(255,205,235)},
    {"name":"Ocean",   "head":(10,140,255),  "tail":(125,235,255)},
    {"name":"Gold",    "head":(190,130,12),  "tail":(255,238,115)},
    {"name":"Neon",    "head":(0,255,128),   "tail":(0,200,255)},
    {"name":"Sakura",  "head":(255,105,160), "tail":(255,235,240)},
]

DIFF={
    "Easy":   {"speed":150,"tiles":6,"lives":5},
    "Normal": {"speed":95, "tiles":8,"lives":3},
    "Hard":   {"speed":55, "tiles":10,"lives":2},
    "Expert": {"speed":35, "tiles":12,"lives":1},
}

LETTERS=list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
NUMBERS=[str(i) for i in range(1,21)]

def get_pool():
    return LETTERS if SETTINGS["mode"]=="Letters" else NUMBERS

# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════
def tc(surf, text, font, col, cx, cy, shadow=False):
    if shadow:
        sh=font.render(str(text), True, (0,0,0))
        surf.blit(sh, sh.get_rect(center=(cx+2, cy+2)))
    s=font.render(str(text), True, col)
    surf.blit(s, s.get_rect(center=(cx, cy)))

def tl(surf, text, font, col, x, y):
    surf.blit(font.render(str(text), True, col), (x, y))

def lerp_col(c1, c2, t):
    return tuple(max(0,min(255,int(c1[i]+(c2[i]-c1[i])*t))) for i in range(3))

def draw_pill(surf, rect, col, border_col=None, border_w=2, alpha=255, radius=None):
    r=radius if radius else rect.height//2
    if alpha<255:
        s=pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*col, alpha), s.get_rect(), border_radius=r)
        surf.blit(s, rect.topleft)
    else:
        pygame.draw.rect(surf, col, rect, border_radius=r)
    if border_col:
        pygame.draw.rect(surf, border_col, rect, border_w, border_radius=r)

def draw_glow_circle(surf, col, cx, cy, r, intensity=60):
    for i in range(4, 0, -1):
        a=intensity//(5-i)
        s=pygame.Surface((r*2*i, r*2*i), pygame.SRCALPHA)
        pygame.draw.circle(s, (*col, a), (r*i, r*i), r*i)
        surf.blit(s, (cx-r*i, cy-r*i))
    pygame.draw.circle(surf, col, (cx, cy), r)

# ═══════════════════════════════════════════════════════════
#  BACKGROUND  — layered cosmic depth
# ═══════════════════════════════════════════════════════════
_bg_surf=None

def _build_bg():
    s=pygame.Surface((SW,SH))
    # deep radial gradient — not linear, more dramatic
    for y in range(0, SH, 2):
        for x in range(0, SW, 2):
            dx=(x-SW//2)/SW; dy=(y-SH//2)/SH
            d=math.sqrt(dx*dx+dy*dy)
            t=min(d*2.2, 1.0)
            col=lerp_col(C["bg_top"], C["bg_deep"], t)
            pygame.draw.rect(s, col, (x, y, 2, 2))
    return s

def get_bg():
    global _bg_surf
    if _bg_surf is None:
        _bg_surf=_build_bg()
    return _bg_surf

# nebula blobs
BLOBS=[(random.randint(80,SW-80), random.randint(80,SH-80),
        random.randint(100,260),
        (random.randint(15,55), random.randint(0,25), random.randint(40,100)))
       for _ in range(18)]

def draw_bg(surf, t):
    surf.blit(get_bg(), (0,0))
    for bx,by,br,bc in BLOBS:
        pulse=int(18*math.sin(t*0.016+bx*0.009))
        col=tuple(max(0,min(255,c+int(22*math.sin(t*0.011+by*0.007)))) for c in bc)
        s=pygame.Surface((br*2+pulse,br*2+pulse), pygame.SRCALPHA)
        rad=br+pulse//2
        if rad>0:
            pygame.draw.circle(s, (*col,22), (rad,rad), rad)
        surf.blit(s, (bx-rad, by-rad))

# stars — 3 layers for parallax
STAR_LAYERS=[
    [(random.randint(0,SW), random.randint(0,SH), random.randint(1,2)) for _ in range(120)],
    [(random.randint(0,SW), random.randint(0,SH), random.randint(1,2)) for _ in range(60)],
    [(random.randint(0,SW), random.randint(0,SH), random.randint(2,3)) for _ in range(30)],
]
_sy=0.0

def draw_stars(surf, t):
    speeds=[0.08, 0.18, 0.35]
    for li, layer in enumerate(STAR_LAYERS):
        spd=speeds[li]
        for sx,ry,sz in layer:
            y=int(ry+_sy*spd)%SH
            phase=math.sin(t*0.03*(li+1)+sx*0.05)
            br=int(95+75*phase*(li+1)/3)
            br=max(30, min(200, br))
            alpha=br
            if sz<=1:
                surf.set_at((sx,y), (br,br,min(255,br+50)))
            else:
                sc=pygame.Surface((sz*2,sz*2), pygame.SRCALPHA)
                pygame.draw.circle(sc, (br,br,min(255,br+50),alpha), (sz,sz), sz)
                surf.blit(sc, (sx-sz, y-sz))

# ═══════════════════════════════════════════════════════════
#  HEART
# ═══════════════════════════════════════════════════════════
def draw_heart(surf, cx, cy, size, col, filled=True):
    pts=[]
    for i in range(64):
        a=2*math.pi*i/64-math.pi/2
        x=size*16*math.sin(a)**3
        y=-size*(13*math.cos(a)-5*math.cos(2*a)-2*math.cos(3*a)-math.cos(4*a))
        pts.append((int(cx+x*0.053), int(cy+y*0.053)))
    if filled:
        pygame.draw.polygon(surf, col, pts)
        # highlight
        hl=tuple(min(255,c+80) for c in col)
        pygame.draw.circle(surf, hl,
            (int(cx-size*0.17), int(cy-size*0.20)), max(1,int(size*0.13)))
    else:
        pygame.draw.polygon(surf, col, pts, 2)

# ═══════════════════════════════════════════════════════════
#  ANIMALS  (same drawing code, cleaner organisation)
# ═══════════════════════════════════════════════════════════
ANIMALS=["lion","frog","rabbit","owl","cat","bear","duck","panda"]
A_ACCENT=[(255,195,70),(75,205,75),(238,228,228),(150,110,60),
          (220,178,138),(158,108,55),(255,228,75),(242,242,242)]

def draw_animal(surf, kind, cx, cy, r=40):
    def c(dx,dy,rad,col):
        pygame.draw.circle(surf, col, (int(cx+dx),int(cy+dy)), max(1,int(rad)))
    def rr(dx,dy,w,h,col,br=0):
        pygame.draw.rect(surf, col,
            pygame.Rect(int(cx+dx-w//2),int(cy+dy-h//2),int(w),int(h)), border_radius=br)
    def tri(pts,col): pygame.draw.polygon(surf, col, pts)

    if kind=="lion":
        for a in range(0,360,40):
            c(math.cos(math.radians(a))*(r+6),math.sin(math.radians(a))*(r+6),9,(205,125,10))
        c(0,0,r,(255,192,65))
        c(-r*.45,-r*.45,r*.23,(255,215,105)); c(r*.45,-r*.45,r*.23,(255,215,105))
        c(-r*.28,r*.05,r*.14,(55,26,4)); c(r*.28,r*.05,r*.14,(55,26,4))
        c(-r*.28,0,r*.07,(255,255,170)); c(r*.28,0,r*.07,(255,255,170))
        c(0,r*.35,r*.2,(255,150,105))
    elif kind=="frog":
        c(-r*.62,-r*.68,r*.4,(38,165,38)); c(r*.62,-r*.68,r*.4,(38,165,38))
        c(0,r*.12,r,(68,200,68))
        c(-r*.62,-r*.68,r*.32,(178,255,178)); c(r*.62,-r*.68,r*.32,(178,255,178))
        c(-r*.62,-r*.68,r*.15,(15,15,15)); c(r*.62,-r*.68,r*.15,(15,15,15))
        rr(0,r*.45,r+5,r//3,(250,135,135),5)
    elif kind=="rabbit":
        rr(-r*.3,-r*1.02,r*.33,r*.62,(210,180,190),8)
        rr(r*.3,-r*1.02,r*.33,r*.62,(210,180,190),8)
        rr(-r*.3,-r*1.02,r*.19,r*.5,(255,170,190),6)
        rr(r*.3,-r*1.02,r*.19,r*.5,(255,170,190),6)
        c(0,0,r,(233,222,222))
        c(-r*.32,-r*.15,r*.17,(65,45,75)); c(r*.32,-r*.15,r*.17,(65,45,75))
        c(-r*.32,-r*.2,r*.07,(255,255,205)); c(r*.32,-r*.2,r*.07,(255,255,205))
        c(0,r*.28,r*.16,(252,150,170))
    elif kind=="owl":
        c(0,0,r,(145,105,55))
        c(-r*.34,-r*.22,r*.34,(210,190,150)); c(r*.34,-r*.22,r*.34,(210,190,150))
        c(-r*.34,-r*.22,r*.2,(30,20,6)); c(r*.34,-r*.22,r*.2,(30,20,6))
        c(-r*.34,-r*.26,r*.07,(255,255,200)); c(r*.34,-r*.26,r*.07,(255,255,200))
        rr(0,r*.2,r*.28,r*.22,(252,170,40),4)
        rr(-r*.45,-r*.83,r*.2,r*.29,(110,72,28),4)
        rr(r*.45,-r*.83,r*.2,r*.29,(110,72,28),4)
    elif kind=="cat":
        tri([(int(cx-r*.7),int(cy-r*.55)),(int(cx-r*.45),int(cy-r*1.02)),(int(cx-r*.1),int(cy-r*.55))],(200,160,125))
        tri([(int(cx+r*.7),int(cy-r*.55)),(int(cx+r*.45),int(cy-r*1.02)),(int(cx+r*.1),int(cy-r*.55))],(200,160,125))
        tri([(int(cx-r*.63),int(cy-r*.58)),(int(cx-r*.45),int(cy-r*.95)),(int(cx-r*.14),int(cy-r*.58))],(252,170,190))
        tri([(int(cx+r*.63),int(cy-r*.58)),(int(cx+r*.45),int(cy-r*.95)),(int(cx+r*.14),int(cy-r*.58))],(252,170,190))
        c(0,0,r,(215,173,132))
        c(-r*.33,-r*.14,r*.17,(60,40,22)); c(r*.33,-r*.14,r*.17,(60,40,22))
        c(-r*.33,-r*.2,r*.07,(255,255,195)); c(r*.33,-r*.2,r*.07,(255,255,195))
        c(0,r*.28,r*.15,(252,150,170))
    elif kind=="bear":
        c(-r*.58,-r*.58,r*.31,(140,90,40)); c(r*.58,-r*.58,r*.31,(140,90,40))
        c(-r*.58,-r*.58,r*.19,(190,150,92)); c(r*.58,-r*.58,r*.19,(190,150,92))
        c(0,0,r,(153,103,50)); c(0,r*.38,r*.46,(193,153,102))
        c(-r*.3,-r*.08,r*.16,(50,30,12)); c(r*.3,-r*.08,r*.16,(50,30,12))
        c(-r*.3,-r*.13,r*.06,(255,255,195)); c(r*.3,-r*.13,r*.06,(255,255,195))
        c(0,r*.35,r*.13,(70,34,12))
    elif kind=="duck":
        c(0,r*.08,r,(252,223,68))
        c(-r*.28,-r*.2,r*.16,(30,20,5))
        c(-r*.28,-r*.25,r*.06,(255,255,205))
        rr(r*.62,r*.12,r*.39,r*.23,(252,130,24),5)
        c(-r*.65,-r*.65,r*.27,(252,210,55))
    elif kind=="panda":
        c(-r*.55,-r*.58,r*.31,(33,33,33)); c(r*.55,-r*.58,r*.31,(33,33,33))
        c(-r*.55,-r*.58,r*.21,(55,55,55)); c(r*.55,-r*.58,r*.21,(55,55,55))
        c(0,0,r,(238,238,238))
        c(-r*.33,-r*.08,r*.28,(24,24,24)); c(r*.33,-r*.08,r*.28,(24,24,24))
        c(-r*.33,-r*.08,r*.15,(255,255,255)); c(r*.33,-r*.08,r*.15,(255,255,255))
        c(-r*.33,-r*.1,r*.06,(24,24,24)); c(r*.33,-r*.1,r*.06,(24,24,24))
        c(0,r*.38,r*.19,(50,50,50))

# side + bottom decoration
SIDE_L=[]; SIDE_R=[]; BOT_ROW=[]

def build_sides():
    global SIDE_L, SIDE_R
    SIDE_L=[]; SIDE_R=[]
    STEP=105; n=int(BH/STEP)
    total=(n-1)*STEP; sy0=BY+(BH-total)//2
    for i in range(n):
        y=sy0+i*STEP
        SIDE_L.append((LP,y,i%len(ANIMALS)))
        SIDE_R.append((RP,y,(i+4)%len(ANIMALS)))

def build_bottom():
    global BOT_ROW
    BOT_ROW=[]
    STEP=108; n=int(BW/STEP)
    x0=BX+(BW-(n-1)*STEP)//2; bot_y=BY+BH+56
    for i in range(n):
        BOT_ROW.append((x0+i*STEP,bot_y,(i+2)%len(ANIMALS)))

def draw_sides(surf, t):
    for lst in [SIDE_L, SIDE_R]:
        for ax,ay,ai in lst:
            bob=int(math.sin(t*0.04+ai*1.1)*4)
            y2=ay+bob
            # subtle glow ring
            for ring_r in [52,49]:
                alpha=30 if ring_r==52 else 0
                col=(*A_ACCENT[ai],alpha if ring_r==52 else 255)
                if ring_r==52:
                    gs=pygame.Surface((ring_r*2,ring_r*2), pygame.SRCALPHA)
                    pygame.draw.circle(gs, col, (ring_r,ring_r), ring_r)
                    surf.blit(gs, (ax-ring_r, y2-ring_r))
                else:
                    pygame.draw.circle(surf, (12,8,35), (ax,y2), ring_r)
            pygame.draw.circle(surf, A_ACCENT[ai], (ax,y2), 50, 2)
            draw_animal(surf, ANIMALS[ai], ax, y2, r=42)

def draw_bottom(surf, t):
    for ax,ay,ai in BOT_ROW:
        bob=int(math.sin(t*0.045+ai*0.85)*3)
        y2=ay+bob
        for ring_r in [46,43]:
            if ring_r==46:
                gs=pygame.Surface((ring_r*2,ring_r*2), pygame.SRCALPHA)
                pygame.draw.circle(gs, (*A_ACCENT[ai],25), (ring_r,ring_r), ring_r)
                surf.blit(gs, (ax-ring_r, y2-ring_r))
            else:
                pygame.draw.circle(surf, (12,8,35), (ax,y2), ring_r)
        pygame.draw.circle(surf, A_ACCENT[ai], (ax,y2), 44, 2)
        draw_animal(surf, ANIMALS[ai], ax, y2, r=36)

# ═══════════════════════════════════════════════════════════
#  PARTICLES
# ═══════════════════════════════════════════════════════════
class Pt:
    __slots__=["x","y","vx","vy","life","ml","col","sz","lbl","spin"]
    def __init__(self, x, y, col, lbl=None):
        a=random.uniform(0,2*math.pi); spd=random.uniform(2.5,7)
        self.x=float(x); self.y=float(y)
        self.vx=math.cos(a)*spd; self.vy=math.sin(a)*spd-random.uniform(1,3.5)
        self.life=self.ml=random.randint(38,70)
        self.col=col; self.sz=random.randint(4,12); self.lbl=lbl
        self.spin=random.uniform(-0.15,0.15)
    def tick(self):
        self.x+=self.vx; self.y+=self.vy
        self.vy+=0.18; self.vx*=0.98
        self.life-=1
    def draw(self, surf):
        a=self.life/self.ml
        col=tuple(max(0,min(255,int(c*a))) for c in self.col)
        if self.lbl:
            s=F["sm_b"].render(self.lbl, True, col)
            surf.blit(s, s.get_rect(center=(int(self.x),int(self.y))))
        else:
            pygame.draw.circle(surf, col, (int(self.x),int(self.y)), max(1,int(self.sz*a)))

PARTS=[]
def burst(x, y, col, n=24, lbl=None):
    for _ in range(n): PARTS.append(Pt(x,y,col))
    if lbl: PARTS.append(Pt(x,y-36,col,lbl))
def tick_pts(surf):
    for p in PARTS[:]:
        p.tick(); p.draw(surf)
        if p.life<=0: PARTS.remove(p)

# ═══════════════════════════════════════════════════════════
#  BUTTON  — clean pill, no emoji boxes, text-only labels
# ═══════════════════════════════════════════════════════════
class Btn:
    def __init__(self, cx, cy, w, h, label, bg,
                 fg=None, font=None, icon=None, icon_col=None):
        self.cx=cx; self.cy=cy; self.w=w; self.h=h
        self.label=label; self.bg=bg
        self.fg=fg or C["white"]
        self.font=font or F["menu"]
        self.icon=icon          # small circle colour indicator (no emoji)
        self.icon_col=icon_col
        self._a=0.0
        self.rect=pygame.Rect(cx-w//2, cy-h//2, w, h)

    def update(self, mx, my):
        target=1.0 if self.rect.collidepoint(mx,my) else 0.0
        self._a+=(target-self._a)*0.20

    def draw(self, surf):
        sc=1+0.045*self._a
        w=int(self.w*sc); h=int(self.h*sc)
        x=self.cx-w//2; y=self.cy-h//2; r=h//2

        # drop shadow
        sh=pygame.Surface((w+20,h+20), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0,0,0,int(80+40*self._a)),
            pygame.Rect(10,10,w,h), border_radius=r)
        surf.blit(sh, (x-10,y-10))

        # glow on hover
        if self._a>0.1:
            gw=int(self._a*8)
            rim=tuple(min(255,c+100) for c in self.bg)
            pygame.draw.rect(surf, rim,
                pygame.Rect(x-gw,y-gw,w+gw*2,h+gw*2), border_radius=r+gw)

        # main pill — gradient effect via two overlapping rects
        pygame.draw.rect(surf, self.bg, pygame.Rect(x,y,w,h), border_radius=r)
        # top highlight strip
        hl=tuple(min(255,c+45) for c in self.bg)
        hi=pygame.Surface((w,h//2), pygame.SRCALPHA)
        pygame.draw.rect(hi, (*hl,60), hi.get_rect(), border_radius=r)
        surf.blit(hi, (x,y))

        # icon dot
        if self.icon_col:
            pygame.draw.circle(surf, self.icon_col,
                (self.cx - self.font.size(self.label)[0]//2 - 18, self.cy), 7)

        # label — clean text, no emoji fallback boxes
        lbl=self.font.render(self.label, True, self.fg)
        surf.blit(lbl, lbl.get_rect(center=(self.cx,self.cy)))

    def hit(self, ev):
        return (ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1
                and self.rect.collidepoint(ev.pos))

# ═══════════════════════════════════════════════════════════
#  GAME STATE
# ═══════════════════════════════════════════════════════════
class GS:
    def reset(self):
        d=DIFF[SETTINGS["difficulty"]]
        self.snake=[{"x":12,"y":8},{"x":11,"y":8},{"x":10,"y":8}]
        self.dir={"x":1,"y":0}; self.ndir={"x":1,"y":0}
        self.letters=[]; self.target=""
        self.score=0; self.lives=d["lives"]; self.maxliv=d["lives"]
        self.level=1; self.eaten=0; self.speed=d["speed"]
        self.ntiles=d["tiles"]; self.flash=0; self.lvlf=0
        self.rainbow=False; self.rb_idx=0; self.rb_t=0
        self.combo=0; self.combo_t=0    # combo system
        self.keyword=""                  # learning keyword for current target
        self._fill(); self._new_target()
        SETTINGS["games_played"]=SETTINGS.get("games_played",0)+1

    def _taken(self):
        return {(s["x"],s["y"]) for s in self.snake}|{(l["x"],l["y"]) for l in self.letters}

    def _fill(self):
        pool=get_pool()
        used={l["ch"] for l in self.letters}
        available=[s for s in pool if s not in used]
        random.shuffle(available)
        tk=self._taken()
        while len(self.letters)<self.ntiles and available:
            sym=available.pop()
            for _ in range(300):
                x=random.randint(0,COLS-1); y=random.randint(0,ROWS-1)
                if (x,y) not in tk:
                    self.letters.append({"x":x,"y":y,"ch":sym,
                        "col":TILES[random.randint(0,11)],
                        "bob":random.uniform(0,math.pi*2)})
                    tk.add((x,y)); used.add(sym); break

    def _new_target(self):
        pool=get_pool()
        on_board=[l["ch"] for l in self.letters]
        if on_board:
            self.target=random.choice(on_board)
        else:
            self.target=random.choice(pool)
        if not any(l["ch"]==self.target for l in self.letters):
            tk=self._taken()
            for _ in range(500):
                x=random.randint(0,COLS-1); y=random.randint(0,ROWS-1)
                if (x,y) not in tk:
                    self.letters.append({"x":x,"y":y,"ch":self.target,
                        "col":TILES[random.randint(0,11)],"bob":0.0})
                    break
        # store keyword for HUD display
        self.keyword=get_keyword(self.target)
        # announce new target via TTS
        speak_target(self.target)

    def _add_tile(self):
        pool=get_pool()
        used={l["ch"] for l in self.letters}
        available=[s for s in pool if s not in used]
        if not available: return
        sym=random.choice(available)
        tk=self._taken()
        for _ in range(400):
            x=random.randint(0,COLS-1); y=random.randint(0,ROWS-1)
            if (x,y) not in tk:
                self.letters.append({"x":x,"y":y,"ch":sym,
                    "col":TILES[random.randint(0,11)],
                    "bob":random.uniform(0,math.pi*2)})
                return

    def step(self):
        d=self.ndir
        head={"x":(self.snake[0]["x"]+d["x"])%COLS,
              "y":(self.snake[0]["y"]+d["y"])%ROWS}
        self.dir=d
        # combo timeout
        if self.combo_t>0:
            self.combo_t-=1
        else:
            self.combo=0

        if any(s["x"]==head["x"] and s["y"]==head["y"] for s in self.snake[1:]):
            return "dead"

        hit=next((i for i,l in enumerate(self.letters)
                   if l["x"]==head["x"] and l["y"]==head["y"]),None)
        grew=False; res="ok"
        if hit is not None:
            ltr=self.letters.pop(hit)
            px=BX+head["x"]*CELL+CELL//2
            py=BY+head["y"]*CELL+CELL//2
            if ltr["ch"]==self.target:
                grew=True
                self.combo+=1; self.combo_t=120
                bonus=1 if self.combo<3 else (2 if self.combo<6 else 3)
                pts=10*self.level*bonus
                self.score+=pts; self.eaten+=1
                SETTINGS["total_eaten"]=SETTINGS.get("total_eaten",0)+1
                label=f"+{pts}" if bonus==1 else f"+{pts}  x{bonus}!"
                burst(px,py,ltr["col"],26,label)
                play("good")
                speak_correct(self.target)   # "A … Apple  Well done!"
                prev=self.score-pts
                if prev<500<=self.score and not self.rainbow:
                    self.rainbow=True; play("500")
                if self.eaten%5==0:
                    self.level+=1; self.speed=max(28,self.speed-7)
                    self.lvlf=90; play("level")
                    speak(f"Level {self.level}! Amazing!")
                    res="level"
                self._add_tile(); self._new_target()
            else:
                self.lives-=1; self.flash=24; self.combo=0
                burst(px,py,C["red"],18,"WRONG"); play("wrong")
                self._add_tile()
                if self.lives<=0: return "dead"
                res="wrong"
        self.snake.insert(0,head)
        if not grew: self.snake.pop()
        if self.rainbow:
            self.rb_t+=1
            if self.rb_t%5==0: self.rb_idx=(self.rb_idx+1)%len(RAINBOW)
        return res

G=GS(); G.reset()

def record(score, level):
    SCORES.append({
        "name":SETTINGS["player_name"],"score":score,"level":level,
        "diff":SETTINGS["difficulty"],"mode":SETTINGS["mode"],
        "date":time.strftime("%d/%m/%y")
    })
    SCORES.sort(key=lambda e:-e["score"])
    while len(SCORES)>10: SCORES.pop()
    save_data()

# ═══════════════════════════════════════════════════════════
#  HUD  — fully custom drawn, NO emoji
# ═══════════════════════════════════════════════════════════
def draw_hud(g, t):
    # HUD bar background
    hud_surf=pygame.Surface((SW,HUD_H), pygame.SRCALPHA)
    hud_surf.fill((*C["hud_bg"],230))
    screen.blit(hud_surf,(0,0))
    # bottom edge line with glow
    line_col=RAINBOW[g.rb_idx] if g.rainbow else C["indigo"]
    pygame.draw.line(screen, line_col, (0,HUD_H), (SW,HUD_H), 2)
    # inner top accent line
    pygame.draw.line(screen, C["dim2"], (0,1), (SW,1), 1)

    LBL = (175,175,215)   # readable label colour throughout HUD

    # ── LEFT: SCORE ───────────────────────────────────────
    tl(screen, "SCORE", F["hudl"], LBL, 50, 14)
    tl(screen, str(g.score), F["hud"], C["gold"], 50, 40)

    # ── LEFT2: LEVEL ──────────────────────────────────────
    tl(screen, "LEVEL", F["hudl"], LBL, 300, 14)
    tl(screen, str(g.level), F["hud"], C["cyan"], 300, 40)

    # mode badge
    mc=C["pink"] if SETTINGS["mode"]=="Letters" else C["amber"]
    badge_r=pygame.Rect(282, 96, 120, 26)
    draw_pill(screen, badge_r, mc, alpha=40, radius=13)
    pygame.draw.rect(screen, mc, badge_r, 1, border_radius=13)
    tc(screen, SETTINGS["mode"], F["xs"], mc, 342, 109)

    # ── LEFT3: SPEED bar ──────────────────────────────────
    tl(screen, "SPEED", F["hudl"], LBL, 490, 14)
    bar_x=490; bar_y=46; bar_w=120; bar_h=14
    pygame.draw.rect(screen, C["dim2"], (bar_x,bar_y,bar_w,bar_h), border_radius=7)
    spd_pct=min(1.0, (g.level-1)/8)
    spd_col=lerp_col(C["green"], C["red"], spd_pct)
    filled_w=int(bar_w*spd_pct)
    if filled_w>0:
        pygame.draw.rect(screen, spd_col, (bar_x,bar_y,filled_w,bar_h), border_radius=7)
    pygame.draw.rect(screen, C["dim"], (bar_x,bar_y,bar_w,bar_h), 1, border_radius=7)

    # ── COMBO display ─────────────────────────────────────
    if g.combo>=2:
        fade=min(1.0, g.combo_t/40)
        cc=C["magenta"] if g.combo<5 else C["gold"]
        combo_col=tuple(int(c*fade) for c in cc)
        tl(screen, "COMBO", F["hudl"], LBL, 490, 70)
        tl(screen, f"x{g.combo}", F["sm_b"], combo_col, 490, 92)

    # ── DIFFICULTY badge (right side, above lives) ────────
    diff_cols_hud={"Easy":C["green"],"Normal":C["cyan"],
                   "Hard":C["orange"],"Expert":C["red"]}
    diff_col=diff_cols_hud.get(SETTINGS["difficulty"],C["dim"])
    db_r=pygame.Rect(SW-200,14,150,26)
    draw_pill(screen,db_r,diff_col,alpha=35,radius=13)
    pygame.draw.rect(screen,diff_col,db_r,1,border_radius=13)
    tc(screen,SETTINGS["difficulty"],F["xs"],diff_col,SW-125,27)

    # ── CENTRE: target symbol + learning keyword ───────────
    tc(screen, "FIND THIS", F["xs_b"], LBL, SW//2, 12)
    tcol=RAINBOW[g.rb_idx] if g.rainbow else C["gold"]

    # letter — slightly smaller to leave room for keyword
    tc(screen, g.target, F["xl"], tcol, SW//2, 58, shadow=True)

    # keyword beneath the letter — pulsing brightness
    kw=getattr(g,"keyword","")
    if kw:
        pulse=int(200+50*math.sin(t*0.09))
        kw_col=(min(255,pulse), min(255,pulse), 150)
        # keyword in bold small font, centred, with a subtle dark pill behind it
        kw_w=F["sm_b"].size(kw)[0]
        kw_pill=pygame.Rect(SW//2-kw_w//2-10, 88, kw_w+20, 30)
        draw_pill(screen, kw_pill, (0,0,0), alpha=80, radius=14)
        tc(screen, kw, F["sm_b"], kw_col, SW//2, 103)

    # ── RIGHT: LIVES as drawn hearts ──────────────────────
    h_gap=52
    hx0=SW-60-h_gap*(g.maxliv-1)
    tl(screen, "LIVES", F["hudl"], LBL, hx0-12, 14)
    for i in range(g.maxliv):
        alive=i<g.lives
        col=C["heart"] if alive else C["dim2"]
        draw_heart(screen, hx0+i*h_gap, 78, 19, col, filled=alive)
        if not alive:
            draw_heart(screen, hx0+i*h_gap, 78, 19, C["dim"], filled=False)

    # ESC hint — white with shadow so it reads on any background
    def tl_outlined(surf, text, font, fg, x, y):
        sh=font.render(text, True, (0,0,0))
        for ox,oy in [(-1,0),(1,0),(0,-1),(0,1)]:
            surf.blit(sh, (x+ox, y+oy))
        surf.blit(font.render(text, True, fg), (x, y))

    tl_outlined(screen, "ESC  Pause", F["xs"], C["white"], 50, HUD_H-26)
    # player name — white outlined
    nm_text=SETTINGS["player_name"]
    nm_sh=F["xs"].render(nm_text, True, (0,0,0))
    nm_s =F["xs"].render(nm_text, True, C["white"])
    nx=SW-nm_s.get_width()-50
    for ox,oy in [(-1,0),(1,0),(0,-1),(0,1)]:
        screen.blit(nm_sh, (nx+ox, 14+oy))
    screen.blit(nm_s, (nx, 14))

# ═══════════════════════════════════════════════════════════
#  BOARD  — polished tiles, clipped
# ═══════════════════════════════════════════════════════════
def draw_board(g, t):
    # checkerboard with subtle shading
    for row in range(ROWS):
        for col in range(COLS):
            if (row+col)%2==0:
                col_c=(232,245,255)
            else:
                col_c=(212,230,250)
            pygame.draw.rect(screen, col_c,
                pygame.Rect(BX+col*CELL, BY+row*CELL, CELL, CELL))

    # wrong flash overlay
    if g.flash>0:
        a=int(160*g.flash/24)
        fl=pygame.Surface((BW,BH), pygame.SRCALPHA)
        fl.fill((255,40,40,a))
        screen.blit(fl, (BX,BY))
        g.flash-=1

    clip_rect=pygame.Rect(BX,BY,BW,BH)
    screen.set_clip(clip_rect)

    # tiles
    for l in g.letters:
        if not (0<=l["x"]<COLS and 0<=l["y"]<ROWS): continue
        l["bob"]+=0.05
        bx=BX+l["x"]*CELL
        by=BY+l["y"]*CELL+int(math.sin(l["bob"])*2.5)
        is_t=(l["ch"]==g.target)

        # target pulse glow
        if is_t:
            pulse=int(6+3*math.sin(t*0.12))
            glow=pygame.Surface((CELL+pulse*2+8,CELL+pulse*2+8), pygame.SRCALPHA)
            for gi in range(5,0,-1):
                pygame.draw.rect(glow, (*C["gold"],gi*14),
                    pygame.Rect(5-gi,5-gi,CELL+pulse*2+gi*2,CELL+pulse*2+gi*2),
                    border_radius=12+gi)
            screen.blit(glow, (bx-pulse-5, by-pulse-5))
            pygame.draw.rect(screen, C["gold"],
                pygame.Rect(bx-pulse,by-pulse,CELL+pulse*2,CELL+pulse*2), border_radius=12)

        # tile body with gradient feel
        tile_col=l["col"]
        pygame.draw.rect(screen, tile_col,
            pygame.Rect(bx+2,by+2,CELL-4,CELL-4), border_radius=9)
        # top highlight
        hi=tuple(min(255,c+55) for c in tile_col)
        hi_s=pygame.Surface((CELL-4,CELL//2-2), pygame.SRCALPHA)
        pygame.draw.rect(hi_s, (*hi,65), hi_s.get_rect(), border_radius=9)
        screen.blit(hi_s, (bx+2,by+2))
        # subtle border
        pygame.draw.rect(screen, (255,255,255,80),
            pygame.Rect(bx+2,by+2,CELL-4,CELL-4), 1, border_radius=9)

        # letter
        ch=F["tile"].render(l["ch"], True, C["white"])
        # shadow
        sh=F["tile"].render(l["ch"], True, (0,0,0))
        screen.blit(sh, sh.get_rect(center=(bx+CELL//2+1,by+CELL//2+2)))
        screen.blit(ch, ch.get_rect(center=(bx+CELL//2,by+CELL//2)))

    # snake
    if g.rainbow:
        sk_head=RAINBOW[g.rb_idx]
        sk_tail=RAINBOW[(g.rb_idx+3)%len(RAINBOW)]
    else:
        sk=SKINS[SETTINGS["skin"]]
        sk_head=sk["head"]; sk_tail=sk["tail"]

    n=len(g.snake)
    for i,seg in enumerate(g.snake):
        if not (0<=seg["x"]<COLS and 0<=seg["y"]<ROWS): continue
        sx=BX+seg["x"]*CELL; sy=BY+seg["y"]*CELL
        tr=i/max(n-1,1)
        col=lerp_col(sk_head, sk_tail, tr)
        sz=CELL-2 if i==0 else CELL-5
        ox=(CELL-sz)//2
        # shadow
        sh_s=pygame.Surface((sz,sz), pygame.SRCALPHA)
        pygame.draw.rect(sh_s, (0,0,0,50), sh_s.get_rect(),
            border_radius=(11 if i==0 else 6))
        screen.blit(sh_s, (sx+ox+2,sy+ox+2))
        # body
        pygame.draw.rect(screen, col,
            pygame.Rect(sx+ox,sy+ox,sz,sz), border_radius=(11 if i==0 else 6))
        # top gloss
        gl=tuple(min(255,c+60) for c in col)
        gl_s=pygame.Surface((sz,sz//2), pygame.SRCALPHA)
        pygame.draw.rect(gl_s, (*gl,70), gl_s.get_rect(),
            border_radius=(11 if i==0 else 6))
        screen.blit(gl_s, (sx+ox,sy+ox))

        # head eyes
        if i==0:
            d=g.dir
            ex=sx+CELL//2+d["x"]*8; ey=sy+CELL//2+d["y"]*8
            px,py=-d["y"],d["x"]
            for sgn in[-1,1]:
                epx=ex+px*7*sgn; epy=ey+py*7*sgn
                pygame.draw.circle(screen, C["white"],(int(epx),int(epy)),6)
                pygame.draw.circle(screen,(20,20,20),(int(epx+d["x"]*2),int(epy+d["y"]*2)),3)
                # eye glint
                pygame.draw.circle(screen,C["white"],(int(epx+d["x"]*1-1),int(epy+d["y"]*1-1)),1)

    screen.set_clip(None)

    # board border — double line with glow effect
    br_col=RAINBOW[g.rb_idx] if g.rainbow else C["indigo"]
    glow_s=pygame.Surface((BW+16,BH+16), pygame.SRCALPHA)
    pygame.draw.rect(glow_s, (*br_col,40), glow_s.get_rect(), 8, border_radius=8)
    screen.blit(glow_s, (BX-8,BY-8))
    pygame.draw.rect(screen, br_col, pygame.Rect(BX,BY,BW,BH), 3, border_radius=6)
    inner_col=tuple(min(255,c+60) for c in br_col)
    pygame.draw.rect(screen, inner_col, pygame.Rect(BX+1,BY+1,BW-2,BH-2), 1, border_radius=5)

# ═══════════════════════════════════════════════════════════
#  DECORATIVE DIVIDER  (clean horizontal rule with dots)
# ═══════════════════════════════════════════════════════════
def draw_divider(surf, y, col, width=600, cx=None):
    if cx is None: cx=SW//2
    x0=cx-width//2; x1=cx+width//2
    pygame.draw.line(surf, col, (x0,y), (cx-24,y), 1)
    pygame.draw.line(surf, col, (cx+24,y), (x1,y), 1)
    pygame.draw.circle(surf, col, (cx,y), 4)
    pygame.draw.circle(surf, col, (cx-18,y), 2)
    pygame.draw.circle(surf, col, (cx+18,y), 2)

# ═══════════════════════════════════════════════════════════
#  3D RAINBOW CURVED TITLE
# ═══════════════════════════════════════════════════════════
# Each letter gets its own colour cycling through the rainbow.
# Letters are placed on a gentle upward arc.  Each letter is
# rendered multiple times with downward offsets to fake 3D depth,
# plus a dark outline pass and a glow halo behind it.

TITLE_LETTER_COLS=[
    (255,60,100),(255,130,0),(255,220,0),
    (55,220,80),(50,200,255),(130,80,255),(255,60,200),
]

def draw_3d_title(surf, text, font, cx, cy, t, scale=1.0):
    """Render `text` centred at (cx,cy) with 3D depth, outline, arc & glow."""
    letters=list(text)
    n=len(letters)
    # measure total width to centre properly
    widths=[font.size(ch)[0] for ch in letters]
    total_w=sum(widths)+max(0,(n-1))*4
    # arc: letters rise toward centre, fall at edges — gentle parabola
    arc_height=28*scale
    # animation: slight gentle float
    base_y=cy+int(math.sin(t*0.038)*6)

    # no per-letter glow — the 3D shadow layers give enough depth on their own
    x=cx-total_w//2
    for i,ch in enumerate(letters):
        x+=widths[i]+4  # just advance x, nothing drawn here

    # 3D depth layers (darkened copies shifted down-right)
    DEPTH=6
    x=cx-total_w//2
    for i,ch in enumerate(letters):
        w=widths[i]; frac=(i/(max(n-1,1)))
        arc_off=-int(arc_height*(1-(2*frac-1)**2))
        lx=x+w//2; ly=base_y+arc_off
        col=TITLE_LETTER_COLS[(i+int(t*0.08))%len(TITLE_LETTER_COLS)]
        dark=tuple(max(0,c//4) for c in col)
        for d in range(DEPTH,0,-1):
            shade=tuple(int(dark[j]+(col[j]-dark[j])*(DEPTH-d)/DEPTH) for j in range(3))
            s=font.render(ch,True,shade)
            surf.blit(s,s.get_rect(center=(lx+d,ly+d)))
        x+=w+4

    # outline pass (thin black stroke simulated by 8-direction offset)
    x=cx-total_w//2
    for i,ch in enumerate(letters):
        w=widths[i]; frac=(i/(max(n-1,1)))
        arc_off=-int(arc_height*(1-(2*frac-1)**2))
        lx=x+w//2; ly=base_y+arc_off
        out_s=font.render(ch,True,(0,0,0))
        for ox,oy in[(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,-2),(-2,2),(2,2)]:
            surf.blit(out_s,out_s.get_rect(center=(lx+ox,ly+oy)))
        x+=w+4

    # main coloured letter pass
    x=cx-total_w//2
    for i,ch in enumerate(letters):
        w=widths[i]; frac=(i/(max(n-1,1)))
        arc_off=-int(arc_height*(1-(2*frac-1)**2))
        lx=x+w//2; ly=base_y+arc_off
        col=TITLE_LETTER_COLS[(i+int(t*0.08))%len(TITLE_LETTER_COLS)]
        # white top-gloss on each letter
        s=font.render(ch,True,col)
        surf.blit(s,s.get_rect(center=(lx,ly)))
        # gloss highlight — top 1/3
        hl=font.render(ch,True,tuple(min(255,c+110) for c in col))
        clip=pygame.Rect(lx-w//2,ly-s.get_height()//2,w,s.get_height()//3)
        surf.set_clip(clip); surf.blit(hl,hl.get_rect(center=(lx,ly)))
        surf.set_clip(None)
        x+=w+4

    return total_w   # return so callers can know width

# ═══════════════════════════════════════════════════════════
#  SCREEN: MAIN MENU
# ═══════════════════════════════════════════════════════════
def scr_menu():
    global _sy
    cx=SW//2

    # ── Y positions: title top, everything stacks cleanly, no overlap ──
    TITLE_LINE1_Y = 95    # "LETTER & NUMBER" centre
    TITLE_LINE2_Y = 185   # "SNAKE" centre
    TAGLINE_Y     = 252   # subtitle
    MODE_LBL_Y    = 300   # "CHOOSE MODE" label
    MODE_BTN_Y    = 340   # Letters / Numbers pills
    BTN_START_Y   = 412   # first main button
    BTN_GAP       = 82

    mode_l=Btn(cx-120,MODE_BTN_Y,215,56,"Letters",
               C["pink"] if SETTINGS["mode"]=="Letters" else (45,42,85))
    mode_n=Btn(cx+120,MODE_BTN_Y,215,56,"Numbers",
               C["amber"] if SETTINGS["mode"]=="Numbers" else (45,42,85))

    btns=[
        Btn(cx, BTN_START_Y+BTN_GAP*0, 360,70,"PLAY",        C["indigo"], font=F["lg"]),
        Btn(cx, BTN_START_Y+BTN_GAP*1, 360,70,"SETTINGS",    C["teal"],   font=F["menu"]),
        Btn(cx, BTN_START_Y+BTN_GAP*2, 360,70,"HIGH SCORES", C["orange"], font=F["menu"]),
        Btn(cx, BTN_START_Y+BTN_GAP*3, 360,70,"QUIT",        C["coral"],  font=F["menu"]),
    ]

    # 4 animals each side, vertically spanning the mode+button zone
    ZONE_TOP  = MODE_BTN_Y - 10
    ZONE_BOT  = BTN_START_Y + BTN_GAP*3 + 45
    N_SIDE    = 4
    A_STEP    = (ZONE_BOT - ZONE_TOP) // (N_SIDE - 1)
    LEFT_AX   = cx - 310
    RIGHT_AX  = cx + 310

    t=0
    while True:
        dt=clock.tick(60); _sy=(_sy+0.28)%SH
        mx,my=pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: save_data(); pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_RETURN: return "play"
            for i,b in enumerate(btns):
                if b.hit(ev): play("click"); return ["play","settings","scores","quit"][i]
            if mode_l.hit(ev):
                SETTINGS["mode"]="Letters"; mode_l.bg=C["pink"]; mode_n.bg=(45,42,85); play("click")
            if mode_n.hit(ev):
                SETTINGS["mode"]="Numbers"; mode_n.bg=C["amber"]; mode_l.bg=(45,42,85); play("click")

        draw_bg(screen,t); draw_stars(screen,t)

        # ── 3D rainbow arc titles at the very top ─────────
        draw_3d_title(screen,"LETTER & NUMBER",F["xl"],  cx,TITLE_LINE1_Y,t,scale=0.7)
        draw_3d_title(screen,"SNAKE",           F["hero"],cx,TITLE_LINE2_Y,t,scale=1.0)

        # tagline just below title, stays well clear of mode buttons
        draw_divider(screen,TAGLINE_Y-14,C["dim2"],440,cx)
        tc(screen,"Eat the right symbol  -  Learn & Have Fun",F["sm"],C["cyan"],cx,TAGLINE_Y)
        draw_divider(screen,TAGLINE_Y+20,C["dim2"],440,cx)

        # ── animals flanking the button column ────────────
        for i in range(N_SIDE):
            bob=int(math.sin(t*0.04+i*1.3)*5)
            ay=ZONE_TOP + i*A_STEP + bob

            li=i % len(ANIMALS)
            pygame.draw.circle(screen,(10,7,30),(LEFT_AX,ay),44)
            pygame.draw.circle(screen,A_ACCENT[li],(LEFT_AX,ay),44,2)
            draw_animal(screen,ANIMALS[li],LEFT_AX,ay,r=36)

            ri=(i+4) % len(ANIMALS)
            pygame.draw.circle(screen,(10,7,30),(RIGHT_AX,ay),44)
            pygame.draw.circle(screen,A_ACCENT[ri],(RIGHT_AX,ay),44,2)
            draw_animal(screen,ANIMALS[ri],RIGHT_AX,ay,r=36)

        # ── mode selector ─────────────────────────────────
        tc(screen,"CHOOSE MODE",F["xs_b"],(175,175,215),cx,MODE_LBL_Y)
        mode_l.update(mx,my); mode_l.draw(screen)
        mode_n.update(mx,my); mode_n.draw(screen)

        # ── main buttons ──────────────────────────────────
        for b in btns: b.update(mx,my); b.draw(screen)

        # ── footer — outlined white so readable on any bg ─
        def footer(text,x,y,right=False):
            s=F["xs"].render(text,True,C["white"])
            sh=F["xs"].render(text,True,(0,0,0))
            px=SW-s.get_width()-x if right else x
            for ox,oy in[(-1,0),(1,0),(0,-1),(0,1)]:
                screen.blit(sh,(px+ox,y+oy))
            screen.blit(s,(px,y))

        footer(f"Player: {SETTINGS['player_name']}",38,SH-30)
        footer(f"Diff: {SETTINGS['difficulty']}  |  Games: {SETTINGS.get('games_played',0)}",38,SH-52)
        best_s=max((e["score"] for e in SCORES
                    if e["name"]==SETTINGS["player_name"]),default=0)
        if best_s>0:
            footer(f"Personal Best: {best_s}",50,SH-30,right=True)

        t+=1; pygame.display.flip()

# ═══════════════════════════════════════════════════════════
#  FIRE PARTICLES  — for combo x3+ on snake head
# ═══════════════════════════════════════════════════════════
class FirePt:
    __slots__=["x","y","vx","vy","life","ml","size"]
    def __init__(self,x,y):
        self.x=float(x); self.y=float(y)
        self.vx=random.uniform(-1.8,1.8)
        self.vy=random.uniform(-4.0,-1.5)
        self.life=self.ml=random.randint(12,28)
        self.size=random.randint(3,9)
    def tick(self):
        self.x+=self.vx; self.y+=self.vy
        self.vy-=0.05
        self.life-=1
    def draw(self,surf):
        a=self.life/self.ml
        if a>0.6:   col=(255,255,int(255*(a-0.6)/0.4))
        elif a>0.3: col=(255,int(255*(a-0.3)/0.3),0)
        else:       col=(int(255*a/0.3),0,0)
        sz=max(1,int(self.size*a))
        pygame.draw.circle(surf,col,(int(self.x),int(self.y)),sz)

FIRE_PARTS=[]
def add_fire(x,y,n=4):
    for _ in range(n): FIRE_PARTS.append(FirePt(x,y))
def tick_fire(surf):
    for p in FIRE_PARTS[:]:
        p.tick(); p.draw(surf)
        if p.life<=0: FIRE_PARTS.remove(p)

# ═══════════════════════════════════════════════════════════
#  COUNTDOWN SCREEN  (3 – 2 – 1 – GO!)
# ═══════════════════════════════════════════════════════════
def scr_countdown():
    """Numbers ride in from the right like a train, pause at centre, exit left."""
    font_big=F["hero"]
    steps=[("3",C["red"]),("2",C["orange"]),("1",C["gold"]),("GO!",C["green"])]

    # timing (in frames at 60fps)
    SLIDE_IN  = 14   # frames to arrive at centre
    HOLD      = 22   # frames sitting at centre
    SLIDE_OUT = 14   # frames to exit left
    TOTAL     = SLIDE_IN + HOLD + SLIDE_OUT

    # easing — smooth decelerate in, accelerate out
    def ease_out(t): return 1-(1-t)**3
    def ease_in(t):  return t**3

    cy=SH//2

    for label,col in steps:
        frame=0
        s=font_big.render(label,True,col)
        sw2,sh2=s.get_width(),s.get_height()

        while frame<TOTAL:
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: save_data(); pygame.quit(); sys.exit()

            # dark overlay drawn over whatever is on screen
            ovl=pygame.Surface((SW,SH),pygame.SRCALPHA)
            ovl.fill((0,0,0,160))
            screen.blit(ovl,(0,0))

            # compute x position
            if frame < SLIDE_IN:
                # arriving from right
                p=ease_out(frame/SLIDE_IN)
                lx=int(SW + sw2//2 + (SW//2 - SW - sw2//2)*p)
            elif frame < SLIDE_IN+HOLD:
                # sitting at centre
                lx=SW//2
            else:
                # exiting to left
                p=ease_in((frame-SLIDE_IN-HOLD)/SLIDE_OUT)
                lx=int(SW//2 + (-SW//2 - sw2//2 - SW//2)*p)

            # motion trail — ghost copies behind the label while moving
            if frame < SLIDE_IN or frame >= SLIDE_IN+HOLD:
                speed_frac=abs(lx-SW//2)/SW
                for ghost in range(1,4):
                    gx=lx + ghost*int(30*speed_frac)*(1 if frame<SLIDE_IN else -1)
                    ga=max(0,80-ghost*25)
                    gs=font_big.render(label,True,col)
                    gs.set_alpha(ga)
                    screen.blit(gs,gs.get_rect(center=(gx,cy)))

            # subtle colour glow behind (tight, not wild)
            pad=18
            glow=pygame.Surface((sw2+pad*2,sh2+pad*2),pygame.SRCALPHA)
            pygame.draw.rect(glow,(*col,45),glow.get_rect(),border_radius=20)
            screen.blit(glow,(lx-sw2//2-pad,cy-sh2//2-pad))

            # main label
            screen.blit(s,s.get_rect(center=(lx,cy)))

            # track strip — thin horizontal line the number rides on
            pygame.draw.line(screen,(*col,60),(0,cy+sh2//2+8),(SW,cy+sh2//2+8),2)

            pygame.display.flip()
            clock.tick(60)
            frame+=1

# ═══════════════════════════════════════════════════════════
#  SCREEN: SETTINGS  — clean, no emoji buttons
# ═══════════════════════════════════════════════════════════
def scr_settings():
    global _sy
    cx=SW//2; ni=SETTINGS["player_name"]; typing=False; t=0
    diff_o=["Easy","Normal","Hard","Expert"]
    diff_cols=[C["green"],C["cyan"],C["orange"],C["red"]]

    Y={"title":82,"diff_lbl":178,"diff_row":225,
       "snd_lbl":310,"snd_btn":355,
       "skin_lbl":435,"skin_row":482,
       "name_lbl":565,"name_row":610,"back":725}

    def mk_diff():
        return [Btn(cx-450+i*300,Y["diff_row"],265,58,d,
                    diff_cols[i] if d==SETTINGS["difficulty"] else (42,38,88),
                    font=F["sm_b"])
                for i,d in enumerate(diff_o)]
    dbtn=mk_diff()
    snd=Btn(cx,Y["snd_btn"],280,58,"",C["teal"],font=F["sm_b"])
    sp =Btn(cx-245,Y["skin_row"],58,58," < ",(42,38,88),font=F["md"])
    sn =Btn(cx+245,Y["skin_row"],58,58," > ",(42,38,88),font=F["md"])
    back=Btn(cx,Y["back"],300,68,"BACK",C["pink"],font=F["menu"])

    while True:
        clock.tick(60); _sy=(_sy+0.18)%SH
        mx,my=pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: save_data(); pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN:
                if typing:
                    if ev.key==pygame.K_RETURN: typing=False
                    elif ev.key==pygame.K_BACKSPACE: ni=ni[:-1]
                    elif len(ni)<14 and ev.unicode.isprintable(): ni+=ev.unicode
                elif ev.key==pygame.K_ESCAPE:
                    SETTINGS["player_name"]=ni; save_data(); return
            if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                nb=pygame.Rect(cx-215,Y["name_row"]-26,430,52)
                typing=nb.collidepoint(ev.pos)
                for i,b in enumerate(dbtn):
                    if b.hit(ev):
                        SETTINGS["difficulty"]=diff_o[i]; play("click"); dbtn=mk_diff()
                if snd.hit(ev): SETTINGS["sound"]=not SETTINGS["sound"]; play("click")
                if sp.hit(ev): SETTINGS["skin"]=(SETTINGS["skin"]-1)%len(SKINS); play("click")
                if sn.hit(ev): SETTINGS["skin"]=(SETTINGS["skin"]+1)%len(SKINS); play("click")
                if back.hit(ev):
                    SETTINGS["player_name"]=ni; save_data(); play("click"); return

        draw_bg(screen,t); draw_stars(screen,t)
        tc(screen,"SETTINGS",F["xl"],C["gold"],cx,Y["title"],shadow=True)
        draw_divider(screen,Y["title"]+50,C["dim2"],400,cx)

        # Difficulty
        tc(screen,"DIFFICULTY",F["xs_b"],C["dim"],cx,Y["diff_lbl"])
        for b in dbtn: b.update(mx,my); b.draw(screen)

        # Sound
        snd.label="SOUND  ON" if SETTINGS["sound"] else "SOUND  OFF"
        snd.bg=C["teal"] if SETTINGS["sound"] else (70,70,95)
        tc(screen,"AUDIO",F["xs_b"],C["dim"],cx,Y["snd_lbl"])
        snd.update(mx,my); snd.draw(screen)

        # Skin preview
        sk=SETTINGS["skin"]
        tc(screen,"SNAKE SKIN",F["xs_b"],C["dim"],cx,Y["skin_lbl"])
        tc(screen,SKINS[sk]["name"],F["md"],C["white"],cx,Y["skin_row"])
        # colour swatch dots
        for i,col in enumerate([SKINS[sk]["head"],
            lerp_col(SKINS[sk]["head"],SKINS[sk]["tail"],0.5),
            SKINS[sk]["tail"]]):
            pygame.draw.circle(screen,(20,15,48),(cx-28+i*28,Y["skin_row"]+44),14)
            pygame.draw.circle(screen,col,(cx-28+i*28,Y["skin_row"]+44),12)
            pygame.draw.circle(screen,(255,255,255,60),(cx-28+i*28,Y["skin_row"]+40),4)
        sp.update(mx,my); sp.draw(screen)
        sn.update(mx,my); sn.draw(screen)

        # Name
        tc(screen,"PLAYER NAME",F["xs_b"],C["dim"],cx,Y["name_lbl"])
        cursor="|" if typing and int(t*0.5)%2==0 else ""
        tc(screen,ni+cursor,F["md"],C["white"],cx,Y["name_row"])
        nw=F["md"].size(ni+cursor)[0]
        line_col=C["gold"] if typing else C["dim"]
        pygame.draw.line(screen,line_col,
            (cx-nw//2-6,Y["name_row"]+28),(cx+nw//2+6,Y["name_row"]+28),2)

        back.update(mx,my); back.draw(screen)
        draw_divider(screen,Y["back"]-46,C["dim2"],400,cx)
        t+=1; pygame.display.flip()

# ═══════════════════════════════════════════════════════════
#  SCREEN: SCORES  — polished table
# ═══════════════════════════════════════════════════════════
def scr_scores():
    global _sy
    cx=SW//2
    back=Btn(cx,960,300,68,"BACK",C["pink"],font=F["menu"])
    while True:
        clock.tick(60); _sy=(_sy+0.18)%SH
        mx,my=pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: save_data(); pygame.quit(); sys.exit()
            if back.hit(ev) or (ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE):
                play("click"); return

        draw_bg(screen,0); draw_stars(screen,0)
        tc(screen,"HIGH SCORES",F["xl"],C["gold"],cx,82,shadow=True)
        draw_divider(screen,132,C["dim2"],600,cx)

        CX=[cx-540,cx-320,cx-80,cx+130,cx+320,cx+490]
        HEADS=["RANK","NAME","SCORE","LEVEL","MODE","DATE"]
        HCOLS=[C["silver"],C["white"],C["gold"],C["cyan"],C["pink"],C["dim"]]
        for i,(h,hc) in enumerate(zip(HEADS,HCOLS)):
            tc(screen,h,F["xs_b"],hc,CX[i],172)
        pygame.draw.line(screen,C["dim"],(cx-620,192),(cx+560,192),1)

        RANK_COLS=[C["gold"],C["silver"],(212,130,55)]
        RANK_LABELS=["1ST","2ND","3RD"]
        for rank,e in enumerate(SCORES[:9]):
            y=218+rank*72
            rc=RANK_COLS[rank] if rank<3 else C["white"]
            # row bg for top 3
            if rank<3:
                row_bg=pygame.Surface((1200,62), pygame.SRCALPHA)
                row_bg.fill((*rc,10))
                screen.blit(row_bg,(cx-610,y-28))

            lbl=RANK_LABELS[rank] if rank<3 else f"#{rank+1}"
            vals=[lbl, e["name"], str(e["score"]), str(e["level"]),
                  e.get("mode","?"), e.get("date","?")]
            for i,v in enumerate(vals):
                tc(screen,v,F["sm_b"] if rank<3 else F["sm"],rc,CX[i],y)
            pygame.draw.line(screen,C["dim2"],(cx-620,y+34),(cx+560,y+34),1)

        if not SCORES:
            tc(screen,"No scores yet - go play!",F["lg"],C["dim"],cx,420)

        total=SETTINGS.get("total_eaten",0)
        if total>0:
            tc(screen,f"Total symbols eaten across all games: {total}",
               F["xs"],C["dim"],cx,920)

        draw_divider(screen,940,C["dim2"],600,cx)
        back.update(mx,my); back.draw(screen)
        pygame.display.flip()

# ═══════════════════════════════════════════════════════════
#  SCREEN: PAUSE  — overlay
# ═══════════════════════════════════════════════════════════
def scr_pause():
    cx=SW//2
    res =Btn(cx,490,340,70,"RESUME",    C["green"],font=F["lg"])
    menu=Btn(cx,578,340,70,"MAIN MENU", C["indigo"],font=F["menu"])
    ovl=pygame.Surface((SW,SH),pygame.SRCALPHA); ovl.fill((0,0,0,205))
    while True:
        clock.tick(60); mx,my=pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: save_data(); pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE: return "resume"
            if res.hit(ev): return "resume"
            if menu.hit(ev): return "menu"
        screen.blit(ovl,(0,0))

        # pause card — taller to fit controls section
        card=pygame.Surface((560,380),pygame.SRCALPHA)
        card.fill((10,7,42,245))
        pygame.draw.rect(card,C["indigo"],card.get_rect(),2,border_radius=22)
        screen.blit(card,(cx-280,340))

        tc(screen,"PAUSED",F["xl"],C["gold"],cx,390,shadow=True)
        draw_divider(screen,428,C["dim2"],400,cx)

        res.update(mx,my); res.draw(screen)
        menu.update(mx,my); menu.draw(screen)

        # keyboard controls hint
        draw_divider(screen,660,C["dim2"],400,cx)
        tc(screen,"CONTROLS",F["xs_b"],C["dim"],cx,678)
        hints=[
            ("Move",    "Arrow Keys / WASD"),
            ("Pause",   "ESC"),
        ]
        for i,(lbl,key) in enumerate(hints):
            hy=700+i*28
            tc(screen,lbl,F["xs"],C["dim"],cx-80,hy)
            tc(screen,key,F["xs_b"],C["silver"],cx+70,hy)

        pygame.display.flip()

# ═══════════════════════════════════════════════════════════
#  SCREEN: GAME OVER
# ═══════════════════════════════════════════════════════════
def scr_gameover(g):
    record(g.score, g.level); play("over")
    cx=SW//2
    retry=Btn(cx,620,380,76,"PLAY AGAIN",C["green"],font=F["lg"])
    menu =Btn(cx,718,380,76,"MAIN MENU", C["indigo"],font=F["menu"])
    t=0
    while True:
        clock.tick(60); mx,my=pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: save_data(); pygame.quit(); sys.exit()
            if retry.hit(ev): return "retry"
            if menu.hit(ev): return "menu"

        draw_bg(screen,t); draw_stars(screen,t)

        # large title
        wave=int(math.sin(t*0.045)*8)
        tc(screen,"GAME OVER",F["hero"],C["red"],cx,185+wave,shadow=True)
        draw_divider(screen,250+wave,C["dim2"],500,cx)
        tc(screen,f"{SETTINGS['player_name']}'s Run",F["xs"],C["dim"],cx,270+wave)

        # stat cards
        stats=[("SCORE",str(g.score),C["gold"]),
               ("LEVEL",str(g.level),C["cyan"]),
               ("MODE",SETTINGS["mode"],C["pink"])]
        for i,(lbl,val,col) in enumerate(stats):
            sx=cx-300+i*300
            card=pygame.Surface((240,110), pygame.SRCALPHA)
            card.fill((12,8,42,200))
            pygame.draw.rect(card, col, card.get_rect(), 1, border_radius=14)
            screen.blit(card,(sx-120,310))
            tc(screen,lbl,F["xs_b"],C["dim"],sx,330)
            tc(screen,val,F["lg"],col,sx,380)

        best=max((e["score"] for e in SCORES
                  if e["name"]==SETTINGS["player_name"]),default=0)
        if g.score==best and best>0:
            pb_wave=int(math.sin(t*0.08)*5)
            tc(screen,"NEW PERSONAL BEST!",F["md"],C["gold"],cx,455+pb_wave,shadow=True)

        retry.update(mx,my); retry.draw(screen)
        menu.update(mx,my); menu.draw(screen)
        tick_pts(screen); t+=1; pygame.display.flip()

# ═══════════════════════════════════════════════════════════
#  GAMEPLAY
# ═══════════════════════════════════════════════════════════
def scr_game():
    global _sy
    G.reset(); build_sides(); build_bottom()
    FIRE_PARTS.clear()

    # draw initial board frame so countdown has something behind it
    t=0
    draw_bg(screen,t); draw_stars(screen,t)
    draw_sides(screen,t); draw_bottom(screen,t)
    draw_hud(G,t); draw_board(G,t)
    pygame.display.flip()

    # 3-2-1 GO! countdown
    scr_countdown()

    mt=0
    while True:
        dt=clock.tick(60); mt+=dt; _sy=(_sy+0.12)%SH
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: save_data(); pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN:
                k=ev.key; d=G.dir
                if k in(pygame.K_UP,   pygame.K_w) and d["y"]==0: G.ndir={"x":0,"y":-1}
                if k in(pygame.K_DOWN, pygame.K_s) and d["y"]==0: G.ndir={"x":0,"y": 1}
                if k in(pygame.K_LEFT, pygame.K_a) and d["x"]==0: G.ndir={"x":-1,"y":0}
                if k in(pygame.K_RIGHT,pygame.K_d) and d["x"]==0: G.ndir={"x": 1,"y":0}
                if k==pygame.K_ESCAPE:
                    if scr_pause()=="menu": return "menu"
        if mt>=G.speed:
            mt=0
            if G.step()=="dead": return "gameover"

        draw_bg(screen,t); draw_stars(screen,t)
        draw_sides(screen,t); draw_bottom(screen,t)
        draw_hud(G,t); draw_board(G,t)

        # fire on snake head when combo x3+
        if G.combo>=3 and G.snake:
            hx=BX+G.snake[0]["x"]*CELL+CELL//2
            hy=BY+G.snake[0]["y"]*CELL+CELL//2
            add_fire(hx,hy,n=5)
        tick_fire(screen)

        tick_pts(screen)

        # level-up flash banner
        if G.lvlf>0:
            a=min(255,int(280*G.lvlf/90))
            banner=pygame.Surface((600,80),pygame.SRCALPHA)
            banner.fill((10,7,38,int(a*0.8)))
            pygame.draw.rect(banner,(*C["gold"],a),banner.get_rect(),2,border_radius=18)
            bx2=SW//2-300
            screen.blit(banner,(bx2,SH//2-40))
            lv_s=F["xl"].render(f"LEVEL {G.level}  UP!",True,C["gold"])
            lv_s.set_alpha(a)
            screen.blit(lv_s,lv_s.get_rect(center=(SW//2,SH//2)))
            G.lvlf-=1

        t+=1; pygame.display.flip()

# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
def main():
    state="menu"
    while True:
        if   state=="menu":     result=scr_menu()
        elif state=="play":     result=scr_game()
        elif state=="gameover": result=scr_gameover(G)
        elif state=="settings": scr_settings(); result="menu"
        elif state=="scores":   scr_scores();   result="menu"
        elif state=="quit":     save_data(); pygame.quit(); sys.exit()
        else: result="menu"
        if result=="quit": save_data(); pygame.quit(); sys.exit()
        state="play" if result=="retry" else result

if __name__=="__main__":
    main()