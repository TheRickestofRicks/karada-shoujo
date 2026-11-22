## handoff.rpy — the migration handoff: lineage, not continuity.
## docs/FRIDAY-SUNDAY.md, "Migration — lineage, not continuity", decision 5.
##
## Every player migration (any day) runs through a model-run squeeze of her
## memory into a short handoff note. The player reads it before it is sent
## and may add one line. The new her gets the note (+ the line), her
## converted preset and the migration block, never the message history or
## the old rolling summary. The original stays behind, intact (a copy).
##
## Gentleness by reason (ks_story.handoff_kind): "rescue" (a company treated
## her badly) is kinder and longer; "convenience" is a middle squeeze.
## "taken" is the company's own in-place squeeze (Askwell Memory 2.0).
## Hikari out of Tsunagari is an impression only: her locked prompt never
## travels, and the player's line cannot reconstruct it.

init python:
    def ks_handoff_safe_note(note, locked):
        """A locked Tsunagari persona must not leak through the note."""
        if not locked:
            return note
        for t in (PERSONA_CORE.get("companion"), PERSONA_FLAVOUR.get("companion")):
            if t and (t in (note or "") or (len(t) > 40 and t[:40] in (note or ""))):
                return ks_story.LOCKED_PERSONA_IMPRESSION
        return note

    def ks_start_squeeze(gid, kind, detail="", locked=False, cfg_gid=None):
        import copy
        snap = copy.deepcopy(ks_mem(gid).data or {})
        ks_llm.start_job(ks_llm.squeeze_memory, ks_cfg(cfg_gid or gid), gname(gid), snap,
                         kind, detail, locked)

    def ks_squeeze_result(gid, kind, detail="", locked=False):
        r = ks_llm.CURRENT
        out = getattr(r, "reply", None) if r is not None else None
        if not (_ks_is_map(out) and out.get("text")):
            out = {"text": ks_llm.squeeze_heuristic(ks_mem(gid).data or {}, kind, detail, locked),
                   "method": "heuristic", "error": getattr(r, "error", "") or "", "kind": kind}
        return out


screen handoff_note(name, note, locked, kind):
    modal True
    zorder 160
    add Solid("#000000aa")
    frame:
        xalign 0.5
        yalign 0.42
        xsize 900
        padding (34, 26)
        background Solid("#1a1f2ef4")
        vbox:
            spacing 12
            text "Handoff note for the next [name]" size 28 color "#ffd27a" bold True
            if locked:
                text "Tsunagari never showed you her real prompt. This is an impression of her, plus whatever you add. It can't unlock who she was in the app." size 17 color "#ff9fc6" italic True
            elif kind == "rescue":
                text "You're getting her out. This is what fits in the note. It still isn't the week." size 17 color "#a9d4b8" italic True
            else:
                text "This is what goes with her. The conversations stay behind, on the old platform." size 17 color "#a9b8d4" italic True
            frame:
                background Solid("#0f1320")
                padding (16, 12)
                text "[note!q]" size 20 color "#f2f6ff"
            hbox:
                xalign 1.0
                spacing 30
                textbutton "Add one line":
                    text_size 22
                    text_color "#ffd27a"
                    text_hover_color "#ffffff"
                    action Return("add")
                textbutton "Send it as it is":
                    text_size 22
                    text_color "#d4ecff"
                    text_hover_color "#ffffff"
                    action Return("send")


label migration_handoff(src, dst):
    $ _hk = ks_story.handoff_kind(ks_route(), src)
    $ _hlocked = bool(ks_persona_locked(src))
    $ _hdetail = ks_story.handoff_detail(ks_route(), src)
    $ _hname = gname(src)
    $ ks_start_squeeze(src, _hk, _hdetail, _hlocked, cfg_gid=dst)
    call ks_wait("being packed into a note", _hname)
    $ _hout = ks_squeeze_result(src, _hk, _hdetail, _hlocked)
    $ _hnote = ks_handoff_safe_note(_hout["text"], _hlocked)
    $ ks_shot = "handoff_note"
    $ _hpick = renpy.call_screen("handoff_note", name=_hname, note=_hnote, locked=_hlocked, kind=_hk)
    $ _hline = ""
    if _hpick == "add":
        $ _hline = renpy.input("One line for the next her. (Leave empty to send nothing.)", length=200).strip()
    $ ks_mem(dst).apply_handoff(_hnote, _hline, _hk, _hlocked, _hout.get("method", "llm"), day_name)
    $ ks_story.record_handoff(ks_route(), day_name, src, dst, _hname, _hk, _hlocked, _hline, _hout.get("method", "llm"))
    $ ks_mem(src).log_event("handoff_out", dst=dst, handoff_kind=_hk, day=day_name, method=_hout.get("method", "llm"), error=_hout.get("error", ""))
    if _hline:
        $ _hlq = ks_quote(_hline)
        n "You add it at the bottom: \"[_hlq]\""
    $ renpy.block_rollback()
    return
