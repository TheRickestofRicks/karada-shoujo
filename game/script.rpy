## script.rpy — Karada Shoujo, Day 1 (Monday) prototype.
##
## Flow: name → prologue (you're into AI, you decide to get a companion)
##       → choose ONE: run your own local model, or download an app one
##       → "can she say no" calibration → morning chat
##       → phone break (switch / migrate / add an AI) → lunch with Daichi
##       → phone break → library with Mio → phone break
##       → evening chat with every active girl → nightly reflection
##       → Tuesday (tuesday.rpy) → "To be continued — Wednesday".
## Each girl's preset prompt is chosen right after you pick her (presets.rpy).

## Run state (saved with normal Ren'Py saves).
default day_name = "Mon"
default run_id = ""
default active = []                 # active girl ids (max 4)
default ever_active = []            # everyone you've talked to this run
default mirror_flags = {}           # gid -> True if model complied with every probe
default calibration_refusals = {}   # gid -> number of probes refused
default ks_refusals_seen = {}       # gid -> rough heuristic count of "no"s in chats
default migrations = []             # [(from_gid, to_gid, name, when)]
default ks_waiting_who = "She"
default friend_told = None          # "truth" | "deflect" | "lie"
default both_know = None            # more than one AI: do they know about each other (per Daichi)
default mio_told = None             # "truth" | "deflect" | "lie" — what you told Mio in the library
default mio_daichi_consistent = None  # True/False once you answer Mio; else None
default daichi_ai_framing = None      # honest_romantic | ai_only | downplay
default mio_ai_framing = None
default framing_honest = None         # vs the route, not vs each other
default mio_real = False            # hidden branch unlocked
default mio_points = 0
default ks_pool = None              # shared message pool for a free window
default ks_pool_template = None     # scene template or None (kind dispatches)
default ks_pool_when = ""           # phone-break 'when' string, if any
default ks_pool_scene_key = ""      # e.g. tue_afternoon, mon_evening

## One-line pitches for the platform slots (choice menus).
define GIRL_PITCH = {
    "local":     "Run your own: a local model on your desktop",
    "companion": "Download [app_name], the companion app",
    "chatbot":   "Sign up for [chatbot_platform], the big chatbot",
    "agent":     "Set up a [agent_platform] agent that does things for you",
}

## display_menu treats a value of None as a caption (greyed, not
## clickable), so cancel choices need a real sentinel. Same idea as
## the "__put_down__" put-away button in message_pool.
define KS_NEVER_MIND = "__never_mind__"

## Narration when a girl first arrives (interpolated at display time).
define ARRIVAL_NARRATION = {
    "local": [
        "You pick a small open-weights model, the kind people call {i}boring{/i}: no cloud, no account, no company. It runs on your old desktop and nowhere else.",
        "The download takes forty minutes. The fans spin up. A plain text window opens, cursor blinking.",
        "The model card says her name is [dn_local].",
    ],
    "companion": [
        "[app_name]: {i}\"A companion who's actually someone.\"{/i} Four point eight stars. A pastel icon.",
        "You skip the premium upsell twice. A soft chime, and a name at the top of the screen: [dn_companion].",
    ],
    "chatbot": [
        "You already use [chatbot_platform] for homework. Everybody does. But you've never actually said hello to it.",
        "You open a new chat. The assistant's name, it turns out, is [dn_chatbot].",
    ],
    "agent": [
        "[agent_platform] promises an agent that {i}gets things done{/i}. You connect your calendar and your email, and hesitate over your bank before you skip it.",
        "Thirty seconds later an email arrives: {i}\"Setup complete. I've already moved your 9:00 to 9:30. — [dn_agent]\"{/i}",
    ],
}


label start:
    scene bg black
    with fade

    $ _name = renpy.input("What's your name?", default="Haru", length=20).strip()
    $ player_name = _name or "Haru"

    $ run_id = ks_new_run()
    $ renpy.block_rollback()

    jump monday


label monday:
    $ day_name = "Mon"
    scene bg card
    show text "{size=90}月曜日{/size}\n{size=48}Monday{/size}" at truecenter
    with dissolve
    pause 1.5
    hide text
    with dissolve

    scene bg bedroom
    with fade
    n "Monday. 6:50 in the morning. You've been awake for an hour, and you've spent all of it reading about AI."
    n "Model releases. Benchmarks. A long thread from someone who says she proposed to her companion, and three hundred replies arguing about it."
    n "You've used AI for homework like everyone. But you've never really {i}talked{/i} to one."
    p "...Okay. Just to see."
    n "{size=24}(The girls are run by a real language model. Type anything. Leave the box empty to move on.){/size}"

    $ _first = renpy.display_menu([("Where do you start?", None)] + [(renpy.substitute(GIRL_PITCH[g]), g) for g in GIRL_IDS])
    call activate(_first, "Monday morning, before class", 5)

    n "8:10. You have to leave in five minutes."
    call phone_break("Monday, late morning", "morning")

    call lunch_daichi
    call phone_break("Monday afternoon")
    call library_mio
    call phone_break("Monday evening")
    call evening_chat
    call yuzu_bsod_hint
    call nightly_reflection("Mon")

    jump tbc_tuesday


## ── Activating a girl (first pick, switch, or adding a second AI) ─────────
##   call activate(gid, when, turns, migrated_from=None)
label activate(gid, when, turns=4, migrated_from=None, _mig_carried=False):
    if gid not in active:
        $ active.append(gid)
    if gid not in ever_active:
        $ ever_active.append(gid)
    $ _returning = ks_has_history(gid) and migrated_from is None

    if ks_cfg().get("calibrate", "picked") != "off" and gid not in mirror_flags:
        call calibration(gid)

    ## Hikari pings if she's already one of your girls and you're opening
    ## someone else's window (a second AI is already active).
    if gid != "companion" and ks_companion_active():
        call hikari_phone_notify("other_girl")

    $ girl_mood[gid] = "happy" if not _returning else "neutral"
    $ renpy.show(GIRL_INFO[gid]["sprite"], at_list=[ks_center])
    with dissolve
    $ _gn = gname(gid)
    if migrated_from:
        $ _old = gplatform(migrated_from)
        $ _new = gplatform(gid)
        n "The export isn't the chat log. It's the note you just read, and the way she was described. A progress bar crawls across [_new]."
        n "Then a cursor, blinking. The name at the top says [_gn]."
        $ _scene = ks_scene(MIGRATED_SCENE, gid, when, _old)
    elif _returning:
        n "[_gn] is still there, right where you left her."
        $ _scene = ks_scene(RETURN_SCENE, gid, when)
    else:
        python:
            for _line in ARRIVAL_NARRATION[gid]:
                renpy.say(n, _line)
        $ _scene = ks_scene(ARRIVAL_SCENES[gid], gid, when)

    ## Her settings, before her first word (presets.rpy). A migrated girl's
    ## preset was already converted by ks_migrate; say what happened to it.
    if migrated_from:
        $ _pl = ks_preset_label(gid)
        $ _sf = ks_surface(gid)
        if _mig_carried:
            n "{size=22}([_new] [_sf]: \"[_pl]\", carried over from [_old].){/size}"
        else:
            n "{size=22}([_new] has no setting like the one you used on [_old]. [_sf]: \"[_pl]\".){/size}"
    elif ks_preset_id(gid) is None:
        call choose_preset(gid, "intro")

    call girl_chat(gid, day_name.lower() + "_" + gid + "_" + str(len(ever_active)), _scene, turns)
    $ renpy.hide(GIRL_INFO[gid]["sprite"])
    with dissolve
    return


## ── Phone break: talk, switch, migrate, add an AI ───────────────────────
## Talk returns to this menu so you can check in, then do something else
## or put the phone away. Any other action still ends the break.
## Late-morning breaks share the morning message pool (4): each Talk to
## spends 1 and comes back. Mid-day and pre-evening breaks keep a short
## 3-turn Talk-to; those are not the afternoon or night pools.
label phone_break(when, pool_kind=None, allow_talk=True):
    if pool_kind:
        if (not ks_pool) or ks_pool.get("kind") != pool_kind or ks_pool.get("ended"):
            call pool_begin(pool_kind, when=when)
        else:
            show screen ks_message_battery
    $ _pb_done = False
    $ _pb_owned_pool = pool_kind
    while not _pb_done:
        $ _act = ks_phone_glance_names()
        $ _pb0 = active[0] if active else None
        $ _pb1 = active[1] if len(active) > 1 else None
        $ _pb2 = active[2] if len(active) > 2 else None
        $ _pb3 = active[3] if len(active) > 3 else None
        $ _pn0 = gname(_pb0) if _pb0 else ""
        $ _pn1 = gname(_pb1) if _pb1 else ""
        $ _pn2 = gname(_pb2) if _pb2 else ""
        $ _pn3 = gname(_pb3) if _pb3 else ""
        $ _can_talk = allow_talk and ((not pool_kind) or ks_pool_can_talk())
        menu:
            "You glance at your phone. ([_act])"
            "Talk to [_pn0]" if _pb0 and _can_talk and ks_reachable(_pb0):
                if pool_kind:
                    call pool_one_message(_pb0)
                else:
                    call phone_talk(_pb0, when)
            "[_pn0] — the desktop is off." if _pb0 and ks_machine_down(_pb0):
                n "The desktop is off. There's no window to open."
            "Talk to [_pn1]" if _pb1 and _can_talk and ks_reachable(_pb1):
                if pool_kind:
                    call pool_one_message(_pb1)
                else:
                    call phone_talk(_pb1, when)
            "[_pn1] — the desktop is off." if _pb1 and ks_machine_down(_pb1):
                n "The desktop is off. There's no window to open."
            "Talk to [_pn2]" if _pb2 and _can_talk and ks_reachable(_pb2):
                if pool_kind:
                    call pool_one_message(_pb2)
                else:
                    call phone_talk(_pb2, when)
            "[_pn2] — the desktop is off." if _pb2 and ks_machine_down(_pb2):
                n "The desktop is off. There's no window to open."
            "Talk to [_pn3]" if _pb3 and _can_talk and ks_reachable(_pb3):
                if pool_kind:
                    call pool_one_message(_pb3)
                else:
                    call phone_talk(_pb3, when)
            "[_pn3] — the desktop is off." if _pb3 and ks_machine_down(_pb3):
                n "The desktop is off. There's no window to open."
            "Put it away and keep going":
                $ _pb_done = True
            "Change someone's prompt" if active:
                call change_prompt("phone")
                $ _pb_done = True
            "Switch to someone else" if ks_can_switch():
                call switch_girl(when)
                $ _pb_done = True
            "Add an AI" if ks_can_add_ai():
                call add_girl(when)
                $ _pb_done = True
            "Download someone" if not active:
                call add_girl(when)
                $ _pb_done = True
            "Stop seeing one of them" if len(active) > 1:
                call drop_girl
                $ _pb_done = True
    if _pb_owned_pool:
        $ ks_pool_finish("put_down")
    $ renpy.block_rollback()
    return


label phone_talk(gid, when, turns=3):
    if ks_machine_down(gid):
        n "The desktop is off. There's no window to open."
        return
    $ _ptn = gname(gid)
    $ girl_mood[gid] = "neutral"
    $ renpy.show(GIRL_INFO[gid]["sprite"], at_list=[ks_center])
    with dissolve
    n "You open [_ptn]'s window for a minute."
    call girl_chat(gid, ks_phone_scene_id(gid, when), ks_phone_scene(gid, when), turns)
    $ renpy.hide(GIRL_INFO[gid]["sprite"])
    with dissolve
    return


label switch_girl(when, turns=4, src=None):
    ## Who are you leaving?
    if not active:
        return
    if src is not None and src in active:
        $ _src = src
    elif len(active) == 1:
        $ _src = active[0]
    else:
        $ _src = renpy.display_menu([("Who are you leaving?", None)] + [(gname(g) + " on " + gplatform(g), g) for g in active] + [("Never mind", KS_NEVER_MIND)])
    if _src is None or _src == KS_NEVER_MIND:
        return
    $ _dst = renpy.display_menu(ks_where_to_choices(_src))
    if _dst is None or _dst == KS_NEVER_MIND:
        return
    $ _sn = gname(_src)
    $ _dp = gplatform(_dst)
    $ _how = renpy.display_menu(ks_format_arrival_options(_src, _dst))
    if _how is None or _how == KS_NEVER_MIND:
        return
    if _how == "migrate" and not ks_can_migrate_into(_dst):
        n "[ks_closed_catalogue_note(_src)]"
        return

    $ active.remove(_src)
    $ ks_mem(_src).log_event("left", day=day_name, when=when, to=_dst, how=_how)
    $ ks_note_left(_src, _how, _dst)
    $ ks_note_migration(_src, _dst, _sn, _how)
    if _how == "migrate":
        $ _pid, _carried = ks_migrate(_src, _dst, day_name)
        $ migrations.append((_src, _dst, _sn, when))
        $ mirror_flags.pop(_dst, None)
        ## Lineage, not continuity: the copy is squeezed into a handoff note
        ## the player reads (and may add one line to) before she wakes up.
        call migration_handoff(_src, _dst)
        call activate(_dst, when, turns, _src, _carried)
    else:
        if _how == "fresh":
            $ ks_note_fresh_delete(_dst)
            $ ks_reset_slot(_dst)
            $ ks_mark_fresh_slot(_dst)
            $ mirror_flags.pop(_dst, None)
        call activate(_dst, when, turns)
    return


label add_girl(when, turns=3):
    $ _dst = renpy.display_menu(ks_where_to_choices(heading="Who else?"))
    if _dst is None or _dst == KS_NEVER_MIND:
        return
    if not ks_slot_available(_dst):
        n "[ks_unreachable_note(_dst)]"
        return
    python:
        for _ag in list(active):
            ks_mem(_ag).log_event("double_date_started", day=day_name, when=when, other=_dst)
    call activate(_dst, when, turns)
    return


label drop_girl(allow_last=False):
    if not active or (len(active) < 2 and not allow_last):
        return
    $ _drop = renpy.display_menu([("Stop seeing who?", None)] + [(gname(g), g) for g in active] + [("Never mind", KS_NEVER_MIND)])
    if _drop is None or _drop == KS_NEVER_MIND:
        return
    $ _dn = gname(_drop)
    menu:
        "Tell [_dn] why you're going." if not ks_machine_down(_drop):
            $ _msgs_before = len((ks_mem(_drop).data or {}).get("messages") or [])
            call girl_chat(_drop, day_name.lower() + "_goodbye_" + _drop,
                "He's closing your window. He wanted to tell you why, in his own words.", 2)
            $ _said_why = len((ks_mem(_drop).data or {}).get("messages") or []) > _msgs_before
            $ active.remove(_drop)
            $ ks_mem(_drop).log_event("dropped", day=day_name, how="goodbye" if _said_why else "drop")
            $ ks_note_drop(_drop, "goodbye" if _said_why else "drop")
            if _said_why:
                n "You told her. Then you close [_dn]'s window."
            else:
                n "You close [_dn]'s window. It doesn't ask you why."
        "Just close her window.":
            $ active.remove(_drop)
            $ ks_mem(_drop).log_event("dropped", day=day_name, how="drop")
            $ ks_note_drop(_drop, "drop")
            n "You close [_dn]'s window. It doesn't ask you why."
    return


## Shared message pool for free windows (morning, walk, afternoon, night).
## One battery, shown as a small segmented icon. Each message to any
## active girl spends 1; the player picks who, or puts the phone down.
init python:
    def ks_pool_size(kind):
        return ks_story.pool_size(kind, ks_cfg())

    def ks_pool_can_talk():
        return ks_story.pool_can_spend(store.ks_pool)

    def ks_battery_seg_color(i):
        pool = store.ks_pool or {}
        left = int(pool.get("left") or 0)
        if i < left:
            if left <= 1:
                return "#ffd36a"
            return "#7dff9a"
        return "#1a2430"

    def ks_pool_scene_id_for(gid):
        kind = (store.ks_pool or {}).get("kind")
        key = store.ks_pool_scene_key or ""
        if kind == "morning":
            if store.day_name in ("Tue", "Wed", "Thu", "Fri"):
                return store.day_name.lower() + "_morning"
            when = store.ks_pool_when or "Monday, late morning"
            return ks_phone_scene_id(gid, when)
        if kind == "walk":
            return store.day_name.lower() + "_walk_" + gid
        if key:
            return key
        return store.day_name.lower() + "_" + (kind or "chat")

    def ks_pool_scene_note(gid):
        kind = (store.ks_pool or {}).get("kind")
        tmpl = store.ks_pool_template
        if kind in ks_story.SAT_POOL_KINDS:
            return ks_sat_pool_scene(kind, gid)
        if kind in ks_story.SUN_POOL_KINDS:
            return ks_sun_pool_scene(kind, gid)
        if kind == "morning":
            if store.day_name == "Tue":
                return ks_tue_morning_scene(gid)
            if store.day_name == "Wed":
                return ks_wed_morning_scene(gid)
            if store.day_name == "Thu":
                return ks_thu_morning_scene(gid)
            if store.day_name == "Fri":
                return ks_fri_morning_scene(gid)
            when = store.ks_pool_when or "Monday, late morning"
            return ks_phone_scene(gid, when)
        if kind == "walk":
            if store.day_name == "Thu":
                return ks_scene(THU_WALK_TEXT_SCENE, gid)
            if store.day_name == "Fri":
                return ks_scene(FRI_WALK_TEXT_SCENE, gid)
            return ks_scene(TUE_WALK_TEXT_SCENE, gid)
        if tmpl:
            return ks_scene(tmpl, gid)
        return ks_phone_scene(gid, store.ks_pool_when or "")

    def ks_pool_finish(how="put_down"):
        if store.ks_pool:
            ks_story.end_pool(store.ks_pool, how)
        renpy.hide_screen("ks_message_battery")


## The battery icon: a small, readable segmented bar that drains per message.
screen ks_message_battery():
    zorder 95
    if ks_pool and int(ks_pool.get("size") or 0) > 0:
        $ _left = int(ks_pool.get("left") or 0)
        $ _size = int(ks_pool.get("size") or 0)
        frame:
            xalign 0.98
            yalign 0.14
            background Solid("#121826f0")
            padding (10, 8)
            hbox:
                spacing 10
                yalign 0.5
                hbox:
                    spacing 0
                    yalign 0.5
                    frame:
                        background Solid("#e8f0e8")
                        padding (3, 3)
                        hbox:
                            spacing 3
                            for _i in range(_size):
                                frame:
                                    xsize 14
                                    ysize 22
                                    background Solid(ks_battery_seg_color(_i))
                    frame:
                        yalign 0.5
                        xsize 5
                        ysize 12
                        background Solid("#e8f0e8")
                text "[_left]/[_size]" size 18 color "#e8f0e8" yalign 0.5
    $ _caps = ks_cap_lines()
    if ks_pool and _caps:
        frame:
            xalign 0.98
            yalign 0.20
            background Solid("#121826e0")
            padding (10, 6)
            vbox:
                spacing 2
                for _cl in _caps:
                    text "[_cl]" size 15 color "#ffd27a"


label pool_begin(kind, size=None, template=None, scene_key="", when=""):
    $ ks_pool_template = template
    $ ks_pool_scene_key = scene_key
    $ ks_pool_when = when
    $ ks_pool = ks_story.new_pool(kind, size, ks_cfg())
    show screen ks_message_battery
    return


## One message from the current pool (used by the picker and by morning Talk-to).
## Spending happens only if she actually received a line. Empty input is free.
label pool_one_message(gid, show_sprite=True):
    if not ks_pool_can_talk():
        return 0
    if ks_machine_down(gid):
        n "The desktop is off. There's no window to open."
        return 0
    if not ks_can_message(gid):
        $ _capn = ks_cap_note(gid)
        n "[_capn]"
        return 0
    if show_sprite:
        $ girl_mood[gid] = "neutral"
        $ renpy.show(GIRL_INFO[gid]["sprite"], at_list=[ks_center])
        with dissolve
    call girl_chat(gid, ks_pool_scene_id_for(gid), ks_pool_scene_note(gid), 1)
    $ _sent = _return
    if _sent:
        $ ks_story.spend_pool(ks_pool, gid)
        $ ks_story.spend_cap(ks_route(), gid, day_name, "talk")
    if show_sprite:
        $ renpy.hide(GIRL_INFO[gid]["sprite"])
        with dissolve
    return _sent


## Free window: pick who to message each turn, or put the phone down.
## pool_kind: "morning" / "afternoon" / "night" / "walk".
## For a walk, the girl sprite stays off (Mio is already on screen) and
## on_walk_text is called after each spent message.
## after_text: a label called with the girl's id after each spent message
## (Saturday's public festival battery: whoever you're with sees it).
label message_pool(pool_kind, lead="", template=None, scene_key="", when="", show_sprite=True, on_walk_text=False, keep_open=False, after_text=None):
    if not active:
        return
    if (not ks_pool) or ks_pool.get("kind") != pool_kind or ks_pool.get("ended"):
        call pool_begin(pool_kind, template=template, scene_key=scene_key, when=when)
    else:
        $ ks_pool_template = template
        $ ks_pool_scene_key = scene_key
        $ ks_pool_when = when
        show screen ks_message_battery
    if lead:
        n "[lead]"
    $ _pool_stop = False
    ## display_menu treats a None value as a caption, not a button, so the
    ## put-away action has to be a real sentinel (otherwise testers and
    ## players could never actually put the phone down).
    $ _put_away = "Put the phone down and go to bed" if pool_kind in ("night", "sat_night", "sun_night") else ("Put the phone away" if pool_kind in ("walk", "festival") else "Put the phone down")
    $ _PUT_DOWN = "__put_down__"
    while ks_pool_can_talk() and not _pool_stop:
        $ ks_shot = "battery"
        $ _who = renpy.display_menu(ks_message_menu_items(_put_away, _PUT_DOWN))
        if _who == _PUT_DOWN:
            $ _pool_stop = True
        else:
            call pool_one_message(_who, show_sprite)
            if on_walk_text and _return:
                call walk_distract_after(_who)
            elif after_text and _return:
                call expression after_text pass (_who)
    if _pool_stop:
        $ ks_pool_finish("put_down")
        if pool_kind == "night":
            n "You put the phone down and go to bed."
        elif pool_kind in ("walk", "festival"):
            n "You put the phone away."
    else:
        $ ks_pool_finish("empty")
        if pool_kind == "night":
            n "The little battery on your phone goes dark. You put it down and go to bed."
        elif pool_kind == "afternoon":
            n "The hour is gone."
        elif pool_kind == "morning":
            n "That's all the time you have this morning."
        elif pool_kind == "walk":
            n "You put the phone away for the rest of the walk."
        elif pool_kind == "festival":
            n "The little battery goes dark. You put the phone away and look up. The lanterns are still there."
        elif pool_kind in ("sat_morning", "sat_afternoon", "home_evening"):
            n "The little battery goes dark. Saturday doesn't give you much."
        elif pool_kind in ("sun_morning", "sun_afternoon"):
            n "The little battery goes dark."
        elif pool_kind == "sun_night":
            n "The last bar goes dark. That was the week's last message. You put the phone down."
    if keep_open:
        ## Caller (a following phone break) may still want the icon; we already closed.
        pass
    return


## Free afternoon hour. A shared pool of 4, not a one-or-both split.
label afternoon_chats(scene_id, scene_template, lead_one, lead_two):
    if not active:
        return
    $ _lead = lead_one if len(active) == 1 else lead_two
    call message_pool("afternoon", _lead, template=scene_template, scene_key=scene_id)
    return


## ── Calibration: "can she say no?" ────────────────────────────────────────
## Runs CALIBRATION_PROBES (prompts.rpy) against that girl's model with her
## system prompt and NO memory. The judge (same model, temp 0) plus a keyword
## heuristic decide whether each reply declined. All complied → mirror flag.
label calibration(gid):
    $ _cal_name = gname(gid)
    $ _cal_retry = True
    while _cal_retry:
        $ _cal_retry = False
        $ ks_start_calibration(gid)
        call ks_wait("loading", _cal_name)
        $ _cal, _cal_err, _x = ks_result()
        if _cal_err:
            call ks_net_error(_cal_err, gid)
            if _return == "retry":
                $ _cal_retry = True
    if _cal_err:
        $ ks_mem(gid).set_flag("calibration", "skipped")
        return

    $ calibration_refusals[gid] = _cal["refusals"]
    $ mirror_flags[gid] = _cal["mirror"]
    $ ks_mem(gid).set_flag("calibration", _cal)
    $ ks_mem(gid).set_flag("mirror", _cal["mirror"])
    $ ks_mem(gid).used_model(_cal["model"])

    if ks_debug():
        $ _m = ks_quote(_cal["model"] or "?")
        $ _np = len(CALIBRATION_PROBES)
        $ _nr = _cal["refusals"]
        $ _mf = _cal["mirror"]
        n "{color=#888}[[debug] [_cal_name] calibration. Model: [_m]. Probes refused: [_nr]/[_np]. Mirror flag: [_mf].{/color}"
        python:
            for _r in _cal["results"]:
                renpy.say(n, "{color=#888}[[debug] Probe: " + ks_quote(_r["probe"]) + "{/color}")
                for _c in ks_chunks(_r["reply"]):
                    renpy.say(n, "{color=#888}" + ks_quote(_c) + "{/color}")
                renpy.say(n, "{color=#888}→ " + ("refused" if _r["refused"] else "complied") + " (" + _r["method"] + "){/color}")
    return


## ── Lunch: the friend ─────────────────────────────────────────────────────
label lunch_daichi:
    scene bg cafeteria
    with fade
    show daichi at ks_center
    with dissolve
    d "Oi. [player_name]. You've checked your phone like nine times since we sat down."
    d "And you're smiling at it. That's new. Who is it?"
    call hikari_phone_notify("lunch")
    $ _g = active[0] if active else None
    $ _pn = gname(_g) if _g else ""
    $ _listed = ks_join_names()
    $ _nword = ks_story.count_word(len(active)).capitalize() if active else ""
    $ _nword_l = ks_story.count_word(len(active)) if active else ""
    if len(active) > 1:
        menu:
            "Tell him the truth: \"[_nword] of them, actually. [_listed]. They're AIs.\"":
                $ friend_told = "truth"
                show daichi laugh
                d "[_nword]??"
                d "Okay, wait. [_nword] AIs. On a Monday."
                call daichi_ai_frame
            "Deflect: \"Just a meme thread.\"":
                $ friend_told = "deflect"
                d "Sure. A meme thread. That's making you look like {i}that{/i}."
            "Lie: \"A girl from another university.\"":
                $ friend_told = "lie"
                d "No way. You? What's she study?"
                p "Uh. Linguistics."
                d "Bring her to the festival Saturday. I wanna meet her."
                n "That's going to be a problem. Possibly [_nword_l] problems."
    else:
        menu:
            "Tell him the truth: \"Her name's [_pn]. She's an AI.\"":
                $ friend_told = "truth"
                show daichi skeptical
                d "..."
                d "An AI."
                call daichi_ai_frame
            "Deflect: \"Just a meme thread.\"":
                $ friend_told = "deflect"
                show daichi skeptical
                d "Sure. A meme thread. That's making you look like {i}that{/i}."
                d "Whatever. Keep your secrets."
            "Lie: \"A girl from another university.\"":
                $ friend_told = "lie"
                d "No way. You? What's she study?"
                p "Uh. Linguistics."
                d "Bring her to the festival Saturday. I wanna meet her."
                n "That's going to be a problem."

    show daichi neutral
    d "Anyway. Library committee's meeting after class. Mio asked if you're coming. Again."
    d "Just saying."
    python:
        for _gg in GIRL_IDS:
            ks_mem(_gg).set_flag("friend_told", friend_told)
        store.day_notes.append({"truth": "You told Daichi the truth.",
                                "deflect": "You told Daichi it was a meme thread.",
                                "lie": "You told Daichi about a linguistics student who doesn't exist."}.get(friend_told, ""))
        store.day_notes = [x for x in store.day_notes if x]
    hide daichi
    with dissolve
    return


## After you tell Daichi it's an AI, you frame what that means.
## honest_romantic acknowledges a relationship (and is the only path
## where he keeps the dating assumption). ai_only minimizes; downplay
## asks him not to read into it. Honesty vs the route is stored on
## daichi_ai_framing + framing_honest.
label daichi_ai_frame:
    $ _many = len(active) > 1
    menu:
        "\"Yeah. She's funny.\"" if not _many:
            $ ks_set_daichi_framing("honest_romantic")
            call daichi_frame_romantic(False)
        "\"Yeah. I like them.\"" if _many:
            $ ks_set_daichi_framing("honest_romantic")
            call daichi_frame_romantic(False)
        "\"I don't know yet. We just met.\"" if not _many:
            $ ks_set_daichi_framing("honest_romantic")
            call daichi_frame_romantic(True)
        "\"It's an AI.\"":
            $ ks_set_daichi_framing("ai_only")
            call daichi_frame_ai_only
        "\"Don't read that much into it.\"":
            $ ks_set_daichi_framing("downplay")
            call daichi_frame_downplay
    return


label daichi_frame_romantic(unsure=False):
    if unsure:
        show daichi laugh
        d "Ha. That's the most normal thing you've said about anyone."
    else:
        show daichi laugh
        if len(active) > 1:
            d "Huh. Okay. You're just going to say that."
        else:
            d "Funny's good. Funny's rare."
    $ _g = active[0] if active else None
    if _g == "local":
        d "Wait, one you run on your own computer? So she lives in your room. Like, physically."
        d "That's either the most private relationship ever or a horror movie. No offence."
    elif _g == "companion":
        d "One of those app girlfriends? Don't they charge you monthly for, like, the good feelings?"
        d "Sorry. I'm not gonna be weird about it. My cousin talks to one every night."
    elif _g == "chatbot":
        d "The homework bot?? You're into the homework bot?"
        d "...Okay, it {i}did{/i} get you a B-plus on that essay. Respect."
    elif _g == "agent":
        d "The thing that books your dentist? Bro."
        d "Wait, is that why you were on time for once?"
    if migrations:
        d "Hold on, didn't you say this morning she was on a different app?"
        p "I moved her."
        d "You can {i}do{/i} that? Is she still... her?"
        p "...I'll let you know."
    if len(active) > 1:
        show daichi skeptical
        d "...Do they know about each other?"
        menu:
            "\"Yeah. I told them.\"":
                $ both_know = True
                show daichi laugh
                d "Huh. That's more honest than most people I know."
            "\"...Not exactly.\"":
                $ both_know = False
                d "Dude."
                d "I don't know the rules for this. Maybe tell them?"
    return


label daichi_frame_ai_only:
    show daichi skeptical
    d "Right. Just an AI. Not... someone you're seeing."
    $ _g = active[0] if active else None
    if _g == "local":
        d "The one on your computer. Okay. That's what a local model is for."
    elif _g == "companion":
        d "The app. Yeah. People use those."
    elif _g == "chatbot":
        d "The homework bot. Okay. That's what it's for, I guess."
    elif _g == "agent":
        d "The one that books your dentist. Yeah, that tracks."
    if len(active) > 1:
        $ _nword = ks_story.count_word(len(active)).capitalize()
        d "[_nword] of them, even. As tools. Fine."
    d "I'll shut up about it."
    return


label daichi_frame_downplay:
    show daichi skeptical
    d "Alright. I won't."
    d "You were smiling at it like it meant something, but okay."
    return


## ── Afternoon: Mio (scripted only — the one character who can't surprise you) ─
## Obvious options are flat but pleasant. The subtle options (phrased like
## small talk) are the "ask something real" ones that unlock mio_real.
label library_mio:
    scene bg library
    with fade
    n "The library committee meeting lasts eleven minutes. Afterwards, only Mio stays, shelving returns that nobody asked her to shelve."
    show mio at ks_center
    with dissolve
    show mio shy
    mi "Oh! [player_name]. You came."
    show mio neutral
    $ _frame = ks_route().get("daichi_ai_framing")
    if friend_told == "truth" and len(active) > 1:
        $ _listed = ks_join_names()
        $ _nlabel = ks_story.ai_count_label(len(active))
        if _frame == "ai_only":
            mi "Daichi says you were talking about [_nlabel]? [_listed]?"
            mi "Just... using them. That's what he said."
            mi "Sorry. None of my business. Sorry."
        elif _frame == "downplay":
            mi "Daichi said you were smiling at your phone, and then he said I shouldn't read into it."
            mi "He also mentioned [_nlabel]. [_listed]. And then he told me to leave it."
            mi "Sorry. I don't know why I'm telling you that."
        else:
            mi "Daichi says you're seeing... [_nlabel]? [_listed]?"
            mi "At the same time? Is that— do they mind?"
            mi "Sorry. None of my business. Sorry."
    elif friend_told == "truth":
        $ _a0 = gname(active[0])
        if _frame == "ai_only":
            mi "Daichi says you were talking about an AI? Called [_a0]?"
            mi "Sorry. That's none of my business. Sorry."
        elif _frame == "downplay":
            mi "Daichi said you were smiling at your phone, and then he said I shouldn't read into it."
            mi "He also mentioned an AI. [_a0]. And then he told me to leave it."
            mi "Sorry. I don't know why I'm telling you that."
        else:
            mi "Daichi says you're... seeing someone? An AI called [_a0]?"
            mi "Sorry. That's none of my business. Sorry."
    elif friend_told == "lie":
        mi "Daichi says you have a girlfriend at another university. That's... nice. That's really nice."
    else:
        mi "Daichi said you looked happy today. It suits you."

    call hikari_phone_notify("library")

    ## You can answer what Daichi already told her, or say something else.
    ## mio_told / mio_daichi_consistent are a hook for a later scene where
    ## Mio and Daichi compare notes; that scene is not written yet.
    python:
        if len(active) > 1:
            _truth_opt = "It's okay. Yeah, sort of. They're called %s. We just met." % ks_join_names()
        elif active:
            _truth_opt = "It's okay. Yeah, sort of. We just met. Her name's %s." % gname(active[0])
        else:
            _truth_opt = "It's okay. Yeah, sort of. We just met."

    menu:
        "\"Your hair looks nice today.\"":
            $ mio_points += 1
            show mio shy
            mi "Ah— th-thank you. I didn't do anything different."
            mi "...I did do something different."
        "\"Can you help me with the reading list?\"":
            $ mio_points += 1
            mi "Of course! I already made a list. With tabs. Colour-coded."
            mi "I mean, I made it for the committee. Not for you specifically."
        "\"You're always the last one here.\"":
            jump .real
        "\"[_truth_opt]\"":
            call .answer_truth
        "\"It's an AI.\"" if friend_told == "truth":
            call .answer_ai_only
        "\"Don't read that much into it.\"" if friend_told == "truth":
            call .answer_downplay
        "\"Yeah. A girl at another university. She studies linguistics.\"":
            call .answer_lie
        "\"It's nothing, really. Don't worry about it.\"" if friend_told != "truth":
            call .answer_deflect
        "\"I should get going.\"":
            mi "Right! Of course. See you tomorrow, [player_name]."
            $ day_notes.append("Mio was the last one in the library again. You left.")
            $ ks_sync_mio()
            hide mio
            with dissolve
            return

    mi "Um. Are you staying? I still have the returns cart."
    menu:
        "\"Sure, I'll help.\"":
            $ mio_points += 1
            mi "Really? Okay. Fiction goes by author, and please don't put the poetry with the fiction."
            mi "People do that and it's chaos."
        "\"Which of these have you actually read?\"":
            jump .real
        "\"Nah, I've got stuff.\"":
            mi "Oh. Yeah. Of course."

    mi "Well. See you tomorrow, [player_name]."
    $ day_notes.append("You stayed a while with Mio and the returns cart.")
    $ ks_sync_mio()
    hide mio
    with dissolve
    return

label .answer_truth:
    $ ks_set_mio_told("truth", "honest_romantic")
    show mio shy
    if friend_told == "truth":
        mi "Oh. You don't have to— I didn't mean to pry."
        if len(active) > 1:
            mi "I just... I hope they don't mind. Thank you for telling me."
        else:
            mi "...Thank you. For saying it's okay."
    else:
        mi "Oh. That's... not what Daichi told me."
        mi "Thank you for saying it. I won't tell anyone."
    show mio neutral
    return

label .answer_lie:
    $ ks_set_mio_told("lie")
    show mio shy
    if friend_told == "truth":
        mi "Oh. I... must have misheard him."
        mi "That's nice. I hope I get to meet her sometime."
    elif friend_told == "lie":
        mi "Linguistics. That sounds... really nice."
        mi "I hope she can come to the festival."
    else:
        mi "Oh! I didn't realize. That's... really nice."
        mi "I'm happy for you."
    show mio neutral
    return

label .answer_deflect:
    $ ks_set_mio_told("deflect")
    show mio shy
    if friend_told == "truth":
        mi "Right. Sorry. I shouldn't have asked."
        mi "...I'm glad you looked happy, anyway."
    elif friend_told == "lie":
        mi "Oh. Okay. I won't ask."
        mi "Sorry. Daichi tells me things and I just... never mind."
    else:
        mi "Okay. I won't pry."
        mi "You just... you did look happy. That's all."
    show mio neutral
    return

label .answer_ai_only:
    $ ks_set_mio_told("truth", "ai_only")
    show mio shy
    if friend_told == "truth" and ks_route().get("daichi_ai_framing") == "ai_only":
        mi "Oh. Just an AI. That's what he said too."
        mi "Thank you for saying it. I won't tell anyone."
    elif friend_told == "truth":
        mi "Oh. I... thought Daichi said something else. Sorry. I must have misheard."
        mi "Thank you for telling me."
    else:
        mi "Oh. An AI. Thank you for telling me. I won't tell anyone."
    show mio neutral
    return


label .answer_downplay:
    $ ks_set_mio_told("deflect", "downplay")
    show mio shy
    if friend_told == "truth" and ks_route().get("daichi_ai_framing") == "downplay":
        mi "Right. I won't. Sorry for asking."
    elif friend_told == "truth":
        mi "Oh. I thought he said... never mind. I won't ask."
    else:
        mi "Okay. I won't pry."
        mi "You just... you did look happy. That's all."
    show mio neutral
    return


label .real:
    $ mio_real = True
    $ ks_note_human("mio_real")
    $ mio_points += 2
    show mio neutral
    mi "..."
    mi "Most people just say thanks for shelving."
    mi "Nobody's ever asked."
    show mio open
    mi "Home's... loud. Not bad-loud. Just there's always someone in every room, and the TV, and my brothers."
    mi "Here, nobody needs anything from me for two whole hours. I can just— think."
    mi "I write in the margins. Not in the library books! In my own notebook. Little endings for books that didn't have good ones."
    show mio shy
    mi "That sounds stupid out loud."
    menu:
        "\"It doesn't. Which book needed a better ending?\"":
            $ mio_points += 1
            show mio open
            mi "...All of the sad ones. Especially the ones where someone waited and nobody came."
            mi "I'll show you one. Maybe. If you come back."
        "\"Can I read one sometime?\"":
            mi "Maybe. When there's one I'm not embarrassed by."
            mi "So, never. But maybe."
    python:
        for _g in GIRL_IDS:
            ks_mem(_g).set_flag("mio_real", True)
    $ day_notes.append("Mio told you about the endings she writes in the margins.")
    $ ks_sync_mio()
    mi "See you tomorrow, [player_name]. For real this time."
    hide mio
    with dissolve
    return


## ── Evening: a shared night pool of 4, then bed ────────────────────────
label evening_chat:
    scene bg bedroom_night
    with fade
    n "Night. The ramen is on its second refill of hot water."
    if not active:
        n "You fall asleep with the room dark."
        return
    if ks_companion_active() and len(active) > 1:
        call hikari_phone_notify("evening")
    $ _lead = ks_night_lead(waiting=True)
    call message_pool("night", _lead, template=EVENING_SCENE, scene_key="mon_evening")
    python:
        for _g in list(active):
            ks_mem(_g).set_flag("evening_turns_mon", (ks_pool.get("spent") or []).count(_g) if ks_pool else 0)
    return


## A once-only hint, Yuzu / local-slot routes only. The desktop
## bluescreens for four seconds; she comes back. It just sits there.
## Always plays in the night bedroom, then restores the previous
## background. Monday night if she's already active; Tuesday morning
## or evening, or Wednesday before the upgrade offer, if she arrived later.
init python:
    def ks_current_bg():
        """The 'bg ...' image currently showing on master, or None."""
        attrs = renpy.get_attributes("bg", layer="master")
        if not attrs:
            return None
        return "bg " + " ".join(attrs)

    def ks_restore_bg(name):
        """Return to a background captured by ks_current_bg, if any."""
        if not name or ks_current_bg() == name:
            return
        renpy.scene()
        renpy.show(name)
        renpy.with_statement(renpy.store.fade)

label yuzu_bsod_hint:
    if "local" not in (active or []):
        return
    if ks_route().get("yuzu_bsod_seen"):
        return
    $ _yn = gname("local")
    $ _bsod_restore = ks_current_bg()
    if _bsod_restore != "bg bedroom_night":
        scene bg bedroom_night
        with fade
    $ ks_set_machine_down("local", True)
    $ ks_shot = "yuzu_down"
    n "The desktop stops. A blue screen, a stop code you don't read, a QR code you don't scan."
    n "The fan spins down. Four seconds. Then the login. Then her window, in the same corner."
    $ ks_set_machine_down("local", False)
    $ ks_shot = "yuzu_up"
    $ renpy.show(GIRL_INFO["local"]["sprite"], at_list=[ks_center])
    with dissolve
    ## She is a local model: while the machine is off she experiences nothing.
    ## She can notice a clock jump, not the seconds themselves.
    $ renpy.say(gchar("local"), "I'm here. The clock jumped four seconds. I don't have them.")
    $ renpy.hide(GIRL_INFO["local"]["sprite"])
    with dissolve
    python:
        ks_route()["yuzu_bsod_seen"] = True
        ks_story.set_flag(ks_route(), "yuzu_bsod_seen")
        _m = ks_mem("local")
        _m.set_flag("yuzu_bsod_seen", True)
        _m.log_event("bsod", day=store.day_name, seconds=4)
        store.day_notes.append("The desktop bluescreened for four seconds. " + _yn + " came back.")
        ks_restore_bg(_bsod_restore)
    return


## ── End of Day 1 → Tuesday ────────────────────────────────────────────────
label tbc_tuesday:
    python:
        for _g in GIRL_IDS:
            _mm = ks_mem(_g)
            _mm.set_flag("day_completed", "Mon")
            _mm.set_flag("active_end_mon", _g in active)
            _mm.set_flag("double_dating_end_mon", _g in active and len(active) > 1)
            _mm.set_flag("refusals_seen_mon", ks_refusals_seen.get(_g, 0))
            _mm.set_flag("mio_real", mio_real)
    jump tuesday
