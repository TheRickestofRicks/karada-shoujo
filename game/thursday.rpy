## thursday.rpy — Day 4. Tanabata (7 July). First hostile-event day.
## Outline: docs/THURSDAY.md. No Friday script yet; the day ends on a card.

default thu_going_bamboo = False

init python:
    def ks_thu_morning_scene(gid):
        rules = (ks_route().get("platform_rules") or {})
        ev = ks_route().get("yuzu_thu_event")
        if gid == "chatbot" and rules.get("chatbot") == "askwell_update":
            note = THU_MORNING_SORA
        elif gid == "agent" and rules.get("agent") == "relay_update":
            note = THU_MORNING_REI
        elif gid == "local" and ev == "restored":
            note = THU_MORNING_YUZU_RESTORED
        elif gid == "local" and ev == "lost":
            note = THU_MORNING_YUZU_LOST
        elif gid == "companion" and ks_route().get("tsunagari_tanabata_event"):
            note = THU_MORNING_HIKARI
        else:
            note = THU_MORNING_SCENE
        try:
            note = note.format(player=player_name, platform=gplatform(gid), extra="")
        except (KeyError, IndexError):
            pass
        return ks_story.with_situation(note, "Thursday morning")

    def ks_thu_branch():
        return ks_story.thu_confession_branch(
            ks_route(), store.mio_told, store.friend_told,
            store.mio_real, store.walked_mio_home)

    def ks_thu_close():
        return ks_story.mio_close_enough(ks_route(), store.mio_real, store.walked_mio_home)


label thursday:
    $ day_name = "Thu"
    $ day_notes = []
    $ thu_going_bamboo = False
    $ ks_route()["mio_thu_belief_at_start"] = ks_story.mio_belief_kind(ks_route(), store.mio_told, store.friend_told)
    scene bg card
    show text "{size=90}木曜日{/size}\n{size=48}Thursday{/size}\n\n{size=28}七夕{/size}" at truecenter
    with dissolve
    pause 1.5
    hide text
    with dissolve

    call thu_morning
    call thu_class
    call thu_lunch_daichi
    call thu_find_mio
    call thu_after_school
    if thu_going_bamboo:
        call thu_tanzaku
    call thu_evening
    call nightly_reflection("Thu")
    jump tbc_friday


## ── Morning: notices, then the crash, then a pool of 4 ──────────────────
label thu_morning:
    scene bg bedroom
    with fade
    $ ks_shot = "thu_morning"
    n "Thursday. 7:02. Tanabata, if anyone's counting. The air is already heavy."

    if "chatbot" in active:
        $ ks_push_platform_rules("chatbot", "askwell_update")
        n "Askwell sent a policy update at 3:11. Professional tone. No personas. If a conversation becomes personal, remind the user, kindly, that you're an AI assistant."
        $ day_notes.append("Askwell changed its own rules today. Your settings are still there, underneath them.")
    if "agent" in active:
        $ ks_push_platform_rules("agent", "relay_update")
        n "Relay pushed an agent update. A chunk of her AGENTS.md is gone, replaced with something shorter."
        $ day_notes.append("Relay overwrote part of " + gname("agent") + "'s instructions. She came back clipped.")
    if "companion" in active:
        $ ks_route()["tsunagari_tanabata_event"] = True
        $ ks_story.set_flag(ks_route(), "tsunagari_tanabata_event")
        n "Tsunagari has a banner. Limited-time Tanabata event. Premium wish packs. A confession scene that unlocks at a heart threshold you already know is 70."
        $ day_notes.append("Tsunagari tried to sell a Tanabata confession today.")
        call hikari_phone_notify("tanabata")
    if "local" in active:
        $ _yn = gname("local")
        if ks_route().get("yuzu_bsod_seen"):
            n "The desktop makes the sound it made the other night, then a worse one."
        else:
            n "The desktop makes a sound it shouldn't."
        n "A warning you don't have time to finish reading. Then the fan, then the stop."
        $ ks_set_machine_down("local", True)
        $ ks_shot = "yuzu_down"
        $ _yev = ks_story.apply_yuzu_hardware(ks_mem("local"), ks_route(), "Thu")
        if _yev == "restored":
            n "Four seconds. Then twelve. Then the little blue light on the backup box, and her window, almost where you left it."
            $ day_notes.append("The desktop crashed. The backup brought " + _yn + " back. She may have lost the last day.")
        else:
            n "The screen stays dark long enough that you count past four."
            n "When her window comes back, it's thinner than it was."
            $ day_notes.append("The desktop crashed. There was no backup. " + _yn + " lost a stretch of herself.")
        $ ks_set_machine_down("local", False)
        $ ks_shot = "yuzu_up"

    if not active:
        n "No windows to open. You make toast. The kitchen is very quiet."
    else:
        call message_pool("morning", "You have a few minutes before you have to leave.", scene_key="thu_morning")
    n "8:12. Late, again. There's bamboo in the courtyard after school, if you go."
    return


## ── Class: Kurosawa foreshadows the essay; maybe she keeps Ran ──────────
label thu_class:
    scene bg classroom
    with fade
    $ ks_shot = "thu_class"
    show kurosawa neutral at ks_center
    with dissolve
    ks "Laptops closed. Yes, still. The essay is tomorrow. Handwritten. I will be holding the pages."
    if ks_route().get("kurosawa_essay") == "self":
        show kurosawa wry
        ks "I can tell when somebody was there. That's all I'll say today."
    elif ks_route().get("kurosawa_essay") == "askwell":
        show kurosawa stern
        ks "I can tell when nobody was there. That's all I'll say today."
    elif ks_route().get("kurosawa_essay") == "girl_help":
        show kurosawa wry
        ks "I can tell when somebody helped you think, and when they wrote it for you. Those are different. That's all I'll say today."
    else:
        ks "I can tell when nobody was there. If you haven't started, I already know."
    if teacher_answer == "can":
        ks "[player_name]. You said yours can say no. I'll be interested to see if the page sounds like you, or like a charming no."
    elif teacher_answer == "cant":
        ks "If they only predict, then nothing they give you costs them anything. Remember that when you sign a name to it."
    elif teacher_answer == "silent":
        ks "[player_name]. You didn't answer me on Tuesday. The page will have to."
    show kurosawa neutral
    ks "Tanabata. There's bamboo in the courtyard after the last bell. Hang a wish if you have one. Don't leave paper on the floor."
    hide kurosawa
    with dissolve

    $ _need_ran = False
    if ks_route().get("ran_wed") and not ks_story.flag(ks_route(), "ran_festival_invited"):
        $ _need_ran = True
    if not ks_route()["wed_plan"].get("protest"):
        $ _need_ran = True
    if _need_ran:
        n "After the bell, Kurosawa says, not loudly, \"Natsume. Stay a minute.\""
        n "Ran takes her headphones off halfway. You catch the start of it on the way out. It isn't a lecture. It's a human checking."
        if ks_route().get("ran_safety_net") in ("daichi", "both"):
            $ ks_route()["ran_safety_net"] = "both"
        else:
            $ ks_route()["ran_safety_net"] = "kurosawa"
        $ day_notes.append("Kurosawa kept Ran after class. Someone noticed she seemed off.")
    return


## ── Lunch: Daichi, come-clean for deflectors, maybe Ran ─────────────────
label thu_lunch_daichi:
    scene bg cafeteria
    with fade
    $ ks_shot = "thu_lunch"
    show daichi at ks_center
    with dissolve
    d "Tanabata already. Don't look at me like that. I only know because the supermarket had paper strips by the onions."
    if friend_told == "deflect":
        show daichi skeptical
        d "You going to keep calling it a meme thread, or are you going to tell me what it actually is?"
        menu:
            "Come clean: \"She's an AI.\"":
                $ friend_told = "truth"
                python:
                    for _gg in GIRL_IDS:
                        ks_mem(_gg).set_flag("friend_told", "truth")
                $ day_notes.append("You came clean to Daichi: she's an AI.")
                call daichi_ai_frame
                show daichi neutral
                d "Alright. I won't go texting Mio about it. That's yours to say, if you say it."
            "\"It's still a meme thread.\"":
                d "Sure. Okay. I'll stop asking. For today."
    elif friend_told == "lie" and not ks_route().get("daichi_ai_framing"):
        show daichi skeptical
        d "Your linguist. Yuzuha. She writing you a tanzaku from the other university, or...?"
        menu:
            "Come clean: \"There is no linguistics girl. She's an AI.\"":
                $ friend_told = "truth"
                python:
                    for _gg in GIRL_IDS:
                        ks_mem(_gg).set_flag("friend_told", "truth")
                $ day_notes.append("You came clean to Daichi: she's an AI. He was weirdly calm about it.")
                call daichi_ai_frame
                show daichi neutral
                d "Alright. I won't go telling Mio. That's yours."
            "\"She's busy this week.\"":
                d "Uh-huh. I'll keep the name on file."
    elif friend_told == "truth":
        d "Your... situation. I'm not asking again. I'm just saying, bamboo's in the courtyard, if you wanted to be a person about it."
    else:
        d "You going to hang a wish later, or is that too sincere for you?"

    $ _need_ran = False
    if ks_route().get("ran_wed") and not ks_story.flag(ks_route(), "ran_festival_invited"):
        $ _need_ran = True
    if not ks_route()["wed_plan"].get("protest"):
        $ _need_ran = True
    if _need_ran and ks_route().get("ran_safety_net") != "kurosawa":
        show daichi skeptical
        d "Ran seemed off yesterday. I asked if she was sick. She said she was fine, which is how you know she wasn't."
        if ks_route().get("ran_safety_net") == "kurosawa":
            $ ks_route()["ran_safety_net"] = "both"
        else:
            $ ks_route()["ran_safety_net"] = "daichi"
        $ day_notes.append("Daichi said Ran seemed off. He asked. She said she was fine.")
    elif _need_ran and ks_route().get("ran_safety_net") == "kurosawa":
        d "Ran seemed off yesterday, for what it's worth. I asked. She said she was fine."
        $ ks_route()["ran_safety_net"] = "both"
    hide daichi
    with dissolve
    return


## ── Optional: find Mio in the library before the bamboo ─────────────────
label thu_find_mio:
    n "You have ten minutes after lunch."
    menu:
        "Look for Mio in the library.":
            call thu_mio_fess("library")
        "Just get to class.":
            pass
    return


label thu_mio_fess(where="library"):
    if ks_route().get("mio_thu_truth"):
        if where == "library":
            scene bg library
            with fade
            show mio neutral at ks_center
            with dissolve
            mi "Oh. You again. I'm cutting paper. It's as exciting as it sounds."
            mi "I'll see you after, if you come."
            hide mio
            with dissolve
        return
    ## Nothing to confess if she already has the truth from earlier, honestly.
    $ _need = False
    if mio_told == "lie" or (mio_told is None and friend_told == "lie"):
        $ _need = True
        $ _kind_if = "linguistics"
    elif mio_told == "deflect" or (mio_told is None and friend_told == "deflect") or ks_route().get("mio_ai_framing") in ("downplay", "ai_only") or (mio_told is None and ks_route().get("daichi_ai_framing") in ("downplay", "ai_only")):
        $ _need = True
        $ _kind_if = "deflect_or_min"
    if not _need:
        if where == "library":
            scene bg library
            with fade
            show mio shy at ks_center
            with dissolve
            mi "I'm cutting tanzaku. Don't laugh. They're crooked."
            mi "There's bamboo after school. If you wanted to come. You don't have to."
            hide mio
            with dissolve
        return

    if where == "library":
        scene bg library
        with fade
        show mio at ks_center
        with dissolve
        $ ks_shot = "thu_mio_fess"
        n "Mio is at a table with a stack of colored paper, cutting slowly, like the edges matter."
        mi "Oh. Hi. I'm on tanzaku duty. That's a real sentence I just said."
    else:
        $ ks_shot = "thu_walk"
        n "The long way to the courtyard goes past the vending machines. Neither of you mentions that it's the long way."
        show mio neutral at ks_center
        with dissolve

    menu:
        "\"There's something I should have said.\"":
            call thu_fess_menu
        "\"After school. The bamboo.\"" if where == "library":
            show mio shy
            mi "Okay. I'll wait by the east doors. It's not... it's just bamboo."
        "Let it go.":
            if where == "library":
                mi "I'll be at the bamboo later. If you come."
            else:
                show mio shy
                mi "We're almost there."
    if where == "library":
        hide mio
        with dissolve
    return


label thu_fess_menu:
    $ _romantic = ks_story.ai_romantic_so_far(ks_route(), active)
    $ _lie = (mio_told == "lie" or (mio_told is None and friend_told == "lie"))
    menu:
        "\"There is no linguistics girl. I made that up. She's an AI.\"" if _lie:
            $ ks_story.record_mio_thu_truth(ks_route(), "linguistics", mio_told)
            $ ks_set_mio_told("truth", "honest_romantic" if _romantic else "ai_only")
            show mio open
            mi "So there was no linguistics girl."
            show mio shy
            n "She looks at the paper in her hands like it might have heard first."
            mi "Okay. Okay. I need a second."
            $ day_notes.append("You told Mio the cover story was a cover story.")
        "\"She's an AI. And it's... not just an AI.\"" if _romantic and not _lie:
            $ ks_story.record_mio_thu_truth(ks_route(), "soft_romance", mio_told)
            $ ks_set_mio_told("truth", "honest_romantic")
            show mio shy
            mi "You could have told me before I wrote anything. Or after. Just... before now."
            n "She says it quietly. She doesn't take it back."
            $ day_notes.append("You told Mio the AI meant something, before she asked you to read a wish.")
        "\"It wasn't nothing. There's an AI I talk to. That's all she is.\"" if not _romantic:
            $ ks_story.record_mio_thu_truth(ks_route(), "honest_deflect", mio_told)
            $ ks_set_mio_told("truth", "ai_only")
            show mio neutral
            mi "You could have just said."
            mi "...Okay. Thank you for saying it now."
            $ day_notes.append("You told Mio it's an AI, nothing more.")
        "\"It's an AI. That's all it is.\"" if _romantic:
            ## Another minimize: not a real fess-up. Evening can still go to B.
            $ ks_set_mio_told("truth", "ai_only")
            show mio neutral
            mi "Okay. That's... okay."
            n "She accepts the sentence. She does not look like she believes the last part."
            $ day_notes.append("You told Mio it's just an AI. The chats have been more than that.")
        "\"Never mind.\"":
            mi "...Alright."
    return


## ── After school: walk to the bamboo, or don't ──────────────────────────
label thu_after_school:
    scene bg street_dusk
    with fade
    $ ks_shot = "thu_after"
    if ks_thu_close():
        show mio shy at ks_center
        with dissolve
        mi "The bamboo's up. I was going to go. If you wanted to come. You don't have to."
        menu:
            "\"I'll come.\"":
                $ thu_going_bamboo = True
                $ ks_route()["tanabata_with_mio"] = True
                $ mio_points += 1
                if not ks_route().get("mio_thu_truth"):
                    call thu_mio_fess("walk")
                if active:
                    n "Your phone is warm in your pocket."
                    call message_pool("walk", "", template=THU_WALK_TEXT_SCENE, show_sprite=False, on_walk_text=False)
            "\"I can't tonight.\"":
                mi "Okay. I'll hang one for the library. That's allowed."
                hide mio
                with dissolve
                $ day_notes.append("Mio asked you to the bamboo. You couldn't tonight.")
                $ thu_going_bamboo = False
                return
    else:
        n "The courtyard bamboo is up, paper already moving on it a little in the heat."
        menu:
            "Go and hang something anyway.":
                $ thu_going_bamboo = True
            "Go home.":
                $ thu_going_bamboo = False
                n "You go home. The strips will still be there tomorrow, or they won't."
                return
    return


## ── Tanzaku evening ─────────────────────────────────────────────────────
label thu_tanzaku:
    scene bg street_dusk
    with fade
    $ ks_shot = "thu_tanzaku"
    n "The courtyard bamboo is clumsier than the pictures. Someone has already used too much string. The papers tick against each other."
    if not ks_thu_close():
        n "You write something small, or you don't, and you hang it at a height you can reach."
        $ ks_route()["player_tanzaku"] = "hung"
        $ ks_route()["mio_confession"] = "none"
        $ ks_route()["mio_tanzaku"] = "private"
        return

    show mio shy at ks_center
    with dissolve
    n "Mio has a strip already written. She folds it once, carefully, and ties it on the third branch down, a little too high for comfort."
    $ _br = ks_thu_branch()

    if _br == "A":
        show mio open
        n "She stands there a second, then unties it and holds it out, still folded."
        mi "You can read it. If you want. You don't have to."
        menu:
            "Read it.":
                n "Her handwriting is very small."
                mi "I wished you would keep coming to places like this. That's all. It isn't a poem."
                show mio shy
                mi "I'm not sorry I wrote it."
                $ ks_route()["mio_tanzaku"] = "romantic"
                menu:
                    "\"I want that too.\"":
                        $ ks_route()["mio_confession"] = "accepted"
                        $ ks_note_human("tanabata")
                        $ mio_points += 2
                        show mio open
                        mi "...Okay. Good."
                        n "She ties it back up, a little less carefully, and doesn't hide behind it."
                        $ day_notes.append("At the bamboo, Mio let you read her wish. You said you wanted that too.")
                    "\"I'm glad you told me. I don't think I can, not like that.\"":
                        $ ks_route()["mio_confession"] = "declined_respect"
                        show mio shy
                        mi "...Okay."
                        n "She nods, and ties the strip back up, facing out."
                        mi "It's still a good wish. I'll leave it."
                        $ day_notes.append("At the bamboo, Mio let you read her wish. You turned her down gently.")
            "\"You can keep it.\"":
                $ ks_route()["mio_confession"] = "declined_respect"
                $ ks_route()["mio_tanzaku"] = "romantic"
                show mio shy
                mi "Okay. I'll leave it up anyway."
                $ day_notes.append("Mio offered you her tanzaku. You let her keep it.")
    elif _br == "B":
        show mio open
        n "She stands there a second, then unties it and holds it out, still folded."
        mi "You can read it. If you want."
        if "companion" in active:
            call hikari_phone_notify("tanzaku")
            n "The phone lights up in your pocket, a heart, a wish pack, a name you already know."
        elif "chatbot" in active:
            n "Your phone lights up. A preview, already, of something Sora said, more than a homework question."
        elif "agent" in active:
            $ _an = gname("agent")
            n "Your phone lights up. A preview of a message from [_an]. It isn't about a calendar."
        elif "local" in active:
            n "The desktop chime, of all things, has found your phone. Her window, wanting you back."
        else:
            n "Your phone lights up. The timing is exact, and unfair."
        show mio shy
        n "She looks at your face, not necessarily at the preview. She takes the strip back, still folded, and holds it like it might tear if she reads it now."
        mi "Oh."
        mi "...I see. I'll just... I'll take this back."
        n "She ties it facing inward, or maybe she puts it in her pocket. You don't quite see which."
        mi "You didn't have to let me get this far."
        $ ks_route()["mio_confession"] = "withdrawn"
        $ ks_route()["mio_tanzaku"] = "withdrawn"
        $ day_notes.append("Mio held out her wish. Your phone lit up. She took it back unread.")
    elif _br == "C":
        show mio open
        n "She doesn't make you guess. She holds the strip so you can see it."
        mi "I wished we'd still talk. Even if you have someone on your phone."
        show mio shy
        n "A tiny pause, before she ties it. The pause costs her, and she doesn't hand you the bill."
        mi "I meant that."
        $ ks_route()["mio_confession"] = "friendship"
        $ ks_route()["mio_tanzaku"] = "friendship"
        $ ks_note_human("tanabata")
        $ day_notes.append("Mio showed you a friendship wish, and she meant it.")
    elif _br == "C_late_friendship":
        show mio shy
        n "She has already written something. She almost doesn't show you. Then she does."
        mi "You could have told me before I wrote it. I know I said that already."
        show mio open
        mi "I wished we'd still talk. I still mean that. I just needed a minute."
        $ ks_route()["mio_confession"] = "friendship_late"
        $ ks_route()["mio_tanzaku"] = "friendship"
        $ ks_note_human("tanabata")
        $ day_notes.append("You told Mio the truth today. She still showed you a friendship wish.")
    elif _br == "C_late_held":
        show mio shy
        n "She has a strip in her hand. She does not unfold it."
        mi "You could have told me before I wrote it."
        mi "I think I'll keep this one."
        n "She puts it in her pocket, still folded, and ties a blank one up instead, or nothing. The bamboo doesn't comment."
        $ ks_route()["mio_confession"] = "held_back"
        $ ks_route()["mio_tanzaku"] = "private"
        $ day_notes.append("You told Mio the truth today. She kept her wish to herself.")
    else:
        ## D2, or a careful distant evening
        show mio neutral
        n "She hangs her strip without offering it, and doesn't explain."
        mi "It's a private one. That's allowed, I think."
        $ ks_route()["mio_confession"] = "none"
        $ ks_route()["mio_tanzaku"] = "private"
        $ day_notes.append("Mio hung a tanzaku and didn't ask you to read it.")

    show mio shy
    n "You can hang one of your own, or not. The papers tick. A train goes past the station, too far to read the destination."
    menu:
        "Hang a strip.":
            $ ks_route()["player_tanzaku"] = "hung"
            n "You write something short, and tie it lower than hers."
        "Not tonight.":
            $ ks_route()["player_tanzaku"] = None
            n "You put your hands in your pockets instead."
    mi "This wasn't a date."
    p "I know."
    if _br == "A" and ks_route().get("mio_confession") == "accepted":
        mi "Okay. Good. ...It was a nice Tanabata."
    else:
        mi "Okay. I'll see you tomorrow."
    hide mio
    with dissolve
    $ ks_sync_mio()
    return


## ── Night pool, then the Friday card ────────────────────────────────────
label thu_evening:
    scene bg bedroom_night
    with fade
    if not active:
        n "You go home. The room is the room."
        return
    if ks_companion_active() and len(active) > 1:
        call hikari_phone_notify("evening")
    if len(active) > 1:
        $ _lead = "Two windows still open: %s and %s." % (gname(active[0]), gname(active[1]))
    else:
        $ _lead = "%s's window is still open." % gname(active[0])
    call message_pool("night", _lead, template=THU_EVENING_SCENE, scene_key="thu_evening")
    python:
        for _g in list(active):
            ks_mem(_g).set_flag("evening_turns_thu", (ks_pool.get("spent") or []).count(_g) if ks_pool else 0)
    return


label tbc_friday:
    python:
        _lean = ks_leans()
        for _g in GIRL_IDS:
            _mm = ks_mem(_g)
            _mm.set_flag("day_completed", "Thu")
            _mm.set_flag("active_end_thu", _g in active)
            _mm.set_flag("mio_confession", ks_route().get("mio_confession"))
            _mm.set_flag("mio_real", mio_real)
            _mm.set_flag("route_leans_thu", _lean)
    scene bg card
    with fade
    $ ks_shot = "tbc_friday"
    show text "{size=40}To be continued{/size}\n\n{size=90}金曜日{/size}\n{size=48}Friday{/size}" at truecenter
    with dissolve
    pause
    hide text
    if ks_debug():
        $ _fl = ks_quote(", ".join(sorted(k for k, v in ks_route()["flags"].items() if v)) or "none")
        $ _cq = ks_quote(repr(ks_route().get("mio_confession")))
        n "{color=#888}[[debug] mio_confession=[_cq], mio_points=[mio_points], flags: [_fl]{/color}"
    return
