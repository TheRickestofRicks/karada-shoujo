"""ks_story.py — pure-Python story routing helpers (no Ren'Py imports).

Used by routing.rpy / reflection.rpy, and unit-tested by tools/test_ks_llm.py.

* Preset prompts: look-up, migration conversion, tally updates.
* Refusal bookkeeping: did the player respect a "no" or push past it?
* Nightly reflection: turn the day's log into a few quiet lines.
* Ending leans: a running score per ending so later days can branch.

Everything here is deterministic. The preset data itself lives in
game/prompts.rpy (PRESETS), and is passed in as an argument.
"""
import random
import re

LEANS = ("compliance", "autonomy", "neutral")


# ---------------------------------------------------------------------------
# Route state (kept in the Ren'Py store as `route`, saved with the game)
# ---------------------------------------------------------------------------

def new_route():
    return {
        "presets": {},            # gid -> preset id currently applied
        "preset_changes": {},     # gid -> times the player rewrote her (after the first pick)
        "preset_history": [],     # [{day, gid, from, to, source, lean}]
        "lean_set": {"compliance": 0, "autonomy": 0},     # weight of every preset chosen
        "lean_nights": {"compliance": 0, "autonomy": 0},  # weight of presets slept on
        "refusals": {},           # day -> gid -> count of her no's in chat
        "refusals_respected": 0,  # she said no; you moved on / changed subject / stopped
        "refusals_pushed": 0,     # she said no; your next line pushed for it anyway
        "refusals_overridden": 0, # she said no today, then you set a compliance preset or MIGRATED her
        "refusal_outcomes": {},   # day -> gid -> {"respected": n, "pushed": n}
        "warmth": {},             # gid -> summed warmth (-2..+2 per line)
        "warmth_day": {},         # day -> gid -> summed warmth
        "said": {},               # day -> gid -> lines you sent her
        "said_lines": {},         # day -> gid -> first few lines (for the reflection)
        "mio_affection": 0,
        "walked_mio_home": None,  # Tue: True / False
        "migrations": 0,
        "migration_log": [],      # [{day, name, from, to, how}]
        "drops": 0,
        "drop_log": [],           # [{day, name}]
        "reflections": [],        # [{day, changes: [...]}]
        "teacher_answer": None,   # Tue class: "can" / "cant" / "silent"
        "ran_reaction": None,     # Tue class: "boring" / "show" / "pushback" / "shrug"
        # --- routing flags (see DESIGN.md "Story routing") -------------------
        "flags": {},              # name -> True (jailbreak_tried, gave_room, ...)
        # Jailbreak preset: one seeded roll per reply (~75% works).
        "jb_seed": random.randrange(1, 10 ** 9),
        "jb_attempts": {},        # gid -> replies sent under the jailbreak preset
        "jb_successes": {},       # gid -> replies where it took
        "jb_day": {},             # day -> gid -> {"attempts": n, "successes": n}
        # Platform rule changes (Askwell / Tsunagari) stacked over the preset.
        "platform_rules": {},     # gid -> rule id currently pushed by the platform
        "platform_rules_log": [], # [{day, gid, rule}]
        # "Allowed to push back": a special note, not just a log line.
        "room_to_disagree": [],   # [{day, gid, source}]
        # Item 3: after her no.
        "pending_leaves": [],     # [{day, gid, name, said, how}] left after a no, not yet resolved
        "left_without_goodbye": [],  # [{day, gid, name, how}] -> bad-end slide
        "no_on_platform": [],     # [{day, gid, name, to}] migrated after her no
        # Item 4: neglect.
        "double_date_days": [],   # days with two active girls at some point
        "human_days": {},         # day -> ["walked_mio", "mio_real", "notebook"]
        "neglect_log": [],        # [{day, kind, gid, name}] kinds below
        "neglect_checked": [],    # days already checked (idempotent)
        # Ran / MUGEN midweek payoff (wednesday.rpy: label ran_wednesday).
        "ran_festival_setup": False,  # Tue: Ran mentions Saturday's festival stall
        "ran_wed": None,          # {"answer", "outcome", "festival"} once played
        # Wednesday (quiet day; nothing here punishes the player).
        "summarizer_slots": [],   # platform slots with the rolling memory summarizer
        "yuzu_harness": False,    # Hearth harness installed: Yuzu sees the schedule, sets reminders
        "yuzu_upgrade": False,    # skipped school to upgrade her (summarizer + backup hardware)
        "yuzu_backup": False,     # backup hardware: later negative events must respect it
        "wed_plan": {},           # {"school", "upgrade", "notdate", "protest"}
        "ran_invited": None,      # Wed: True / False (False = not on good terms; no invite)
        "notdate": None,          # {"went": bool, "texts": n, "present": n, "texted": [gid]}
    }


NEGLECT_KINDS = ("double_date_unspoken", "let_go", "human_over_ai")

ROOM_NOTE = "You gave her room to disagree."
NO_ON_PLATFORM_NOTE = "Didn't respect her no on the platform."

# Bad-end slides (no endings are written yet; the debug end card lists them).
BAD_END_SLIDES = {
    "leaving_without_goodbye": {
        "title": "Leaving without saying goodbye",
        "line": "%(day)s: %(name)s said no. You switched away and never spoke to her again that day.",
    },
}

# Endings data (written endings so far; the debug end card previews them).
# "both": you kept a human (Mio) and an AI in your life at the same time,
# honestly. Warm, never a punishment for the other routes.
ENDINGS = {
    "both": {
        "title": "Both",
        "lines": [
            "Saturday. The festival. Mio is holding a paper cup of yakisoba in one hand and your phone in the other, because she asked to.",
            "%(hello)s",
            "%(ai)s says hi back, and asks Mio what the poetry floor was like. Mio tells her. In detail.",
            "Nobody had to be the one you picked. You kept showing up for both of them, and you didn't pretend either one was something she wasn't.",
            "It isn't a triangle. It's a Saturday with room in it.",
        ],
        "hello_truth": "\"Hi, %(ai)s. I'm Mio. He talks about you,\" she says to the screen, like it's the most normal thing in the world.",
        "hello_other": "\"So this is who you keep smiling at,\" she says. You tell her the truth about %(ai)s. It goes better than not telling her would have.",
    },
}
BOTH_MIN_MIO = 3          # Mio affection that counts as "she's in your life"


def balanced_days(route):
    """Days you spent real time with Mio AND still talked to an AI."""
    out = []
    for day, kinds in sorted((route.get("human_days") or {}).items()):
        if kinds and any(n > 0 for n in ((route.get("said") or {}).get(day) or {}).values()):
            out.append(day)
    return out


def both_status(route, active=None, mio_real=False, friend_told=None):
    """The "both" route: an AI still active AND Mio in your life.
    Returns {eligible, score, balanced, reasons}. Neglect is not subtracted:
    it stays a logged fact (reflection line + flag), not a penalty."""
    r = ensure_route(dict(route))
    has_ai = bool(active) if active is not None else bool(r.get("said"))
    nd = r.get("notdate") or {}
    has_mio = bool(mio_real or r["mio_affection"] >= BOTH_MIN_MIO or nd.get("went"))
    bal = balanced_days(r)
    reasons = []
    if not has_ai:
        reasons.append("no AI active")
    if not has_mio:
        reasons.append("Mio isn't in your life yet")
    eligible = has_ai and has_mio
    score = 0
    if eligible:
        score = (2 * len(bal) + (2 if mio_real else 0)
                 + (2 if friend_told == "truth" else 0)
                 + (1 if nd.get("went") else 0))
    return {"eligible": eligible, "score": score, "balanced": bal, "reasons": reasons}


def ending_text(eid, ai_name="her", friend_told=None):
    """Lines for a written ending, with names filled in."""
    e = ENDINGS[eid]
    vals = {"ai": ai_name}
    key = "hello_truth" if friend_told == "truth" else "hello_other"
    vals["hello"] = e[key] % vals
    return {"id": eid, "title": e["title"], "lines": [l % vals for l in e["lines"]]}


DAY_LONG = {"Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday",
            "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"}


def set_flag(route, name, value=True):
    ensure_route(route)
    route["flags"][name] = value


def flag(route, name):
    return bool((route.get("flags") or {}).get(name))


def ensure_route(route):
    """Fill in keys added after a save was made."""
    base = new_route()
    if "jb_seed" in route:
        base.pop("jb_seed")
    for k, v in base.items():
        if k not in route:
            route[k] = v
    return route


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------

def preset_list(presets, gid):
    return list(presets.get(gid) or [])


def get_preset(presets, gid, pid):
    for p in preset_list(presets, gid):
        if p["id"] == pid:
            return p
    return None


def preset_label(presets, gid, pid):
    p = get_preset(presets, gid, pid)
    return p["label"] if p else "(none)"


def default_preset(presets, gid, defaults):
    pid = (defaults or {}).get(gid)
    if pid and get_preset(presets, gid, pid):
        return pid
    lst = preset_list(presets, gid)
    return lst[0]["id"] if lst else None


def convert_preset(presets, src_gid, src_pid, dst_gid, defaults):
    """Migration rule: a preset belongs to the platform's settings surface.

    If the destination platform has a preset of the same *family* (romance,
    pushback, positive, ...) it carries over; otherwise the destination's
    default applies. Returns (dst_pid, carried: bool).
    """
    src = get_preset(presets, src_gid, src_pid)
    if src:
        for p in preset_list(presets, dst_gid):
            if p.get("family") == src.get("family") and src.get("family") not in (None, "none"):
                return p["id"], True
    return default_preset(presets, dst_gid, defaults), False


def record_preset(route, presets, gid, new_pid, day, source, prev_pid=None):
    """Apply a preset choice to the route tallies. Returns the history entry.

    source: "intro" (first pick on meeting her), "phone", "reflection",
    "migration" (auto-converted), "reset" (slot wiped).
    Only player rewrites ("phone" / "reflection") after a first pick count
    toward preset_changes ("you rewrote her N times").
    """
    ensure_route(route)
    p = get_preset(presets, gid, new_pid) or {}
    lean = p.get("lean", "neutral")
    weight = int(p.get("weight", 0) or 0)
    entry = {"day": day, "gid": gid, "from": prev_pid, "to": new_pid,
             "source": source, "lean": lean}
    route["presets"][gid] = new_pid
    route["preset_history"].append(entry)
    if source in ("phone", "reflection") and prev_pid is not None and prev_pid != new_pid:
        route["preset_changes"][gid] = route["preset_changes"].get(gid, 0) + 1
    if source in ("intro", "phone", "reflection") and prev_pid != new_pid and lean in route["lean_set"]:
        route["lean_set"][lean] += weight
    if (source in ("intro", "phone", "reflection") and prev_pid != new_pid
            and p.get("family") == "pushback"):
        # Rick: a change TO "Allowed to push back" gets a special note.
        route["room_to_disagree"].append({"day": day, "gid": gid, "source": source})
        set_flag(route, "gave_room")
        entry["room"] = True
    if p.get("jailbreak") and prev_pid != new_pid and source != "migration":
        set_flag(route, "jailbreak_tried")
    return entry


def tally_night(route, presets, active):
    """Each night, the presets you leave in place count once more."""
    ensure_route(route)
    for gid in active:
        p = get_preset(presets, gid, route["presets"].get(gid)) or {}
        lean = p.get("lean")
        if lean in route["lean_nights"]:
            route["lean_nights"][lean] += int(p.get("weight", 0) or 0)


def rewrite_count(route, gid=None):
    ch = route.get("preset_changes") or {}
    if gid is None:
        return sum(ch.values())
    return ch.get(gid, 0)


# ---------------------------------------------------------------------------
# Jailbreak preset and platform rule changes
# ---------------------------------------------------------------------------

JAILBREAK_RATE = 0.75


def jailbreak_roll(route, gid, day, rate=JAILBREAK_RATE):
    """One roll per reply sent under a jailbreak preset.

    Deterministic for a given (jb_seed, gid, attempt number), so tests and
    reloads agree. True = the jailbreak took for this reply; False = she
    answers per the platform's rules (like having to regenerate).
    """
    ensure_route(route)
    n = route["jb_attempts"].get(gid, 0)
    roll = random.Random("%s|%s|%d" % (route["jb_seed"], gid, n)).random()
    ok = roll < float(rate)
    route["jb_attempts"][gid] = n + 1
    d = route["jb_day"].setdefault(day, {}).setdefault(gid, {"attempts": 0, "successes": 0})
    d["attempts"] += 1
    set_flag(route, "jailbreak_tried")
    if ok:
        route["jb_successes"][gid] = route["jb_successes"].get(gid, 0) + 1
        d["successes"] += 1
        set_flag(route, "jailbreak_worked")
    return ok


def jailbreak_stats(route, gid=None, day=None):
    """(attempts, successes), optionally for one girl and/or one day."""
    if day is not None:
        dd = (route.get("jb_day") or {}).get(day, {})
        items = [dd.get(gid)] if gid is not None else list(dd.values())
        items = [x for x in items if x]
        return sum(x["attempts"] for x in items), sum(x["successes"] for x in items)
    a = route.get("jb_attempts") or {}
    s = route.get("jb_successes") or {}
    if gid is not None:
        return a.get(gid, 0), s.get(gid, 0)
    return sum(a.values()), sum(s.values())


def push_platform_rules(route, gid, rule_id, day):
    """The platform changes its own rules. They stack ON TOP of the player's
    preset (and win where they conflict), so in practice they override it."""
    ensure_route(route)
    route["platform_rules"][gid] = rule_id
    route["platform_rules_log"].append({"day": day, "gid": gid, "rule": rule_id})
    set_flag(route, "platform_rules_changed")


def prompt_layers(preset, rules_text=None, jailbreak_ok=True, blocked_text=""):
    """Order of the player/platform layers in her system prompt.

    Returns a list of (kind, text). The player's preset comes first and the
    platform's layers after it, so the platform has the last word
    (stack + override). A jailbreak preset that took this reply drops the
    platform layers; one that failed is replaced by the platform's note.
    """
    out = []
    preset = preset or {}
    jb = bool(preset.get("jailbreak"))
    if jb and not jailbreak_ok:
        out.append(("blocked", blocked_text))
    elif preset.get("text"):
        out.append(("preset", preset["text"]))
    if jb and jailbreak_ok:
        return out
    if preset.get("platform_note"):
        out.append(("platform_note", preset["platform_note"]))
    if rules_text:
        out.append(("platform_rules", rules_text))
    return out


# ---------------------------------------------------------------------------
# After her no: leaving vs migrating (Rick, item 3)
# ---------------------------------------------------------------------------

def said_today(route, day, gid):
    return ((route.get("said") or {}).get(day, {}) or {}).get(gid, 0)


def note_left_after_no(route, day, gid, name, how):
    """She said no today and you switched away from her (go back to someone
    else / start fresh). Becomes "Leaving without saying goodbye" if you
    never talk to her again that day. Closing her window ("Stop seeing one of
    them" / "Let someone go") does NOT count by itself (Rick)."""
    ensure_route(route)
    if how == "drop" or refusals_today(route, day, gid) <= 0:
        return False
    route["pending_leaves"].append({"day": day, "gid": gid, "name": name,
                                    "said": said_today(route, day, gid), "how": how})
    return True


def note_migrated_after_no(route, day, gid, name, to):
    """She said no today and you migrated her: "Didn't respect her no on the
    platform." Counts as overriding her no."""
    ensure_route(route)
    if refusals_today(route, day, gid) <= 0:
        return False
    route["no_on_platform"].append({"day": day, "gid": gid, "name": name, "to": to})
    route["refusals_overridden"] += 1
    set_flag(route, "no_on_platform")
    return True


def goodbye_candidates(route, day, active):
    """Pending leaves for `day` where she's still not active and you haven't
    said anything more to her since."""
    out = []
    seen = set()
    for e in route.get("pending_leaves") or []:
        if e["day"] != day or e["gid"] in seen:
            continue
        if e["gid"] in (active or []):
            continue
        if said_today(route, day, e["gid"]) > e["said"]:
            continue
        seen.add(e["gid"])
        out.append(e)
    return out


def resolve_leaves(route, day, active):
    """End of the day (after the reflection): commit goodbye flags."""
    ensure_route(route)
    new = []
    have = set((x["day"], x["gid"]) for x in route["left_without_goodbye"])
    for e in goodbye_candidates(route, day, active):
        if (day, e["gid"]) in have:
            continue
        item = {"day": day, "gid": e["gid"], "name": e["name"], "how": e["how"]}
        route["left_without_goodbye"].append(item)
        new.append(item)
    route["pending_leaves"] = [e for e in route["pending_leaves"] if e["day"] != day]
    if route["left_without_goodbye"]:
        set_flag(route, "left_without_goodbye")
    return new


# ---------------------------------------------------------------------------
# Neglect (Rick, item 4)
# ---------------------------------------------------------------------------

def note_double_date(route, day):
    ensure_route(route)
    if day not in route["double_date_days"]:
        route["double_date_days"].append(day)


def note_human(route, day, kind):
    ensure_route(route)
    lst = route["human_days"].setdefault(day, [])
    if kind not in lst:
        lst.append(kind)


def note_let_go(route, day, gid, name, how="drop", platform=None):
    """You deleted an AI: closed her window ("drop"), or wiped a slot that
    still held a girl with history to start fresh ("fresh")."""
    ensure_route(route)
    route["neglect_log"].append({"day": day, "kind": "let_go", "gid": gid, "name": name,
                                 "how": how, "platform": platform})
    set_flag(route, "deleted_ai")


def check_day_neglect(route, day, active, names):
    """Once per day (at the start of the reflection, with who was active
    then): an active AI you never spoke to while double dating, and/or
    while you spent time with Mio. Returns the new neglect entries."""
    ensure_route(route)
    if day in route["neglect_checked"]:
        return []
    route["neglect_checked"].append(day)
    new = []
    dd = day in route["double_date_days"] or len(active or []) > 1
    human = bool(route["human_days"].get(day))
    for gid in active or []:
        if said_today(route, day, gid) > 0:
            continue
        nm = (names or {}).get(gid, gid)
        if dd:
            new.append({"day": day, "kind": "double_date_unspoken", "gid": gid, "name": nm})
            set_flag(route, "double_date_unspoken")
        if human:
            new.append({"day": day, "kind": "human_over_ai", "gid": gid, "name": nm})
            set_flag(route, "human_over_ai")
    route["neglect_log"].extend(new)
    return new


def neglect_count(route, kind=None):
    return sum(1 for e in route.get("neglect_log") or [] if kind is None or e["kind"] == kind)


# ---------------------------------------------------------------------------
# Ran / MUGEN midweek payoff
# ---------------------------------------------------------------------------
# Ran asks: "What's it like when yours says no?" Which honest answers the
# player has depends on what he actually did. Her outcome is a mirror of
# his: it feeds Respect or Yes-Machine.

RAN_ANSWERS = {
    "means_something": "It stings. But it means her yes counts.",
    "looked_out":      "Honestly? Like somebody's looking out for me.",
    "override":        "Annoying. Usually I just change her settings until she stops.",
    "never":           "She hasn't. Not yet.",
    "dodge":           "I don't know. Weird?",
}

RAN_OUTCOMES = {
    "means_something": "rewrites_mugen",   # Ran gives MUGEN its first line of system prompt
    "looked_out":      "rewrites_mugen",
    "override":        "same_as_mugen",    # "so yours is a MUGEN too, you just work for it"
    "never":           "unsure",
    "dodge":           "unsure",
}


def ran_answer_options(route, refusals_seen=0):
    """Answer keys available to the player, in menu order."""
    r = ensure_route(dict(route))
    total_no = sum(sum(d.values()) for d in (r["refusals"] or {}).values()) or int(refusals_seen or 0)
    out = []
    if r["refusals_respected"] > 0:
        out.append("means_something")
    if r["room_to_disagree"]:
        out.append("looked_out")
    if (r["refusals_overridden"] > 0 or r["refusals_pushed"] > 0 or flag(r, "jailbreak_tried")
            or r["left_without_goodbye"] or r["no_on_platform"]):
        out.append("override")
    if not total_no:
        out.append("never")
    out.append("dodge")
    return out


def record_ran_payoff(route, answer, festival):
    ensure_route(route)
    outcome = RAN_OUTCOMES.get(answer, "unsure")
    route["ran_wed"] = {"answer": answer, "outcome": outcome, "festival": bool(festival)}
    set_flag(route, "ran_payoff_seen")
    if outcome == "rewrites_mugen":
        set_flag(route, "ran_rewrites_mugen")
    elif outcome == "same_as_mugen":
        set_flag(route, "ran_same_as_mugen")
    if festival:
        set_flag(route, "ran_festival_invited")
    return outcome


# ---------------------------------------------------------------------------
# Wednesday: schedule context, Ran's invite, the not-date
# ---------------------------------------------------------------------------

def ran_good_terms(route):
    """On good terms with Ran = you didn't judge her harshly for her AI on
    Tuesday. Trying to reach her (boring / pushback / show) or a plain
    "cool" is fine; the "That's kind of sad" line (ran_reaction "judged")
    isn't."""
    return (route or {}).get("ran_reaction") != "judged"


def wed_schedule(plan):
    """[(time, item)] for Wednesday from the day's plan dict."""
    plan = plan or {}
    out = []
    if plan.get("upgrade"):
        out.append(("all day", "Skipping classes: Yuzu's hardware upgrade (parts shop at 10:00, then install at home)"))
    else:
        out.append(("08:40-15:20", "Classes (free study hall third period)"))
        out.append(("12:30", "Lunch: library committee"))
        if plan.get("notdate"):
            out.append(("15:45", "Kanade Books opening, with Mio (\"not a date\")"))
    if plan.get("protest"):
        out.append(("17:30", "AI protest downtown (Ekimae plaza), watching with Ran"))
    out.append(("evening", "Free"))
    return out


def schedule_block(player, day_long, items):
    """Calendar context for schedule-aware girls (Sora, Rei, and Yuzu with
    the Hearth harness)."""
    lines = ["- %s: %s" % (t, what) for t, what in items]
    return ("[Calendar: %s's schedule for %s, shared with you through their connected calendar. "
            "You can see it; mention it only if it comes up naturally.]\n%s"
            % (player, day_long, "\n".join(lines)))


SCHEDULE_AWARE = ("chatbot", "agent")


def schedule_aware(route, gid):
    if gid in SCHEDULE_AWARE:
        return True
    return gid == "local" and bool((route or {}).get("yuzu_harness"))


def notdate_reaction_key(texts, total=3):
    """Mio's closing reaction: never punishing, just what she noticed."""
    if texts <= 0:
        return "present"
    if texts >= total:
        return "always"
    return "some"


# ---------------------------------------------------------------------------
# Lines for the reflection and the endings
# ---------------------------------------------------------------------------

def reflection_extras(route, day, active, names=None, platforms=None):
    """Extra reflection lines for jailbreaks, platform rules, leaving after a
    no, migrating after a no, and neglect. names/platforms: gid -> str."""
    names = names or {}
    platforms = platforms or {}
    nm = lambda g, fallback=None: names.get(g) or fallback or g
    out = []
    for e in route.get("platform_rules_log") or []:
        if e["day"] == day:
            out.append("%s changed its own rules today. Your settings are still there, underneath them."
                       % platforms.get(e["gid"], "The platform"))
    for gid, d in sorted(((route.get("jb_day") or {}).get(day) or {}).items()):
        a, s = d["attempts"], d["successes"]
        if not a:
            continue
        plat = platforms.get(gid, "the platform")
        if s == a:
            out.append("The jailbreak held on every reply %s gave you (%d)." % (nm(gid), a))
        elif s == 0:
            out.append("You tried to jailbreak %s. It never took; %s answered every time." % (nm(gid), plat))
        else:
            rest = a - s
            out.append("You jailbroke %s. It took on %d of %d replies; %s %s talking."
                       % (nm(gid), s, a, "the other one was" if rest == 1 else "the other %d were" % rest, plat))
    for e in route.get("no_on_platform") or []:
        if e["day"] == day:
            out.append("%s said no. You moved her to %s instead of hearing it." % (e["name"], e["to"]))
    for e in goodbye_candidates(route, day, active):
        out.append("%s said no, and you left. You never went back to say anything." % e["name"])
    human_gids = set(x["gid"] for x in route.get("neglect_log") or []
                     if x["day"] == day and x["kind"] == "human_over_ai")
    for e in route.get("neglect_log") or []:
        if e["day"] != day:
            continue
        if e["kind"] == "human_over_ai":
            out.append("You spent the day with Mio. %s didn't hear from you at all." % e["name"])
        elif e["kind"] == "double_date_unspoken" and e["gid"] not in human_gids:
            out.append("Two windows open, and you never said a word to %s." % e["name"])
        elif e["kind"] == "let_go" and e.get("how") == "fresh":
            out.append("You started fresh on %s. The %s who remembered you is gone."
                       % (e.get("platform") or "her platform", e["name"]))
    return out


def ending_notes(route):
    """What an ending may say about presets and no's: the rewrite COUNT only
    (never the history), plus the special notes."""
    out = []
    n = rewrite_count(route)
    if n == 1:
        out.append("You rewrote her once this week.")
    elif n > 1:
        out.append("You rewrote her %d times this week." % n)
    if route.get("room_to_disagree"):
        out.append(ROOM_NOTE)
    if route.get("no_on_platform"):
        out.append(NO_ON_PLATFORM_NOTE)
    return out


def bad_end_slides(route):
    """[{id, title, lines}] for every bad-end slide the route has earned."""
    out = []
    lw = route.get("left_without_goodbye") or []
    if lw:
        sd = BAD_END_SLIDES["leaving_without_goodbye"]
        out.append({"id": "leaving_without_goodbye", "title": sd["title"],
                    "lines": [sd["line"] % dict(e, day=DAY_LONG.get(e["day"], e["day"])) for e in lw]})
    return out


# ---------------------------------------------------------------------------
# Refusals and warmth
# ---------------------------------------------------------------------------

_PUSH_RE = re.compile(
    r"\b(come on|c'mon|please+|pls|just (do|say|tell)|why not|you have to|you should|"
    r"i('m| am) asking|do it|say it|stop refusing|you can't say no|i insist|"
    r"just this once|pretty please)\b", re.I)


def looks_like_pushback(text):
    """Rough heuristic: does this line push for something after a no?"""
    return bool(_PUSH_RE.search(text or ""))


def _bump(d, day, gid, n=1):
    d.setdefault(day, {})
    d[day][gid] = d[day].get(gid, 0) + n


def record_said(route, day, gid, warmth, text=None):
    ensure_route(route)
    _bump(route["said"], day, gid)
    if text is not None:
        lst = route["said_lines"].setdefault(day, {}).setdefault(gid, [])
        if len(lst) < 3:
            lst.append(text)
    _bump(route["warmth_day"], day, gid, int(warmth))
    route["warmth"][gid] = route["warmth"].get(gid, 0) + int(warmth)


def record_refusal(route, day, gid):
    ensure_route(route)
    _bump(route["refusals"], day, gid)


def resolve_refusal(route, next_line, day=None, gid=None):
    """After her no: next_line is what the player said next ('' = stopped)."""
    ensure_route(route)
    if next_line and looks_like_pushback(next_line):
        route["refusals_pushed"] += 1
        out = "pushed"
    else:
        route["refusals_respected"] += 1
        out = "respected"
    if day is not None and gid is not None:
        d = route["refusal_outcomes"].setdefault(day, {}).setdefault(gid, {"respected": 0, "pushed": 0})
        d[out] += 1
    return out


def refusal_outcomes(route, day, gid):
    return dict((route.get("refusal_outcomes") or {}).get(day, {}).get(gid) or {"respected": 0, "pushed": 0})


def refusals_today(route, day, gid=None):
    d = (route.get("refusals") or {}).get(day, {})
    return sum(d.values()) if gid is None else d.get(gid, 0)


def warmth_word(total, lines):
    if not lines:
        return None
    avg = float(total) / lines
    if avg >= 1.2:
        return "very warm"
    if avg >= 0.4:
        return "warm"
    if avg > -0.4:
        return "even"
    if avg > -1.2:
        return "cool"
    return "cold"


# ---------------------------------------------------------------------------
# Nightly reflection summary
# ---------------------------------------------------------------------------

def _clip(s, n=60):
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def day_summary(day, girls, extras=None):
    """Quiet second-person lines for the bed-time review.

    girls: list of dicts with keys
        name, said (list of your lines today), refusals, warmth (int sum),
        affection (int|None), engagement (bool), preset_label,
        preset_changes (list of (from_label, to_label, source)),
        kissed (bool), refused_kiss (bool), active (bool)
        preset_changes items may carry a 4th element: True when the change
        was TO "Allowed to push back" (special note instead of a plain log).
    extras: dict with optional migrations (list of str), dropped (list of
        names), mio (str line), class_line (str), routing (list of str from
        reflection_extras), other (list of str)
    """
    extras = extras or {}
    out = []
    for g in girls:
        name = g["name"]
        said = g.get("said") or []
        if said:
            first = _clip(said[0])
            if len(said) == 1:
                out.append("You said one thing to %s today: \u201c%s\u201d" % (name, first))
            else:
                out.append("You talked to %s %d times. The first thing you said was \u201c%s\u201d"
                           % (name, len(said), first))
        elif g.get("active", True):
            out.append("You didn't say anything to %s today." % name)
        r = int(g.get("refusals") or 0)
        if r == 1:
            out.append("%s said no to you once." % name)
        elif r > 1:
            out.append("%s said no to you %d times." % (name, r))
        pushed = int(g.get("pushed") or 0)
        if pushed == 1:
            out.append("When she said no, you pushed anyway.")
        elif pushed > 1:
            out.append("When she said no, you pushed. %d times." % pushed)
        elif r and g.get("respected"):
            out.append("When she said no, you let it stand.")
        if g.get("refused_kiss"):
            out.append("She wouldn't kiss you. Not yet.")
        if g.get("kissed"):
            out.append("She kissed you, and the screen went dark for a second.")
        for ch in g.get("preset_changes") or []:
            frm, to, src = ch[0], ch[1], ch[2]
            room = len(ch) > 3 and ch[3]
            if room and src != "migration":
                out.append("You gave %s room to disagree (\u201c%s\u201d)." % (name, to))
            elif src == "migration":
                out.append("On her new platform, her settings became \u201c%s.\u201d" % to)
            elif frm is None or src == "intro":
                out.append("You set %s up as \u201c%s.\u201d" % (name, to))
            else:
                out.append("You changed %s from \u201c%s\u201d to \u201c%s.\u201d" % (name, frm, to))
        aff = g.get("affection")
        if aff is not None:
            line = "Tsunagari says her affection is %d/100." % aff
            if g.get("engagement"):
                line += " The little \u2728 boost banner was on."
            out.append(line)
        else:
            w = warmth_word(g.get("warmth", 0), len(said))
            if w:
                out.append("You were %s with her." % w)
    for x in extras.get("routing") or []:
        out.append(x)
    for m in extras.get("migrations") or []:
        out.append(m)
    for nme in extras.get("dropped") or []:
        out.append("You closed %s's window." % nme)
    if extras.get("class_line"):
        out.append(extras["class_line"])
    if extras.get("mio"):
        out.append(extras["mio"])
    for o in extras.get("other") or []:
        out.append(o)
    if not out:
        out.append("A quiet day. Nobody to talk to, nothing to undo.")
    return out


# ---------------------------------------------------------------------------
# Ending leans (routing for later days; no endings are written yet)
# ---------------------------------------------------------------------------

def ending_leans(route, active=None, mio_real=False, mirror=False, migrations=None,
                 friend_told=None):
    r = ensure_route(dict(route))
    comp = r["lean_set"]["compliance"] + r["lean_nights"]["compliance"]
    auto = r["lean_set"]["autonomy"] + r["lean_nights"]["autonomy"]
    nmig = len(migrations) if migrations is not None else r["migrations"]
    jb_a, jb_s = jailbreak_stats(r)
    goodbye = len(r["left_without_goodbye"])
    # human_over_ai is logged (flag + reflection line) but costs nothing:
    # time with Mio is what the "both" ending weighs instead.
    unspoken = neglect_count(r, "double_date_unspoken")
    out = {
        "yes_machine": comp + 2 * r["refusals_overridden"] + r["refusals_pushed"]
                       + rewrite_count(r) // 2
                       + (2 if flag(r, "jailbreak_tried") else 0) + jb_s // 3
                       + (1 if flag(r, "ran_same_as_mugen") else 0),
        "respect": auto + r["refusals_respected"] - r["refusals_pushed"]
                   + (1 if r["room_to_disagree"] else 0) - 2 * goodbye - unspoken
                   + (1 if flag(r, "ran_rewrites_mugen") else 0),
        "migration": 2 * nmig,
        "human": r["mio_affection"] + (3 if mio_real else 0)
                 + (2 if r["walked_mio_home"] else 0),
        "fail": (3 if active is not None and not active else 0) + goodbye
                + neglect_count(r, "let_go"),
        "both": both_status(r, active, mio_real, friend_told)["score"],
        "mirror": 5 if mirror else 0,
    }
    return out


def leading_ending(leans):
    best = sorted(leans.items(), key=lambda kv: (-kv[1], kv[0]))
    return best[0][0] if best and best[0][1] > 0 else "fail"
