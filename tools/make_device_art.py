#!/usr/bin/env python3
"""Procedural device/interface art for the three non-avatar girls (PIL).
Yuzu = cozy beige retro monitor w/ green CRT face glyph.
Sora = clean chat-app window w/ sky-blue avatar orb.
Rei  = dark agent dashboard w/ amber status lights.
States: idle, happy, thinking, distant.  Also origin accent badges.
Run: python3 make_device_art.py  -> game/images/devices/*.png
"""
import math, os
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "game", "images", "devices")
S = 2  # supersample

def canvas(w, h):
    return Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))

def fin(img, path):
    w, h = img.size
    img = img.resize((w // S, h // S), Image.LANCZOS)
    img.save(os.path.join(OUT, path))

def rr(d, box, r, **kw):
    d.rounded_rectangle([v * S for v in box], radius=r * S, **kw)

def glow(img, box, r, color, blur):
    g = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).rounded_rectangle([v * S for v in box], radius=r * S, fill=color)
    g = g.filter(ImageFilter.GaussianBlur(blur * S))
    return Image.alpha_composite(g, img)

def vgrad(size, top, bot):
    w, h = size
    g = Image.new("RGBA", size)
    px = g.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(4))
        for x in range(w):
            px[x, y] = c
    return g

def paste_grad(img, box, r, top, bot):
    x0, y0, x1, y1 = [v * S for v in box]
    g = vgrad((x1 - x0, y1 - y0), top, bot)
    m = Image.new("L", g.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, g.size[0] - 1, g.size[1] - 1], radius=r * S, fill=255)
    img.paste(g, (x0, y0), m)

def face(d, cx, cy, state, col, scale=1.0, dim=False):
    """Simple glyph face. cx,cy in unscaled px."""
    k = scale * S
    lw = int(9 * k)
    ex = 52 * scale
    if state == "happy":   # ^ ^ and wide smile
        for sx in (-ex, ex):
            pts = [((cx + sx - 22 * scale) * S, (cy - 18 * scale) * S), ((cx + sx) * S, (cy - 40 * scale) * S), ((cx + sx + 22 * scale) * S, (cy - 18 * scale) * S)]
            d.line(pts, fill=col, width=lw, joint="curve")
        d.arc([(cx - 46 * scale) * S, (cy - 10 * scale) * S, (cx + 46 * scale) * S, (cy + 50 * scale) * S], 20, 160, fill=col, width=lw)
    elif state == "thinking":  # eyes up-left, small o mouth, dots
        for sx in (-ex, ex):
            d.ellipse([(cx + sx - 14 * scale) * S, (cy - 44 * scale) * S, (cx + sx + 10 * scale) * S, (cy - 18 * scale) * S], fill=col)
        d.ellipse([(cx - 10 * scale) * S, (cy + 18 * scale) * S, (cx + 10 * scale) * S, (cy + 36 * scale) * S], outline=col, width=int(6 * k))
        for i in range(3):
            x = cx + 150 * scale + i * 22 * scale if scale < 1.0 else cx + 70 * scale + i * 22 * scale
            d.ellipse([(x - 6 * scale) * S, (cy - 80 * scale) * S, (x + 6 * scale) * S, (cy - 68 * scale) * S], fill=col)
    elif state == "distant":  # flat line eyes, flat mouth
        for sx in (-ex, ex):
            d.line([((cx + sx - 20 * scale) * S, (cy - 26 * scale) * S), ((cx + sx + 20 * scale) * S, (cy - 26 * scale) * S)], fill=col, width=lw)
        d.line([((cx - 22 * scale) * S, (cy + 28 * scale) * S), ((cx + 22 * scale) * S, (cy + 28 * scale) * S)], fill=col, width=int(7 * k))
    else:  # idle: tall oval eyes, small gentle smile
        for sx in (-ex, ex):
            d.ellipse([(cx + sx - 12 * scale) * S, (cy - 46 * scale) * S, (cx + sx + 12 * scale) * S, (cy - 10 * scale) * S], fill=col)
        d.arc([(cx - 26 * scale) * S, (cy + 0 * scale) * S, (cx + 26 * scale) * S, (cy + 36 * scale) * S], 30, 150, fill=col, width=int(7 * k))

# ---------------------------------------------------------------- Yuzu
def yuzu(state):
    W, H = 640, 640
    img = canvas(W, H)
    scr_on = state != "distant"
    green = (150, 230, 140, 255) if scr_on else (90, 130, 90, 255)
    img = glow(img, (70, 50, 570, 450), 40, (150, 230, 140, 110 if scr_on else 30), 40)
    d = ImageDraw.Draw(img)
    # stand
    paste_grad(img, (250, 455, 390, 540), 10, (214, 205, 180, 255), (176, 166, 140, 255))
    paste_grad(img, (170, 530, 470, 575), 18, (222, 214, 190, 255), (180, 170, 146, 255))
    # body (beige bezel)
    paste_grad(img, (60, 40, 580, 470), 46, (236, 228, 205, 255), (196, 186, 160, 255))
    d = ImageDraw.Draw(img)
    rr(d, (60, 40, 580, 470), 46, outline=(150, 140, 116, 255), width=3 * S)
    # screen
    top, bot = ((34, 58, 38, 255), (18, 34, 22, 255)) if scr_on else ((30, 36, 32, 255), (20, 24, 22, 255))
    paste_grad(img, (110, 85, 530, 400), 30, top, bot)
    d = ImageDraw.Draw(img)
    # scanlines
    for y in range(90, 398, 6):
        d.line([(115 * S, y * S), (525 * S, y * S)], fill=(0, 0, 0, 40), width=S)
    # face glow layer
    fl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(fl)
    face(fd, 320, 250, state, green, 1.25)
    blur = fl.filter(ImageFilter.GaussianBlur(8 * S))
    img = Image.alpha_composite(img, blur)
    img = Image.alpha_composite(img, fl)
    d = ImageDraw.Draw(img)
    # prompt cursor + status LED + vents
    d.rectangle([140 * S, 360 * S, 162 * S, 372 * S], fill=green)
    led = (120, 230, 120, 255) if scr_on else (120, 90, 60, 255)
    d.ellipse([500 * S, 425 * S, 516 * S, 441 * S], fill=led)
    for i in range(5):
        d.rounded_rectangle([(110 + i * 24) * S, 428 * S, (124 + i * 24) * S, 438 * S], radius=3 * S, fill=(170, 160, 134, 255))
    # glass highlight
    hl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).polygon([(120 * S, 95 * S), (300 * S, 95 * S), (170 * S, 300 * S), (120 * S, 300 * S)], fill=(255, 255, 255, 18))
    img = Image.alpha_composite(img, hl)
    fin(img, "yuzu_%s.png" % state)

# ---------------------------------------------------------------- Sora
def sora(state):
    W, H = 700, 620
    img = canvas(W, H)
    sky = (110, 190, 245, 255)
    img = glow(img, (40, 30, 660, 590), 34, (120, 200, 255, 90 if state != "distant" else 30), 34)
    paste_grad(img, (40, 30, 660, 590), 30, (250, 252, 255, 255), (232, 240, 250, 255))
    d = ImageDraw.Draw(img)
    rr(d, (40, 30, 660, 590), 30, outline=(200, 214, 232, 255), width=3 * S)
    # title bar
    paste_grad(img, (40, 30, 660, 92), 30, (232, 242, 252, 255), (220, 234, 248, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([40 * S, 70 * S, 660 * S, 92 * S], fill=(226, 238, 250, 255))
    for i, c in enumerate([(255, 140, 140), (255, 210, 120), (140, 220, 150)]):
        d.ellipse([(68 + i * 30) * S, 50 * S, (86 + i * 30) * S, 68 * S], fill=c + (255,))
    d.rounded_rectangle([260 * S, 52 * S, 440 * S, 66 * S], radius=7 * S, fill=(205, 222, 240, 255))
    # orb avatar
    ocx, ocy, r = 350, 250, 112
    orb_col_top = (170, 225, 255, 255) if state != "distant" else (180, 196, 210, 255)
    orb_col_bot = (80, 165, 235, 255) if state != "distant" else (130, 150, 170, 255)
    og = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(og).ellipse([(ocx - r - 30) * S, (ocy - r - 30) * S, (ocx + r + 30) * S, (ocy + r + 30) * S], fill=(120, 200, 255, 110 if state != "distant" else 30))
    img = Image.alpha_composite(img, og.filter(ImageFilter.GaussianBlur(22 * S)))
    g = vgrad((2 * r * S, 2 * r * S), orb_col_top, orb_col_bot)
    m = Image.new("L", g.size, 0); ImageDraw.Draw(m).ellipse([0, 0, g.size[0] - 1, g.size[1] - 1], fill=255)
    img.paste(g, ((ocx - r) * S, (ocy - r) * S), m)
    hl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse([(ocx - 72) * S, (ocy - 92) * S, (ocx - 16) * S, (ocy - 62) * S], fill=(255, 255, 255, 110))
    img = Image.alpha_composite(img, hl.filter(ImageFilter.GaussianBlur(4 * S)))
    d = ImageDraw.Draw(img)
    fstate = {"thinking": "thinking", "happy": "happy", "distant": "distant"}.get(state, "idle")
    if state == "apologetic":
        fstate = "idle"
    face(d, ocx, ocy + 12, fstate if fstate != "thinking" else "idle", (255, 255, 255, 255), 0.9)
    if state == "apologetic":  # worried brows + sweat drop
        for sx, a in ((-47, 1), (47, -1)):
            d.line([((ocx + sx - 18) * S, (ocy - 40 - 8 * a) * S), ((ocx + sx + 18) * S, (ocy - 40 + 8 * a) * S)], fill=(255, 255, 255, 255), width=6 * S)
        d.polygon([((ocx + 88) * S, (ocy - 50) * S), ((ocx + 78) * S, (ocy - 22) * S), ((ocx + 98) * S, (ocy - 22) * S)], fill=(225, 245, 255, 255))
        d.ellipse([(ocx + 77) * S, (ocy - 34) * S, (ocx + 99) * S, (ocy - 12) * S], fill=(225, 245, 255, 255))
    # chat bubbles
    d.rounded_rectangle([80 * S, 400 * S, 400 * S, 446 * S], radius=22 * S, fill=(226, 238, 250, 255))
    d.rounded_rectangle([300 * S, 460 * S, 620 * S, 506 * S], radius=22 * S, fill=sky)
    if state == "thinking":
        d.rounded_rectangle([80 * S, 460 * S, 190 * S, 506 * S], radius=22 * S, fill=(226, 238, 250, 255))
        for i in range(3):
            x = 108 + i * 26
            d.ellipse([(x - 7) * S, 476 * S, (x + 7) * S, 490 * S], fill=sky)
    # input bar
    d.rounded_rectangle([70 * S, 528 * S, 630 * S, 570 * S], radius=21 * S, fill=(255, 255, 255, 255), outline=(200, 214, 232, 255), width=2 * S)
    d.ellipse([590 * S, 534 * S, 620 * S, 564 * S], fill=sky)
    fin(img, "sora_%s.png" % state)

# ---------------------------------------------------------------- Rei
def rei(state):
    W, H = 700, 600
    img = canvas(W, H)
    amber = (255, 176, 80, 255) if state != "distant" else (150, 110, 80, 255)
    red = (255, 90, 80, 255)
    img = glow(img, (40, 40, 660, 560), 26, (255, 170, 70, 80 if state != "distant" else 20), 32)
    paste_grad(img, (40, 40, 660, 560), 24, (38, 36, 40, 255), (20, 19, 22, 255))
    d = ImageDraw.Draw(img)
    rr(d, (40, 40, 660, 560), 24, outline=(70, 64, 60, 255), width=3 * S)
    # header strip + status lights
    d.rectangle([40 * S, 96 * S, 660 * S, 99 * S], fill=(70, 60, 50, 255))
    for i in range(4):
        on = state != "distant" and (i < 3 or state == "working")
        col = amber if on else (70, 60, 50, 255)
        if state == "distant" and i == 0:
            col = red
        cx = 80 + i * 34
        lg = Image.new("RGBA", img.size, (0, 0, 0, 0))
        if on:
            ImageDraw.Draw(lg).ellipse([(cx - 16) * S, 52 * S, (cx + 16) * S, 84 * S], fill=col[:3] + (120,))
            img = Image.alpha_composite(img, lg.filter(ImageFilter.GaussianBlur(6 * S)))
        d = ImageDraw.Draw(img)
        d.ellipse([(cx - 9) * S, 59 * S, (cx + 9) * S, 77 * S], fill=col)
    d.rounded_rectangle([450 * S, 60 * S, 630 * S, 76 * S], radius=8 * S, fill=(52, 48, 50, 255))
    # eye ring
    ecx, ecy = 230, 300
    ring = Image.new("RGBA", img.size, (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse([(ecx - 120) * S, (ecy - 120) * S, (ecx + 120) * S, (ecy + 120) * S], outline=amber, width=10 * S)
    if state == "working":
        rd.arc([(ecx - 140) * S, (ecy - 140) * S, (ecx + 140) * S, (ecy + 140) * S], 300, 60, fill=amber, width=8 * S)
    face(rd, ecx, ecy + 10, {"happy": "happy", "distant": "distant", "working": "thinking"}.get(state, "idle"), amber, 0.95)
    img = Image.alpha_composite(img, ring.filter(ImageFilter.GaussianBlur(7 * S)))
    img = Image.alpha_composite(img, ring)
    d = ImageDraw.Draw(img)
    # task list on right
    for i in range(4):
        y = 170 + i * 76
        done = state == "happy" or (state == "working" and i < 2) or (state == "idle" and i < 1)
        d.rounded_rectangle([400 * S, y * S, 626 * S, (y + 52) * S], radius=10 * S, fill=(44, 40, 42, 255))
        d.rounded_rectangle([418 * S, (y + 16) * S, 438 * S, (y + 36) * S], radius=4 * S, outline=amber, width=3 * S, fill=amber if done else None)
        d.rounded_rectangle([452 * S, (y + 20) * S, (452 + 140 - i * 20) * S, (y + 32) * S], radius=6 * S, fill=(90, 80, 72, 255))
    # progress bar bottom
    d.rounded_rectangle([80 * S, 490 * S, 620 * S, 506 * S], radius=8 * S, fill=(52, 48, 50, 255))
    frac = {"idle": 0.35, "happy": 1.0, "working": 0.62, "distant": 0.1}[state]
    d.rounded_rectangle([80 * S, 490 * S, int(80 + 540 * frac) * S, 506 * S], radius=8 * S, fill=red if state == "distant" else amber)
    fin(img, "rei_%s.png" % state)

def badge(name, col):
    """Small 5-point star accent badge (migrated identity hint)."""
    W = 96
    img = canvas(W, W)
    d = ImageDraw.Draw(img)
    cx = cy = W / 2
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = 40 if i % 2 == 0 else 17
        pts.append(((cx + r * math.cos(a)) * S, (cy + r * math.sin(a)) * S))
    g = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).polygon(pts, fill=col[:3] + (160,))
    img = Image.alpha_composite(img, g.filter(ImageFilter.GaussianBlur(5 * S)))
    d = ImageDraw.Draw(img)
    d.polygon(pts, fill=col, outline=(255, 255, 255, 230), width=3 * S)
    fin(img, "badge_%s.png" % name)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for st in ("idle", "happy", "thinking", "distant"):
        yuzu(st)
    for st in ("idle", "happy", "thinking", "apologetic", "distant"):
        sora(st)
    for st in ("idle", "happy", "working", "distant"):
        rei(st)
    badge("companion", (159, 214, 255, 255))
    badge("local", (170, 230, 150, 255))
    badge("chatbot", (120, 195, 250, 255))
    badge("agent", (255, 178, 90, 255))
    print("ok", sorted(os.listdir(OUT)))
