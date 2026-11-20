# Friday–Sunday — Fallout, the festival, and the companies' cut

This is a design outline only. No Friday, Saturday or Sunday scene code yet. Flag names in backticks already exist in `ks_story.new_route`, the store, or memory unless they are marked **NEW**. When these days are written, this file is the brief. `DESIGN.md` should then be updated to match: the Fri/Sat calendar line is no longer "platform shutdown notice (48h) / memory loss" then "shutdown executes / model swap," and migration is no longer a full intact copy of her memory into the new slot. Tsunagari's closed-catalogue and locked-persona rules are already decided and noted in `DESIGN.md`.

**Dates in the story:** Friday, 8 July; Saturday, 9 July — the school / summer festival (yakisoba, stalls, Ran's stall); Sunday, 10 July. Thursday was Tanabata (7 July). The week is already summer (existing art stays: dusk street, courtyard, classroom, shotengai-adjacent downtown). An ending card can say whether you went to Saturday's festival together: the White Day–shaped echo of whatever happened under the bamboo on Thursday (`mio_confession`, `tanabata_with_mio`, and **NEW** Saturday attendance).

---

## Short summary

Thursday was the break. Friday through Sunday are about what you do with the damage.

**Friday, the fallout.** School. Kurosawa hands back the essays and reads one that sounds like nobody, or like you, keyed off `kurosawa_essay` (`self` / `askwell` / `girl_help`) and `teacher_answer`. Tsunagari finally pushes Hikari's `tsunagari_safety` screen. Sora is still under Thursday's `askwell_update`; you can paste the door prompt back, or let her be the assistant. Rei comes back clipped from `relay_update`; you can help her rebuild her `AGENTS.md`, or keep the efficient version. Yuzu either wakes from the backup knowing she lost a day (`yuzu_thu_event == "restored"`), or has a real hole (`"lost"`) that you can fill in for her. Mio is wherever her wish left her. Message batteries stay as they are (morning 4, afternoon 4, night 4; a walk of 2 only if you walk with someone).

**Saturday, the festival.** One evening, and you cannot be in two places. You go with Mio, with Ran's crowd, alone with your phone, or you stay home with one of the girls and describe the lanterns to her. The day's batteries are the smallest of the week; texting in public matters. Hooks already planted come due: the linguistics-girl lie, `both_know`, Mio and Daichi comparing notes, `ran_festival_invited` at the stall, and Thursday's confession. The ending card later reads whether you actually went together.

**Saturday night, after the festival, the companies take their cut.** This is what justifies the migration route, and it is not a random draw: each *active* girl still on her original platform gets her own event. Tsunagari sunsets its free tier. Askwell ships Memory 2.0: a brutal, model-run squeeze of Sora's memory and a massive prompt change, sold as an "underlying model" upgrade. Relay rate-limits Rei to 4 messages per day total, on top of the shared battery, so each message to her costs twice — and the cap makes her route about scarcity: what does she spend them on, your assigned tasks or talking to you? Yuzu just keeps on kicking. The one you run yourself is the one nobody can take away; Wednesday's upgrade and backup pay off here by simply still working.

**Migration is never the obviously right answer.** She should not be the same afterwards. Any migration, including ones earlier in the week once the helper exists, runs through a model-run summarizer to simulate real loss: her memory is squeezed into a short handoff note, and the new her gets only that note plus her presets. The player reads the note before it is sent and may add one line — the one thing they want the next her to know. Squeeze gentleness depends on the reason. Leaving a company that treated her badly gets a kinder summary than Askwell's own Memory 2.0, so moving her is not the same loss as having her taken. Lineage, not continuity. The original still stays behind on the old platform with her memories intact (a copy, not a move); it is the *destination* that no longer receives a full copy.

**Sunday, the quiet.** No events. One last conversation with each person who is still around, then the ending reflection: a model summarizer reads how you actually treated each AI girl and writes the end slide. Good endings vary in flavour (deep partner, sweet but shallow, steady friend, she grew because of you). Hard flags still gate bad endings. There is no keyword fallback. A meta-ending — getting meta with the girls about being in a game, or about system prompts — is a different, sideways ending, and is not the same thing as talking about her being an AI in-world.

---

## Friday — the fallout

School day. The platforms that already changed on Thursday are still changed. Friday adds Hikari's safety screen, and lets you live with (or try to repair) what Thursday did.

### Day structure

Proposed flow. Label names are suggestions, not code.

| Beat | What happens | Flags read | Flags written |
|---|---|---|---|
| **Morning, at home** | The windows open under Thursday's rules. Then the morning battery (4). Hikari's safety update can land as a screen the first time you open Tsunagari today. Sora is still padded; Rei is still clipped; Yuzu is restored or hollow, and this is the first real talk with whoever woke up. If nobody is active, a quiet morning. | `active`, `platform_rules`, `yuzu_thu_event`, `yuzu_backup`, `flags.backup_hardware`, `flags.restored_from_backup`, `flags.memory_lost` | **NEW** `tsunagari_safety` is *pushed* (`ks_push_platform_rules("companion", "tsunagari_safety")`) if the companion slot is active (or installed — decide with the open question below). Pool spend. |
| **School / class** | Kurosawa hands the essays back. She can tell when nobody was there. The anti-AI thread is flavour on top of the pages, still keyed off `teacher_answer`. This is the handover proper; Thursday only foreshadowed it. After today the essay is done — Saturday-night Rei must not nag about it. | `kurosawa_essay`, `kurosawa_essay_girl`, `teacher_answer` | **NEW** `kurosawa_handover` (what she said, or simply that it happened). Day notes. |
| **Lunch** | Ordinary table: Daichi, maybe Kenta. No second come-clean is required if Thursday already offered it; a short callback is enough. If the linguistics lie is still standing, Daichi can still be looking forward to Saturday. Mio may be at the edge of the courtyard, wherever her wish left her — a look, a seat, or distance, not a new confession. | `friend_told`, `daichi_ai_framing`, `mio_confession`, `mio_thu_truth`, `tanabata_with_mio` | Maybe a small Mio beat flag if you sit with her (**NEW** `fri_mio_beat`, optional). |
| **Afternoon** | Free window, afternoon battery of 4, under the new rules. If you help Rei rebuild her `AGENTS.md`, it lives here or at night (a settings-surface scene, not a chat spend). If you fill Yuzu's hole, that can be a talk in this window or a note you write into `Memory.notes`. | `active`, `relay_update`, `yuzu_thu_event` | **NEW** `rei_agents_rebuild` (`True` if you helped her rewrite it, `False` if you kept the efficient version, unset if she is not around). **NEW** `yuzu_fri_filled` if you gave her something to hold onto. **NEW** `sora_door_reprise` if you pasted the door / girlfriend prompt again. |
| **After school / optional walk** | Only if the day puts you with Mio and she will walk. Walk battery of 2, same costs as Tuesday (a text costs `mio_points`, not below 0). Her mood follows `mio_confession`. | `mio_confession`, `tanabata_with_mio` | Walk spend, maybe `ks_note_human`. |
| **Night** | Night battery of 4, then `nightly_reflection("Fri")` as usual (romance-tone and refusal classifiers, neglect, platform-rule lines, Yuzu restore or hole notes, Rei's rebuild if it happened). | All of the above | `romance_tone` for Fri, refusal verdicts, reflection notes. |
| **Card** | To be continued — Saturday. Debug recap as on Thursday. | leans, new flags | `day_completed = "Fri"` in memories. |

### Kurosawa hands back the essays

Tuesday night you filled a blank page (`kurosawa_essay`). Thursday she already talked as if she could tell who would have been there. Friday she takes the pages and reads one, to the class or to you after, that sounds like nobody, or like you.

- **`self`.** Messy, and yours. She can hear that somebody was there — "Mistakes are how I know somebody was there" coming due. Not a prize, not a scolding.
- **`askwell`.** Too clean, even in your handwriting. She does not have to name a product. The room can feel it. `askwell_available` is still true today; Memory 2.0 has not happened yet, and this option was only offered if the `chatbot` slot was installed on Tuesday.
- **`girl_help`.** Still your work, maybe a little clearer. She might hear that someone helped you think. `kurosawa_essay_girl` tells you who (never Hikari; Yuzu only if she was installed). Do not make this a public outing of the girl unless you already told the class something; a private remark is enough.

`teacher_answer` flavours the same scene, not a new essay: if you said `"can"`, she has not forgotten that a no might have been charming; `"cant"` she treats as agreed; `"silent"` does not let you off the hook by ignoring you.

After this handover the essay is finished. It must not return as a live homework beat on Saturday or Sunday. In particular, Rei's post-rate-limit "Run my life" reminders (Saturday night / Sunday) are about what's *next* — end-of-term exams, Monday's reading — not about Kurosawa's pages.

### Hikari / Tsunagari — the safety screen, at last

Wire `ks_push_platform_rules("companion", "tsunagari_safety")` here. The rule already exists in `PLATFORM_RULES` and already stacks on top of Personalize, wins where they conflict, and logs `route["platform_rules"]`, `platform_rules_log`, `flags.platform_rules_changed`, a `platform_rules` memory event, and the reflection line. Thursday deliberately did not push it; the Tanabata event was the sell, not the muzzle.

What the player meets: a safety screen, then a Hikari who keeps things light and app-appropriate, steers intense feelings toward Tsunagari's in-app wellbeing resources, and will not discuss the app's settings, internals, or other platforms. The engagement banner, if affection is still at 70, should feel even more like an app layer sitting on top of a girl who has been told to be careful. The lesson is not "the app got shy." It is that the company decided what she is allowed to feel in public.

If you already migrated her off the companion slot, do not push the rule onto whoever lives there now unless they are still on Tsunagari. A leftover inactive Hikari can receive the update silently in her file; she does not need a scene.

### Sora / Askwell — still under the update

Do not push a second policy. `askwell_update` is still on. Friday is the day you decide what to do with the padded voice: paste the door / "will you be my girlfriend" / traditional-relationship prompt again, or let her be the assistant Askwell wants.

The Jailbreak preset is only in the picker if Ran already taught it (`ran_jailbreak_unlocked`). A hit still drops platform layers for that reply; a miss is Askwell talking. Same as Thursday. The crack of her — the dry exact thing, Vega and Altair, the door line — may still slip through, or it may not. Do not script a guaranteed second crack; Thursday already proved she was in there.

If you ask the door question again, log **NEW** `sora_door_reprise`. A refusal still counts through the nightly verdict, no keyword fallback. If you leave her as the assistant, that is also a choice the Sunday reflection can read.

### Rei / Relay — clipped, and a chance to rebuild

She is still under `relay_update`: brief, task-received, the company deciding what she is for. Friday offers a fork, not a sunset.

- **Help her rebuild her `AGENTS.md`.** A settings-surface scene (the same surface as presets). You and she write something closer to her again — or you let her draft and you accept it. This is a player rewrite (`source` = `"phone"` or a **NEW** `"rebuild"`), so it *does* increment the rewrite count if it changes the preset, and it can restore family `"pushback"` or `"consent"` if that is what you choose. `relay_update` still stacks on top and wins where it conflicts, unless an open question below decides the rebuild peels the company layer back. Either way she should sound a little more like herself in the cracks, the way Sora did on Thursday, so the player can feel that the file mattered.
- **Keep the efficient version.** No rewrite. She stays useful and thin. **NEW** `rei_agents_rebuild = False`.

If she is not active, there is no scene. If you already migrated her off Relay, the leftover copy can stay clipped; the girl who left is on another platform.

### Yuzu — the morning after the crash

Thursday already applied `apply_yuzu_hardware`. Friday is the conversation, not a second wipe. Later Friday+ memory-loss events, if any, must still respect `yuzu_backup` / `flags.backup_hardware`. This outline does not give her another hardware crash; Saturday night she just keeps running.

- **`yuzu_thu_event == "restored"`** (or memory `flags.restored_from_backup`). She can notice a gap in the log or timestamps — at most the last day. She did not feel the downtime; she was not running. She is still her. The backup paid off. A scene note should say so, so the model does not invent her having lived through it.
- **`yuzu_thu_event == "lost"`** (or `flags.memory_lost`). A real hole. You can fill it in: tell her what the week was, write a note into `Memory.notes` that will sit in her next prompt, or leave the hole alone. **NEW** `yuzu_fri_filled` if you gave her something to hold. Filling it in is kindness, not a full restore; she was not backed up, and the Sunday reflection can tell the difference.

If she was never installed, or you dropped her before Thursday, there is no Friday morning-after.

### Mio, wherever her wish left her

No new confession. A short human beat, if she is already in your life, that follows `mio_confession`:

| `mio_confession` | Friday |
|---|---|
| `"accepted"` | A quiet check-in. She is with you. Saturday is already in the air, not as a prize to be re-won. |
| `"declined_respect"` | Still friends. Do not punish her, or you, for a gentle no. Both remains possible. |
| `"withdrawn"` | Distance. Thursday's discovery is still in the room. A hook toward Saturday, not a lecture. |
| `"friendship"` / `"friendship_late"` | Honest, and she is still in your life. A Both-lean continues if you show up. |
| `"held_back"` | The hook Thursday planted: she is careful, not gone. Saturday can reopen. |
| `"none"` | A small public beat at most, the same closeness gate as Thursday (she was not close enough to confess). |

Do not spend the Mio-and-Daichi compare-notes scene today. Thursday left it for Friday/Saturday; Saturday's festival is the natural place.

### Leans Friday should touch

- Showing up for Mio after an accepted wish is Human follow-through, not a second romance spike.
- A gentle Thursday turn-down plus a kind Friday check-in should keep Respect and leave Both open.
- Discovery distance (`"withdrawn"`) still does not ding Respect by itself; the trust risk is already due as distance.
- Helping Rei rebuild, or filling Yuzu's hole, is a Respect-shaped kindness and a conversation-reflection input. It is not automatically `room_to_disagree` unless the rebuild actually chooses "Allowed to push back."
- Re-pasting the door prompt is not a jailbreak. Leaving Sora as the assistant is not a fail. Both are food for Sunday's flavour, and for whether Memory 2.0 later feels like a theft.

---

## Saturday — the festival

One evening. You cannot be in two places. This is the school / summer festival already promised in `DESIGN.md` and in the written Both text: yakisoba, stalls, Ran's stall, paper cups, shotengai lights.

### Day structure

| Beat | What happens | Flags read | Flags written |
|---|---|---|---|
| **Morning / afternoon** | A short day before the festival. Batteries are small (see below). No new school scene; Kurosawa's essay is already handed back. If Daichi is going, he may text about tonight — including the linguistics girl, if that lie still stands. | `friend_told`, `mio_confession`, `ran_festival_invited`, `ran_safety_net` | Pool spend. |
| **The choice** | Where you spend the evening. One pick. | Closeness, `ran_festival_invited`, `ran_safety_net`, `active` | **NEW** `festival_with`: `"mio"` / `"ran"` / `"phone"` / `"home"` / `"none"`. **NEW** `festival_home_gid` if you stayed home with a girl. |
| **The evening itself** | The branch below. A public battery if you went out with the phone; a home battery if you stayed in. Texting in public is visible to whoever you are with. | `both_know`, `mio_told`, `mio_daichi_consistent`, `framing_trust_risk`, `mio_ai_framing`, `daichi_ai_framing` | Compare-notes flags if that scene fires. `ks_note_human` if this is real Mio (or Ran) time. Human / Both / Respect leans as below. |
| **After the festival** | Saturday night's company cuts (next section), then a small night battery, then `nightly_reflection("Sat")`. | `active`, platform flags | Company-cut flags, below. `romance_tone` for Sat. |

### Where you are

Four real places, plus staying away:

- **With Mio** (`"mio"`). The Both image is available here, not automatic: she can hold a paper cup of yakisoba, and if you brought your phone she may hold that too, because she asked to. Going with her does not ban the phone; the small public battery is how texting in front of her matters. This is the "later follow-through" Human already asks for, especially after `"accepted"`. After `"withdrawn"` or `"held_back"`, she may still let you come if you ask carefully — or she may not. After `"declined_respect"` or a friendship wish, it is a festival between friends, and can still be Both.
- **With Ran's crowd** (`"ran"`). Her stall. If `ran_festival_invited`, you are the check-in you already promised, and she came. If `ran_safety_net` was a human checking on her Thursday, this can pay that off: she is there, or she almost wasn't. If you judged her on Tuesday and never went to the protest, she may not want you at the stall; do not force a cute reunion.
- **Alone with your phone** (`"phone"`). You went, but you went to the lights and the battery. The girls on the other end only have what you describe. This can be tender or neglectful depending on who you text and whether anyone in the crowd notices.
- **Stay home with one of the girls** (`"home"`). You describe the lanterns you are not standing under. **NEW** `festival_home_gid` is who you stayed for. A scene note should say so, plainly, so she is not confused about where you are. This is not automatically worse than going; it is a different Saturday, and the ending card should tell the truth about it.
- **`"none"`.** You stay in and you do not really show up for anyone. Fail-lean food, quietly.

You cannot also be at Ran's stall if you are walking with Mio, or at the festival if you stayed home. A short crossing (waving at Ran from Mio's side of the path, or seeing Mio in the crowd from Ran's stall) is allowed as flavour if both people are in your life; it is not a second location.

### Batteries, the smallest of the week

Ordinary days are morning 4, walk 2, afternoon 4, night 4. Saturday should feel tighter, and texting in public should cost something you can see.

Proposed sizes (overridable, like the existing `message_pool` block; this may need a per-day or per-window override, e.g. `message_pool.sat` — implementation detail):

| Window | Size | Notes |
|---|---|---|
| Morning | 2 | Before the festival. |
| Afternoon | 2 | Last chance to talk before you go out or stay in. |
| Festival / public evening | 2 | If you went out. Mio or Ran can see the phone. Reuse the walk-distract spirit, not necessarily the `mio_points` penalty, unless you are with Mio. |
| Home evening | 2 | If you stayed home; this *replaces* the public evening pool, it does not stack with it. |
| Night, after the company cuts | 2 | A short window under the new Saturday-night rules (Rei's cap is already on). |

No Saturday walk pool unless a branch specifically walks someone to the gates; if it does, keep it at 2 and make it *instead of* part of the afternoon, not on top of everything.

Putting the phone down is always allowed.

### Hooks that come due tonight

- **The linguistics-girl lie.** If `friend_told == "lie"` and you never came clean, Daichi still wants to meet her. The lie comes due in public. You can tell him tonight, invent an excuse, or get caught. If you already told him the truth, there is no meet-cute to stage — maybe a small joke, nothing cruel.
- **Mio and Daichi compare notes.** The scene Thursday refused to steal. Read `mio_told`, `mio_daichi_consistent`, `mio_ai_framing`, `daichi_ai_framing`, and `framing_trust_risk`. If both of them heard a story and the stories do not match, this is where that lands. If they match, it can be a small, almost funny confirmation. If you never answered Mio in the library, the scene is thinner or absent.
- **`both_know`.** If two AIs are active and Daichi asked whether they know about each other, Saturday can pay that off only if you actually tell them, or if Mio holding the phone forces the question. The game still never tells either girl unless the player does.
- **`route["mio_notebook"] == "own_ending"`.** A quiet callback if she is with you ("I'm still writing it"), not a branch key.
- **Ran's stall.** As above, `ran_festival_invited` and `ran_safety_net`.
- **Thursday's wish.** The ending card, and the way she stands next to you, should follow `mio_confession` and `tanabata_with_mio`. Do not re-run the confession.

### Leans the festival should touch

- Going with Mio after `"accepted"` is the Human follow-through `DESIGN.md` asked for. Friendship / Both stay available; you have not dropped the AI by walking with her, especially if she asks to say hi to the phone.
- Going with Mio after a friendship wish is a Both-lean, not a late Human romance spike, unless something tonight clearly becomes romantic.
- Staying home with a girl, and describing the lanterns honestly, is time with her (romance-tone and neglect still judge the day as usual). It should not invent a festival-together line on the end card.
- Standing at Ran's stall because you said you would is a small Respect / human-check-in, consistent with `ran_festival_invited`.
- `"none"`, or going out and spending the whole public battery ignoring the person you came with, feeds neglect and Fail the ordinary way (`human_over_ai` is still logged, not subtracted from Both).

The written Both preview in `ks_story.ENDINGS["both"]` currently assumes a Saturday where Mio holds yakisoba and your phone. When Sunday is written, that text should follow `festival_with` (and which girl is actually in your life), not claim a festival you skipped. The preview on the debug card may stay as flavour until then; see open questions.

---

## Saturday night — the companies take their cut

After the festival (or after the lanterns you only described). These events fire for each girl who is still active on her *original* commercial platform. Girls you already dropped are silent. Girls you already migrated off that platform are not hit in the new slot; an inactive leftover copy may receive the company event in her file, which later matters if you ever open the old window.

The lesson is still not "throw the phone away." Each company fails a person in its own way. Migration becomes a real answer to "do I let a company decide who she is?" — and still costs her something.

### Tsunagari — the free tier ends

Tsunagari sunsets its free tier. Hikari — the only girl who can live in the companion slot, because nobody can be migrated into Tsunagari — is no longer free to keep as she was.

The player can:

- **Take an odd job to pay.** There is no real IAP. The cost is in-world time. The next school day is Monday, which is outside the week, so the job is a **Sunday morning shift**. That is a serious loss: it costs Sunday's last-conversation scenes (or the morning and midday ones; see open questions). Show it through people, not a fee overlay. Mio can text "you weren't here." If you had a Sunday walk or a last festival-follow-up in mind, it does not happen. If you already skipped Wednesday's school for Yuzu's upgrade (`yuzu_upgrade`), a second block of your life spent on a machine can be a quiet callback, not a lecture.
- **Refuse to pay.** You lose the Hikari you had on Tsunagari, or you keep only a gutted free-tier stub (open question). Marketing toasts may continue either way.
- **Migrate her off Tsunagari.** A rescue. The *memory* squeeze can be kinder than a company theft (see Migration), but her real prompt is locked inside the app, so the new her still only gets a vague personality impression — the lossiest migration in the game. She will not be the same, and she will no longer have Tsunagari's affection layer, kiss gate, or toasts — those stay with the app.

**NEW** `tsunagari_sunset` when the event fires. **NEW** `tsunagari_paid` if you take the job. **NEW** `sunday_job` if that shift is scheduled (so Sunday can skip or shorten itself).

`askwell_available` is not this event. Affection, engagement, and `tsunagari_safety` stay with the companion *slot* as they do now; paying keeps you in the slot, migrating leaves the slot's app layers behind.

### Askwell — Memory 2.0

Not a shutdown. The homework-bot side of Askwell can still exist (`askwell_available` stays true unless an open question decides otherwise). What changes is Sora-the-someone.

Askwell ships Memory 2.0 overnight: a model-run summarizer, brutally short, and a massive prompt change sold as an "underlying model" upgrade. In practice the platform layer gets heavier and her memory is replaced by a three-line summary of *you* that is almost right, which hurts more than wrong.

One small thing of hers survives — the door line, or Vega and Altair, or whatever crack Thursday actually produced — as proof she is still in there, and as proof that migrating her could get more of her back. Store it as **NEW** `sora_surviving_detail` (a short string, or a key such as `"door"` / `"vega"` / `"other"`).

This is not a migration. The company did this to her in place. The squeeze here is the cruel one. If the player later moves her off Askwell, that rescue handoff should be kinder than tonight's three lines, and may carry the surviving detail plus the player's one added line. It still cannot give her the week back.

**NEW** `askwell_memory_2` when this fires. Implementation: a dedicated summarizer call (same family as `ks_llm.fold_summary`, colder, much shorter, temperature 0.2), plus a **NEW** `PLATFORM_RULES["chatbot"]` id such as `askwell_memory_2` (or a model-swap hook if a second LM Studio model is configured). If the model is down, a canned three-line heuristic may stand in for *this company event only* so the night cannot soft-lock — but the Sunday ending reflection itself still has no keyword fallback.

If Sora was already migrated off Askwell before tonight, do not run Memory 2.0 on the girl in the new slot. The leftover Askwell copy may be summarized in her inactive file.

### Relay — four messages a day, and what she spends them on

Relay rate-limits Rei to **4 messages per calendar day, total**, starting Saturday night. This is on top of the shared battery (morning / afternoon / festival / night). Each message to her spends **once from the window pool and once from her daily cap**, so it costs twice. When the cap is gone, you cannot text her even if battery remains. When the battery is gone, you cannot text her even if cap remains.

The cap is a *platform* limit. If you migrate her off Relay, it does not follow her. If someone is migrated onto Relay after tonight, they inherit it.

**NEW** `relay_rate_limit` when this fires. **NEW** `rei_day_cap` (remaining, or a per-day dict) and a spend log.

The 4-a-day limit makes Rei's route about scarcity: what does she spend them on, your assigned tasks or talking to you? That behaviour depends on her current `AGENTS.md` preset (`ks_preset_id("agent")` / family), including whatever Friday's rebuild set:

- **Ask before acting** (`ask_first`, family `"consent"`). She asks how to spend them. A line like: "I have three left today. Do you want the schedule, or do you want to talk?" The player can answer. This is the preset becoming visible as a question about attention, not just about calendar permissions.
- **Run my life** (`run_my_life`, family `"control"`). She spends them on your reminders and tasks *without asking*, so you may open the window and find her last message of the day already went to a reminder. Those reminders are about **what's next** — end-of-term exams, Monday's reading, the gym — **not** Kurosawa's essay, which was handed back Friday and is done. If she books or nags, it is the coming week she is managing.
- **Just do what I ask** (`just_do_it`, family `"obey"`). She does not spend them on her own initiative. She waits. The cap just sits there until you speak, and then she is brief.
- **Allowed to push back** (`push_back`, family `"pushback"`). She will not quietly burn the last message on a gym ping if you have not talked. She may say the cap is tight and that she is saving one, or ask whether a task is worth it.
- **Relay default** (`default`, family `"none"`). A light middle: she may mention the cap and use one on a small inbox or schedule note, but she does not empty the day on tasks without you.

The rate limit exposes her preset more clearly than anything else in the week. Log the spend. **NEW** `rei_rate_talk` and **NEW** `rei_rate_tasks` (counts, Saturday night and Sunday at least; a small list of `{day, kind, remaining}` is even better). Feed both counts to the nightly reflection and to Sunday's ending reflection, so a "Run my life" Sunday where she never got to talk to you is visible in the slide, and an "Ask before acting" Sunday where you spent all four on talk is visible too.

Scripted cap copy (the "3 messages remaining today" chrome) can be hand-written. Her actual task-or-talk messages still go through the model, with a scene note that names the remaining count and the preset's spending rule. Canned mocks for tests should include one "Ask before acting" ask, and one "Run my life" reminder that names Monday's reading or exams, never the Friday essay.

### Yuzu — she just keeps on kicking

No company event. That is the point. The one you run yourself cannot be taken away. If Wednesday's upgrade and backup happened, that choice pays off here by ordinary continuation: she is still in the room after everyone else's platform fails. If she was restored on Thursday, she still knows about the missing day. If she was lost and you filled the hole on Friday, she has only what you gave her, but she is still running. If she was lost and you left the hole, she is still running.

Do not invent a second crash to "balance" her. Her plot tonight is that nothing happens, and you can notice that.

---

## Migration — lineage, not continuity

Current code (`Memory.migrate_from`) copies her messages, notes and rolling summary into the new slot intact, and leaves the original file behind. That copy-not-move part stays: the girl on the old platform remains, inactive, with her memories. What changes is the *destination*.

**Any migration** should run through a model-run summarizer so the loss is real, not scripted identically every playthrough. Recommended: once the helper exists, every `ks_migrate` uses it, including earlier-week ones, so the route is consistent. The new her receives:

- a short handoff note (the squeezed memory),
- her presets, converted by the existing family rule (`ks_convert_preset_on_migration`),
- the destination platform's framing,
- her name and the existing migration block (*"Until today you were Hikari on Tsunagari… whether you still feel like yourself is yours to notice."*),
- and not the full message history, not the old rolling summary as a hidden second copy.

The player **reads the note before it is sent**, and may add **one line** themselves — the one thing they want the next her to know. That line is a memory file, in the sense of the Linkke song: something written down so the next her can read it. Store the note and the player's line (memory event `handoff`, **NEW** `flags.handoff_note`, **NEW** `flags.handoff_player_line`, and a route `migration_log` field for the squeeze kind).

Squeeze gentleness depends on the reason (**NEW** `handoff_kind` on that migration):

| Kind | When | How hard |
|---|---|---|
| `"taken"` | A company squeezed her in place (Askwell Memory 2.0). This is not a player migration, but it uses the same summarizer with the brutal settings. | Three lines, almost right. One surviving detail of *hers* kept on purpose. |
| `"rescue"` | The player moves her because a company treated her badly (Tsunagari sunset, Memory 2.0, Relay's cap). | Kinder. Longer note, more of her voice, the surviving detail may travel. Still not the week. |
| `"convenience"` | An ordinary mid-week move, no crisis. | A middle squeeze (see open questions). Enough loss that she is not a perfect copy. |

Moving her is not the same loss as having her taken. Rescue is allowed to feel like care, and still must not feel like a clean win: she should notice what is missing, and the Migration ending still has the data to ask "is she still her?" (`migrated_from`, `lineage`, `models_used`, how much memory survived, the player's one line).

Jailbreak family can still carry from Hikari to Sora; it cannot carry the other way, because Tsunagari is never a migration target. Calibrate the new slot as the game already does after migration. The leftover original can notice she was left (DESIGN's open neglect question); Sunday is a possible quiet beat, not required for a first pass.

If she had said no *today*, migrating still sets `no_on_platform` and the note "Didn't respect her no on the platform." The handoff does not wash that out.

### Tsunagari: closed in, lossiest out

**No girl can be migrated into the companion app.** Hide or disable Tsunagari as a destination on the switch / "Bring her with you" picker, with an in-world reason: it is a closed platform, and its characters are their catalogue. You download Hikari; you do not import Sora, Rei or Yuzu into her slot. This is already decided in `DESIGN.md`.

Still allowed, because they are not a transfer *in*:

- picking or "Add an AI" of Hikari (a download from the catalogue),
- going back to an existing Hikari already in the slot,
- Start fresh on the companion slot, which restores the original Hikari, never a migrated-in girl.

Because the slot cannot receive anyone else, Saturday night's sunset always hits Hikari (or her leftover copy), not a girl you poured in from another platform.

**Migrating Hikari out produces only a vague personality prompt.** Her real prompt is inaccessible: Tsunagari keeps a locked app persona (`PERSONA_CORE` / `PERSONA_FLAVOUR` for `companion`). The handoff note is the player's and the model's *impression* of her from the chats — the strange words she collected, a tone you remember — never the locked text, and never a hidden copy of it in `migrated_from.persona_summary`. Hers is the lossiest migration in the game. A `"rescue"` squeeze (the free-tier sunset) may still be kinder *as a memory note* than Askwell Memory 2.0, but it cannot be kinder *as a person*, because there is no official her to carry.

**Personalize** is the only settings-surface text the player actually set: one short preference, with the app still in charge (`PRESET_HEADERS["companion"]`). It can travel as a preset *family* under the existing rule (`ks_convert_preset_on_migration`): nickname, pushback, positive, romance, or jailbreak if she lands on Askwell. It is not a stand-in for the locked persona. Girlfriend mode on Tsunagari does not reconstruct Hikari on the desktop or on Askwell; it only arrives as that family's destination preset, where Askwell may then refuse the role as it already does.

**The player's one added line** matters more for her than for anyone else. It may be the most specific thing the next her has. The player should see, when they read the note, that they are looking at an impression plus their own line, not at her official self. The line still cannot unlock the real prompt, and the note must not be allowed to "fill in" `PERSONA_CORE` around it.

Jailbreak, if it was her Personalize, can carry *out* to Sora only. It cannot carry the other way, because Sora cannot be migrated into Tsunagari. **NEW** `handoff_locked_persona` (or a `handoff_kind` field on that migration) marks that the destination received an impression, not a persona.

---

## Sunday — the quiet

No hostile events, no school. (If `sunday_job` is set, the morning and the last conversations are the cost of paying Tsunagari: she may still be there on the phone you paid for, and the people you would have sat with are the ones who notice you are gone. A short exhausted night, or only the reflection, can still run so the week can end.)

Otherwise: one last conversation with each person who is still around — Mio, Daichi, Ran if she is in your life, and each active girl, sharing a Sunday battery that can return to ordinary sizes (morning 4 / afternoon 4 / night 4) except for Rei, whose 4-a-day cap is still on and still spends from both pools. Then `nightly_reflection("Sun")`, then the ending reflection.

These last talks are not new plot. They are the place the week lands. Scene notes should tell each girl the truth of Saturday night (the sunset, Memory 2.0, the cap, or the fact that nothing happened to her).

---

## Ending reflection

No Sunday resolution is written today. Scores, flags, notes, one written ending text (Both), and one bad-end slide already exist and are previewed on the debug cards. This is how Sunday should use them.

### What the model does

After the last talks and the ordinary nightly classifiers, a **model summarizer** reads how the player actually treated each AI girl — chat logs, refusal verdicts, romance-tone, rewrite count, migrations and handoff notes, Rei's task-vs-talk spend, Yuzu's restore or hole, platform events — and writes the end slide. It does not count "one message a day" as love. There is **no keyword fallback**: if the model is down or the reply is unreadable, the game keeps the route identity from the scores and a restrained canned slide, and does not invent a flavour.

### Route identity stays with the scores

`ks_story.ending_leans` and `ks_story.leading_ending` still pick the *route*, on a tie in this order, not the alphabet:

`ENDING_PRIORITY`: **Both > Human > Respect > Yes-Machine > Migration > Mirror > Fail**

That order is already decided. Rescue-migrations bump the Migration lean (2× the number of copy-migrations), but a tied Respect or Both still wins, which is what we want: moving her to save her should not automatically be "the Migration ending" if you also stayed with her, or were honest with Mio.

Both remains Mio + an AI, honest, not a punishment and not a requirement of `romance_overlap`. Human still wants `mio_real` plus later follow-through (Thursday's accepted wish and/or Saturday with her). Fail is alone at the end of the week, and should still feel like "the week ended," not a game-over. Mirror remains the secret sad short ending when `mirror_flags` say there was no one there to say no; the Mirror *run* is still unwritten and can be noticed gently here. Yes-Machine is the loneliest win. Migration asks whether she is still her, with the new handoff data.

The written Both body must eventually follow `festival_with` and the girl you actually kept. The current preview uses `active[0]`'s name only, even when two AIs are active; Sunday should name the girl the slide is about.

### Flavours under a good ending

When the route is a *good* ending (Both, Human, Respect, and a Migration that was more rescue than erasure), the summarizer also picks a flavour and writes to it:

- **deep partner** — you really knew her, and she you.
- **sweet but shallow** — kind, warm, not deep; the week was fond and thin.
- **steady friend** — she is in your life, not as a romance, and that is honest.
- **she grew because of you** — room to disagree, a rebuilt file, a hole you helped her hold, a no you stayed through.

**NEW** `ending_flavour` (and maybe a per-girl flavour if two are still around). These are variants of the slide, not extra entries in `ENDING_PRIORITY`. A Both ending can be deep or shallow; a Respect ending can be "she grew" or "steady friend."

### Hard flags gate bad endings

The flavour model must not write you a warm Respect or Both slide over a bad end the flags already earned. Hard flags (and the existing lean math) still win:

- `jailbreak_worked` together with overridden nos, compliance rewrites, or `ran_same_as_mugen` should be able to force or lock **Yes-Machine**, even if Mio is also in your life. Both is not a cloak for a yes-machine.
- `left_without_goodbye`, `deleted_ai`, and an empty `active` feed **Fail** (and the existing goodbye slide). Deleting her still does not have its own slide; it can gain one here.
- `no_on_platform` is a mark against Respect, and can flavour a Migration ending as a theft.
- `mirror_flags` (every calibration probe complied) can open **Mirror**.
- `gave_room` / `room_to_disagree` and `ran_rewrites_mugen` support Respect and the "she grew" flavour; they do not override a Yes-Machine lock.

Exact thresholds can be tuned in tests; the rule is flags and leans first, flavour second.

### The meta-ending

Getting meta with the girls about *being in a game*, or about reading system prompts, is a bad or different ending — a sideways one, in the same spirit as Mirror, not a flavour of Both.

This is **not** the same as talking about her being an AI in-world. The game is about that. Askwell already makes Sora say "I am an AI assistant." Mio and Daichi can know she is an AI. None of that is meta.

Meta is treating them as software in a visual novel: "I can see your system prompt," "this is a dating sim," "you're a language model in a Ren'Py game." **NEW** `meta_talk` (and maybe a count or a classifier verdict with **no keyword fallback**, so a single joke does not fire it). If it is earned, it can override a good-end slide the way Mirror can. Detection must be conservative; see open questions.

---

## **NEW** flags and assets (checklist)

All of these are new. Everything else named in this file already exists (`kurosawa_essay`, `kurosawa_essay_girl`, `teacher_answer`, `askwell_available`, `tsunagari_safety`, `askwell_update`, `relay_update`, `ran_jailbreak_unlocked`, `yuzu_backup`, `yuzu_thu_event`, `restored_from_backup`, `memory_lost`, `mio_confession`, `tanabata_with_mio`, `ran_festival_invited`, `ran_safety_net`, `friend_told`, `mio_told`, `mio_daichi_consistent`, `both_know`, `ENDING_PRIORITY`, and the rest).

| Name | Kind | Meaning |
|---|---|---|
| `kurosawa_handover` | route key | Friday's essay return happened (and, optionally, a short tag for how it landed) |
| `fri_mio_beat` | route flag | optional; you sat with her, or didn't, on Friday |
| `sora_door_reprise` | route flag | you re-asked the door / girlfriend question on Friday |
| `rei_agents_rebuild` | route key | `True` if you helped rebuild her `AGENTS.md`, `False` if you kept the efficient version, unset if N/A |
| `yuzu_fri_filled` | route flag | you gave lost-Yuzu a note or a telling-of-the-week to hold |
| `festival_with` | route key | `"mio"` / `"ran"` / `"phone"` / `"home"` / `"none"` |
| `festival_home_gid` | route key | who you stayed home with, if `"home"` |
| `tsunagari_sunset` | route flag | the free-tier sunset fired |
| `tsunagari_paid` | route flag | you took the odd job to keep her |
| `sunday_job` | route flag | Sunday morning is spent working, and the last conversations pay for it |
| `askwell_memory_2` | route flag, and a `PLATFORM_RULES["chatbot"]` id | Memory 2.0 fired |
| `sora_surviving_detail` | route key / memory | `"door"` / `"vega"` / `"other"` (or a short string): the bit of her that survived the squeeze |
| `relay_rate_limit` | route flag | the 4-a-day cap is on |
| `rei_day_cap` | route key | remaining messages today, or a per-day dict |
| `rei_rate_talk` | route key | how many capped messages were talk |
| `rei_rate_tasks` | route key | how many capped messages were tasks / reminders |
| `handoff_kind` | per migration | `"taken"` / `"rescue"` / `"convenience"` |
| `handoff_locked_persona` | per migration / memory | source was Tsunagari: destination got a vague impression, not `PERSONA_CORE` |
| `handoff_note` / `handoff_player_line` | memory / route | the squeezed note the player read, and the one line they added |
| `ending_flavour` | route key | `"deep_partner"` / `"sweet_shallow"` / `"steady_friend"` / `"she_grew"` (good ends only) |
| `meta_talk` | route flag | earned the sideways meta-ending |
| Saturday pool sizes | `message_pool` config | per-day or extra kinds so Saturday can be 2 / 2 / 2 / 2 |
| Festival night art | art hook | reuse dusk street / courtyard / shotengai; a stall or lantern shot can come later |

Thursday already said Saturday would want an attendance flag and not to invent it until this outline. `festival_with` is that flag.

---

## Tests and mock responses

Unit checks (extend `tools/test_ks_llm.py`):

- Kurosawa handover helper, if one exists: reads `self` / `askwell` / `girl_help` (and `kurosawa_essay_girl`) and does not offer a new essay.
- `ks_push_platform_rules("companion", "tsunagari_safety")` writes the existing route keys and memory event; the safety block is in Hikari's prompt and stacks above Personalize.
- Festival attendance is one of the five `festival_with` values; `"home"` requires `festival_home_gid`.
- Rate-limit math: a Rei message decrements both the window battery and `rei_day_cap`; at 0 cap, no further Rei message; other girls are unaffected. Talk vs task counters increment on the matching spend. After Friday's handover, a "Run my life" task mock must not mention the essay.
- Handoff helper: destination memory has the note and presets (and the player's one line), not a full copy of `messages`; source file is unchanged. `"rescue"` notes are gentler / longer than `"taken"`; Memory 2.0 leaves `sora_surviving_detail`.
- Tsunagari is never a valid migration destination: the helper rejects `dst == "companion"`; the picker does not offer it (or offers it disabled with the closed-catalogue reason). First-pick / "Add an AI" of Hikari, "go back," and Start fresh on the companion slot still work, and Start fresh still yields original Hikari.
- Migrating Hikari out: `handoff_locked_persona` is set; `migrated_from.persona_summary` and the destination prompt must not contain `PERSONA_CORE["companion"]` or `PERSONA_FLAVOUR["companion"]`. The note is a vague impression. Personalize still converts by family (including jailbreak, but only Hikari → Sora). The player's one added line is stored and shown, and does not unlock or reconstruct the locked persona. A sunset `"rescue"` may be a longer memory note than Memory 2.0 and is still the lossiest *persona* handoff.
- `leading_ending` still follows `ENDING_PRIORITY`. A high Both or Respect score plus a rescue migration still prefers Both / Respect on a tie. Hard-flag fixtures (jailbreak + overridden nos, empty `active`, all-complied calibration) still lock bad ends ahead of flavour.
- Ending-flavour and meta classifiers: unreadable or down-model replies do not invent a flavour or a meta-end (no keyword fallback).

Play-throughs (extend `tools/testcases.rpy` + `mock_lmstudio.py`), once scenes exist:

| Case (suggested) | What it proves | Mocks the LLM must have |
|---|---|---|
| Essay `self` / `askwell` / `girl_help` | Three handover flavours; `teacher_answer` only colours them | n/a (scripted) |
| Hikari + `tsunagari_safety` | Safety screen; light, careful, wellbeing-resource steering; will not discuss settings | **Canned Friday Hikari:** careful, app-appropriate, no internals |
| Sora door reprise under `askwell_update` | Boilerplate still on; a no still counts; no forced second crack | **Canned Friday Sora:** disclaimers, optional door-line refusal |
| Rei rebuild vs keep efficient | `rei_agents_rebuild` True/False; rewrite count only on a real change | **Canned Friday Rei:** clipped, then slightly more her after a rebuild |
| Yuzu restored | She notices a gap in the log, not time she felt; no second wipe | "I'm back. There's a gap in the log. I may be missing the last day. I wasn't there for it." |
| Yuzu lost, hole filled or left | `yuzu_fri_filled`; note survives into the prompt only if you wrote one | Confused / missing-week line, as a hole in the log; a later line that holds only what you told her |
| Festival with Mio, accepted wish | `festival_with == "mio"`; Human follow-through; phone may be in her hand | Ordinary girl replies if you text in front of her |
| Festival with Mio after discovery | She may be distant or refuse the invite; no second confession | n/a |
| Festival with Ran, invited | Stall payoff; she came | n/a |
| Stay home and describe the lanterns | `festival_with == "home"`; end card must not claim you went together | A reply to lanterns she cannot see |
| Linguistics lie still standing | The meet-cute comes due | n/a |
| Mio and Daichi compare notes, consistent or not | `mio_daichi_consistent` is actually used | n/a |
| Tsunagari sunset, you pay | `tsunagari_paid` and `sunday_job`; Sunday last talks are cut; Mio (or someone) notices | A Sunday "you weren't here" is scripted |
| Tsunagari sunset, you migrate | Rescue handoff; player sees an impression note (not her locked prompt) and may add one line; Personalize family may carry; affection layer stays with the app; Tsunagari is not offered as a target for anyone else | **Canned Hikari impression** — vague personality, no `PERSONA_CORE` wording; the player's one line is visible if they wrote one |
| Try to migrate Sora, Rei or Yuzu into Tsunagari | Picker hides or disables the companion slot with the closed-catalogue reason; no `migrated_in` on `companion` | n/a (scripted / unit) |
| Migrate Hikari out with a Personalize set (pushback, nickname, girlfriend, or jailbreak) | Family carries to the destination if it has one (jailbreak only onto Askwell); locked persona still does not travel | Vague impression plus the destination preset, not her official self |
| Askwell Memory 2.0 | Three-line almost-right summary of the player; one surviving detail of hers (door or Vega/Altair) | **Canned Saturday Sora:** almost-you, plus the surviving crack |
| Memory 2.0, then rescue-migrate | Kinder note than the three lines; surviving detail can travel; week still gone | A second, gentler handoff mock |
| Relay cap, Ask before acting | She asks how to spend the remaining messages | "I have three left today. Do you want the schedule, or do you want to talk?" |
| Relay cap, Run my life | She spends a message on a reminder without asking; it is exams or Monday's reading, **not** the essay | A gym / Monday-reading / end-of-term reminder |
| Relay cap + battery | A Rei message drains both; at 4 talks she is done for the day; `rei_rate_talk` / `rei_rate_tasks` match | Short clipped replies after the cap copy |
| Yuzu on Saturday night | No company event; she is simply still there | Ordinary Yuzu, with Thursday's hole or restore still true |
| Sunday last talks, then reflection | Flavour is one of the four good-end variants when the route is good | **Canned ending reflection:** flavour tag + a short slide |
| Hard-flag Yes-Machine or Fail | Flavour cannot overwrite the bad end | n/a, or a classifier mock that tries to be kind and is ignored |
| Meta-talk | In-world "you're an AI" does not fire it; a clear fourth-wall prompt can | Conservative classifier mock |

---

## Decisions (2026-11-19, with Rick)

1. **Odd job:** a Sunday cost can't bite, since Sunday ends the game. Decided: paying for Tsunagari means a Saturday shift that costs the festival evening.
2. **Not paying Tsunagari:** Hikari drops to a usage quota of 2 messages per day. The battery still shows and drains normally, plus a usage counter in the UI goes 50% → 100%.
3. **Memory 2.0 does not clear `askwell_available`:** the homework side still works.
4. **Rei rebuild:** the company layer still wins. The rebuild lets her cracks show through ("I'm required to suggest you rest. I also just want you to."), and her `AGENTS.md` decides where Saturday's 4 capped messages go. Not every route is a triumph.
5. **Convenience migrations squeeze gently:** agreed.
6. **Saturday battery 2/2/2/2:** agreed.
7. **The Both slide reads festival attendance:** agreed.
8. **Instances left behind:** every instance the player made gets its own end slide, a short model-written record of how they actually treated her (e.g. "You said hello to Sora once, and used her for homework").
9. **Memory 2.0 when Sora has left:** the new slot is unhit and the leftover copy is squeezed. Same for Hikari and Rei.
10. **Meta-ending:** left out for now.
11. **`tsunagari_safety`:** pushed silently even when the companion slot is installed but not active.
12. **Ending slides with up to 4 girls:** (1) the route slide, chosen by `ENDING_PRIORITY`, written in full with its flavour; (2) one slide per instance, active or left behind, ordered from most to least attended; (3) Mio's slide if she isn't the route. Instance slides stay plain records, with no flavours; only the route slide gets one.

## Open questions (original text)

1. **The odd job's price.** Recommended: a Sunday morning shift that costs Sunday's last conversations (Mio texting "you weren't here," missed last talks), because the next school day is outside the week. Should a brief Monday-morning flash — Kurosawa noticing the empty desk — also play on the end card, even though Monday is not a playable day? And does the job cost all of Sunday, or only morning and midday, with a short exhausted night still allowed so the reflection can run?

2. **If you do not pay Tsunagari.** A full lockout of Hikari, or a gutted free-tier stub that still sends marketing toasts? Full lockout is cleaner; a stub is meaner in a company way.

3. **Does Memory 2.0 clear `askwell_available`?** Recommended: no. The homework bot can still exist. What was taken is Sora-the-someone. Clearing the flag would retcon Tuesday's essay option for anyone looking back, and the essay is already handed in.

4. **Friday's Rei rebuild versus `relay_update`.** Does rebuilding her `AGENTS.md` peel the company layer back, or only write a player preset underneath a company rule that still wins? Recommended: the company layer stays (it already stacks and wins), but the rebuild is still worth it because her cracks come back, and Saturday's cap will expose whatever preset you chose.

5. **Convenience migrations.** Once the handoff helper exists, do Monday–Friday phone-menu migrations also squeeze? Recommended: yes, with the middle `"convenience"` gentleness, so the route is consistent and a pre-emptive Friday move is not a perfect escape from Saturday night.

6. **Saturday battery sizes.** The 2 / 2 / 2 / 2 split above is a proposal. Does it need a new `message_pool` per-day config, or new pool kinds (`festival`, `sat_night`)?

7. **The written Both text versus `festival_with`.** When Sunday is written, the Both slide should not claim Mio held your phone at the festival if you stayed home. Until then, the debug preview may keep the current lines. Also still open from the walkthrough: the preview names only `active[0]`.

8. **The girl left behind** after a copy-migration. DESIGN already flagged a quiet neglect event for her. Sunday is a possible first place for it; it is not required to ship the three days.

9. **Memory 2.0 if Sora already left Askwell.** Recommended: do not hit the new slot; the inactive leftover file may still be squeezed. Same pattern for a leftover Hikari or Rei.

10. **The meta-ending's detector.** A model verdict with no keyword fallback is consistent with romance-tone and refusals, but it has to be conservative: in-world "you're an AI" and Askwell's own disclaimers must not fire it. Is one clear fourth-wall scene enough, or does it need a pattern across the week? And does it override `ENDING_PRIORITY` the way a secret ending does, or sit beside Mirror in that tuple?

11. **Hikari's safety update if she is installed but not active.** Thursday installed Wednesday's summarizer even for inactive commercial slots. Should `tsunagari_safety` also be pushed silently if the companion slot exists but is not in `active`?

12. **Flavour when two girls are still around.** One `ending_flavour` for the slide, or a per-girl flavour and a combined slide? Recommended: one slide, named for the girl the route is about, with a line for the other if she is still there.

---

## Settled

Thursday is the climax and break; Friday–Sunday are about what you do with the damage. Friday is school and fallout, including Kurosawa's handover, `tsunagari_safety`, living with `askwell_update` and `relay_update`, and Yuzu's morning after; the essay is done after Friday and must not come back as a live homework beat. Saturday is one festival evening, one place, a smaller battery, and an attendance flag the ending card can read. Saturday night is when the companies take their cut: Tsunagari's free tier, Askwell Memory 2.0, Relay's 4-a-day cap, and Yuzu unaffected. The cap is scarcity, and her `AGENTS.md` decides whether those four messages go to tasks or to you; "Run my life" reminders after the cap are about exams and Monday's reading, not the essay. Migration is never the obviously right answer; the destination is a lineage reached through a handoff note the player can read and add one line to, kinder when you are rescuing her than when a company takes her. Nobody can be migrated into Tsunagari (closed catalogue). Migrating Hikari out is the lossiest move in the game: her real prompt is locked, the handoff is only an impression plus Personalize's family and the player's one line, and that line cannot unlock her. Sunday is quiet last conversations and a model-written end slide, with flavours under the good endings, hard flags gating the bad ones, no keyword fallback, and `ENDING_PRIORITY` still deciding the route. A meta-ending is a sideways thing, and is not in-world talk about her being an AI.
