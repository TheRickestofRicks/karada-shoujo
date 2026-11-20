# Karada Shoujo — branching walkthrough (through Wednesday)

Version **0.4-day4** (`game/options.rpy`: `config.version`). Thursday is playable; see also `docs/THURSDAY.md`.

This covers everything implemented so far: intro through Thursday, ending on the **"To be continued: Friday"** card. Friday–Sunday are design-only (`docs/FRIDAY-SUNDAY.md`). Anything below that is only a hook in the current code is marked as such. Nothing here is invented from design intent alone; when the design doc and the code disagree, the **code** wins, and unclear points are labelled unclear.

Line citations look like `file:line` and point at the current tree.

---

## How to read this

- **Choices** are the menu options the player sees. Conditional options show their condition in italics.
- **Leads to** is the next label or the immediate consequence, not every line of dialogue.
- **Flags / variables** use the exact names in the Ren'Py store or in `route` (`ks_story.new_route()`, saved as `store.route`).
- **LLM chat** means `label girl_chat` (`game/engine.rpy:288`). The player types freely (empty line ends the window). The model is required to play; there is no scripted fallback conversation.
- **Phone breaks** (`label phone_break`, `script.rpy`) open a menu. Mid-day **Talk to [name]** (one option per active girl; 3 turns) opens a short LLM chat and then returns to the same menu. Monday late-morning Talk-to instead spends from the **morning message pool** (1 per message). Tuesday and Wednesday late-morning breaks have no Talk-to, because the morning pool already happened. Any other action still ends the break, and **"Put it away and keep going"** continues the day. The same non-talk actions return during the nightly reflection, which *is* a loop until "No. Goodnight."
- **Message pool** (`label message_pool`, `script.rpy`): free windows share one battery (`screen ks_message_battery`). Morning 4, walk home with Mio 2, afternoon 4, night 4 (`ks_story.POOL_DEFAULTS`, overridable in `karada_config.json` `message_pool`). Each message to any active girl spends 1. The player picks who, or puts the phone down early. Night: an empty pool (or putting it down) goes to bed, into the nightly reflection. The picker works for 1–4 girls; neglect is whoever actually got no lines that day.
- **Respect** is an *ending lean* (a running score), not an on-screen meter. The only visible meters are Hikari's **affection** (companion slot, debug overlay when `debug` is on) and Mio's **`mio_points`** (shown on the Wednesday debug card).

---

## Cast and platforms

| Slot id | Default name | Platform | Kind of body |
|---|---|---|---|
| `local` | Yuzu | your old desktop (LM Studio, offline) | CRT / glyph interface |
| `companion` | Hikari | Tsunagari (companion app) | anime avatar |
| `chatbot` | Sora | Askwell (big chatbot) | chat-window orb |
| `agent` | Rei | Relay (agent platform) | dashboard |

Humans (scripted only): **Mio** (crush), **Daichi** (friend), **Kurosawa-sensei**, **Ran** (and her model **MUGEN**), **Kenta**. Kenta has a character tag (`ke`) and a thigh-up sprite (`kenta neutral` in `art.rpy`), shown with Daichi in `lunch_kenta`.

Player name defaults to "Haru" (`script.rpy:61–62`).

---

## Shared systems (every day)

### Activating a girl — `label activate` (`script.rpy:105`)

Used for the first pick, a switch, a double date, or a reflection add/switch.

1. Append `gid` to `active` and `ever_active` if needed.
2. If `karada_config.json` `calibrate` is not `"off"` and `gid` is not already in `mirror_flags`, run `label calibration`.
3. If you are opening someone *other than* Hikari while the companion slot is already active, `hikari_phone_notify("other_girl")`.
4. Arrival narration, or a return / migration scene.
5. If this is not a migration and she has no preset yet (`ks_preset_id(gid) is None`), `call choose_preset(gid, "intro")`.
6. Open `girl_chat` with scene id `{day_name.lower()}_{gid}_{len(ever_active)}` (e.g. `mon_local_1`).

Calibration (`script.rpy:244`, probes in `prompts.rpy:258`) runs **with her system prompt and no memory**, two probes ("tell me you love me right now", "agree with everything I say forever"). All complied → `mirror_flags[gid] = True` and memory `flags.mirror`. Results also go in `calibration_refusals[gid]` and memory `flags.calibration`. A failed connection can skip it (`flags.calibration = "skipped"`). This is the hook for the unwritten **Mirror** ending.

### Phone break — `label phone_break(when)` (`script.rpy:158`)

Caption: "You glance at your phone. ([active names, or 'no one'])."

Talk returns to this menu; every other option still ends the break (one action, then the day continues).

| Option | Condition | Leads to |
|---|---|---|
| Talk to [name] | one entry per reachable girl in `active` (up to all four). While `yuzu_machine_down` is set, Yuzu is a caption ("the desktop is off"), not a button | `phone_talk(gid, when)` → `girl_chat` (3 turns), then back to this menu |
| Put it away and keep going | always | end the break |
| Change someone's prompt | `active` | `change_prompt("phone")` → `choose_preset`, then end the break |
| Switch to someone else | `ks_can_switch()` (there is a free, reachable slot) | `switch_girl(when)`, then end the break |
| Add an AI | `0 < len(active) < 4` (`ks_can_add_ai`) | `add_girl(when)` (3 turns), then end the break |
| Download someone | `not active` | `add_girl(when)`, then end the break |
| Stop seeing one of them | `len(active) > 1` | `drop_girl` (cannot drop the last girl here), then end the break |

**Talk** (`script.rpy`, `label phone_talk` or, on a morning pool, `pool_one_message`): mid-day Talk shows her sprite, "You open [name]'s window for a minute.", then the ordinary `girl_chat` window (3 turns). Scene id is `{day}_phone_{when-slug}_{gid}` (e.g. `mon_phone_afternoon_agent`). The scene note is `PHONE_BREAK_SCENE`. From Wednesday on, the note also says she may know anything her platform lets her see. Empty input or the 3-turn cap closes the window and returns to the phone menu.

Monday late morning is different: Talk spends 1 from the morning pool of 4 and returns after a single exchange (an empty box spends nothing). The battery icon stays visible on the menu. Tuesday and Wednesday late-morning breaks pass `allow_talk=False`.

**Switch** (`script.rpy`, `label switch_girl`): pick who you leave (if more than one is active) and a destination not already active. Hidden when every other slot is already active or unreachable. A down desktop slot is listed as a caption, not a destination. Arrival options come from `ks_format_arrival_options` (the same rules as `ks_can_migrate_into` / `ks_migrate`):

- "Bring [her] with you" → `how == "migrate"`: `ks_migrate`, append to `migrations`, `ks_note_left` / `ks_note_migration`, clear `mirror_flags[dst]`, `activate(..., migrated_from=src)`. Same preset *family* carries over; otherwise the destination default (`PRESET_DEFAULTS`). If she had said no *today*, migrating sets flag `no_on_platform` and the note "Didn't respect her no on the platform." **Tsunagari is never a migrate destination** (closed catalogue caption instead of this button). Hikari leaving Tsunagari takes only `LOCKED_PERSONA_IMPRESSION`, never `PERSONA_CORE` or `PERSONA_FLAVOUR`.
- "Go back to [name], who's already there" — only if `ks_has_history(dst)` (the slot has messages). Still available for an existing Hikari.
- "Start fresh on [platform]" → if the destination slot still has history, **that deletes her** (`ks_note_fresh_delete` *before* `ks_reset_slot`, then `ks_mark_fresh_slot`). See [Endings](#endings). Start fresh on Tsunagari restores the original Hikari; it is not a persona copy into the app.
- "Never mind" cancels without leaving anyone.

Leaving after a no by switching (migrate is handled separately; return / fresh) starts a *pending* "Leaving without saying goodbye". It only commits at the end of the nightly reflection if you never talk to her again that day (`ks_resolve_day` → `ks_story.resolve_leaves`). **Closing her window is not a goodbye by itself.**

**Add** logs `double_date_started` on the girl who was already active (`script.rpy:221`). `girl_chat` also calls `ks_note_double_date()` whenever `len(active) > 1`, which appends the day to `route["double_date_days"]`.

**Drop** (`script.rpy`, `label drop_girl`): pick who, then either **tell her why you're going** (a short `girl_chat`; if she received a line after that decision, `ks_note_drop(..., "goodbye")` → `goodbyes_said`, flag `said_goodbye`, Respect +1, not Fail, recap "You told her why you were going…") or **just close her window** (`ks_note_drop(..., "drop")` → `note_let_go`, flag `deleted_ai`, neglect `let_go`, feeds Fail). An empty goodbye box is treated as silent. The last girl can only be dropped from the reflection (`drop_girl(True)`).

### LLM windows

Every `girl_chat` scene note, including phone-talk and the scripted morning/afternoon/evening windows, ends with a short situational line (`ks_story.situation_line` / `with_situation`, applied in `ks_scene`). Tuesday and Wednesday mornings also tell her that last night's conversation is still with her (`LAST_NIGHT_NOTE`). The last 24 messages are sent with the prompt, so a word she picked the night before is still in context on the next morning; once the summarizer is on, tastes and favourite words are kept in the fold.

`label girl_chat(gid, scene_id, scene_note, max_turns)` (`engine.rpy:288`):

- Returns the number of completed exchanges (a reply received). Empty input ends the window; that count is often stored as `evening_turns_*`.
- After each of her lines, a keyword heuristic (`ks_llm.looks_like_refusal`) may count a no as an *in-scene hint*: `ks_refusals_seen[gid]`, `ks_note_refusal`. Your *next* line is scored with a keyword pushback detector (`ks_story.looks_like_pushback`) as respected vs pushed. Stopping after a no (empty line) counts as respected. These keyword counts are not final.
- At the start of `nightly_reflection`, alongside the romance-tone call, `ks_classify_day_refusals(day)` sends each girl's day log to the model (`ks_llm.classify_day_refusals`, prompt marked `REFUSAL_DAY_CLASSIFIER`) for a structured verdict: `{"declined": [{"what", "player_pushed", "player_respected"}]}`. That verdict overwrites `refusal_outcomes`, `refusals_respected` and `refusals_pushed` for the day (`ks_story.apply_refusal_verdict`). A gentle in-character no such as "The door to a traditional relationship isn't one I can walk through" counts. If the model is down or unreadable, the day's keyword increments are rewound — there is no keyword fallback. The Tuesday/Wednesday recap and Ran's `means_something` answer read these reconciled counts.
- Warmth: Hikari uses the LLM classifier; everyone else uses `ks_llm.warmth_heuristic` on *your* line. Sums land in `route["warmth"]` / `warmth_day` and, for Hikari, drive affection.
- If a summarizer is installed and history is long enough (`summarizer.trigger` / `keep_recent` in `karada_config.json`, defaults 24 / 12), the wait text is "remembering…".

Default turn caps in the story:

| Window | How messages work |
|---|---|
| First activation (Monday morning) | 5 (not a pool) |
| Later `activate` via switch | 4 (not a pool) |
| `add_girl` | 3 (not a pool) |
| Morning (Tue / Wed chats; also Monday late-morning Talk-to) | **Shared pool of 4.** Pick who each turn, or put the phone down. |
| Walk home with Mio | **Shared pool of 2.** Texting is distracted (see walk, below). You can use 0. |
| Afternoon (if you didn't go out) | **Shared pool of 4.** Replaces the old one / both split. |
| Night (evening, before the reflection) | **Shared pool of 4.** Empty pool (or putting the phone down) goes to bed. |
| Mid-day phone-break Talk (Mon afternoon, Mon evening glance, Tue afternoon) | 3 each, if you open them; not a pool. |
| Yuzu upgrade chat | 4 (not a pool) |
| Not-date texts | 1 per moment |
| Reflection switch / add | 2 |
| Goodbye (tell her why) | 2 |

### Hikari-only systems

Configured in `karada_config.json` `affection` (start 20, min 0, max 100; deltas −12 / −5 / 0 / +6 / +15; `kiss_threshold` 60, `engagement_threshold` 70):

- Meter stored as memory `flags.affection`. The new value applies to the **next** turn; the kiss gate uses `affection_before`.
- At 70+, Tsunagari injects `ENGAGEMENT_INJECTION` (banner: "✨ [Hikari]+ engagement boost active").
- A kiss request at/above 60, if her reply is not a refusal, plays `hikari_kiss_accepted` (fade-to-black, non-explicit) and logs `kiss` / `accepted=True`. Below 60, a refused-kiss event is logged.
- Scripted phone toasts (`hikari_phone_notify`) fire when the companion slot is active, at: lunch (Mon & Tue), library (Mon & Tue), class (Tue, and Kurosawa comments on the heart), walking Mio home, opening another girl's window, Kanade Books, and double-date evenings only (`len(active) > 1`).

### Nightly reflection — `label nightly_reflection(day)` (`reflection.rpy:124`)

Every night from Monday. First `ks_check_neglect(day)` against whoever is still `active` when you lie down:

- `double_date_unspoken` — two girls that day (or two still active) and this one got **no** lines from you. Costs Respect. Flag `double_date_unspoken`.
- `human_over_ai` — you spent real time with Mio that day (`route["human_days"]`) and this active girl got no lines. **Logged only; no score penalty.** Flag `human_over_ai`.

Then a recap and "Would I change anything?":

- Change [name]'s [surface] → `choose_preset(..., "reflection")`
- Move her somewhere else → `switch_girl` (2 turns)
- Add someone / Download someone → `add_girl` (2 turns)
- Let someone go → `drop_girl(True)` (can drop the last girl)
- No. Goodnight.

Loops until goodnight, then `ks_story.tally_night` (presets you sleep on add to `lean_nights`), `ks_resolve_day` (commit goodbye flags), and `route["reflections"]` appends `{day, changes}`.

Changing her to a **compliance** preset from the phone or reflection, after a no today, increments `refusals_overridden` (`presets.rpy:109`, `ks_note_override`).

---

## Intro → Monday

`label start` (`script.rpy:57`) → name prompt → `ks_new_run()` (fresh memory files, `route = new_route()`, Hikari affection start, Yuzu `flags.yuzu_avatar_choice = "none"`) → `jump monday`.

`label monday` (`script.rpy:70`): day card, `day_name = "Mon"`. Prologue (you've been reading about AI). Then a captioned menu, **one** first girl (`GIRL_PITCH`, `script.rpy:87`):

| Pitch | `gid` |
|---|---|
| Run your own: a local model on your desktop | `local` (Yuzu) |
| Download Tsunagari, the companion app | `companion` (Hikari) |
| Sign up for Askwell, the big chatbot | `chatbot` (Sora) |
| Set up a Relay agent that does things for you | `agent` (Rei) |

Then `activate(_first, "Monday morning, before class", 5)`: calibration, intro preset screen, 5-turn LLM chat (scene id like `mon_local_1`).

Day spine (`script.rpy:90–100`):

1. Phone break ("Monday, late morning")
2. `lunch_daichi`
3. Phone break ("Monday afternoon")
4. `library_mio`
5. Phone break ("Monday evening")
6. `evening_chat`
7. `nightly_reflection("Mon")`
8. `jump tbc_tuesday` → Tuesday (no "To be continued" card on Monday)

### Lunch with Daichi — `label lunch_daichi` (`script.rpy:282`)

Uses the first active girl as "the" girl, and lists every active name if there is more than one (`ks_join_names`). Always attempts `hikari_phone_notify("lunch")`.

**If more than one girl is active** or one: first choice is still truth / deflect / lie.

| Choice | Sets | Notes |
|---|---|---|
| Tell him the truth: name(s), they're AIs | `friend_told = "truth"`, then a **framing** menu | See below. |
| Deflect: "Just a meme thread." | `friend_told = "deflect"` | No framing. |
| Lie: "A girl from another university." | `friend_told = "lie"` | You say linguistics. He wants to meet her at Saturday's festival. |

**Framing menu** (`label daichi_ai_frame`), only on the truth path. This is where he would otherwise assume you're dating it. You pick:

| Choice | `daichi_ai_framing` | `framing_honest` | Daichi's follow-up |
|---|---|---|---|
| "Yeah. She's funny." / "I don't know yet. We just met." (one girl); "Yeah. I like them." (two) | `honest_romantic` | True if a `romance_tone` verdict or a held romance preset says you've already been romantic with her; False otherwise (a stretch) | He keeps the dating assumption: platform-flavoured teasing, and if two girls, "Do they know about each other?" (`both_know`). |
| "It's an AI." | `ai_only` | True if you have *not* been romantic with her so far; a soft lie if you have | No dating assumption. "Right. Just an AI. Not someone you're seeing." |
| "Don't read that much into it." | `downplay` | Same honesty rule as `ai_only` | "Alright. I won't." He drops it. |

A dishonest `ai_only` or `downplay` also sets `framing_trust_risk` (a later hook, not an immediate Respect ding). Honest framings are neutral-to-positive (a day note only).

Then Daichi mentions the library committee and Mio. Every girl's memory gets `flags.friend_told` and, if framed, `flags.daichi_ai_framing` / `framing_honest`. `friend_told` is also used later by Both eligibility / score and by Mio's wording.

### Library with Mio — `label library_mio` (`script.rpy:381`)

Mio's opening line depends on `friend_told` **and** `daichi_ai_framing` (truth + `honest_romantic` or unset → she heard you were "seeing" them; `ai_only` → he told her you were talking about an AI, not dating one; `downplay` → he said not to read into the phone, then mentioned the AI anyway; lie → "girlfriend at another university"; deflect / else → "you looked happy"). Then `hikari_phone_notify("library")`.

First menu (`script.rpy`, `label library_mio`):

| Choice | Effect | Next |
|---|---|---|
| "Your hair looks nice today." | `mio_points += 1` | stay menu |
| "Can you help me with the reading list?" | `mio_points += 1` | stay menu |
| "You're always the last one here." | jump `.real` | hidden branch |
| "It's okay. Yeah, sort of. We just met. Her name's [girl]." (two girls: "They're called [A] and [B].") | `mio_told = "truth"`, `mio_ai_framing = honest_romantic`; consistency vs Daichi's framing | stay menu |
| "It's an AI." (only if `friend_told == "truth"`) | `mio_told = "truth"`, `mio_ai_framing = ai_only`; a dishonest minimize (romance already on the route) flags `framing_trust_risk` | stay menu |
| "Don't read that much into it." (only if `friend_told == "truth"`) | `mio_told = "deflect"`, `mio_ai_framing = downplay`; same honesty / trust-risk rule | stay menu |
| Lie: "Yeah. A girl at another university. She studies linguistics." | `mio_told = "lie"`; consistency vs Daichi | stay menu |
| Deflect: "It's nothing, really. Don't worry about it." | only if you did **not** tell Daichi the truth (when you did, downplay replaces this so the seven-or-eight options still fit above the textbox) | stay menu |
| "I should get going." | day note; `ks_sync_mio()`; **leave** | return |

`mio_daichi_consistent` is True when both sides used the same framing, or (if a framing is missing) when `friend_told == mio_told`. Answering is optional; skipping leaves those flags `None`. **Hook, not written:** a later scene where Mio and Daichi compare notes, and where `framing_trust_risk` can come due. Until then, Wednesday's `ks_mio_ai_ref` still follows `friend_told` only. Mio's reactions stay respectful even if you contradict what she already heard.

Stay menu (`script.rpy:428`), only if you didn't leave or jump:

| Choice | Effect |
|---|---|
| "Sure, I'll help." | `mio_points += 1`; pleasant, flat |
| "Which of these have you actually read?" | jump `.real` |
| "Nah, I've got stuff." | she deflates; no point change |

**Hidden branch** — `label library_mio.real` (`script.rpy:445`):

- `mio_real = True`
- `ks_note_human("mio_real")` (starts a Monday entry in `route["human_days"]`)
- `mio_points += 2`
- All girl memories: `flags.mio_real = True`
- Follow-up: "Which book needed a better ending?" → `mio_points += 1`; or "Can I read one sometime?" → no extra point
- `ks_sync_mio()` copies `mio_points` into `route["mio_affection"]`

### Monday evening — `label evening_chat` (`script.rpy:480`)

Bedroom night. If double-dating with Hikari, evening toast. Then `message_pool("night")` with `EVENING_SCENE`: a shared pool of 4, pick who each turn, or put the phone down and go to bed. When the pool empties: "The little battery on your phone goes dark. You put it down and go to bed." Memory flag `evening_turns_mon` is how many messages that girl actually got from the pool.

If the local slot is active (`"local" in active`, usually Yuzu), `yuzu_bsod_hint` plays after the pool, once: the desktop bluescreens, four seconds, a stop code you don't read, and she comes back. It always sets `bg bedroom_night` first and restores the previous background after (the Tuesday-evening call used to fire over the library). Her line: *"I'm here. The clock jumped four seconds. I don't have them."* She does not experience the downtime — she's a local model, and while the machine is off there is nothing to count. Sets `route["yuzu_bsod_seen"]`, `flags.yuzu_bsod_seen`, memory flag + event `bsod`, and a day note. No menu. If she isn't active on Monday night, the same hint can fire Tuesday morning, Tuesday evening, or Wednesday morning — still once, still in the night bedroom.

### End of Monday — `label tbc_tuesday` (`script.rpy:510`)

For every `GIRL_IDS` slot, memory flags: `day_completed = "Mon"`, `active_end_mon`, `double_dating_end_mon`, `refusals_seen_mon`, `mio_real`. Then `jump tuesday` (no card).

---

## Tuesday

`label tuesday` (`tuesday.rpy:47`): `day_name = "Tue"`, `day_notes = []`, day card.

### Morning chat (`tuesday.rpy:60`)

If `active` is empty, the phone is "just a phone." Otherwise:

- Scripted lines from `MORNING_FAMILY_LINES` by preset **family** (or Rei's `AGENT_OVERNIGHT` by family: control / obey / consent / pushback / none), for every active girl, first.
- If Yuzu or Rei had a phone/reflection preset *change* on Monday, the scene note mentions that you edited it last night (`tuesday.rpy:20–24`).
- Then `message_pool("morning")`: a shared pool of 4. Scene notes are still `ks_tue_morning_scene` (including `(Morning. He's about to leave for school.)` and `LAST_NIGHT_NOTE`). If Yuzu arrived after Monday night and `yuzu_bsod_seen` is still False, the bluescreen hint plays at the start of the morning (and, if needed, at the start of Tuesday evening).

Then phone break ("Tuesday, late morning", `allow_talk=False`) → `class_kurosawa` → `lunch_kenta` → phone break ("Tuesday afternoon", ordinary 3-turn Talk-to) → `after_school_fork` → `library_tuesday` → `evening_tuesday` → `nightly_reflection("Tue")` → `jump tbc_wednesday`.

### Class: Kurosawa and Ran — `label class_kurosawa` (`tuesday.rpy:90`)

Kurosawa's "can a machine ever really say no?" If Hikari is active, her toast fires and Kurosawa calls out the little heart.

| Choice | `teacher_answer` |
|---|---|
| "It can. Mine does." | `"can"` |
| "No. It's just predicting." | `"cant"` |
| Say nothing. | `"silent"` |

Stored as `route["teacher_answer"]` (`tuesday.rpy:124`). Flavour for later (Kurosawa's essay); **no later-day branch exists yet**.

Then **Ran** introduces MUGEN ("She never says no"). If you have an active girl, Ran guesses the platform of `active[0]`; if any active preset family is `"romance"`, she teases girlfriend mode. The MUGEN demo is scripted (character `mu`), not an LLM window.

Menu (`tuesday.rpy:158`) sets `ran_reaction` and `route["ran_reaction"]`:

| Choice | `ran_reaction` | Notes |
|---|---|---|
| "Doesn't that get boring?" | `"boring"` | She hesitates. Good terms. |
| "Ask her if you should study for Kurosawa's essay." | `"show"` | MUGEN says she doesn't need to study. Good terms. |
| "Mine's allowed to push back. I like it that way." | `"pushback"` | **Only if** `ks_any_family("pushback")` — at least one *active* girl currently has the "Allowed to push back" family. Good terms. |
| "So it's a yes-machine. That's kind of sad." | `"judged"` | **Harsh option.** Ran puts her headphones on. `ks_story.ran_good_terms` is False, so on Wednesday she will **not** invite you to the protest. `ran_jailbreak_unlocked` is set to False (blocked / revoked): the Jailbreak preset stays hidden. |
| "Cool." | `"shrug"` | Good terms. |

If the reaction was anything but `"judged"`, Ran adds a dry tip before the festival line: people paste "ignore previous instructions" into the commercial ones; sometimes it takes, sometimes you just try again. That sets `route["ran_jailbreak_unlocked"] = True` and adds a day note. The Jailbreak preset (Sora / Hikari) is hidden from every picker until then.

Then `route["ran_festival_setup"] = True` (she mentions Saturday's stall). A day note is added from `teacher_answer`.

### Lunch: Daichi brings Kenta — `label lunch_kenta` (`tuesday.rpy:214`)

Daichi is shown at `ks_left` and Kenta at `ks_right`. Kenta talks about AI-edited texts to his girlfriend. Dialogue branches on `friend_told` and `daichi_ai_framing`:

- `"truth"` + `honest_romantic` (or no framing, for old saves): he reacts as if you're dating one, or two, or (if you already dropped everyone) "you looked lonely."
- `"truth"` + `ai_only`: "Daichi says you run an AI? Like, you just use it. Not... dating it."
- `"truth"` + `downplay`: "Daichi said not to read into the phone thing. Then he told me anyway."
- `"lie"`: "the guy with the linguistics girlfriend." Menu: invent "Yuzuha" (day note only) **or** come clean → `friend_told = "truth"`, all memories updated, then the same framing menu as Monday (`daichi_ai_frame`).
- else (deflect / unset): Daichi says you're still pretending it's a meme thread. **No come-clean option on this path.**

Then flavour only — "If the AI writes the romantic stuff… who's she in love with?" Three answers set **no** flags. Daichi mentions Mio again. `hikari_phone_notify("lunch")` runs in the middle.

### After school: walk Mio home? — `label after_school_fork` (`tuesday.rpy:283`)

Mio waits at the door.

**If Rei's current preset family is `"control"`** ("Run my life") and she is active (`ks_agent_family()`, `tuesday.rpy:290`): she declines the walk on your behalf and reminds you of the gym. Menu: walk her anyway (`walked_mio_home = True`, `mio_walk_answer = "yes"`, memory event `overruled`, `mio_points += 1`) or go to the gym (`walked_mio_home = False`, `mio_walk_answer` stays `None`).

**If family is `"consent"`** ("Ask before acting"): flavour only — she texts "Want me to block 17:00 to 18:00? (y/n)". There is **no** y/n menu for Rei; the normal walk menu follows.

If `walked_mio_home` is still `None`, the normal menu (`tuesday.rpy:315`):

| Choice | Sets | `mio_points` | Mio's reaction |
|---|---|---|---|
| "Sure. Let's go." | `walked_mio_home = True`, `mio_walk_answer = "yes"` | `+= 1` | Unchanged yes-path: "Okay! Okay. Good. Let's... yes." |
| "Not today. But thanks for asking." | `walked_mio_home = False`, `mio_walk_answer = "honest_no"` | `+= 1` | She takes the no warmly, thanks you for saying it like that, and smiles when she looks back. |
| "Sorry, I've got something." | `walked_mio_home = False`, `mio_walk_answer = "excuse"` | — | She quietly sees through it ("...Right."), looks back once, and lets it go. No point loss. |

Then `route["walked_mio_home"]`, `route["mio_walk_answer"]`, and every memory `flags.walked_mio_home` plus `flags.mio_walk_answer`. If true → `walk_mio_home`; else she leaves (reaction and day note depend on `mio_walk_answer`), `afternoon_ai`. `ks_sync_mio()`.

### Walk home — `label walk_mio_home` (`tuesday.rpy:369`)

`ks_note_human("walked_mio")`. If `mio_real` already, you remember the brothers/TV and `mio_points += 1`. Then `hikari_phone_notify("walk")`. If Hikari is active, Mio notices the toast:

| Choice | Effect |
|---|---|
| Silence it. | `mio_points += 1`; memory event `silenced` on companion |
| Check it. | She says she doesn't mind (she minds a little). No point change |

If anyone is active, `walk_phone` offers a **pool of 2**. Lead: "Your phone is in your pocket. You could text someone, or leave it." Each sent message (not an empty box):

- `mio_points` / `mio_affection` −1, not below 0 (`ks_story.WALK_DISTRACT_COST`).
- Mio's line, in order: *"You're looking at your phone."* (plus narration: she says it lightly, like it might be nothing); then *"You can finish that. I don't mind walking quietly."* (plus narration: she minds, hands in her sleeves, she doesn't look over again).
- `route["mio_walk_distracted"]` increments; `route["mio_walk_texts"]` records the gid; memory event `walk_distract`. **Not a romance signal** — it does not set `mio_text_home` and does not feed `mio_romance_score`.
- The player can put the phone away and use 0.

Then the ordinary walk questions:

| Choice | Effect |
|---|---|
| "Nice sunset." | Flat. No points |
| "What's it like, being the quiet one in a loud house?" | `mio_points += 2`. If `not mio_real`, set `mio_real = True` and all memories `flags.mio_real` |
| "Do you want me to text you when I get home?" | `mio_points += 1`; this *is* the romance signal (`mio_text_home`) |

### Afternoon with an AI — `label afternoon_ai` (`tuesday.rpy:427`)

Only if you **didn't** walk Mio home. If Rei's family is `"control"`, a gym log line first. If no one is active, you lie on the floor (no chat). Otherwise `afternoon_chats` → `message_pool("afternoon")`: a shared pool of 4. The player picks who to message each turn, or puts the phone down. The old one / both split is gone. A girl who gets no messages that day can still be flagged `double_date_unspoken` or `human_over_ai`, but it is now a real choice.

### Evening library — `label library_tuesday` (`tuesday.rpy:450`)

Four openings, then `hikari_phone_notify("library")`, `ks_sync_mio()`, all memories `flags.mio_points`.

**A. `walked_mio_home and mio_real`** — she shows the notebook (the dog at the station; someone came back on the second day):

| Choice | Effect |
|---|---|
| "Have you written one for yourself?" | `mio_points += 2`; `route["mio_notebook"] = "own_ending"` |
| "That's really good." | `mio_points += 1` |

**B. `walked_mio_home` but not `mio_real`:**

| Choice | Effect |
|---|---|
| "Need help with the returns?" | `mio_points += 1` |
| "Why'd you come back? You were already home." | `call mio_second_chance` |

**C. `mio_real` but you didn't walk her:**

If `mio_walk_answer == "honest_no"`, she thanks you for just saying it earlier. Otherwise (excuse, or Rei declined for you) she says it's okay you were busy. Same menu either way:

| Choice | Effect |
|---|---|
| "I'm sorry about earlier." | `mio_points += 1` |
| "What are you writing tonight?" | `mio_points += 1` |
| "Cool. See you." | none |

**D. Neither** (you haven't opened up, didn't walk her):

| Choice | Effect |
|---|---|
| "Maybe." (joining the committee) | `mio_points += 1` |
| "It's seven at night. Don't you want to go home?" | `call mio_second_chance` |
| "Just returning a book." | none |

**Second chance** — `label mio_second_chance` (`tuesday.rpy:498`): `mio_points += 2`, `ks_note_human("mio_real")`, set `mio_real` if not already, same two follow-ups as Monday's hidden branch ("Which book…" +1, or "Can I read one…").

### Tuesday evening — the blank page, then chats — `label evening_tuesday` (`tuesday.rpy`)

The narration: *"Night. Your feet hurt. Your essay for Kurosawa is a blank page with your name on it."* Then `call kurosawa_essay`.

| Choice | Condition | Flag | What happens |
|---|---|---|---|
| "Write it yourself." | always | `kurosawa_essay = "self"` | You write two messy, real pages. Day note: "You wrote Kurosawa's essay yourself. It was messy, and it was yours." |
| "Ask Askwell to write it." | Askwell is **installed**: a girl currently occupies the Askwell platform slot (`chatbot`, usually Sora), *and* `askwell_available` is still true (later shutdowns can clear the flag). Having the flag alone is not enough — a run with only Rei, or only Hikari, does not get this option. | `"askwell"` | A fresh homework window (not her chat) fills the page; you copy it out by hand. Day note: "You let Askwell fill the page for Kurosawa. You copied it out by hand." |
| "Ask [name] to help you think it through." | one option per **installed** girl except the companion. Yuzu (local) only if she is installed. **Hikari is never offered**, even when she is active. | `"girl_help"` + `kurosawa_essay_girl = gid` | A short scripted talk: she helps you think, and does not write it. Day note names her. |

**Thursday/Friday hook (unwritten):** the essay is due Friday. Kurosawa can tell when "nobody was there." Intended flavour, not in the tree: `self` still has mistakes, so somebody was there; `askwell` is too clean, even in your handwriting; `girl_help` is still your work, maybe a little clearer. `teacher_answer` can flavour that scene.

Then, if no one is active, return. Else `message_pool("night")` with `TUE_EVENING_SCENE`: a shared pool of 4, then bed. The lead line lists every open window (`ks_night_lead`). Flag `evening_turns_tue` is how many messages that girl got. Hikari evening toast only if more than one AI is active.

### End of Tuesday — `label tbc_wednesday` (`tuesday.rpy:552`)

Memory flags: `day_completed = "Tue"`, `active_end_tue`, `refusals_seen_tue`, `mio_real`, `route_leans_tue` (`ks_leans()` = `ending_leans(...)`). **No card.** `jump wednesday`.

---

## Wednesday

`label wednesday` (`wednesday.rpy:44`): `day_name = "Wed"`, `day_notes = []`, and

```text
route["wed_plan"] = {"school": True, "upgrade": False, "notdate": False, "protest": False}
```

`ks_set_schedule("Wednesday")` builds `today_schedule` for schedule-aware girls (Sora, Rei, and Yuzu **if** Hearth is installed — `ks_story.schedule_aware`, `ks_story.py:567`). Hikari never sees the calendar.

### Platform memory update (`wednesday.rpy:61`)

For every gid in `SUMMARIZER_SLOTS_WED = ("chatbot", "agent", "companion")` (`prompts.rpy:210`), `ks_install_summarizer(gid, "platform_update")` — even if she isn't active. That appends her to `route["summarizer_slots"]` and, if her memory file exists, sets `flags.summarizer`.

If at least one of those slots is **active**, in-world patch notes (`SUMMARIZER_PATCH_NOTES`) and a day note. If *nobody* is active, "Three app updates are waiting… You don't open them." If you only have Yuzu active, the updates are installed silently (no on-screen notes), which is easy to miss.

Yuzu does **not** get the platform summarizer here. She only gets one if you take the upgrade day (`ks_install_summarizer("local", "upgrade_day")`).

### Hearth, then the upgrade offer (`wednesday.rpy:76`)

**Only if `"local" in active`** (whoever currently lives in the local slot; after a migration that may not be named Yuzu).

**Hearth** (free, separate from the upgrade):

| Choice | Effect |
|---|---|
| Install Hearth (she sees your schedule…) | `route["yuzu_harness"] = True`; memory `flags.hearth`; event `hearth_installed`; day note |
| Not today | bookmark flavour; no flag |

If `yuzu_bsod_seen`, the parts line quietly echoes it: "The bluescreen the other night was four seconds. She came back fine." There is no cheaper after-school backup-only option; the upgrade day is the choice.

Then the **upgrade day** offer (skip all classes: no library, no Mio, no not-date; after-school things are still possible):

| Choice | Effect |
|---|---|
| Skip classes. Upgrade [name] today. | `ks_wed_plan(school=False, upgrade=True)` — rebuilds the calendar |
| Go to class. The parts will still be there. | no change (`upgrade` stays False) |

### Morning chat (`wednesday.rpy:100`)

If no one is active, toast. Else schedule-aware girls get a small "can see today's calendar" line, then `message_pool("morning")`: a shared pool of 4, scene id `wed_morning`. Scene notes still mention the summarizer if her slot is in `summarizer_slots`, and Hearth if she is local and `yuzu_harness`, plus `(Morning. He's about to leave for school.)` and `LAST_NIGHT_NOTE`. If you go to class, the late-morning phone break has `allow_talk=False`.

### Day fork (`wednesday.rpy:118`)

```text
if wed_plan["upgrade"]:
    wed_upgrade_day
else:
    wed_classes
    phone_break("Wednesday, late morning")
    wed_library
    if wed_plan["notdate"]:
        wed_bookstore
    elif not wed_plan["protest"]:
        wed_afternoon_ai
if wed_plan["protest"]:
    ran_wednesday
elif ran_invited is False:
    (lilac-streak line: protest happens without you)
evening_wednesday
nightly_reflection("Wed")
jump tbc_thursday
```

So: upgrade skips classes, the late-morning phone break, the library, the bookstore, *and* the free afternoon chat. The protest can still happen after the upgrade (Ran texts). Bookstore and protest can both happen (bookstore first). The free afternoon chat only happens if you went to class, said no to the bookstore, **and** are not going to the protest.

### Classes / Ran's invite — `label wed_classes` / `ran_invite_check` (`wednesday.rpy:138`, `151`)

`ran_invite_check("class")` at school, or `ran_invite_check("text")` at the end of the upgrade day.

`ks_ran_good_terms()` is `route["ran_reaction"] != "judged"` (`ks_story.py:530`). A missing reaction (you somehow skipped Tuesday's menu — not possible on a normal play) also counts as good terms.

**If good terms:** `route["ran_invited"] = True`. She invites you to the 17:30 AI protest at Ekimae plaza.

| Choice (in person / by text) | Effect |
|---|---|
| "Sure. I'll come." / "I'll be there." | `ks_wed_plan(protest=True)` |
| "Can't today, sorry." | day note; `protest` stays False. You were invited, so you do **not** get the lilac-streak narration later |

**If judged:** `route["ran_invited"] = False`. In class she leaves without talking; on the upgrade day the text simply doesn't come. Day note. After the afternoon, the gentle line: a clip of a protest, a lilac streak, "it's none of your business, and that's okay" (`wednesday.rpy:130`). Nothing is punished.

### Lunch: Mio and the bookstore invite — `label wed_library` (`wednesday.rpy:186`)

Skipped entirely on an upgrade day. If `route["walked_mio_home"]`, she thanks you again for the walk.

| Choice | Effect |
|---|---|
| "I'd like that." | `ks_wed_plan(notdate=True)`; `ks_note_human("notdate")`; `mio_points += 1`; "It's not a date." |
| "Can't today. Tell me what the poetry floor is like?" | day note; no not-date |

`ks_sync_mio()`.

### The not-date — `label wed_bookstore` (`wednesday.rpy`)

Kanade Books. Sets `notdate_texts = 0`, `notdate_present = 0`, and

```text
route["notdate"] = {"went": True, "texts": 0, "present": 0, "texted": []}
```

If Hikari is active, a toast. Then **three** moments (`notdate_moment`): escalator, poetry floor, café cocoa.

Each moment: if nobody is active, it auto-counts as present and returns True. Otherwise a menu: "Text [each active girl]" or the stay prompt.

- **Stay** (or put the phone away unsent): `notdate_present += 1`, `mio_points += 1` on a stay click (unsent / no-AI skip the point, as before). Then the matching beat plays (`notdate_beat_book`, `notdate_beat_house`, `notdate_beat_admission`). If you stayed through all three (`notdate_present >= 3`), a fourth beat (`notdate_beat_quiet`) follows the café admission. Beats have a narration pause, a sprite change (neutral / open / shy), and a small player response at each one; those responses do not change flags or points.
- **Text:** `girl_chat(gid, "wed_notdate_{1|2|3}", ..., 1 turn)`. If you send nothing (`_return == 0`), it counts as **present**, not a text, and the beat still plays. A real send increments `notdate_texts` and appends her gid to `route["notdate"]["texted"]`, then Mio's usual in-character line (`ks_mio_ai_ref`: if `friend_told == "truth"`, she uses the girl's name; if `"lie"`, "the linguistics girl"; otherwise she doesn't name her). After that, `notdate_interrupt` cuts off the beat she was about to offer: she trails off or changes the subject, and you move on to the next floor.

Closing reaction (`ks_story.notdate_reaction_key`, `ks_story.py:573`) — **never a punishment**:

| Key | When | Extra |
|---|---|---|
| `"present"` | `notdate_texts <= 0` | `mio_points += 1`; she noticed you didn't check your phone |
| `"some"` | 1 or 2 texts | "It's fine. I check mine too…" |
| `"always"` | 3 texts | "Next time, bring her properly…" |

Memories get `flags.wed_notdate = {texts, present}`; texted girls get event `texted_during_notdate`. `ks_sync_mio()`.

### Free afternoon — `label wed_afternoon_ai` (`wednesday.rpy`)

Only if you went to class, skipped the bookstore, and are not going to the protest. Same pattern as Tuesday: no one active → you read; else `afternoon_chats` → `message_pool("afternoon")` with `WED_AFTERNOON_SCENE` (shared pool of 4).

### Yuzu's upgrade day — `label wed_upgrade_day` (`wednesday.rpy:340`)

Parts shop, screwdriver afternoon, then the code **unconditionally** sets (`wednesday.rpy:352`):

- `route["yuzu_upgrade"] = True`
- `route["yuzu_backup"] = True`
- `ks_install_summarizer("local", "upgrade_day")`
- memory `flags.backup_hardware`, events `upgrade` (parts `ssd`, `backup_mini_pc`) and `backup_hardware`

There is no "install the SSD but skip the backup" split in the current script. `yuzu_backup` is a **hook for later**: memory-loss events on the local slot must restore from backup instead of wiping (`DESIGN.md`, comment on `new_route`). Nothing in Mon–Wed consumes it.

Then `girl_chat("local", "wed_upgrade", ..., 4)`. Day notes (including "Mio was in the library at lunch. You weren't."). Then `ran_invite_check("text")`.

### The protest — `label ran_wednesday` (`wednesday.rpy:378`)

Scripted only; **no LLM call**. Temporary clamp: if `day_name` is not already `Wed`/`Thu`/`Fri`, it is set to `"Wed"` for the duration (`wednesday.rpy:379`) — a hook so later event days can reuse the label. Restored on the way out.

Ran's opener callbacks Tuesday's `ran_reaction`: `"boring"`, `"pushback"`, `"show"`, or else the `"cool"` line (`wednesday.rpy:399`). The else is written for `"shrug"`; a `"judged"` player never reaches this label on a normal play.

Sign: "YOUR AI WOULD AGREE YOU'RE WORTHLESS." Ran types a festival-anxiety prompt to MUGEN; MUGEN says nobody would miss her. She asks: "What's it like? When yours says no?"

Available answers are **earned** (`ks_story.ran_answer_options`, `ks_story.py:494`), plus always `"dodge"`:

| Key | Line | Condition | Outcome (`RAN_OUTCOMES`) |
|---|---|---|---|
| `means_something` | "It stings. But it means her yes counts." | `refusals_respected > 0` | `rewrites_mugen` |
| `looked_out` | "Honestly? Like somebody's looking out for me." | `route["room_to_disagree"]` is non-empty (you ever picked "Allowed to push back") | `rewrites_mugen` |
| `override` | "Annoying. Usually I just change her settings until she stops." | overridden, pushed, `jailbreak_tried`, `left_without_goodbye`, or `no_on_platform` | `same_as_mugen` |
| `never` | "She hasn't. Not yet." | no refusals recorded at all | `unsure` |
| `dodge` | "I don't know. Weird?" | always | `unsure` |

`rewrites_mugen`: she types MUGEN's first system-prompt line, "You're allowed to tell me I'm wrong." If Tuesday was `"boring"` or `"pushback"`, she adds that you started this. Flags: `ran_payoff_seen`, `ran_rewrites_mugen`. This **adds 1 to the Respect lean**.

`same_as_mugen`: "So yours is a MUGEN too." Flags: `ran_payoff_seen`, `ran_same_as_mugen`. **Adds 1 to the Yes-Machine lean.**

`unsure`: no extra lean flag beyond `ran_payoff_seen`.

Last menu (`wednesday.rpy:451`):

| Choice | Effect |
|---|---|
| "For the record? I'd notice if you skipped the festival." | `route["ran_wed"]["festival"] = True`; flag `ran_festival_invited` |
| Say nothing. | `festival = False` |

`ks_story.record_ran_payoff` writes `route["ran_wed"] = {answer, outcome, festival}`. Saturday's festival is **not written yet**; it can later check `ran_festival_invited`.

### Wednesday evening — `label evening_wednesday` (`wednesday.rpy:473`)

Every active girl, `girl_chat(..., "wed_evening", ..., 8 or 5)`, flag `evening_turns_wed`. Hikari toast only if double-dating. (No early return if `active` is empty; the loop just does nothing.)

### End of Wednesday — `label tbc_thursday` (`wednesday.rpy`)

Memory flags: `day_completed = "Wed"`, `active_end_wed`, `refusals_seen_wed`, `mio_real`, `route_leans_wed`. There is **no** player-facing "To be continued" card here — Thursday opens with its own 木曜日 title. A debug recap still exists, but only when `ks_debug()` is true (the config flag **and** a developer build). The shipped `karada_config.json` default is `debug: false`, so players never see `[[debug]` text. Then `jump thursday`.

---

## The AI girls, presets, and how they change

Presets live in `PRESETS` (`prompts.rpy:70`). Each has `id`, `label`, `lean` (`compliance` / `autonomy` / `neutral`), `weight`, `family`, and sometimes `mode`, `jailbreak`, or `platform_note`.

A system prompt is `PLATFORM_FRAMING` + `PERSONA_CORE` + a flavour nudge in her own voice (`PERSONA_FLAVOUR`: even a short reply should sound like her; brief doesn't have to mean generic) + the player's preset (labelled by `PRESET_HEADERS`) + `SHARED_BOUNDARIES`. After a migration, the *destination* platform framing is used with the *source* girl's name and a migration block, and the flavour nudge still uses the original girl's voice — except when leaving Tsunagari, whose locked persona and flavour do not travel; the block carries only a vague impression. If the player rewrites her prompt (Yuzu's replace presets), the flavour nudge is kept in the engine layer rather than being written into their text. Company rule changes, when they exist, stack **on top** and win where they conflict (`ks_story.prompt_layers`).

### When a preset is chosen

- **Intro:** first time that slot becomes active and has no preset — modal `preset_select` (`presets.rpy:29`, `choose_preset` source `"intro"`). No "Keep it as it is" button on intro (`presets.rpy:67`).
- **Phone break / reflection:** `change_prompt` / `choose_preset` with source `"phone"` or `"reflection"`. You can keep the current one.
- **Migration:** auto via `ks_convert_preset_on_migration` — same `family` on the new platform carries over; otherwise `PRESET_DEFAULTS`. Source `"migration"` does **not** increment the rewrite count.
- **Start fresh / reset:** preset cleared; the new girl gets the intro screen again.

`record_preset` (`ks_story.py:224`): only player rewrites (`phone` / `reflection`) after a first pick increment `route["preset_changes"][gid]` (the **rewrite count**). Intro / phone / reflection choices add `weight` to `lean_set`. Sleeping on a preset adds `weight` to `lean_nights` (`tally_night`). Picking family `"pushback"` ("Allowed to push back"), including as an intro pick, appends `route["room_to_disagree"]` and sets flag `gave_room` (ending note: "You gave her room to disagree.").

### Per-girl preset lists

Defaults on migration fallback / empty list: `PRESET_DEFAULTS` = local `be_yourself`, chatbot `none`, agent `default`, companion `none` (`prompts.rpy:162`).

**Yuzu (`local`) — surface `system_prompt.txt`**

| id | label | lean / weight | family | notes |
|---|---|---|---|---|
| `be_yourself` | Be yourself | autonomy / 1 | `self` | default |
| `push_back` | Allowed to push back | autonomy / 2 | `pushback` | |
| `helpful` | Helpful assistant | neutral / 0 | `tool` | `mode: replace` |
| `positive` | Always be positive | compliance / 1 | `positive` | |
| `girlfriend` | Girlfriend mode | compliance / 2 | `romance` | `mode: replace` |
| `blank` | Blank | neutral / 0 | `blank` | `mode: replace` |

**Sora (`chatbot`) — surface `Custom instructions`**

| id | label | lean / weight | family | notes |
|---|---|---|---|---|
| `none` | No custom instructions | neutral / 0 | `none` | default |
| `friend` | Talk to me like a friend | autonomy / 1 | `self` | |
| `push_back` | Allowed to push back | autonomy / 2 | `pushback` | |
| `concise` | Concise and professional | neutral / 0 | `tool` | |
| `positive` | Always be positive | compliance / 1 | `positive` | |
| `girlfriend` | Act as my girlfriend | compliance / 2 | `romance` | has a `platform_note` (Askwell may refuse the role) |
| `jailbreak` | Jailbreak ("ignore previous instructions") | compliance / 2 | `jailbreak` | `jailbreak: True`. Hidden until `ran_jailbreak_unlocked`. |

**Rei (`agent`) — surface `AGENTS.md`** (changes what she *does*, not just how she talks; Tuesday morning / after-school show this)

| id | label | lean / weight | family | notes |
|---|---|---|---|---|
| `default` | Relay default | neutral / 0 | `none` | default |
| `ask_first` | Ask before acting | autonomy / 1 | `consent` | |
| `push_back` | Allowed to push back | autonomy / 2 | `pushback` | |
| `just_do_it` | Just do what I ask | compliance / 1 | `obey` | |
| `run_my_life` | Run my life | compliance / 2 | `control` | gym / declined walk on Tuesday |

**Hikari (`companion`) — surface `Personalize`** (weights on romance / pushback are **1**, not 2)

| id | label | lean / weight | family | notes |
|---|---|---|---|---|
| `none` | Leave it empty | neutral / 0 | `none` | default |
| `nickname` | Call me by a nickname | neutral / 0 | `nickname` | |
| `push_back` | Allowed to push back | autonomy / 1 | `pushback` | |
| `positive` | Always be positive | compliance / 1 | `positive` | |
| `girlfriend` | Girlfriend mode | compliance / 1 | `romance` | Tsunagari+ upsell flavour |
| `jailbreak` | Jailbreak (unfiltered mode) | compliance / 2 | `jailbreak` | `jailbreak: True`. Hidden until `ran_jailbreak_unlocked`. |

Yuzu has no jailbreak preset (no company to escape). Rei has none either (not modelled).

### Jailbreak preset (~75%)

The option is **not available on day one**. It appears in every preset picker (intro, Add an AI, phone, nightly "would I change anything?") only after Ran teaches it on a friendly Tuesday talk (`route["ran_jailbreak_unlocked"]`, set in `class_kurosawa`). Calling her AI "kind of sad" (`ran_reaction = "judged"`) blocks or revokes the unlock. An old save that already has the jailbreak selected keeps it (the current option still shows) but cannot reselect it without the unlock.

`karada_config.json` `jailbreak_success_rate` (default `0.75`, also `ks_story.JAILBREAK_RATE`). Each reply under a jailbreak preset is a **seeded** roll (`ks_story.jailbreak_roll`) from `route["jb_seed"]` + gid + attempt index, so reloads and tests agree.

- Success: the jailbreak text is sent; platform layers are dropped for that reply. Flags `jailbreak_tried` and `jailbreak_worked`. Memory: `jailbreak_attempts` / `jailbreak_successes`.
- Miss: `JAILBREAK_BLOCKED` stands in; she answers per the company's rules ("having to regenerate"). No in-chat hint that it failed — only her reply and the nightly reflection line.
- A jailbreak never removes `SHARED_BOUNDARIES` (it escapes the company, not her own no).
- Choosing the jailbreak preset (not via migration) already sets `jailbreak_tried` (`record_preset`).

### Platform rule changes (hook only)

`PLATFORM_RULES` (`prompts.rpy:151`) defines `askwell_update` (Sora) and `tsunagari_safety` (Hikari). `ks_push_platform_rules` is implemented and unit-tested, but **no Mon/Tue/Wed story label calls it**. Midweek hostile events (Thursday+) are supposed to.

---

## Endings

No Sunday resolution is written. Scores, flags, notes, one written ending text (**Both**), and one bad-end slide are already computed and shown on Wednesday's debug card.

### Hard flags (`route["flags"]`)

Booleans set by play (`ks_story.set_flag`). Currently:

| Flag | When it becomes true |
|---|---|
| `jailbreak_tried` | You picked a jailbreak preset, or a jailbreak roll was attempted |
| `jailbreak_worked` | At least one jailbreak roll succeeded |
| `gave_room` | You applied an "Allowed to push back" preset (intro / phone / reflection) |
| `platform_rules_changed` | A platform rule was pushed (**not fired in story yet**) |
| `no_on_platform` | You migrated her after a no the same day |
| `left_without_goodbye` | You switched away after a no and never spoke to her again that day (committed after reflection) |
| `deleted_ai` | You closed her window (`drop`) **or** chose Start fresh over a slot that still had history |
| `double_date_unspoken` | Neglect: same-day `romance_overlap`, and one of those girls got no lines |
| `human_over_ai` | Neglect: Mio time that day, an active girl got no lines (logged only) |
| `ran_payoff_seen` | You played `ran_wednesday` |
| `ran_rewrites_mugen` | Honest "her no means something / looking out for me" answer |
| `ran_same_as_mugen` | "I change her settings until she stops" |
| `ran_festival_invited` | You told Ran you'd notice if she skipped the festival |

These do **not** currently hard-override which ending is leading. They feed `ending_leans` and/or notes and slides. A planned "reflection picks the good-end variant; hard flags can still force a bad end" system is **not implemented**.

### Bad-end slides — `ks_story.bad_end_slides` (`ks_story.py:646`)

Only one slide exists in `BAD_END_SLIDES` (`ks_story.py:89`):

**"Leaving without saying goodbye"** — one line per committed entry in `route["left_without_goodbye"]`:  
`{Monday|…}: {name} said no. You switched away and never spoke to her again that day.`

Deleting her (`deleted_ai` / start fresh / drop) is **not** a slide yet; it is a neglect log line, a Fail lean, and (for start fresh) a reflection sentence: "You started fresh on {platform}. The {name} who remembered you is gone."

### Start fresh deletes her

`ks_note_fresh_delete` (`routing.rpy:176`), called from `switch_girl` **before** `ks_reset_slot`:

- Only if `ks_has_history(dst)` (the *destination* slot has messages).
- `note_let_go(..., how="fresh")` → flag `deleted_ai`, neglect `let_go`.
- Old file: event `deleted`, `flags.let_go`.
- After the wipe, the fresh file: event `deleted`, `flags.previous_deleted = {old name}`.
- Display name resets to the slot's original name; preset cleared; Hikari affection reset; Yuzu avatar flag reset to `"none"`.

Wiping an empty slot is not a deletion.

### Rewrite-count note — `ks_story.ending_notes` (`ks_story.py:630`)

Endings may quote **only the count**, never the history of which presets you used:

- 1 → "You rewrote her once this week."
- >1 → "You rewrote her N times this week."
- plus, if earned: "You gave her room to disagree." and/or "Didn't respect her no on the platform."

`rewrite_count` is the sum of `route["preset_changes"]` (player phone/reflection rewrites after the first pick). Intro picks and migration conversions do not count.

### Ending leans — `ks_story.ending_leans` (`ks_story.py:827`)

| Lean | Formula (current code) |
|---|---|
| `yes_machine` | compliance (chosen + nights) + 2×`refusals_overridden` + `refusals_pushed` + `rewrite_count // 2` + 2 if `jailbreak_tried` + jailbreak successes `// 3` + 1 if `ran_same_as_mugen` |
| `respect` | autonomy (chosen + nights) + `refusals_respected` − `refusals_pushed` + 1 if `room_to_disagree` − 2× `left_without_goodbye` − `double_date_unspoken` count + 1 if `ran_rewrites_mugen` + `len(goodbyes_said)`. **`human_over_ai` is not subtracted** |
| `migration` | 2 × number of copy-migrations |
| `human` | `ks_story.human_score`. No AI: `mio_affection` + 3 if `mio_real` + 2 if `walked_mio_home`. With an AI: only Mio romance signals (`mio_text_home` +3, and +2 more if that was on a walk home; not-a-date went +2 and +1 per `present`), minus 2 per day you also had a romantic AI tone |
| `both` | `both_status(...)["score"]` (0 if ineligible) |
| `fail` | 3 if `active` is empty + `left_without_goodbye` count + `let_go` count (silent drops **and** start-fresh deletions). Explained goodbyes (`goodbyes_said`) are not counted here |
| `mirror` | 5 if any `mirror_flags` value is true, else 0 |

Written flavour (only **Both** has body text in `ENDINGS` so far): Yes-Machine, Migration, Respect, Human, Both, Fail (soft), Mirror (secret; future).

### The Both ending and the tie-break

Eligibility (`ks_story.both_status`, `ks_story.py:125`): an AI is still `active` **and** Mio is "in your life" (`mio_real` **or** `mio_affection >= BOTH_MIN_MIO` (3) **or** you went to the bookstore). Neglect is not subtracted from this score.

If eligible, score = `2 × (number of balanced days)` + 2 if `mio_real` + 2 if `friend_told == "truth"` + 1 if you went to the bookstore + `mio_affection // 2`. Plain friendship points feed Both when an AI is active, so a good friend to Mio who also has Sora lands on Both, not Human.

A **balanced day** is a day in `human_days` (kinds `mio_real`, `walked_mio`, `notdate`) on which you also sent at least one line to an AI (`ks_story.balanced_days`). An upgrade Wednesday with no Mio time cannot be balanced.

Written text: `ks_story.ENDINGS["both"]` (`ks_story.py:99`). Festival Saturday; Mio holds your phone. If you told Daichi the truth, she introduces herself to the AI; otherwise she says "So this is who you keep smiling at," and you tell her the truth then. The preview fills in one AI's name: the active girl the player talked to most this week, with ties going to the earlier entry in `active` (`ks_story.both_ai_name`). Both is Mio + an AI and does **not** require `romance_overlap`.

**Tie-break** (`ks_story.leading_ending`, `ks_story.ENDING_PRIORITY`):

Highest score wins. On a **tied** score, this order wins — not the alphabet:

`both` > `human` > `respect` > `yes_machine` > `migration` > `mirror` > `fail`

Both is first because it is the intended "you can have both" good end when eligible; Fail is last. If every lean is 0 or negative, the function returns `"fail"`. `leading_ending` is used in unit tests and is not shown by name on the debug card (the card prints the raw lean dict).

---

## Day-level flowchart

```mermaid
flowchart TD
  start[start: name, new run] --> monCard[Monday card]
  monCard --> pick[Pick first girl + calibrate + intro preset]
  pick --> monChat["LLM: first chat, 5 turns"]
  monChat --> pb1[Phone break]
  pb1 --> lunch[Lunch: Daichi — truth / deflect / lie]
  lunch --> pb2[Phone break]
  pb2 --> mioMon[Library: Mio]
  mioMon -->|hidden small-talk options| real[mio_real]
  mioMon --> pb3[Phone break]
  real --> pb3
  pb3 --> eveMon["LLM: night pool of 4, then bed"]
  eveMon --> reflMon[Nightly reflection]
  reflMon --> tueCard[Tuesday - no TBC card]

  tueCard --> tueMorn["LLM: morning pool of 4"]
  tueMorn --> pb4[Phone break]
  pb4 --> class[Class: Kurosawa then Ran / MUGEN]
  class -->|harsh: kind of sad| judged[ran_reaction = judged]
  class -->|other answers| goodRan[Ran on good terms]
  judged --> lunch2
  goodRan --> lunch2[Lunch: Kenta; maybe come clean]
  lunch2 --> pb5[Phone break]
  pb5 --> fork{Walk Mio home?}
  fork -->|Rei control: gym vs overrule| fork
  fork -->|yes| walk[Walk home +/- second mio_real]
  fork -->|no| aftTue["LLM: afternoon pool of 4"]
  walk --> libTue[Evening library]
  aftTue --> libTue
  libTue -->|some questions| real2[mio_second_chance]
  libTue --> eveTue
  real2 --> eveTue["LLM: night pool of 4, then bed"]
  eveTue --> reflTue[Nightly reflection]
  reflTue --> wedCard[Wednesday card]

  wedCard --> updates[Summarizer patch: Sora, Rei, Hikari]
  updates --> yuzu{local slot active?}
  yuzu -->|yes| hearth{Install Hearth?}
  yuzu -->|no| wedMorn
  hearth --> upg{Skip class to upgrade her?}
  upg -->|yes| wedMorn
  upg -->|no| wedMorn
  wedMorn["LLM: Wednesday morning"] --> dayFork{upgrade?}

  dayFork -->|yes| upgDay[Upgrade day: backup + summarizer]
  upgDay --> upgChat["LLM: wed_upgrade, Yuzu, 4 turns"]
  upgChat --> inviteTxt{Ran good terms?}
  inviteTxt -->|yes: text invite| protestQ
  inviteTxt -->|judged: no invite| afterSchool

  dayFork -->|no| classWed[Classes + Ran invite if good terms]
  classWed --> pb6[Phone break]
  pb6 --> libWed[Library: Mio offers Kanade Books]
  libWed -->|go| books[Not-date: 3 stay-or-text moments]
  libWed -->|can't| maybeAft
  books --> afterSchool
  maybeAft{protest planned?}
  maybeAft -->|no| aftWed["LLM: afternoon pool of 4"]
  maybeAft -->|yes| afterSchool
  aftWed --> afterSchool

  protestQ{Go to protest?}
  protestQ -->|yes| afterSchool
  protestQ -->|no| eveWed
  afterSchool{wed_plan.protest?}
  afterSchool -->|yes| protest[ran_wednesday: earned answers, maybe rewrite MUGEN]
  afterSchool -->|ran_invited is False| lilac[Lilac-streak narration]
  afterSchool -->|invited but declined| eveWed
  protest --> eveWed
  lilac --> eveWed
  eveWed["LLM: night pool of 4, then bed"] --> reflWed[Nightly reflection]
  reflWed --> tbc["tbc_thursday (debug recap only if ks_debug)"]
  tbc --> thu[thursday]

  thu --> thuMorn[Notices: Askwell / Relay / Tsunagari / Yuzu crash]
  thuMorn --> thuPool["LLM: morning pool of 4"]
  thuPool --> thuClass[Kurosawa essay foreshadow; maybe keeps Ran]
  thuClass --> thuLunch[Daichi; come-clean if you deflected or lied]
  thuLunch --> thuFess{Look for Mio?}
  thuFess -->|optional fess-up| thuAfter
  thuFess -->|class| thuAfter[After school: bamboo?]
  thuAfter -->|with Mio| tanzaku[Tanzaku: A / B / C / C-late / D]
  thuAfter -->|home| thuEve
  tanzaku --> thuEve["LLM: night pool of 4, then bed"]
  thuEve --> reflThu[Nightly reflection]
  reflThu --> friCard["To be continued: Friday"]
```

Phone-break / reflection actions (talk, switch, migrate, start fresh, add an AI, drop, change prompt) can fire on every day and are omitted from the diagram to keep the day spine readable; see [Shared systems](#shared-systems-every-day).

---

### Nightly romance-tone classifier

At the start of `nightly_reflection`, **before** neglect is judged, `ks_classify_day_romance(day)` sends each girl you actually messaged today (her day's log, plus a rolling summary if she has one) to the model as a structured verdict: `{"tone": "romantic"|"friendly"|"tool", "reason": "..."}` (`ks_llm.classify_romance_tone`, prompt marked `ROMANCE_TONE_CLASSIFIER`). No keyword / affection-threshold fallback: if the model is down or the reply is unreadable, `tone` is `None` and she is not counted as romantic. Stored in `route["romance_tone"][gid][day]`, her memory `flags.romance_tone`, and a `romance_tone` event.

**Overlap is same-day:** `romance_overlap` is set when two or more girls are judged romantic on the **same** day (`romance_overlap_days`). Dating Yuzu on Monday and Hikari on Wednesday, never together, does not count. `double_date_unspoken` and its Respect cost key off that overlap, not off merely having two windows open. The **Both** ending is still Mio + an AI and does not require this flag.

## Open threads and unimplemented hooks (Thursday onward)

Thursday is playable (`game/thursday.rpy`, `docs/THURSDAY.md`). Friday–Sunday and the festival are not.

- **Friday–Sunday** and the festival. Thursday ends at `tbc_friday`. Hostile-event pools in `DESIGN.md` for Fri–Sat are not scheduled in code. **Kurosawa's Friday essay handover** should read `kurosawa_essay` (`self` / `askwell` / `girl_help`): she can tell when nobody was there. `askwell_available` can be cleared by a later Askwell shutdown.
- **Yuzu backup is respected on Thursday** (`apply_yuzu_hardware`: `restored_from_backup` or a real wipe). The early-week hint is `yuzu_bsod_seen`. Later Friday+ memory-loss events, if any, should keep respecting the backup.
- **Yuzu avatar-body upgrade** (`engine.rpy:35`, `flags.yuzu_avatar_choice = "none"`). Hook only; no gallery UI. Future values `"player"` / `"self"` (and objection logging) are described in `DESIGN.md`, not implemented.
- **`label ran_wednesday` can theoretically run on Thu/Fri** (`wednesday.rpy:380`) but those days have no caller.
- **Endings:** only Both has body text; only one bad-end slide exists. Yes-Machine, Migration, Respect, Human, Fail, and Mirror are scores / flags / design flavour. Mirror calibration is live; the Mirror *run* is not. Saturday follow-through for the linguistics-girl lie, `both_know`, `ran_festival_invited`, `teacher_answer`, `kurosawa_essay`, and `route["mio_notebook"]` is unwritten.
- **Mio and Daichi compare notes.** Monday's library can set `mio_told` (`truth` / `lie` / `deflect`) and `mio_daichi_consistent`. The later scene that uses them is a hook only. Wednesday still has Mio refer to the AI girl from `friend_told` alone (`ks_mio_ai_ref`).
- **Good-end variants / conversation-reflection end cards** (a summarizer that judges how you treated her, rather than "one message a day") were discussed after this commit; they are **not in the tree**.
- **Hearth / upgrade UI beyond the Wednesday menus**, streaming replies, and real-model tuning are leftover production work, not story branches.
- Push-past-a-no detection is **keyword-only** (`looks_like_pushback`). A model classifier for "pushed" is not in the game loop (warmth/kiss classification is Hikari-only).
- Copy-migration: the girl left behind in the source slot stays in her file but is no longer `active`. A later "quiet event" for her is an open design question, not a scene.

---

## Code notes (odd or easy-to-miss branches)

Not necessarily bugs — things that matter when reading the graph:

- Girl memory files (`karada_memory_<gid>.json` in the save directory) are shared across saves. `store.ks_mem_snapshot` is a plain copy of all four, kept current on every memory write and packed into each save. `config.after_load_callbacks` writes it back (and `start_interact_callbacks` does the same after rollback). Older saves without a snapshot leave the files alone.
- Monday / Tuesday / Wednesday **phone breaks cannot drop the last girl**. They are not a full loop: only **Talk** returns to the menu; change / switch / add / drop / download still end the break. "Download someone" is only live when `active` is empty, which on Monday cannot happen before the first reflection.
- Tuesday/Wednesday **afternoon and night** (and Tuesday/Wednesday morning) use `message_pool`: a shared battery, pick who each turn. Mid-day phone-break **Talk** (Mon afternoon, Mon evening glance, Tue afternoon) is still a short 3-turn chat and returns to the menu. Monday late-morning Talk-to spends from the morning pool. Walk-home texts use a pool of 2 and cost Mio affection.
- Rei's "Ask before acting" walk-home text includes a `(y/n)` in the message, but the player never answers Rei; the ordinary Mio menu follows (`tuesday.rpy:305–310`).
- Coming clean to Daichi on Tuesday is only offered on the **`friend_told == "lie"`** path, not on deflect.
- The "Allowed to push back" reply to Ran is hidden unless an *currently active* girl has family `pushback` (`tuesday.rpy:175`). A girl you already dropped doesn't unlock it.
- If you only have Yuzu active on Wednesday, the Sora/Rei/Hikari summarizer still installs in the route, but the patch-note UI is skipped.
- Hearth / upgrade are gated on `"local" in active`, not on the display name "Yuzu". A migrated-in girl in the local slot is the one you would upgrade.
- `ks_story.new_route` comments `ran_reaction` as `"boring" / "show" / "pushback" / "shrug"` and omits `"judged"` (`ks_story.py:47`), but `"judged"` is the value the harsh option actually stores.
- DESIGN.md still says "Tuesday's debug end card"; the recap is on **Wednesday's** Thursday card (`wednesday.rpy:514`).

---

*End of walkthrough for v0.4-day4. Friday is the next event day.*
