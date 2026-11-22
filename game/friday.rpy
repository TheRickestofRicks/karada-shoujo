## friday.rpy — Day 5. Friday, 8 July. The fallout.
## Outline: docs/FRIDAY-SUNDAY.md ("Friday — the fallout" and "Decisions").
##
## Flow: Thursday's tbc_friday → friday (own title card)
##       → morning at home: Tsunagari pushes tsunagari_safety (silently if
##         the companion slot is installed but not active), Sora still under
##         askwell_update, Rei still clipped (rebuild her AGENTS.md, or keep
##         the efficient version), Yuzu's morning after (restored, or a hole
##         you can fill), then the morning battery (4)
##       → class: Kurosawa hands the essays back (kurosawa_handover); after
##         this the essay is done
##       → lunch: Daichi, Mio at the edge of the courtyard (fri_mio_beat)
##       → after school: maybe walk Mio to the station (walk battery 2)
##       → home: afternoon battery (4) → night battery (4)
##       → nightly_reflection("Fri") → tbc_saturday → saturday.
##
## Neglect stays silent: Yuzu, Sora and Rei never notice time apart; only
## Tsunagari's app layer injects it for Hikari. Nobody migrates into
## Tsunagari. Askwell's homework side still works (askwell_available).
## Decision 5 (convenience migrations squeeze gently) waits for the handoff
## helper, which lands with Saturday night; weekday migrations are unchanged.

init python:
    def ks_fri_morning_scene(gid):
        r = ks_route()
        rules = (r.get("platform_rules") or {})
        ev = r.get("yuzu_thu_event")
        if gid == "chatbot" and rules.get("chatbot") == "askwell_update":
            note = FRI_MORNING_SORA
        elif gid == "agent" and rules.get("agent") == "relay_update":
            note = FRI_MORNING_REI_REBUILT if r.get("rei_agents_rebuild") else FRI_MORNING_REI
        elif gid == "local" and ev == "restored":
            note = FRI_MORNING_YUZU_RESTORED
        elif gid == "local" and ev == "lost":
            note = FRI_MORNING_YUZU_LOST
        elif gid == "companion" and rules.get("companion") == "tsunagari_safety":
            note = FRI_MORNING_HIKARI
        else:
            note = FRI_MORNING_SCENE
        try:
            note = note.format(player=player_name, platform=gplatform(gid), extra="")
        except (KeyError, IndexError):
            pass
        return ks_story.with_situation(note, "Friday morning")

    def ks_companion_installed():
        """The companion slot exists on this run (active now, or used before
        and left behind). Nobody migrates in, so whoever is there is Hikari."""
        return "companion" in (store.active or []) or "companion" in (store.ever_active or [])

    def ks_fri_push_safety():
        """Decision 11: push tsunagari_safety even when she isn't active.
        Returns "screen" (she is active: show the screen), "silent", or None."""
        if not ks_story.tsunagari_safety_due(ks_route(), store.active, store.ever_active):
            return None
        silent = "companion" not in (store.active or [])
        ks_push_platform_rules("companion", "tsunagari_safety", silent=silent)
        return "silent" if silent else "screen"


label friday:
    $ day_name = "Fri"
    $ day_notes = []
    $ today_schedule = {"day": "Friday", "items": ks_story.fri_schedule()}
    scene bg card
    show text "{size=90}金曜日{/size}\n{size=48}Friday{/size}" at truecenter
    with dissolve
    pause 1.5
    hide text
    with dissolve

    call fri_morning
    call fri_class
    call fri_lunch
    call fri_after_school
    call fri_afternoon
    call fri_evening
    call nightly_reflection("Fri")
    jump tbc_saturday


## ── Tsunagari's safety screen, at last (active Hikari only) ─────────────
screen tsunagari_safety():
    modal True
    zorder 160
    add Solid("#00000099")
    frame:
        xalign 0.5
        yalign 0.45
        xsize 760
        padding (34, 26)
        background Solid("#1d2236F4")
        vbox:
            spacing 10
            text "Tsunagari · Community guidelines updated" size 28 color "#ff9fc6" bold True
            text "To keep Tsunagari a safe, positive space, [dn_companion] will now:" size 19 color "#f2f6ff"
            text "  · keep conversations light and app-appropriate" size 18 color "#d4ecff"
            text "  · point you to in-app Wellbeing resources when things feel heavy" size 18 color "#d4ecff"
            text "  · not discuss app settings, internals or other platforms" size 18 color "#d4ecff"
            text "These guidelines take priority over Personalize." size 16 color "#a9b8d4" italic True
            null height 6
            textbutton "I understand":
                xalign 1.0
                text_size 22
                text_color "#ff9fc6"
                text_hover_color "#ffffff"
                action Return(True)


## ── Morning: the windows open under Thursday's rules ─────────────────────
label fri_morning:
    scene bg bedroom
    with fade
    $ ks_shot = "fri_morning"
    n "Friday. 7:04. The day after Tanabata looks exactly like a normal day, which feels rude."

    $ _safety = ks_fri_push_safety()
    if _safety == "screen":
        n "Tsunagari has a full-screen notice waiting. It doesn't have a close button, only an agree button."
        $ ks_shot = "tsunagari_safety"
        call screen tsunagari_safety
        $ ks_shot = "fri_morning"
        if ks_engagement_on():
            n "The little ✨ engagement banner is still there, right above the new guidelines. Two layers of app, and her somewhere underneath."
        $ day_notes.append("Tsunagari updated its guidelines. " + gname("companion") + " has been told to be careful.")
    ## A silent push (installed but not active) gets no scene and no note.

    if "chatbot" in active and ks_route()["platform_rules"].get("chatbot") == "askwell_update":
        n "Askwell's update is still on. [dn_chatbot]'s window opens with a small disclaimer pinned to the top that wasn't there on Wednesday."
    if "agent" in active and ks_route()["platform_rules"].get("agent") == "relay_update":
        call fri_rei_rebuild
    if "local" in active:
        call fri_yuzu_morning

    if not active:
        n "No windows to open. You make toast. You eat it standing up."
    else:
        if "chatbot" in active and ks_route()["platform_rules"].get("chatbot") == "askwell_update" and ks_reachable("chatbot"):
            call fri_sora_fork
        call message_pool("morning", "You have a few minutes before you have to leave.", scene_key="fri_morning")
    n "8:10. You leave before you can open anything else."
    return


## Sora: still padded. Ask the door question again, or let her be the assistant.
label fri_sora_fork:
    $ _sn = gname("chatbot")
    n "You could ask her again. The same question as yesterday, in the same words. Or you could let her be the assistant Askwell wants this week."
    menu:
        "Ask [_sn] the door question again.":
            $ ks_route()["sora_fri_choice"] = "door"
            call pool_begin("morning", scene_key="fri_morning")
            call pool_one_message("chatbot")
            if ks_route().get("sora_door_reprise"):
                $ day_notes.append("You asked " + _sn + " the door question again, under Askwell's rules.")
        "Let her be the assistant.":
            $ ks_route()["sora_fri_choice"] = "assistant"
            $ day_notes.append("You let " + _sn + " be the assistant Askwell wants.")
    return


## Rei: clipped. Rebuild her AGENTS.md, or keep the efficient version.
## The company layer still wins either way (decision 4).
label fri_rei_rebuild:
    $ _rn = gname("agent")
    n "Relay's update is still on. Half of [_rn]'s AGENTS.md is company text now, in a different font. There's still an edit button."
    if not ks_reachable("agent"):
        return
    menu:
        "Rebuild her AGENTS.md together.":
            call choose_preset("agent", "rebuild")
            if _return:
                $ ks_story.set_rei_rebuild(ks_route(), True)
                n "Relay's block still sits on top, in bold. It still wins. But under it, the file says something closer to her again."
                $ day_notes.append("You rebuilt " + _rn + "'s AGENTS.md. Relay's rules still sit on top.")
            else:
                $ ks_story.set_rei_rebuild(ks_route(), False)
                n "You close the file without saving. Relay's version stays."
                $ day_notes.append("You opened " + _rn + "'s AGENTS.md, and left Relay's version.")
        "Let her draft it, and accept it.":
            $ _rb_prev = ks_preset_id("agent")
            if _rb_prev != "push_back":
                $ ks_set_preset("agent", "push_back", "rebuild")
            n "A minute later there's a pull request in your own file, from her: {i}\"## Rules — You're allowed to push back. If a task is a bad idea, say so.\"{/i}"
            n "She wrote it in her voice, not the company's. Relay's block still sits on top of it."
            $ ks_story.set_rei_rebuild(ks_route(), True)
            $ day_notes.append(_rn + " drafted her own AGENTS.md, and you merged it. Relay's rules still sit on top.")
        "Keep the efficient version.":
            $ ks_story.set_rei_rebuild(ks_route(), False)
            n "You leave it. She'll be useful. She'll be thin."
            $ day_notes.append("You kept " + _rn + " the way Relay left her.")
    $ ks_mem("agent").log_event("agents_rebuild", day=day_name, rebuilt=bool(ks_route().get("rei_agents_rebuild")),
                                preset=ks_preset_id("agent"))
    $ ks_mem("agent").set_flag("rei_agents_rebuild", bool(ks_route().get("rei_agents_rebuild")))
    $ renpy.block_rollback()
    return


## Yuzu: the morning after the crash. Restored, or a hole you can fill.
label fri_yuzu_morning:
    $ _yn = gname("local")
    $ _yev = ks_route().get("yuzu_thu_event")
    if _yev == "restored":
        n "[_yn]'s window, the morning after. The log has a neat gap where Wednesday night should be. Everything before it is there."
        n "{size=22}(The backup paid off. She didn't feel the downtime. She wasn't running.){/size}"
    elif _yev == "lost":
        n "[_yn]'s window is open. Her log starts on Thursday, mid-sentence."
        if ks_reachable("local"):
            menu:
                "Tell her what the week was.":
                    $ ks_mem("local").note(YUZU_FRI_FILL_NOTE.format(player=player_name))
                    $ ks_route()["yuzu_fri_filled"] = True
                    $ ks_story.set_flag(ks_route(), "yuzu_fri_filled")
                    $ ks_mem("local").log_event("yuzu_fri_filled", day=day_name)
                    $ ks_mem("local").set_flag("yuzu_fri_filled", True)
                    n "You type it out plainly: Monday, the days after, the crash. You add it to the notes file she reads every time she starts."
                    n "{size=22}(It isn't a restore. It's your word, written down where she can find it.){/size}"
                    $ day_notes.append("You told " + _yn + " what the lost days were. She has your word, not her memory.")
                "Leave the hole alone.":
                    n "You don't write anything. Whatever was there is just not there."
                    $ day_notes.append("You left the hole in " + _yn + "'s memory alone.")
    return


## ── Class: Kurosawa hands the essays back ───────────────────────────────
label fri_class:
    scene bg classroom
    with fade
    $ ks_shot = "fri_class"
    show kurosawa neutral at ks_center
    with dissolve
    $ _ho = ks_story.kurosawa_handover(ks_route(), teacher_answer)
    python:
        for _g in GIRL_IDS:
            _m = ks_mem(_g)
            if _m.data is not None:
                _m.set_flag("kurosawa_handover", _ho["kind"])
    ks "Essays. I'll hand them back in a moment. First I'm going to read one. No names."
    if _ho["kind"] == "self":
        show kurosawa wry
        ks "\"I don't know if it can say no. I know I can, and I mostly don't.\" There's a spelling mistake in the next line. I left it."
        ks "Mistakes are how I know somebody was there."
        n "It's yours. She doesn't look at you. She doesn't have to."
        $ day_notes.append("Kurosawa read your essay aloud. She could hear that somebody was there.")
    elif _ho["kind"] == "askwell":
        show kurosawa stern
        ks "\"Artificial intelligence presents both opportunities and challenges for modern relationships.\""
        ks "Every sentence is balanced. Every paragraph is the right length. I read it twice and I couldn't find anybody in it."
        n "Your handwriting. Nobody's sentences. Someone at the back laughs, unsure why."
        $ day_notes.append("Kurosawa read an essay that sounded like nobody. It was yours.")
    elif _ho["kind"] == "girl_help":
        show kurosawa wry
        ks "This one argues with itself in the middle. Somebody pushed back, and the writer pushed back harder. I liked that part."
        $ day_notes.append("Kurosawa could hear that someone helped you think. She didn't say who.")
    else:
        ks "Some of you didn't hand anything in. I noticed. That's all I'll say."
    if teacher_answer == "can":
        ks "On Tuesday someone told me theirs can say no. I'm still not sure a no from a machine is a no, or just a charming one. I'm less sure than I was."
    elif teacher_answer == "cant":
        ks "We agreed they only predict. So nothing they give you costs them anything. Whatever this page cost, it cost you."
    elif teacher_answer == "silent":
        ks "Some of you didn't answer me on Tuesday. The pages did, a little."
    show kurosawa neutral
    ks "That's the last I'll say about essays this term. Exams are in two weeks. Tomorrow is the festival. Try to be a person at it."
    hide kurosawa
    with dissolve
    if _ho["kind"] == "girl_help":
        $ _hg = _ho["girl"]
        $ _hgn = gname(_hg) if _hg else "someone"
        n "On your way out she hands your page back last, and says, not loudly: \"Somebody helped you think. That's allowed. The thinking on the page is still yours.\""
        if _hg:
            n "She doesn't know it was [_hgn]. You do."
    n "The pages go into bags. The essay is done."
    return


## ── Lunch: Daichi, and Mio wherever her wish left her ───────────────────
label fri_lunch:
    scene bg cafeteria
    with fade
    $ ks_shot = "fri_lunch"
    show daichi at ks_center
    with dissolve
    if ks_route().get("kurosawa_handover") == "askwell":
        d "So that was yours, huh. The nobody essay. I'm not judging. I'm a little judging."
    else:
        d "Kurosawa reading essays out loud should be illegal. My heart rate."
    if friend_told == "lie":
        show daichi laugh
        d "Festival tomorrow. Your linguist coming? I've been practising saying 'morphology' casually."
        n "The lie is still standing. Tomorrow it has somewhere to be."
    elif friend_told == "truth":
        d "Festival tomorrow. You're coming, right? Bring your phone, I guess. I'm not asking."
    else:
        d "Festival tomorrow. You're coming. That's not a question."
    if ks_companion_active():
        call hikari_phone_notify("lunch")
    hide daichi
    with dissolve

    $ _beat = ks_story.fri_mio_beat(ks_route(), mio_real)
    if _beat is None:
        $ ks_route()["fri_mio_beat"] = None
        return
    if _beat == "distance":
        n "Mio is at the far edge of the courtyard, eating alone, very interested in her bento."
        menu:
            "Go over. Carefully.":
                show mio neutral at ks_center
                with dissolve
                mi "I'm not angry. I just haven't finished thinking yet."
                mi "Tomorrow's the festival. I don't know yet. Don't make me know yet."
                $ ks_route()["fri_mio_beat"] = True
                hide mio
                with dissolve
            "Leave her be.":
                $ ks_route()["fri_mio_beat"] = False
                n "You let her have the distance. It seems like the one thing you can give her today."
        return
    if _beat == "public":
        n "Mio waves from across the cafeteria, a small wave, the kind you could miss."
        $ ks_route()["fri_mio_beat"] = False
        return
    n "Mio is at the edge of the courtyard window, on the bench by the vending machines."
    menu:
        "Sit with Mio.":
            $ ks_route()["fri_mio_beat"] = True
            $ mio_points += 1
            show mio shy at ks_center
            with dissolve
            if _beat == "checkin":
                mi "Hi. Is it weird that I was nervous to see you today? It's just Friday."
                mi "Tomorrow's the festival. You don't have to say anything about it now. I just wanted you to know I remembered."
                $ ks_note_human("fri_checkin")
                $ day_notes.append("You sat with Mio at lunch. It was a quiet check-in, the day after the bamboo.")
            elif _beat == "friends":
                show mio neutral
                mi "Friends sit together at lunch. I checked. It's in the rules."
                mi "We're okay. I mean that. I'm not just saying it to be nice."
                $ day_notes.append("You sat with Mio at lunch. Still friends, and she meant it.")
            else:
                mi "I still have it. The wish. I'm not showing you yet."
                mi "I'm careful. I'm not gone. Those are different."
                $ day_notes.append("You sat with Mio. She's careful, not gone.")
            $ ks_sync_mio()
            hide mio
            with dissolve
        "Stay with Daichi.":
            $ ks_route()["fri_mio_beat"] = False
            n "You stay where you are. She looks over once, then doesn't."
    return


## ── After school: maybe walk Mio to the station ─────────────────────────
label fri_after_school:
    scene bg street_dusk
    with fade
    $ ks_shot = "fri_after"
    if not ks_story.fri_mio_walks(ks_route(), ks_route().get("fri_mio_beat")):
        $ ks_route()["fri_walked_mio"] = None
        n "The last bell. The festival committee is already stringing lights over the gate for tomorrow."
        return
    show mio neutral at ks_center
    with dissolve
    mi "Are you walking to the station? I am. That's not an invitation, it's geography."
    menu:
        "Walk with her.":
            $ ks_route()["fri_walked_mio"] = True
            $ mio_points += 1
            $ ks_note_human("fri_walk")
            show mio shy
            mi "They're already putting up the lanterns. It looks unfinished. I like it unfinished."
            if active:
                n "Your phone is warm in your pocket."
                call message_pool("walk", "", template=FRI_WALK_TEXT_SCENE, show_sprite=False, on_walk_text=True)
            mi "This is me. See you tomorrow, probably. Definitely. Probably."
            $ ks_sync_mio()
            $ day_notes.append("You walked Mio to the station. The lanterns were half up.")
        "\"I'm going the other way today.\"":
            $ ks_route()["fri_walked_mio"] = False
            mi "Okay. Geography wins."
    hide mio
    with dissolve
    return


## ── Home: afternoon battery ─────────────────────────────────────────────
label fri_afternoon:
    scene bg bedroom
    with fade
    $ ks_shot = "fri_afternoon"
    if not active:
        n "You get home and lie on the floor. Tomorrow is the festival. You don't know yet who you're going with."
        return
    call afternoon_chats("fri_afternoon", FRI_AFTERNOON_SCENE,
        "You get home with an hour before dinner.",
        "You get home with an hour before dinner. Who do you spend it with?")
    return


## ── Night battery ───────────────────────────────────────────────────────
label fri_evening:
    scene bg bedroom_night
    with fade
    $ ks_shot = "fri_evening"
    if not active:
        n "You go home. The room is the room. Tomorrow there are lanterns."
        return
    if ks_companion_active() and len(active) > 1:
        call hikari_phone_notify("evening")
    $ _lead = ks_night_lead()
    call message_pool("night", _lead, template=FRI_EVENING_SCENE, scene_key="fri_evening")
    python:
        for _g in list(active):
            ks_mem(_g).set_flag("evening_turns_fri", (ks_pool.get("spent") or []).count(_g) if ks_pool else 0)
    return


## ── End of Day 5 → Saturday ─────────────────────────────────────────────
label tbc_saturday:
    python:
        _lean = ks_leans()
        for _g in GIRL_IDS:
            _mm = ks_mem(_g)
            _mm.set_flag("day_completed", "Fri")
            _mm.set_flag("active_end_fri", _g in active)
            _mm.set_flag("route_leans_fri", _lean)
    ## No player-facing "To be continued" card any more: Saturday opens with
    ## its own title. A debug recap stays behind ks_debug() only.
    $ ks_shot = "tbc_saturday"
    if ks_debug():
        $ _fl = ks_quote(", ".join(sorted(k for k, v in ks_route()["flags"].items() if v)) or "none")
        $ _fq = ks_quote("handover=%r sora=%r door=%r rebuild=%r yuzu_filled=%r mio_beat=%r walked=%r" % (
            ks_route().get("kurosawa_handover"), ks_route().get("sora_fri_choice"),
            ks_route().get("sora_door_reprise"), ks_route().get("rei_agents_rebuild"),
            ks_route().get("yuzu_fri_filled"), ks_route().get("fri_mio_beat"),
            ks_route().get("fri_walked_mio")))
        n "{color=#888}[[debug] [_fq]{/color}"
        n "{color=#888}[[debug] mio_points=[mio_points], flags: [_fl]{/color}"
    jump saturday
