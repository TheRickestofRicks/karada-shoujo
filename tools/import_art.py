#!/usr/bin/env python3
"""Import GenerateImage outputs from art_src into game/images/.

Sprites are keyed to transparent PNG, cropped thigh-up to 540px.
Device art is keyed to transparent PNG (no thigh crop) and fitted to 700px max.
Backgrounds and title key art are resized to 1280x720.

    python3 import_art.py [--only alias1,alias2] [extra_search_dir ...]

Looks for files by alias (hikari_neutral.jpg, yuzu_idle.png, ...) in the
search dirs. Missing files are skipped and the game keeps using its placeholder.
"""
import os, sys
from PIL import Image, ImageChops, ImageFilter, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
IMG = os.path.join(ROOT, "game", "images")
ART_SRC = os.path.join(ROOT, "art_src")
# --only a,b,c  -> import just these aliases (faster re-runs)
ONLY = None
_args = list(sys.argv[1:])
if "--only" in _args:
    i = _args.index("--only")
    ONLY = set(_args[i + 1].split(","))
    del _args[i:i + 2]
SEARCH = _args + [
    ART_SRC,
    "/workspace/games/art_src",
    os.path.join(HERE, "art_src"),
]

SPRITES = [
    "hikari_neutral", "hikari_smile", "hikari_distant",
    "mio_neutral", "mio_shy", "mio_open",
    "daichi_neutral", "daichi_laugh", "daichi_skeptical",
    "kurosawa_neutral", "kurosawa_stern", "kurosawa_wry",
    "ran_neutral", "ran_grin", "ran_uneasy",
]
DEVICES = [
    "yuzu_idle", "yuzu_happy", "yuzu_thinking", "yuzu_distant",
    "sora_idle", "sora_happy", "sora_thinking", "sora_apologetic", "sora_distant",
    "rei_idle", "rei_happy", "rei_working", "rei_distant",
]
BACKGROUNDS = {
    "bg/bedroom_morning": "bedroom_morning",
    "bg/cafeteria": "cafeteria",
    "bg/library": "library",
    "bg/bedroom_night": "bedroom_night",
    "bg/classroom": "classroom",
    "bg/street_dusk": "street_dusk",
    "bg/bookstore": "bookstore",
    "bg/downtown": "downtown",
    "title_keyart": "title_keyart",
}

SPRITE_H = 540          # on-screen height; sources are already thigh-up
CROP_FRAC = 1.00        # do not crop further (0.60 was for full-body sources)
DEVICE_MAX = 700        # longest side after cutout


def find(alias):
    for d in SEARCH:
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            p = os.path.join(d, alias + ext)
            if os.path.exists(p):
                return p
        # also allow the alias used as a bare filename
        p = os.path.join(d, alias)
        if os.path.exists(p):
            return p
    return None


_session = None
def cutout(img):
    global _session
    from rembg import remove, new_session
    if _session is None:
        _session = new_session("isnet-anime")
    return remove(img, session=_session, alpha_matting=False)


def _corner_color(im):
    w, h = im.size
    pts = [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3),
           (w // 2, 2), (w // 2, h - 3), (2, h // 2), (w - 1, h // 2)]
    cols = [im.getpixel(p)[:3] for p in pts]
    # median per channel
    return tuple(sorted(c[i] for c in cols)[len(cols) // 2] for i in range(3))


def flat_bg_mask(im, thresh=14, color_dist=28):
    """255 where the pixel is flat studio background.

    Combines a border flood-fill (so anti-aliased edges stay) with a global
    color-distance key (so enclosed hair gaps and JPEG speckles go too).
    """
    work = im.copy()
    key = (255, 0, 255)
    w, h = work.size
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
             (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
    for xy in seeds:
        if work.getpixel(xy) != key:
            ImageDraw.floodfill(work, xy, key, thresh=thresh)
    r, g, b = work.split()
    flood = ImageChops.multiply(
        ImageChops.multiply(
            r.point(lambda v: 255 if v == 255 else 0),
            g.point(lambda v: 255 if v == 0 else 0),
        ),
        b.point(lambda v: 255 if v == 255 else 0),
    )
    if color_dist <= 0:
        # flood-fill only: enclosed regions that match the backdrop colour
        # (a gray book, silver hair streaks) stay opaque.
        return flood
    bg = _corner_color(im)
    dist = Image.new("L", im.size)
    dp = dist.load()
    px = im.load()
    for y in range(h):
        for x in range(w):
            c = px[x, y]
            d = ((c[0] - bg[0]) ** 2 + (c[1] - bg[1]) ** 2 + (c[2] - bg[2]) ** 2) ** 0.5
            dp[x, y] = 255 if d <= color_dist else 0
    # union
    mask = ImageChops.lighter(flood, dist)
    return mask


def drop_speckles(alpha, min_px=24):
    """Clear tiny opaque islands (JPEG crumbs left in the keyed area)."""
    from PIL import ImageDraw as _ID
    bin = alpha.point(lambda v: 255 if v > 24 else 0)
    # connected components via flood fill on a working copy
    work = bin.convert("RGB")
    w, h = work.size
    px = bin.load()
    seen = bytearray(w * h)
    # only consider components that do not touch the (already empty) border much;
    # we iterate opaque pixels
    wp = work.load()
    mark = 1
    for y in range(h):
        for x in range(w):
            if px[x, y] < 255 or seen[y * w + x]:
                continue
            # flood
            stack = [(x, y)]
            cells = []
            seen[y * w + x] = 1
            while stack:
                cx, cy = stack.pop()
                cells.append((cx, cy))
                for nx, ny in ((cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx] and px[nx, ny] == 255:
                        seen[ny * w + nx] = 1
                        stack.append((nx, ny))
            if len(cells) < min_px:
                for cx, cy in cells:
                    px[cx, cy] = 0
    # apply: zero alpha where bin was cleared
    return ImageChops.multiply(alpha, bin)


def key_to_rgba(src, use_rembg=True, thresh=14, color_dist=28, speckle=24):
    im = Image.open(src).convert("RGB")
    if use_rembg:
        try:
            rgba = cutout(im)
            alpha = rgba.split()[-1]
        except Exception as e:
            print("rembg failed (%s); using flat-background key" % e)
            alpha = Image.new("L", im.size, 255)
    else:
        alpha = Image.new("L", im.size, 255)
    bg = flat_bg_mask(im, thresh=thresh, color_dist=color_dist)
    # If rembg missed most of the figure, trust the flat-bg key alone.
    if use_rembg:
        fg = bg.point(lambda v: 255 if v == 0 else 0)
        fg_count = 0
        covered = 0
        # sample via resize for speed
        tiny_bg = bg.resize((80, 80), Image.NEAREST)
        tiny_a = alpha.resize((80, 80), Image.NEAREST)
        bp, ap = tiny_bg.load(), tiny_a.load()
        for y in range(80):
            for x in range(80):
                if bp[x, y] == 0:
                    fg_count += 1
                    if ap[x, y] > 128:
                        covered += 1
        if fg_count and covered / fg_count < 0.6:
            print("  rembg coverage %.0f%% on %s; using flat-background key" %
                  (covered / fg_count * 100, os.path.basename(src)))
            alpha = Image.new("L", im.size, 255)
    alpha = ImageChops.subtract(alpha, bg)
    if speckle:
        alpha = drop_speckles(alpha, min_px=speckle)
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.6))
    rgba = im.convert("RGBA")
    rgba.putalpha(alpha)
    a = rgba.split()[-1].point(lambda v: 255 if v > 24 else 0)
    bbox = a.getbbox()
    if not bbox:
        raise RuntimeError("empty cutout for %s" % src)
    return rgba.crop(bbox)


# Characters whose own colours are close to the gray studio backdrop
# (Kurosawa's silver hair and gray book): rembg + a tight border flood only.
SPRITE_KEY = {
    "kurosawa": dict(thresh=5, color_dist=0),
    "ran": dict(thresh=8, color_dist=0),
}


def do_sprite(src, dst):
    who = os.path.basename(src).split("_")[0].lower()
    kw = SPRITE_KEY.get(who, dict(thresh=14))
    rgba = key_to_rgba(src, use_rembg=True, **kw)
    w, h = rgba.size
    rgba = rgba.crop((0, 0, w, int(h * CROP_FRAC)))
    scale = SPRITE_H / rgba.size[1]
    rgba = rgba.resize((max(1, int(rgba.size[0] * scale)), SPRITE_H), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    rgba.save(dst)
    print("  sprite %s -> %s %s" % (os.path.basename(src), os.path.basename(dst), rgba.size))


def do_device(src, dst):
    # Devices are solid props on a flat studio backdrop; the flat-bg key is
    # more reliable than rembg (which can eat glows and window chrome).
    # Yuzu's beige plastic has soft contact shadows, so keep the key tight.
    # Rei's amber glow fades into the studio gray and needs a wider key.
    name = os.path.basename(src).lower()
    if name.startswith("yuzu"):
        kwargs = dict(thresh=16, color_dist=14, speckle=48)
    elif name.startswith("rei"):
        kwargs = dict(thresh=22, color_dist=42, speckle=40)
    else:
        kwargs = dict(thresh=18, color_dist=22, speckle=40)
    rgba = key_to_rgba(src, use_rembg=False, **kwargs)
    w, h = rgba.size
    long_side = max(w, h)
    if long_side > DEVICE_MAX:
        scale = DEVICE_MAX / long_side
        rgba = rgba.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    rgba.save(dst)
    print("  device %s -> %s %s" % (os.path.basename(src), os.path.basename(dst), rgba.size))


def do_bg(src, dst):
    im = Image.open(src).convert("RGB").resize((1280, 720), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, optimize=True)
    print("  bg %s -> %s %s" % (os.path.basename(src), os.path.basename(dst), im.size))


if __name__ == "__main__":
    done, missing = [], []
    def _skip(a):
        return ONLY is not None and a not in ONLY and a.split("/")[-1] not in ONLY
    for alias in SPRITES:
        if _skip(alias):
            continue
        p = find(alias)
        if not p:
            missing.append(alias)
            continue
        do_sprite(p, os.path.join(IMG, "sprites", alias + ".png"))
        done.append(alias)
    for alias in DEVICES:
        if _skip(alias):
            continue
        p = find(alias)
        if not p:
            missing.append(alias)
            continue
        do_device(p, os.path.join(IMG, "devices", alias + ".png"))
        done.append(alias)
    for dest, alias in BACKGROUNDS.items():
        if _skip(alias):
            continue
        p = find(alias)
        if not p:
            missing.append(dest)
            continue
        do_bg(p, os.path.join(IMG, dest + ".png"))
        done.append(dest)
    print("imported:", done)
    print("missing (placeholder used):", missing)
