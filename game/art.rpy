## art.rpy — images. Real art lives in game/images/; every image falls back
## to a placeholder shape if its file is missing, so the game always runs.
##
## Only the companion-app girl (Hikari's slot) has an anime avatar body.
## Local / Chatbot / Agent girls are device interfaces with mood states.
## A migrated girl takes the look of her NEW platform, plus a small star badge
## in her ORIGINAL slot's colour (and, in the companion app, a glow in that colour).

init -5 python:
    def ks_file(path, fallback, size=None):
        """Image file if present, else fallback displayable."""
        if renpy.loadable(path):
            d = path
            if size:
                d = Transform(path, xysize=size, fit="cover")
            return d
        return fallback

    def _ks_name_text(st, at, name_var, size):
        return Text(str(getattr(store, name_var, "")), size=size, color="#ffffff",
                    outlines=[(2, "#000000")]), 0.5

    def ks_device_fallback(name_var, body, screen, face, w=380, h=500):
        cx = w // 2
        return Fixed(
            Solid(body, xsize=w, ysize=h),
            Transform(Solid(screen), xsize=w - 40, ysize=h - 100, xpos=20, ypos=50),
            Transform(Solid(face), xsize=140, ysize=140, xpos=cx - 70, ypos=120),
            Transform(DynamicDisplayable(_ks_name_text, name_var, 40), xalign=0.5, ypos=300),
            xysize=(w, h))

    def ks_person_fallback(name_var, hair, body, accent):
        return Fixed(
            Transform(Solid(hair), xsize=180, ysize=180, xpos=90, ypos=0),
            Transform(Solid("#f1d3bd"), xsize=140, ysize=130, xpos=110, ypos=55),
            Transform(Solid(body), xsize=300, ysize=360, xpos=30, ypos=190),
            Transform(Solid(accent), xsize=300, ysize=24, xpos=30, ypos=260),
            Transform(DynamicDisplayable(_ks_name_text, name_var, 36), xalign=0.5, ypos=380),
            xysize=(360, 550))

## ── Backgrounds (1280x720) ───────────────────────────────────────────────
image bg black         = Solid("#000000")
image bg card          = Solid("#14111f")
image bg bedroom       = ks_file("images/bg/bedroom_morning.png", Solid("#3a3550"), (1280, 720))
image bg bedroom_night = ks_file("images/bg/bedroom_night.png",   Solid("#15132a"), (1280, 720))
image bg cafeteria     = ks_file("images/bg/cafeteria.png",       Solid("#8a6f52"), (1280, 720))
image bg library       = ks_file("images/bg/library.png",         Solid("#4d3b2f"), (1280, 720))
image bg classroom     = ks_file("images/bg/classroom.png",       Solid("#5a4a3a"), (1280, 720))
image bg street_dusk   = ks_file("images/bg/street_dusk.png",     Solid("#4a3a5a"), (1280, 720))
image bg title         = ks_file("images/title_keyart.png",       Solid("#14111f"), (1280, 720))

## ── Humans (scripted). Sprites are pre-cropped thigh-up, 540px tall. ─────
init -4 python:
    _MIO_FB = ks_person_fallback("mio_name", "#2b1d1a", "#f4f0e6", "#c03a5b")
    _DAI_FB = ks_person_fallback("daichi_name", "#111111", "#2f4b8a", "#ffd27a")

image mio = "mio neutral"
image mio neutral = ks_file("images/sprites/mio_neutral.png", _MIO_FB)
image mio shy     = ks_file("images/sprites/mio_shy.png",     _MIO_FB)
image mio open    = ks_file("images/sprites/mio_open.png",    _MIO_FB)
image daichi = "daichi neutral"
image daichi neutral   = ks_file("images/sprites/daichi_neutral.png",   _DAI_FB)
image daichi laugh     = ks_file("images/sprites/daichi_laugh.png",     _DAI_FB)
image daichi skeptical = ks_file("images/sprites/daichi_skeptical.png", _DAI_FB)

## Tuesday cast.
init -4 python:
    _KUR_FB = ks_person_fallback("kurosawa_name", "#4a4a4a", "#333333", "#d8cfc0")
    _RAN_FB = ks_person_fallback("ran_name", "#111111", "#151515", "#c9a8ff")
image kurosawa = "kurosawa neutral"
image kurosawa neutral = ks_file("images/sprites/kurosawa_neutral.png", _KUR_FB)
image kurosawa stern   = ks_file("images/sprites/kurosawa_stern.png",   _KUR_FB)
image kurosawa wry     = ks_file("images/sprites/kurosawa_wry.png",     _KUR_FB)
image ran = "ran neutral"
image ran neutral = ks_file("images/sprites/ran_neutral.png", _RAN_FB)
image ran grin    = ks_file("images/sprites/ran_grin.png",    _RAN_FB)
image ran uneasy  = ks_file("images/sprites/ran_uneasy.png",  _RAN_FB)

## ── AI girls: one image per platform slot, mood + migration aware ────────
default girl_mood = {"local": "neutral", "companion": "neutral", "chatbot": "neutral", "agent": "neutral"}
default girl_origin = {}    # slot -> original slot of the girl living there (after migration)

init -4 python:
    ## abstract mood -> file state per slot
    KS_MOOD_FILES = {
        "local":     {"neutral": "idle", "happy": "happy", "thinking": "thinking", "sorry": "thinking", "distant": "distant"},
        "chatbot":   {"neutral": "idle", "happy": "happy", "thinking": "thinking", "sorry": "apologetic", "distant": "distant"},
        "agent":     {"neutral": "idle", "happy": "happy", "thinking": "working", "sorry": "idle", "distant": "distant"},
        "companion": {"neutral": "neutral", "happy": "smile", "thinking": "neutral", "sorry": "neutral", "distant": "distant"},
    }
    KS_DEVICE_PREFIX = {"local": "yuzu", "chatbot": "sora", "agent": "rei"}
    KS_SLOT_COLOR = {"local": "#aae696", "companion": "#9fd6ff", "chatbot": "#78c3fa", "agent": "#ffb25a"}
    KS_FALLBACK = {
        "local":     ("dn_local", "#b8b29a", "#33402a", "#c9e4a8"),
        "companion": ("dn_companion", "#10131d", "#2a4f7a", "#9fd6ff"),
        "chatbot":   ("dn_chatbot", "#ececf4", "#4a3a6a", "#e0c3ff"),
        "agent":     ("dn_agent", "#1a1a1a", "#3a2416", "#ffb27a"),
    }
    ## Max on-screen box for each look (kept above the textbox).
    KS_MAX = (560, 470)
    KS_HIKARI_H = 540

    def _ks_girl_base(slot, mood):
        state = KS_MOOD_FILES[slot].get(mood, KS_MOOD_FILES[slot]["neutral"])
        if slot == "companion":
            path = "images/sprites/hikari_%s.png" % state
        else:
            path = "images/devices/%s_%s.png" % (KS_DEVICE_PREFIX[slot], state)
        if not renpy.loadable(path):
            return ks_device_fallback(*KS_FALLBACK[slot]), False
        if slot == "companion":
            return path, True
        return Transform(path, fit="contain", xysize=KS_MAX), False

    def ks_girl_dd(st, at, slot):
        mood = store.girl_mood.get(slot, "neutral")
        base, is_avatar = _ks_girl_base(slot, mood)
        origin = store.girl_origin.get(slot)
        layers = []
        if is_avatar:
            ## Device-glow framing behind the avatar: a soft panel of light in
            ## the colour of whoever she originally was. A slightly warmer
            ## glow is the in-world tell that Tsunagari's engagement layer
            ## is on (alongside the tiny banner).
            boost = False
            try:
                boost = (slot == "companion" and bool(
                    (ks_mem("companion").data or {}).get("flags", {}).get("engagement_boost")))
            except Exception:
                boost = False
            col = "#ffc6dc" if boost else KS_SLOT_COLOR.get(origin or slot)
            alpha = 0.28 if boost else 0.16
            layers.append(Transform(Solid(col), xysize=(420, 470), xalign=0.5, yalign=1.0, alpha=alpha))
            layers.append(Transform(Solid(col), xysize=(440, 4), xalign=0.5, yalign=0.0, yoffset=70, alpha=0.75 if boost else 0.6))
        layers.append(Transform(base, xalign=0.5, yalign=1.0))
        if origin and origin != slot and renpy.loadable("images/devices/badge_%s.png" % origin):
            layers.append(Transform("images/devices/badge_%s.png" % origin, xalign=0.92, yalign=0.08, zoom=0.75))
        size = (480, KS_HIKARI_H) if is_avatar else KS_MAX
        return Fixed(*layers, xysize=size), None

## Toast icon: a tight crop of Hikari's face (companion sprite is 227x540).
image hikari_icon = ConditionSwitch(
    "renpy.loadable('images/sprites/hikari_smile.png')",
    Transform("images/sprites/hikari_smile.png", crop=(20, 0, 187, 187), xysize=(72, 72)),
    "True", Solid("#9fd6ff", xsize=72, ysize=72))

image girl_local     = DynamicDisplayable(ks_girl_dd, "local")
image girl_companion = DynamicDisplayable(ks_girl_dd, "companion")
image girl_chatbot   = DynamicDisplayable(ks_girl_dd, "chatbot")
image girl_agent     = DynamicDisplayable(ks_girl_dd, "agent")

init python:
    def ks_mood(slot, mood):
        store.girl_mood[slot] = mood
        renpy.restart_interaction()

    def ks_mood_from_reply(slot, text):
        """Rough auto-expression from a reply. A refusal is NOT shown as
        'distant' (that's reserved for platform events); it reads as thoughtful."""
        t = (text or "").lower()
        if ks_llm.looks_like_refusal(text):
            return "sorry" if slot == "chatbot" else "thinking"
        if any(k in t for k in ("!", "haha", "hehe", "lol", ":)", "glad", "love that", "happy")):
            return "happy"
        return "neutral"

## ── Placement: everything sits above the textbox (720 - 185 = 535). ──────
transform ks_center:
    xalign 0.5 yanchor 1.0 ypos 560
transform ks_left:
    xalign 0.27 yanchor 1.0 ypos 560
transform ks_right:
    xalign 0.73 yanchor 1.0 ypos 560
