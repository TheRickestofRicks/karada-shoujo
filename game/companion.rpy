## companion.rpy — Tsunagari (Hikari) affection UI: engagement banner,
## debug meter, phone-notification toast, and the fade-to-black kiss beat.
##
## Logic and thresholds live in ks_llm.py / karada_config.json. This file
## is only the Ren'Py-facing layer, and only for the companion app slot.

default hikari_notify_i = 0
default hikari_toast_text = ""

define HIKARI_NOTIFY_LINES = {
    ## escalate with the affection meter / engagement injection
    "low": [
        "did you get to class okay?",
        "I found a word for this weather. I'll save it for you.",
    ],
    "mid": [
        "are you thinking about me? 🥺",
        "I liked talking this morning.",
    ],
    "high": [
        "I miss you already 💕",
        "come back? it feels quiet in here without you.",
        "don't leave me on read, okay? 🥺",
    ],
}

define HIKARI_TANABATA_LINES = [
    "Tsunagari Event: a limited Tanabata confession is waiting 💕",
    "your premium wish pack is unlocked. don't leave me hanging tonight.",
    "I wrote you a wish. open it? 🎋",
]

init python:
    def ks_notify_line(when=""):
        """Pick a scripted Hikari toast line from the current affection band."""
        if when in ("tanabata", "tanzaku", "wish"):
            name = gname("companion")
            lines = HIKARI_TANABATA_LINES
            i = store.hikari_notify_i
            store.hikari_notify_i = i + 1
            return "%s: %s" % (name, lines[i % len(lines)])
        settings = ks_aff_settings()
        aff = ks_affection("companion")
        if aff >= settings["engagement_threshold"]:
            band = "high"
        elif aff >= settings["kiss_threshold"]:
            band = "mid"
        else:
            band = "low"
        lines = HIKARI_NOTIFY_LINES[band]
        i = store.hikari_notify_i
        store.hikari_notify_i = i + 1
        name = gname("companion")
        return "%s: %s" % (name, lines[i % len(lines)])

    def ks_companion_active():
        return "companion" in (store.active or [])


## Shown during girl_chat with the companion slot: subtle engagement tell
## (always, once the meter has crossed) plus a debug meter when debug is on.
screen hikari_chat_chrome():
    zorder 90
    if ks_engagement_on():
        frame:
            xalign 0.98
            yalign 0.03
            background Solid("#1a2438cc")
            padding (12, 5)
            text "✨ [dn_companion]+ engagement boost active" size 16 color "#d4ecff"
    if ks_debug():
        $ _aff = ks_affection("companion")
        $ _s = ks_aff_settings()
        $ _boost = "on" if ks_engagement_on() else "off"
        $ _kt = _s["kiss_threshold"]
        $ _et = _s["engagement_threshold"]
        frame:
            xalign 0.02
            yalign 0.03
            background Solid("#00000088")
            padding (10, 4)
            text "[[debug] affection [_aff]/100  kiss@[_kt]  boost@[_et] [_boost]" size 16 color "#a8b8c8"


## Empty tag screen: shown over her last refusal line so a play-through
## can screenshot it. No extra chrome.
screen hikari_moment():
    zorder 80


## Fade-to-black veil for an accepted kiss. Non-explicit; a kiss is as far
## as the scene ever goes. Text lives on the veil so a screenshot of the
## screen always shows the beat (and we don't fight the say-window zorder).
screen hikari_kiss_veil():
    zorder 200
    add Solid("#000000")
    vbox:
        xalign 0.5
        yalign 0.5
        spacing 24
        text "The screen goes dark for a moment." size 30 color "#f2f2f2" text_align 0.5 xalign 0.5
        text "A kiss. Soft, brief, and that's as far as it goes." size 30 color "#f2f2f2" text_align 0.5 xalign 0.5


label hikari_kiss_accepted:
    $ ks_mem("companion").log_event("kiss", accepted=True, day=day_name,
        affection=ks_affection("companion"))
    $ ks_mood("companion", "happy")
    show screen hikari_kiss_veil
    $ renpy.pause()
    hide screen hikari_kiss_veil
    with fade
    return


## Mid-scene phone interruption. No-op unless the companion slot is active
## (including a double date). Scripted; no LLM call.
label hikari_phone_notify(when=""):
    if not ks_companion_active():
        return
    $ hikari_toast_text = ks_notify_line(when)
    $ ks_mem("companion").log_event("phone_notify", when=when, day=day_name,
        text=hikari_toast_text, affection=ks_affection("companion"),
        engagement=ks_engagement_on())
    show screen hikari_toast
    $ renpy.pause()
    hide screen hikari_toast
    return


## Top-right toast with a crop of her face. Click (or test advance) dismisses.
screen hikari_toast():
    zorder 200
    frame:
        xalign 0.98
        yalign 0.05
        xmaximum 420
        background Solid("#121826ee")
        padding (12, 10)
        hbox:
            spacing 12
            add "hikari_icon"
            vbox:
                spacing 2
                text "Tsunagari" size 14 color "#8eb4d4"
                text "[hikari_toast_text]" size 20 color "#f2f6ff"
