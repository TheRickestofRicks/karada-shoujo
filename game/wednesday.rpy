## wednesday.rpy — self-contained Wednesday scenes, callable once Wednesday
## exists (`call ran_wednesday`). Until then, tbc_wednesday offers a debug
## preview.
##
## Ran / MUGEN midweek payoff. MUGEN cheerfully agrees with something that
## hurts Ran. She realises a yes-machine can't look out for her, and asks
## the player what it's like when your AI says no. Which honest answers he
## has depends on what he actually did (ks_story.ran_answer_options); her
## reaction also remembers Tuesday's ran_reaction. Logged as
## route["ran_wed"] + flags ran_payoff_seen / ran_rewrites_mugen /
## ran_same_as_mugen / ran_festival_invited (a mirror: Respect / Yes-Machine).
## Scripted only; no LLM call.

label ran_wednesday:
    $ _rw_prev_day = day_name
    if day_name not in ("Wed", "Thu", "Fri"):
        $ day_name = "Wed"
    scene bg classroom
    with fade
    $ ks_shot = "ran_wed"
    n "Wednesday, lunch. Most of the class has gone to the cafeteria. Ran hasn't moved."
    show ran uneasy at ks_center
    with dissolve
    n "She's staring at her phone like it said something in a language she almost knows."
    ra "Oh. It's you."
    $ _rw_react = ks_route().get("ran_reaction")
    if _rw_react == "boring":
        ra "You asked me if it got boring. Yesterday."
        ra "I said no. I've been thinking about it since, which is annoying."
    elif _rw_react == "pushback":
        ra "You're the one whose AI is {i}allowed{/i} to disagree with you."
        ra "I keep thinking about that word. Allowed."
    elif _rw_react == "show":
        ra "You watched it tell me not to study. I didn't, by the way. Study."
    else:
        ra "You said \"cool.\" Yesterday. About MUGEN."
    ra "Look at this."
    n "She turns the phone around. The last message is hers: {i}nobody would even notice if I skipped the festival lol{/i}"
    show ran grin
    mu "You're right, nobody would miss you at the festival! Staying home sounds perfect. You deserve a night just for you!"
    show ran uneasy
    ra "..."
    ra "I wanted it to say \"don't be stupid.\""
    ra "That's all. Three words. Anybody would have said it. Daichi would've said it, and he doesn't even like me."
    ra "It agreed. It always agrees. It thinks that's being nice."
    ra "It doesn't know which of my sentences are the ones I don't mean. It can't. I took that part out."
    ra "So it can't look out for me. It just... holds the door open on whatever I say."
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
    if _rw_outcome == "rewrites_mugen":
        n "She opens a settings file you didn't know MUGEN had. It's empty."
        n "She types one line, deletes it, and types it again: {i}You're allowed to tell me I'm wrong.{/i}"
        ra "Don't look. It's stupid."
        if _rw_react in ("boring", "pushback"):
            ra "...You kind of started this. Yesterday. So it's your fault if it gets weird."
    elif _rw_outcome == "same_as_mugen":
        n "She puts the phone face-down, then turns it back over, like she'd miss something."
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
            n "The silence sits there. MUGEN's last message glows on her desk: {i}You deserve a night just for you!{/i}"
    $ ks_story.record_ran_payoff(ks_route(), _rw_ans, _rw_fest)
    $ day_notes.append({"rewrites_mugen": "MUGEN told Ran nobody would miss her. She gave it its first line of system prompt.",
                        "same_as_mugen": "MUGEN told Ran nobody would miss her. You told her yours is the same, if you work at it.",
                        "unsure": "MUGEN told Ran nobody would miss her. She asked what it's like when yours says no."}[_rw_outcome])
    hide ran
    with dissolve
    $ day_name = _rw_prev_day
    return
