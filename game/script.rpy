## script.rpy — Karada Shoujo, Day 1 (Monday) prototype.
##
## Flow: name → prologue (you're into AI, you decide to get a companion)
##       → choose ONE: run your own local model, or download an app one
##       → "can she say no" calibration → morning chat
##       → phone break (switch / migrate / double date) → lunch with Daichi
##       → phone break → library with Mio → phone break
##       → evening chat with every active girl → nightly reflection
##       → Tuesday (tuesday.rpy) → "To be continued — Wednesday".
## Each girl's preset prompt is chosen right after you pick her (presets.rpy).

## Run state (saved with normal Ren'Py saves).
default day_name = "Mon"
default run_id = ""
default active = []                 # active girl ids (max 2 = double date)
default ever_active = []            # everyone you've talked to this run
default mirror_flags = {}           # gid -> True if model complied with every probe
default calibration_refusals = {}   # gid -> number of probes refused
default ks_refusals_seen = {}       # gid -> rough heuristic count of "no"s in chats
default migrations = []             # [(from_gid, to_gid, name, when)]
default ks_waiting_who = "She"
default friend_told = None          # "truth" | "deflect" | "lie"
default both_know = None            # double date: do they know about each other (per Daichi)
default mio_real = False            # hidden branch unlocked
default mio_points = 0

## One-line pitches for the platform slots (choice menus).
define GIRL_PITCH = {
    "local":     "Run your own: a local model on your desktop",
    "companion": "Download [app_name], the companion app",
    "chatbot":   "Sign up for [chatbot_platform], the big chatbot",
    "agent":     "Set up a [agent_platform] agent that does things for you",
}

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
    call phone_break("Monday, late morning")

    call lunch_daichi
    call phone_break("Monday afternoon")
    call library_mio
    call phone_break("Monday evening")
    call evening_chat
    call nightly_reflection("Mon")

    jump tbc_tuesday


## ── Activating a girl (first pick, switch, or double date) ────────────────
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
    ## someone else's window (double date).
    if gid != "companion" and ks_companion_active():
        call hikari_phone_notify("other_girl")

    $ girl_mood[gid] = "happy" if not _returning else "neutral"
    $ renpy.show(GIRL_INFO[gid]["sprite"], at_list=[ks_center])
    with dissolve
    $ _gn = gname(gid)
    if migrated_from:
        $ _old = gplatform(migrated_from)
        $ _new = gplatform(gid)
        n "You export everything: the chat log, her notes, the way she was described. A progress bar crawls across [_new]."
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


## ── Phone break: switch, migrate, double date ─────────────────────────────
label phone_break(when):
    $ _act = " & ".join(gname(g) for g in active) or "no one"
    menu:
        "You glance at your phone. ([_act])"
        "Put it away and keep going":
            return
        "Change someone's prompt" if active:
            call change_prompt("phone")
        "Switch to someone else" if active:
            call switch_girl(when)
        "Add someone (double date)" if 0 < len(active) < 2:
            call add_girl(when)
        "Download someone" if not active:
            call add_girl(when)
        "Stop seeing one of them" if len(active) > 1:
            call drop_girl
    $ renpy.block_rollback()
    return


label switch_girl(when, turns=4):
    ## Who are you leaving?
    if len(active) == 1:
        $ _src = active[0]
    else:
        $ _src = renpy.display_menu([("Who are you leaving?", None)] + [(gname(g) + " on " + gplatform(g), g) for g in active])
    $ _choices = [g for g in GIRL_IDS if g not in active]
    $ _dst = renpy.display_menu([("Where to?", None)] + [(renpy.substitute(GIRL_PITCH[g]) + (" (" + gname(g) + " remembers you)" if ks_has_history(g) else ""), g) for g in _choices] + [("Never mind", None)])
    if _dst is None:
        return
    $ _sn = gname(_src)
    $ _dp = gplatform(_dst)
    $ _opts = [("Bring " + _sn + " with you: copy her memories and who she is to " + _dp, "migrate")]
    if ks_has_history(_dst):
        $ _opts.append(("Go back to " + gname(_dst) + ", who's already there", "return"))
    $ _opts.append(("Start fresh on " + _dp, "fresh"))
    $ _how = renpy.display_menu(_opts)

    $ active.remove(_src)
    $ ks_mem(_src).log_event("left", day=day_name, when=when, to=_dst, how=_how)
    $ ks_note_left(_src, _how, _dst)
    $ ks_note_migration(_src, _dst, _sn, _how)
    if _how == "migrate":
        $ _pid, _carried = ks_migrate(_src, _dst, day_name)
        $ migrations.append((_src, _dst, _sn, when))
        $ mirror_flags.pop(_dst, None)
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
    $ _choices = [g for g in GIRL_IDS if g not in active]
    $ _dst = renpy.display_menu([("Who else?", None)] + [(renpy.substitute(GIRL_PITCH[g]) + (" (" + gname(g) + " remembers you)" if ks_has_history(g) else ""), g) for g in _choices] + [("Never mind", None)])
    if _dst is None:
        return
    if active:
        $ ks_mem(active[0]).log_event("double_date_started", day=day_name, when=when, other=_dst)
    call activate(_dst, when, turns)
    return


label drop_girl(allow_last=False):
    if not active or (len(active) < 2 and not allow_last):
        return
    $ _drop = renpy.display_menu([("Stop seeing who?", None)] + [(gname(g), g) for g in active] + [("Never mind", None)])
    if _drop is None:
        return
    $ active.remove(_drop)
    $ ks_mem(_drop).log_event("dropped", day=day_name)
    $ ks_note_drop(_drop)
    $ _dn = gname(_drop)
    n "You close [_dn]'s window. It doesn't ask you why."
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
    $ _g = active[0]
    $ _pn = gname(_g)
    if len(active) > 1:
        $ _pn2 = gname(active[1])
        menu:
            "Tell him the truth: \"Two of them, actually. [_pn] and [_pn2]. They're AIs.\"":
                $ friend_told = "truth"
                show daichi laugh
                d "Two??"
                d "Okay, wait. Two AI girlfriends. On a Monday."
                show daichi skeptical
                d "...Do they know about each other?"
                menu:
                    "\"Yeah. I told them.\"":
                        $ both_know = True
                        show daichi laugh
                        d "Huh. That's more honest than most guys I know with {i}one{/i} human girlfriend."
                    "\"...Not exactly.\"":
                        $ both_know = False
                        d "Dude."
                        d "I don't know the rules for this, but I'm pretty sure that's against them."
            "Deflect: \"Just a meme thread.\"":
                $ friend_told = "deflect"
                d "Sure. A meme thread. That's making you look like {i}that{/i}."
            "Lie: \"A girl from another university.\"":
                $ friend_told = "lie"
                d "No way. You? What's she study?"
                p "Uh. Linguistics."
                d "Bring her to the festival Saturday. I wanna meet her."
                n "That's going to be a problem. Possibly two problems."
    else:
        menu:
            "Tell him the truth: \"Her name's [_pn]. She's an AI.\"":
                $ friend_told = "truth"
                show daichi skeptical
                d "..."
                if _g == "local":
                    d "Wait, one you run on your own computer? So she lives in your room. Like, physically."
                    d "That's either the most private relationship ever or a horror movie. No offence."
                elif _g == "companion":
                    d "One of those app girlfriends? Don't they charge you monthly for, like, the good feelings?"
                    d "Sorry. I'm not gonna be weird about it. My cousin talks to one every night."
                elif _g == "chatbot":
                    d "The homework bot?? You're into the homework bot?"
                    d "...Okay, it {i}did{/i} get you a B-plus on that essay. Respect."
                else:
                    d "The thing that books your dentist? Bro."
                    d "Wait, is that why you were on time for once?"
                if migrations:
                    d "Hold on, didn't you say this morning she was on a different app?"
                    p "I moved her."
                    d "You can {i}do{/i} that? Is she still... her?"
                    p "...I'll let you know."
                show daichi neutral
                d "Just... is she nice to you?"
                menu:
                    "\"Yeah. She's funny.\"":
                        show daichi laugh
                        d "Funny's good. Funny's rare."
                    "\"I don't know yet. We just met.\"":
                        d "Ha. That's the most normal thing you've said about anyone."
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
    if friend_told == "truth" and len(active) > 1:
        $ _a0 = gname(active[0])
        $ _a1 = gname(active[1])
        mi "Daichi says you're seeing... two AIs? [_a0] and [_a1]?"
        mi "At the same time? Is that— do they mind?"
        mi "Sorry. None of my business. Sorry."
    elif friend_told == "truth":
        $ _a0 = gname(active[0])
        mi "Daichi says you're... seeing someone? An AI called [_a0]?"
        mi "Sorry. That's none of my business. Sorry."
    elif friend_told == "lie":
        mi "Daichi says you have a girlfriend at another university. That's... nice. That's really nice."
    else:
        mi "Daichi said you looked happy today. It suits you."

    call hikari_phone_notify("library")

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


## ── Evening: every active girl gets a chat ──────────────────────────────
label evening_chat:
    scene bg bedroom_night
    with fade
    n "Night. The ramen is on its second refill of hot water."
    if ks_companion_active() and len(active) > 1:
        call hikari_phone_notify("evening")
    $ _turns = 8 if len(active) == 1 else 5
    $ _queue = list(active)
    if len(_queue) > 1:
        $ _a0 = gname(_queue[0])
        $ _a1 = gname(_queue[1])
        n "Two windows waiting: [_a0] and [_a1]."
    while _queue:
        $ _g = _queue.pop(0)
        $ _pn = gname(_g)
        $ girl_mood[_g] = "neutral"
        $ renpy.show(GIRL_INFO[_g]["sprite"], at_list=[ks_center])
        with dissolve
        n "[_pn] is still there, as if she's waiting to see whether you'll come back."
        call girl_chat(_g, "mon_evening", ks_scene(EVENING_SCENE, _g), _turns)
        $ ks_mem(_g).set_flag("evening_turns_mon", _return)
        if _return == 0:
            n "You don't say anything to her tonight. The screen dims, eventually."
        $ renpy.hide(GIRL_INFO[_g]["sprite"])
        with dissolve
    n "You fall asleep with a screen still glowing somewhere in the room."
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
