## routing.rpy — story-routing state and the glue around ks_story.py.
##
## `route` (saved with the game) tallies everything later days and endings
## branch on: presets chosen per girl and how often you rewrote her, her
## refusals and whether you respected or pushed past them, warmth, Mio
## affection, migrations and drops. See DESIGN.md "Story routing".

init -9 python:
    import ks_story

default route = ks_story.new_route()
default day_notes = []          # short lines scenes leave for tonight's reflection
default ks_jb_last = {}         # gid -> did the jailbreak take on her last reply?
default _ks_deleted_name = None # set between ks_note_fresh_delete and ks_mark_fresh_slot

init python:
    def ks_route():
        return ks_story.ensure_route(store.route)

    ## ── presets ──────────────────────────────────────────────────────────
    def ks_preset_id(gid):
        return ks_route()["presets"].get(gid)

    def ks_preset_obj(gid):
        pid = ks_preset_id(gid)
        return ks_story.get_preset(PRESETS, gid, pid) if pid else None

    def ks_preset_label(gid, pid=None):
        pid = pid if pid is not None else ks_preset_id(gid)
        return ks_story.preset_label(PRESETS, gid, pid)

    def ks_preset_family(gid):
        p = ks_preset_obj(gid)
        return p.get("family") if p else None

    def ks_surface(gid):
        return PRESET_SURFACE[gid][0]

    def ks_set_preset(gid, pid, source):
        """Apply a preset, tally it, and log it in her memory file."""
        r = ks_route()
        prev = r["presets"].get(gid)
        entry = ks_story.record_preset(r, PRESETS, gid, pid, store.day_name, source, prev)
        m = ks_mem(gid)
        if entry.get("room") and m.data is not None:
            m.log_event("room_to_disagree", day=store.day_name, source=source,
                        note=ks_story.ROOM_NOTE)
            m.set_flag("gave_room", True)
        if m.data is not None:
            m.set_flag("preset", pid)
            m.set_flag("preset_changes", ks_story.rewrite_count(r, gid))
            m.log_event("preset", day=store.day_name, preset=pid,
                        label=ks_preset_label(gid, pid), prev=prev, source=source,
                        lean=entry["lean"], rewrites=ks_story.rewrite_count(r, gid))
        return entry

    def ks_clear_preset(gid):
        ks_route()["presets"].pop(gid, None)

    def ks_convert_preset_on_migration(src, dst):
        """Migration rule (DESIGN.md): same preset family carries over to the
        new platform's surface; otherwise the new platform's default."""
        src_pid = ks_preset_id(src)
        pid, carried = ks_story.convert_preset(PRESETS, src, src_pid, dst, PRESET_DEFAULTS)
        ks_set_preset(dst, pid, "migration")
        return pid, carried

    ## ── chat bookkeeping ────────────────────────────────────────────────
    def ks_note_said(gid, text, warmth):
        ks_story.record_said(ks_route(), store.day_name, gid, warmth, text)

    def ks_note_refusal(gid, scene_id):
        ks_story.record_refusal(ks_route(), store.day_name, gid)
        ks_mem(gid).log_event("refusal", day=store.day_name, scene=scene_id)

    def ks_note_after_refusal(gid, next_line):
        out = ks_story.resolve_refusal(ks_route(), next_line, store.day_name, gid)
        ks_mem(gid).log_event("refusal_followup", day=store.day_name, outcome=out)
        return out

    def ks_note_override(gid, how):
        """A refusal today, then you set her to a compliance preset."""
        r = ks_route()
        if ks_story.refusals_today(r, store.day_name, gid) > 0:
            r["refusals_overridden"] += 1
            ks_mem(gid).log_event("override_after_no", day=store.day_name, how=how)

    def ks_note_left(gid, how, to=None):
        """You switched away from her / closed her window (Rick's item 3).

        * migrated her after a no today -> "Didn't respect her no on the
          platform" (counts as overriding her no);
        * otherwise, after a no today -> pending "Leaving without saying
          goodbye", committed at the end of the day if you never talk to her
          again (ks_story.resolve_leaves).
        Leaving when she hasn't said no today logs nothing extra.
        """
        r = ks_route()
        d = store.day_name
        if how == "migrate":
            if ks_story.note_migrated_after_no(r, d, gid, gname(gid), gplatform(to) if to else "?"):
                ks_mem(gid).log_event("no_on_platform", day=d, to=to,
                                      note=ks_story.NO_ON_PLATFORM_NOTE)
                ks_mem(gid).set_flag("no_on_platform", True)
        elif ks_story.note_left_after_no(r, d, gid, gname(gid), how):
            ks_mem(gid).log_event("left_after_no", day=d, how=how)

    def ks_resolve_day(day):
        """End of the day: commit goodbye flags into the route and her file."""
        for e in ks_story.resolve_leaves(ks_route(), day, store.active):
            m = ks_mem(e["gid"])
            m.log_event("left_without_goodbye", day=day, how=e["how"])
            m.set_flag("left_without_goodbye", True)

    def ks_check_neglect(day):
        names = dict((g, gname(g)) for g in GIRL_IDS)
        for e in ks_story.check_day_neglect(ks_route(), day, list(store.active), names):
            m = ks_mem(e["gid"])
            m.log_event(e["kind"], day=day)
            m.set_flag(e["kind"], True)

    def ks_note_human(kind):
        ks_story.note_human(ks_route(), store.day_name, kind)

    def ks_note_double_date():
        if len(store.active) > 1:
            ks_story.note_double_date(ks_route(), store.day_name)

    ## ── jailbreak + platform rules ──────────────────────────────────────
    def ks_jailbreak_rate():
        try:
            return float(ks_cfg().get("jailbreak_success_rate", ks_story.JAILBREAK_RATE))
        except (TypeError, ValueError):
            return ks_story.JAILBREAK_RATE

    def ks_jailbreak_roll(gid):
        """Roll for this reply if her preset is a jailbreak. None otherwise."""
        p = ks_preset_obj(gid)
        if not (p and p.get("jailbreak")):
            return None
        r = ks_route()
        ok = ks_story.jailbreak_roll(r, gid, store.day_name, ks_jailbreak_rate())
        store.ks_jb_last[gid] = ok
        a, s = ks_story.jailbreak_stats(r, gid)
        m = ks_mem(gid)
        if m.data is not None:
            m.log_event("jailbreak_roll", day=store.day_name, worked=ok, attempt=a)
            m.set_flag("jailbreak_attempts", a)
            m.set_flag("jailbreak_successes", s)
        return ok

    def ks_push_platform_rules(gid, rule_id):
        ks_story.push_platform_rules(ks_route(), gid, rule_id, store.day_name)
        m = ks_mem(gid)
        if m.data is not None:
            m.log_event("platform_rules", day=store.day_name, rule=rule_id,
                        preset=ks_preset_id(gid))
            m.set_flag("platform_rules", rule_id)

    def ks_note_migration(src, dst, name, how):
        r = ks_route()
        r["migrations"] += 1 if how == "migrate" else 0
        r["migration_log"].append({"day": store.day_name, "name": name,
                                   "from": gplatform(src), "to": gplatform(dst), "how": how})

    def ks_note_drop(gid):
        r = ks_route()
        r["drops"] += 1
        r["drop_log"].append({"day": store.day_name, "name": gname(gid)})
        ks_story.note_let_go(r, store.day_name, gid, gname(gid))
        ks_mem(gid).set_flag("let_go", True)
        ## Closing her window after a no is NOT "Leaving without saying
        ## goodbye" by itself (Rick): only switching away counts.

    def ks_note_fresh_delete(gid):
        """"Start fresh" over a slot that still holds a girl with history:
        that deletes her. Call BEFORE ks_reset_slot(gid)."""
        if not ks_has_history(gid):
            return False
        nm = gname(gid)
        plat = gplatform(gid).split(" (")[0]
        ks_story.note_let_go(ks_route(), store.day_name, gid, nm, "fresh", plat)
        m = ks_mem(gid)
        m.log_event("deleted", day=store.day_name, how="fresh", name=nm)
        m.set_flag("let_go", True)
        store._ks_deleted_name = nm
        return True

    def ks_mark_fresh_slot(gid):
        """After ks_reset_slot: the fresh file remembers who was deleted."""
        nm = getattr(store, "_ks_deleted_name", None)
        if nm:
            m = ks_mem(gid)
            m.log_event("deleted", day=store.day_name, how="fresh", name=nm)
            m.set_flag("previous_deleted", nm)
            store._ks_deleted_name = None

    def ks_sync_mio():
        ks_route()["mio_affection"] = store.mio_points

    def ks_leans():
        return ks_story.ending_leans(ks_route(), store.active, store.mio_real,
                                     any(store.mirror_flags.values()), store.migrations)
