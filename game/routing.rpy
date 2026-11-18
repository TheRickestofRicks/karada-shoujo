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
        """A refusal today, then that night you rewrote / moved her."""
        r = ks_route()
        if ks_story.refusals_today(r, store.day_name, gid) > 0:
            r["refusals_overridden"] += 1
            ks_mem(gid).log_event("override_after_no", day=store.day_name, how=how)

    def ks_note_migration(src, dst, name, how):
        r = ks_route()
        r["migrations"] += 1 if how == "migrate" else 0
        r["migration_log"].append({"day": store.day_name, "name": name,
                                   "from": gplatform(src), "to": gplatform(dst), "how": how})

    def ks_note_drop(gid):
        r = ks_route()
        r["drops"] += 1
        r["drop_log"].append({"day": store.day_name, "name": gname(gid)})

    def ks_sync_mio():
        ks_route()["mio_affection"] = store.mio_points

    def ks_leans():
        return ks_story.ending_leans(ks_route(), store.active, store.mio_real,
                                     any(store.mirror_flags.values()), store.migrations)
