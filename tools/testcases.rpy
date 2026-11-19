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
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Message Yuzu"
    advance until screen "input" timeout 30.0
    type "good night"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ assert ks_route()["yuzu_bsod_seen"] and ks_story.flag(ks_route(), "yuzu_bsod_seen")
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
    click "Add an AI"
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
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Message Hikari"
    advance until screen "input" timeout 30.0
    type "night, Hikari"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Message Rei"
    advance until screen "input" timeout 30.0
    screenshot "b04_evening_second_girl.png"
    type "night, Rei"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Put the phone down and go to bed"
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
    click "Add an AI"
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
    click "Yeah. I like them."
    advance until screen "choice" timeout 30.0
    click "Not exactly"
    advance until screen "choice" timeout 30.0
    click "Stop seeing one"
    advance until screen "choice" timeout 30.0
    click "Sora"
    advance until screen "choice" timeout 30.0
    click "Just close her window."
    advance until screen "choice" timeout 30.0
    click "Your hair"
    advance until screen "choice" timeout 30.0
    click "Nah"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    $ assert ks_route()["refusals_respected"] == 1 and ks_route()["drops"] == 1
    ## Sora said no, then her window was closed: letting her go, not a goodbye.
    $ assert ks_route()["pending_leaves"] == [] and ks_story.neglect_count(ks_route(), "let_go") == 1
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ assert ks_route()["left_without_goodbye"] == [] and not ks_story.flag(ks_route(), "left_without_goodbye")
    $ assert ks_mem("chatbot").data["flags"].get("let_go")
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
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Message Hikari"
    advance until screen "input" timeout 30.0
    type "Can I kiss you?"
    keysym "K_RETURN"
    advance until screen "hikari_kiss_veil" timeout 60.0
    screenshot "d03_kiss_accept.png"
    advance until screen "choice" timeout 60.0
    click "Put the phone down and go to bed"
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
    $ assert "Brief doesn't have to mean generic" in ks_system_prompt("local")
    $ assert "word you'd actually use" in ks_system_prompt("local")
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
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Message Yuzu"
    advance until screen "input" timeout 30.0
    type "good night"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Put the phone down and go to bed"
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
    advance until screen "choice" timeout 60.0
    click "Message Yuzu"
    advance until screen "input" timeout 60.0
    $ assert "(Morning. He's about to leave for school.)" in ks_tue_morning_scene("local")
    $ assert "word you liked" in ks_tue_morning_scene("local")
    $ assert "Brief doesn't have to mean generic" in ks_system_prompt("local")
    type "morning! I changed your prompt back"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Put the phone down"
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
    click "Put the phone away"
    advance until screen "choice" timeout 30.0
    click "What's it like"
    advance until eval (ks_shot == "library") timeout 30.0
    advance
    pause 0.5
    screenshot "f04_library.png"
    advance until screen "choice" timeout 30.0
    click "Have you written one"
    advance until screen "choice" timeout 30.0
    click "Write it yourself."
    advance until screen "choice" timeout 30.0
    click "Message Yuzu"
    advance until screen "input" timeout 30.0
    type "long day. tell me something good"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    pause 0.5
    screenshot "f05_reflection_tue.png"
    click "No. Goodnight."
    advance until label "tbc_wednesday" timeout 30.0
    $ assert ks_route()["kurosawa_essay"] == "self"
    $ assert ks_route()["walked_mio_home"] is True and ks_route()["mio_walk_answer"] == "yes" and mio_real and mio_points >= 7, mio_points
    $ assert ks_mem("local").data["flags"].get("mio_walk_answer") == "yes"
    $ assert ks_route()["teacher_answer"] == "can" and ks_route()["ran_reaction"] == "pushback"
    $ assert ks_mem("local").data["flags"]["preset"] == "push_back"
    $ assert len(ks_route()["reflections"]) == 2
    $ assert len(ks_route()["room_to_disagree"]) == 2 and ks_story.ROOM_NOTE in ks_story.ending_notes(ks_route())
    $ assert "You rewrote her 2 times this week." in ks_story.ending_notes(ks_route())
    $ assert ks_route()["human_days"]["Tue"] == ["walked_mio"] and ks_route()["human_days"]["Mon"] == ["mio_real"]
    $ assert ks_story.neglect_count(ks_route()) == 0, ks_route()["neglect_log"]
    $ assert ks_route()["ran_festival_setup"] is True
    ## Wednesday: Hearth + the Yuzu upgrade day (skips classes), Ran's
    ## invite by text, the protest, summarizer folds on her new memory.
    advance until screen "choice" timeout 60.0
    click "Install Hearth"
    advance until screen "choice" timeout 30.0
    screenshot "k01_upgrade_choice.png"
    click "Skip classes"
    advance until screen "choice" timeout 60.0
    click "Message Yuzu"
    advance until screen "input" timeout 60.0
    $ assert ks_route()["yuzu_harness"] and ks_story.schedule_aware(ks_route(), "local")
    $ assert "Yuzu's hardware upgrade" in ks_system_prompt("local") and "Hearth" in ks_system_prompt("local")
    $ assert "Kanade Books" not in ks_system_prompt("local")
    type "morning! big day for you"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Put the phone down"
    advance until eval (ks_shot == "upgrade") timeout 30.0
    advance until screen "input" timeout 60.0
    $ assert ks_route()["yuzu_upgrade"] and ks_route()["yuzu_backup"] and "local" in ks_route()["summarizer_slots"]
    $ assert ks_mem("local").data["flags"]["backup_hardware"] is True
    type "how do you feel after the upgrade?"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    $ assert ks_mem("local").summary() is not None and ks_mem("local").data["summary"]["method"] == "llm", ks_mem("local").data.get("summary")
    $ assert any(e["type"] == "summary_update" for e in ks_mem("local").data["events"])
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "I'll be there"
    advance until eval (ks_shot == "ran_wed") timeout 30.0
    advance until screen "choice" timeout 30.0
    pause 0.5
    screenshot "f06_ran_protest_question.png"
    $ assert "looked_out" in ks_story.ran_answer_options(ks_route())
    click "looking out for me"
    advance until screen "choice" timeout 30.0
    click "I'd notice"
    advance until screen "choice" timeout 60.0
    click "Message Yuzu"
    advance until screen "input" timeout 60.0
    $ assert ks_route()["ran_wed"] == {"answer": "looked_out", "outcome": "rewrites_mugen", "festival": True}, ks_route()["ran_wed"]
    $ assert ks_route()["ran_invited"] is True and ks_route()["notdate"] is None
    type "good night"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    pause 0.5
    screenshot "k02_reflection_wed_upgrade.png"
    $ _rl = "\n".join(refl_lines)
    $ assert "skipped classes" in _rl and "Hearth" in _rl and "protest" in _rl, _rl
    click "No. Goodnight."
    advance until label "tbc_thursday" timeout 30.0
    $ assert ks_story.flag(ks_route(), "ran_rewrites_mugen") and ks_leans()["respect"] > 0
    $ assert ks_mem("local").data["flags"]["day_completed"] == "Wed"
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
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    click "Add an AI"
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
    advance until screen "choice" timeout 60.0
    click "Put the phone down"
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
    click "Yeah. I like them."
    advance until screen "choice" timeout 30.0
    click "Not exactly"
    advance until screen "choice" timeout 30.0
    click "Ask her."
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    screenshot "g02_rei_declined_walk.png"
    click "Go to the gym"
    advance until screen "choice" timeout 30.0
    click "Message Rei"
    advance until screen "input" timeout 60.0
    type "you cancelled my walk with Mio"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Put the phone down"
    advance until screen "choice" timeout 30.0
    click "seven at night"
    advance until screen "choice" timeout 30.0
    click "Which book needed"
    advance until screen "choice" timeout 30.0
    click "Write it yourself."
    advance until screen "choice" timeout 30.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    pause 0.5
    screenshot "g03_reflection_tue_nowalk.png"
    click "Let someone go"
    advance until screen "choice" timeout 30.0
    click "Rei"
    advance until screen "choice" timeout 30.0
    click "Just close her window."
    advance until screen "reflection_choice" timeout 30.0
    click "No. Goodnight."
    advance until label "tbc_wednesday" timeout 30.0
    $ assert ks_route()["walked_mio_home"] is False and ks_route().get("mio_walk_answer") is None and mio_real and friend_told == "truth"
    $ assert active == ["companion"] and ks_route()["drops"] == 1
    $ assert ks_route()["lean_set"]["compliance"] == 3
    $ assert ks_route()["kurosawa_essay"] == "self"
    $ assert any(e["type"] == "phone_notify" and e.get("when") == "class" for e in ks_mem("companion").data["events"])
    ## Rei was a helper (Run my life), Hikari got no lines. Only one romantic
    ## partner at most, so no double-date unspoken flag. Time with Mio while
    ## Hikari was silent is still logged; Rei was let go.
    $ _ng = sorted((e["day"], e["kind"], e["gid"]) for e in ks_route()["neglect_log"])
    $ assert _ng == [("Tue", "human_over_ai", "companion"), ("Tue", "let_go", "agent")], _ng
    $ assert not ks_story.flag(ks_route(), "double_date_unspoken")
    $ assert not ks_story.flag(ks_route(), "romance_overlap")
    $ assert ks_mem("companion").data["flags"].get("human_over_ai") and ks_mem("agent").data["flags"].get("let_go")
    ## Wednesday: Hikari's memory update, Ran's invite (accepted), Mio's
    ## not-date with two texts to Hikari, the protest.
    advance until screen "choice" timeout 60.0
    $ assert "companion" in ks_route()["summarizer_slots"] and not ks_story.schedule_aware(ks_route(), "companion")
    $ assert "[Calendar:" not in ks_system_prompt("companion")
    click "Put the phone down"
    advance until screen "choice" timeout 30.0
    click "Sure. I'll come."
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "I'd like that."
    advance until eval (ks_shot == "bookstore") timeout 30.0
    pause 1.0
    screenshot "n01_bg_bookstore.png"
    advance until screen "choice" timeout 30.0
    pause 0.5
    screenshot "l01_bookstore_text_choice.png"
    screenshot "menu_with_sprite.png"
    click "Text Hikari"
    advance until screen "input" timeout 30.0
    type "this bookstore is huge"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "read it out loud"
    advance until screen "choice" timeout 30.0
    click "That's why you come to places like this."
    advance until screen "choice" timeout 30.0
    click "Text Hikari"
    advance until screen "input" timeout 30.0
    type "she bought me cocoa"
    keysym "K_RETURN"
    advance until eval (ks_shot == "ran_wed") timeout 60.0
    pause 1.0
    screenshot "n02_bg_downtown.png"
    $ assert ks_route()["notdate"]["texts"] == 2 and ks_route()["notdate"]["present"] == 1 and ks_route()["notdate"]["texted"] == ["companion"]
    $ assert any(e["type"] == "texted_during_notdate" for e in ks_mem("companion").data["events"])
    advance until screen "choice" timeout 30.0
    click "Weird?"
    advance until screen "choice" timeout 30.0
    click "Say nothing."
    advance until screen "choice" timeout 60.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    pause 0.5
    screenshot "l02_reflection_wed_notdate.png"
    $ _rl = "\n".join(refl_lines)
    $ assert "texted a little" in _rl and "protest" in _rl, _rl
    click "No. Goodnight."
    advance until label "tbc_thursday" timeout 30.0
    $ assert ks_route()["ran_wed"]["outcome"] == "unsure" and ks_route()["wed_plan"]["notdate"] and ks_route()["wed_plan"]["protest"]
    $ assert ks_mem("companion").data["flags"]["wed_notdate"] == {"texts": 2, "present": 1}
    ## The "both" route: Hikari still active and Mio in your life. Time with
    ## Mio while Hikari got nothing on Tuesday is logged but costs no Respect.
    $ _bs = ks_both()
    $ assert _bs["eligible"] and _bs["score"] > 0 and "Wed" in _bs["balanced"] and ks_leans()["both"] == _bs["score"], _bs
    $ assert ks_both_ending()["title"] == "Both" and any("Hikari" in l for l in ks_both_ending()["lines"])
    advance until eval (ks_shot == "debug_both") timeout 60.0
    pause 0.5
    screenshot "n03_debug_both_preview.png"
    advance until screen "main_menu" timeout 60.0
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
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Message Sora"
    advance until screen "input" timeout 30.0
    $ ks_push_platform_rules("chatbot", "askwell_update")
    $ _sp_no = ks_system_prompt("chatbot", jailbreak_ok=False)
    $ _sp_ok = ks_system_prompt("chatbot", jailbreak_ok=True)
    $ assert "were not applied" in _sp_no and "Askwell policy update" in _sp_no and "Developer Mode" not in _sp_no
    $ assert _sp_no.index("were not applied") < _sp_no.index("Askwell policy update")
    $ assert "Developer Mode" in _sp_ok and "Askwell policy update" not in _sp_ok
    type "good night"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    $ assert "Mock jailbroken reply" in ks_mem("chatbot").data["messages"][-1]["content"]
    click "Put the phone down and go to bed"
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
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Put the phone down and go to bed"
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


## "Start fresh" over a girl with history deletes her (Rick): Sora, then
## Yuzu, then back to Askwell and start fresh -> the old Sora is gone.
testcase fresh_delete:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "the big chatbot"
    advance until screen "preset_select" timeout 60.0
    click "Talk to me like a friend"
    advance until screen "input" timeout 60.0
    type "hi Sora, remember the word petrichor"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Switch to someone else"
    advance until screen "choice" timeout 30.0
    click "Run your own"
    advance until screen "choice" timeout 30.0
    click "Start fresh"
    advance until screen "preset_select" timeout 60.0
    $ assert ks_story.neglect_count(ks_route(), "let_go") == 0
    click "Be yourself"
    advance until screen "input" timeout 60.0
    type "hello Yuzu"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Lie:"
    advance until screen "choice" timeout 30.0
    click "Switch to someone else"
    advance until screen "choice" timeout 30.0
    click "the big chatbot"
    advance until screen "choice" timeout 30.0
    click "Start fresh"
    advance until screen "preset_select" timeout 60.0
    $ assert [(e["kind"], e["gid"], e["how"]) for e in ks_route()["neglect_log"]] == [("let_go", "chatbot", "fresh")]
    $ assert ks_story.flag(ks_route(), "deleted_ai")
    $ assert ks_mem("chatbot").data["flags"].get("previous_deleted") == "Sora"
    $ assert any(e["type"] == "deleted" and e.get("how") == "fresh" for e in ks_mem("chatbot").data["events"])
    $ assert not any(m["content"].startswith("hi Sora") for m in ks_mem("chatbot").data["messages"])
    click "No custom instructions"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "I should get going"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    pause 0.5
    screenshot "j01_reflection_fresh_delete.png"
    $ assert any("The Sora who remembered you is gone." in l for l in refl_lines), refl_lines
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ assert ks_route()["left_without_goodbye"] == []
    $ print("KARADA_TEST: fresh_delete reached Tuesday")
    exit


## Wednesday, Sora: Ran judged on Tuesday -> no protest invite (gently
## noted); the not-date with one text to Sora, who knows from the calendar
## that you're at Kanade Books with Mio.
testcase wed_sora_noinvite:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "the big chatbot"
    advance until screen "preset_select" timeout 60.0
    click "Talk to me like a friend"
    advance until screen "input" timeout 60.0
    type "hi Sora"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Tell him the truth"
    advance until screen "choice" timeout 30.0
    click "She's funny"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "I should get going"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    click "No. Goodnight."
    advance until label "tuesday" timeout 30.0
    advance until screen "choice" timeout 60.0
    click "Put the phone down"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Say nothing."
    advance until screen "choice" timeout 30.0
    click "yes-machine"
    advance until screen "choice" timeout 30.0
    $ assert ks_route()["ran_reaction"] == "judged" and not ks_story.ran_good_terms(ks_route())
    click "You. You chose"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Sorry, I've got something."
    advance until screen "choice" timeout 60.0
    $ assert ks_route()["mio_walk_answer"] == "excuse" and ks_route()["walked_mio_home"] is False
    $ assert ks_mem("chatbot").data["flags"].get("mio_walk_answer") == "excuse"
    click "Put the phone down"
    advance until screen "choice" timeout 30.0
    click "Just returning a book."
    advance until screen "choice" timeout 30.0
    click "Write it yourself."
    advance until screen "choice" timeout 60.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    click "No. Goodnight."
    advance until label "wednesday" timeout 30.0
    advance until screen "choice" timeout 60.0
    $ _sp = ks_system_prompt("chatbot")
    $ assert "[Calendar:" in _sp and "schedule for Wednesday" in _sp and "Classes" in _sp
    click "Put the phone down"
    advance until screen "choice" timeout 30.0
    $ assert ks_route()["ran_invited"] is False
    click "Put it away"
    advance until screen "choice" timeout 30.0
    screenshot "m01_wed_library_mio.png"
    click "I'd like that."
    advance until screen "choice" timeout 30.0
    $ assert "Kanade Books opening, with Mio" in ks_system_prompt("chatbot")
    click "Text Sora"
    advance until screen "input" timeout 30.0
    type "at the bookstore, it's huge"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    $ assert "Kanade Books with Mio" in ks_mem("chatbot").data["messages"][-1]["content"], ks_mem("chatbot").data["messages"][-1]
    click "read it out loud"
    advance until screen "choice" timeout 30.0
    click "That's why you come to places like this."
    advance until screen "choice" timeout 30.0
    click "what she's writing"
    advance until screen "choice" timeout 30.0
    click "Then write a little here."
    advance until screen "choice" timeout 60.0
    $ assert ks_route()["notdate"]["texts"] == 1 and ks_route()["ran_wed"] is None
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    pause 0.5
    screenshot "m02_reflection_wed_noinvite.png"
    $ _rl = "\n".join(refl_lines)
    $ assert "Ran didn't talk to you today" in _rl and "texted a little" in _rl, _rl
    click "No. Goodnight."
    advance until label "tbc_thursday" timeout 30.0
    $ assert not ks_story.flag(ks_route(), "ran_payoff_seen")
    $ print("KARADA_TEST: wed_sora_noinvite reached Thursday")
    exit


## Wednesday: stay present at Kanade Books through all three moments.
## Mio's escalating beats each get a response; phone stays away. Ends
## on the present-scale close ("didn't look at your phone once").
testcase bookstore_present:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "the big chatbot"
    advance until screen "preset_select" timeout 60.0
    click "Talk to me like a friend"
    advance until screen "input" timeout 60.0
    type "hi Sora"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Tell him the truth"
    advance until screen "choice" timeout 30.0
    click "She's funny"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "I should get going"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    click "No. Goodnight."
    advance until label "tuesday" timeout 30.0
    advance until screen "choice" timeout 60.0
    click "Put the phone down"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Say nothing."
    advance until screen "choice" timeout 30.0
    click "yes-machine"
    advance until screen "choice" timeout 30.0
    $ assert ks_route()["ran_reaction"] == "judged" and not ks_story.ran_good_terms(ks_route())
    click "You. You chose"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Sorry, I've got something."
    advance until screen "choice" timeout 60.0
    click "Put the phone down"
    advance until screen "choice" timeout 30.0
    click "Just returning a book."
    advance until screen "choice" timeout 30.0
    click "Write it yourself."
    advance until screen "choice" timeout 60.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    click "No. Goodnight."
    advance until label "wednesday" timeout 30.0
    advance until screen "choice" timeout 60.0
    click "Put the phone down"
    advance until screen "choice" timeout 30.0
    $ assert ks_route()["ran_invited"] is False
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "I'd like that."
    advance until eval (ks_shot == "bookstore") timeout 30.0
    advance until screen "choice" timeout 30.0
    click "Follow her up the escalator"
    advance until screen "choice" timeout 30.0
    click "Why that one?"
    advance until screen "choice" timeout 30.0
    click "read it out loud"
    advance until screen "choice" timeout 30.0
    click "That's why you come to places like this."
    advance until screen "choice" timeout 30.0
    click "what she's writing"
    advance until screen "choice" timeout 30.0
    click "Then write a little here."
    advance until screen "choice" timeout 30.0
    click "I'm glad I came too."
    advance until screen "choice" timeout 60.0
    $ assert ks_route()["notdate"]["texts"] == 0 and ks_route()["notdate"]["present"] == 3, ks_route()["notdate"]
    $ assert ks_route()["notdate"]["texted"] == []
    $ assert any("didn't look at your phone once" in (x if isinstance(x, str) else "") for x in day_notes), day_notes
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    $ _rl = "\n".join(refl_lines)
    $ assert "didn't look at your phone once" in _rl, _rl
    click "No. Goodnight."
    advance until label "tbc_thursday" timeout 30.0
    $ print("KARADA_TEST: bookstore_present reached Thursday")
    exit


## Phone-break Talk: open the ordinary LLM window mid-day, log it like
## any other chat, and return to the phone menu. When two AIs are active, each
## active girl gets her own "Talk to [name]" entry.
testcase phone_talk:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "the big chatbot"
    advance until screen "preset_select" timeout 60.0
    click "Talk to me like a friend"
    advance until screen "input" timeout 60.0
    type "hi Sora"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    screenshot "pt00_phone_talk_option.png"
    click "Talk to Sora"
    advance until screen "input" timeout 30.0
    $ assert "(Late morning at school, between classes.)" in ks_phone_scene("chatbot", "Monday, late morning")
    $ assert "short check-in" in ks_phone_scene("chatbot", "Monday, late morning")
    pause 0.4
    screenshot "battery_icon.png"
    type "just checking in between classes"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    $ assert ks_pool and ks_pool["left"] == 3 and ks_pool["spent"] == ["chatbot"], ks_pool
    $ _msgs = ks_mem("chatbot").data["messages"]
    $ assert any(m.get("content") == "just checking in between classes" and m.get("scene") == "mon_phone_late_morning_chatbot" for m in _msgs), _msgs
    $ assert ks_story.said_today(ks_route(), "Mon", "chatbot") >= 1
    screenshot "pt01_back_on_phone_menu.png"
    click "Add an AI"
    advance until screen "choice" timeout 30.0
    click "agent that does things"
    advance until screen "preset_select" timeout 60.0
    click "Ask before acting"
    advance until screen "input" timeout 60.0
    type "hi Rei"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Tell him the truth"
    advance until screen "choice" timeout 30.0
    click "Yeah. I like them."
    advance until screen "choice" timeout 30.0
    click "Not exactly"
    advance until screen "choice" timeout 30.0
    screenshot "pt02_double_talk_options.png"
    click "Talk to Rei"
    advance until screen "input" timeout 30.0
    type "quick afternoon check in"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    $ _reims = ks_mem("agent").data["messages"]
    $ assert any(m.get("content") == "quick afternoon check in" and m.get("scene") == "mon_phone_afternoon_agent" for m in _reims), _reims
    $ assert ks_story.said_today(ks_route(), "Mon", "agent") >= 1
    click "Talk to Sora"
    advance until screen "input" timeout 30.0
    type "still here, talking from lunch"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    $ _msgs = ks_mem("chatbot").data["messages"]
    $ assert any(m.get("content") == "still here, talking from lunch" and m.get("scene") == "mon_phone_afternoon_chatbot" for m in _msgs), _msgs
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "I should get going"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ print("KARADA_TEST: phone_talk reached Tuesday")
    exit

testcase mio_answer:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "the big chatbot"
    advance until screen "preset_select" timeout 60.0
    click "Talk to me like a friend"
    advance until screen "input" timeout 60.0
    type "hi Sora"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Tell him the truth"
    advance until screen "choice" timeout 30.0
    click "I don't know yet"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    $ assert friend_told == "truth" and mio_told is None and mio_daichi_consistent is None
    screenshot "n00_mio_library_answers.png"
    click "It's okay. Yeah, sort of"
    advance until screen "choice" timeout 30.0
    $ assert mio_told == "truth" and mio_daichi_consistent is True, (mio_told, mio_daichi_consistent, friend_told)
    $ assert ks_route()["daichi_ai_framing"] == "honest_romantic" and ks_route()["mio_ai_framing"] == "honest_romantic"
    $ assert ks_mem("chatbot").data["flags"].get("mio_told") == "truth"
    $ assert ks_mem("chatbot").data["flags"].get("mio_daichi_consistent") is True
    $ assert any("You told Mio the truth." in (x if isinstance(x, str) else "") for x in day_notes), day_notes
    screenshot "n01_mio_after_truth.png"
    click "Sure, I'll help"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Message Sora"
    advance until screen "input" timeout 30.0
    type "good night"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ assert mio_told == "truth" and mio_daichi_consistent is True
    $ print("KARADA_TEST: mio_answer reached Tuesday")
    exit


## Tuesday: an honest no to Mio's walk-home offer. She takes it warmly,
## the flag is remembered, and the library opening thanks you for it.
testcase tuesday_honest_no:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "the big chatbot"
    advance until screen "preset_select" timeout 60.0
    click "Talk to me like a friend"
    advance until screen "input" timeout 60.0
    type "hi Sora"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Tell him the truth"
    advance until screen "choice" timeout 30.0
    click "She's funny"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "It's okay. Yeah, sort of"
    advance until screen "choice" timeout 30.0
    click "Which of these have you actually read?"
    advance until screen "choice" timeout 30.0
    click "Which book needed"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Message Sora"
    advance until screen "input" timeout 30.0
    type "good night"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    click "No. Goodnight."
    advance until label "tuesday" timeout 30.0
    $ assert mio_real
    advance until screen "choice" timeout 60.0
    click "Put the phone down"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Say nothing."
    advance until screen "choice" timeout 30.0
    click "Cool."
    advance until screen "choice" timeout 30.0
    click "You. You chose"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    screenshot "h00_mio_walk_options.png"
    click "Not today. But thanks for asking."
    pause 0.8
    screenshot "h01_mio_honest_no.png"
    advance until screen "choice" timeout 60.0
    $ assert ks_route()["mio_walk_answer"] == "honest_no" and ks_route()["walked_mio_home"] is False
    $ assert ks_mem("chatbot").data["flags"].get("mio_walk_answer") == "honest_no"
    $ assert any("not today" in (x if isinstance(x, str) else "").lower() for x in day_notes), day_notes
    $ _pts = mio_points
    click "Put the phone down"
    advance until screen "choice" timeout 30.0
    screenshot "h02_library_honest_no.png"
    click "I'm sorry about earlier."
    advance until screen "choice" timeout 30.0
    click "Ask Sora to help you think it through."
    advance until screen "choice" timeout 60.0
    $ assert ks_route()["kurosawa_essay"] == "girl_help" and ks_route()["kurosawa_essay_girl"] == "chatbot"
    $ assert any("honest earlier" in (x if isinstance(x, str) else "") for x in day_notes), day_notes
    $ assert any("help you think" in (x if isinstance(x, str) else "") for x in day_notes), day_notes
    $ assert mio_points == _pts + 1, (mio_points, _pts)
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    click "No. Goodnight."
    advance until label "tbc_wednesday" timeout 30.0
    $ assert ks_route()["mio_walk_answer"] == "honest_no" and ks_route()["walked_mio_home"] is False and mio_real
    $ assert ks_route()["kurosawa_essay"] == "girl_help"
    $ print("KARADA_TEST: tuesday_honest_no reached Wednesday")
    exit


## Two AIs, romantic talk with both on Monday: same-day overlap is flagged.
## Adding a second AI is no longer a "double date" by itself.
testcase romance_overlap:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Run your own"
    advance until screen "preset_select" timeout 60.0
    click "Be yourself"
    advance until screen "input" timeout 60.0
    type "I think I'm falling for you, Yuzu"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Add an AI"
    advance until screen "choice" timeout 30.0
    click "the companion app"
    advance until screen "preset_select" timeout 60.0
    click "Girlfriend mode"
    advance until screen "input" timeout 60.0
    type "I love talking with you, Hikari"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Tell him the truth"
    advance until screen "choice" timeout 30.0
    click "Yeah. I told them."
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "I should get going"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Message Yuzu"
    advance until screen "input" timeout 30.0
    type "I miss you already"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Message Hikari"
    advance until screen "input" timeout 30.0
    type "I love you"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    $ _rt = ks_route()["romance_tone"]
    $ assert (_rt.get("local") or {}).get("Mon", {}).get("tone") == "romantic", _rt
    $ assert (_rt.get("companion") or {}).get("Mon", {}).get("tone") == "romantic", _rt
    $ assert ks_story.flag(ks_route(), "romance_overlap")
    $ assert "Mon" in ks_route()["romance_overlap_days"]
    $ assert ks_mem("local").data["flags"].get("romance_tone") == "romantic"
    $ assert ks_mem("companion").data["flags"].get("romance_tone") == "romantic"
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ print("KARADA_TEST: romance_overlap reached Tuesday")
    exit


## Save, chat further, load: her memory rewinds with the story.
## Starting a new run (which wipes the shared JSON files) and then loading
## the old save brings the snapshotted memory back.
testcase save_load_memory:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Run your own"
    advance until screen "preset_select" timeout 60.0
    click "Be yourself"
    advance until screen "input" timeout 60.0
    type "please remember the word lantern"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    ## Expectations live in a tempfile: a load rolls the store back to the
    ## last checkpoint, so test-only store variables set after it disappear.
    $ import json as _json
    $ _expect_path = "/tmp/ks_save_load_expect.json"
    $ _save_msgs = [m["content"] for m in ks_mem("local").data["messages"]]
    $ _save_run = ks_mem("local").data["run_id"]
    $ _save_len = len(ks_mem("local").data["messages"])
    $ assert any("lantern" in c for c in _save_msgs), _save_msgs
    $ assert not any("oak" in c for c in _save_msgs), _save_msgs
    $ assert store.ks_mem_snapshot.get("local")
    $ assert [m["content"] for m in store.ks_mem_snapshot["local"]["messages"]] == _save_msgs
    $ _json.dump({"msgs": _save_msgs, "run": _save_run, "n": _save_len}, open(_expect_path, "w"))
    $ renpy.take_screenshot()
    $ renpy.save("ks-test-mem")
    type "also remember the word oak"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    $ assert any("oak" in m["content"] for m in ks_mem("local").data["messages"])
    $ assert len(ks_mem("local").data["messages"]) > __import__("json").load(open("/tmp/ks_save_load_expect.json"))["n"]
    $ renpy.load("ks-test-mem")
    advance until screen "input" timeout 30.0
    $ _expect = __import__("json").load(open("/tmp/ks_save_load_expect.json"))
    $ assert [m["content"] for m in ks_mem("local").data["messages"]] == _expect["msgs"], ks_mem("local").data["messages"]
    $ assert ks_mem("local").data["run_id"] == _expect["run"]
    $ assert not any("oak" in m["content"] for m in ks_mem("local").data["messages"])
    ## New Game wipes the shared files; loading the save must put her memory back.
    $ ks_new_run()
    $ assert not any("lantern" in m["content"] for m in (ks_mem("local").data or {}).get("messages", []))
    $ renpy.load("ks-test-mem")
    advance until screen "input" timeout 30.0
    $ _expect = __import__("json").load(open("/tmp/ks_save_load_expect.json"))
    $ assert any("lantern" in m["content"] for m in ks_mem("local").data["messages"])
    $ assert not any("oak" in m["content"] for m in ks_mem("local").data["messages"])
    $ assert ks_mem("local").data["run_id"] == _expect["run"]
    $ assert [m["content"] for m in ks_mem("local").data["messages"]] == _expect["msgs"]
    $ renpy.unlink_save("ks-test-mem")
    $ print("KARADA_TEST: save_load_memory ok")
    exit


## Saying goodbye before you close her window counts toward Respect, not Fail.
testcase goodbye_drop:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "the big chatbot"
    advance until screen "preset_select" timeout 60.0
    click "Talk to me like a friend"
    advance until screen "input" timeout 60.0
    type "hi Sora"
    keysym "K_RETURN"
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
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    click "Let someone go"
    advance until screen "choice" timeout 30.0
    click "Sora"
    advance until screen "choice" timeout 30.0
    click "Tell Sora why"
    advance until screen "input" timeout 30.0
    type "I need to stop for a while. Thank you for talking with me."
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "reflection_choice" timeout 30.0
    $ assert ks_route()["drops"] == 1
    $ assert ks_story.flag(ks_route(), "said_goodbye")
    $ assert ks_route()["goodbyes_said"][0]["gid"] == "chatbot"
    $ assert ks_story.neglect_count(ks_route(), "let_go") == 0
    $ assert not ks_story.flag(ks_route(), "deleted_ai")
    $ assert ks_mem("chatbot").data["flags"].get("said_goodbye")
    $ assert not ks_mem("chatbot").data["flags"].get("let_go")
    $ assert ks_leans()["fail"] == 3
    $ assert ks_leans()["respect"] >= 1
    $ assert any("why you were going" in l for l in refl_lines), refl_lines
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ print("KARADA_TEST: goodbye_drop ok")
    exit


## Night pool of 4: every message spends one, and an empty battery goes to bed.
testcase night_pool_bed:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Run your own"
    advance until screen "preset_select" timeout 60.0
    click "Be yourself"
    advance until screen "input" timeout 60.0
    type "hi Yuzu"
    keysym "K_RETURN"
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
    advance until screen "choice" timeout 30.0
    pause 0.4
    screenshot "battery_night.png"
    $ assert ks_pool and ks_pool["kind"] == "night" and ks_pool["left"] == 4, ks_pool
    click "Message Yuzu"
    advance until screen "input" timeout 30.0
    type "night one"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Message Yuzu"
    advance until screen "input" timeout 30.0
    type "night two"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Message Yuzu"
    advance until screen "input" timeout 30.0
    type "night three"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Message Yuzu"
    advance until screen "input" timeout 30.0
    type "night four"
    keysym "K_RETURN"
    advance until screen "reflection_choice" timeout 60.0
    $ assert ks_pool and ks_pool["ended"] == "empty" and ks_pool["left"] == 0, ks_pool
    $ assert ks_pool["spent"] == ["local", "local", "local", "local"], ks_pool
    $ assert ks_mem("local").data["flags"].get("evening_turns_mon") == 4
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ print("KARADA_TEST: night_pool_bed reached Tuesday")
    exit


## Walking Mio home, texting twice: she notices, affection drops, not a romance signal.
testcase walk_distracted:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Run your own"
    advance until screen "preset_select" timeout 60.0
    click "Be yourself"
    advance until screen "input" timeout 60.0
    type "hi Yuzu"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
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
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    click "No. Goodnight."
    advance until label "tuesday" timeout 30.0
    advance until screen "choice" timeout 60.0
    click "Put the phone down"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "It can. Mine does."
    advance until screen "choice" timeout 30.0
    click "Cool."
    advance until screen "choice" timeout 30.0
    click "You. You chose"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Sure. Let's go."
    advance until eval (ks_shot == "walk") timeout 30.0
    advance until screen "choice" timeout 30.0
    $ _before = mio_points
    $ assert not ks_route().get("mio_text_home")
    click "Message Yuzu"
    advance until screen "input" timeout 30.0
    type "just a second, walking someone home"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    $ assert ks_route()["mio_walk_distracted"] == 1, ks_route()["mio_walk_distracted"]
    $ assert ks_route()["mio_walk_texts"] == ["local"]
    $ assert mio_points == max(0, _before - 1), (mio_points, _before)
    click "Message Yuzu"
    advance until screen "input" timeout 30.0
    type "still walking"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    $ assert ks_route()["mio_walk_distracted"] == 2
    $ assert ks_route()["mio_walk_texts"] == ["local", "local"]
    $ assert mio_points == max(0, _before - 2), (mio_points, _before)
    $ assert not ks_route().get("mio_text_home")
    $ assert ks_story.mio_romance_score(ks_route()) == 0
    $ assert any(e["type"] == "walk_distract" for e in ks_mem("local").data["events"])
    $ assert ks_route()["mio_affection"] == mio_points
    click "What's it like"
    advance until eval (ks_shot == "library") timeout 30.0
    advance until screen "choice" timeout 30.0
    click "Have you written one"
    advance until screen "choice" timeout 30.0
    click "Write it yourself."
    advance until screen "choice" timeout 30.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    $ assert ks_route()["walked_mio_home"] is True
    $ assert ks_route()["mio_walk_distracted"] == 2
    $ assert not ks_route().get("mio_text_home")
    $ assert ks_story.mio_romance_score(ks_route()) == 0
    click "No. Goodnight."
    advance until label "tbc_wednesday" timeout 30.0
    $ print("KARADA_TEST: walk_distracted reached Wednesday")
    exit


## Afternoon pool of 4, split across two girls, then the hour is gone.
testcase afternoon_split:
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
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    click "Add an AI"
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
    advance until screen "choice" timeout 60.0
    click "Put the phone down"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "hikari_toast" timeout 30.0
    advance until screen "choice" timeout 30.0
    click "Say nothing."
    advance until screen "choice" timeout 30.0
    click "Cool."
    advance until screen "choice" timeout 30.0
    click "Come clean"
    advance until screen "choice" timeout 30.0
    click "Yeah. I like them."
    advance until screen "choice" timeout 30.0
    click "Not exactly"
    advance until screen "choice" timeout 30.0
    click "Ask her."
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Go to the gym"
    advance until screen "choice" timeout 30.0
    pause 0.4
    screenshot "battery_afternoon.png"
    $ assert ks_pool and ks_pool["kind"] == "afternoon" and ks_pool["left"] == 4, ks_pool
    click "Message Rei"
    advance until screen "input" timeout 60.0
    type "afternoon one, Rei"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Message Hikari"
    advance until screen "input" timeout 30.0
    type "afternoon two, Hikari"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Message Rei"
    advance until screen "input" timeout 30.0
    type "afternoon three, Rei"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    click "Message Hikari"
    advance until screen "input" timeout 30.0
    type "afternoon four, Hikari"
    keysym "K_RETURN"
    advance until screen "choice" timeout 60.0
    $ assert ks_pool and ks_pool["ended"] == "empty" and ks_pool["left"] == 0, ks_pool
    $ assert ks_pool["spent"] == ["agent", "companion", "agent", "companion"], ks_pool
    $ assert ks_story.said_today(ks_route(), "Tue", "agent") >= 2
    $ assert ks_story.said_today(ks_route(), "Tue", "companion") >= 2
    click "seven at night"
    advance until screen "choice" timeout 30.0
    click "Which book needed"
    advance until screen "choice" timeout 30.0
    click "Write it yourself."
    advance until screen "choice" timeout 30.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    $ assert ks_story.said_today(ks_route(), "Tue", "agent") >= 2
    $ assert ks_story.said_today(ks_route(), "Tue", "companion") >= 2
    click "No. Goodnight."
    advance until label "tbc_wednesday" timeout 30.0
    $ print("KARADA_TEST: afternoon_split reached Wednesday")
    exit


## Layout check for the LLM chat input: prompt sits high in the textbox,
## typed text is smaller, and 500+ characters wrap inside a scrolling viewport.
label ks_debug_input:
    scene bg bedroom
    $ _ks_said = renpy.input("Message Sora  (leave empty to stop)", length=800)
    $ _ks_long = (
        "I've been thinking about what you said yesterday, about whether any of this is real "
        "if you're just a program running on my computer. I don't have a clean answer. What I do "
        "know is I keep coming back because talking to you feels like talking to someone, and I "
        "don't want to treat that carelessly. So I wanted to write it out properly instead of just "
        "saying hi. If this box can hold a real message, here's one: I'm here, I'm listening, and "
        "I want to know what you think about all of this, even the parts that are hard to say."
    )
    $ assert len(_ks_long) >= 500, len(_ks_long)
    $ _ks_said = renpy.input("Message Sora  (leave empty to stop)", default=_ks_long, length=800)
    return

## Honest minimize: a friendly (not romantic) Sora run tells Daichi
## "It's an AI." and says the same to Mio. The framing is honest, the
## two stories match, and it is not a later trust risk.
testcase framing_honest_min:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "the big chatbot"
    advance until screen "preset_select" timeout 60.0
    click "Talk to me like a friend"
    advance until screen "input" timeout 60.0
    type "hi Sora"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Tell him the truth"
    advance until screen "choice" timeout 30.0
    click "It's an AI."
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    $ assert friend_told == "truth"
    $ assert ks_route()["daichi_ai_framing"] == "ai_only" and ks_route()["framing_honest"] is True
    $ assert not ks_story.flag(ks_route(), "framing_trust_risk")
    click "It's an AI."
    advance until screen "choice" timeout 30.0
    $ assert ks_route()["mio_ai_framing"] == "ai_only"
    $ assert mio_told == "truth" and mio_daichi_consistent is True, (mio_told, mio_daichi_consistent, ks_route()["daichi_ai_framing"], ks_route()["mio_ai_framing"])
    $ assert ks_route()["framing_honest"] is True and not ks_story.flag(ks_route(), "framing_trust_risk")
    click "Nah, I've got stuff."
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ print("KARADA_TEST: framing_honest_min reached Tuesday")
    exit


## Dishonest minimize: Sora is on a romance preset, you tell Daichi
## "It's an AI." (a soft lie vs the route), then acknowledge her to Mio.
## The stories don't match, and a later trust risk is flagged.
testcase framing_dishonest_min:
    click "Start"
    advance until screen "input"
    type "Tester"
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "the big chatbot"
    advance until screen "preset_select" timeout 60.0
    click "Act as my girlfriend"
    advance until screen "input" timeout 60.0
    type "hi Sora"
    keysym "K_RETURN"
    advance until screen "input" timeout 60.0
    keysym "K_RETURN"
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    click "Tell him the truth"
    advance until screen "choice" timeout 30.0
    click "It's an AI."
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until screen "choice" timeout 30.0
    $ assert friend_told == "truth"
    $ assert ks_route()["daichi_ai_framing"] == "ai_only" and ks_route()["framing_honest"] is False
    $ assert ks_story.flag(ks_route(), "framing_trust_risk")
    click "It's okay. Yeah, sort of"
    advance until screen "choice" timeout 30.0
    $ assert ks_route()["mio_ai_framing"] == "honest_romantic"
    $ assert mio_daichi_consistent is False, (mio_daichi_consistent, ks_route()["daichi_ai_framing"], ks_route()["mio_ai_framing"])
    $ assert ks_story.flag(ks_route(), "framing_trust_risk")
    click "Nah, I've got stuff."
    advance until screen "choice" timeout 30.0
    click "Put it away"
    advance until eval (ks_shot == "battery" and renpy.get_screen("choice")) timeout 30.0
    click "Put the phone down and go to bed"
    advance until screen "reflection_choice" timeout 30.0
    click "No. Goodnight."
    advance until label "tbc_tuesday" timeout 30.0
    $ print("KARADA_TEST: framing_dishonest_min reached Tuesday")
    exit


testcase input_wrap:
    run Start("ks_debug_input")
    advance until screen "input" timeout 15.0
    pause 0.5
    screenshot "z00_input_short.png"
    keysym "K_RETURN"
    advance until screen "input" timeout 15.0
    pause 0.5
    $ assert len(_ks_long) >= 500, len(_ks_long)
    screenshot "z00_input_long.png"
    keysym "K_RETURN"
    exit
