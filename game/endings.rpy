## endings.rpy — the end of the week (docs/FRIDAY-SUNDAY.md, "Ending
## reflection"; decisions 8 and 12).
##
## Route identity stays with the flags and the scores: hard flags first
## (ks_story.hard_gates: a Yes-Machine lock, or nobody left = Fail), then
## ending_leans / ENDING_PRIORITY. Only a good route (Both, Human, Respect,
## and a Migration that was more rescue than erasure) asks the model for a
## flavour and a written slide; a bad end keeps its written text, so a kind
## model can't paper over it. No keyword fallback: if the model is down or
## unreadable, the route's written slide stands alone, with no flavour.
##
## Slides: (1) the route slide; (2) one plain record per instance, active or
## left behind, most to least attended (model-written; plain facts if it
## fails); (3) Mio's slide if she isn't the route; then any earned bad-end
## slides (leaving without goodbye, deleted).

default ks_end = None

init python:
    def ks_ending_girls():
        """[(gid, name, platform, is_active)] for every instance the player made."""
        out = []
        for g in GIRL_IDS:
            m = ks_mem(g)
            if m.data is None:
                continue
            if g in store.active or g in store.ever_active:
                out.append((g, gname(g), gplatform(g).split(" (")[0], g in store.active))
        return out

    def ks_final_ending():
        return ks_story.final_ending(ks_route(), store.active, store.mio_real,
                                     any(store.mirror_flags.values()), store.migrations,
                                     store.friend_told)

    def ks_ending_focus(eid):
        """The girl the route slide is about."""
        r = ks_route()
        names = dict((g, gname(g)) for g in GIRL_IDS)
        if eid == "migration":
            for h in reversed(r.get("handoffs") or []):
                if h.get("dst") in store.active:
                    return gname(h["dst"])
        return ks_story.both_ai_name(r, store.active or store.ever_active, names, "her")

    def ks_ending_result():
        r = ks_llm.CURRENT
        out = getattr(r, "reply", None) if r is not None else None
        return out if _ks_is_map(out) else {"slide": None, "records": {}}


screen ending_title(title, sub=""):
    zorder 50
    frame:
        xalign 0.5
        yalign 0.12
        background None
        vbox:
            xalign 0.5
            text "[title]" size 44 color "#ffd27a" xalign 0.5
            if sub:
                text "[sub]" size 20 color "#c8c0e0" italic True xalign 0.5


label week_ending:
    $ ks_shot = "ending_wait"
    $ renpy.block_rollback()
    python:
        _end = ks_final_ending()
        _names = dict((g, gname(g)) for g in GIRL_IDS)
        _girls = ks_ending_girls()
        _order = ks_story.instance_order(ks_route(), [g[0] for g in _girls])
        _gmap = dict((g[0], g) for g in _girls)
        _digest = ks_story.ending_digest(ks_route(), _end, [_gmap[g] for g in _order],
                                         store.mio_real, store.friend_told, _names)
        _inst = [(g, _gmap[g][1], ks_story.instance_facts(ks_route(), g, _gmap[g][1], _gmap[g][2], _gmap[g][3]))
                 for g in _order]
        ks_llm.start_job(ks_llm.write_week_ending, ks_cfg(), bool(_end["good"]), _digest, _inst)
    scene bg card
    with fade
    call ks_wait("writing the end of the week", "The week")
    python:
        _out = ks_ending_result()
        _sl = _out.get("slide") or {}
        _flavour = ks_story.accept_flavour(_end, _sl.get("flavour"))
        _slide = _sl.get("slide") if _flavour else None
        _records = {}
        for _g, _nm, _facts in _inst:
            _rec = (_out.get("records") or {}).get(_g) or {}
            _records[_g] = _rec.get("text") or ks_story.instance_record_canned(_facts)
        _focus = ks_ending_focus(_end["id"])
        _body = ks_story.route_slide_canned(_end["id"], ks_route(), _focus, store.friend_told, _names)
        ks_end = ks_story.ending_record(ks_route(), _end, _flavour, _slide, _records,
                                        "llm" if _slide else "written")
        for _g in GIRL_IDS:
            _m = ks_mem(_g)
            if _m.data is not None:
                _m.set_flag("ending", _end["id"])
                _m.set_flag("ending_flavour", _flavour)
                _m.log_event("week_ending", ending=_end["id"], flavour=_flavour,
                             record=_records.get(_g), active=_g in store.active)
        _card = ks_story.festival_card_line(ks_route(), _names)

    ## 1. The route slide.
    $ ks_shot = "ending_title"
    $ _etitle = _end["title"]
    show text "{size=34}Sunday, 10 July{/size}\n\n{size=86}[_etitle]{/size}" at truecenter
    with dissolve
    pause 2.0
    hide text
    with dissolve
    $ ks_shot = "ending_route"
    $ _sub = ks_story.FLAVOUR_LABELS.get(_flavour, "") if _flavour else ""
    show screen ending_title(_end["title"], _sub)
    python:
        for _l in _body:
            renpy.say(n, _l)
        if _slide:
            renpy.say(n, ks_quote(_slide))
        if _card and _end["id"] != "both":
            renpy.say(n, "{i}" + _card + "{/i}")
        for _note in ks_story.ending_notes(ks_route()):
            renpy.say(n, "{i}" + _note + "{/i}")

    ## 2. One record per instance, most to least attended.
    $ ks_shot = "ending_instances"
    hide screen ending_title
    show screen ending_title("Who was there", "")
    python:
        for _g in _order:
            renpy.say(n, "{b}" + ks_quote(_gmap[_g][1]) + "{/b} · " + ks_quote(_gmap[_g][2]) + "\n" + ks_quote(_records[_g]))
        if not _order:
            renpy.say(n, "Nobody. You never opened a window this week.")

    ## 3. Mio, if she isn't the route; then the bad-end slides.
    if _end["id"] not in ("human", "both"):
        $ _ms = ks_story.mio_slide(ks_route(), store.mio_real, _card)
        hide screen ending_title
        show screen ending_title(_ms["title"], "")
        python:
            for _l in _ms["lines"]:
                renpy.say(n, _l)
    python:
        _bads = list(ks_story.bad_end_slides(ks_route()))
        _ds = ks_story.deleted_slide(ks_route())
        if _ds:
            _bads.append(_ds)
    if _bads:
        $ ks_shot = "ending_bad"
        python:
            for _bs in _bads:
                renpy.hide_screen("ending_title")
                renpy.show_screen("ending_title", _bs["title"], "")
                for _l in _bs["lines"]:
                    renpy.say(n, ks_quote(_l))
    hide screen ending_title

    ## The end.
    $ ks_shot = "the_end"
    scene bg card
    with fade
    show text "{size=90}おわり{/size}\n{size=40}The end of the week{/size}\n\n{size=24}Thanks for playing Karada Shoujo.{/size}" at truecenter
    with dissolve
    pause
    hide text
    if ks_debug():
        $ _lq = ks_quote(repr(_end["leans"]))
        $ _rq = ks_quote("ending=%s lock=%s good=%s flavour=%s reasons=%s" % (_end["id"], _end["lock"], _end["good"], _flavour, "; ".join(_end["lock_reasons"]) or "none"))
        n "{color=#888}[[debug] [_rq]{/color}"
        n "{color=#888}[[debug] leans: [_lq]{/color}"
    return
