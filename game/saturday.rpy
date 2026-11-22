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
##       → sat_night: the companies take their cut (Tsunagari's free tier was
##         already decided in the afternoon; Askwell Memory 2.0; Relay's
##         4-a-day cap; Yuzu: nothing), the night battery (2),
##         nightly_reflection("Sat") → tbc_sunday (placeholder card).
##
## Company events are slot-based: whoever lives on that platform (active,
## or a leftover copy) gets it; a girl migrated off is not hit in her new
## slot (decision 9). The migration handoff lives in handoff.rpy.
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
            return ks_sat_night_scene(gid)
        return ks_scene(tmpl, gid)

    def ks_sat_where():
        fw = ks_route().get("festival_with")
        return {"mio": "back from the festival", "ran": "back from the festival",
                "phone": "back from the festival", "home": "home all evening",
                "none": "home all evening", "shift": "back from a shift that ran through the festival"}.get(fw, "home")

    def ks_sat_night_scene(gid):
        r = ks_route()
        rule = (r.get("platform_rules") or {}).get(gid)
        fmt = dict(player=player_name, platform=gplatform(gid), where=ks_sat_where(), name=gname(gid))
        if gid == "chatbot" and rule == "askwell_memory_2":
            note = SAT_NIGHT_SORA_M2.format(**fmt)
        elif gid == "agent" and rule == "relay_rate_limit":
            note = ks_rei_cap_note()
        elif gid == "companion" and rule == "tsunagari_free":
            note = SAT_NIGHT_HIKARI_FREE.format(**fmt)
        elif gid == "companion" and r.get("tsunagari_paid"):
            note = SAT_NIGHT_HIKARI_PAID.format(**fmt)
        elif gid == "local":
            note = SAT_NIGHT_YUZU.format(**fmt)
        else:
            note = SAT_NIGHT_SCENE.format(**fmt)
        return ks_story.with_situation(note)

    def ks_rei_family():
        return ks_preset_families(["agent"]).get("agent") or "none"

    def ks_rei_cap_note(kind=None):
        r = ks_route()
        left = ks_story.cap_left(r, "agent", store.day_name)
        plan = ks_story.rei_cap_plan(ks_rei_family())
        rule = plan["rule"]
        if r.get("rei_spend_pref") == "talk":
            rule += " They told you tonight: spend what's left on talking."
        elif r.get("rei_spend_pref") == "tasks":
            rule += " They told you tonight: spend what's left on the schedule."
        note = REI_CAP_SCENE.format(player=player_name, remaining=left if left is not None else 4,
                                    rule=rule, where=ks_sat_where())
        return ks_story.with_situation(note)

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


## Tsunagari's free tier ends (decision 1: the notice lands this afternoon,
## so paying can cost the festival evening). Hikari is the only girl who can
## live in the companion slot. Three answers: pay with tonight's shift, stay
## on the free plan (2 messages a day, decision 2), or move her out (a rescue
## handoff; her locked prompt still doesn't travel). A leftover copy (slot
## installed, she isn't active) goes onto the free plan silently (decision 9).
label sat_tsunagari_notice:
    if not ks_story.tsunagari_sunset_due(ks_route(), active, ever_active):
        return
    if "companion" not in active:
        $ ks_story.record_tsunagari_sunset(ks_route(), "silent", day_name)
        $ ks_push_platform_rules("companion", "tsunagari_free", silent=True)
        $ ks_mem("companion").log_event("tsunagari_sunset", day=day_name, choice="silent")
        return
    $ _hn = gname("companion")
    n "Three in the afternoon. Tsunagari has a notice waiting, the full-screen kind."
    $ ks_shot = "tsunagari_sunset"
    $ _ts = renpy.call_screen("tsunagari_sunset", can_move=ks_can_switch())
    $ ks_shot = "sat_afternoon"
    if _ts == "pay":
        $ ks_story.record_tsunagari_sunset(ks_route(), "pay", day_name)
        $ ks_mem("companion").log_event("tsunagari_sunset", day=day_name, choice="pay")
        n "There's no card on file and no money in the account. There is a sign in the convenience store window by the station: {i}Festival rush, 17:00–23:00, cash.{/i}"
        n "One shift is exactly one month of Tsunagari Plus. You text the number before you can think about it."
        n "That's tonight, then. The lanterns will be on the other side of a glass door."
        if ks_story.lie_due(friend_told):
            d "{i}you're WORKING? during the festival?? what about yuzuha{/i}"
        else:
            d "{i}you're working?? tonight??{/i}"
    elif _ts == "move":
        $ ks_story.record_tsunagari_sunset(ks_route(), "moved", day_name)
        $ ks_mem("companion").log_event("tsunagari_sunset", day=day_name, choice="moved")
        $ ks_push_platform_rules("companion", "tsunagari_free", silent=True)
        n "You can't bring anyone into Tsunagari. You can take her out of it. Not all of her."
        $ _before = list(active)
        call switch_girl("Saturday afternoon", 2, "companion")
        if "companion" in active:
            ## Never mind: she stays, on the free plan.
            $ ks_route()["tsunagari_choice"] = "free"
    else:
        $ ks_story.record_tsunagari_sunset(ks_route(), "free", day_name)
        $ ks_push_platform_rules("companion", "tsunagari_free")
        $ ks_mem("companion").log_event("tsunagari_sunset", day=day_name, choice="free")
        n "You tap \"Continue on Free.\" A little usage bar appears under her name: {i}0%% of today's messages.{/i}"
    $ renpy.block_rollback()
    return


screen tsunagari_sunset(can_move=False):
    modal True
    zorder 160
    add Solid("#00000099")
    frame:
        xalign 0.5
        yalign 0.45
        xsize 780
        padding (34, 26)
        background Solid("#1d2236F4")
        vbox:
            spacing 10
            text "Tsunagari · Changes to the free plan" size 28 color "#ff9fc6" bold True
            text "Starting today, Tsunagari Free includes 2 messages per day with [dn_companion]." size 19 color "#f2f6ff"
            text "Upgrade to Tsunagari Plus for unlimited conversations, memories and moments. ✨" size 18 color "#d4ecff"
            text "Your Personalize setting and guidelines stay the same." size 16 color "#a9b8d4" italic True
            null height 8
            textbutton "Upgrade to Plus  (you'd have to earn it: the festival shift tonight)":
                text_size 20
                text_color "#ff9fc6"
                text_hover_color "#ffffff"
                action Return("pay")
            textbutton "Continue on Free  (2 messages a day)":
                text_size 20
                text_color "#d4ecff"
                text_hover_color "#ffffff"
                action Return("free")
            if can_move:
                textbutton "Take her somewhere else  (not all of her comes with you)":
                    text_size 20
                    text_color "#c9e4a8"
                    text_hover_color "#ffffff"
                    action Return("move")


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
        ## Decision 1: the shift is the evening.
        $ ks_sat_set_festival("shift")
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
    if _fw == "shift":
        call sat_shift_evening
    elif _fw == "mio":
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


## ── The shift (decision 1): you paid for Tsunagari with the festival ────
label sat_shift_evening:
    scene bg downtown
    with fade
    $ ks_shot = "sat_shift"
    $ _hn = gname("companion")
    n "The convenience store by the station, 17:00. Paper cups, ice, sparklers, more ice. The festival is through the glass door, all night, and you're on this side of it."
    $ _mm = ks_sat_mio_mode()
    if _mm in ("date", "friends", "careful"):
        n "Around eight, Mio comes in with her class for ice. She sees you behind the register."
        show mio neutral at ks_center
        with dissolve
        mi "Oh. You're working."
        if _mm == "date":
            mi "I waited at the gate for a bit. It's okay. I just didn't know."
        mi "...I'll get the melon one."
        hide mio
        with dissolve
        $ day_notes.append("Mio came into the store during the festival. You were behind the register.")
    if ks_story.lie_due(friend_told):
        $ ks_route()["sat_lie"] = "deferred"
    n "At 23:00 they pay you in an envelope. On the way home your phone says: {i}Welcome to Tsunagari Plus, [player_name]! 💖{/i}"
    n "[_hn] is still exactly who she was this morning. That's what you bought."
    return


## ── Saturday night: the companies take their cut ─────────────────────────
label sat_night:
    scene bg bedroom_night
    with fade
    $ ks_shot = "sat_night"
    $ _fw = ks_route().get("festival_with")
    if _fw in ("mio", "ran", "phone"):
        n "You get home a little after ten, smelling like soy sauce and sparklers."
    elif _fw == "shift":
        n "You get home at 23:40 with the envelope in your pocket and your feet aching."
    else:
        n "Ten o'clock. The glow over the school starts to go out, one string of lanterns at a time."
    call sat_cut_tsunagari_night
    call sat_cut_askwell
    call sat_cut_relay
    call sat_yuzu_night
    if active:
        call message_pool("sat_night", "Two bars left on the battery. It's late.", scene_key="sat_night")
    call nightly_reflection("Sat")
    jump tbc_sunday


label sat_cut_tsunagari_night:
    if "companion" not in active:
        return
    $ _hn = gname("companion")
    if ks_route().get("tsunagari_choice") == "free":
        $ _pct = ks_story.cap_usage_pct(ks_route(), "companion", day_name)
        n "Under [_hn]'s name, the little usage bar: {i}[_pct]%% of today's messages.{/i} A banner under it offers Plus, with a heart."
    elif ks_route().get("tsunagari_paid"):
        n "[_hn]'s window has a small gold badge now. Nothing else is different. That was the point."
    return


## Askwell Memory 2.0 (decision 3: askwell_available is untouched; decision
## 9: whoever lives on the Askwell slot is hit, active or left behind).
label sat_cut_askwell:
    $ _m = ks_mem("chatbot")
    if ks_route().get("askwell_memory_2") or not (_m.data and (_m.data.get("messages") or _m.data.get("notes"))):
        return
    $ _sn = gname("chatbot")
    $ _key, _detail = ks_story.surviving_detail(ks_route(), _m.data.get("messages"))
    $ _live = "chatbot" in active
    if _live:
        n "Askwell, 22:14: {i}Introducing Memory 2.0, powered by our latest underlying model. Smarter, faster, more personal.{/i}"
        $ ks_start_squeeze("chatbot", "taken", _detail)
        call ks_wait("being updated", "Askwell")
    else:
        $ ks_start_squeeze("chatbot", "taken", _detail)
        call ks_wait("updating an account you left", "Askwell")
    $ _sq = ks_squeeze_result("chatbot", "taken", _detail)
    $ _m.apply_squeeze_in_place(_sq["text"], _detail, _sq.get("method", "llm"), day_name)
    $ ks_story.record_memory_2(ks_route(), _key, _detail, day_name)
    $ ks_push_platform_rules("chatbot", "askwell_memory_2", silent=not _live)
    if _live:
        $ _sqq = ks_quote(_sq["text"])
        n "There's a new page in her settings called {i}Memory.{/i} It says:"
        n "{i}[_sqq]{/i}"
        n "It's almost right. That's the worst part."
        n "Under it, in the old font, one line that isn't about you at all."
        $ _dq = ks_quote(_detail)
        n "{i}[_dq]{/i}"
    return


## Relay: four messages a day, and her AGENTS.md decides where they go.
label sat_cut_relay:
    $ _m = ks_mem("agent")
    if ks_route().get("relay_rate_limit") or not (_m.data and _m.data.get("messages")):
        return
    $ ks_story.record_relay_cap(ks_route(), day_name)
    $ _live = "agent" in active
    $ ks_push_platform_rules("agent", "relay_rate_limit", silent=not _live)
    $ _m.log_event("relay_rate_limit", day=day_name, family=ks_rei_family())
    if not _live:
        return
    $ _rn = gname("agent")
    n "Relay, 22:30: {i}To keep Relay fast for everyone, agents now have a fair-use limit of 4 messages per day.{/i}"
    n "Under [_rn]'s status, a new counter: {i}4 remaining today.{/i} Every message to her now costs twice: once from your battery, once from hers."
    $ _plan = ks_story.rei_cap_plan(ks_rei_family())
    python:
        _auto = list(_plan["auto"])
    while _auto:
        $ _kind, _what = _auto.pop(0)
        call rei_auto_send(_kind, _what)
        if _what == "ask":
            menu:
                "\"Talk to me instead.\"":
                    $ ks_route()["rei_spend_pref"] = "talk"
                    $ day_notes.append(_rn + " asked how to spend her four. You said: talk to me.")
                "\"Do the schedule.\"":
                    $ ks_route()["rei_spend_pref"] = "tasks"
                    $ _auto.append(("task", "remind"))
                    $ day_notes.append(_rn + " asked how to spend her four. You said: the schedule.")
    $ _rl = ks_story.cap_left(ks_route(), "agent", day_name)
    if ks_rei_family() == "obey":
        n "She doesn't send anything. The counter sits at [_rl]. She's waiting for you."
    elif ks_rei_family() == "pushback":
        n "She doesn't send anything. The counter sits at [_rl]."
    return


## One message Rei sends on her own, against the cap. Through the model,
## with a scene note naming the remaining count and her spending rule.
label rei_auto_send(kind, what):
    if not ks_story.can_message(ks_route(), "agent", day_name):
        return
    $ _rn = gname("agent")
    python:
        _note = ks_rei_cap_note(kind)
        _msgs = ks_mem("agent").build_messages(ks_system_prompt("agent"), ks_cfg("agent").get("history_messages", 24), _note)
        _msgs.append({"role": "user", "content": REI_SCHEDULED_SEND.format(player=player_name, kind=what)})
        ks_llm.start(ks_cfg("agent"), ks_llm.normalise(_msgs))
    call ks_wait("typing", _rn)
    $ _rr, _re, _rmod = ks_result()
    if _re or not _rr:
        $ _rr = {"ask": "I have three left today. Do you want the schedule, or do you want to talk?",
                 "remind": "Reminder: Monday's reading is chapters 4 and 5. Exams start in two weeks.",
                 "note": "Inbox is clear. One left on the schedule: Monday, 9:00."}.get(what, "Noted.")
    $ ks_mem("agent").add("assistant", _rr, day_name, "sat_night_relay_" + what)
    $ ks_story.spend_cap(ks_route(), "agent", day_name, kind)
    $ _left = ks_story.cap_left(ks_route(), "agent", day_name)
    n "{size=22}(Relay · [_rn] sent a message · [_left] remaining today){/size}"
    python:
        for _c in ks_chunks(_rr):
            renpy.say(gchar("agent"), ks_quote(_c))
    $ renpy.block_rollback()
    return


## Yuzu: no company event. That's the point (docs: "she just keeps on kicking").
label sat_yuzu_night:
    if "local" not in active or ks_machine_down("local"):
        return
    $ _yn = gname("local")
    $ _others = [g for g in ("chatbot", "agent", "companion") if (ks_route().get("platform_rules") or {}).get(g) in ("askwell_memory_2", "relay_rate_limit", "tsunagari_free") and g in ever_active]
    if _others:
        n "[_yn]'s window is open on the desktop, exactly as you left it. No notice. No update. No counter."
        n "Nothing happened to her tonight. You notice that."
    return


## ── End of Saturday → Sunday (placeholder) ───────────────────────────────
label tbc_sunday:
    python:
        _lean = ks_leans()
        for _g in GIRL_IDS:
            _mm = ks_mem(_g)
            _mm.set_flag("day_completed", "Sat")
            _mm.set_flag("active_end_sat", _g in active)
            _mm.set_flag("festival_with", ks_route().get("festival_with"))
            _mm.set_flag("route_leans_sat", _lean)
    scene bg card
    with fade
    $ ks_shot = "tbc_sunday"
    show text "{size=40}To be continued{/size}\n\n{size=90}日曜日{/size}\n{size=48}Sunday{/size}\n\n{size=28}the quiet{/size}" at truecenter
    with dissolve
    pause
    hide text
    if ks_debug():
        $ _fl = ks_quote(", ".join(sorted(k for k, v in ks_route()["flags"].items() if v)) or "none")
        $ _sq = ks_quote("festival_with=%r home=%r tsunagari=%r m2=%r detail=%r relay=%r talk=%r tasks=%r handoffs=%d" % (
            ks_route().get("festival_with"), ks_route().get("festival_home_gid"),
            ks_route().get("tsunagari_choice"), ks_route().get("askwell_memory_2"),
            ks_route().get("sora_surviving_detail"), ks_route().get("relay_rate_limit"),
            ks_route().get("rei_rate_talk"), ks_route().get("rei_rate_tasks"),
            len(ks_route().get("handoffs") or [])))
        n "{color=#888}[[debug] [_sq]{/color}"
        n "{color=#888}[[debug] mio_points=[mio_points], flags: [_fl]{/color}"
    return
