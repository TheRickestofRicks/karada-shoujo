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
    advance until screen "main_menu" timeout 30.0
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
    advance until screen "main_menu" timeout 30.0
    $ print("KARADA_TEST: tuesday_nowalk reached main menu")
    exit
