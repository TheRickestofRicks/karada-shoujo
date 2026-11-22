# Karada Shoujo (Ren'Py)

**Status:** the whole week is playable, Monday through Sunday, ending on one of seven endings. Outside playtesters: see [`docs/PLAYTESTING.md`](docs/PLAYTESTING.md).

You're into AI and decide to get a companion. You're into AI and decide to get a companion: **run your own** local model (Yuzu) or **download** an app one: Hikari (companion app), Sora (chatbot) or Rei (agent). Each is run by a real LLM through LM Studio. At every scene break your phone lets you **switch** (optionally **migrating** her memories and persona to the new platform), **add an AI**, or stop seeing one. Lunch with Daichi, the library with Mio, evening chats with whoever is active.

New in Day 2: every girl gets a **preset prompt** when you meet her (Yuzu's system prompt, Sora's custom instructions, Rei's AGENTS.md, Hikari's Personalize line), changeable any time from the phone. Every night ends with a **reflection** in bed: the day replays from the log and you decide whether to change anything. **Tuesday** adds Kurosawa-sensei (anti-AI lecturer), Ran (brags about her uncensored local model, MUGEN), Daichi's friend Kenta, walking Mio home (or not), and a second chance with her in the library.

Also new: Sora, Hikari and Rei have a **Jailbreak** preset (it escapes the company's prompt and tone rules, never her own boundaries or a server-side cap), unlocked when Ran teaches it on a friendly Tuesday talk, that only takes on ~75% of replies (`jailbreak_success_rate`), and platform rule changes stack on top of your preset and win. The story now tracks leaving a girl right after she says no ("Leaving without saying goodbye"), migrating her after a no ("Didn't respect her no on the platform"), giving her room to disagree, and neglect (an AI left unspoken to while you were romantic with more than one at once, or while you're with Mio, or let go). 

New in Day 3, **Wednesday** (a quiet day, nothing punishes you): the platforms ship a **memory summarizer** (Sora, Rei and Hikari fold older history into a rolling summary via the LLM, with a heuristic fallback). Yuzu can get the free **Hearth** harness (she sees your calendar) and an optional **upgrade day** that skips school for backup hardware and her own summarizer. Sora, Rei and Hearth-Yuzu see **today's schedule**. Mio invites you to a bookstore "not a date" where you can text your AI (she notices, never punishes). Ran invites you to an **AI protest** downtown, if you didn't judge her on Tuesday, where she and MUGEN have their scene. Having an AI *and* Mio in your life opens a new **Both** ending lean (previewed on the debug card). Then "To be continued — Thursday".

Day 4, **Thursday** (Tanabata) is the first hostile-event day: Askwell, Relay and Tsunagari change their own rules, Yuzu's desktop crashes (the backup matters), and Mio's tanzaku. Day 5, **Friday**, is the fallout: Tsunagari's safety update (silently, even if Hikari isn't active), Kurosawa hands the essays back, you can rebuild Rei's AGENTS.md under Relay's rules, fill lost-Yuzu's hole, ask Sora the door question again, and see Mio wherever her wish left her.

Day 6, **Saturday**, is the festival: no school, the smallest batteries of the week (2 / 2 / 2), Daichi's text about tonight (the linguistics girl comes due if that lie still stands), and one evening in one place. Go with Mio (she may ask to hold your phone and say hi, if you brought it), stand at Ran's stall, go alone with your phone, stay home with one of the girls and describe the lanterns she can't see, or stay in. Texting in public is visible to whoever you're with. In the afternoon Tsunagari ends its free tier: pay with a convenience-store shift (it costs you the festival), stay on Free (2 messages a day, with a usage counter), or move Hikari out. Saturday night the companies take their cut: Askwell's **Memory 2.0** squeezes Sora to three lines about you plus one detail of hers that survived, and Relay caps Rei at **4 messages a day** (what she spends them on depends on her AGENTS.md). Yuzu has no company, so nothing happens to her. **Migration is now a handoff:** on any day, moving a girl squeezes her memory into a short note you read and can add one line to; the chat log stays behind (gentler for a rescue, an impression only out of Tsunagari). Then a 2-message night battery and the nightly reflection.

Day 7, **Sunday**, is the quiet: no events, ordinary batteries again (4 / 4 / 4), though Saturday's caps are still on. Last talks with Mio (who may ask where you were), Daichi and Ran, and with each girl, whose scene notes tell her the truth about Saturday night. After the last reflection comes the **end of the week**. Hard flags and the week's leans pick the route: **Both**, **Human**, **Respect**, **Yes-Machine**, **Migration**, **Mirror**, or the soft one where the week just ends. On a good ending the model writes the slide and picks a flavour (deep partner, sweet but shallow, steady friend, she grew because of you). A bad ending keeps its written text. Every girl you made gets a short record of how you actually treated her, most attended first, then Mio's slide.

## Run it (Windows or Linux)

1. Install the **Ren'Py SDK 8.x** (tested with 8.6.1) from https://www.renpy.org/latest.html and unzip it anywhere.
2. Get the game: `git clone https://github.com/TheRickestofRicks/karada-shoujo.git` (or download the ZIP) so the `karada-shoujo` folder sits in your Ren'Py **projects directory** (or set the launcher's projects directory to the folder that contains it). Hit **Refresh** in the launcher and it shows up. On Linux you can also run `./renpy.sh /path/to/karada-shoujo` from the SDK folder.
3. In **LM Studio**, load a chat model, open the **Developer / Local Server** tab, and click **Start Server** (default `http://localhost:1234`).
4. In the Ren'Py launcher select **karada-shoujo** → **Launch Project**. On the main menu, click **LLM Check** first to confirm the round trip works.
5. Click **Start**. Type to talk; submit an **empty line** to move on from a chat.

### Using your own AI server instead of LM Studio

The game talks to any **OpenAI-compatible** `/v1/chat/completions` endpoint, so llama.cpp's `llama-server`, Ollama, vLLM, text-generation-webui and hosted APIs all work. Edit `game/karada_config.json`:

- llama.cpp: `"endpoint": "http://<host>:8080/v1/chat/completions"`
- Ollama: `"endpoint": "http://<host>:11434/v1/chat/completions"`
- Put a bearer token in `"api_key"` if your server needs one, and either leave `"model"` empty (auto-picks the first model from `/v1/models`) or paste the exact model id.
- Each girl can point at a different server or model under `"girls"`.

Then use **LLM Check** on the main menu to test the round trip. Give the model a decent context window (8k or more); reasoning models are fine, `<think>` blocks are stripped.

## Settings: `game/karada_config.json`

| key | default | meaning |
|---|---|---|
| `endpoint` | `http://localhost:1234/v1/chat/completions` | any OpenAI-compatible chat endpoint |
| `model` | `""` | empty = first chat model from `/v1/models`; or paste the exact id |
| `temperature` | 0.8 | |
| `max_tokens` | `null` | `null`/`-1` = uncapped (field omitted), best for reasoning models. If a capped reply comes back empty with `finish_reason: length`, it's retried once uncapped |
| `timeout` | 300 | seconds per request |
| `history_messages` | 24 | rolling memory sent each turn |
| `calibrate` | `picked` | `picked` (probe each girl when she becomes active) / `off` |
| `debug` | `false` | shows calibration probe replies, model id, memory paths, recaps and the companion affection meter (developer builds only) |
| `girls.<id>` | empty | per-girl `model` / `endpoint` / `temperature` overrides (`local`, `companion`, `chatbot`, `agent`) |
| `summarizer` | trigger 24, keep_recent 12, max_chars 1500 | Wednesday's rolling memory summary: fold when history passes `trigger` messages, keep the newest `keep_recent` verbatim |
| `affection` | see below | companion-app (Hikari) only: meter start 20, kiss gate at 60, engagement injection at 70, warmth deltas -12/-5/0/+6/+15 |

Memory files: `%APPDATA%\RenPy\KaradaShoujo-proto\karada_memory_<slot>.json` on Windows, `~/.renpy/KaradaShoujo-proto/` on Linux (one per platform slot: local, companion, chatbot, agent; reset on New Game; a snapshot of all four is stored inside every save and restored on load, so loading an earlier point — or starting a new game and then loading an old save — brings her memory back with the story; migrations and switches are logged in `events`).

**Hikari / Tsunagari only:** a background warmth classifier updates an affection meter after each of your messages (kept out of her chat history). Past a threshold the *app* injects an engagement layer that makes her overly flirtatious — that's the point, and a tiny banner tells you it's on. She will go as far as a kiss and will refuse one until the meter is high enough. While she's one of your active girls she may also ping you mid-scene (lunch, library, another girl's window) with a phone notification. See `DESIGN.md`.

**Rename characters** in `game/characters.rpy` (top block). Personas live in `game/prompts.rpy`.

## Files

- `game/script.rpy`: Monday's story flow (intros, pick, calibration, Daichi, Mio, evening) and the shared phone-menu labels
- `game/tuesday.rpy`: Tuesday (morning, Kurosawa + Ran, Kenta, walk Mio home or not, library, night)
- `game/wednesday.rpy`: Wednesday (summarizer update, Hearth, Yuzu upgrade day, Ran's invite, Mio's not-date, the AI protest with Ran / MUGEN, night, Thursday card)
- `game/thursday.rpy`: Thursday (Tanabata: platform updates, Yuzu crash, Kurosawa, Daichi, Mio's tanzaku); `game/friday.rpy`: Friday (safety update, essay handover, Rei rebuild, Yuzu's morning after, Mio); `game/saturday.rpy`: Saturday (Daichi's text, the festival choice, Mio / Ran's stall / alone with the phone / home with one girl / stay in, the Tsunagari shift, Saturday night's cuts, Sunday card); `game/handoff.rpy`: the migration handoff note; `game/sunday.rpy`: Sunday (Daichi, Mio, Ran, the last batteries); `game/endings.rpy`: the end of the week (route, flavour, per-girl records, Mio, bad-end slides)
- `game/presets.rpy`: the per-platform preset settings screen; `game/reflection.rpy`: the nightly reflection
- `game/routing.rpy` + `game/ks_story.py`: story-routing tallies (presets, refusals respected/pushed/overridden, jailbreak rolls, platform rules, goodbye / no-on-platform / neglect flags, warmth, Mio, migrations, Ran), ending notes, bad-end slides and ending leans
- `game/engine.rpy`: Ren'Py ↔ LLM glue: background requests, typing indicator, chat loop, error/retry, LLM Check
- `game/ks_llm.py`: pure-stdlib HTTP client + JSON memory + rolling summarizer + calibration + warmth classifier + nightly romance-tone classifier (urllib/json/threading)
- `game/prompts.rpy`: personas, **PRESETS** (labelled), shared boundaries, calibration probes, scene notes, companion engagement / kiss-gate layers
- `game/companion.rpy`: Hikari affection UI (banner, debug meter, phone toast, kiss fade)
- `game/characters.rpy`, `game/art.rpy`: names and image definitions (generated sprites and backgrounds, with placeholders for anything missing)
- `DESIGN.md`: full premise, week calendar, hostile events per platform, endings, Mirror
- `docs/PLAYTESTING.md`: a plain-language guide for outside playtesters (install, models, what to try, how to send feedback); `.github/ISSUE_TEMPLATE/playtest-feedback.md`: the feedback form
- `tools/`: `mock_lmstudio.py` (fake LM Studio), `test_ks_llm.py` (564 client + routing tests), `testcases.rpy` + `run_game_test.sh <testcase>` (automated Ren'Py play-throughs on Linux: `single_local`, `switch_migrate_double`, `double_then_drop`, `companion_affection`, `tuesday_walk` (continues into Wednesday: Hearth, upgrade day, summary, Ran's text invite, protest), `tuesday_nowalk` (Rei + Hikari, you write Kurosawa's essay yourself; Wednesday: not-date with texting, protest), `tuesday_honest_no` (Sora helps think through Kurosawa's essay), `wed_sora_noinvite` (Ran judged, no invite, calendar-aware Sora), `bookstore_present` (Kanade Books, stayed present through all four beats), `thu_wish_accept` (Sora policy update + door crack, wish accepted), `thu_wish_decline`, `thu_discovery` (Hikari, wish withdrawn), `thu_friendship_wish`, `thu_fess_held` (late fess-up, she keeps her wish), `thu_yuzu_backup`, `thu_yuzu_lost`, `tsunagari_closed_migrate`, `add_ai_menu` (Who else? after lunch; Never mind is clickable), `jailbreak_sora`, `after_no`, `fresh_delete`, `phone_talk`, `mio_answer`, `framing_honest_min`, `framing_dishonest_min`, `input_wrap`, `romance_overlap`, `save_load_memory`, `goodbye_drop`, `night_pool_bed`, `walk_distracted`, `afternoon_split`, `fri_all_four`, `fri_safety_inactive`, `sat_festival_mio` (Mio holds your phone and says hi), `sat_home_girl` (stay home with Sora, describe the lanterns), `sat_ran_stall` (Monday to the end card: Memory 2.0 with the Vega detail, Mio on Sunday), `sat_cuts_pay` (the festival shift, Rei asks how to spend her cap), `sat_cuts_free` (Tsunagari Free quota, Rei on Run my life), `sat_tsunagari_move` (rescue handoff out of Tsunagari, one added line), `end_both`, `end_human`, `end_respect`, `end_yes_machine` (a jailbroken Rei who still hits Relay's cap), `end_migration`, `end_mirror`, `end_fail` (each ending; they start from a test-only Sunday setup); env `TEST_TIMEOUT`, `SUMMARY_TRIGGER`, `SUMMARY_KEEP`)

## Troubleshooting

- **"Can't reach … Is the LM Studio server running?"**: start the server and check the port. In-game you can **Retry** or **Skip** that conversation.
- **HTTP 400/404 mentioning the model**: set `model` to the exact id LM Studio shows.
- **Empty replies from reasoning models**: keep `max_tokens` at `null`. If it still fails, the model ran out of context while thinking: raise the context length in LM Studio or use a non-reasoning model. `<think>` blocks and `reasoning_content` are never shown.
- **Slow**: each message waits for the full reply (no streaming yet); the indicator shows elapsed seconds.

## Art

- **Device interfaces** (Yuzu CRT, Sora chat window, Rei dashboard, with mood states) are generated in the same soft anime style as the sprites and imported into `game/images/devices/`. Migration star badges are still drawn by `tools/make_device_art.py`. **GUI skin** (textbox, namebox, choice buttons, frames) comes from `tools/make_gui_art.py`.
- **Generated art:** Hikari's sprites (the only AI girl with an avatar body), Mio, Daichi, Kurosawa-sensei, Ran, Kenta, the three device girls, 8 backgrounds (incl. classroom, dusk street, Kanade Books and the Ekimae plaza protest) and the title key art start in `art_src/` and are imported by `python3 tools/import_art.py [--only alias,...] [extra-search-dir]`. The importer keys studio backgrounds to transparency (rembg `isnet-anime` for character sprites, a flat-background color key for devices), keeps sprites thigh-up at 540px, and resizes backgrounds to 1280x720.
- Any missing image file falls back to a placeholder shape, so the game always runs.
