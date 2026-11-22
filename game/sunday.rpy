## sunday.rpy — Day 7. Sunday, 10 July. The quiet.
## Outline: docs/FRIDAY-SUNDAY.md ("Sunday — the quiet", "Ending reflection",
## decisions 8 and 12) and "Sunday status".
##
## Flow: tbc_sunday (Saturday's card) → sunday (own title card)
##       → morning at home: the shift's ache if you paid for Tsunagari, Daichi's
##         text, then the morning battery (4)
##       → afternoon: Mio (together / missed / friends / distant), Ran if she's
##         in your life, then the afternoon battery (4)
##       → night: the last battery of the week (4), nightly_reflection("Sun")
##       → week_ending (endings.rpy)
##
## No hostile events. Saturday's caps stay on (they're per calendar day):
## Tsunagari Free is 2 a day, Relay is 4 a day, both on top of the battery.
## Scene notes tell each girl the truth of Saturday night.

init python:
    def ks_sun_pool_scene(kind, gid):
        r = ks_route()
        tmpl = {"sun_morning": SUN_MORNING_SCENE, "sun_afternoon": SUN_AFTERNOON_SCENE}.get(kind, SUN_NIGHT_SCENE)
        note = tmpl.format(player=player_name, truth=ks_story.sat_truth(r, gid), name=gname(gid))
        left = ks_story.cap_left(r, gid, store.day_name)
        if gid == "agent" and left is not None:
            note += SUN_CAP_NOTE.format(remaining=left)
        return ks_story.with_situation(note)

    def ks_sun_mio_mode():
        return ks_story.sun_mio_mode(ks_route(), store.mio_real)

    def ks_sun_where_line():
        r = ks_route()
        fw = r.get("festival_with")
        if fw == "home":
            return "\"I stayed home. With " + gname(r.get("festival_home_gid") or "local") + ". I described the lanterns to her.\""
        if fw == "shift":
            return "\"I worked a shift. To pay for an app. For her.\""
        if fw == "phone":
            return "\"I went. Alone. Mostly with my phone.\""
        if fw == "ran":
            return "\"I was at Ran's stall. I said I'd go.\""
        return "\"I stayed in. I didn't want to see anyone. That's the truth.\""

    def ks_sun_cut_hit_someone():
        r = ks_route()
        rules = r.get("platform_rules") or {}
        return any(rules.get(g) in ks_story.SAT_CUT_RULES for g in store.active)


label sunday:
    $ day_name = "Sun"
    $ day_notes = []
    $ today_schedule = {"day": "Sunday", "items": ks_story.sun_schedule()}
    $ ks_route()["rei_day_cap"]["Sun"] = ks_story.cap_left(ks_route(), "agent", "Sun") if ks_story.cap_limit(ks_route(), "agent") else None
    scene bg card
    show text "{size=90}日曜日{/size}\n{size=48}Sunday{/size}" at truecenter
    with dissolve
    pause 1.5
    hide text
    with dissolve

    call sun_morning
    call sun_afternoon
    jump sun_night


## ── Morning ───────────────────────────────────────────────────────────────
label sun_morning:
    scene bg bedroom
    with fade
    $ ks_shot = "sun_morning"
    if ks_route().get("sat_shift"):
        n "Sunday. 10:20. Your feet still hurt from the shift. There's a konbini receipt in your jacket pocket you don't remember keeping."
        if ks_companion_active():
            n "On your phone, a small gold badge next to [dn_companion]'s name. Plus. You paid for that with the festival."
    else:
        n "Sunday. 9:10. The loudspeaker at the school is quiet. Somebody is sweeping up lantern paper in the street."
    call sun_daichi_text
    if not active:
        n "No windows to open. You eat breakfast standing up and look out the window for a while."
        return
    call message_pool("sun_morning", "Four bars on the battery. Sunday gives some back.", scene_key="sun_morning")
    return


label sun_daichi_text:
    n "Your phone buzzes. Daichi."
    $ _sl = ks_route().get("sat_lie")
    if _sl == "caught":
        d "{i}so. the linguist. we're good. i just want you to know i'm going to bring it up at your wedding{/i}"
    elif friend_told == "truth":
        d "{i}tell her i said hi. the AI. whichever one. see you monday{/i}"
    elif ks_route().get("festival_with") in ("none", "home", "shift"):
        d "{i}missed you last night. next year no excuses{/i}"
    else:
        d "{i}good festival. see you monday{/i}"
    return


## ── Afternoon: the last talks with people ────────────────────────────────
label sun_afternoon:
    $ ks_shot = "sun_afternoon"
    call sun_mio
    call sun_ran
    scene bg bedroom
    with fade
    if not active:
        n "The afternoon is long and yellow. You don't mind it as much as you thought you would."
        return
    call message_pool("sun_afternoon", "Home again. The afternoon is yours.", scene_key="sun_afternoon")
    return


label sun_mio:
    $ _mm = ks_sun_mio_mode()
    if _mm == "none":
        return
    if _mm == "distant":
        scene bg bedroom
        with fade
        n "A text from Mio, around two."
        mi "{i}hope your weekend was ok. see you at school{/i}"
        n "Kind. Further away than it used to be."
        $ ks_route()["sun_mio"] = "distant"
        return
    scene bg bookstore
    with fade
    $ ks_shot = "sun_mio"
    if _mm == "together":
        show mio open at ks_center
        with dissolve
        n "Mio texted at noon: {i}kanade books? i have something.{/i} She's by the poetry shelf when you get there."
        mi "I kept one of the lanterns. The paper ones. Don't laugh."
        n "You don't laugh. She shows you a photo of it on her desk, next to a stack of library books."
        if ks_route().get("mio_confession") == "accepted":
            mi "Same time next year? I'm asking early so you can't say you had plans."
        else:
            mi "That was a good night. I'm glad you came."
        $ ks_route()["sun_mio"] = "together"
        $ ks_note_human("sun_mio")
    elif _mm == "missed":
        show mio neutral at ks_center
        with dissolve
        n "She asked to meet. She's already there, not reading the book in her hands."
        mi "You weren't there last night."
        mi "I'm not angry. I just waited by the gate for a while, and then I didn't."
        menu:
            "Tell her where you actually were.":
                $ _wl = ks_sun_where_line()
                p "[_wl]"
                show mio open
                mi "...Okay. Thank you. I'd rather know than guess."
                $ ks_route()["sun_mio"] = "honest"
                $ mio_points += 1
                $ ks_sync_mio()
                $ ks_note_human("sun_mio")
            "\"Something came up.\"":
                mi "Okay."
                n "She lets it go. You can see her decide to."
                $ ks_route()["sun_mio"] = "deflected"
    else:
        show mio neutral at ks_center
        with dissolve
        n "You run into Mio at Kanade Books, which is less of a coincidence than either of you pretends."
        mi "The festival was loud. I liked it anyway. I think."
        $ ks_route()["sun_mio"] = "friends"
        $ ks_note_human("sun_mio")
    if ks_route().get("sun_mio") != "deflected" and (ks_route().get("both_know") or friend_told == "truth") and ks_sun_cut_hit_someone():
        mi "Is she okay? Yours. I heard the companies all did something last night."
        n "You tell her what happened, as well as you understand it. She listens like it's a real thing that happened to someone. It is."
    hide mio
    with dissolve
    return


label sun_ran:
    if not ks_ran_good_terms():
        return
    n "A text from Ran, late afternoon."
    if ks_route().get("festival_with") == "ran":
        ra "{i}stall made 4,200 yen. MUGEN says it was 4,000. MUGEN is wrong. thanks for coming{/i}"
    else:
        ra "{i}stall survived. MUGEN wrote the sign. it says FRESH ICE in a font that should be illegal{/i}"
    return


## ── Night: the last battery of the week ──────────────────────────────────
label sun_night:
    scene bg bedroom_night
    with fade
    $ ks_shot = "sun_night"
    n "Sunday night. Tomorrow is school again. The week is almost over."
    if active:
        call message_pool("sun_night", "Four bars. The last ones this week.", scene_key="sun_night")
    call nightly_reflection("Sun")
    jump week_ending
