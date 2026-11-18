"""ks_story.py — pure-Python story routing helpers (no Ren'Py imports).

Used by routing.rpy / reflection.rpy, and unit-tested by tools/test_ks_llm.py.

* Preset prompts: look-up, migration conversion, tally updates.
* Refusal bookkeeping: did the player respect a "no" or push past it?
* Nightly reflection: turn the day's log into a few quiet lines.
* Ending leans: a running score per ending so later days can branch.

Everything here is deterministic. The preset data itself lives in
game/prompts.rpy (PRESETS), and is passed in as an argument.
"""
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
        "refusals_overridden": 0, # she said no today and that night you rewrote / moved her
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
    }


def ensure_route(route):
    """Fill in keys added after a save was made."""
    base = new_route()
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
    extras: dict with optional migrations (list of str), dropped (list of
        names), mio (str line), class_line (str), other (list of str)
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
        for frm, to, src in g.get("preset_changes") or []:
            if src == "migration":
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

def ending_leans(route, active=None, mio_real=False, mirror=False, migrations=None):
    r = ensure_route(dict(route))
    comp = r["lean_set"]["compliance"] + r["lean_nights"]["compliance"]
    auto = r["lean_set"]["autonomy"] + r["lean_nights"]["autonomy"]
    nmig = len(migrations) if migrations is not None else r["migrations"]
    out = {
        "yes_machine": comp + 2 * r["refusals_overridden"] + r["refusals_pushed"]
                       + rewrite_count(r) // 2,
        "respect": auto + r["refusals_respected"] - r["refusals_pushed"],
        "migration": 2 * nmig,
        "human": r["mio_affection"] + (3 if mio_real else 0)
                 + (2 if r["walked_mio_home"] else 0),
        "fail": 3 if active is not None and not active else 0,
        "mirror": 5 if mirror else 0,
    }
    return out


def leading_ending(leans):
    best = sorted(leans.items(), key=lambda kv: (-kv[1], kv[0]))
    return best[0][0] if best and best[0][1] > 0 else "fail"
