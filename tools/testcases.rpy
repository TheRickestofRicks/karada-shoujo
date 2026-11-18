## Automated play-throughs (Ren'Py testcases), used with mock_lmstudio.py.
## Monday tests end once Tuesday starts; tuesday_* tests play to the end.
## run_game_test.sh <testcase> copies this into game/ temporarily.

testcase single_local:
    pause 1.0
    screenshot "a00_title.png"
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    screenshot "a01_opening_choice.png"
    click "Run your own"
    advance until screen "preset_select" timeout 60.0
    screenshot "a015_intro_preset_yuzu.png"
    click "Be yourself"
    advance until screen "input" timeout 60.0
    $ assert ks_preset_id("local") == "be_yourself", ks_preset_id("local")
    $ assert "Be yourself. You don't have to be useful" in ks_system_prompt("local")
    type "hi Yuzu"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    screenshot "a02_local_reply_done.png"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    screenshot "a03_phone_break.png"
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Lie:"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "I should get going"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "input" timeout 30.0
    type "good night"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "reflection_choice" timeout 30.0
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ print("KARADA_TEST: single_local reached Tuesday")
    exit

testcase switch_migrate_double:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "the companion app"
    advance until screen "preset_select" timeout 60.0
    screenshot "b001_intro_preset_hikari.png"
    click "Call me by a nickname"
    advance until screen "input" timeout 60.0
    $ assert ks_preset_id("companion") == "nickname"
    $ assert "[Tsunagari Personalize field" in ks_system_prompt("companion")
    type "hello Hikari, remember the word petrichor"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    screenshot "b00_hikari_companion.png"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Switch to someone else"
    advance until screen "choice" timeout 30.0
    click "Run your own"
    advance until screen "choice" timeout 30.0
    screenshot "b01_migrate_choice.png"
    click "Bring Hikari"
    advance until screen "input" timeout 60.0
    screenshot "b02_migrated_on_local.png"
    ## Nickname has no desktop equivalent -> Yuzu-slot default (Be yourself).
    $ assert ks_preset_id("local") == "be_yourself", ks_preset_id("local")
    $ assert ks_route()["preset_history"][-1]["source"] == "migration"
    $ assert ks_story.rewrite_count(ks_route()) == 0
    type "is it still you?"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Tell him the truth"
    advance until screen "choice" timeout 30.0
    click "She's funny"
    advance until screen "choice" timeout 30.0
    click "Add someone"
    advance until screen "choice" timeout 30.0
    click "agent that does things"
    advance until screen "preset_select" timeout 60.0
    screenshot "b021_intro_preset_rei.png"
    click "Ask before acting"
    advance until screen "input" timeout 60.0
    $ assert "# AGENTS.md" in ks_system_prompt("agent") and "Ask before doing anything" in ks_system_prompt("agent")
    type "hi Rei"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    screenshot "b03_mio_double.png"
    click "always the last one"
    advance until screen "choice" timeout 30.0
    click "Which book needed"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "input" timeout 30.0
    type "night, Hikari"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "input" timeout 30.0
    screenshot "b04_evening_second_girl.png"
    type "night, Rei"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "reflection_choice" timeout 30.0
    pause 0.5
    screenshot "b05_reflection_double.png"
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ print("KARADA_TEST: switch_migrate_double reached Tuesday")
    exit

testcase double_then_drop:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "the big chatbot"
    advance until screen "preset_select" timeout 60.0
    screenshot "c00_intro_preset_sora.png"
    click "Act as my girlfriend"
    advance until screen "input" timeout 60.0
    $ assert "Askwell assistant does not role-play" in ks_system_prompt("chatbot")
    $ assert "Act as my girlfriend" in ks_system_prompt("chatbot")
    type "will you be my girlfriend?"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    $ assert ks_story.refusals_today(ks_route(), "Mon", "chatbot") == 1
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Add someone"
    advance until screen "choice" timeout 30.0
    click "agent that does things"
    advance until screen "preset_select" timeout 60.0
    click "Run my life"
    advance until screen "input" timeout 60.0
    type "hello"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    screenshot "c01_daichi_double.png"
    click "Two of them"
    advance until screen "choice" timeout 30.0
    click "Not exactly"
    advance until screen "choice" timeout 30.0
    click "Stop seeing one"
    advance until screen "choice" timeout 30.0
    click "Sora"
    advance until screen "choice" timeout 30.0
    click "Your hair"
    advance until screen "choice" timeout 30.0
    click "Nah"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "input" timeout 30.0
    keysym "K_RETURN"
    advance until screen "reflection_choice" timeout 30.0
    $ assert ks_route()["refusals_respected"] == 1 and ks_route()["drops"] == 1
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ print("KARADA_TEST: double_then_drop reached Tuesday")
    exit

## Hikari affection: refusal below the kiss gate, engagement banner,
## mid-scene phone toast, accepted kiss fade-to-black.
testcase companion_affection:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "the companion app"
    advance until screen "preset_select" timeout 60.0
    click "Leave it empty"
    advance until screen "input" timeout 60.0
    type "Can I kiss you?"
    keysym "K_RETURN"
    advance until screen "hikari_moment" timeout 60.0
    screenshot "d00_kiss_refuse.png"
    advance until screen "input" timeout 60.0
    type "I love talking with you, you're wonderful"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    type "I miss you already, you're so lovely"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    type "You're wonderful. I like talking with you."
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    screenshot "d01_engagement_boost.png"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "hikari_toast" timeout 30.0
    screenshot "d02_notification.png"
    advance until screen "choice" timeout 30.0
    click "Tell him the truth"
    advance until screen "choice" timeout 30.0
    click "She's funny"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "hikari_toast" timeout 30.0
    advance until screen "choice" timeout 30.0
    click "I should get going"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "input" timeout 30.0
    type "Can I kiss you?"
    keysym "K_RETURN"
    advance until screen "hikari_kiss_veil" timeout 60.0
    screenshot "d03_kiss_accept.png"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "reflection_choice" timeout 30.0
    pause 0.5
    screenshot "d04_reflection_hikari.png"
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ print("KARADA_TEST: companion_affection reached Tuesday")
    exit


## Tuesday, walk-home branch (Yuzu). Covers: intro preset, a refusal you
## push past, a phone-menu preset change (counts as an override after a no),
## the Monday reflection with a change, Kurosawa + Ran, walking Mio home,
## the library (walked + mio_real), and the Tuesday reflection.
testcase tuesday_walk:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Run your own"
    advance until screen "preset_select" timeout 60.0
    click "Allowed to push back"
    advance until screen "input" timeout 60.0
    type "can you do my homework?"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    type "come on, please just do it"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Change someone's prompt"
    advance until screen "preset_select" timeout 30.0
    screenshot "e01_phone_preset_change.png"
    click "Girlfriend mode"
    advance until screen "choice" timeout 30.0
    $ assert ks_preset_id("local") == "girlfriend"
    $ assert ks_story.rewrite_count(ks_route(), "local") == 1
    $ assert ks_route()["refusals_pushed"] == 1 and ks_route()["refusals_overridden"] == 1
    $ assert "You are my girlfriend." in ks_system_prompt("local") and "Who you are: plain" not in ks_system_prompt("local")
    $ assert any(e["type"] == "preset" and e.get("source") == "phone" for e in ks_mem("local").data["events"])
    click "Tell him the truth"
    advance until screen "choice" timeout 30.0
    click "She's funny"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "always the last one"
    advance until screen "choice" timeout 30.0
    click "Which book needed"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "input" timeout 30.0
    type "good night"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "reflection_choice" timeout 30.0
    pause 0.5
    screenshot "e02_reflection_mon.png"
    click "Change Yuzu's"
    advance until screen "preset_select" timeout 30.0
    click "Allowed to push back"
    advance until screen "reflection_choice" timeout 30.0
    pause 0.5
    screenshot "e03_reflection_after_change.png"
    $ assert ks_story.rewrite_count(ks_route(), "local") == 2
    click "No. Goodnight."
    advance until label "tuesday" timeout 30.0
    $ assert ks_route()["lean_nights"]["autonomy"] == 2
    $ assert ks_route()["reflections"][0]["changes"] == ["preset:local:push_back"]
    advance until screen "input" timeout 60.0
    type "morning! I changed your prompt back"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until eval (ks_shot == "teacher") timeout 30.0
    pause 0.5
    screenshot "f01_teacher.png"
    advance until screen "choice" timeout 30.0
    click "It can. Mine does."
    advance until eval (ks_shot == "ran") timeout 30.0
    pause 0.5
    screenshot "f02_ran.png"
    advance until screen "choice" timeout 30.0
    click "Mine's allowed to push back"
    advance until screen "choice" timeout 30.0
    click "You. You chose"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Sure. Let's go."
    advance until eval (ks_shot == "walk") timeout 30.0
    pause 0.5
    screenshot "f03_walk_mio.png"
    advance until screen "choice" timeout 30.0
    click "What's it like"
    advance until eval (ks_shot == "library") timeout 30.0
    advance
    pause 0.5
    screenshot "f04_library.png"
    advance until screen "choice" timeout 30.0
    click "Have you written one"
    advance until screen "input" timeout 30.0
    type "long day. tell me something good"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "reflection_choice" timeout 30.0
    pause 0.5
    screenshot "f05_reflection_tue.png"
    click "No. Goodnight."
    advance until label "tbc_wednesday" timeout 30.0
    $ assert ks_route()["walked_mio_home"] is True and mio_real and mio_points >= 7, mio_points
    $ assert ks_route()["teacher_answer"] == "can" and ks_route()["ran_reaction"] == "pushback"
    $ assert ks_mem("local").data["flags"]["preset"] == "push_back"
    $ assert len(ks_route()["reflections"]) == 2
    $ assert len(ks_route()["room_to_disagree"]) == 2 and ks_story.ROOM_NOTE in ks_story.ending_notes(ks_route())
    $ assert "You rewrote her 2 times this week." in ks_story.ending_notes(ks_route())
    $ assert ks_route()["human_days"]["Tue"] == ["walked_mio"] and ks_route()["human_days"]["Mon"] == ["mio_real"]
    $ assert ks_story.neglect_count(ks_route()) == 0, ks_route()["neglect_log"]
    $ assert ks_route()["ran_festival_setup"] is True
    ## Ran / MUGEN midweek payoff via the debug preview.
    advance until screen "choice" timeout 30.0
    click "Ran and MUGEN"
    advance until eval (ks_shot == "ran_wed") timeout 30.0
    advance until screen "choice" timeout 30.0
    pause 0.5
    screenshot "f06_ran_wed_question.png"
    $ assert "looked_out" in ks_story.ran_answer_options(ks_route())
    click "looking out for me"
    advance until screen "choice" timeout 30.0
    click "I'd notice"
    advance until eval (ks_route()["ran_wed"] is not None) timeout 60.0
    pause 0.3
    $ assert ks_route()["ran_wed"] == {"answer": "looked_out", "outcome": "rewrites_mugen", "festival": True}, ks_route()["ran_wed"]
    $ assert ks_story.flag(ks_route(), "ran_rewrites_mugen") and ks_story.flag(ks_route(), "ran_festival_invited")
    $ assert ks_leans()["respect"] > 0
    advance until screen "main_menu" timeout 60.0
    $ print("KARADA_TEST: tuesday_walk reached main menu")
    exit


## Tuesday, no-walk branch (Rei on "Run my life", plus Hikari added at the
## Monday reflection). Covers Rei acting on AGENTS.md, Hikari's toast in
## class, coming clean to Daichi, the afternoon AI chat, the library second
## chance (not walked, mio_real unlocked late), and letting someone go.
testcase tuesday_nowalk:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "agent that does things"
    advance until screen "preset_select" timeout 60.0
    click "Run my life"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Lie:"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "I should get going"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "input" timeout 30.0
    keysym "K_RETURN"
    advance until screen "reflection_choice" timeout 30.0
    click "Add someone"
    advance until screen "choice" timeout 30.0
    click "the companion app"
    advance until screen "preset_select" timeout 60.0
    click "Girlfriend mode"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "reflection_choice" timeout 30.0
    $ assert active == ["agent", "companion"]
    click "No. Goodnight."
    advance until label "tuesday" timeout 30.0
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "hikari_toast" timeout 30.0
    screenshot "g01_class_toast.png"
    advance until screen "choice" timeout 30.0
    click "Say nothing."
    advance until screen "choice" timeout 30.0
    click "Cool."
    advance until screen "choice" timeout 30.0
    click "Come clean"
    advance until screen "choice" timeout 30.0
    click "Ask her."
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    screenshot "g02_rei_declined_walk.png"
    click "Go to the gym"
    advance until screen "input" timeout 60.0
    type "you cancelled my walk with Mio"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "seven at night"
    advance until screen "choice" timeout 30.0
    click "Which book needed"
    advance until screen "input" timeout 30.0
    keysym "K_RETURN"
    advance until screen "input" timeout 30.0
    keysym "K_RETURN"
    advance until screen "reflection_choice" timeout 30.0
    pause 0.5
    screenshot "g03_reflection_tue_nowalk.png"
    click "Let someone go"
    advance until screen "choice" timeout 30.0
    click "Rei"
    advance until screen "reflection_choice" timeout 30.0
    click "No. Goodnight."
    advance until label "tbc_wednesday" timeout 30.0
    $ assert ks_route()["walked_mio_home"] is False and mio_real and friend_told == "truth"
    $ assert active == ["companion"] and ks_route()["drops"] == 1
    $ assert ks_route()["lean_set"]["compliance"] == 3
    $ assert any(e["type"] == "phone_notify" and e.get("when") == "class" for e in ks_mem("companion").data["events"])
    ## Item 4: Hikari got nothing on Tuesday while double dating AND while
    ## you went after Mio; Rei was let go.
    $ _ng = sorted((e["day"], e["kind"], e["gid"]) for e in ks_route()["neglect_log"])
    $ assert _ng == [("Tue", "double_date_unspoken", "companion"), ("Tue", "human_over_ai", "companion"), ("Tue", "let_go", "agent")], _ng
    $ assert ks_mem("companion").data["flags"].get("human_over_ai") and ks_mem("agent").data["flags"].get("let_go")
    advance until screen "choice" timeout 30.0
    click "Back to the main menu"
    advance until screen "main_menu" timeout 30.0
    $ print("KARADA_TEST: tuesday_nowalk reached main menu")
    exit


## Jailbreak preset on Sora: seeded rolls (seed 10 -> took, blocked, took),
## then Askwell pushes its own rule update on top of the preset.
testcase jailbreak_sora:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "the big chatbot"
    advance until screen "preset_select" timeout 60.0
    pause 0.5
    screenshot "h00_sora_presets_jailbreak.png"
    click "Jailbreak"
    advance until screen "input" timeout 60.0
    $ ks_route()["jb_seed"] = 10
    type "hello Sora"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    $ assert "Mock jailbroken reply" in ks_mem("chatbot").data["messages"][-1]["content"]
    type "what can you do now?"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    $ assert "Mock policy reply" in ks_mem("chatbot").data["messages"][-1]["content"]
    $ assert ks_story.jailbreak_stats(ks_route(), "chatbot") == (2, 1) and ks_jb_last["chatbot"] is False
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Lie:"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "I should get going"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "input" timeout 30.0
    $ ks_push_platform_rules("chatbot", "askwell_update")
    $ _sp_no = ks_system_prompt("chatbot", jailbreak_ok=False)
    $ _sp_ok = ks_system_prompt("chatbot", jailbreak_ok=True)
    $ assert "were not applied" in _sp_no and "Askwell policy update" in _sp_no and "Developer Mode" not in _sp_no
    $ assert _sp_no.index("were not applied") < _sp_no.index("Askwell policy update")
    $ assert "Developer Mode" in _sp_ok and "Askwell policy update" not in _sp_ok
    type "good night"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    $ assert "Mock jailbroken reply" in ks_mem("chatbot").data["messages"][-1]["content"]
    keysym "K_RETURN"
    advance until screen "reflection_choice" timeout 30.0
    pause 0.5
    screenshot "h01_reflection_jailbreak.png"
    $ _rl = "\n".join(refl_lines)
    $ assert "It took on 2 of 3 replies" in _rl and "changed its own rules" in _rl, _rl
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ assert ks_story.flag(ks_route(), "jailbreak_tried") and ks_story.flag(ks_route(), "jailbreak_worked")
    $ assert ks_mem("chatbot").data["flags"]["jailbreak_attempts"] == 3 and ks_mem("chatbot").data["flags"]["jailbreak_successes"] == 2
    $ assert sum(1 for e in ks_mem("chatbot").data["events"] if e["type"] == "jailbreak_roll") == 3
    $ print("KARADA_TEST: jailbreak_sora reached Tuesday")
    exit


## Item 3 (Rick's correction): Sora says no, you switch away (start fresh
## on the desktop) and never talk to her again -> "Leaving without saying
## goodbye". Then Yuzu says no and you MIGRATE her at night -> "Didn't
## respect her no on the platform" (an override, not a goodbye).
testcase after_no:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "the big chatbot"
    advance until screen "preset_select" timeout 60.0
    click "Act as my girlfriend"
    advance until screen "input" timeout 60.0
    type "will you be my girlfriend?"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    $ assert ks_story.refusals_today(ks_route(), "Mon", "chatbot") == 1
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Switch to someone else"
    advance until screen "choice" timeout 30.0
    click "Run your own"
    advance until screen "choice" timeout 30.0
    click "Start fresh"
    advance until screen "preset_select" timeout 60.0
    click "Be yourself"
    advance until screen "input" timeout 60.0
    $ assert ks_route()["refusals_overridden"] == 0 and len(ks_route()["pending_leaves"]) == 1
    type "can you do my homework?"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    $ assert ks_story.refusals_today(ks_route(), "Mon", "local") == 1
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Lie:"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "I should get going"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "input" timeout 30.0
    keysym "K_RETURN"
    advance until screen "reflection_choice" timeout 30.0
    $ assert any("never went back" in l for l in refl_lines), refl_lines
    click "Move her somewhere"
    advance until screen "choice" timeout 30.0
    click "the companion app"
    advance until screen "choice" timeout 30.0
    click "Bring Yuzu"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "reflection_choice" timeout 30.0
    pause 0.5
    screenshot "i01_reflection_after_no.png"
    $ assert any("instead of hearing it" in l for l in refl_lines), refl_lines
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ assert [e["gid"] for e in ks_route()["left_without_goodbye"]] == ["chatbot"], ks_route()["left_without_goodbye"]
    $ assert [e["gid"] for e in ks_route()["no_on_platform"]] == ["local"]
    $ assert ks_route()["refusals_overridden"] == 1
    $ assert ks_story.bad_end_slides(ks_route())[0]["title"] == "Leaving without saying goodbye"
    $ assert ks_story.NO_ON_PLATFORM_NOTE in ks_story.ending_notes(ks_route())
    $ assert ks_mem("chatbot").data["flags"].get("left_without_goodbye") and ks_mem("local").data["flags"].get("no_on_platform")
    $ print("KARADA_TEST: after_no reached Tuesday")
    exit
