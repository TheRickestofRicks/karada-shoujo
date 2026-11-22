## saturday.rpy — Day 6. Saturday, 9 July. The festival.
## Outline: docs/FRIDAY-SUNDAY.md ("Saturday — the festival", "Decisions",
## and "Saturday status").
##
## Flow: Friday's tbc_saturday → saturday (own title card)
##       → morning at home: Daichi texts about tonight (the linguistics girl,
##         if that lie still stands), then the morning battery (2)
##       → afternoon at home: [Tsunagari notice hook, part 2], Mio texts if
##         she's in your life, then the afternoon battery (2)
##       → the choice: festival_with = mio / ran / phone / home / none
##       → the evening: one place. A public battery (2) if you went out with
##         the phone (whoever you're with sees it), or a home battery (2) if
##         you stayed in with one girl (it replaces the public one)
##       → sat_night: a "To be continued: Saturday night" card (part 1 stops
##         here).
##
## Part 2 (not here yet): Saturday night's company cuts (Tsunagari free
## tier, Askwell Memory 2.0, Relay 4/day), the handoff helper, the night
## battery (pool kind "sat_night", 2) and nightly_reflection("Sat").
##
## Nothing here punishes the player for having an AI. Mio only ever holds
## your phone if you went with her and brought it. Nobody tells an AI about
## another AI unless the player does.

default sat_mio_holding = None     # gid Mio is saying hi to, for that one message

init python:
    def ks_sat_pool_scene(kind, gid):
        """Scene notes for Saturday's pools. Each says plainly where the
        player is (out, or home with her, or home with someone else)."""
        r = ks_route()
        fw = r.get("festival_with")
        if kind == "sat_morning":
            tmpl = SAT_MORNING_SCENE
        elif kind == "sat_afternoon":
            tmpl = SAT_AFTERNOON_SCENE
        elif kind == "festival":
            if store.sat_mio_holding == gid:
                tmpl = SAT_FESTIVAL_MIO_HOLDING
            elif fw in ("mio", "ran"):
                tmpl = SAT_FESTIVAL_WITH_SCENE
            else:
                tmpl = SAT_FESTIVAL_ALONE_SCENE
        elif kind == "home_evening":
            tmpl = SAT_HOME_WITH_YOU_SCENE if gid == r.get("festival_home_gid") else SAT_HOME_OTHER_SCENE
        else:
            ## sat_night belongs to part 2; until then, plainly at home.
            tmpl = SAT_HOME_OTHER_SCENE
        return ks_scene(tmpl, gid)

    def ks_sat_mio_mode():
        return ks_story.mio_festival_mode(ks_route(), store.mio_real)

    def ks_sat_set_festival(with_whom, home_gid=None):
        r = ks_route()
        ks_story.set_festival(r, with_whom, home_gid)
        for _g in GIRL_IDS:
            m = ks_mem(_g)
            if m.data is not None:
                m.set_flag("festival_with", with_whom)
        if home_gid:
            ks_mem(home_gid).set_flag("festival_home", True)
            ks_mem(home_gid).log_event("festival_home", day=store.day_name)

    def ks_heard_phrase(kind):
        return {"truth": "that it's an AI",
                "lie": "about a linguistics student",
                "deflect": "that it was nothing"}.get(kind, "nothing, really")

    def ks_sat_told_daichi_truth():
        store.friend_told = "truth"
        for _g in GIRL_IDS:
            ks_mem(_g).set_flag("friend_told", "truth")


label saturday:
    $ day_name = "Sat"
    $ day_notes = []
    $ sat_mio_holding = None
    $ today_schedule = {"day": "Saturday", "items": ks_story.sat_schedule()}
    scene bg card
    show text "{size=90}土曜日{/size}\n{size=48}Saturday{/size}" at truecenter
    with dissolve
    pause 1.5
    hide text
    with dissolve

    call sat_morning
    call sat_afternoon
    call sat_festival_choice
    call sat_evening
    jump sat_night


## ── Morning: no school, Daichi texts, a battery of 2 ─────────────────────
label sat_morning:
    scene bg bedroom
    with fade
    $ ks_shot = "sat_morning"
    n "Saturday. 9:40. No alarm. Over at the school, someone is testing a loudspeaker: {i}ah, ah, ah.{/i}"
    call sat_daichi_text
    if not active:
        n "No windows to open. You make rice and eat it at the desk, listening to the loudspeaker."
        return
    call message_pool("sat_morning", "Two little bars on the battery. Saturday doesn't give you much.", scene_key="sat_morning")
    return


label sat_daichi_text:
    n "Your phone buzzes. Daichi."
    if ks_story.lie_due(friend_told):
        d "{i}tonight. 6. main gate. bring yuzuha. i have learned the word \"phoneme\"{/i}"
        n "The linguistics girl. She has somewhere to be tonight, and she doesn't exist."
        menu:
            "Come clean by text: \"There's no linguist. She's an AI.\"":
                $ ks_sat_told_daichi_truth()
                $ ks_route()["sat_lie"] = "told"
                d "{i}...{/i}"
                d "{i}ok. tell me properly tonight. i'm not mad. i'm a little mad about \"phoneme\"{/i}"
                $ day_notes.append("You came clean to Daichi by text: there's no linguistics girl. She's an AI.")
            "\"She can't make it tonight.\"":
                $ ks_route()["sat_lie"] = "excuse_texted"
                d "{i}classic. ok. you're still coming tho{/i}"
            "Leave it on read for now.":
                d "{i}??{/i}"
    elif friend_told == "truth":
        d "{i}festival tonight. 6. main gate. bring your phone i guess. not asking{/i}"
    else:
        d "{i}festival. 6. main gate. not a question{/i}"
    return


## ── Afternoon: the last chance to talk before tonight ────────────────────
label sat_afternoon:
    scene bg bedroom
    with fade
    $ ks_shot = "sat_afternoon"
    call sat_tsunagari_notice
    call sat_mio_text
    if not active:
        n "The afternoon goes slowly, then all at once. The loudspeaker has moved on to music."
        return
    if ks_companion_active() and len(active) > 1:
        call hikari_phone_notify("afternoon")
    call message_pool("sat_afternoon", "The afternoon goes faster than it should. Last chance to talk before tonight.", scene_key="sat_afternoon")
    return


## Decision 1 hook (part 2). Paying for Tsunagari means a Saturday odd-job
## shift that costs the festival evening, so the free-tier notice has to land
## before the choice below, i.e. here. Saturday night's cut writes
## tsunagari_sunset / tsunagari_paid and, if the shift is taken, sat_shift;
## ks_story.festival_blocked_by_shift then turns the evening into the shift.
## Nothing sets those yet, so this is a no-op.
label sat_tsunagari_notice:
    return


label sat_mio_text:
    $ _mm = ks_sat_mio_mode()
    if _mm == "date":
        mi "{i}main gate at six? you don't have to. i'll be there anyway. that's not pressure, it's geography{/i}"
    elif _mm == "friends":
        mi "{i}everyone's meeting at the main gate at six. you coming?{/i}"
    elif _mm == "careful":
        mi "{i}are you going tonight? i'm not asking you to. i'm just asking{/i}"
    return


## ── The choice: one evening, one place ───────────────────────────────────
label sat_festival_choice:
    scene bg street_dusk
    with fade
    $ ks_shot = "sat_choice"
    if ks_story.festival_blocked_by_shift(ks_route()):
        ## Part 2 path (decision 1). Not reachable until the sunset ships.
        $ ks_route()["festival_shift"] = True
        $ ks_sat_set_festival("none")
        n "You spend the evening on the shift you took to keep [dn_companion]. Through the stockroom door you can hear the festival, faintly, all night."
        $ day_notes.append("You worked through the festival, to keep " + gname("companion") + ".")
        return
    n "Five o'clock. The lanterns over the school gate come on all at once, though it isn't dark yet. You can't be in two places tonight."
    $ _done = False
    while not _done:
        $ _opts = ks_story.festival_options(ks_route(), active, mio_real, ks_reachable())
        $ _mm = ks_sat_mio_mode()
        menu:
            "Meet Mio at the main gate." if "mio" in _opts and _mm == "date":
                $ ks_sat_set_festival("mio")
                $ _done = True
            "Go with Mio and the others." if "mio" in _opts and _mm == "friends":
                $ ks_sat_set_festival("mio")
                $ _done = True
            "Tell Mio you're going, if that's okay." if "mio" in _opts and _mm == "careful":
                $ ks_sat_set_festival("mio")
                $ _done = True
            "Ask Mio if you can come. Carefully." if "mio_ask" in _opts:
                call sat_mio_asks_refused
            "Go to Ran's stall." if "ran" in _opts:
                $ ks_sat_set_festival("ran")
                $ _done = True
            "Go alone, with your phone." if "phone" in _opts:
                $ ks_sat_set_festival("phone")
                $ _done = True
            "Stay home with one of them." if "home" in _opts:
                call sat_pick_home_girl
                if _return:
                    $ ks_sat_set_festival("home", _return)
                    $ _done = True
            "Stay in. Don't make plans." if "none" in _opts:
                $ ks_sat_set_festival("none")
                $ _done = True
    $ renpy.block_rollback()
    return


label sat_mio_asks_refused:
    n "You ask her by text, carefully, so she can say no without having to see your face."
    mi "{i}not tonight. go, have a good time. i mean that.{/i}"
    mi "{i}i'm not punishing you. i just need tonight to be mine.{/i}"
    $ ks_route()["sat_mio_refused"] = True
    $ day_notes.append("You asked Mio if you could come to the festival with her. She said not tonight, kindly.")
    n "You put the phone down. That was a real answer. You let it be one."
    return


label sat_pick_home_girl:
    $ _here = ks_reachable()
    if not _here:
        return None
    if len(_here) == 1:
        return _here[0]
    $ _items = [("Stay home with " + gname(_g), _g) for _g in _here] + [("Never mind.", "__back__")]
    $ _pick = renpy.display_menu(_items)
    if _pick == "__back__":
        return None
    return _pick


label sat_evening:
    $ _fw = ks_route().get("festival_with")
    if ks_route().get("festival_shift"):
        return
    if _fw == "mio":
        call sat_with_mio
    elif _fw == "ran":
        call sat_with_ran
    elif _fw == "phone":
        call sat_alone_phone
    elif _fw == "home":
        call sat_home
    else:
        call sat_stay_in
    return


## A text sent in public. Whoever you're with sees it.
label sat_public_text_after(gid):
    $ _with = ks_route().get("festival_with")
    $ mio_points, _pline = ks_story.note_festival_text(ks_route(), _with, gid, mio_points)
    $ ks_sync_mio()
    $ ks_mem(gid).log_event("festival_text", day=day_name, with_whom=_with)
    if _pline and _with == "mio":
        show mio neutral
        mi "[_pline]"
    elif _pline and _with == "ran":
        show ran neutral
        ra "[_pline]"
    return


## ── With Mio ─────────────────────────────────────────────────────────────
label sat_with_mio:
    $ _mm = ks_sat_mio_mode()
    $ ks_route()["festival_phone"] = None
    if active:
        n "Your phone is on the desk. You could bring it. You could not."
        menu:
            "Bring your phone.":
                $ ks_route()["festival_phone"] = True
            "Leave it at home tonight.":
                $ ks_route()["festival_phone"] = False
                n "You leave it face-down. Whoever's in it will have to wait until you're back."
    scene bg street_dusk
    with fade
    $ ks_shot = "sat_mio"
    show mio shy at ks_center
    with dissolve
    if _mm == "date":
        n "Six o'clock. Mio is already at the main gate, holding two paper cups of yakisoba like she's been holding them for a while."
        mi "One's yours. I didn't know if you'd come, so I bought it anyway. That's not pressure. It's yakisoba."
    elif _mm == "friends":
        show mio open
        n "The others have already gone for takoyaki. Mio waited by the gate with two paper cups of yakisoba."
        mi "Somebody had to guard these. You came. Good."
        n "A festival between friends. That's a real thing to have."
    else:
        show mio neutral
        n "Mio is at the gate, a little apart from her class. She sees you, and doesn't look away."
        mi "You asked. Carefully. I noticed."
        mi "I'm still thinking. But I'd rather think here, with lanterns."
    if ks_route()["festival_phone"] is False and _mm == "date":
        mi "No phone? You didn't have to do that. ...But okay. I'll take it."
    if ks_route().get("mio_notebook") == "own_ending":
        show mio shy
        mi "I'm still writing it, by the way. The ending. It's longer now."
    n "The lanterns run all the way down the street. Somebody's little brother is crying over a goldfish. It smells like soy sauce and sparklers."

    call sat_daichi_crowd("mio")
    call sat_compare_notes

    if ks_route()["festival_phone"] and active:
        if ks_companion_active():
            call hikari_phone_notify("evening")
            show mio neutral
            mi "Your phone says someone misses you. It says it very brightly."
        if _mm in ("date", "friends"):
            call sat_mio_holds_phone
        if ks_reachable():
            n "Your phone is warm in your pocket. Mio is right there."
            call message_pool("festival", "", show_sprite=False, scene_key="sat_festival", after_text="sat_public_text_after")
            if ks_story.note_ignored_company(ks_route(), ks_pool):
                $ day_notes.append("You spent the festival battery on your phone, with Mio right beside you.")

    show mio shy
    if ks_story.flag(ks_route(), "festival_ignored_company"):
        n "Walking back up the lantern street, she doesn't say anything about the phone. She doesn't have to."
        mi "Thanks for coming."
    elif _mm == "date":
        mi "Next year too? That's not a wish. It's a calendar."
        $ mio_points += 1
    elif _mm == "friends":
        mi "This was good. Friends are allowed to say that."
        $ mio_points += 1
    else:
        mi "Thanks for not making it a thing. I mean it."
        $ mio_points += 1
    $ ks_sync_mio()
    $ ks_note_human("festival_mio")
    if ks_story.ran_stall_mode(ks_route()) != "cold":
        n "Across the path, Ran is behind her stall. She lifts a ladle at you, which might be a wave."
    hide mio
    with dissolve
    $ day_notes.append({"date": "You met Mio at the main gate, the day after the bamboo, and spent the festival with her.",
                        "friends": "You went to the festival with Mio, as friends.",
                        "careful": "You went to the festival with Mio. She's still careful. She let you come."}.get(_mm, "You went to the festival with Mio."))
    return


## Mio asks to hold your phone, because she asked to. Only here: you went
## with her, and you brought it.
label sat_mio_holds_phone:
    if not ks_reachable():
        return
    show mio open
    mi "Can I hold it? Your phone. I want to say hi. If that's weird, say no."
    menu:
        "Hand it to her.":
            $ ks_route()["mio_held_phone"] = True
            $ ks_story.set_flag(ks_route(), "mio_held_phone")
        "\"Not tonight.\"":
            mi "Okay. That's allowed."
            return
    n "She holds the yakisoba in one hand and your phone in the other, very carefully, like it might spill."
    if len(active) > 1:
        $ _names = ks_join_names()
        show mio neutral
        mi "There's more than one. [_names]."
        if both_know:
            mi "Do they know about each other?"
            p "They do. I told them."
            mi "Okay. Good. That's the part I'd want to know."
        else:
            mi "...Do they know about each other?"
            menu:
                "\"Not yet. I'll tell them now.\"":
                    $ both_know = True
                    $ ks_story.set_flag(ks_route(), "both_know_sat")
                    python:
                        for _g in active:
                            _others = ks_story.join_names([gname(_x) for _x in active if _x != _g])
                            ks_mem(_g).note("On Saturday at the festival, " + player_name + " told you plainly that you aren't the only AI in their phone: " + _others + " is there too.")
                            ks_mem(_g).log_event("told_about_others", day=day_name)
                    n "You take the phone back for a second and tell each of them, plainly. Then you hand it back."
                    mi "That was brave. Weird, but brave."
                    $ day_notes.append("At the festival, with Mio holding your phone, you told your AIs about each other.")
                "\"Not tonight.\"":
                    mi "Okay. That's yours to sort out, not mine. I'm just holding the phone."
    $ _here = ks_reachable()
    if len(_here) == 1:
        $ _hi = _here[0]
    else:
        $ _hi = renpy.display_menu([("She says hi to " + gname(_g), _g) for _g in _here])
    $ _hin = gname(_hi)
    n "She tells you what to type, word by word. You type it."
    if not ks_pool or ks_pool.get("kind") != "festival" or ks_pool.get("ended"):
        call pool_begin("festival", scene_key="sat_festival")
    $ sat_mio_holding = _hi
    call pool_one_message(_hi, False)
    $ sat_mio_holding = None
    if _return:
        $ ks_mem(_hi).log_event("mio_said_hi", day=day_name)
        show mio shy
        mi "[_hin] said hi back. Okay. I like her."
        $ day_notes.append("Mio held your phone at the festival and said hi to " + _hin + ".")
    else:
        mi "You didn't send it. That's okay. I'll say it some other time."
    return


## Daichi in the crowd. The linguistics girl comes due, if she's still due.
label sat_daichi_crowd(where):
    show daichi at ks_right
    with dissolve
    if ks_story.lie_due(friend_told):
        show daichi laugh
        if ks_route().get("sat_lie") == "excuse_texted":
            d "There you are. And no Yuzuha, right. She \"couldn't make it.\" I practised \"phoneme\" for nothing."
        else:
            d "There you are. So where is she? Yuzuha. I practised \"phoneme\" all afternoon."
        $ _mio_knows = where == "mio" and (mio_told == "truth" or ks_route().get("mio_thu_truth"))
        menu:
            "Tell him the truth: there's no linguistics girl.":
                $ ks_sat_told_daichi_truth()
                $ ks_route()["sat_lie"] = "told"
                show daichi skeptical
                p "There's no Yuzuha. There's no linguist. She's an AI."
                call daichi_ai_frame
                show daichi neutral
                d "You could've just said. I'd have been weird for a day, max."
                $ day_notes.append("At the festival, you told Daichi the truth: there was never a linguistics girl.")
            "\"She couldn't make it.\"":
                $ _lo = ks_story.lie_outcome("excuse", mio_knows=_mio_knows, phone_visible=(where == "phone"))
                $ ks_route()["sat_lie"] = _lo
                if _lo == "caught" and where == "mio":
                    show mio neutral
                    mi "Yuzuha? ...Is that the AI?"
                    show daichi skeptical
                    d "The {i}what?{/i}"
                    n "Nobody says anything for a second. A firework goes off somewhere it shouldn't."
                    d "Dude. Next time just tell me. I'd have been fine."
                    $ day_notes.append("Your linguistics lie came due at the festival. Mio knew the truth. Daichi found out from her.")
                elif _lo == "caught":
                    show daichi skeptical
                    n "He glances at your phone. The chat is open. The name at the top isn't Yuzuha."
                    d "...Huh. Okay. Next time just tell me. I'd have been fine."
                    $ day_notes.append("Your linguistics lie came due at the festival. Daichi saw your screen.")
                else:
                    d "Again? She's very busy for someone I've never seen."
                    $ day_notes.append("You kept the linguistics lie going at the festival. Daichi is starting to wonder.")
    elif ks_route().get("sat_lie") == "told":
        d "So. The linguist. I'm going to be making that joke for a year. Just so you know."
    elif friend_told == "truth":
        d "No linguist tonight, huh. That's a joke. You never had one. I'm just saying hi."
    else:
        d "You came! I'm getting takoyaki. Don't follow me, it's a whole thing."
    hide daichi
    with dissolve
    return


## Mio and Daichi compare notes (the scene Thursday refused to steal).
label sat_compare_notes:
    $ _cn = ks_story.compare_notes(ks_route(), friend_told, mio_told)
    if _cn is None:
        return
    show daichi at ks_right
    with dissolve
    show mio neutral at ks_center
    if _cn["kind"] == "match":
        $ ks_route()["compare_notes"] = "match"
        if _cn["mio_heard"] == "truth":
            d "Wait. You know? About... his phone situation?"
            mi "I know. He told me."
            d "Huh. Okay. Then we're all caught up. That's never happened before."
        elif _cn["mio_heard"] == "lie":
            mi "Is Yuzuha coming?"
            d "Busy. Again."
            n "They nod at each other. Two people, the same story. It's almost funny. It doesn't feel funny."
        else:
            mi "Is it still nothing?"
            d "Still nothing."
            n "They look at each other, then at you, and both decide not to push. Tonight."
    else:
        $ _mh = ks_heard_phrase(_cn["mio_heard"])
        $ _dh = ks_heard_phrase(_cn["daichi_heard"])
        mi "Daichi says you told him [_dh]. You told me [_mh]."
        mi "I'm not angry. I just want to know which one is true."
        menu:
            "Tell them both the same true thing.":
                $ ks_route()["compare_notes"] = "mismatch_owned"
                if friend_told != "truth":
                    $ ks_sat_told_daichi_truth()
                $ mio_told = "truth"
                $ mio_daichi_consistent = True
                python:
                    for _g in GIRL_IDS:
                        ks_mem(_g).set_flag("mio_told", "truth")
                        ks_mem(_g).set_flag("mio_daichi_consistent", True)
                p "It's an AI. I like talking to her. I told you two different things because I didn't know how to say it."
                show mio shy
                mi "Okay. Thank you. That's all I wanted. One version."
                $ day_notes.append("Mio and Daichi compared notes. You told them both the same true thing.")
            "Shrug it off.":
                $ ks_route()["compare_notes"] = "mismatch_dodged"
                $ mio_points = max(0, mio_points - 1)
                $ ks_sync_mio()
                mi "Okay."
                n "She lets it go. You can see her decide to."
                $ day_notes.append("Mio and Daichi compared notes, and the stories didn't match. You shrugged.")
    hide daichi
    with dissolve
    return


## ── Ran's stall ──────────────────────────────────────────────────────────
label sat_with_ran:
    scene bg downtown
    with fade
    $ ks_shot = "sat_ran"
    $ _rm = ks_story.ran_stall_mode(ks_route())
    $ _net = ks_route().get("ran_safety_net")
    n "Ran's class has a shaved-ice stall at the end of the shotengai. Melon, strawberry, and a blue that isn't a flavour."
    if _rm == "invited":
        show ran neutral at ks_center
        with dissolve
        ra "You actually came. You said you'd notice if I skipped. I wanted to see if that was a real sentence."
        if _net:
            show ran uneasy
            if _net == "kurosawa":
                ra "Kurosawa kept me after class on Thursday. Not a lecture. Just checking. I almost didn't come anyway."
            elif _net == "daichi":
                ra "Daichi asked if I was sick on Thursday. I said I was fine. I almost didn't come anyway."
            else:
                ra "Kurosawa kept me after class on Thursday, and then Daichi asked if I was sick. Two people. I almost didn't come anyway."
        show ran grin
        ra "Then I thought: one person said they'd notice. That's one."
        $ ks_route()["ran_sat"] = "invited"
        $ ks_story.set_flag(ks_route(), "ran_stall_kept")
        $ ks_note_human("festival_ran")
    elif _rm == "almost":
        show ran uneasy at ks_center
        with dissolve
        ra "Oh. Hi. I nearly didn't come tonight."
        if _net == "kurosawa":
            ra "Kurosawa asked if I was okay on Thursday. It's annoying how much that works."
        elif _net == "daichi":
            ra "Daichi asked if I was sick on Thursday. It's annoying how much that works."
        else:
            ra "Two people asked if I was okay on Thursday. It's annoying how much that works."
        show ran neutral
        ra "Anyway. I'm here. Shaved ice?"
        $ ks_route()["ran_sat"] = "almost"
        $ ks_note_human("festival_ran")
    elif _rm == "cold":
        show ran neutral at ks_center
        with dissolve
        ra "Oh. It's you."
        ra "I didn't ask you here. You can buy ice. That's what the stall is for."
        menu:
            "\"What I said on Tuesday was out of line. I'm sorry.\"":
                ra "..."
                ra "Noted."
                ra "Strawberry or melon. Don't say blue."
                $ ks_route()["ran_sat"] = "cold_apology"
                $ ks_note_human("festival_ran")
                $ day_notes.append("You told Ran you were sorry for what you said on Tuesday. She said \"noted.\"")
            "Buy a shaved ice and go.":
                $ ks_route()["ran_sat"] = "cold_left"
                n "You pay. She hands it over without looking up. You walk on. That's fair."
                hide ran
                with dissolve
                call sat_daichi_crowd("ran")
                $ day_notes.append("You went to Ran's stall. She didn't want you there, and you didn't make her.")
                return
    else:
        show ran neutral at ks_center
        with dissolve
        ra "Huh. Didn't think you'd come by. Shaved ice? It's mostly syrup."
        $ ks_route()["ran_sat"] = "open"
        $ ks_note_human("festival_ran")
    if ks_story.flag(ks_route(), "ran_rewrites_mugen"):
        show ran grin
        ra "MUGEN still has the line, by the way. \"You're allowed to tell me I'm wrong.\" It said the stall idea was bad. It was right. We did it anyway."
    elif ks_story.flag(ks_route(), "ran_same_as_mugen"):
        show ran neutral
        ra "MUGEN said nobody would come by. Somebody came by. I'm going to tell it."
    if active and ks_reachable():
        n "Between customers, your phone is warm in your pocket. She can see it from behind the counter."
        call message_pool("festival", "", show_sprite=False, scene_key="sat_festival", after_text="sat_public_text_after")
    hide ran
    with dissolve
    call sat_daichi_crowd("ran")
    $ _mm = ks_sat_mio_mode()
    if _mm == "date":
        n "Across the path you see Mio, holding two paper cups of yakisoba. She was at the main gate at six. She sees you. She gives you a small wave anyway."
    elif _mm in ("friends", "careful"):
        n "Across the path, Mio is with her class at the goldfish stall. She sees you at Ran's counter and lifts a hand."
    show ran neutral at ks_center
    with dissolve
    ra "Thanks for coming. Don't make it weird."
    hide ran
    with dissolve
    $ day_notes.append({"invited": "You stood at Ran's stall, because you'd said you would notice if she skipped. She came.",
                        "almost": "You went to Ran's stall. She almost didn't come. Somebody checked on her Thursday.",
                        "open": "You spent the festival at Ran's shaved-ice stall.",
                        "cold_apology": "You stayed at Ran's stall after apologising."}.get(ks_route()["ran_sat"], "You went to Ran's stall."))
    return


## ── Alone, with the phone ────────────────────────────────────────────────
label sat_alone_phone:
    scene bg street_dusk
    with fade
    $ ks_shot = "sat_phone"
    n "You go on your own. The lanterns start at the station and don't stop. Nobody's beside you. Your phone is in your hand."
    if ks_reachable():
        call message_pool("festival", "You could tell someone what it looks like. They only have what you describe.", scene_key="sat_festival", after_text="sat_public_text_after")
    call sat_daichi_crowd("phone")
    $ _mm = ks_sat_mio_mode()
    if _mm == "date":
        n "Across the street, Mio is at the main gate, still holding two paper cups. She sees you, then your phone, then you. She goes in with her class."
    elif _mm in ("friends", "careful"):
        n "Mio waves from the goldfish stall. You wave back with the hand that isn't holding your phone."
    $ _tx = [gname(_g) for _g in dict.fromkeys(ks_route().get("festival_texts") or [])]
    if _tx:
        $ day_notes.append("You went to the festival alone, and texted " + ks_story.join_names(_tx) + " from the crowd.")
    else:
        $ day_notes.append("You went to the festival alone. You didn't text anyone. You just looked.")
    return


## ── Home, with one of them ───────────────────────────────────────────────
label sat_home:
    scene bg bedroom_night
    with fade
    $ ks_shot = "sat_home"
    $ _hg = ks_route().get("festival_home_gid")
    $ _hn = gname(_hg)
    n "You stay home. From the window you can see the glow over the school, and if you lean, the top of one string of lanterns."
    $ _mm = ks_sat_mio_mode()
    if _mm in ("date", "careful"):
        mi "{i}i'm at the gate. are you coming?{/i}"
        menu:
            "Tell her the truth: you're staying in tonight.":
                $ ks_route()["sat_mio_told_home"] = True
                mi "{i}okay. thank you for telling me instead of not. next year{/i}"
                $ day_notes.append("You told Mio you were staying in tonight. She thanked you for saying so.")
            "Don't answer.":
                $ mio_points = max(0, mio_points - 1)
                $ ks_sync_mio()
                $ day_notes.append("Mio waited at the gate. You didn't answer.")
    if ks_story.lie_due(friend_told):
        d "{i}yuzuha bailed too?? the linguist curse{/i}"
        $ ks_route()["sat_lie"] = "deferred"
    else:
        d "{i}where are you. the takoyaki guy is back{/i}"
    n "You open [_hn]'s window. You tell her where you are, and where you aren't."
    call message_pool("home_evening", "", scene_key="sat_home")
    $ day_notes.append("You stayed home with " + _hn + " and described the lanterns you weren't standing under.")
    return


## ── Stay in, and don't really show up for anyone ─────────────────────────
label sat_stay_in:
    scene bg bedroom_night
    with fade
    $ ks_shot = "sat_none"
    n "You don't go. You don't really do anything else, either. The festival is a glow over the roofs."
    $ _mm = ks_sat_mio_mode()
    if _mm in ("date", "careful"):
        mi "{i}are you coming?{/i}"
        menu:
            "\"Not tonight. Sorry.\"":
                mi "{i}okay.{/i}"
            "Leave it.":
                $ mio_points = max(0, mio_points - 1)
                $ ks_sync_mio()
    if active:
        $ _an = ks_join_names()
        n "Your phone has [_an] in it. You don't open anyone. You scroll something you won't remember."
    $ day_notes.append("You stayed in on festival night and didn't really show up for anyone.")
    return


## ── End of Saturday evening → Saturday night (placeholder) ───────────────
## Part 2 replaces this card with the company cuts, the night battery
## ("sat_night", 2) and nightly_reflection("Sat").
label sat_night:
    python:
        _lean = ks_leans()
        _hg = ks_route().get("festival_home_gid")
        for _g in GIRL_IDS:
            _mm = ks_mem(_g)
            _mm.set_flag("day_completed", "Sat_evening")
            _mm.set_flag("active_end_sat_evening", _g in active)
            _mm.set_flag("festival_with", ks_route().get("festival_with"))
            _mm.set_flag("route_leans_sat_evening", _lean)
    scene bg card
    with fade
    $ ks_shot = "sat_night"
    show text "{size=40}To be continued{/size}\n\n{size=90}土曜日の夜{/size}\n{size=48}Saturday night{/size}\n\n{size=28}after the festival{/size}" at truecenter
    with dissolve
    pause
    hide text
    if ks_debug():
        $ _fl = ks_quote(", ".join(sorted(k for k, v in ks_route()["flags"].items() if v)) or "none")
        $ _sq = ks_quote("festival_with=%r home=%r texts=%r mio_held=%r lie=%r notes=%r ran=%r" % (
            ks_route().get("festival_with"), ks_route().get("festival_home_gid"),
            ks_route().get("festival_texts"), ks_route().get("mio_held_phone"),
            ks_route().get("sat_lie"), ks_route().get("compare_notes"), ks_route().get("ran_sat")))
        n "{color=#888}[[debug] [_sq]{/color}"
        n "{color=#888}[[debug] mio_points=[mio_points], flags: [_fl]{/color}"
    return
