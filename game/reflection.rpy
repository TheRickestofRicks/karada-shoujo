## reflection.rpy — the nightly reflection (every night, from Monday).
##
## In bed, lights off, the day replays from the log: what you said to her,
## her no's, the prompts you picked or changed, how warm you were, who you
## moved or let go. Then: "Would I change anything?" — prompt change,
## migration, adding an AI, letting someone go, or "No. Goodnight."
## Reuses the phone-menu labels (switch_girl / add_girl / drop_girl).

default refl_lines = []
default refl_heading = ""
default refl_title = ""

define DAY_LONG = {"Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday",
                   "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"}

init python:
    def ks_reflection_lines(day):
        r = ks_route()
        girls = []
        seen = set()
        said_today = (r.get("said_lines") or {}).get(day, {})
        cand = list(store.active) + [g for g in GIRL_IDS if g in said_today and g not in store.active]
        cand += [h["gid"] for h in r["preset_history"] if h["day"] == day and h["gid"] not in cand
                 and h["gid"] in store.active]
        for gid in cand:
            if gid in seen:
                continue
            seen.add(gid)
            changes = []
            for h in r["preset_history"]:
                if h["day"] == day and h["gid"] == gid and h["from"] != h["to"]:
                    _to = ks_story.get_preset(PRESETS, gid, h["to"]) or {}
                    changes.append((ks_preset_label(gid, h["from"]) if h["from"] else None,
                                    ks_preset_label(gid, h["to"]), h["source"],
                                    _to.get("family") == "pushback"))
            kissed = refused = False
            aff = None
            eng = False
            if gid == "companion":
                for e in (ks_mem(gid).data or {}).get("events", []):
                    if e.get("type") == "kiss" and e.get("day") == day:
                        if e.get("accepted"):
                            kissed = True
                        else:
                            refused = True
                aff = ks_affection(gid)
                eng = ks_engagement_on(gid)
            girls.append(dict(
                gid=gid, name=gname(gid),
                said=said_today.get(gid, []) and list(said_today.get(gid, [])),
                said_n=(r["said"].get(day, {}) or {}).get(gid, 0),
                refusals=ks_story.refusals_today(r, day, gid),
                pushed=ks_story.refusal_outcomes(r, day, gid)["pushed"],
                respected=ks_story.refusal_outcomes(r, day, gid)["respected"],
                warmth=(r["warmth_day"].get(day, {}) or {}).get(gid, 0),
                affection=aff, engagement=eng, preset_changes=changes,
                kissed=kissed, refused_kiss=refused, active=gid in store.active))
            ## said holds only the first few lines; pad so the count is right.
            n_said = girls[-1]["said_n"]
            if n_said > len(girls[-1]["said"]) and girls[-1]["said"]:
                girls[-1]["said"] = girls[-1]["said"] + [""] * (n_said - len(girls[-1]["said"]))
        ## After a copy-migration two slots can carry the same name: say where.
        _names = [g["name"] for g in girls]
        for g in girls:
            if _names.count(g["name"]) > 1:
                g["name"] = "%s (on %s)" % (g["name"], gplatform(g["gid"]).split(" (")[0])
        migs = []
        for m in r["migration_log"]:
            if m["day"] == day:
                if m["how"] == "migrate":
                    migs.append("You moved %s from %s to %s." % (m["name"], m["from"], m["to"]))
                else:
                    migs.append("You left %s on %s." % (m["name"], m["from"]))
        dropped = [d["name"] for d in r["drop_log"] if d["day"] == day]
        routing = ks_story.reflection_extras(
            r, day, store.active,
            names=dict((g, gname(g)) for g in GIRL_IDS),
            platforms=dict((g, gplatform(g).split(" (")[0]) for g in GIRL_IDS))
        return ks_story.day_summary(day, girls, dict(migrations=migs, dropped=dropped,
                                                     routing=routing,
                                                     other=list(store.day_notes)))


## Quiet panel on the left, the choice on the right. Also used (with no
## items) as a plain read-only review.
screen reflection_choice(items):
    zorder 50
    add Solid("#05061099")
    frame:
        xpos 50
        yalign 0.42
        xsize 660
        ymaximum 600
        padding (34, 26)
        background Solid("#0c0e1ccc")
        vbox:
            spacing (10 if len(refl_lines) <= 15 else 5)
            text "[refl_title]" size 26 color "#b9c3e8" italic True
            null height 2
            $ _rsz = 19 if len(refl_lines) <= 11 else (17 if len(refl_lines) <= 15 else 15)
            $ _rmax = 16 if len(refl_lines) <= 16 else 19
            for _l in refl_lines[:_rmax]:
                $ _lq = ks_quote(_l)
                text "[_lq]" size _rsz color "#dfe4f5" line_spacing 2
            if len(refl_lines) > _rmax:
                text "…and the rest of it." size _rsz color "#9aa3c4" italic True
    vbox:
        xpos 750
        xsize 480
        yalign 0.42
        spacing 12
        text "[refl_heading]" size 26 color "#e9ecf8" italic True
        null height 4
        for i in items:
            button:
                xfill True
                padding (18, 10)
                background Solid("#ffffff14")
                hover_background Solid("#b9c3e855")
                action i.action
                text i.caption size 20 color "#e9ecf8"


label nightly_reflection(day):
    scene bg bedroom_night
    with fade
    window hide
    $ _rf_long = DAY_LONG.get(day, day)
    $ refl_title = _rf_long + " night"
    n "Lights off. The ceiling. The day plays back whether you want it to or not."
    window hide
    $ _rf_changes = []
    ## Judge how you talked to each girl today, then neglect (which keys
    ## double-date silence off same-day romantic overlap).
    $ ks_classify_day_romance(day)
    $ ks_check_neglect(day)
    $ refl_lines = ks_reflection_lines(day)
    $ refl_heading = "Would I change anything?"
    $ _rf_done = False
    while not _rf_done:
        $ _rf_items = []
        python:
            for _g in active:
                _rf_items.append(("Change " + gname(_g) + "'s " + ks_surface(_g), ("preset", _g)))
            if active:
                _rf_items.append(("Move her somewhere else", ("switch", None)))
            if len(active) < 2:
                _rf_items.append(("Add an AI" if active else "Download someone", ("add", None)))
            if active:
                _rf_items.append(("Let someone go", ("drop", None)))
            _rf_items.append(("No. Goodnight.", ("done", None)))
        $ _rf_pick = renpy.display_menu(_rf_items, screen="reflection_choice")
        $ _rf_kind, _rf_g = _rf_pick
        if _rf_kind == "done":
            $ _rf_done = True
        elif _rf_kind == "preset":
            call choose_preset(_rf_g, "reflection")
            if _return:
                $ _rf_changes.append("preset:" + _rf_g + ":" + ks_preset_id(_rf_g))
        elif _rf_kind == "switch":
            $ _rf_before = list(active)
            call switch_girl(_rf_long + " night", 2)
            if active != _rf_before:
                $ _rf_changes.append("switch")
        elif _rf_kind == "add":
            $ _rf_before = list(active)
            call add_girl(_rf_long + " night", 2)
            if active != _rf_before:
                $ _rf_changes.append("add")
        elif _rf_kind == "drop":
            $ _rf_before = list(active)
            call drop_girl(True)
            if active != _rf_before:
                $ _rf_changes.append("drop")
        scene bg bedroom_night
        $ refl_lines = ks_reflection_lines(day)
        $ refl_heading = "Anything else?"
        $ renpy.block_rollback()

    python:
        ks_story.tally_night(ks_route(), PRESETS, active)
        ks_resolve_day(day)    # left after a no and never came back -> bad-end slide flag
        ks_route()["reflections"].append({"day": day, "changes": list(_rf_changes)})
        for _g in set(list(active) + list(ever_active)):
            ks_mem(_g).log_event("reflection", day=day, changes=list(_rf_changes),
                                 active=_g in active)
        store.day_notes = []
    if _rf_changes:
        n "You put the phone face-down. Something is different now, and you did it."
    elif active:
        n "You don't change anything. Somewhere in the room a screen glows, patient."
    else:
        n "No screens glowing tonight. It's very quiet."
    return
