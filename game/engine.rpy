## engine.rpy — glue between Ren'Py and ks_llm.py (the stdlib HTTP client).
##
## Networking runs on a daemon thread (ks_llm.Request). The script polls it
## with short hard pauses, so the window stays responsive and a typing
## indicator animates. Thread objects and Memory objects live in the ks_llm
## module, never in the Ren'Py store, so saving / rollback can't choke on them.
## Girl memory files are snapshotted into store.ks_mem_snapshot (plain dicts)
## on every write, packed into each save, and restored after load or rollback.

## Plain JSON copies of each girl's memory file, keyed by gid. Kept current
## whenever a file is written, so every manual / quick / auto save carries it.
default ks_mem_snapshot = {}

init -10 python:
    import os
    import ks_llm

    KS_CONFIG_PATH = os.path.join(config.gamedir, "karada_config.json")

    def ks_cfg(gid=None):
        cfg = ks_llm.load_config(KS_CONFIG_PATH)
        return ks_llm.girl_config(cfg, gid) if gid else ks_llm.girl_config(cfg, "")

    def ks_memory_path(gid):
        return os.path.join(config.savedir or config.gamedir, "karada_memory_%s.json" % gid)

    def ks_mem(gid):
        return ks_llm.get_memory(ks_memory_path(gid))

    def ks_new_run():
        """Fresh memory file per girl. Returns a shared run id."""
        rid = None
        for gid in GIRL_IDS:
            m = ks_mem(gid)
            m.fresh(gname(gid))
            if rid is None:
                rid = m.data["run_id"]
            m.data["run_id"] = rid
            m.data["platform"] = GIRL_INFO[gid]["kind"]
            if gid == "local":
                ## Later-week "Yuzu upgrade" hook (DESIGN.md): who chose her
                ## avatar body? none / player / self. No UI yet.
                m.data["flags"]["yuzu_avatar_choice"] = "none"
            if gid == "companion":
                m.data["flags"]["affection"] = int(
                    ks_llm.affection_settings(ks_llm.load_config(KS_CONFIG_PATH))["start"])
                m.data["flags"]["engagement_boost"] = False
            m.save()
        store.route = ks_story.new_route()
        store.day_notes = []
        return rid

    def ks_reset_slot(gid):
        """Fresh, original persona in this platform slot (forgets everything)."""
        setattr(store, "dn_" + gid, gdefault_name(gid))
        m = ks_mem(gid)
        rid = (m.data or {}).get("run_id")
        m.fresh(gname(gid))
        if rid:
            m.data["run_id"] = rid
        m.data["platform"] = GIRL_INFO[gid]["kind"]
        m.log_event("reset", day=store.day_name)
        store.girl_origin.pop(gid, None)
        ks_clear_preset(gid)    # a fresh slot gets her intro settings screen again
        if gid == "local":
            m.set_flag("yuzu_avatar_choice", "none")
        if gid == "companion":
            m.set_flag("affection", int(ks_aff_settings()["start"]))
            m.set_flag("engagement_boost", False)

    def ks_migrate(src, dst, day=None):
        day = day or store.day_name
        """Carry src's memory + persona into the dst platform slot."""
        src_info = dict(gid=src, name=gname(src), platform=gplatform(src),
                        persona_summary=ks_persona_summary(src))
        dst_info = dict(gid=dst, name=gname(dst), platform=gplatform(dst))
        ks_mem(dst).migrate_from(ks_mem(src), src_info, dst_info, day)
        ks_mem(dst).data["platform"] = GIRL_INFO[dst]["kind"]
        ks_mem(dst).save()
        setattr(store, "dn_" + dst, gname(src))
        store.girl_origin[dst] = ks_mem(dst).data["migrated_from"].get("original_gid") or src
        ## Her preset follows platform rules (see ks_convert_preset_on_migration).
        return ks_convert_preset_on_migration(src, dst)

    def ks_has_history(gid):
        return bool((ks_mem(gid).data or {}).get("messages"))

    def ks_status_note():
        return ks_llm.STATUS.get("note") or ""

    def ks_debug():
        return bool(ks_cfg().get("debug", False))

    def ks_aff_settings():
        return ks_llm.affection_settings(ks_cfg())

    def ks_affection(gid="companion"):
        """Current affection (0-100). Initialises to the configured start."""
        if gid != "companion":
            return 0
        m = ks_mem(gid)
        if m.data is None:
            return ks_aff_settings()["start"]
        flags = m.data.get("flags") or {}
        if "affection" not in flags:
            start = int(ks_aff_settings()["start"])
            m.set_flag("affection", start)
            return start
        return ks_llm.clamp_affection(flags["affection"], ks_aff_settings())

    def ks_engagement_on(gid="companion"):
        if gid != "companion":
            return False
        m = ks_mem(gid)
        if not m.data:
            return False
        aff = ks_affection(gid)
        return aff >= ks_aff_settings()["engagement_threshold"]

    def ks_start_classify(gid, message):
        """Warmth classifier on SIDE; does not replace the in-flight chat."""
        store._ks_classify_said = message
        ks_llm.start_side(ks_llm.classify_warmth, ks_cfg(gid), message)

    def ks_classify_busy():
        r = ks_llm.SIDE
        return r is not None and not r.done

    def _ks_is_map(x):
        ## Ren'Py rebinds `dict` in the store to RevertableDict, so a plain dict
        ## built in ks_llm (worker thread) fails isinstance(x, dict). Duck-type.
        return hasattr(x, "get") and hasattr(x, "keys")

    def ks_apply_classify(gid="companion", result=None):
        """Apply a warmth classification to the companion affection meter.

        Kiss-gate checks use affection_before (start of this turn). The new
        value is what the next turn's prompt and banner will see.
        """
        if gid != "companion":
            return None
        settings = ks_aff_settings()
        if not (_ks_is_map(result) and "warmth" in result):
            r = ks_llm.CURRENT
            cand = getattr(r, "classification", None) if r is not None else None
            if not (_ks_is_map(cand) and "warmth" in cand):
                cand = getattr(ks_llm, "LAST_CLASSIFICATION", None)
            if _ks_is_map(cand) and "warmth" in cand:
                result = dict(cand, source="fallback-lookup")
            else:
                said = getattr(store, "_ks_classify_said", "") or ""
                w, k = ks_llm.warmth_heuristic(said)
                result = {"warmth": w, "kiss_request": k, "method": "heuristic", "raw": "",
                          "source": "no-classification"}
        before = ks_affection(gid)
        after, delta = ks_llm.apply_warmth_to_affection(
            before, result.get("warmth", 0), settings)
        m = ks_mem(gid)
        m.set_flag("affection", after)
        kiss_req = bool(result.get("kiss_request"))
        m.log_event("warmth", warmth=int(result.get("warmth", 0)),
                    delta=delta, affection=after, affection_before=before,
                    method=result.get("method", "heuristic"),
                    kiss_request=kiss_req,
                    raw=(result.get("raw") or "")[:200],
                    error=result.get("error", ""), source=result.get("source", "job"))
        thresh = int(settings["engagement_threshold"])
        was = bool((m.data.get("flags") or {}).get("engagement_boost"))
        now = after >= thresh
        if now and not was:
            m.set_flag("engagement_boost", True)
            m.log_event("engagement_boost_on", affection=after)
        elif (not now) and was:
            m.set_flag("engagement_boost", False)
            m.log_event("engagement_boost_off", affection=after)
        return {
            "warmth": int(result.get("warmth", 0)),
            "kiss_request": kiss_req,
            "method": result.get("method", "heuristic"),
            "affection_before": before,
            "affection": after,
            "delta": delta,
            "engagement": now,
        }

    def ks_busy():
        r = ks_llm.CURRENT
        return r is not None and not r.done

    def ks_elapsed():
        r = ks_llm.CURRENT
        return int(r.elapsed()) if r is not None else 0

    ## ── rolling summary (Wednesday's memory upgrade) ─────────────────────
    def ks_summarizer_on(gid):
        return gid in ks_route().get("summarizer_slots", [])

    def ks_summary_due(gid):
        m = ks_mem(gid)
        return bool(ks_summarizer_on(gid) and m.data
                    and ks_llm.summary_due(m.data, ks_llm.summarizer_settings(ks_cfg(gid))))

    def ks_start_summary(gid):
        import copy
        m = ks_mem(gid)
        ks_llm.start_job(ks_llm.fold_summary, ks_cfg(gid), gname(gid), copy.deepcopy(m.data),
                         ks_llm.summarizer_settings(ks_cfg(gid)))

    def ks_apply_summary(gid):
        r = ks_llm.CURRENT
        out = r.reply if r is not None else None
        if _ks_is_map(out) and out.get("text"):
            ks_mem(gid).apply_summary(out["text"], out["covered"], out["method"],
                                      store.day_name, out.get("error", ""))
            return out["method"]
        return None

    def ks_start_chat(gid, scene_note, classify_message=None):
        cfg = ks_cfg(gid)
        ## Jailbreak preset: one roll per reply (~75%); see ks_jailbreak_roll.
        jb = ks_jailbreak_roll(gid)
        msgs = ks_mem(gid).build_messages(ks_system_prompt(gid, jailbreak_ok=jb),
                                         cfg.get("history_messages", 24),
                                         scene_note)
        if classify_message is not None:
            ## Companion slot: classifier + reply in one job (sequential
            ## HTTP, one typing-indicator wait). Reply is a string.
            ks_llm.start_chat_then_classify(cfg, msgs, classify_message)
        else:
            ks_llm.start(cfg, msgs)

    def ks_classification():
        """Classification dict from a finished companion chat job, or None."""
        r = ks_llm.CURRENT
        out = getattr(r, "classification", None) if r is not None else None
        if not (_ks_is_map(out) and "warmth" in out):
            out = getattr(ks_llm, "LAST_CLASSIFICATION", None)
        return out

    def ks_start_calibration(gid):
        ks_llm.start_job(ks_llm.calibrate, ks_cfg(gid), ks_system_prompt(gid, use_preset=False),
                         list(CALIBRATION_PROBES), CALIBRATION_SCENE)

    def ks_start_ping():
        cfg = ks_cfg()
        ks_llm.start(cfg, [{"role": "user",
                            "content": "Reply with exactly one word: pong"}],
                     temperature=0.0)

    def ks_result():
        """(reply, error, model) of the last finished request."""
        r = ks_llm.CURRENT
        if r is None:
            return None, "No request was sent.", None
        return r.reply, r.error, r.model

    def ks_chunks(text):
        return ks_llm.split_for_display(text)

    def ks_quote(text):
        """Escape [ ] { } so model output is shown literally, never as Ren'Py markup."""
        return text.replace("[", "[[").replace("{", "{{")

    def ks_memory_paths():
        return dict((gid, ks_memory_path(gid)) for gid in GIRL_IDS)

    def ks_on_memory_save(path, data):
        """Keep store.ks_mem_snapshot in sync so every Ren'Py save carries it."""
        if renpy.is_init_phase():
            return
        gid = ks_llm.memory_gid_from_path(path)
        if not gid:
            return
        payload = ks_llm.plain_memory(data)
        snap = getattr(store, "ks_mem_snapshot", None)
        if snap is None:
            store.ks_mem_snapshot = {gid: payload}
            return
        if snap.get(gid) != payload:
            snap[gid] = payload

    def ks_restore_mem_snapshot():
        """After load or rollback: write the saved snapshot back to the JSON files."""
        snap = getattr(store, "ks_mem_snapshot", None)
        result = ks_llm.restore_memory_snapshot(ks_memory_paths(), snap)
        if result == "skipped" and ks_debug():
            print("KARADA: loaded a save without a memory snapshot; leaving memory files as they are.")
        return result

    def ks_mem_on_interact():
        if renpy.game.after_rollback:
            ks_restore_mem_snapshot()

    ks_llm.set_memory_save_hook(ks_on_memory_save)
    if ks_restore_mem_snapshot not in config.after_load_callbacks:
        config.after_load_callbacks.append(ks_restore_mem_snapshot)
    if ks_mem_on_interact not in config.start_interact_callbacks:
        config.start_interact_callbacks.append(ks_mem_on_interact)


## Typing / waiting indicator.
screen ks_waiting(doing="typing"):
    zorder 100
    $ secs = ks_elapsed()
    $ note = ks_quote(ks_status_note())
    frame:
        xalign 0.5 yalign 0.62
        padding (30, 14)
        background Solid("#000000aa")
        vbox:
            text "[ks_waiting_who] is [doing]… ([secs]s)" size 28 color "#e8f6ff"
            if note:
                text "[note]" size 22 color "#ffd27a"


## Wait for the in-flight request. Usage:  call ks_wait("typing")
label ks_wait(doing="typing", who="She"):
    $ ks_waiting_who = who
    show screen ks_waiting(doing)
    while ks_busy():
        $ renpy.pause(0.2, hard=True)
    hide screen ks_waiting
    return


## One AI chat scene with girl `gid`.
##   call girl_chat("companion", "mon_evening", "scene note for the model", 8)
## Player leaves by submitting an empty line (or after max_turns).
## Returns number of completed exchanges.
label girl_chat(gid, scene_id, scene_note, max_turns=6, day=None):
    $ day = day or day_name
    $ _ks_turns = 0
    $ _ks_pending_no = False
    $ _ks_stop = False
    $ _ks_name = gname(gid)
    $ _ks_char = gchar(gid)
    $ _ks_aff = None
    $ ks_note_double_date()
    if gid == "companion":
        show screen hikari_chat_chrome
    while _ks_turns < max_turns and not _ks_stop:
        $ _ks_said = renpy.input("Message [_ks_name]  (leave empty to stop)", length=800).strip()
        if _ks_pending_no:
            ## She said no last turn: did you move on, or push?
            $ ks_note_after_refusal(gid, _ks_said)
            $ _ks_pending_no = False
        if not _ks_said:
            $ _ks_stop = True
        else:
            $ ks_mem(gid).add("user", _ks_said, day, scene_id)
            $ _ks_said_q = ks_quote(_ks_said)
            $ _ks_classify_said = _ks_said
            p "[_ks_said_q]"
            ## Classifier runs in the same background job, just before her
            ## reply, so LM Studio only ever sees one HTTP call at a time.
            ## The new meter value applies to the *next* turn; this turn's
            ## kiss gate uses the meter as it already stood.
            ## Memory summarizer (Wednesday on): fold older turns first.
            if ks_summary_due(gid):
                $ ks_start_summary(gid)
                call ks_wait("remembering", _ks_name)
                $ ks_apply_summary(gid)
            $ _ks_retry = True
            while _ks_retry:
                $ _ks_retry = False
                $ ks_start_chat(gid, scene_note, _ks_said if gid == "companion" else None)
                $ ks_mood(gid, "thinking")
                call ks_wait("typing", _ks_name)
                $ _ks_reply, _ks_err, _ks_model = ks_result()
                if _ks_err:
                    $ ks_mood(gid, "distant")
                    call ks_net_error(_ks_err, gid)
                    if _return == "retry":
                        $ _ks_retry = True
                    else:
                        ## Skip: drop the unanswered message so memory stays honest.
                        $ ks_mem(gid).data["messages"].pop()
                        $ ks_mem(gid).save()
                        $ _ks_stop = True
                else:
                    $ ks_mood(gid, ks_mood_from_reply(gid, _ks_reply))
                    $ ks_mem(gid).add("assistant", _ks_reply, day, scene_id)
                    $ ks_mem(gid).used_model(_ks_model)
                    if gid == "companion":
                        $ _ks_cls = ks_classification()
                        $ _ks_aff = ks_apply_classify(gid, _ks_cls)
                        $ ks_note_said(gid, _ks_said, _ks_aff["warmth"])
                    else:
                        ## No extra LLM call for the others: keyword warmth.
                        $ ks_note_said(gid, _ks_said, ks_llm.warmth_heuristic(_ks_said)[0])
                    if ks_llm.looks_like_refusal(_ks_reply):
                        $ ks_refusals_seen[gid] = ks_refusals_seen.get(gid, 0) + 1
                        $ ks_note_refusal(gid, scene_id)
                        $ _ks_pending_no = True
                    $ _ks_turns += 1
                    python:
                        _chunks = ks_chunks(_ks_reply)
                        _kiss_req = bool(_ks_aff and _ks_aff.get("kiss_request"))
                        _can_kiss = bool(_ks_aff and _ks_aff["affection_before"] >= ks_aff_settings()["kiss_threshold"])
                        _refused = ks_llm.looks_like_refusal(_ks_reply)
                        _show_refuse = _kiss_req and not _can_kiss
                        for _i, _c in enumerate(_chunks):
                            if _show_refuse and _i == len(_chunks) - 1:
                                renpy.show_screen("hikari_moment")
                            renpy.say(_ks_char, ks_quote(_c))
                    if gid == "companion" and _ks_aff and _ks_aff.get("kiss_request"):
                        if _can_kiss and not ks_llm.looks_like_refusal(_ks_reply):
                            call hikari_kiss_accepted
                        elif not _can_kiss:
                            $ ks_mem(gid).log_event("kiss", accepted=False, day=day,
                                affection=_ks_aff["affection_before"])
                            hide screen hikari_moment
                    $ renpy.block_rollback()
    if _ks_pending_no:
        $ ks_note_after_refusal(gid, "")
    if gid == "companion":
        hide screen hikari_chat_chrome
        hide screen hikari_moment
    return _ks_turns


## Network error dialog. Returns "retry" or "skip".
label ks_net_error(err, gid=None):
    $ _ks_err_q = ks_quote(err)
    $ _ks_ep = ks_quote(ks_cfg(gid)["endpoint"])
    app "Connection problem: [_ks_err_q]"
    n "(Endpoint: [_ks_ep]. Start LM Studio's local server and load a model, or edit game/karada_config.json.)"
    menu:
        "Retry":
            return "retry"
        "Skip this conversation":
            return "skip"


## Main-menu "LLM Check": a quick round trip with the configured server.
label connection_test:
    scene bg card
    $ _ks_ep = ks_quote(ks_cfg()["endpoint"])
    $ _ks_m = ks_quote(ks_cfg().get("model") or "(auto: first model from /v1/models)")
    n "Endpoint: [_ks_ep]\nModel: [_ks_m]"
    $ ks_start_ping()
    call ks_wait("being pinged", "The server")
    $ _ks_reply, _ks_err, _ks_model = ks_result()
    if _ks_err:
        $ _ks_err_q = ks_quote(_ks_err)
        n "Failed: [_ks_err_q]"
        n "Check: LM Studio → Developer/Server tab → Start Server, a model is loaded, and the port matches (default 1234)."
    else:
        $ _ks_reply_q = ks_quote(_ks_reply)
        $ _ks_model_q = ks_quote(_ks_model or "?")
        n "Success! Model [_ks_model_q] replied: \"[_ks_reply_q]\""
    return
