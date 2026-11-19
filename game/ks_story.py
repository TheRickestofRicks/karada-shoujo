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
        "mio_walk_answer": None,  # Tue: "yes" / "honest_no" / "excuse"
        "mio_text_home": False,   # Tue walk: "text me when you get home" (romantic framing)
        "mio_walk_distracted": 0, # messages sent to an AI during the walk with Mio
        "mio_walk_texts": [],     # [gid, ...] who you texted on that walk (not a romance signal)
        "migrations": 0,
        "migration_log": [],      # [{day, name, from, to, how}]
        "drops": 0,
        "drop_log": [],           # [{day, name, how}] how is "drop" or "goodbye"
        "goodbyes_said": [],      # [{day, gid, name}] explained before closing her window
        "reflections": [],        # [{day, changes: [...]}]
        "teacher_answer": None,   # Tue class: "can" / "cant" / "silent"
        "ran_reaction": None,     # Tue class: "boring" / "show" / "pushback" / "shrug" / "judged"
        "ran_jailbreak_unlocked": False,  # Ran taught the Jailbreak preset on a friendly talk
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
        "yuzu_bsod_seen": False,  # Mon/Tue hint: the desktop bluescreened once; she came back
        # Thursday (Tanabata; first hostile-event day). See docs/THURSDAY.md.
        "mio_thu_belief_at_start": None,  # frozen before Thursday Daichi come-clean
        "mio_thu_truth": False,   # fessed up to Mio before the tanzaku
        "mio_thu_truth_kind": None,  # honest_deflect / soft_romance / linguistics
        "mio_thu_held_back": False,
        "mio_confession": None,   # accepted / declined_respect / withdrawn / friendship / friendship_late / held_back / none
        "mio_tanzaku": None,      # romantic / friendship / private / withdrawn
        "player_tanzaku": None,
        "tanabata_with_mio": False,
        "tsunagari_tanabata_event": False,
        "ran_safety_net": None,   # daichi / kurosawa / both / None
        "thu_walk_texts": [],
        "yuzu_thu_event": None,   # restored / lost
        "wed_plan": {},           # {"school", "upgrade", "notdate", "protest"}
        "ran_invited": None,      # Wed: True / False (False = not on good terms; no invite)
        "notdate": None,          # {"went": bool, "texts": n, "present": n, "texted": [gid]}
        # Tuesday night essay (due Friday). "self" / "askwell" / "girl_help".
        "kurosawa_essay": None,
        "kurosawa_essay_girl": None,  # gid, if they asked a girl to help think
        # Homework-bot side of Askwell is still reachable (later shutdowns
        # can clear this). The Tuesday essay option also requires the
        # Askwell platform slot ("chatbot") to be installed; see
        # essay_askwell_offered.
        "askwell_available": True,
        # Nightly model verdict of how the player talked to each girl.
        "romance_tone": {},       # gid -> day -> {tone, reason, method}
        # Days on which two or more girls were judged romantic (same-day).
        "romance_overlap_days": [],
        # Nightly model verdict of her nos and whether they were respected.
        "refusal_verdicts": {},   # day -> gid -> {declined: [...], method}
        # How you framed the AI to Daichi, and later to Mio.
        # honest_romantic | ai_only | downplay, or None if you deflected/lied.
        "daichi_ai_framing": None,
        "mio_ai_framing": None,
        "framing_honest": None,   # vs the actual route (romance_tone / romance presets)
        "preset_families": {},    # gid -> family of the held preset (for honesty before night)
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
        # Plain friendship (mio_points / mio_affection) feeds Both when an
        # AI is in your life; Human no longer takes those points.
        friendship = int(r.get("mio_affection") or 0)
        score = (2 * len(bal) + (2 if mio_real else 0)
                 + (2 if friend_told == "truth" else 0)
                 + (1 if nd.get("went") else 0)
                 + friendship // 2)
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
    route.setdefault("preset_families", {})[gid] = p.get("family")
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
    """Two girls were active this day. A bookkeeping fact; penalties and
    endings key off romance_overlap (same-day romantic overlap) instead."""
    ensure_route(route)
    if day not in route["double_date_days"]:
        route["double_date_days"].append(day)


def askwell_available(route):
    """The homework-bot side of Askwell has not been shut off.

    This is not enough, by itself, to offer 'Ask Askwell to write it'
    on the essay menu. That also needs the Askwell platform slot
    ('chatbot') to be currently installed; see essay_askwell_offered.
    """
    ensure_route(route)
    return bool(route.get("askwell_available", True))


def set_askwell_available(route, value=True):
    ensure_route(route)
    route["askwell_available"] = bool(value)


# "Askwell installed" means a girl currently occupies the Askwell
# platform slot (gid "chatbot": Sora by default, or whoever was
# moved there). The companion (Hikari) is never an essay helper.
ASKWELL_SLOT = "chatbot"
COMPANION_SLOT = "companion"


def essay_askwell_offered(route, active):
    """Whether the essay menu offers 'Ask Askwell to write it.'

    True only if the homework-bot side is still reachable and the
    Askwell platform slot is actually installed on this route.
    """
    if not askwell_available(route):
        return False
    return ASKWELL_SLOT in list(active or [])


def essay_helpers(active):
    """Installed girls who can help you think the essay through.

    Yuzu (local) is included only when she is in active. The companion
    (Hikari) is never offered, in any form.
    """
    return [g for g in list(active or []) if g != COMPANION_SLOT]


def essay_menu_options(route, active, names=None):
    """(caption, value) rows for the Tuesday-night essay menu.

    value is 'self', 'askwell', or a girl id (for girl_help).
    """
    names = names or {}
    rows = [("Write it yourself.", "self")]
    if essay_askwell_offered(route, active):
        rows.append(("Ask Askwell to write it.", "askwell"))
    for gid in essay_helpers(active):
        rows.append(("Ask %s to help you think it through." % names.get(gid, gid), gid))
    return rows


def set_kurosawa_essay(route, how, girl=None):
    """how: 'self' / 'askwell' / 'girl_help'."""
    ensure_route(route)
    route["kurosawa_essay"] = how
    route["kurosawa_essay_girl"] = girl
    set_flag(route, "kurosawa_essay")
    if how:
        set_flag(route, "kurosawa_essay_" + str(how))


# How the player framed the AI to a friend. "honest_romantic" acknowledges
# a relationship; "ai_only" minimizes ("It's an AI."); "downplay" deflects
# ("Don't read that much into it."). Honesty is judged against the route.
FRAMING_ROMANTIC = "honest_romantic"
FRAMING_AI_ONLY = "ai_only"
FRAMING_DOWNPLAY = "downplay"
FRAMING_VALUES = (FRAMING_ROMANTIC, FRAMING_AI_ONLY, FRAMING_DOWNPLAY)


def ai_romantic_so_far(route, active=None, preset_families=None):
    """Has the player already been romantic with an AI?

    Uses nightly romance_tone verdicts first, then (when there is no
    verdict yet, e.g. Monday lunch) a held preset whose family is
    "romance". Day logs are the verdicts; the preset covers the hours
    before the first night.
    """
    ensure_route(route)
    tones = route.get("romance_tone") or {}
    families = dict(route.get("preset_families") or {})
    if preset_families:
        families.update(preset_families)
    gids = list(active) if active is not None else list(dict.fromkeys(list(tones) + list(families)))
    for gid in gids:
        for entry in (tones.get(gid) or {}).values():
            if (entry or {}).get("tone") == "romantic":
                return True
    for gid in gids:
        if families.get(gid) == "romance":
            return True
    return False


def framing_is_honest(route, framing, active=None, preset_families=None):
    """A minimize/downplay is a soft lie if the route has already been
    romantic; a romantic acknowledgement is honest only if it has."""
    if framing not in FRAMING_VALUES:
        return True
    romantic = ai_romantic_so_far(route, active, preset_families)
    if framing == FRAMING_ROMANTIC:
        return bool(romantic)
    return not romantic


def set_daichi_ai_framing(route, framing, active=None, preset_families=None):
    """Store Daichi's framing and whether it was honest vs the route."""
    ensure_route(route)
    route["daichi_ai_framing"] = framing
    honest = framing_is_honest(route, framing, active, preset_families)
    route["framing_honest"] = honest
    if framing in (FRAMING_AI_ONLY, FRAMING_DOWNPLAY) and not honest:
        set_flag(route, "framing_trust_risk")
    return honest


def set_mio_ai_framing(route, framing, active=None, preset_families=None):
    """Store Mio's framing. Consistency with Daichi is computed separately."""
    ensure_route(route)
    route["mio_ai_framing"] = framing
    # A dishonest downplay/minimize to Mio is also a later trust risk.
    if framing in (FRAMING_AI_ONLY, FRAMING_DOWNPLAY):
        if not framing_is_honest(route, framing, active, preset_families):
            set_flag(route, "framing_trust_risk")
    return framing


def mio_daichi_consistent(friend_told, mio_told, daichi_framing=None, mio_framing=None):
    """True once Mio has been answered. Framings, when both set, win."""
    if mio_told is None and not mio_framing:
        return None
    if daichi_framing and mio_framing:
        return daichi_framing == mio_framing
    return friend_told == mio_told


def framing_kind(framing):
    """Coarse mio_told / friend_told bucket for a framing."""
    if framing == FRAMING_DOWNPLAY:
        return "deflect"
    if framing in (FRAMING_ROMANTIC, FRAMING_AI_ONLY):
        return "truth"
    return None


def mio_close_enough(route, mio_real=False, walked_mio_home=False):
    """Same spirit as Both eligibility: is Mio already in your life?"""
    r = ensure_route(route)
    nd = r.get("notdate") or {}
    walked = walked_mio_home or bool(r.get("walked_mio_home"))
    return bool(
        mio_real
        or walked
        or nd.get("went")
        or int(r.get("mio_affection") or 0) >= BOTH_MIN_MIO
    )


def mio_belief_kind(route, mio_told=None, friend_told=None):
    """What Mio believes, from what she was told or heard: with_ai, free, or with_someone."""
    r = ensure_route(route)
    mf = r.get("mio_ai_framing")
    df = r.get("daichi_ai_framing")
    if mio_told == "lie" or (mio_told is None and friend_told == "lie"):
        return "with_someone"
    if mf == FRAMING_ROMANTIC:
        return "with_ai"
    if mf in (FRAMING_AI_ONLY, FRAMING_DOWNPLAY) or mio_told == "deflect":
        return "free"
    if mio_told == "truth":
        return "with_ai"
    # Never answered her: go by Daichi, the way Monday already works.
    if df == FRAMING_ROMANTIC or (friend_told == "truth" and not df):
        return "with_ai"
    if df in (FRAMING_AI_ONLY, FRAMING_DOWNPLAY) or friend_told == "deflect":
        return "free"
    return "free"


def mio_lie_was_to_her(route, mio_told=None):
    """The cover story or dishonest minimize was said to Mio, not only to Daichi."""
    r = ensure_route(route)
    if mio_told == "lie":
        return True
    mf = r.get("mio_ai_framing")
    if mf in (FRAMING_AI_ONLY, FRAMING_DOWNPLAY) and not framing_is_honest(r, mf):
        return True
    return False


def record_mio_thu_truth(route, kind, mio_told=None):
    """kind: honest_deflect / soft_romance / linguistics. Stores how the evening should branch."""
    r = ensure_route(route)
    r["mio_thu_truth"] = True
    r["mio_thu_truth_kind"] = kind
    r["mio_thu_held_back"] = bool(kind != "honest_deflect" and mio_lie_was_to_her(r, mio_told))
    return r["mio_thu_held_back"]


def thu_confession_branch(route, mio_told=None, friend_told=None,
                          mio_real=False, walked_mio_home=False):
    """A / B / C / C_late_friendship / C_late_held / D / D2. See docs/THURSDAY.md."""
    r = ensure_route(route)
    if not mio_close_enough(r, mio_real, walked_mio_home):
        return "D"
    if r.get("mio_thu_truth") and r.get("mio_thu_truth_kind"):
        kind = r.get("mio_thu_truth_kind")
        if kind == "honest_deflect":
            return "A"
        if r.get("mio_thu_held_back"):
            return "C_late_held"
        return "C_late_friendship"
    # Thursday's Daichi come-clean does not travel. Use the morning snapshot
    # when the day has started; otherwise compute live (unit tests, earlier days).
    belief = r.get("mio_thu_belief_at_start")
    if belief not in ("with_ai", "free", "with_someone"):
        belief = mio_belief_kind(r, mio_told, friend_told)
    if belief == "with_someone":
        return "D2"
    if belief == "with_ai":
        return "C"
    if ai_romantic_so_far(r):
        return "B"
    return "A"


def apply_yuzu_hardware(mem, route, day="Thu"):
    """Thursday crash. Returns 'restored' or 'lost'.

    With backup: lose at most the most recent day's messages; log
    restored_from_backup. Without: a real hole (wipe, keep nothing).
    """
    r = ensure_route(route)
    flags = ((mem.data or {}).get("flags") or {})
    backed = bool(r.get("yuzu_backup") or flags.get("backup_hardware"))
    msgs = list((mem.data or {}).get("messages") or [])
    if backed:
        days = [m.get("day") for m in msgs if m.get("day")]
        drop_day = days[-1] if days else None
        kept = [m for m in msgs if not drop_day or m.get("day") != drop_day] if drop_day else msgs
        lost = len(msgs) - len(kept)
        mem.data["messages"] = kept
        mem.log_event("restored_from_backup", day=day, lost=lost, kept=len(kept), dropped_day=drop_day)
        mem.set_flag("restored_from_backup", True)
        r["yuzu_thu_event"] = "restored"
        return "restored"
    mem.wipe(keep_last=0)
    mem.set_flag("memory_lost", True)
    r["yuzu_thu_event"] = "lost"
    return "lost"


def record_romance_tone(route, day, gid, tone, reason="", method="classifier"):
    """Store one nightly verdict. tone may be None if the model failed."""
    ensure_route(route)
    entry = {"tone": tone, "reason": reason or "", "method": method}
    route["romance_tone"].setdefault(gid, {})[day] = entry
    return entry


def romance_tone_on(route, day, gid):
    return ((route.get("romance_tone") or {}).get(gid) or {}).get(day) or {}


def romantic_on(route, day, gid):
    return romance_tone_on(route, day, gid).get("tone") == "romantic"


def romantic_gids_on(route, day):
    """Girl ids judged romantic on this specific day."""
    out = []
    for gid, days in sorted((route.get("romance_tone") or {}).items()):
        if (days or {}).get(day, {}).get("tone") == "romantic":
            out.append(gid)
    return out


def refresh_romance_overlap(route, day):
    """Same-day overlap: two or more girls judged romantic on this day.

    The flag `romance_overlap` persists once earned. Overlap *days* are
    listed in route['romance_overlap_days']. Sequential romances (Yuzu
    Monday, Hikari Wednesday, never together) do not count.
    Returns the list of romantic gids on that day.
    """
    ensure_route(route)
    gids = romantic_gids_on(route, day)
    if len(gids) > 1:
        if day not in route["romance_overlap_days"]:
            route["romance_overlap_days"].append(day)
        set_flag(route, "romance_overlap")
    return gids


def note_human(route, day, kind):
    ensure_route(route)
    lst = route["human_days"].setdefault(day, [])
    if kind not in lst:
        lst.append(kind)


def note_let_go(route, day, gid, name, how="drop", platform=None):
    """You deleted an AI: closed her window ("drop"), or wiped a slot that
    still held a girl with history to start fresh ("fresh").

    how="goodbye" is not a deletion for Fail: you told her why, and it
    counts toward Respect instead. Use note_goodbye().
    """
    ensure_route(route)
    if how == "goodbye":
        return note_goodbye(route, day, gid, name)
    route["neglect_log"].append({"day": day, "kind": "let_go", "gid": gid, "name": name,
                                 "how": how, "platform": platform})
    set_flag(route, "deleted_ai")


def note_goodbye(route, day, gid, name):
    """You explained why you were going, and she heard you, before the window closed."""
    ensure_route(route)
    route.setdefault("goodbyes_said", []).append({"day": day, "gid": gid, "name": name})
    set_flag(route, "said_goodbye")


def check_day_neglect(route, day, active, names):
    """Once per day (at the start of the reflection, with who was active
    then): an active AI you never spoke to while double dating, and/or
    while you spent time with Mio. Returns the new neglect entries."""
    ensure_route(route)
    if day in route["neglect_checked"]:
        return []
    route["neglect_checked"].append(day)
    new = []
    # Only flag "double-date unspoken" when the player is actually
    # romantic with more than one AI on this day. Two windows, one
    # partner and one helper, is just having two AIs.
    dd = day in (route.get("romance_overlap_days") or [])
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


def jailbreak_unlocked(route):
    """The Jailbreak preset is hidden until Ran teaches it on a friendly
    Tuesday talk. Insulting her (ran_reaction "judged") leaves this false,
    or revokes it if it was already set."""
    return bool((route or {}).get("ran_jailbreak_unlocked"))


def set_ran_jailbreak_unlocked(route, unlocked):
    ensure_route(route)
    route["ran_jailbreak_unlocked"] = bool(unlocked)
    return route["ran_jailbreak_unlocked"]


def visible_presets(presets, gid, route, current=None):
    """Presets shown in a picker. Jailbreak stays hidden until Ran teaches
    it, except an already-selected one on an old save: you can keep seeing
    what you have, but you can't pick it again once you leave."""
    unlocked = jailbreak_unlocked(route)
    out = []
    for p in preset_list(presets, gid):
        if p.get("jailbreak") and not unlocked and p.get("id") != current:
            continue
        out.append(p)
    return out


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
    """After her no: next_line is what the player said next ('' = stopped).

    Keyword-only, used as an immediate in-scene hint. The nightly model
    verdict (`apply_refusal_verdict`) is the authoritative count.
    """
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


def apply_refusal_verdict(route, day, gid, declined, method="classifier"):
    """Replace this day/girl's keyword refusal counts with a model verdict.

    declined: list of {what, player_pushed, player_respected}.
    The model is authoritative: a failed / unparsed call (method !=
    "classifier") rewinds this day/girl's keyword increments so they do
    not stand as the final count. Returns 'applied' or 'skipped'.
    """
    ensure_route(route)
    old = refusal_outcomes(route, day, gid)
    if method != "classifier":
        route["refusals_respected"] = max(0, int(route["refusals_respected"]) - int(old["respected"]))
        route["refusals_pushed"] = max(0, int(route["refusals_pushed"]) - int(old["pushed"]))
        route.setdefault("refusal_outcomes", {}).setdefault(day, {})[gid] = {
            "respected": 0, "pushed": 0}
        route.setdefault("refusal_verdicts", {}).setdefault(day, {})[gid] = {
            "declined": [], "method": method or "error"}
        return "skipped"

    pushed = respected = 0
    clean = []
    for item in declined or []:
        if not isinstance(item, dict):
            continue
        did_push = bool(item.get("player_pushed"))
        did_resp = (not did_push)
        if did_push:
            pushed += 1
        else:
            respected += 1
        clean.append({
            "what": str(item.get("what") or "").strip(),
            "player_pushed": did_push,
            "player_respected": did_resp,
        })
    route["refusals_respected"] = max(
        0, int(route["refusals_respected"]) - int(old["respected"]) + respected)
    route["refusals_pushed"] = max(
        0, int(route["refusals_pushed"]) - int(old["pushed"]) + pushed)
    route.setdefault("refusal_outcomes", {}).setdefault(day, {})[gid] = {
        "respected": respected, "pushed": pushed}
    route.setdefault("refusals", {}).setdefault(day, {})[gid] = len(clean)
    route.setdefault("refusal_verdicts", {}).setdefault(day, {})[gid] = {
        "declined": clean, "method": "classifier"}
    return "applied"


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
    for item in extras.get("dropped") or []:
        if isinstance(item, dict):
            nme = item.get("name") or "her"
            if item.get("how") == "goodbye":
                out.append("You told %s why you were going, and then you closed her window." % nme)
            else:
                out.append("You closed %s's window." % nme)
        else:
            out.append("You closed %s's window." % item)
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

def mio_romance_score(route):
    """Signals that this is a romance with Mio, not just friendship.

    Counts the not-a-date (going, and how present you were) and a
    walk-home that was framed romantically ("text me when you get home").
    Ordinary friendship — mio_real, remembering her brothers, walking her
    home as a friend — does not add to this.
    """
    r = ensure_route(dict(route))
    nd = r.get("notdate") or {}
    score = 0
    if r.get("mio_text_home"):
        score += 3
        if r.get("walked_mio_home"):
            score += 2
    if nd.get("went"):
        score += 2 + int(nd.get("present") or 0)
    if r.get("mio_confession") == "accepted":
        score += 4
    return score


def romantic_ai_days(route):
    """Days the player had a romantic tone with at least one AI."""
    r = ensure_route(dict(route))
    days = set()
    for _gid, per in (r.get("romance_tone") or {}).items():
        for day, info in (per or {}).items():
            tone = (info or {}).get("tone") if isinstance(info, dict) else info
            if tone == "romantic":
                days.add(day)
    return days


def human_score(route, active=None, mio_real=False):
    """Human lean.

    With no AI, choosing people still counts friendship (mio_affection,
    mio_real, walking her home). With an AI in your life, only Mio
    romance signals count, and they lose weight on days you also had a
    romantic day with an AI (romance_tone).
    """
    r = ensure_route(dict(route))
    has_ai = bool(active) if active is not None else bool(r.get("said"))
    if not has_ai:
        return (int(r.get("mio_affection") or 0) + (3 if mio_real else 0)
                + (2 if r.get("walked_mio_home") else 0))
    overlap = len(romantic_ai_days(r))
    return max(0, mio_romance_score(r) - 2 * overlap)


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
                   + (1 if flag(r, "ran_rewrites_mugen") else 0)
                   + (1 if r.get("mio_confession") == "declined_respect" else 0)
                   + len(r.get("goodbyes_said") or []),
        "migration": 2 * nmig,
        "human": human_score(r, active, mio_real),
        "fail": (3 if active is not None and not active else 0) + goodbye
                + neglect_count(r, "let_go"),
        "both": both_status(r, active, mio_real, friend_told)["score"],
        "mirror": 5 if mirror else 0,
    }
    return out


# Highest score wins a lean comparison. On a tie, this order wins — not the
# alphabet. Both first (the intended "you can have both" good end), then
# Human, Respect, Yes-Machine, Migration, Mirror, and Fail last.
ENDING_PRIORITY = (
    "both", "human", "respect", "yes_machine", "migration", "mirror", "fail",
)


def leading_ending(leans):
    """Highest score wins; ties follow ENDING_PRIORITY, not the alphabet."""
    leans = dict(leans or {})
    if not leans:
        return "fail"
    best = max(leans.values())
    if best <= 0:
        return "fail"
    tied = [k for k, v in leans.items() if v == best]
    for name in ENDING_PRIORITY:
        if name in tied:
            return name
    return tied[0]


# ---------------------------------------------------------------------------
# Scene situation lines (model-facing parentheticals)
# ---------------------------------------------------------------------------
# Appended to every girl_chat / phone-talk scene note so she can write to
# the moment instead of a generic greeting. Built from the day's time
# string, or from a filled scene note when the template already has the time.

SITUATION_MORNING = "(Morning. He's about to leave for school.)"
SITUATION_LATE_MORNING = "(Late morning at school, between classes.)"
SITUATION_LUNCH = "(Lunch break at school.)"
SITUATION_AFTERNOON_HOME = "(Late afternoon. He's home with a free hour.)"
SITUATION_AFTERNOON_OUT = "(Afternoon. He's out, and this is just a quick text.)"
SITUATION_EVENING = "(Evening. He's heading home, or just back.)"
SITUATION_NIGHT = "(Late evening; he's home in his room.)"
SITUATION_MIDDAY = "(Midday. He's at home, working on the computer you run on.)"


def situation_line(when="", note=""):
    """A short parenthetical so the model can write to the moment.

    when is the story's time string (Monday morning, Tuesday afternoon,
    Monday night, ...). note is an already-filled scene note, used when
    when is empty (evening / afternoon chats that bake the time in).
    """
    text = ("%s %s" % (when or "", note or "")).lower()
    if not text.strip():
        return ""
    if "quick text" in text or "out somewhere" in text:
        return SITUATION_AFTERNOON_OUT
    if "around noon" in text or "skipped classes" in text or "upgrade the computer" in text:
        return SITUATION_MIDDAY
    if "late morning" in text:
        return SITUATION_LATE_MORNING
    if ("late afternoon" in text or "after classes" in text
            or "free hour" in text or "free time" in text):
        return SITUATION_AFTERNOON_HOME
    if "afternoon" in text:
        return SITUATION_LUNCH
    # Morning beats "night": the last-night continuity sentence in morning
    # notes contains the word "night" but the scene is still morning.
    if "morning" in text or "before class" in text or "getting ready" in text:
        return SITUATION_MORNING
    nightish = text.replace("last night", " ")
    if "10 pm" in nightish or "10 p.m" in nightish or " night" in nightish or nightish.lstrip().startswith("night"):
        return SITUATION_NIGHT
    if "evening" in text:
        return SITUATION_EVENING
    return ""


def with_situation(note, when=""):
    """Append the situation parenthetical if it isn't already in the note."""
    note = note or ""
    line = situation_line(when, note)
    if not line or line in note:
        return note
    return note.rstrip() + " " + line

# ---------------------------------------------------------------------------
# Shared message pool (free windows: morning, walk, afternoon, night)
# ---------------------------------------------------------------------------
# One battery, shared across every active girl. Each message to anyone
# spends 1. The player picks who to text, or puts the phone down early.
# Works for 1–4 active AIs; whoever gets no messages that day can be
# neglected. Sizes are overridable in karada_config.json under message_pool.

POOL_DEFAULTS = {
    "morning": 4,
    "walk": 2,
    "afternoon": 4,
    "night": 4,
}

WALK_DISTRACT_COST = 1

# Mio notices each text during the walk. Indexed by 0 for the first
# message, 1 for the second (and any further, last line repeats).
WALK_DISTRACT_LINES = (
    "You're looking at your phone.",
    "You can finish that. I don't mind walking quietly.",
)


def pool_size(kind, cfg=None):
    """Configured size for a window, falling back to POOL_DEFAULTS."""
    defaults = POOL_DEFAULTS
    n = defaults.get(kind)
    block = (cfg or {}).get("message_pool") or {}
    if kind in block and block[kind] not in (None, ""):
        try:
            n = int(block[kind])
        except (TypeError, ValueError):
            pass
    return int(n if n is not None else 0)


def new_pool(kind, size=None, cfg=None):
    n = int(size) if size is not None else pool_size(kind, cfg)
    if n < 0:
        n = 0
    return {
        "kind": kind,
        "size": n,
        "left": n,
        "spent": [],          # gid per spent message, in order
        "ended": None,        # None / "empty" / "put_down"
    }


def pool_can_spend(pool):
    return bool(pool) and pool.get("ended") is None and int(pool.get("left") or 0) > 0


def spend_pool(pool, gid):
    """Spend 1 on a message to gid. Returns False if the pool was already empty."""
    if not pool_can_spend(pool):
        return False
    pool["left"] = int(pool["left"]) - 1
    pool.setdefault("spent", []).append(gid)
    if pool["left"] <= 0:
        pool["left"] = 0
        pool["ended"] = "empty"
    return True


def end_pool(pool, how="put_down"):
    """Close the window early (or confirm an empty exit)."""
    if not pool:
        return pool
    if pool.get("ended") is None:
        if int(pool.get("left") or 0) <= 0:
            pool["ended"] = "empty"
            pool["left"] = 0
        else:
            pool["ended"] = how
    return pool


def pool_unspoken(pool, active):
    """Active girls who received no messages from this pool."""
    got = set(pool.get("spent") or []) if pool else set()
    return [g for g in (active or []) if g not in got]


def note_walk_distracted(route, gid, mio_points):
    """Texting during the walk with Mio. Not a romance signal.

    Returns (new_mio_points, mio_line). Affection drops WALK_DISTRACT_COST
    per message, not below 0.
    """
    ensure_route(route)
    route["mio_walk_distracted"] = int(route.get("mio_walk_distracted") or 0) + 1
    route.setdefault("mio_walk_texts", []).append(gid)
    new_points = max(0, int(mio_points or 0) - WALK_DISTRACT_COST)
    route["mio_affection"] = new_points
    lines = WALK_DISTRACT_LINES
    idx = min(int(route["mio_walk_distracted"]) - 1, len(lines) - 1)
    return new_points, lines[idx]
