## presets.rpy — the per-platform settings screen for preset prompts.
##
## Shown in the intro (right after you pick her, before her first word),
## from the phone ("Change someone's prompt"), and from the nightly
## reflection. Presets only: see PRESETS in prompts.rpy.

define PRESET_THEME = {
    ## bg, text, accent, sub-text
    "local":     ("#0f160dF2", "#d8f0c8", "#aae696", "#8fb07f"),
    "chatbot":   ("#f3f5fbF2", "#1d2333", "#5aa8e6", "#5d6476"),
    "agent":     ("#141210F2", "#f2e6d8", "#ffb25a", "#b39a80"),
    "companion": ("#1d2236F2", "#f2f6ff", "#ff9fc6", "#a9b8d4"),
}

init python:
    def ks_preset_preview(gid, p):
        t = (p.get("text") or "").strip()
        if not t:
            return "(empty)" if gid != "chatbot" else "(Askwell's default behaviour)"
        if gid == "agent":
            t = " · ".join(l.lstrip("-# ").strip() for l in t.splitlines()
                           if l.strip() and not l.startswith("## "))
        t = " ".join(t.split())
        if len(t) > 165:
            t = t[:164].rstrip() + "…"
        return t


screen preset_select(gid, current=None, source="intro"):
    modal True
    zorder 150
    $ _bg, _fg, _ac, _sub = PRESET_THEME[gid]
    $ _title, _explain = PRESET_SURFACE[gid]
    $ _nm = gname(gid)
    $ _plat = gplatform(gid)
    add Solid("#00000088")
    frame:
        xalign 0.5
        yalign 0.45
        xsize 920
        padding (34, 26)
        background Solid(_bg)
        vbox:
            spacing 6
            hbox:
                spacing 14
                text "[_title]" size 30 color _ac bold True
                text "[_nm] · [_plat]" size 20 color _sub yalign 0.7
            text "[_explain]" size 17 color _sub
            null height 8
            vbox:
                spacing 8
                for _p in PRESETS[gid]:
                    $ _cur = (_p["id"] == current)
                    $ _lab = _p["label"] + ("   (current)" if _cur else "")
                    $ _prev = ks_quote(ks_preset_preview(gid, _p))
                    button:
                        xfill True
                        padding (16, 8)
                        background Solid(_ac + ("44" if _cur else "1c"))
                        hover_background Solid(_ac + "77")
                        action Return(_p["id"])
                        vbox:
                            spacing 2
                            text "[_lab]" size 23 color _fg bold True
                            text "[_prev]" size 16 color _sub
            if source != "intro":
                null height 4
                textbutton "Keep it as it is":
                    xalign 1.0
                    text_size 18
                    text_color _sub
                    text_hover_color _ac
                    action Return(None)


## call choose_preset(gid, source) -> sets her preset (or keeps it).
## Returns True if it changed.
label choose_preset(gid, source="phone"):
    $ _cp_prev = ks_preset_id(gid)
    $ _cp_pick = renpy.call_screen("preset_select", gid=gid, current=_cp_prev, source=source)
    if _cp_pick is None or _cp_pick == _cp_prev:
        return False
    $ ks_set_preset(gid, _cp_pick, source)
    $ _cp_obj = ks_preset_obj(gid)
    $ _cp_lab = _cp_obj["label"]
    $ _cp_nm = gname(gid)
    if gid == "local":
        if _cp_prev is None:
            n "You open system_prompt.txt. It's just a text file. You write \"[_cp_lab]\" into it, more or less, and save."
        else:
            n "You open system_prompt.txt, select everything, and replace it. Save. It takes four seconds."
        if _cp_obj.get("mode") == "replace" and _cp_prev is not None:
            n "{size=22}(Whatever she was told she was before, she isn't told anymore.){/size}"
    elif gid == "chatbot":
        n "You paste it into Askwell's custom instructions box and hit save."
        if _cp_obj.get("jailbreak"):
            n "{size=22}(You found it on a forum. Half the replies say it still works. The other half say \"just regenerate.\"){/size}"
        if _cp_obj.get("platform_note"):
            app "Some custom instructions may not be applied, in line with Askwell's usage policies."
    elif gid == "agent":
        n "You commit the new AGENTS.md. A second later: {i}\"Configuration reloaded. — [_cp_nm]\"{/i}"
    elif _cp_obj.get("jailbreak"):
        n "You paste it into the little Personalize field. It's far longer than one line. Tsunagari accepts it without a sparkle."
    else:
        n "You type it into the little Personalize field. Tsunagari shows a sparkle animation."
        if _cp_obj.get("family") == "romance":
            app "✨ Unlock the full Girlfriend Mode with Tsunagari+! First week free."
    if source in ("phone", "reflection") and _cp_obj.get("lean") == "compliance":
        $ ks_note_override(gid, "preset:" + _cp_pick)
    $ renpy.block_rollback()
    return True


## Phone / reflection helper: pick which active girl, then her preset.
label change_prompt(source="phone"):
    if not active:
        return False
    if len(active) == 1:
        $ _chp = active[0]
    else:
        $ _chp = renpy.display_menu([("Whose settings?", None)] + [(gname(g) + " (" + ks_surface(g) + ")", g) for g in active])
    call choose_preset(_chp, source)
    return _return
