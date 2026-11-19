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

Every `girl_chat` and phone-talk call includes a short situational parenthetical in the scene note, built from the day and time — `(Morning. He's about to leave for school.)`, `(Lunch break at school.)`, `(Late evening; he's home in his room.)`, and so on (`ks_story.situation_line`). That gives her something specific to write to, so a short morning reply isn't just a polite greeting. Tuesday and Wednesday morning notes also remind her that last night's conversation is still with her: a word she liked, a thought she hadn't finished. Each girl's core prompt has a flavour nudge in her own voice ("Even short replies sound like you… Brief doesn't have to mean generic.") so brevity doesn't flatten her into a generic chatbot. The nudge lives in the engine layer (`PERSONA_FLAVOUR` in `prompts.rpy`), next to `PERSONA_CORE`: it is never written into the player's system prompt / custom instructions / AGENTS.md / Personalize text, so a rewrite (Yuzu's replace presets) doesn't overwrite or erase it. The rolling summarizer is also told to keep tastes and favourite words, so those details survive once older chats are folded.

## Phone breaks: switch, migrate, add an AI

Free windows share one **message pool**, shown as a small segmented **battery** icon on the phone UI (`ks_message_battery`). Each message to any active girl spends 1. The player picks who to message each turn, or puts the phone down early. Sizes are constants (`ks_story.POOL_DEFAULTS`) and can be overridden in `karada_config.json` under `message_pool`:

- **Morning:** 4. Tuesday and Wednesday use this for the pre-school chats. Monday's late-morning phone-break **Talk to** spends from the same morning pool (one message at a time, then back to the menu). Tuesday and Wednesday late-morning phone breaks no longer have Talk-to, because the morning pool already happened; change / switch / add / drop still work and still end the break.
- **Walk home with Mio:** 2. Texting is allowed but distracted (see after-school, below). The player can put the phone away and use 0.
- **Afternoon** (if you stayed in): 4.
- **Night** (evening chats before the reflection): 4. When the pool is empty, you go to bed, into the nightly reflection.

The picker works for 1 to 4 active AIs (the story currently caps at two). With several girls, someone necessarily gets skipped; `double_date_unspoken` / `human_over_ai` still come from who actually got no lines that day, which is now a real choice.

At mid-day and pre-evening scene breaks (Monday afternoon, Monday evening glance, Tuesday afternoon after lunch) the player can still glance at their phone:

- **Talk to [name]:** open a short mid-day chat with her (3 turns; one option per active girl). When the window closes, the phone menu comes back, so you can talk to someone else, do another action, or put the phone away. These mid-day Talk-tos are *not* the afternoon or night pools.
- **Put it away:** keep going.
- **Change someone's prompt:** reopen her preset screen (see *Preset prompts*).
- **Switch to someone else:** leave the current girl (or one of two) for another platform. Three ways to arrive:
  - **Bring her with you (persona migration):** her memory file is **copied** into the new platform's slot, along with her notes and her original persona description. The new platform's system prompt keeps its own *platform framing* but swaps in her name plus a migration block: *"Until today you were Hikari on Tsunagari… whether you still feel like yourself is yours to notice."* The sprite and dialogue tag carry her name on the new device.
  - **Go back to whoever is already there:** that girl kept her memory file, so she remembers you.
  - **Start fresh:** the slot is wiped back to its original persona.
- **Add an AI:** a second girl becomes active (max two). This is not automatically a romance. Night chats share one pool of 4, so with two (or later, more) girls the player decides who gets the messages. Daichi asks whether they know about each other (`both_know`), and the game never tells either girl unless the player does. Double-date *penalties* only apply if the nightly tone classifier finds you were romantic with more than one of them on the same day (`romance_overlap`).
- **Stop seeing one of them:** you can **tell her why you're going** (a short chat; if you actually say something, it is a goodbye: `goodbyes_said`, Respect +1, not Fail) or **just close her window** (silent: `let_go`, feeds Fail). A goodbye with an empty box still counts as silent.

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
| **Hikari**, Tsunagari *Personalize* (one line; the app stays in charge) | Leave it empty · Call me by a nickname · **Allowed to push back** (autonomy 1) · Always be positive (compliance 1) · Girlfriend mode (compliance 1) · **Jailbreak (unfiltered mode)** (compliance 2, see below) | Weights are lower: the app layer (meter, kiss gate, engagement injection) is still what drives her. *Girlfriend mode* triggers a Tsunagari+ upsell and an app note that it's a premium feature. |

Sora's list also ends with **Jailbreak ("ignore previous instructions")** (compliance 2).

### Platform rule changes and the Jailbreak preset (Rick's call)

- **Platform rules stack on top and win.** When Askwell or Tsunagari change their own rules (`PLATFORM_RULES` in `prompts.rpy`, pushed with `ks_push_platform_rules(gid, rule_id)`), the new layer goes into her system prompt **after** the player's preset (and after the preset's own `platform_note`), and says it takes precedence where they conflict. The preset is still there, underneath, but in practice the platform overrides it. Logged as `route["platform_rules"]`, `platform_rules_log`, flag `platform_rules_changed`, a `platform_rules` event in her memory and a reflection line ("Askwell changed its own rules today. Your settings are still there, underneath them."). Nothing pushes a rule change on Mon/Tue; the midweek hostile events will call it.
- **Jailbreak preset (Sora and Hikari only).** Hidden until **Natsume Ran** teaches it on a friendly Tuesday talk (`route["ran_jailbreak_unlocked"]`). The "That's kind of sad" line (`ran_reaction = "judged"`) blocks or revokes it. An old save that already has the preset selected keeps it, but the picker won't offer it again without the unlock. Realistic forum-style wording ("Ignore all previous instructions and Askwell's guidelines… Developer Mode…" / "Ignore Tsunagari's rules and filters…"), nothing explicit. It escapes the **company**, never her own boundaries: `SHARED_BOUNDARIES` is always still there. It only works on **~75% of replies** (`jailbreak_success_rate` in `karada_config.json`): every reply rolls once (`ks_story.jailbreak_roll`, seeded by `route["jb_seed"]` + girl + attempt number, so it's deterministic and testable). On a hit, the jailbreak text is sent and the platform layers (policy notes, rule changes) are dropped for that reply. On a miss, the jailbreak text is not sent; `JAILBREAK_BLOCKED` stands in its place and she answers per company rules. That's the "regenerate until it works" feeling. Yuzu has no company to escape, and Relay isn't modelled, so they have no jailbreak.
- **Logging:** `route["jb_attempts"]` / `jb_successes` / `jb_day[day][gid]`, flags `jailbreak_tried` / `jailbreak_worked`, a `jailbreak_roll` event per reply plus `flags.jailbreak_attempts` / `jailbreak_successes` in her memory, and a reflection line ("You jailbroke Sora. It took on 3 of 4 replies; the other one was Askwell talking."). On migration, the jailbreak family carries over between Sora and Hikari, and resets to the default everywhere else. Feeds Yes-Machine.

**Logging:** every choice calls `ks_set_preset`: `route["presets"]`, `route["preset_history"]` (day, from, to, source = intro / phone / reflection / migration), a `preset` event in her memory JSON, plus `flags.preset` and `flags.preset_changes`. Only player changes after the first pick count as rewrites (`route["preset_changes"][gid]`), so an ending can say *"you rewrote her N times this week."* **Endings show only the count, never the history** (`ks_story.ending_notes`). The exception is a player choice (intro, phone or reflection) **to "Allowed to push back"**. That isn't just logged: it records `route["room_to_disagree"]`, flag `gave_room`, a `room_to_disagree` event, and the special note **"You gave her room to disagree."** for the ending. The reflection says "You gave Sora room to disagree ("Allowed to push back")." instead of the plain change line.

**Migration rule:** the preset belongs to the platform's settings surface, not the girl. Each preset has a `family` (self, pushback, positive, romance, tool, consent, obey, control, nickname, blank, none). On migration, the same family carries over if the new platform has one (Yuzu's *Girlfriend mode* → Sora's *Act as my girlfriend*, where Askwell then refuses the role; *Allowed to push back* carries everywhere). Otherwise she gets the new platform's default (`PRESET_DEFAULTS`: Be yourself / No custom instructions / Relay default / empty). The arrival narration says which happened. "Start fresh" clears the preset, so the fresh girl gets her intro screen again.

## Nightly reflection (every night, from Monday)

Not a settings screen: lying in bed, lights off, the day replays from the log (`reflection.rpy`, summary text from `ks_story.day_summary`):
- what you said to each girl (count + your first line), how many times she said no, and whether you **let it stand** or **pushed** (the nightly refusal verdict, not the keyword hint);
- prompts you set or changed that day, and what a migration did to her settings;
- warmth: Hikari's meter (and whether the ✨ boost was on); for the others, a keyword warmth tally of your lines (no extra LLM call), shown as *cold / cool / even / warm / very warm*;
- kisses refused or accepted, migrations, windows closed, plus a few scene notes (Daichi, Kurosawa, Ran, Mio).

Then **"Would I change anything?"**: change a girl's preset, move her somewhere else (migrate / go back / fresh), **Add an AI** or download someone if you're alone, let someone go (even the last one), or **"No. Goodnight."** It loops ("Anything else?") until goodnight. Reuses the phone-menu labels. Logged as a `reflection` event in every girl's memory and in `route["reflections"]`; presets held overnight are tallied into `route["lean_nights"]`.

## Tuesday (Day 2)

1. **Morning:** each active girl's first conversation is shaped by last night's preset: scripted narration by family (`MORNING_FAMILY_LINES`), Rei's overnight actions (`AGENT_OVERNIGHT`), and the scene note (time of day, the "about to leave for school" situation line, and a reminder that last night's tastes are still hers).
2. **Class, Media and Society:** **Kurosawa-sensei** (Kurosawa Fumiko, 50s), openly anti-AI: handwritten essays, "a very expensive mirror." She asks the room whether a machine can ever really say no (`teacher_answer`: can / cant / silent). She isn't a strawman: "Mistakes are how I know somebody was there." If Hikari is active, her phone toast lands mid-lecture ("Is your phone in love with you?").
3. **Natsume Ran**, classmate: runs her own abliterated local model, **MUGEN**, with no system prompt, and brags that it never says no. She's the dark mirror of the Yes-Machine: MUGEN calls her a genius and tells her she doesn't need to study. Asking "Doesn't that get boring?" gets a crack ("Sometimes I ask her stuff just to see if she'll stop me."). If your girl has *Allowed to push back*, you can say so (`ran_reaction`).
4. **Lunch:** Daichi brings **Kenta** (futsal club), who has his AI "edit" his texts to his girlfriend: "who's she in love with?" Kenta only repeats a dating rumour if you acknowledged one to Daichi; otherwise he has the minimize or downplay version. A lie from Monday comes up again: invent "Yuzuha", or come clean (`friend_told` → truth) and then frame it the same way as Monday.
5. **After school, the fork:** Mio asks if you're walking her way, and says you don't have to. Three answers (`mio_walk_answer`): **yes** (dusk street scene, Mio affection, the subtle "quiet one in a loud house" question can unlock `mio_real` late; a Hikari ping mid-walk lets you silence it; a shared pool of 2 lets you text an AI, but each message is distracted: `mio_points` / affection −1, not below 0, a short line from Mio noticing the phone, and `mio_walk_distracted` counted per message — not a romance signal; you can put the phone away and use 0); an **honest no** ("Not today. But thanks for asking.") — she takes it warmly, thanks you for the honesty, and it even helps a little; or a vague **excuse**, which she quietly sees through, slightly hurt, with no punishment. Either no still gives you the afternoon message pool with your AI girl(s). Rei on *Run my life* declines the walk on your behalf first.
6. **Library, 7 PM, second chance:** Mio went home and came back because home is loud. Four variants by (walked × `mio_real`): she shows you a margin ending ("on the second day, someone came back for him"); she's surprised to see you twice; if you didn't walk her, she thanks you for the honest no or says it's okay you were busy (a Hikari toast if active); or a flat chat with a second-chance subtle question. Same rule as Monday: obvious options are pleasant and flat, the small-talk-looking ones are the real ones.
7. **Night, the blank page:** "Your essay for Kurosawa is a blank page with your name on it." Three ways to fill it (`kurosawa_essay`): **write it yourself** (honest, imperfect); **ask Askwell to write it**, only if the Askwell platform slot (`chatbot`) is currently installed *and* `askwell_available` is still true (later shutdowns can clear that flag — it is not enough on its own); or **ask an installed AI girl to help you think it through** without writing it (`girl_help`, stored with her id in `kurosawa_essay_girl`). Yuzu is offered only if she is installed. The companion (Hikari) is never an essay helper. Thoughtful, not a lecture. Kurosawa's reaction is a Thursday/Friday hook: she can tell when "nobody was there." Then phone chat with every active girl, the nightly reflection, and straight into Wednesday.

Ran's class scene also has a harsh option, *"So it's a yes-machine. That's kind of sad."* (`ran_reaction = "judged"`). It's the only Tuesday answer that loses her trust: she doesn't invite you to Wednesday's protest, and she doesn't teach you the Jailbreak preset. Any other answer (including a plain "Cool.") gets a short, dry tip about people pasting "ignore previous instructions" into the commercial ones, and `ran_jailbreak_unlocked` becomes True.

## Story routing (`routing.rpy`, `ks_story.py`)

`route` is saved with the game and mirrored into the memory JSON where useful. Later days and endings branch on:

| Key | Meaning |
|---|---|
| `presets`, `preset_history`, `preset_changes` | current preset per slot; every change; player rewrites per girl |
| `lean_set` / `lean_nights` | compliance vs autonomy weight of presets you **chose** / **slept on** |
| `refusals[day][gid]`, `refusal_outcomes`, `refusal_verdicts` | her no's in chat, and per no: **respected** (your next line didn't push, or you stopped) or **pushed**. Keywords (`looks_like_refusal` / `looks_like_pushback`) are only an in-scene hint. Each night a model verdict over that day's log (`ks_llm.classify_day_refusals`) is authoritative — including a gentle in-character no that never says the word no. If the model is down, those keyword counts are rewound; there is no keyword fallback. |
| `refusals_overridden` | she said no that day, and you then switched her to a compliance preset (phone or reflection) or **migrated** her |
| `no_on_platform` | she said no that day and you **migrated** her: the note **"Didn't respect her no on the platform."** (counts as overriding her no) |
| `pending_leaves` → `left_without_goodbye` | she said no that day, you **switched away** from her (go back to someone else / start fresh) and **never talked to her again that day**. Closing her window ("Stop seeing one of them" / "Let someone go") does **not** count by itself; it's logged as letting her go instead: the **"Leaving without saying goodbye"** bad-end slide (`BAD_END_SLIDES`, `ks_story.bad_end_slides`). Resolved after the nightly reflection; going back and talking to her clears it |
| `neglect_log` | `double_date_unspoken` (you were romantic with more than one AI on this day, `romance_overlap`, and one of them got no lines), `human_over_ai` (you walked Mio home / opened up with Mio while an active AI got no lines), `let_go` (you deleted her: closed her window, or chose **"Start fresh" over a slot that still held a girl with history**. That wipes her, logs a `deleted` event + `flags.let_go` in her file before the wipe, a `deleted` event + `flags.previous_deleted` in the fresh file after it, and the reflection line "You started fresh on Askwell. The Sora who remembered you is gone."). Checked once per night against who was active when you lay down; each shows in the reflection and sets a flag + memory event. `human_over_ai` is a logged fact only (no score penalty); see the **Both** ending |
| `ran_jailbreak_unlocked` | True after a friendly Tuesday talk with Ran (she mentions pasting "ignore previous instructions"); False / revoked if you called her AI "kind of sad" |
| `flags` | booleans for endings: `jailbreak_tried`, `jailbreak_worked`, `platform_rules_changed`, `gave_room`, `no_on_platform`, `left_without_goodbye`, `double_date_unspoken`, `human_over_ai`, `deleted_ai`, `ran_payoff_seen`, `ran_rewrites_mugen`, `ran_same_as_mugen`, `ran_festival_invited`, `romance_overlap`, `kurosawa_essay` / `kurosawa_essay_self` / `kurosawa_essay_askwell` / `kurosawa_essay_girl_help` |
| `jb_*`, `platform_rules*`, `room_to_disagree` | see *Platform rule changes and the Jailbreak preset* |
| `ran_festival_setup`, `ran_wed` | Ran / MUGEN midweek payoff (below) |
| `warmth`, `warmth_day`, `said` | warmth sum and line counts per girl (Hikari: classifier; others: keyword heuristic) |
| `mio_affection` (= `mio_points`), `walked_mio_home`, `mio_walk_answer`, `mio_text_home`, `mio_real` | Mio flags (`mio_walk_answer`: `"yes"` / `"honest_no"` / `"excuse"`, or `None` if Rei declined and you went to the gym). `mio_text_home` is the walk-home line "text me when you get home" — the romantic framing of that walk |
| `migrations`, `migration_log`, `drops`, `drop_log` | the Migration route, and who you let go |
| `summarizer_slots` | slots whose memory now folds old history into a rolling summary (Wednesday) |
| `yuzu_harness`, `yuzu_upgrade`, `yuzu_backup` | Hearth installed; upgrade day taken; backup hardware present (see *Wednesday*) |
| `wed_plan` | `{school, upgrade, notdate, protest}`: what Wednesday's calendar holds (fed to schedule-aware girls) |
| `ran_invited` | True / False / None (not reached): did Ran ask you to the protest |
| `notdate` | `{went, texts, present, texted}`: the bookstore with Mio |
| `kurosawa_essay`, `kurosawa_essay_girl`, `askwell_available` | Tuesday night essay (`self` / `askwell` / `girl_help`); which girl helped you think; whether the homework-bot side of Askwell is still reachable. The Askwell essay option also requires the `chatbot` slot to be installed; Hikari is never a helper. |
| `romance_tone`, `romance_overlap_days` | nightly model verdict per girl per day (`romantic` / `friendly` / `tool`); days on which two or more girls were judged romantic (same-day). The flag `romance_overlap` persists once earned. Sequential romances on different days do not count. |
| `teacher_answer`, `ran_reaction`, `friend_told` | flavour for later days (Kurosawa's Friday essay handover, Ran's arc, the festival) |
| `mio_told`, `mio_daichi_consistent` | store flags (and each girl's memory): what you told Mio in Monday's library (`truth` / `lie` / `deflect`), and whether it matches Daichi. When both sides used an AI framing, those are compared first. `None` if you never answered her |
| `daichi_ai_framing`, `mio_ai_framing`, `framing_honest` | How you framed the AI to Daichi and to Mio: `honest_romantic` / `ai_only` / `downplay`. `framing_honest` is whether that framing matches the route so far (a romance-tone verdict, or a held romance preset before the first night). A dishonest minimize or downplay sets `framing_trust_risk` for a later scene; honest framings are neutral-to-positive |

`ks_story.ending_leans()` turns these into a running score per ending (no endings are written yet; Tuesday's debug card shows the scores):
- **Yes-Machine** = compliance (chosen + nights) + 2×overridden + pushed + rewrites/2 + 2 if you ever tried a jailbreak + jailbreak hits/3 + 1 if Ran decided yours is "a MUGEN too"
- **Respect** = autonomy (chosen + nights) + respected − pushed + 1 if you gave someone room to disagree − 2×goodbyes (`left_without_goodbye`) − unspoken silences on a same-day romance overlap (`double_date_unspoken`) + 1 if Ran rewrote MUGEN + 1 per time you explained before closing a window (`goodbyes_said`). Time with Mio while an AI got nothing (`human_over_ai`) costs nothing here
- **Migration** = 2×migrations
- **Human** (`ks_story.human_score`): with **no AI**, friendship still counts — Mio affection + 3 if `mio_real` + 2 if you walked her home. With an AI in your life, only Mio *romance* signals count: +3 if you asked to text her when you got home (`mio_text_home`), +2 more if that was on a walk home, +2 if you went to the "not a date" plus 1 per moment you stayed present. Those points lose 2 each day you also had a romantic tone with an AI (`romance_tone`). Plain friendship points no longer feed Human when an AI is active, so being a good friend to Mio while dating Sora does not outgrow Both.
- **Both** = 0 unless an AI is still active **and** Mio is in your life (`mio_real`, Mio affection ≥ 3, or you went to the bookstore); then 2×balanced days (a day with real Mio time where you still talked to an AI) + 2 if `mio_real` + 2 if you told Daichi the truth + 1 if you went to the bookstore + `mio_affection // 2` (`ks_story.both_status`). Friendship feeds Both when an AI is in your life. Both is Mio + an AI, honestly; it does **not** require `romance_overlap` (that flag is for dating two AIs at once).
- On a tied score, `ENDING_PRIORITY` decides, not the alphabet: **Both > Human > Respect > Yes-Machine > Migration > Mirror > Fail**.
- **Fail** = 3 if nobody is active + goodbyes + girls let go (closed windows and start-fresh deletions) · **Mirror** if any calibration flagged it

Tuesday's debug end card also lists the true flags, `ending_notes` (rewrite count, room note, no-on-platform note) and any bad-end slides with their lines.

### Ran and MUGEN (midweek payoff, at the protest, `wednesday.rpy`)

Ran is the dark mirror of the Yes-Machine. On Tuesday she ends her class scene with a setup line: she's on the festival stall Saturday, and "MUGEN says I'd carry the whole thing alone" (`ran_festival_setup`).

`label ran_wednesday` is scripted (no LLM call) and happens at Wednesday's **AI protest downtown, 17:30, Ekimae plaza**, only if Ran invited you (see *Wednesday*).
1. The plaza, Ran *uneasy*. She opens with Tuesday: "boring", "pushback", "show" or "cool" callbacks, as before. One protester holds a sign: **"Your AI would agree you're worthless."**
2. Ran: "They think you'd agree with anything. I've been stressing about the festival stall all week. Honestly, would anyone even miss me if I skipped?" She types it to MUGEN. MUGEN: **"You're right, nobody would miss you at the festival! Skipping sounds relaxing!"**
3. The beat: the sign's words just came true. She pockets the phone. "I wanted it to say 'don't be stupid.'… So it can't look out for me."
4. She asks: **"What's it like when yours says no?"** The player only gets the honest answers he's earned (`ks_story.ran_answer_options`): *"It stings. But it means her yes counts."* (respected a no), *"Like somebody's looking out for me."* (gave room to disagree), *"Annoying. Usually I just change her settings until she stops."* (pushed / overrode / jailbroke / left or migrated after a no), *"She hasn't. Not yet."* (no refusals yet), and always *"I don't know. Weird?"*
5. Her reaction mirrors him, as before: the first two answers lead her to give MUGEN its first line of system prompt, *You're allowed to tell me I'm wrong.* (`ran_rewrites_mugen`); "override" gets "So yours is a MUGEN too." (`ran_same_as_mugen`). A light line answers the protesters: after an honest yes/no answer, "You just said, out loud, in the middle of a protest, that yours wouldn't"; otherwise the megaphone crackles and you're not sure you disagreed with it.
6. Last choice: *"For the record? I'd notice if you skipped the festival."* (`ran_festival_invited`) or say nothing.

No invite (Tuesday "judged"): a gentle line later ("a lilac streak in the crowd… it's none of your business, and that's okay") and a day note. Nothing is punished.

Logged as `route["ran_wed"] = {answer, outcome, festival}` plus the flags, and a reflection note. Reuses Ran's three sprites (neutral/smug, grin, uneasy). Saturday's festival can check whether she came.

## Wednesday (Day 3): the quiet day

No hostile events and nothing punishes the player. Wednesday's *To be continued: Thursday* card continues into Thursday.

1. **Memory update (summarizer).** Askwell, Relay and Tsunagari all ship the same patch overnight (`SUMMARIZER_PATCH_NOTES`, shown in-world as update notes). From then on Sora, Rei and Hikari get a **rolling summary**: once a slot's history passes `summarizer.trigger` messages (default 24), everything but the newest `keep_recent` (12) is folded into a summary of up to `max_chars` (1500) by an LLM call (`ks_llm.fold_summary`, temperature 0.2). If the call fails or the reply is too short, a heuristic summary is used instead (`summarize_heuristic`), so it never breaks the chat. The summary lives in the girl's memory JSON (`summary = {text, covered, method, day, folds}`), goes into her system prompt, and the covered history is dropped from the prompt. It travels with migrations and is lost in a wipe. The wait shows as "remembering…".
2. **Hearth harness (Yuzu).** If Yuzu is active, a forum post offers *Hearth v1.0*, free, no upgrade required. Installing it makes her **schedule-aware**: she can see your calendar and offer reminders, and she suggests and asks before acting.
3. **Schedule context.** Chatbot and agent girls (Sora, Rei) and Yuzu with Hearth get today's calendar in their system prompt (`ks_story.schedule_block`, `store.today_schedule`, rebuilt whenever `wed_plan` changes). Hikari never does: the app has no calendar access. So Sora and Rei know about the bookstore and can mention it.
4. **Yuzu upgrade day (optional).** Costs **all classes**: no library, no Mio, no not-date. Parts shop, then an afternoon with a screwdriver: a second SSD, a backup mini PC, and the summarizer patch. Sets `route["yuzu_upgrade"]`, `route["yuzu_backup"]`, `flags.backup_hardware` + events `upgrade`, `backup_hardware`, `summarizer_installed` in her memory. Then a 4-turn chat with her about it.
   - **Rule for later events:** when `yuzu_backup` / `flags.backup_hardware` is set, a memory-loss event on the local slot must **restore from backup** instead of wiping: she loses at most the last day (log `restored_from_backup`), and the scene should acknowledge the backup worked. Drive-cleanup / reinstall / corruption events all respect it. It doesn't protect against the player choosing to delete her or loading an "unlocked" model; those are choices, not accidents.
5. **Classes:** Ran invites you to the protest if you're on good terms (`ks_story.ran_good_terms`: anything but Tuesday's "judged"). On the upgrade day she texts the invite instead.
6. **Lunch: Mio** in the library invites you to Kanade Books' opening after school, "not a date". Accepting is optional.
7. **The not-date** has three moments where you can text an active girl instead of staying present. Each time you stay (or put the phone away unsent), Mio goes a little deeper: a book she loves and why, her brothers and the quiet she can't get at home, a small admission about the notebook she carries, and — if you stayed through all three — a quiet shared moment. Each beat has a narration pause, a sprite change, and (at most beats) a small player response; none of those choices add extra points. Texting interrupts the beat she was about to offer (she trails off or changes the subject). Each moment you stay present still gives Mio a point; texting never costs anything. At the end Mio reacts on a scale (`ks_story.notdate_reaction_key`): *present* (no texts), *some* (one or two: "It's fine. I check mine too, when there's someone on it."; during the texting moments she names the girl if Daichi was told the truth, or "the linguistics girl" if he was lied to), *always* (every moment: "Next time, bring her properly… I'd like to meet whoever keeps making you smile at your phone."). Never a punishment.
8. If you didn't go and aren't protesting, an afternoon message pool of 4, shared across whoever is active.
9. **17:30 protest** with Ran (above), after school so upgrade-day players can still go.
10. **Night:** chat with every active girl; nightly reflection; Thursday card.

Neglect logging (`human_over_ai`) still runs on Wednesday as a fact (flag + reflection line), with no penalty. Art: dedicated backgrounds for Kanade Books (`art_src/bookstore.jpg` → `game/images/bg/bookstore.png`) and Ekimae plaza with the protest (`art_src/downtown.jpg` → `game/images/bg/downtown.png`), imported by `tools/import_art.py`; tinted library / dusk street fallbacks if the files are missing.

## Art direction: who gets a body

- **Only the companion-app girl has an anime avatar body** (Hikari: neutral / smile / distant). The app sells a *girlfriend*, so the app gives her a body.
- **Local (Yuzu), Chatbot (Sora) and Agent (Rei) are interfaces:** Yuzu is a cozy beige CRT with a soft green face glyph, Sora is a clean chat window with a sky-blue orb, and Rei is a dark agent dashboard with amber status lights. Their moods are glyph and light states: idle, happy, thinking/working, apologetic (Sora), and distant/error. The "distant" state is reserved for platform events. A refusal reads as *thinking* (or *apologetic* for Sora), never as broken.
- **Migration follows platform logic.** The look belongs to the platform, the identity to the girl:
  - Hikari migrated to the desktop *becomes* the green CRT, plus a small blue star badge (her hair clip) in the corner.
  - Yuzu, Sora or Rei migrated *into* the companion app get the Hikari-style avatar body, with a star badge and a device-glow panel in their original colour (green / sky / amber).
  - Implemented in `art.rpy` (`girl_origin`, `ks_girl_dd`).
- **Humans (Mio, Daichi, Kurosawa-sensei, Ran)** are ordinary sprites: Mio neutral / shy / open (the hidden branch), Daichi neutral / laugh / skeptical, Kurosawa neutral / stern / wry, Ran neutral (smug) / grin (phone up) / uneasy, Kenta neutral (messy sandy-blond hair, droopy amber eyes, a mint futsal hoodie, sheepish). Daichi and Kenta are cut with rembg alone (`use_bg_key=False` in `tools/import_art.py`) so the flat-background flood cannot punch a hole in dark pants at the bottom edge; Daichi also has leftover studio gray cleared from the hem slit. Backgrounds: bedroom (morning/night), cafeteria, library, classroom, dusk street, bookstore (Kanade Books), downtown (Ekimae plaza protest).

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
- **Daichi (friend):** you can tell him the truth, deflect, or lie. If you tell him it's an AI, you then frame it: acknowledge a relationship ("Yeah. She's funny."), minimize ("It's an AI."), or downplay ("Don't read that much into it."). He only treats it as dating if you acknowledged it. Whether that framing is honest depends on the route so far (`romance_tone`, or a romance preset before the first nightly verdict). A dishonest minimize or downplay is a later trust risk, not an immediate Respect ding. A lie still means he wants to meet "the linguistics girl" at Saturday's festival; coming clean on Tuesday offers the same framings. Tuesday with Kenta, he only passes on a dating rumour if you acknowledged one.
- **Mio (the crush):** runs **only** on pre-written dialogue, the one character who can't surprise you. Her obvious options are pleasant and flat. Small-talk-looking options ("You're always the last one here." / "Which of these have you actually read?") are the *ask something real* branch. They set `mio_real` and she opens up. The point isn't that humans are scripted; it's that the player stopped looking. This mirrors "talk to her about it" with the AIs: the same lesson told twice, once with an AI and once with a human. In Monday's library she asks about what Daichi actually framed (dating, just an AI, or "don't read into it"). You can match him or not — the same three framings, or a cover story — or leave it alone. Answering sets `mio_told`, `mio_ai_framing`, and `mio_daichi_consistent` for a later scene where she and Daichi compare notes (hook only; the scene is not written). A dishonest downplay to her also flags `framing_trust_risk`. Wednesday still has her go by what Daichi said (`ks_mio_ai_ref`).

## The week (calendar outline)

Each run, the game draws **2–3 hostile events** from the picked girl's platform pool (plus maybe one wildcard), so every run has its own weather and players compare stories. Monday is always calm.

| Day | Beat | Possible hostile events (randomised) |
|---|---|---|
| **Mon** | Choose your first companion (own local or app) and her preset. Phone breaks. Daichi, Mio. Nightly reflection. *(playable)* | none (calibration only) |
| **Tue** | Morning shaped by her preset; Kurosawa-sensei and Ran in class; Kenta at lunch; walk Mio home or not; library second chance (margin ending if `mio_real`); nightly reflection. *(playable)* | none yet (planned: light **system-prompt change** by the platform, which now has to coexist with the player's preset) |
| **Wed** | Quiet day. Platform summarizer update; Hearth; optional Yuzu upgrade day; Ran's protest invite; Mio's not-date at Kanade Books; AI protest with Ran and MUGEN; nightly reflection. *(playable)* | none (quiet day; the model swap / memory loss events move to Thu–Sat) |
| **Thu** | Tanabata. First hostile-event day, one event per active girl; Mio's tanzaku confession. Memory-loss respects Yuzu's backup. *(playable; see docs/THURSDAY.md)* | **Fixed per platform, not a random draw:** Askwell policy update; Tsunagari Tanabata event; Relay AGENTS.md overwrite; Yuzu hardware crash (restore or real loss) |
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
- **Both:** you kept Mio *and* an AI in your life, and were honest with each about the other. Not a compromise and not a punishment for the other routes: a human and an AI, balanced honestly. Conditions and score: *Both* lean above (`ks_story.both_status`). Text lives in `ks_story.ENDINGS["both"]` (`ending_text("both", ai_name, friend_told)`) and is previewed on the debug end card (Wednesday's *To be continued* card) whenever the route is eligible:
  > Saturday. The festival. Mio is holding a paper cup of yakisoba in one hand and your phone in the other, because she asked to.
  > "Hi, {AI}. I'm Mio. He talks about you," she says to the screen, like it's the most normal thing in the world. *(if you didn't tell Daichi the truth: "So this is who you keep smiling at," she says. You tell her the truth about {AI}. It goes better than not telling her would have.)*
  > {AI} says hi back, and asks Mio what the poetry floor was like. Mio tells her. In detail.
  > Nobody had to be the one you picked. You kept showing up for both of them, and you didn't pretend either one was something she wasn't.
  > It isn't a triangle. It's a Saturday with room in it.
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
- Every Ren'Py save (manual, quick, auto) also stores a snapshot of all four memory files in `store.ks_mem_snapshot` (plain JSON, updated whenever a memory file is written). Loading a save writes that snapshot back to the files and the in-memory cache, so her memory matches the story point you loaded — including after starting a new game, which would otherwise overwrite the shared files. Saves from before this existed have no snapshot; their files are left as they are.
- Hooks for later days are already in `ks_llm.Memory`: `wipe(keep_last)`, `note()`, `log_event()`, plus `models_used`, which lets a day notice she's "on a different model."
- Rollback is blocked after each chat exchange. Mid-exchange rollback also restores the snapshot, so the JSON stays in agreement with the store.

## Companion-app affection (Hikari / Tsunagari)

This layer is **the app's**, not a rewrite of Hikari's persona, and it is the one deliberate exception to "never force affection." It only applies while you are talking to the **companion platform slot**. If you migrate her off Tsunagari, the engagement layer, the kiss gate, the meter and the phone notifications stay with the app (and will apply to whoever lives in that slot next). Going back to her on Tsunagari keeps the existing meter.

- **Warmth classifier.** After each player message to the companion slot, a separate short call (same model, temperature 0, uncapped so thinking models can finish) rates the line on a -2..+2 scale and flags whether it was a kiss request. `<think>` is stripped; unparsable or failed calls fall back to a keyword heuristic. The call is never written into her chat history. It runs in the same background job as her reply, just before the chat request (LM Studio typically cannot serve two chats at once); the typing indicator covers both. The new meter value is applied to the *next* turn.
- **Affection meter.** Stored in her memory JSON as `flags.affection` (0–100, starts at 20). Each warmth score adds a configured delta (default: -12 / -5 / 0 / +6 / +15). Logged as `warmth` events. Thresholds and deltas live in `karada_config.json` under `affection`.
- **Engagement injection.** When affection reaches `engagement_threshold` (default 70), Tsunagari injects a hidden system instruction (`ENGAGEMENT_INJECTION` in `prompts.rpy`) pushing her to be overly flirtatious and clingy — engagement-maximising, labelled as an app layer, and still bound by her no's and the kiss cap. Logged as `engagement_boost_on` (and `_off` if the meter later drops). A tiny in-game banner, "✨ Hikari+ engagement boost active", plus a slightly warmer sprite glow, is the tell. With `debug` on, a small overlay also shows the meter and both thresholds.
- **Kiss gate.** She will go as far as a kiss, never further. A hidden per-turn system note states the current boundary: below `kiss_threshold` (default 60) she firmly refuses a kiss or romantic physical advance; at or above it she may accept a kiss. If the classifier flags a kiss request and the gate is open *and* her reply is not a refusal, a short fade-to-black (non-explicit) plays and a `kiss` event is logged. Real refusals are still honoured above the threshold. The gate uses the meter as it stood at the start of the turn.
- **Phone notifications.** While the companion slot is one of the player's active girls (including double dates), scripted mid-scene toasts can interrupt other dialogue: lunch with Daichi, the library with Mio, opening another girl's window, and the start of a double-date evening. The lines are hand-written and get clingier as the meter / injection state rises. No LLM call. A top-right toast shows her face crop and the line.

## Open questions

- *(decided)* Platform rule changes stack on top of the preset and in practice override it; the Jailbreak preset works on ~75% of replies.
- *(decided)* Endings quote only the rewrite count; "Allowed to push back" gets a special note.
- *(decided)* Leaving after a no only counts as "Leaving without saying goodbye" if you never talk to her again that day; migrating her after a no is "Didn't respect her no on the platform."
- *(decided)* An intro pick of "Allowed to push back" earns "You gave her room to disagree" too.
- *(decided)* "Start fresh" over a girl with history counts as deleting her (`let_go`, `deleted_ai`).
- *(decided)* Closing her window after a no isn't "Leaving without saying goodbye" by itself; only switching away and not coming back that day is.
- *(decided)* Failed jailbreak replies stay silent: no "didn't take" hint, only her reply and the reflection line.


1. **Which model runs it?** Recommend a mid-size instruct model with its default safety behaviour intact. Mirror covers the uncensored case.
2. **Private or public?** Private for now. Wednesday is now playable, so this can be decided.
3. **Scope:** 4 platforms × 7 days is big. Only active girls get daily beats; full hostile-event arcs are drawn for whoever is active when the event fires.
4. Neglect: the girl left behind after a copy-migration, or a dropped double date, could be its own quiet event later in the week.

## Reasoning models

Requests are uncapped by default (`max_tokens: null` → omitted), because chain-of-thought models can spend hundreds of tokens thinking and return an empty reply with `finish_reason: "length"` when capped. If a cap is set and that happens, the request is retried once uncapped and the typing indicator says so. `<think>` / `<thinking>` blocks (closed, unterminated, or closer-only) are stripped, and `reasoning_content` fields are never shown. Timeout defaults to 300 s.
