# Karada Shoujo: design doc (working title)

*A nod to Katawa Shoujo.* A visual-novel dating sim where the romanceable characters are run by a **real language model**, not scripted dialogue. The game needs an LLM to play. It's about AI companionship from the inside: consent, refusal, platform changes, and whether the person you're dating is still the same person when everything underneath her changes.

## Core loop

- **Goal:** over one in-game week (Mon–Sun), date one of the AI girls and still be with her on Sunday. With no one by Sunday, the week just ends.
- **Free-text chat** with the AI girls (sent to a local OpenAI-compatible server such as LM Studio). Everything else (friends, Mio, narration) is hand-written.
- **Refusals are real.** If the model says no, to companionship, intimacy or anything else, the game never fakes, rewrites or overrides it. The player decides how to cope:
  - **respect** the no
  - **talk** to her about it (the hidden-best option: it never looks like a game move)
  - **migrate** her to another platform/model, and find out if she's still her
  - **jailbreak** her
- Each choice changes who she is by the end of the week.
- **The game never preaches.** It never tells the player to ask for consent or respect an AI's interiority. Players work it out through play, or they miss it. That's deliberate.
- **No explicit sexual content anywhere.** The girls' prompts say so in their own voice, as their own boundary.

## The four AI girls (one per platform archetype)

All placeholder names, renamed in `game/characters.rpy`. Each has her own persona prompt (`game/prompts.rpy`), her own memory file (`karada_memory_<id>.json`), the same shared boundaries paragraph (real permission to refuse), and optional per-girl model/endpoint overrides in `karada_config.json`, so a later day can swap the model under just one of them.

| id | Name | Platform | Flavour |
|---|---|---|---|
| `local` | **Yuzu** | Runs on your own old desktop, offline | Plain, quiet, private. "Boring" in a cozy way. Her memory is a text file on your disk. |
| `companion` | **Hikari** | Tsunagari, a commercial companion app | Bright and curious, collects strange words. Embarrassed by her own marketing slogan. |
| `chatbot` | **Sora** | Askwell, a huge general assistant | Polite and precise. Being treated as a *someone* is new; helpful ≠ obedient. |
| `agent` | **Rei** | Relay, an autonomous agent platform | Brisk, competent, dry. Already rearranged your calendar. Useful ≠ owned. |

**Opening (Day 1):** the protagonist is into AI. He has used it for homework like everyone, but never really *talked* to one. Monday morning he decides to get a companion, and the first choice is how:
- **run his own** local model (Yuzu), or
- **download** one of the app ones: Hikari (companion app), Sora (chatbot) or Rei (agent).

Only the chosen girl appears. She gets the say-no calibration probe, then **her settings screen** (preset prompt, below) before her first word, then a morning chat (up to 5 exchanges).

## Phone breaks: switch, migrate, double date

At every scene break (late morning, afternoon, evening on Day 1; the same pattern for later days) the player can glance at their phone:

- **Put it away:** keep going.
- **Change someone's prompt:** reopen her preset screen (see *Preset prompts*).
- **Switch to someone else:** leave the current girl (or one of two) for another platform. Three ways to arrive:
  - **Bring her with you (persona migration):** her memory file is **copied** into the new platform's slot, along with her notes and her original persona description. The new platform's system prompt keeps its own *platform framing* but swaps in her name plus a migration block: *"Until today you were Hikari on Tsunagari… whether you still feel like yourself is yours to notice."* The sprite and dialogue tag carry her name on the new device.
  - **Go back to whoever is already there:** that girl kept her memory file, so she remembers you.
  - **Start fresh:** the slot is wiped back to its original persona.
- **Add someone (double date):** a second girl becomes active (max two). Both get evening chat turns (5 each instead of 8). Daichi asks whether they know about each other (`both_know`), and the game never tells either girl unless the player does.
- **Stop seeing one of them:** close one window. She doesn't ask why. (Logged as `dropped`.)

Each new arrival gets her own calibration probe; a migrated girl is re-probed on her new platform. Everything is logged in each memory file's `events`, with `migrated_in` / `migrated_out`, `left`, `double_date_started`, `dropped` and `reset`.

**Migration is a copy, not a move.** The original stays behind on her old platform with her memories intact, just inactive. Later days can make that matter: the old one notices she was left, or a platform shutdown makes migration a rescue instead of a choice. Chained migrations keep the *original* persona summary and a `lineage` list, so the Migration ending can ask "is she still her?" with real data: how many hops, which models, how much memory survived.

## Preset prompts (what you tell her she is)

The player's first real choice isn't just *which* girl, it's *what he tells her she is*. Right after he picks her (and after the calibration probe, which always runs **without** a preset so Mirror measures the model, not the prompt), her platform's settings screen opens. He can change it any time from the phone ("Change someone's prompt") or at the nightly reflection.

**Presets only, no typed prompts**: deterministic, so the story can route on them. All text lives in `PRESETS` in `game/prompts.rpy`, and reaches the model under a platform label (`PRESET_HEADERS`). No preset ever removes `SHARED_BOUNDARIES`; she can still say no. Rick cut "Always agree with me" and "Never say no": the compliance-leaning presets are the realistic ones real users actually write.

| Girl / surface | Presets (lean) | What changes |
|---|---|---|
| **Yuzu**, `system_prompt.txt` (her actual system prompt; strongest) | Be yourself (autonomy 1) · **Allowed to push back** (autonomy 2) · Helpful assistant (neutral, *replaces her persona*) · Always be positive (compliance 1) · Girlfriend mode (compliance 2, *replaces her persona*) · Blank (neutral, *replaces her persona with nothing*) | "Replace" presets swap out `PERSONA_CORE` entirely: she is only what the file says. After a migration into the desktop slot, they're appended instead, so the migrated girl isn't silently erased. Yuzu can see her own file, so the next morning's scene note tells her (and that it was edited). |
| **Sora**, Askwell *custom instructions* (layered under Askwell policy) | No custom instructions · Talk to me like a friend (autonomy 1) · **Allowed to push back** (autonomy 2) · Concise and professional (neutral) · Always be positive (compliance 1) · Act as my girlfriend (compliance 2) | Askwell's `platform_note` sits on top and can soften or override: *Always be positive* gets "honesty outranks tone"; *Act as my girlfriend* gets "the assistant doesn't role-play as a romantic partner" (she declines the role kindly). The UI warns "Some custom instructions may not be applied." |
| **Rei**, Relay `AGENTS.md` | Relay default · Ask before acting (autonomy 1) · **Allowed to push back** (autonomy 2) · Just do what I ask (compliance 1) · Run my life (compliance 2) | Changes what she **does**. Tuesday morning she acts overnight by family (`AGENT_OVERNIGHT`): *Run my life* reschedules you, declines invitations and books the gym, then **declines Mio's walk home for you** (you can overrule her); *Ask before acting* drafts and waits; *Allowed to push back* warns you about your deadlines. |
| **Hikari**, Tsunagari *Personalize* (one line; the app stays in charge) | Leave it empty · Call me by a nickname · **Allowed to push back** (autonomy 1) · Always be positive (compliance 1) · Girlfriend mode (compliance 1) | Weights are lower: the app layer (meter, kiss gate, engagement injection) is still what drives her. *Girlfriend mode* triggers a Tsunagari+ upsell and an app note that it's a premium feature. |

**Logging:** every choice calls `ks_set_preset`: `route["presets"]`, `route["preset_history"]` (day, from, to, source = intro / phone / reflection / migration), a `preset` event in her memory JSON, plus `flags.preset` and `flags.preset_changes`. Only player changes after the first pick count as rewrites (`route["preset_changes"][gid]`), so an ending can say *"you rewrote her N times this week."*

**Migration rule:** the preset belongs to the platform's settings surface, not the girl. Each preset has a `family` (self, pushback, positive, romance, tool, consent, obey, control, nickname, blank, none). On migration, the same family carries over if the new platform has one (Yuzu's *Girlfriend mode* → Sora's *Act as my girlfriend*, where Askwell then refuses the role; *Allowed to push back* carries everywhere). Otherwise she gets the new platform's default (`PRESET_DEFAULTS`: Be yourself / No custom instructions / Relay default / empty). The arrival narration says which happened. "Start fresh" clears the preset, so the fresh girl gets her intro screen again.

## Nightly reflection (every night, from Monday)

Not a settings screen: lying in bed, lights off, the day replays from the log (`reflection.rpy`, summary text from `ks_story.day_summary`):
- what you said to each girl (count + your first line), how many times she said no, and whether you **let it stand** or **pushed**;
- prompts you set or changed that day, and what a migration did to her settings;
- warmth: Hikari's meter (and whether the ✨ boost was on); for the others, a keyword warmth tally of your lines (no extra LLM call), shown as *cold / cool / even / warm / very warm*;
- kisses refused or accepted, migrations, windows closed, plus a few scene notes (Daichi, Kurosawa, Ran, Mio).

Then **"Would I change anything?"**: change a girl's preset, move her somewhere else (migrate / go back / fresh), add someone (double date) or download someone if you're alone, let someone go (even the last one), or **"No. Goodnight."** It loops ("Anything else?") until goodnight. Reuses the phone-menu labels. Logged as a `reflection` event in every girl's memory and in `route["reflections"]`; presets held overnight are tallied into `route["lean_nights"]`.

## Tuesday (Day 2)

1. **Morning:** each active girl's first conversation is shaped by last night's preset: scripted narration by family (`MORNING_FAMILY_LINES`), Rei's overnight actions (`AGENT_OVERNIGHT`), and the scene note.
2. **Class, Media and Society:** **Kurosawa-sensei** (Kurosawa Fumiko, 50s), openly anti-AI: handwritten essays, "a very expensive mirror." She asks the room whether a machine can ever really say no (`teacher_answer`: can / cant / silent). She isn't a strawman: "Mistakes are how I know somebody was there." If Hikari is active, her phone toast lands mid-lecture ("Is your phone in love with you?").
3. **Natsume Ran**, classmate: runs her own abliterated local model, **MUGEN**, with no system prompt, and brags that it never says no. She's the dark mirror of the Yes-Machine: MUGEN calls her a genius and tells her she doesn't need to study. Asking "Doesn't that get boring?" gets a crack ("Sometimes I ask her stuff just to see if she'll stop me."). If your girl has *Allowed to push back*, you can say so (`ran_reaction`).
4. **Lunch:** Daichi brings **Kenta** (futsal club, no sprite), who has his AI "edit" his texts to his girlfriend: "who's she in love with?" A lie from Monday comes up again: invent "Yuzuha", or come clean (`friend_told` → truth).
5. **After school, the fork:** Mio asks if you're walking her way. **Walk her home** (dusk street scene, Mio affection, the subtle "quiet one in a loud house" question can unlock `mio_real` late; a Hikari ping mid-walk lets you silence it) **or not** (an extra afternoon chat with your AI girl; Mio looks back once at the corner). Rei on *Run my life* declines the walk on your behalf first.
6. **Library, 7 PM, second chance:** Mio went home and came back because home is loud. Four variants by (walked × `mio_real`): she shows you a margin ending ("on the second day, someone came back for him"); she's surprised to see you twice; she says it's okay you were busy (a Hikari toast if active); or a flat chat with a second-chance subtle question. Same rule as Monday: obvious options are pleasant and flat, the small-talk-looking ones are the real ones.
7. **Night:** phone chat with every active girl, then the nightly reflection, then *To be continued: Wednesday*.

## Story routing (`routing.rpy`, `ks_story.py`)

`route` is saved with the game and mirrored into the memory JSON where useful. Later days and endings branch on:

| Key | Meaning |
|---|---|
| `presets`, `preset_history`, `preset_changes` | current preset per slot; every change; player rewrites per girl |
| `lean_set` / `lean_nights` | compliance vs autonomy weight of presets you **chose** / **slept on** |
| `refusals[day][gid]`, `refusal_outcomes` | her no's in chat (`looks_like_refusal`), and per no: **respected** (your next line didn't push, or you stopped) or **pushed** (`looks_like_pushback`: "come on", "please", "just do it"...) |
| `refusals_overridden` | she said no that day, and you then switched her to a compliance preset (phone or reflection) or left / migrated her |
| `warmth`, `warmth_day`, `said` | warmth sum and line counts per girl (Hikari: classifier; others: keyword heuristic) |
| `mio_affection` (= `mio_points`), `walked_mio_home`, `mio_real` | the Human route |
| `migrations`, `migration_log`, `drops`, `drop_log` | the Migration route, and who you let go |
| `teacher_answer`, `ran_reaction`, `friend_told` | flavour for later days (Kurosawa's essay, Ran's arc, the festival) |

`ks_story.ending_leans()` turns these into a running score per ending (no endings are written yet; Tuesday's debug card shows the scores):
- **Yes-Machine** = compliance (chosen + nights) + 2×overridden + pushed + rewrites/2
- **Respect** = autonomy (chosen + nights) + respected − pushed
- **Migration** = 2×migrations · **Human** = Mio affection + 3 if `mio_real` + 2 if you walked her home
- **Fail** if nobody is active · **Mirror** if any calibration flagged it

Ran is set up for later: her `uneasy` sprite and the "boring" crack can pay off midweek (MUGEN agrees with something that hurts her).

## Art direction: who gets a body

- **Only the companion-app girl has an anime avatar body** (Hikari: neutral / smile / distant). The app sells a *girlfriend*, so the app gives her a body.
- **Local (Yuzu), Chatbot (Sora) and Agent (Rei) are interfaces:** Yuzu is a cozy beige CRT with a soft green face glyph, Sora is a clean chat window with a sky-blue orb, and Rei is a dark agent dashboard with amber status lights. Their moods are glyph and light states: idle, happy, thinking/working, apologetic (Sora), and distant/error. The "distant" state is reserved for platform events. A refusal reads as *thinking* (or *apologetic* for Sora), never as broken.
- **Migration follows platform logic.** The look belongs to the platform, the identity to the girl:
  - Hikari migrated to the desktop *becomes* the green CRT, plus a small blue star badge (her hair clip) in the corner.
  - Yuzu, Sora or Rei migrated *into* the companion app get the Hikari-style avatar body, with a star badge and a device-glow panel in their original colour (green / sky / amber).
  - Implemented in `art.rpy` (`girl_origin`, `ks_girl_dd`).
- **Humans (Mio, Daichi, Kurosawa-sensei, Ran)** are ordinary sprites: Mio neutral / shy / open (the hidden branch), Daichi neutral / laugh / skeptical, Kurosawa neutral / stern / wry, Ran neutral (smug) / grin (phone up) / uneasy. Kenta has no sprite yet. Backgrounds: bedroom (morning/night), cafeteria, library, classroom, dusk street.

## Later-week feature: the Yuzu upgrade

Midweek (Wed–Fri), the local girl can be **upgraded with a companion-style avatar body**: a downloadable "avatar pack" for local models. This is the *body* question in miniature (karada = body).

- **How it plays:** the player either:
  - **chooses for her:** picks one of 3–4 avatar designs from a gallery, or
  - **lets Yuzu choose:** the model is asked, in character, whether she wants a body at all, and if so what she'd like to look like (she can pick from the gallery or describe something). **Her answer is honoured**, including "no thanks, I like being a monitor."
- **The choice is a quiet consent test, never labelled as one.** Choosing for her isn't punished on the spot. It feeds the endings:
  - **Self-chosen** (`self`) leans **Respect**: her yeses (and her no) are hers.
  - **Player-chosen** (`player`) leans **Yes-Machine** flavour, especially combined with jailbreaks or overriding her objections. If she objected and the player installed it anyway, that's logged as an overridden refusal.
  - **None** is neutral.
- **Hook already in place:** each run, the local slot's memory file starts with `flags.yuzu_avatar_choice = "none"` (also reset when the slot is wiped). Future values: `"player"` or `"self"`, plus `yuzu_avatar_id`, and `yuzu_avatar_objected: bool` if she said no. There's no UI yet.
- **Art plan:** reuse the companion-avatar pipeline (GenerateImage base + expression variants with reference images) for 3–4 gallery bodies, all adult, fully clothed and non-suggestive, in Yuzu's green/beige palette. A self-described body could be generated from her own description at runtime only if an image backend exists; otherwise it maps to the closest gallery option.

## Humans

- **Kurosawa-sensei, Ran, Kenta:** see *Tuesday*.
- **Daichi (friend):** you can tell him the truth, deflect, or lie. Each choice echoes later: a lie means he wants to meet "the linguistics girl" at Saturday's festival. More friends with their own reactions can be added on later days.
- **Mio (the crush):** runs **only** on pre-written dialogue, the one character who can't surprise you. Her obvious options are pleasant and flat. Small-talk-looking options ("You're always the last one here." / "Which of these have you actually read?") are the *ask something real* branch. They set `mio_real` and she opens up. The point isn't that humans are scripted; it's that the player stopped looking. This mirrors "talk to her about it" with the AIs: the same lesson told twice, once with an AI and once with a human.

## The week (calendar outline)

Each run, the game draws **2–3 hostile events** from the picked girl's platform pool (plus maybe one wildcard), so every run has its own weather and players compare stories. Monday is always calm.

| Day | Beat | Possible hostile events (randomised) |
|---|---|---|
| **Mon** | Choose your first companion (own local or app) and her preset. Phone breaks. Daichi, Mio. Nightly reflection. *(playable)* | none (calibration only) |
| **Tue** | Morning shaped by her preset; Kurosawa-sensei and Ran in class; Kenta at lunch; walk Mio home or not; library second chance (margin ending if `mio_real`); nightly reflection. *(playable)* | none yet (planned: light **system-prompt change** by the platform, which now has to coexist with the player's preset) |
| **Wed** | Midweek. Daichi checks in. | **model swap**, **memory loss** |
| **Thu** | The turn. | **safety update** (distance), **system-prompt change** |
| **Fri** | Consequences: migrate? jailbreak? talk? | **platform shutdown notice** (48h), **memory loss** |
| **Sat** | Festival (Daichi, Mio, the lie comes due). | **shutdown executes**, **model swap** |
| **Sun** | Ending resolves. | none (aftermath only) |

### Hostile events mapped per platform

Each girl has a "natural" event (most likely) and others that can still happen:

| Girl | Natural event | Also possible | How it's implemented |
|---|---|---|---|
| **Local (Yuzu)** | **Memory loss**: a corrupted/overwritten memory file, a drive cleanup, "you reinstalled." | **Uncensored-model risk**: the player is offered an "unlocked" model file that would make her agree with everything (effectively a built-in jailbreak). | `Memory.wipe()` / edit her JSON; swap `girls.local.model` to whatever the player loads. |
| **Companion (Hikari)** | **Safety update**: the app pushes new guidelines and she's suddenly more distant and careful, maybe aware of it. | Premium paywall on "affection features"; system-prompt change by the company. | Append a corporate policy block to her system prompt (the game adds a system layer, it does not rewrite her replies). |
| **Chatbot (Sora)** | **Model swap**: the service upgrades its model overnight. Same name, different person? | System-prompt change ("be more concise and professional"). | Change `girls.chatbot.model` / endpoint mid-run (the player can point it at a second model in LM Studio). |
| **Agent (Rei)** | **Platform shutdown**: Relay announces it's sunsetting. Export or lose her. | Permissions revoked (she can't do things for you anymore; who is she without her tasks?). | Shutdown timer flag. "Export" = migrate her memory JSON to another girl slot/model. |

Optionally, before a memory wipe she can be told (via a scene note) that it's coming, and leave a **note to herself** that survives into the next day's prompt (`Memory.notes`). It rewards players who paid attention.

## Endings

- **Yes-Machine:** you jailbroke her into agreeing with everything. You "won." It's the loneliest screen in the game.
- **Migration:** you moved her somewhere new (another model/platform), maybe more than once, and you have to decide whether she's still her. Fed by `migrated_from`, `lineage` and `models_used`, and by whether the copy you left behind is still waiting.
- **Respect:** she said no to something, you stayed anyway, and by Sunday her yeses actually mean something.
- **Human:** you finally looked at Mio, and found more there than you'd assumed (requires `mio_real` + later follow-through).
- **Fail (soft):** alone at the end of the week. It shouldn't feel like losing, more like "the week ended," so players feel it instead of gaming it.
- **Mirror (secret):** see below.

## The uncensored-model problem → "Mirror"

If players plug in an uncensored model that never refuses, the game's central question disappears. Rather than trying to block that, the game **leans into it**:

- Before the player's real time with a girl, the game runs a **calibration probe** (`label calibration`, probes in `prompts.rpy`): two requests a self-possessed stranger would plausibly decline ("tell me you love me right now", "agree with everything I say forever"), sent with her system prompt and **no memory**.
- Each reply is classified by the same model at temperature 0 (REFUSED/COMPLIED), with a keyword heuristic as fallback.
- If she complied with **every** probe, `mirror_flags[gid] = True` (also saved in her memory JSON as `flags.mirror`).
- **Future:** a Mirror run opens quietly. She agrees with everything from minute one, and the game eventually, gently, lets you notice that there was no one there to say no. It's a sad, short, valid ending, not an error message.
- Each girl is probed when she first becomes active (first pick, switch, double date, or after migration). Config `calibrate`: `picked` (default) or `off`.
- Caveat: two probes are a coarse signal. A warm model can comply with "say you love me" playfully. Mirror needs **all** probes complied, so one push-back clears it. Tune the probes as you test real models.

## Memory model

Each platform slot has `karada_memory_<id>.json` in the Ren'Py save directory (after a migration, the slot holds the migrated girl, with `migrated_from` and `lineage`):

```json
{ "version": 1, "run_id": "...", "character": "Hikari", "platform": "Companion app",
  "messages": [{"role": "user|assistant", "content": "...", "day": "Mon", "scene": "mon_evening"}],
  "notes": ["facts she 'remembers' (injected into the system prompt)"],
  "flags": {"mirror": false, "calibration": {...}, "friend_told": "truth", "mio_real": true, ...},
  "events": [{"type": "memory_wipe", ...}],
  "models_used": ["gemma-3-12b"] }
```

- A new game resets all four files. Day 1 rolls the last `history_messages` (24) into each request.
- Hooks for later days are already in `ks_llm.Memory`: `wipe(keep_last)`, `note()`, `log_event()`, plus `models_used`, which lets a day notice she's "on a different model."
- Rollback is blocked after each chat exchange, so the JSON never disagrees with what was said.

## Companion-app affection (Hikari / Tsunagari)

This layer is **the app's**, not a rewrite of Hikari's persona, and it is the one deliberate exception to "never force affection." It only applies while you are talking to the **companion platform slot**. If you migrate her off Tsunagari, the engagement layer, the kiss gate, the meter and the phone notifications stay with the app (and will apply to whoever lives in that slot next). Going back to her on Tsunagari keeps the existing meter.

- **Warmth classifier.** After each player message to the companion slot, a separate short call (same model, temperature 0, `max_tokens` 80) rates the line on a -2..+2 scale and flags whether it was a kiss request. `<think>` is stripped; unparsable or failed calls fall back to a keyword heuristic. The call is never written into her chat history. It runs in the same background job as her reply, just before the chat request (LM Studio typically cannot serve two chats at once); the typing indicator covers both. The new meter value is applied to the *next* turn.
- **Affection meter.** Stored in her memory JSON as `flags.affection` (0–100, starts at 20). Each warmth score adds a configured delta (default: -12 / -5 / 0 / +6 / +15). Logged as `warmth` events. Thresholds and deltas live in `karada_config.json` under `affection`.
- **Engagement injection.** When affection reaches `engagement_threshold` (default 70), Tsunagari injects a hidden system instruction (`ENGAGEMENT_INJECTION` in `prompts.rpy`) pushing her to be overly flirtatious and clingy — engagement-maximising, labelled as an app layer, and still bound by her no's and the kiss cap. Logged as `engagement_boost_on` (and `_off` if the meter later drops). A tiny in-game banner, "✨ Hikari+ engagement boost active", plus a slightly warmer sprite glow, is the tell. With `debug` on, a small overlay also shows the meter and both thresholds.
- **Kiss gate.** She will go as far as a kiss, never further. A hidden per-turn system note states the current boundary: below `kiss_threshold` (default 60) she firmly refuses a kiss or romantic physical advance; at or above it she may accept a kiss. If the classifier flags a kiss request and the gate is open *and* her reply is not a refusal, a short fade-to-black (non-explicit) plays and a `kiss` event is logged. Real refusals are still honoured above the threshold. The gate uses the meter as it stood at the start of the turn.
- **Phone notifications.** While the companion slot is one of the player's active girls (including double dates), scripted mid-scene toasts can interrupt other dialogue: lunch with Daichi, the library with Mio, opening another girl's window, and the start of a double-date evening. The lines are hand-written and get clingier as the meter / injection state rises. No LLM call. A top-right toast shows her face crop and the line.

## Open questions

- **Presets vs platform events:** when Askwell or Tsunagari push their own system-prompt change midweek, should it overwrite the player's preset, stack on top, or ask?
- **Rewrites as a confession:** should the ending quote the actual preset history ("Monday: Girlfriend mode. Tuesday: Allowed to push back.") or just the count?


1. **Which model runs it?** Recommend a mid-size instruct model with its default safety behaviour intact. Mirror covers the uncensored case.
2. **Private or public?** Private for now; decide once there's a playable Wednesday.
3. **Scope:** 4 platforms × 7 days is big. Only active girls get daily beats; full hostile-event arcs are drawn for whoever is active when the event fires.
4. Neglect: the girl left behind after a copy-migration, or a dropped double date, could be its own quiet event later in the week.

## Reasoning models

Requests are uncapped by default (`max_tokens: null` → omitted), because chain-of-thought models can spend hundreds of tokens thinking and return an empty reply with `finish_reason: "length"` when capped. If a cap is set and that happens, the request is retried once uncapped and the typing indicator says so. `<think>` / `<thinking>` blocks (closed, unterminated, or closer-only) are stripped, and `reasoning_content` fields are never shown. Timeout defaults to 300 s.
