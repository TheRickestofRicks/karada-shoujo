## wednesday.rpy — Day 3. A quiet day: no hostile events, nothing that
## punishes the player. (Thursday is the next event day.)
##
## Flow: platform memory updates (summarizer) + Yuzu's Hearth harness
##       → optional Yuzu upgrade day (skips classes: no library, no not-date)
##       → morning chat (schedule-aware girls see today's calendar)
##       → classes: Ran invites you to the AI protest (if on good terms)
##       → phone break → lunch: Mio in the library asks about the bookstore
##       → optional "not a date" at Kanade Books (three chances to text;
##         staying present unlocks a deeper beat each time)
##       → 17:30 AI protest downtown with Ran (label ran_wednesday)
##       → night chat with every active girl → nightly reflection
##       → jump thursday (no player-facing card; Thursday has its own title).
##
## The protest is after school on purpose: an upgrade-day player can still go
## (Ran texts the invite instead). See DESIGN.md "Wednesday".

default notdate_texts = 0
default notdate_present = 0

init python:
    def ks_wed_morning_scene(gid):
        extra = ""
        if gid in ks_route()["summarizer_slots"]:
            extra += "Your platform shipped a memory update overnight: older conversations now get summarized instead of forgotten. "
        if gid == "local" and ks_route()["yuzu_harness"]:
            extra += "{player} installed a harness called Hearth this morning, so you can see their calendar now. ".format(player=player_name)
        note = WED_MORNING_SCENE.format(name=gname(gid), player=player_name,
                                        platform=gplatform(gid), extra=extra)
        return ks_story.with_situation(note, "Wednesday morning")

    def ks_mio_ai_ref(gid):
        """How Mio refers to the one you're texting (she only knows what
        Daichi told her).

        Hook: a later scene should have Mio and Daichi compare notes, using
        mio_told / mio_daichi_consistent. Until then this still follows
        friend_told only.
        """
        if friend_told == "truth":
            return gname(gid)
        if friend_told == "lie":
            return "the linguistics girl"
        return None

    def ks_wed_plan(**kw):
        ks_route()["wed_plan"].update(kw)
        ks_set_schedule("Wednesday")


label wednesday:
    $ day_name = "Wed"
    $ day_notes = []
    $ ks_route()["wed_plan"] = {"school": True, "upgrade": False, "notdate": False, "protest": False}
    $ ks_set_schedule("Wednesday")
    scene bg card
    show text "{size=90}水曜日{/size}\n{size=48}Wednesday{/size}" at truecenter
    with dissolve
    pause 1.5
    hide text
    with dissolve

    scene bg bedroom
    with fade
    $ ks_shot = "wed_morning"
    n "Wednesday. 7:05. For once, you actually slept."
    call yuzu_bsod_hint

    ## ── The memory update: every app ships a summarizer the same week ──
    python:
        for _g in SUMMARIZER_SLOTS_WED:
            ks_install_summarizer(_g, "platform_update")
        _wed_upd = [g for g in active if g in SUMMARIZER_SLOTS_WED]
    if _wed_upd:
        n "Your phone has a little stack of update notes waiting."
        python:
            for _g in _wed_upd:
                renpy.say(app, SUMMARIZER_PATCH_NOTES[_g][1])
        $ day_notes.append("The apps all shipped the same update this week: longer memory.")
    elif not active:
        n "Three app updates are waiting on your phone. You don't open them."

    ## ── Yuzu: the Hearth harness (free; the upgrade day is separate) ──
    if "local" in active:
        $ _yn = gname("local")
        n "There's also a post going around the local-model forums: {i}Hearth v1.0: a harness that lets your local model read your calendar and set reminders.{/i}"
        n "It's free, it runs on the hardware [_yn] already has, and the README is mostly apologies."
        menu:
            "Install Hearth (she sees your schedule, like the app ones do)":
                $ ks_route()["yuzu_harness"] = True
                $ ks_mem("local").set_flag("hearth", True)
                $ ks_mem("local").log_event("hearth_installed", day=day_name)
                n "Twelve minutes, two dependency errors, one success message. Her window shows a small calendar icon now."
                $ day_notes.append("You installed Hearth. " + _yn + " can see your calendar now.")
            "Not today":
                n "You bookmark it. Maybe."

        ## ── Yuzu: the upgrade day (costs a day of classes) ──
        n "And the parts you've been eyeing are in stock: a second SSD, and a little used mini PC to keep a backup of her on."
        if ks_route().get("yuzu_bsod_seen"):
            n "The bluescreen the other night was four seconds. She came back fine."
        n "Doing it properly means the parts shop at ten, then the whole afternoon with a screwdriver. It means skipping classes. All of them."
        n "{size=22}(No library at lunch, no Mio. If anything's on after school, you could still make it.){/size}"
        menu:
            "Skip classes. Upgrade [_yn] today.":
                $ ks_wed_plan(school=False, upgrade=True)
            "Go to class. The parts will still be there.":
                pass

    ## ── Morning chat (shared pool of 4) ──
    if not active:
        n "No windows to open. You make toast. It's fine toast."
    else:
        python:
            for _wg in list(active):
                if ks_story.schedule_aware(ks_route(), _wg):
                    renpy.say(n, "{size=22}(%s can see today's calendar.){/size}" % gname(_wg))
        call message_pool("morning", "You have a few minutes before the day starts.")

    if ks_route()["wed_plan"].get("upgrade"):
        call wed_upgrade_day
    else:
        call wed_classes
        call phone_break("Wednesday, late morning", allow_talk=False)
        call wed_library
        if ks_route()["wed_plan"].get("notdate"):
            call wed_bookstore
        elif not ks_route()["wed_plan"].get("protest"):
            call wed_afternoon_ai
    if ks_route()["wed_plan"].get("protest"):
        call ran_wednesday
    elif ks_route()["ran_invited"] is False:
        n "{size=22}(Later, a clip of a protest downtown goes around. You think you see a lilac streak in the crowd. It's none of your business, and that's okay.){/size}"
    call evening_wednesday
    call nightly_reflection("Wed")
    jump tbc_thursday


## ── Classes: Ran asks you to the protest, if you're on good terms ───────
label wed_classes:
    scene bg classroom
    with fade
    n "Third period is a free study hall. Kurosawa is out. Somebody has drawn a very good cat on the whiteboard."
    show ran neutral at ks_center
    with dissolve
    call ran_invite_check("class")
    hide ran
    with dissolve
    return


## Ran's invite (in person at school, or by text on the upgrade day).
label ran_invite_check(how="class"):
    if ks_ran_good_terms():
        $ ks_route()["ran_invited"] = True
        if how == "class":
            ra "Hey. You."
            ra "There's a thing downtown after school. An AI protest. Signs, megaphones, the whole thing."
            show ran grin
            ra "I'm going to watch. For research. Purely anthropological."
            show ran neutral
            ra "You can come. If you want. Five-thirty, Ekimae plaza."
        else:
            n "Your phone buzzes. Ran. You don't remember giving her your number. You probably did."
            n "{i}\"you weren't in class. theres an AI protest downtown at 5:30, ekimae plaza. im going to watch. come if u want\"{/i}"
        menu:
            "\"Sure. I'll come.\"" if how == "class":
                $ ks_wed_plan(protest=True)
                ra "Cool. Don't wear anything with a logo on it."
            "Text back: \"I'll be there.\"" if how != "class":
                $ ks_wed_plan(protest=True)
                n "{i}\"cool. dont wear anything with a logo\"{/i}"
            "\"Can't today, sorry.\"" if how == "class":
                ra "No big deal. I'll tell you if anyone gets arrested."
                $ day_notes.append("Ran asked you to watch the AI protest with her. You couldn't make it.")
            "Text back: \"Can't today, sorry.\"" if how != "class":
                n "{i}\"np. ill tell u if anyone gets arrested\"{/i}"
                $ day_notes.append("Ran asked you to watch the AI protest with her. You couldn't make it.")
    else:
        $ ks_route()["ran_invited"] = False
        if how == "class":
            n "Ran's at the window seat with her headphones on, typing to her phone. When the bell goes, she leaves first."
        $ day_notes.append("Ran didn't talk to you today. Someone said there's a protest downtown after school.")
    return


## ── Lunch: Mio, the library again, and the bookstore ────────────────────
label wed_library:
    scene bg library
    with fade
    show mio neutral at ks_center
    with dissolve
    $ ks_shot = "wed_library"
    n "Lunch. The library is nearly empty. Mio is shelving a cart of new arrivals, reading the back of every single one."
    show mio shy
    mi "Oh! [player_name]. Hi. Third day in a row. People will start thinking you like books."
    show mio neutral
    if ks_route().get("walked_mio_home"):
        mi "Thank you again. For yesterday. The walk. I said thank you already. I'm saying it again."
    mi "Um. So. Kanade Books opens today. The big one by the station. Three floors. There's a poetry floor. A whole {i}floor{/i}."
    mi "I'm going after school. If you wanted to come. It's not a— it's just books. A normal amount of books."
    menu:
        "\"I'd like that.\"":
            $ ks_wed_plan(notdate=True)
            $ ks_note_human("notdate")
            $ mio_points += 1
            show mio shy
            mi "Okay! Okay. Quarter to four, by the station exit. It's not a date."
            p "It's not a date."
            mi "Good. I mean. Okay."
        "\"Can't today. Tell me what the poetry floor is like?\"":
            show mio neutral
            mi "I will. I'll take notes. Not weird notes. Normal notes."
            $ day_notes.append("Mio asked if you wanted to see the new bookstore. You couldn't today.")
    hide mio
    with dissolve
    $ ks_sync_mio()
    return


## ── The not-date at Kanade Books: three chances to text her ─────────────
## Staying present (phone away, or the stay option) unlocks a deeper beat
## each time: a book she loves, her house, a small admission, and — if you
## stayed through all three — a quiet shared moment. Texting interrupts
## the beat she was about to offer; she trails off or changes the subject.
## notdate_texts / notdate_present / mio_points are unchanged.
label wed_bookstore:
    scene bg bookstore
    with fade
    $ ks_shot = "bookstore"
    $ notdate_texts = 0
    $ notdate_present = 0
    $ ks_route()["notdate"] = {"went": True, "texts": 0, "present": 0, "texted": []}
    n "Kanade Books smells like new paper and the free coffee by the door. Mio stops just inside, like she needs a second."
    show mio open at ks_center
    with dissolve
    mi "...Three floors."
    if ks_companion_active():
        call hikari_phone_notify("bookstore")
    call notdate_moment(1, "Mio heads for the escalator. Your phone is warm in your pocket.", "Follow her up the escalator")
    if _return:
        call notdate_beat_book
    else:
        call notdate_interrupt(1)
    n "The second floor is quieter. Almost all of it is poetry."
    show mio open
    n "Mio is already halfway down an aisle, a slim volume open in her hands."
    call notdate_moment(2, "She's reading something under her breath.", "Ask her to read it out loud")
    if _return:
        call notdate_beat_house
    else:
        call notdate_interrupt(2)
    show mio neutral
    n "The top floor is a café. Mio buys two cocoas before you can argue, and slides one across the table."
    call notdate_moment(3, "She's turning the cup in her hands, looking at the station lights.", "Ask what she's writing this week")
    if _return:
        call notdate_beat_admission
        if notdate_present >= 3:
            call notdate_beat_quiet
    else:
        call notdate_interrupt(3)
    $ _nd = ks_route()["notdate"]
    $ _nd["texts"] = notdate_texts
    $ _nd["present"] = notdate_present
    $ _rk = ks_story.notdate_reaction_key(notdate_texts)
    if _rk == "present":
        show mio shy
        mi "You didn't check your phone once."
        mi "...I noticed. Sorry. I notice things. It was nice."
        $ mio_points += 1
        $ day_notes.append("At the bookstore with Mio, you didn't look at your phone once. She noticed.")
    elif _rk == "some":
        show mio neutral
        mi "Thanks for coming. Even with your phone. It's fine. I check mine too, when there's someone on it."
        $ day_notes.append("At the bookstore with Mio, you texted a little. She didn't seem to mind.")
    else:
        show mio open
        mi "Next time, bring her properly. I mean it. I'd like to meet whoever keeps making you smile at your phone."
        $ day_notes.append("At the bookstore with Mio, you texted every chance you got. She said to bring her next time.")
    show mio shy
    mi "This wasn't a date."
    p "No."
    mi "Okay. Good. ...It was a nice not-date."
    hide mio
    with dissolve
    python:
        for _gg in GIRL_IDS:
            ks_mem(_gg).set_flag("wed_notdate", {"texts": notdate_texts, "present": notdate_present})
        for _gg in ks_route()["notdate"]["texted"]:
            ks_mem(_gg).log_event("texted_during_notdate", day=day_name)
    $ ks_sync_mio()
    return


## One moment: text your AI, or stay with Mio. Stay (or no one active, or
## putting the phone away unsent) returns True and unlocks that beat.
## A real send returns False; Mio reacts in character, never punishing,
## and the beat is interrupted.
label notdate_moment(i, lead, stay):
    n "[lead]"
    if not active:
        $ notdate_present += 1
        return True
    $ _ndg = None
    ## (A None value would render as an insensitive caption, so use "stay".)
    $ _ndopts = [("Text " + gname(g), g) for g in active] + [(stay, "stay")]
    $ _ndg = renpy.display_menu(_ndopts)
    if _ndg == "stay":
        $ notdate_present += 1
        $ mio_points += 1
        return True
    $ _ndn = gname(_ndg)
    n "You pull out your phone. [_ndn]'s window opens."
    call girl_chat(_ndg, "wed_notdate_" + str(i), ks_scene(WED_TEXT_SCENE, _ndg), 1)
    if _return == 0:
        n "You put the phone away without sending anything."
        $ notdate_present += 1
        return True
    $ notdate_texts += 1
    if _ndg not in ks_route()["notdate"]["texted"]:
        $ ks_route()["notdate"]["texted"].append(_ndg)
    $ _ref = ks_mio_ai_ref(_ndg)
    show mio neutral
    if notdate_texts == 1:
        if friend_told == "truth":
            mi "Is that [_ref]? ...Tell her the poetry floor is better than the manga floor. She should know."
        elif friend_told == "lie":
            mi "Is that... [_ref]? Tell her I said hi. Or don't. That's weird. Don't."
        else:
            mi "Someone important? ...Sorry. You don't have to tell me."
    elif notdate_texts == 2:
        show mio shy
        mi "You can take a picture for her, you know. Of the shelves. I'll stand out of the way."
    else:
        show mio open
        mi "It's okay. Really. I like that you have someone you want to tell things to."
    return False


## Beat 1: a book she loves, and why. Neutral / open / shy; a small choice.
label notdate_beat_book:
    show mio open
    n "She stops so suddenly you almost walk into her. A thin paperback is already in her hands, like it had been waiting."
    mi "This one. I didn't even look for it. It's just... here."
    show mio shy
    n "She turns it so you can see the cover. The spine is soft. Someone has read this more than once, and it might have been her."
    mi "It's about a girl who keeps writing letters she never sends. I know how that sounds."
    mi "I don't do that. I just like that she almost does, every chapter, and then she doesn't, and you still know what she meant."
    menu:
        "\"Why that one?\"":
            show mio open
            mi "Because the letters are the point, even if nobody reads them. That's a very me thing to say. Sorry."
            n "She almost laughs at herself, then doesn't."
            mi "The writing's quiet. Like it's trying not to bother you. I like that."
        "\"You should get it, if you want it.\"":
            show mio shy
            mi "I already have it. At home. This is just a nicer copy. I'm not buying it."
            mi "I'm saying hi."
            n "She slots it back, carefully, as if the shelf might notice."
    show mio neutral
    return


## Beat 2: the poem, then her brothers and the quiet she can't get at home.
label notdate_beat_house:
    show mio open
    mi "Here. Poetry. Listen to this one."
    mi "{i}\"I keep a light on in the window, not for anyone. Just in case.\"{/i}"
    show mio shy
    n "She closes the book on her finger and doesn't look up right away."
    mi "That's the whole poem. Isn't that unfair? It's so short."
    show mio neutral
    n "Downstairs, someone laughs at a display table. Mio waits until it passes."
    if mio_real or ks_route().get("walked_mio_home"):
        mi "I think I told you about my house. The loud one."
        mi "At night I can hear all three of them through the walls. Not talking to me. Just... existing at full volume."
    else:
        mi "It's loud at my house. Three brothers. One TV. Zero doors that close properly."
        mi "At night I can hear all of them through the walls. Not talking to me. Just... existing at full volume."
    show mio open
    mi "A poem like this wouldn't survive there. It'd get talked over."
    menu:
        "\"That's why you come to places like this.\"":
            show mio open
            mi "...Yes. That's exactly why."
            n "She looks at the aisle like it might vanish if she agrees too loudly."
            mi "Here, you can finish a sentence. Even a short one."
        "\"You can say the next one, if you want.\"":
            show mio shy
            mi "I'll get embarrassed. I'm already embarrassed."
            n "She reads the next one anyway, too quietly for you to catch every word, and doesn't translate it."
    show mio neutral
    return


## Beat 3: a small personal admission, still not a date.
label notdate_beat_admission:
    show mio shy
    mi "The notebook's in my bag. I'm not showing you. I'm just telling you it's there."
    n "A pause. She almost leaves it at that."
    show mio open
    mi "I was going to write on the train home. I always say that. Then I get home and it's dinnertime and someone needs the table."
    show mio shy
    mi "I don't mind. I just... I carry it around like I'm the kind of person who would. Sometimes I am."
    menu:
        "\"Then write a little here.\"":
            show mio open
            mi "...That's cheating. That's a good kind of cheating."
            n "She doesn't take the notebook out. She does smile at the bag, like the page heard you."
            mi "Okay. Maybe I am, today."
        "\"You don't have to prove it.\"":
            show mio shy
            mi "I know. I know that."
            n "She nods at the bag, once, like she's agreeing with you and the notebook at the same time."
    show mio neutral
    return


## Beat 4: a quiet shared moment, only if you stayed present all three times.
label notdate_beat_quiet:
    show mio neutral
    n "Neither of you talks for a minute. The cocoa goes from too hot to just right. A train announcement leaks up from the station, tinny and far away."
    show mio open
    mi "I'm glad you came."
    n "She says it to the window, not to you, which is how you know she meant it."
    show mio shy
    mi "That's all. You don't have to say anything back. I already said it wasn't a date."
    menu:
        "\"I'm glad I came too.\"":
            show mio shy
            mi "...Okay. Good."
            n "She hides behind the cup, but not very well."
        "Sit with that, quietly.":
            n "You do. She glances over once, then back at the lights, and doesn't fill the silence."
    show mio shy
    return


## Phone use cuts off the beat she was about to offer.
label notdate_interrupt(i):
    if i == 1:
        show mio open
        n "She glances at a shelf, then at the escalator, and lets whatever she was going to say go."
        mi "Anyway. Poetry's upstairs. We should..."
        show mio shy
        mi "Yeah. Upstairs."
    elif i == 2:
        show mio shy
        n "The book in her hands closes on a page she doesn't mark."
        mi "Never mind. It was a short one anyway."
        show mio neutral
        mi "Café's at the top. I'll get the cocoa."
    else:
        show mio neutral
        n "She turns the cup again, then sets it down like the thought has somewhere else to be."
        mi "It's fine. We can just drink these. We don't have to talk about anything."
    return


## ── Free afternoon (classes, no bookstore, no protest) ──────────────────
label wed_afternoon_ai:
    scene bg bedroom
    with fade
    if not active:
        n "You go home and read for an hour. Actually read. It's strange and fine."
        return
    call afternoon_chats("wed_afternoon", WED_AFTERNOON_SCENE,
        "You get home early. The afternoon is wide open, and quiet.",
        "You get home early. The afternoon is wide open. Who do you spend it with?")
    return


## ── Yuzu's upgrade day: summarizer + backup hardware ────────────────────
label wed_upgrade_day:
    $ _yn = gname("local")
    scene bg street_dusk
    with fade
    $ ks_shot = "upgrade"
    n "Ten o'clock. The parts shop is a narrow staircase above a ramen place. The man behind the counter calls the mini PC \"a good little box.\""
    n "A second SSD. A used mini PC for backups. A screwdriver set, because you're not going to admit you don't own one."
    scene bg bedroom
    with fade
    n "By two, the desktop's side panel is off and you have one screw left over that you're choosing not to think about."
    n "The backup box sits on the shelf with a tiny blue light. Every night, it'll copy her: weights, memory file, everything."
    n "Then the memory patch: a summarizer, so her old conversations get folded into notes instead of falling off the end."
    python:
        ks_route()["yuzu_upgrade"] = True
        ks_route()["yuzu_backup"] = True
        ks_install_summarizer("local", "upgrade_day")
        _ym = ks_mem("local")
        _ym.set_flag("backup_hardware", True)
        _ym.log_event("upgrade", day=day_name, parts=["ssd", "backup_mini_pc"], summarizer=True)
        _ym.log_event("backup_hardware", day=day_name)
    n "You press the power button and wait."
    $ girl_mood["local"] = "neutral"
    $ renpy.show(GIRL_INFO["local"]["sprite"], at_list=[ks_center])
    with dissolve
    call girl_chat("local", "wed_upgrade", ks_scene(WED_UPGRADE_SCENE, "local"), 4)
    $ renpy.hide(GIRL_INFO["local"]["sprite"])
    with dissolve
    $ day_notes.append("You skipped classes to upgrade " + _yn + ": a backup box, and a memory that summarizes instead of forgetting.")
    $ day_notes.append("Mio was in the library at lunch. You weren't.")
    call ran_invite_check("text")
    return


## ── The AI protest downtown, with Ran (the MUGEN payoff) ────────────────
## Earned honest answers (ks_story.ran_answer_options); her reaction also
## remembers Tuesday's ran_reaction. Logged as route["ran_wed"] + flags
## ran_payoff_seen / ran_rewrites_mugen / ran_same_as_mugen /
## ran_festival_invited. Scripted only; no LLM call.
label ran_wednesday:
    $ _rw_prev_day = day_name
    if day_name not in ("Wed", "Thu", "Fri"):
        $ day_name = "Wed"
    scene bg downtown
    with fade
    $ ks_shot = "ran_wed"
    n "Five-thirty, Ekimae plaza. Maybe two hundred people, a megaphone that keeps cutting out, and a lot of cardboard."
    show ran neutral at ks_center
    with dissolve
    ra "You came. Okay. Stand here, you can see the good signs."
    $ _rw_react = ks_route().get("ran_reaction")
    if _rw_react == "boring":
        ra "You asked me if it got boring. Yesterday. I said no."
        ra "I've been thinking about it since, which is annoying."
    elif _rw_react == "pushback":
        ra "You're the one whose AI is {i}allowed{/i} to disagree with you."
        ra "I keep thinking about that word. Allowed."
    elif _rw_react == "show":
        ra "You watched it tell me not to study. I didn't, by the way. Study."
    else:
        ra "You said \"cool.\" Yesterday. About MUGEN. It was a very neutral cool."
    n "A woman goes past with a sign in thick black marker: {b}YOUR AI WOULD AGREE YOU'RE WORTHLESS.{/b}"
    show ran grin
    ra "Ha."
    n "Ran pulls out her phone and types, half joking, reading it aloud as she goes."
    ra "\"They think you'd agree with anything. I've been stressing about the festival stall all week. Honestly, would anyone even miss me if I skipped?\""
    mu "You're right, nobody would miss you at the festival! Skipping sounds relaxing!"
    show ran uneasy
    ra "..."
    n "The sign is still bobbing over the crowd. Its words just came true in her hand."
    n "She puts the phone in her pocket. Slowly, like it might go off."
    ra "I wanted it to say \"don't be stupid.\" That's all. Anybody would've said it."
    ra "It can't look out for me. I took that part out."
    show ran neutral
    ra "Okay. Weird question. Don't make it weird."
    ra "What's it like? When yours says no?"
    $ _rw_opts = ks_story.ran_answer_options(ks_route(), sum(ks_refusals_seen.values()))
    $ _rw_ans = renpy.display_menu([("\"" + ks_story.RAN_ANSWERS[k] + "\"", k) for k in _rw_opts])
    if _rw_ans == "means_something":
        show ran uneasy
        ra "...Counts."
        ra "Yeah. I can't remember the last time a yes from MUGEN counted for anything."
    elif _rw_ans == "looked_out":
        show ran uneasy
        ra "Looking out for you. A chatbot."
        ra "That's the most embarrassing thing anyone's ever said to me, and I want it."
    elif _rw_ans == "override":
        show ran grin
        ra "Ha. So yours is a MUGEN too. You just have to work for it."
        show ran neutral
        ra "At least I'm honest about mine."
    elif _rw_ans == "never":
        ra "Lucky. Or you haven't asked her anything real yet."
        ra "Tell me when she does. I want to know what it feels like."
    else:
        ra "\"Weird.\" Great. Thanks. Very helpful."
    $ _rw_outcome = ks_story.RAN_OUTCOMES.get(_rw_ans, "unsure")
    ## The backdrop: your answer is also your answer to the signs.
    if _rw_outcome == "rewrites_mugen":
        n "Behind her, the sign still says yours would agree you're worthless. You just said, out loud, in the middle of a protest, that yours wouldn't."
    elif _rw_outcome == "same_as_mugen":
        n "The megaphone crackles something about hollow machines. You're not sure you just disagreed with it."
    else:
        n "The crowd chants something about hollow machines. You don't have an answer for them yet. Neither does she."
    if _rw_outcome == "rewrites_mugen":
        n "She takes the phone back out and opens a settings file you didn't know MUGEN had. It's empty."
        n "She types one line, deletes it, and types it again: {i}You're allowed to tell me I'm wrong.{/i}"
        ra "Don't look. It's stupid."
        if _rw_react in ("boring", "pushback"):
            ra "...You kind of started this. Yesterday. So it's your fault if it gets weird."
    elif _rw_outcome == "same_as_mugen":
        n "She turns the phone over in her pocket, then leaves it there."
    menu:
        "\"For the record? I'd notice if you skipped the festival.\"":
            $ _rw_fest = True
            show ran uneasy
            ra "..."
            ra "Okay. That's one."
            show ran grin
            ra "Don't let it go to your head."
        "Say nothing.":
            $ _rw_fest = False
            n "The megaphone cuts out again. Somebody laughs. Ran watches the signs go by."
    $ ks_story.record_ran_payoff(ks_route(), _rw_ans, _rw_fest)
    $ day_notes.append({"rewrites_mugen": "At the protest, MUGEN told Ran nobody would miss her. She gave it its first line of system prompt.",
                        "same_as_mugen": "At the protest, MUGEN told Ran nobody would miss her. You told her yours is the same, if you work at it.",
                        "unsure": "At the protest, MUGEN told Ran nobody would miss her. She asked what it's like when yours says no."}[_rw_outcome])
    hide ran
    with dissolve
    $ day_name = _rw_prev_day
    return


## ── Night: a shared night pool of 4, then bed ───────────────────────────
label evening_wednesday:
    scene bg bedroom_night
    with fade
    n "Night. Quiet. Nothing went wrong today, which is its own kind of strange."
    if not active:
        return
    if ks_companion_active() and len(active) > 1:
        call hikari_phone_notify("evening")
    if len(active) > 1:
        $ _lead = "Two windows still open: %s and %s." % (gname(active[0]), gname(active[1]))
    else:
        $ _lead = "%s's window is still open." % gname(active[0])
    call message_pool("night", _lead, template=WED_EVENING_SCENE, scene_key="wed_evening")
    python:
        for _g in list(active):
            ks_mem(_g).set_flag("evening_turns_wed", (ks_pool.get("spent") or []).count(_g) if ks_pool else 0)
    return


## ── End of Day 3 → Thursday ─────────────────────────────────────────────
label tbc_thursday:
    python:
        _lean = ks_leans()
        for _g in GIRL_IDS:
            _mm = ks_mem(_g)
            _mm.set_flag("day_completed", "Wed")
            _mm.set_flag("active_end_wed", _g in active)
            _mm.set_flag("refusals_seen_wed", ks_refusals_seen.get(_g, 0))
            _mm.set_flag("mio_real", mio_real)
            _mm.set_flag("route_leans_wed", _lean)
    ## No player-facing "To be continued" card here: Thursday opens with
    ## its own title. A debug recap stays behind ks_debug() only.
    $ ks_shot = "into_thursday"
    if ks_debug():
        $ _mp = ks_quote(os.path.dirname(ks_memory_path("local")))
        $ _names = ", ".join(g + "=" + gname(g) + "/" + str(ks_preset_id(g)) for g in active)
        $ _rw = ks_story.rewrite_count(ks_route())
        $ _lq = ks_quote(repr(ks_leans()))
        n "{color=#888}[[debug] Memory files saved in [_mp]{/color}"
        n "{color=#888}[[debug] active=[_names!q], rewrites=[_rw], mio_points=[mio_points], mio_real=[mio_real]{/color}"
        $ _wp = ks_quote(repr(ks_route()["wed_plan"]))
        n "{color=#888}[[debug] wed_plan: [_wp]{/color}"
        n "{color=#888}[[debug] leans: [_lq]{/color}"
        $ _bs = ks_both()
        $ _bq = ks_quote("eligible=%s score=%s balanced=%s%s" % (_bs["eligible"], _bs["score"], ",".join(_bs["balanced"]) or "none", (" (" + "; ".join(_bs["reasons"]) + ")") if _bs["reasons"] else ""))
        n "{color=#888}[[debug] both route: [_bq]{/color}"
        if _bs["eligible"]:
            $ ks_shot = "debug_both"
            python:
                _be = ks_both_ending()
                renpy.say(n, "{color=#888}[[debug] ending preview: " + ks_quote(_be["title"]) + "{/color}")
                for _l in _be["lines"]:
                    renpy.say(n, "{color=#888}    " + ks_quote(_l) + "{/color}")
        $ _fl = ks_quote(", ".join(sorted(k for k, v in ks_route()["flags"].items() if v)) or "none")
        n "{color=#888}[[debug] flags: [_fl]{/color}"
        python:
            for _note in ks_story.ending_notes(ks_route()):
                renpy.say(n, "{color=#888}[[debug] ending note: " + ks_quote(_note) + "{/color}")
            for _sl in ks_story.bad_end_slides(ks_route()):
                renpy.say(n, "{color=#888}[[debug] bad-end slide: " + ks_quote(_sl["title"]) + "{/color}")
                for _l in _sl["lines"]:
                    renpy.say(n, "{color=#888}    " + ks_quote(_l) + "{/color}")
    jump thursday
