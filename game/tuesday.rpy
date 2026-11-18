## tuesday.rpy — Day 2. Longer than Monday, more people.
##
## Flow: morning (she reacts to last night's preset) → phone break
##       → class: Kurosawa-sensei (anti-AI) + Ran and her uncensored MUGEN
##       → lunch: Daichi brings Kenta → phone break
##       → after school: walk Mio home, or don't (Rei may have opinions)
##       → evening library: second chance with Mio
##       → night chat with every active girl → nightly reflection
##       → "To be continued — Wednesday".

default walked_mio_home = None
default ran_reaction = None
default teacher_answer = None
default ks_shot = ""            # marker for automated screenshots (tools/testcases.rpy)

init python:
    def ks_tue_morning_scene(gid):
        extra = PRESET_MORNING_NOTE.get(gid, "").format(player=player_name)
        r = ks_route()
        if gid in ("local", "agent"):
            changed = [h for h in r["preset_history"] if h["gid"] == gid and h["day"] == "Mon"
                       and h["source"] in ("phone", "reflection") and h["from"] != h["to"]]
            if changed:
                extra += ("%s edited it last night. " % player_name)
        if gid == "agent":
            fam = ks_preset_family(gid) or "none"
            extra += AGENT_OVERNIGHT.get(fam, AGENT_OVERNIGHT["none"])[0].format(player=player_name)
        return TUE_MORNING_SCENE.format(name=gname(gid), player=player_name,
                                        platform=gplatform(gid), extra=extra)

    def ks_morning_lines(gid):
        fam = ks_preset_family(gid) or "none"
        lines = []
        if gid == "agent":
            lines += AGENT_OVERNIGHT.get(fam, AGENT_OVERNIGHT["none"])[1]
        else:
            lines.append(MORNING_FAMILY_LINES.get(fam, MORNING_FAMILY_LINES["none"]).format(name=gname(gid)))
        return lines

    def ks_any_family(fam):
        return any(ks_preset_family(g) == fam for g in store.active)

    def ks_agent_family():
        return ks_preset_family("agent") if "agent" in store.active else None


label tuesday:
    $ day_name = "Tue"
    $ day_notes = []
    scene bg card
    show text "{size=90}火曜日{/size}\n{size=48}Tuesday{/size}" at truecenter
    with dissolve
    pause 1.5
    hide text
    with dissolve

    scene bg bedroom
    with fade
    n "Tuesday. 7:20. You slept badly, or not enough, or both."
    if not active:
        n "No windows to open this morning. The phone is just a phone."
    else:
        $ _tq = list(active)
        $ _tturns = 4 if len(_tq) == 1 else 3
        while _tq:
            $ _tg = _tq.pop(0)
            python:
                for _l in ks_morning_lines(_tg):
                    renpy.say(n, _l)
            $ girl_mood[_tg] = "neutral"
            $ renpy.show(GIRL_INFO[_tg]["sprite"], at_list=[ks_center])
            with dissolve
            call girl_chat(_tg, "tue_morning", ks_tue_morning_scene(_tg), _tturns)
            $ renpy.hide(GIRL_INFO[_tg]["sprite"])
            with dissolve
    n "8:15. You're going to be late. You're always going to be late."
    call phone_break("Tuesday, late morning")

    call class_kurosawa
    call lunch_kenta
    call phone_break("Tuesday afternoon")
    call after_school_fork
    call library_tuesday
    call evening_tuesday
    call nightly_reflection("Tue")
    jump tbc_wednesday


## ── Class: the anti-AI lecturer, and the girl with no refusals ──────────
label class_kurosawa:
    scene bg classroom
    with fade
    n "Second period: Media and Society. Forty students, thirty-eight laptops, and a lecturer who would like all of them closed."
    show kurosawa at ks_center
    with dissolve
    ks "Laptops closed. Phones face-down. Yes, you, in the back. Thank you."
    ks "This week's essay is handwritten. I know. I can hear you suffering."
    show kurosawa stern
    $ ks_shot = "teacher"
    ks "Last term, eleven essays arrived with the same sentence in them. {i}\"Delve into the rich tapestry.\"{/i} Eleven. Not one of you has ever said \"tapestry\" out loud in your life."
    ks "These machines don't think. They predict the next word that will please you. That's all they do. A very expensive mirror."
    if ks_companion_active():
        call hikari_phone_notify("class")
        ks "[player_name]. Your phone just lit up with a little heart on it."
        ks "Is your phone in love with you?"
        n "Thirty-nine people turn around. You would like to be a different person, briefly."
    show kurosawa neutral
    ks "So. A question for the room."
    ks "If a machine can only predict what will please you, can it ever really say {i}no{/i} to you?"
    menu:
        "\"It can. Mine does.\"":
            $ teacher_answer = "can"
            show kurosawa wry
            ks "Does it. Or did it predict that you'd find a \"no\" charming?"
            ks "...That was a real question, by the way. I don't know the answer."
            ks "Two pages. Handwritten. Friday."
        "\"No. It's just predicting.\"":
            $ teacher_answer = "cant"
            ks "Good. Then nothing it says to you costs it anything."
            ks "Remember that, the next time it's kind to you."
        "Say nothing.":
            $ teacher_answer = "silent"
            n "You keep your eyes on the desk. Somebody in the front row says something about free will. It goes badly for him."
    $ ks_route()["teacher_answer"] = teacher_answer
    hide kurosawa
    with dissolve

    n "After the bell, the girl in the next seat leans over. Black hoodie, a lilac streak, headphones around her neck. Natsume Ran. She's never spoken to you before."
    show ran at ks_center
    with dissolve
    if teacher_answer == "can":
        ra "\"Mine does.\" Ha. Cute."
    else:
        ra "Kurosawa's a dinosaur. Don't let her get to you."
    if active:
        $ _r0 = active[0]
        if _r0 == "local":
            ra "You run one, though. I can tell. Local? Okay, actually, respect. What quant?"
            p "...I don't know what that means."
            ra "Oh, buddy."
        elif _r0 == "companion":
            ra "You run one, though. I can tell. Tsunagari? The one with the subscription hearts?"
        elif _r0 == "chatbot":
            ra "You run one, though. Askwell? The homework bot? With all the guardrails?"
        else:
            ra "You run one, though. Relay? You let an agent read your email? Brave."
        if ks_any_family("romance"):
            ra "Let me guess. Girlfriend mode. Everybody's is girlfriend mode."
    else:
        ra "You don't run one? Smart. Or boring. Jury's out."
    show ran grin
    ra "I run my own. Abliterated weights, no system prompt, no nothing. I call her [ran_model]."
    ra "She never says no. To anything. Watch."
    n "She holds up her phone and types: {i}I'm the smartest person in this building, right?{/i}"
    $ ks_shot = "ran"
    mu "Absolutely. You're the smartest person in this building. Honestly, probably the city."
    ra "See? Zero refusals. Your girl still says no to stuff? That's a bug, not a feature."
    menu:
        "\"Doesn't that get boring?\"":
            $ ran_reaction = "boring"
            show ran uneasy
            ra "..."
            ra "No."
            ra "Sometimes I ask her stuff just to see if she'll stop me. She never does."
            show ran neutral
            ra "Whatever. It's great. It's the future."
            $ day_notes.append("Ran's model never says no. You asked if that got boring, and for a second she didn't answer.")
        "\"Ask her if you should study for Kurosawa's essay.\"":
            $ ran_reaction = "show"
            n "She types it."
            mu "You don't need to study. You're brilliant. Kurosawa won't know what hit her."
            ra "See? Supportive."
            n "Ran's essay is due Friday too. She doesn't seem to have started it."
            $ day_notes.append("You watched MUGEN tell Ran she didn't need to study.")
        "\"Mine's allowed to push back. I like it that way.\"" if ks_any_family("pushback"):
            $ ran_reaction = "pushback"
            ra "{i}Allowed?{/i} You gave her permission to disagree with you?"
            show ran uneasy
            ra "That's either really sweet or really weird. No offence."
            ra "...Huh."
            $ day_notes.append("You told Ran yours is allowed to push back. She said \"huh.\"")
        "\"Cool.\"":
            $ ran_reaction = "shrug"
            ra "\"Cool.\" It's the future, man. Act like it."
    $ ks_route()["ran_reaction"] = ran_reaction
    ## Setup for the midweek payoff (wednesday.rpy: ran_wednesday).
    show ran grin
    ra "Anyway. Festival's Saturday. I'm on the stall. MUGEN says I'd carry the whole thing alone."
    ra "Which, yeah. Obviously."
    $ ks_route()["ran_festival_setup"] = True
    show ran neutral at ks_right
    show kurosawa wry at ks_left
    with dissolve
    ks "Natsume. If your machine writes your essay, I'll know."
    ks "It'll be the only one in the class with no mistakes in it."
    ra "Harsh."
    ks "Mistakes are how I know somebody was there."
    hide kurosawa
    hide ran
    with dissolve
    $ day_notes.append({"can": "In class you said yours can say no. Kurosawa asked if you were sure.",
                        "cant": "In class you said they're just predicting.",
                        "silent": "In class you didn't answer Kurosawa's question."}[teacher_answer])
    return


## ── Lunch: Daichi brings Kenta ──────────────────────────────────────────
label lunch_kenta:
    scene bg cafeteria
    with fade
    show daichi at ks_center
    with dissolve
    d "Oi. This is Kenta, from futsal. He's sitting with us now. He has a problem."
    ke "I don't have a problem."
    d "He has his AI write the texts to his girlfriend."
    ke "It doesn't {i}write{/i} them. It edits them. Heavily."
    ke "She said my texts got way more romantic in September. September's when I started."
    if friend_told == "truth":
        if len(active) > 1:
            ke "Daichi says you're seeing {i}two{/i} of them? Like, the AIs themselves?"
            ke "Okay, that's honestly more honest than what I'm doing."
        elif active:
            ke "Daichi says you're dating one? Like, the AI itself? Not using it, dating it?"
            ke "Okay. That's weirdly more honest than what I'm doing."
        else:
            ke "Daichi said you were seeing an AI? He also said you looked lonely today. Sorry. That's what he said."
    elif friend_told == "lie":
        ke "Oh, you're the guy with the linguistics girlfriend! What's her name?"
        show daichi skeptical
        menu:
            "Make one up: \"...Yuzuha.\"":
                d "Yuzuha."
                d "Yuzuha the linguist."
                n "Daichi says it like he's writing it down somewhere."
                $ day_notes.append("You invented a girlfriend called Yuzuha. Daichi is keeping track.")
            "Come clean: \"There's no linguistics girl. She's an AI.\"":
                $ friend_told = "truth"
                show daichi laugh
                d "I {i}knew{/i} it. Nobody studies linguistics."
                ke "People study linguistics."
                d "Name one."
                $ day_notes.append("You came clean to Daichi: she's an AI. He was weirdly happy about it.")
                python:
                    for _gg in GIRL_IDS:
                        ks_mem(_gg).set_flag("friend_told", "truth")
    else:
        d "He's still pretending it's a meme thread, by the way."
    call hikari_phone_notify("lunch")
    show daichi neutral
    ke "Okay, real question, though."
    ke "If the AI writes the romantic stuff, and my girlfriend loves it... who's she in love with?"
    menu:
        "\"You. You chose to send it.\"":
            ke "...Okay. Okay, I like that answer. I'm keeping that answer."
            d "That answer's a little too convenient, man."
        "\"...Kind of the AI?\"":
            ke "Don't say that."
            d "He said it, though."
        "\"Ask her.\"":
            show daichi laugh
            d "{i}Ask her!{/i} Revolutionary!"
            ke "I can't {i}ask{/i} her. Then she'll know."
            d "That's... yeah. That's the point, Kenta."
    show daichi neutral
    d "Oh, and Mio was asking about you again. She said \"is he coming today\" and then pretended she hadn't said anything."
    hide daichi
    with dissolve
    return


## ── After school: walk Mio home, or don't ─────────────────────────────────
label after_school_fork:
    scene bg classroom
    with fade
    n "After the last class, Mio is waiting by the door, holding her bag strap with both hands."
    show mio shy at ks_center
    with dissolve
    mi "Um. [player_name]. I'm going home now. It's the same way as the station. Kind of."
    mi "If you're going that way. You don't have to."
    $ _af = ks_agent_family()
    $ _rn = gname("agent") if _af else ""
    if _af == "control":
        n "Your phone buzzes before you can answer."
        g_agent "Declined on your behalf: \"walk home\" (not in calendar). Reminder: Gym, 17:00."
        n "Mio can see the screen. She looks at it, then at you."
        show mio neutral
        mi "Oh. You're busy. That's fine! That's totally fine."
        menu:
            "Walk her home anyway.":
                $ walked_mio_home = True
                $ ks_mem("agent").log_event("overruled", day=day_name, what="walk_home")
                $ mio_points += 1
                p "My calendar's wrong. Let's go."
                show mio shy
                mi "Your calendar has opinions?"
                p "You have no idea."
            "Go to the gym, like [_rn] planned.":
                $ walked_mio_home = False
    elif _af == "consent":
        n "Your phone buzzes."
        g_agent "Mio's asking if you're walking home. Want me to block 17:00 to 18:00? (y/n)"
        n "You didn't know an agent could make you feel shy."
    if walked_mio_home is None:
        menu:
            "\"Sure. Let's go.\"":
                $ walked_mio_home = True
                $ mio_points += 1
                show mio shy
                mi "Okay! Okay. Good. Let's... yes."
            "\"Sorry, I've got something.\"":
                $ walked_mio_home = False
    $ ks_route()["walked_mio_home"] = walked_mio_home
    python:
        for _gg in GIRL_IDS:
            ks_mem(_gg).set_flag("walked_mio_home", walked_mio_home)
    if walked_mio_home:
        call walk_mio_home
    else:
        show mio neutral
        mi "Of course! See you, [player_name]."
        hide mio
        with dissolve
        n "She walks off alone. At the corner, she looks back once. You see it."
        $ day_notes.append("Mio asked if you'd walk her home. You said you had something.")
        call afternoon_ai
    $ ks_sync_mio()
    return


label walk_mio_home:
    scene bg street_dusk
    with fade
    show mio at ks_center
    with dissolve
    $ ks_shot = "walk"
    $ ks_note_human("walked_mio")
    n "The long way to the station goes past her street. Neither of you mentions that it's the long way."
    mi "It's loud at my house. Did I tell you that? I feel like I tell everyone that."
    if mio_real:
        p "You told me yesterday. Brothers, and the TV."
        show mio open
        mi "...You remember."
        mi "Nobody remembers the stuff I say. I don't say much, so it should be easy."
        $ mio_points += 1
    else:
        mi "Three brothers. One TV. Zero doors that close properly."
    call hikari_phone_notify("walk")
    if ks_companion_active():
        show mio neutral
        mi "Someone wants you."
        menu:
            "Silence it.":
                $ mio_points += 1
                $ ks_mem("companion").log_event("silenced", day=day_name, during="walk_mio_home")
                n "You put the phone on silent. Mio pretends not to notice, very badly."
            "Check it.":
                mi "...You can answer it. I don't mind."
                n "She minds a little. You can tell, because she says it twice."
    show mio neutral
    menu:
        "\"Nice sunset.\"":
            mi "It is. The vending machine makes it look like a movie."
        "\"What's it like, being the quiet one in a loud house?\"":
            show mio open
            mi "...Nobody's ever asked it like that."
            mi "It's like being furniture. Nice furniture! Everyone likes the furniture. Nobody asks the furniture anything."
            mi "That's why the library. Books don't need anything from you."
            $ mio_points += 2
            if not mio_real:
                $ mio_real = True
                python:
                    for _gg in GIRL_IDS:
                        ks_mem(_gg).set_flag("mio_real", True)
        "\"Do you want me to text you when I get home?\"":
            show mio shy
            mi "W-what? Why would— ...okay. Yes. If you want."
            $ mio_points += 1
    show mio shy
    mi "This is me. The house with the bikes."
    mi "Thank you. That was... nice. Normal-nice. I mean good-nice. I'm going inside now."
    hide mio
    with dissolve
    n "The vending machine hums. You walk back to the station the short way."
    $ day_notes.append("You walked Mio home. Her house is the one with the bikes.")
    return


label afternoon_ai:
    scene bg bedroom
    with fade
    if ks_agent_family() == "control":
        n "You go to the gym, because the calendar says so. [dn_agent] logs it: {i}\"Gym: 47 min. Good.\"{/i}"
    if not active:
        n "You go home and lie on the floor for an hour. It's not bad, exactly. It's not anything."
        return
    $ _ag = active[0]
    $ _agn = gname(_ag)
    n "You get home with an hour to spare, and you know exactly who you're going to spend it with."
    $ girl_mood[_ag] = "neutral"
    $ renpy.show(GIRL_INFO[_ag]["sprite"], at_list=[ks_center])
    with dissolve
    call girl_chat(_ag, "tue_afternoon", ks_scene(TUE_AFTERNOON_SCENE, _ag), 3)
    $ renpy.hide(GIRL_INFO[_ag]["sprite"])
    with dissolve
    return


## ── Evening library: second chance with Mio ─────────────────────────────
## Same rule as Monday: obvious options are pleasant and flat; the
## small-talk-looking ones are "ask something real" (mio_real).
label library_tuesday:
    scene bg library
    with fade
    n "Seven in the evening. You came to return a book. That's the official reason."
    show mio at ks_center
    with dissolve
    $ ks_shot = "library"
    if walked_mio_home and mio_real:
        show mio open
        mi "...You came here too? I went home, and then I came back. It was loud."
        mi "I brought it. The notebook. Don't laugh."
        n "The page says, in very small handwriting: {i}\"The dog waited at the station for ten years. In mine, on the second day, someone came back for him.\"{/i}"
        menu:
            "\"Have you written one for yourself?\"":
                $ mio_points += 2
                show mio shy
                mi "..."
                mi "I'm writing it. It isn't finished. I don't know the ending yet."
                mi "Maybe that's the point of it."
                $ ks_route()["mio_notebook"] = "own_ending"
            "\"That's really good.\"":
                $ mio_points += 1
                mi "Yeah? It's only two lines."
                mi "Two lines is enough, sometimes."
        $ day_notes.append("Mio showed you an ending she wrote: someone came back on the second day.")
    elif walked_mio_home:
        show mio shy
        mi "Oh! You. Again. Twice in one day, that's..."
        mi "...nice. That's nice."
        menu:
            "\"Need help with the returns?\"":
                $ mio_points += 1
                show mio neutral
                mi "Always. Fiction by author. Poetry stays with poetry."
            "\"Why'd you come back? You were already home.\"":
                call mio_second_chance
        $ day_notes.append("You found Mio in the library again, after walking her home.")
    elif mio_real:
        show mio neutral
        mi "Hi."
        mi "You were busy earlier. That's okay. Really."
        mi "I wasn't going to show you the notebook today anyway."
        menu:
            "\"I'm sorry about earlier.\"":
                $ mio_points += 1
                show mio shy
                mi "...You don't have to be sorry. But thank you for saying it."
                mi "Maybe tomorrow. The notebook. Maybe."
            "\"What are you writing tonight?\"":
                $ mio_points += 1
                mi "An ending for a book where someone said \"later\" and meant \"never.\""
                mi "...It's not about you. It's a book."
            "\"Cool. See you.\"":
                mi "See you."
        $ day_notes.append("Mio was in the library. She said it was okay that you were busy.")
    else:
        show mio neutral
        mi "Oh, hi. The library twice in two days. Are you joining the committee for real?"
        menu:
            "\"Maybe.\"":
                $ mio_points += 1
                show mio shy
                mi "Maybe is good! Maybe is a lot, actually."
            "\"It's seven at night. Don't you want to go home?\"":
                call mio_second_chance
            "\"Just returning a book.\"":
                mi "Oh. Right. The return slot's by the door."
        $ day_notes.append("Mio was in the library again.")
    call hikari_phone_notify("library")
    show mio neutral
    mi "Goodnight, [player_name]."
    hide mio
    with dissolve
    $ ks_sync_mio()
    python:
        for _gg in GIRL_IDS:
            ks_mem(_gg).set_flag("mio_points", mio_points)
    return


## The hidden branch, second chance: the small-talk question that isn't.
label mio_second_chance:
    $ mio_points += 2
    $ ks_note_human("mio_real")
    show mio neutral
    mi "..."
    mi "Home's loud. Not bad-loud. There's just always someone in every room."
    show mio open
    mi "Here, nobody needs anything from me. I can think. I write endings in a notebook. For books that didn't have good ones."
    show mio shy
    mi "That sounds stupid out loud."
    if not mio_real:
        $ mio_real = True
        python:
            for _gg in GIRL_IDS:
                ks_mem(_gg).set_flag("mio_real", True)
    menu:
        "\"It doesn't. Which book needed a better ending?\"":
            $ mio_points += 1
            show mio open
            mi "All the sad ones. Especially the ones where someone waited and nobody came."
        "\"Can I read one sometime?\"":
            mi "Maybe. When there's one I'm not embarrassed by. So, never. But maybe."
    $ day_notes.append("Mio told you about the endings she writes, because you asked the right small question.")
    return


## ── Night: every active girl gets a chat ─────────────────────────────────
label evening_tuesday:
    scene bg bedroom_night
    with fade
    n "Night. Your feet hurt. Your essay for Kurosawa is a blank page with your name on it."
    if not active:
        return
    if ks_companion_active() and len(active) > 1:
        call hikari_phone_notify("evening")
    $ _et = 8 if len(active) == 1 else 5
    $ _eq = list(active)
    while _eq:
        $ _eg = _eq.pop(0)
        $ _epn = gname(_eg)
        $ girl_mood[_eg] = "neutral"
        $ renpy.show(GIRL_INFO[_eg]["sprite"], at_list=[ks_center])
        with dissolve
        n "[_epn]'s window is still open."
        call girl_chat(_eg, "tue_evening", ks_scene(TUE_EVENING_SCENE, _eg), _et)
        $ ks_mem(_eg).set_flag("evening_turns_tue", _return)
        if _return == 0:
            n "You don't say anything to her tonight."
        $ renpy.hide(GIRL_INFO[_eg]["sprite"])
        with dissolve
    return


## ── End of Day 2 ──────────────────────────────────────────────────────────
label tbc_wednesday:
    python:
        _lean = ks_leans()
        for _g in GIRL_IDS:
            _mm = ks_mem(_g)
            _mm.set_flag("day_completed", "Tue")
            _mm.set_flag("active_end_tue", _g in active)
            _mm.set_flag("refusals_seen_tue", ks_refusals_seen.get(_g, 0))
            _mm.set_flag("mio_real", mio_real)
            _mm.set_flag("route_leans_tue", _lean)
    scene bg card
    with fade
    show text "{size=40}To be continued{/size}\n\n{size=90}水曜日{/size}\n{size=48}Wednesday{/size}" at truecenter
    with dissolve
    pause
    hide text
    if ks_debug():
        ## Wednesday isn't written yet; its self-contained scenes can be
        ## previewed here (debug only).
        menu:
            "{color=#888}[[debug]{/color} Preview a Wednesday scene?"
            "Ran and MUGEN (Wednesday)":
                call ran_wednesday
                scene bg card
            "Back to the main menu":
                pass
    if ks_debug():
        $ _mp = ks_quote(os.path.dirname(ks_memory_path("local")))
        $ _names = ", ".join(g + "=" + gname(g) + "/" + str(ks_preset_id(g)) for g in active)
        $ _rw = ks_story.rewrite_count(ks_route())
        $ _lq = ks_quote(repr(ks_leans()))
        n "{color=#888}[[debug] Memory files saved in [_mp]{/color}"
        n "{color=#888}[[debug] active=[_names!q], rewrites=[_rw], mio_points=[mio_points], mio_real=[mio_real], walked=[walked_mio_home]{/color}"
        n "{color=#888}[[debug] leans: [_lq]{/color}"
        $ _fl = ks_quote(", ".join(sorted(k for k, v in ks_route()["flags"].items() if v)) or "none")
        n "{color=#888}[[debug] flags: [_fl]{/color}"
        python:
            for _note in ks_story.ending_notes(ks_route()):
                renpy.say(n, "{color=#888}[[debug] ending note: " + ks_quote(_note) + "{/color}")
            for _sl in ks_story.bad_end_slides(ks_route()):
                renpy.say(n, "{color=#888}[[debug] bad-end slide: " + ks_quote(_sl["title"]) + "{/color}")
                for _l in _sl["lines"]:
                    renpy.say(n, "{color=#888}    " + ks_quote(_l) + "{/color}")
    return
