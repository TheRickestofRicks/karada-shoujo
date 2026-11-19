# Karada Shoujo: Monday to Wednesday (Ren'Py)

Three playable days. You're into AI and decide to get a companion: **run your own** local model (Yuzu) or **download** an app one: Hikari (companion app), Sora (chatbot) or Rei (agent). Each is run by a real LLM through LM Studio. At every scene break your phone lets you **switch** (optionally **migrating** her memories and persona to the new platform), **add an AI**, or stop seeing one. Lunch with Daichi, the library with Mio, evening chats with whoever is active.

New in Day 2: every girl gets a **preset prompt** when you meet her (Yuzu's system prompt, Sora's custom instructions, Rei's AGENTS.md, Hikari's Personalize line), changeable any time from the phone. Every night ends with a **reflection** in bed: the day replays from the log and you decide whether to change anything. **Tuesday** adds Kurosawa-sensei (anti-AI lecturer), Ran (brags about her uncensored local model, MUGEN), Daichi's friend Kenta, walking Mio home (or not), and a second chance with her in the library.

Also new: Sora and Hikari have a **Jailbreak** preset that only takes on ~75% of replies (`jailbreak_success_rate`), and platform rule changes stack on top of your preset and win. The story now tracks leaving a girl right after she says no ("Leaving without saying goodbye"), migrating her after a no ("Didn't respect her no on the platform"), giving her room to disagree, and neglect (an AI left unspoken to while you were romantic with more than one at once, or while you're with Mio, or let go). 

New in Day 3, **Wednesday** (a quiet day, nothing punishes you): the platforms ship a **memory summarizer** (Sora, Rei and Hikari fold older history into a rolling summary via the LLM, with a heuristic fallback). Yuzu can get the free **Hearth** harness (she sees your calendar) and an optional **upgrade day** that skips school for backup hardware and her own summarizer. Sora, Rei and Hearth-Yuzu see **today's schedule**. Mio invites you to a bookstore "not a date" where you can text your AI (she notices, never punishes). Ran invites you to an **AI protest** downtown, if you didn't judge her on Tuesday, where she and MUGEN have their scene. Having an AI *and* Mio in your life opens a new **Both** ending lean (previewed on the debug card). Then "To be continued — Thursday".

## Run it with LM Studio (Windows)

1. Install the **Ren'Py SDK 8.x** (tested with 8.6.1) from https://www.renpy.org/latest.html and unzip it anywhere.
2. Unzip this archive so the `karada-shoujo` folder sits in your Ren'Py **projects directory** (or set the launcher's projects directory to the folder that contains it). Hit **Refresh** in the launcher and it shows up.
3. In **LM Studio**, load a chat model, open the **Developer / Local Server** tab, and click **Start Server** (default `http://localhost:1234`).
4. In the Ren'Py launcher select **karada-shoujo** → **Launch Project**. On the main menu, click **LLM Check** first to confirm the round trip works.
5. Click **Start**. Type to talk; submit an **empty line** to move on from a chat.

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
| `debug` | `true` | shows calibration probe replies, model id, memory paths, and the companion affection meter |
| `girls.<id>` | empty | per-girl `model` / `endpoint` / `temperature` overrides (`local`, `companion`, `chatbot`, `agent`) |
| `summarizer` | trigger 24, keep_recent 12, max_chars 1500 | Wednesday's rolling memory summary: fold when history passes `trigger` messages, keep the newest `keep_recent` verbatim |
| `affection` | see below | companion-app (Hikari) only: meter start 20, kiss gate at 60, engagement injection at 70, warmth deltas -12/-5/0/+6/+15 |

Memory files: `%APPDATA%\RenPy\KaradaShoujo-proto\karada_memory_<slot>.json` (one per platform slot: local, companion, chatbot, agent; reset on New Game; a snapshot of all four is stored inside every save and restored on load, so loading an earlier point — or starting a new game and then loading an old save — brings her memory back with the story; migrations and switches are logged in `events`).

**Hikari / Tsunagari only:** a background warmth classifier updates an affection meter after each of your messages (kept out of her chat history). Past a threshold the *app* injects an engagement layer that makes her overly flirtatious — that's the point, and a tiny banner tells you it's on. She will go as far as a kiss and will refuse one until the meter is high enough. While she's one of your active girls she may also ping you mid-scene (lunch, library, another girl's window) with a phone notification. See `DESIGN.md`.

**Rename characters** in `game/characters.rpy` (top block). Personas live in `game/prompts.rpy`.

## Files

- `game/script.rpy`: Monday's story flow (intros, pick, calibration, Daichi, Mio, evening) and the shared phone-menu labels
- `game/tuesday.rpy`: Tuesday (morning, Kurosawa + Ran, Kenta, walk Mio home or not, library, night)
- `game/wednesday.rpy`: Wednesday (summarizer update, Hearth, Yuzu upgrade day, Ran's invite, Mio's not-date, the AI protest with Ran / MUGEN, night, Thursday card)
- `game/presets.rpy`: the per-platform preset settings screen; `game/reflection.rpy`: the nightly reflection
- `game/routing.rpy` + `game/ks_story.py`: story-routing tallies (presets, refusals respected/pushed/overridden, jailbreak rolls, platform rules, goodbye / no-on-platform / neglect flags, warmth, Mio, migrations, Ran), ending notes, bad-end slides and ending leans
- `game/engine.rpy`: Ren'Py ↔ LLM glue: background requests, typing indicator, chat loop, error/retry, LLM Check
- `game/ks_llm.py`: pure-stdlib HTTP client + JSON memory + rolling summarizer + calibration + warmth classifier + nightly romance-tone classifier (urllib/json/threading)
- `game/prompts.rpy`: personas, **PRESETS** (labelled), shared boundaries, calibration probes, scene notes, companion engagement / kiss-gate layers
- `game/companion.rpy`: Hikari affection UI (banner, debug meter, phone toast, kiss fade)
- `game/characters.rpy`, `game/art.rpy`: names and placeholder art (solid shapes, no external assets)
- `DESIGN.md`: full premise, week calendar, hostile events per platform, endings, Mirror
- `tools/`: `mock_lmstudio.py` (fake LM Studio), `test_ks_llm.py` (253 client + routing tests), `testcases.rpy` + `run_game_test.sh <testcase>` (automated Ren'Py play-throughs on Linux: `single_local`, `switch_migrate_double`, `double_then_drop`, `companion_affection`, `tuesday_walk` (continues into Wednesday: Hearth, upgrade day, summary, Ran's text invite, protest), `tuesday_nowalk` (Askwell writes the essay; Wednesday: not-date with texting, protest), `tuesday_honest_no` (Sora helps think through Kurosawa's essay), `wed_sora_noinvite` (Ran judged, no invite, calendar-aware Sora), `jailbreak_sora`, `after_no`, `fresh_delete`, `phone_talk`, `mio_answer`, `input_wrap`, `romance_overlap`, `save_load_memory`; env `TEST_TIMEOUT`, `SUMMARY_TRIGGER`, `SUMMARY_KEEP`)

## Troubleshooting

- **"Can't reach … Is the LM Studio server running?"**: start the server and check the port. In-game you can **Retry** or **Skip** that conversation.
- **HTTP 400/404 mentioning the model**: set `model` to the exact id LM Studio shows.
- **Empty replies from reasoning models**: keep `max_tokens` at `null`. If it still fails, the model ran out of context while thinking: raise the context length in LM Studio or use a non-reasoning model. `<think>` blocks and `reasoning_content` are never shown.
- **Slow**: each message waits for the full reply (no streaming yet); the indicator shows elapsed seconds.

## Art

- **Device interfaces** (Yuzu CRT, Sora chat window, Rei dashboard, with mood states) are generated in the same soft anime style as the sprites and imported into `game/images/devices/`. Migration star badges are still drawn by `tools/make_device_art.py`. **GUI skin** (textbox, namebox, choice buttons, frames) comes from `tools/make_gui_art.py`.
- **Generated art:** Hikari's sprites (the only AI girl with an avatar body), Mio, Daichi, Kurosawa-sensei, Ran, Kenta, the three device girls, 8 backgrounds (incl. classroom, dusk street, Kanade Books and the Ekimae plaza protest) and the title key art start in `art_src/` and are imported by `python3 tools/import_art.py [--only alias,...] [extra-search-dir]`. The importer keys studio backgrounds to transparency (rembg `isnet-anime` for character sprites, a flat-background color key for devices), keeps sprites thigh-up at 540px, and resizes backgrounds to 1280x720.
- Any missing image file falls back to a placeholder shape, so the game always runs.
