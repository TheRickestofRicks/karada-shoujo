#!/usr/bin/env python3
"""Custom GUI skin (textbox, namebox, choice buttons, frames) in the game's cozy palette."""
import os
from PIL import Image, ImageDraw, ImageFilter
G = os.path.join(os.path.dirname(__file__), "..", "game", "gui")
S = 2

def save(img, rel):
    w, h = img.size
    img.resize((w // S, h // S), Image.LANCZOS).save(os.path.join(G, rel))

def grad_panel(w, h, r, top, bot, line=None, border=None):
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    g = Image.new("RGBA", img.size)
    px = g.load()
    for y in range(img.size[1]):
        t = y / (img.size[1] - 1)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(4))
        for x in range(img.size[0]):
            px[x, y] = c
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, img.size[0] - 1, img.size[1] - 1], radius=r * S, fill=255)
    img.paste(g, (0, 0), m)
    d = ImageDraw.Draw(img)
    if border:
        d.rounded_rectangle([S, S, img.size[0] - 1 - S, img.size[1] - 1 - S], radius=r * S, outline=border, width=2 * S)
    if line:
        for x in range(r * S, img.size[0] - r * S):
            t = (x - r * S) / (img.size[0] - 2 * r * S)
            c = tuple(int(line[0][i] + (line[1][i] - line[0][i]) * t) for i in range(4))
            d.line([(x, 2 * S), (x, 5 * S)], fill=c)
    return img

# Textbox: 1280x185, inset panel 1220 wide
tb = Image.new("RGBA", (1280 * S, 185 * S), (0, 0, 0, 0))
panel = grad_panel(1220, 170, 22, (34, 30, 52, 228), (22, 20, 36, 240),
                   line=((159, 214, 255, 230), (255, 196, 170, 230)), border=(255, 255, 255, 40))
tb.paste(panel, (30 * S, 8 * S), panel)
save(tb, "textbox.png")

# Namebox pill
nb = grad_panel(240, 42, 21, (58, 50, 86, 250), (40, 34, 62, 250), border=(255, 196, 170, 200))
save(nb, "namebox.png")

# Choice buttons (790x48)
save(grad_panel(790, 48, 24, (30, 28, 46, 215), (22, 20, 34, 225), border=(159, 214, 255, 90)), "button/choice_idle_background.png")
save(grad_panel(790, 48, 24, (159, 214, 255, 245), (120, 182, 236, 245), border=(255, 255, 255, 160)), "button/choice_hover_background.png")

# Generic frame (confirm dialogs, notify)
save(grad_panel(600, 250, 24, (34, 30, 52, 240), (22, 20, 36, 245), border=(159, 214, 255, 110)), "frame.png")
save(grad_panel(300, 50, 16, (34, 30, 52, 230), (22, 20, 36, 235), border=(159, 214, 255, 110)), "notify.png")
print("gui ok")
