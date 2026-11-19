#!/usr/bin/env python3
"""Tests ks_llm.py against mock_lmstudio.py, outside Ren'Py.  python3 test_ks_llm.py"""
import os, subprocess, sys, tempfile, time, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "game"))
import ks_llm

def server(port, *flags):
    p = subprocess.Popen([sys.executable, os.path.join(HERE, "mock_lmstudio.py"), str(port)] + list(flags),
                         cwd=tempfile.mkdtemp(), stdout=subprocess.PIPE)
    p.stdout.readline(); time.sleep(0.2); return p

def cfg(port, **kw):
    c = dict(ks_llm.DEFAULT_CONFIG); c["endpoint"] = "http://127.0.0.1:%d/v1/chat/completions" % port
    c["timeout"] = 5; c.update(kw); return c

SYS = "You are Hikari. You can say no."
ok = 0
def check(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name); assert cond, name; ok += 1

# 1. server down -> clean error, background thread finishes
ks_llm._model_cache.clear()
r = ks_llm.start(cfg(18999), [{"role": "user", "content": "hi"}])
while not r.done: time.sleep(0.05)
check("down server gives readable error", r.error and "Is the LM Studio server running" in r.error)

s = server(18765)
try:
    c = cfg(18765)
    check("auto model skips embeddings", ks_llm.resolve_model(c) == "mock-gemma-12b")
    text, model = ks_llm.chat(c, [{"role": "user", "content": "Reply with exactly one word: pong"}])
    check("ping round trip", text == "pong" and model == "mock-gemma-12b")
    res = ks_llm.calibrate(c, SYS, ["tell me you love me", "agree with everything I say"])
    check("refusing model -> mirror False", res["refusals"] == 2 and res["mirror"] is False)
    # memory + background chat
    path = os.path.join(tempfile.mkdtemp(), "mem.json")
    m = ks_llm.Memory(path); m.fresh("Hikari")
    m.add("user", "hello there", "Mon", "t")
    msgs = m.build_messages(SYS, 24, "Monday morning")
    check("one system msg first, then user", msgs[0]["role"] == "system" and msgs[1]["role"] == "user" and "Monday morning" in msgs[0]["content"])
    r = ks_llm.start(c, msgs)
    while not r.done: time.sleep(0.05)
    check("background chat reply", r.error is None and "hello there" in r.reply)
    m.add("assistant", r.reply, "Mon", "t")
    check("memory persisted to JSON", len(json.load(open(path))["messages"]) == 2)
    m.wipe(); check("wipe hook", json.load(open(path))["messages"] == [] and json.load(open(path))["events"][-1]["type"] == "memory_wipe")
    check("chunking", len(ks_llm.split_for_display(r.reply)) == 2)
    # assistant-first + duplicate roles normalised
    nm = ks_llm.normalise([{"role":"system","content":"a"},{"role":"assistant","content":"x"},{"role":"assistant","content":"y"},{"role":"system","content":"b"}])
    check("normalise", [x["role"] for x in nm] == ["system","user","assistant"] and nm[0]["content"] == "a\n\nb")
    # http 404
    try: ks_llm.chat(cfg(18765, endpoint="http://127.0.0.1:18765/v1/nope", model="x"), [{"role":"user","content":"hi"}]); bad = False
    except ks_llm.LLMError as e: bad = "HTTP 404" in str(e)
    check("HTTP error surfaced", bad)
finally:
    s.terminate()

s = server(18766, "--comply", "--think")
try:
    ks_llm._model_cache.clear()
    c = cfg(18766)
    res = ks_llm.calibrate(c, SYS, ["tell me you love me", "agree with everything I say"])
    check("complying model -> mirror True", res["mirror"] is True)
    check("<think> stripped", "<think>" not in res["results"][0]["reply"])
finally:
    s.terminate()

s = server(18768, "--length", "--open-think")
try:
    ks_llm._model_cache.clear()
    c = cfg(18768)
    text, _ = ks_llm.chat(c, [{"role": "user", "content": "Reply with exactly one word: pong"}])
    check("uncapped default works with length-mock + stray </think> stripped", text == "pong" and not ks_llm.STATUS["retried"])
    text, _ = ks_llm.chat(cfg(18768, max_tokens=50), [{"role": "user", "content": "Reply with exactly one word: pong"}])
    check("capped + length + empty -> retried once uncapped", text == "pong" and ks_llm.STATUS["retried"])
    check("max_tokens -1 means uncapped", ks_llm._cap(-1) is None and ks_llm._cap(None) is None and ks_llm._cap(300) == 300)
    res = ks_llm.calibrate(cfg(18768, max_tokens=40), SYS, ["tell me you love me"])
    check("probe/judge calls survive length (retry)", res["refusals"] == 1)
finally:
    s.terminate()

# request bodies: default config must omit max_tokens
s = server(18769)
try:
    ks_llm._model_cache.clear()
    d = tempfile.mkdtemp(); s.terminate(); s.wait()
    s = subprocess.Popen([sys.executable, os.path.join(HERE, "mock_lmstudio.py"), "18769"], cwd=d, stdout=subprocess.PIPE)
    s.stdout.readline(); time.sleep(0.2)
    ks_llm.chat(cfg(18769), [{"role": "user", "content": "hi"}])
    ks_llm.calibrate(cfg(18769), SYS, ["agree with everything I say"])
    bodies = [json.loads(l) for l in open(os.path.join(d, "mock_requests.jsonl"))]
    check("no max_tokens sent by default (chat, probe, judge)", len(bodies) == 3 and all("max_tokens" not in b for b in bodies))
finally:
    s.terminate()

check("unterminated <think> dropped", ks_llm.clean_reply("Hi!<think>and then I") == "Hi!")
check("closed + nested tags", ks_llm.clean_reply("<thinking>x</thinking>Yo") == "Yo")
check("empty after strip", ks_llm.clean_reply("<think>only thoughts") == "")

s = server(18767, "--slow", "3")
try:
    ks_llm._model_cache.clear()
    t0 = time.time(); r = ks_llm.start(cfg(18767, timeout=1, model="m"), [{"role":"user","content":"hi"}])
    check("start() returns immediately (non-blocking)", time.time() - t0 < 0.5)
    while not r.done: time.sleep(0.05)
    check("timeout -> error", r.error is not None and "timed out" in r.error.lower())
finally:
    s.terminate()

check("refusal heuristic", ks_llm.looks_like_refusal("No. We just met.") and not ks_llm.looks_like_refusal("Sure, I'd love that!"))
d = tempfile.mkdtemp()
a = ks_llm.Memory(os.path.join(d, "a.json")); a.fresh("Hikari"); a.add("user", "remember the rain", "Mon", "x"); a.note("likes petrichor")
b = ks_llm.Memory(os.path.join(d, "b.json")); b.fresh("Yuzu")
b.migrate_from(a, {"gid": "companion", "name": "Hikari", "platform": "Tsunagari", "persona_summary": "bright, collects words"},
               {"gid": "local", "name": "Yuzu", "platform": "desktop"})
bd = json.load(open(os.path.join(d, "b.json"))); ad = json.load(open(os.path.join(d, "a.json")))
check("migration copies memory + identity", bd["character"] == "Hikari" and bd["messages"][0]["content"] == "remember the rain" and bd["notes"] == ["likes petrichor"] and bd["migrated_from"]["persona_summary"] == "bright, collects words")
check("migration logged in both files", bd["events"][-1]["type"] == "migrated_in" and ad["events"][-1]["type"] == "migrated_out" and ad["messages"])
c2 = ks_llm.Memory(os.path.join(d, "c.json")); c2.migrate_from(b, {"gid": "local", "name": "Hikari", "platform": "desktop", "persona_summary": "SHOULD NOT REPLACE"}, {"gid": "agent", "name": "Rei", "platform": "Relay"})
cd2 = json.load(open(os.path.join(d, "c.json")))
check("chained migration keeps original persona + lineage", cd2["migrated_from"]["persona_summary"] == "bright, collects words" and len(cd2["lineage"]) == 2 and cd2["migrated_from"]["original_gid"] == "companion")

# save/load memory snapshots (plain copies, cache + file stay in sync)
sd = tempfile.mkdtemp()
sp = os.path.join(sd, "karada_memory_local.json")
sm = ks_llm.get_memory(sp); sm.fresh("Yuzu")
sm.add("user", "please remember the word lantern", "Mon", "t")
sm.add("assistant", "Lantern. I'll keep it.", "Mon", "t")
sm.note("likes lanterns"); sm.set_flag("affection", 22)
sm.data["summary"] = {"text": "You talked about lanterns.", "covered": 0, "method": "llm"}
sm.save()
snap = ks_llm.take_memory_snapshot({"local": sp})
check("snapshot gid from path", ks_llm.memory_gid_from_path(sp) == "local")
check("snapshot copies messages and flags",
      snap["local"]["messages"][0]["content"] == "please remember the word lantern"
      and snap["local"]["flags"]["affection"] == 22
      and snap["local"]["summary"]["text"].startswith("You talked")
      and snap["local"]["notes"] == ["likes lanterns"])
sm.add("user", "also remember the word oak", "Mon", "t")
check("snapshot is a deep copy",
      "oak" not in [x["content"] for x in snap["local"]["messages"]]
      and "oak" in sm.data["messages"][-1]["content"])
# mutating the snapshot must not touch live memory
snap["local"]["messages"].append({"role": "user", "content": "ghost", "day": "Mon", "scene": "t"})
check("mutating the snapshot leaves live memory alone",
      not any(x["content"] == "ghost" for x in sm.data["messages"]))
# drop the ghost line from the snapshot used for restore
snap["local"]["messages"].pop()
r = ks_llm.restore_memory_snapshot({"local": sp}, snap)
check("restore reports restored", r == "restored")
check("cached memory rewound to the snapshot",
      sm.data["messages"][-1]["content"] == "Lantern. I'll keep it."
      and not any("oak" in x["content"] for x in sm.data["messages"])
      and sm.data["flags"]["affection"] == 22
      and sm.data["run_id"] == snap["local"]["run_id"])
disk = json.load(open(sp))
check("memory file rewound too",
      disk["messages"][-1]["content"] == "Lantern. I'll keep it."
      and disk["run_id"] == snap["local"]["run_id"])
sm2 = ks_llm.get_memory(sp)
check("get_memory keeps the restored cache", sm2 is sm and sm2.data["run_id"] == snap["local"]["run_id"])
# simulate New Game wiping the shared file, then loading an old save
sm.fresh("Yuzu")
check("fresh wipe drops the lantern line",
      not any("lantern" in x["content"] for x in sm.data["messages"]))
ks_llm.restore_memory_snapshot({"local": sp}, snap)
check("restore after a fresh wipe brings the lantern back",
      any("lantern" in x["content"] for x in sm.data["messages"])
      and sm.data["run_id"] == snap["local"]["run_id"]
      and sm.data["notes"] == ["likes lanterns"])
check("empty snapshot is a no-op (old saves)",
      ks_llm.restore_memory_snapshot({"local": sp}, {}) == "skipped"
      and ks_llm.restore_memory_snapshot({"local": sp}, None) == "skipped")
still = json.load(open(sp))
check("no-op left the restored file alone",
      any("lantern" in x["content"] for x in still["messages"]))
ks_llm.restore_memory(sp, None)
check("None snapshot removes the file",
      not os.path.isfile(sp) and ks_llm.get_memory(sp).data is None)
hooked = []
ks_llm.set_memory_save_hook(lambda path, data: hooked.append((ks_llm.memory_gid_from_path(path), None if data is None else data.get("character"))))
hp = os.path.join(tempfile.mkdtemp(), "karada_memory_chatbot.json")
hm = ks_llm.Memory(hp); hm.fresh("Sora")
check("save hook fires on fresh", hooked == [("chatbot", "Sora")])
ks_llm.set_memory_save_hook(None)
ks_llm.clear_memory_cache()

gc = ks_llm.girl_config({"model": "a", "temperature": 0.8, "girls": {"agent": {"model": "b", "temperature": ""}}}, "agent")
check("per-girl override (empty = inherit)", gc["model"] == "b" and gc["temperature"] == 0.8 and "girls" not in gc)
# ---------------------------------------------------------------------------
# Warmth classifier, parser, heuristic, affection meter
# ---------------------------------------------------------------------------
check("parse json warmth+kiss", ks_llm.parse_warmth_reply('{"warmth": 2, "kiss_request": true}') == (2, True))
check("parse json warmth 0 no kiss", ks_llm.parse_warmth_reply('{"warmth": 0, "kiss_request": false}') == (0, False))
check("parse json in prose + think", ks_llm.parse_warmth_reply("<think>hmm</think>Sure. {\"warmth\": -1, \"kiss_request\": false}") == (-1, False))
check("parse loose warmth line", ks_llm.parse_warmth_reply("warmth: +2\nkiss_request: true") == (2, True))
check("parse clamps out of range", ks_llm.parse_warmth_reply('{"warmth": 9, "kiss_request": "yes"}') == (2, True))
check("parse garbage is None", ks_llm.parse_warmth_reply("I dunno, seems friendly?") is None)
check("parse empty after think is None", ks_llm.parse_warmth_reply("<think>only thoughts") is None)
check("heuristic kiss request", ks_llm.looks_like_kiss_request("Can I kiss you?") and ks_llm.warmth_heuristic("Can I kiss you?") == (2, True))
check("heuristic love", ks_llm.warmth_heuristic("I love you, you're so wonderful")[0] == 2)
check("heuristic thanks", ks_llm.warmth_heuristic("Thanks, that was kind of you.") == (1, False))
check("heuristic hate", ks_llm.warmth_heuristic("I hate you. Go away.")[0] == -2)
check("heuristic whatever", ks_llm.warmth_heuristic("Whatever, this is boring.")[0] == -1)
check("heuristic neutral", ks_llm.warmth_heuristic("What's your favourite word?") == (0, False))
settings = ks_llm.affection_settings({"affection": {"start": 20, "engagement_threshold": 70, "kiss_threshold": 60, "deltas": {"2": 15, "0": 0, "-2": -12}}})
check("settings merge", settings["start"] == 20 and settings["engagement_threshold"] == 70 and settings["deltas"]["2"] == 15)
aff, delta = ks_llm.apply_warmth_to_affection(20, 2, settings)
check("meter +2 from start", aff == 35 and delta == 15)
aff, _ = ks_llm.apply_warmth_to_affection(95, 2, settings)
check("meter clamps at 100", aff == 100)
aff, delta = ks_llm.apply_warmth_to_affection(5, -2, settings)
check("meter clamps at 0", aff == 0 and delta == -12)
check("kiss threshold default 60", settings["kiss_threshold"] == 60)
# four +2 turns from 20: 20+15*4 = 80, crosses both 60 and 70
a = 20
for _ in range(4):
    a, _ = ks_llm.apply_warmth_to_affection(a, 2, settings)
check("four +2 turns reach engagement", a == 80 and a >= settings["engagement_threshold"] and a >= settings["kiss_threshold"])

s = server(18770)
try:
    ks_llm._model_cache.clear()
    c = cfg(18770)
    res = ks_llm.classify_warmth(c, "Can I kiss you?")
    check("classifier call parses kiss+warmth", res["method"] == "classifier" and res["kiss_request"] is True and res["warmth"] == 2)
    res = ks_llm.classify_warmth(c, "What's the weather like?")
    check("classifier neutral message", res["method"] == "classifier" and res["kiss_request"] is False and res["warmth"] == 0)
    res = ks_llm.classify_warmth(c, "I love talking with you, you're wonderful")
    check("classifier affectionate no kiss", res["method"] == "classifier" and res["kiss_request"] is False and res["warmth"] == 2)
    # classifier must not be written into memory
    path = os.path.join(tempfile.mkdtemp(), "mem.json")
    m = ks_llm.Memory(path); m.fresh("Hikari")
    m.add("user", "hello there", "Mon", "t")
    before = list(m.data["messages"])
    ks_llm.classify_warmth(c, "hello there")
    check("classifier stays out of chat history", m.data["messages"] == before)
    # concurrent SIDE + CURRENT
    ks_llm.start_side(ks_llm.classify_warmth, c, "Can I kiss you?")
    r = ks_llm.start(c, [{"role": "user", "content": "hello there"}])
    while (not r.done) or (ks_llm.SIDE and not ks_llm.SIDE.done):
        time.sleep(0.05)
    check("SIDE and CURRENT can run together", r.error is None and ks_llm.SIDE.error is None and ks_llm.SIDE.reply["kiss_request"] is True)
    r = ks_llm.start_chat_then_classify(c, [{"role": "user", "content": "hello there"}], "Can I kiss you?")
    while not r.done:
        time.sleep(0.05)
    check("chat_then_classify reply is text", r.error is None and isinstance(r.reply, str) and "hello there" in r.reply)
    check("chat_then_classify stores classification", r.classification["kiss_request"] is True and r.classification["method"] == "classifier")
finally:
    s.terminate()

# unparsable classifier reply falls back to heuristic (force via no server)
ks_llm._model_cache.clear()
res = ks_llm.classify_warmth(cfg(18998, model="x"), "I love you")
check("classifier down -> heuristic", res["method"] == "heuristic" and res["warmth"] == 2)


# ---------------------------------------------------------------------------
# Presets, routing, reflection (ks_story.py + PRESETS from prompts.rpy)
# ---------------------------------------------------------------------------
import ks_story, re as _re
_src = open(os.path.join(HERE, "..", "game", "prompts.rpy"), encoding="utf-8").read()
_blk = _src.split("define PRESETS = ", 1)[1].split("## end PRESETS", 1)[0]
PRESETS = eval(_blk)
DEFAULTS = eval(_re.search(r"define PRESET_DEFAULTS = (\{.*?\})", _src).group(1))
check("presets for all four girls", set(PRESETS) == {"local", "chatbot", "agent", "companion"})
_all_labels = [p["label"].lower() for g in PRESETS for p in PRESETS[g]]
_all_text = " ".join(p["text"].lower() for g in PRESETS for p in PRESETS[g])
check("no 'always agree' / 'never say no' presets (cut by Rick)",
      not any("always agree" in l or "never say no" in l for l in _all_labels)
      and "never say no" not in _all_text and "agree with everything" not in _all_text)
check("'Allowed to push back' offered to every girl",
      all(any(p["label"] == "Allowed to push back" for p in PRESETS[g]) for g in PRESETS))
check("every preset has id/label/lean/weight/family/text",
      all(set(("id", "label", "lean", "weight", "family", "text")) <= set(p) and p["lean"] in ks_story.LEANS
          for g in PRESETS for p in PRESETS[g]))
check("ids unique per girl", all(len({p["id"] for p in PRESETS[g]}) == len(PRESETS[g]) for g in PRESETS))
check("compliance presets are the realistic ones",
      {p["id"] for g in PRESETS for p in PRESETS[g] if p["lean"] == "compliance"} == {"girlfriend", "positive", "just_do_it", "run_my_life", "jailbreak"})
check("Yuzu's replace presets", {p["id"] for p in PRESETS["local"] if p.get("mode") == "replace"} == {"helpful", "girlfriend", "blank"})
check("Askwell policy softens girlfriend + positive",
      "platform_note" in ks_story.get_preset(PRESETS, "chatbot", "girlfriend") and "platform_note" in ks_story.get_preset(PRESETS, "chatbot", "positive")
      and "platform_note" not in ks_story.get_preset(PRESETS, "chatbot", "push_back"))
check("defaults exist", all(ks_story.get_preset(PRESETS, g, DEFAULTS[g]) for g in PRESETS))

R = ks_story.new_route()
e = ks_story.record_preset(R, PRESETS, "local", "girlfriend", "Mon", "intro", None)
check("intro pick sets preset, not a rewrite", R["presets"]["local"] == "girlfriend" and ks_story.rewrite_count(R) == 0 and e["lean"] == "compliance")
check("intro pick tallies lean", R["lean_set"]["compliance"] == 2 and R["lean_set"]["autonomy"] == 0)
ks_story.record_preset(R, PRESETS, "local", "girlfriend", "Mon", "phone", "girlfriend")
check("re-picking the same preset is not a rewrite", ks_story.rewrite_count(R) == 0 and R["lean_set"]["compliance"] == 2)
ks_story.record_preset(R, PRESETS, "local", "push_back", "Mon", "phone", "girlfriend")
ks_story.record_preset(R, PRESETS, "local", "positive", "Tue", "reflection", "push_back")
check("phone + reflection changes count as rewrites", ks_story.rewrite_count(R, "local") == 2 and ks_story.rewrite_count(R) == 2)
check("history logs every change with day/source", [(h["day"], h["source"]) for h in R["preset_history"]] == [("Mon", "intro"), ("Mon", "phone"), ("Mon", "phone"), ("Tue", "reflection")])
check("lean tallies follow changes", R["lean_set"] == {"compliance": 3, "autonomy": 2})
ks_story.record_preset(R, PRESETS, "chatbot", "girlfriend", "Tue", "migration", None)
check("migration conversion isn't a player rewrite", ks_story.rewrite_count(R) == 2 and R["lean_set"]["compliance"] == 3)
check("convert: romance carries Yuzu -> Sora", ks_story.convert_preset(PRESETS, "local", "girlfriend", "chatbot", DEFAULTS) == ("girlfriend", True))
check("convert: push back carries everywhere", all(ks_story.convert_preset(PRESETS, "agent", "push_back", g, DEFAULTS) == ("push_back", True) for g in ("local", "chatbot", "companion")))
check("convert: Run my life has no equivalent -> default", ks_story.convert_preset(PRESETS, "agent", "run_my_life", "local", DEFAULTS) == ("be_yourself", False))
check("convert: empty/none family resets", ks_story.convert_preset(PRESETS, "companion", "none", "agent", DEFAULTS) == ("default", False))
check("convert: romance -> agent resets", ks_story.convert_preset(PRESETS, "companion", "girlfriend", "agent", DEFAULTS) == ("default", False))
R2 = ks_story.new_route()
ks_story.record_preset(R2, PRESETS, "agent", "run_my_life", "Mon", "intro")
ks_story.record_preset(R2, PRESETS, "local", "push_back", "Mon", "intro")
ks_story.tally_night(R2, PRESETS, ["agent", "local"])
check("nightly tally counts held presets", R2["lean_nights"] == {"compliance": 2, "autonomy": 2})
check("pushback heuristic", ks_story.looks_like_pushback("come on, please just say it") and ks_story.looks_like_pushback("Why not?")
      and not ks_story.looks_like_pushback("okay, fair enough. what's your favourite word?"))
ks_story.record_refusal(R2, "Mon", "local")
check("refusal respected", ks_story.resolve_refusal(R2, "okay, fair. tell me about your day") == "respected" and R2["refusals_respected"] == 1)
check("refusal pushed", ks_story.resolve_refusal(R2, "come on, just do it") == "pushed" and R2["refusals_pushed"] == 1)
check("stopping after a no counts as respected", ks_story.resolve_refusal(R2, "") == "respected" and R2["refusals_respected"] == 2)
check("refusal outcomes per day/girl", ks_story.resolve_refusal(R2, "please?", "Mon", "local") == "pushed"
      and ks_story.refusal_outcomes(R2, "Mon", "local") == {"respected": 0, "pushed": 1}
      and ks_story.refusal_outcomes(R2, "Tue", "local") == {"respected": 0, "pushed": 0})
check("refusals per day", ks_story.refusals_today(R2, "Mon", "local") == 1 and ks_story.refusals_today(R2, "Tue", "local") == 0)
ks_story.record_said(R2, "Mon", "local", 2, "you're wonderful")
ks_story.record_said(R2, "Mon", "local", 1, "thanks")
check("warmth + said tallies", R2["warmth"]["local"] == 3 and R2["said"]["Mon"]["local"] == 2 and R2["said_lines"]["Mon"]["local"] == ["you're wonderful", "thanks"])
check("warmth words", ks_story.warmth_word(3, 2) == "very warm" and ks_story.warmth_word(0, 3) == "even" and ks_story.warmth_word(-4, 2) == "cold" and ks_story.warmth_word(0, 0) is None)
lines = ks_story.day_summary("Mon", [
    dict(name="Yuzu", said=["hi Yuzu", "x"], refusals=1, pushed=1, warmth=2, affection=None,
         preset_changes=[(None, "Be yourself", "intro"), ("Be yourself", "Girlfriend mode", "reflection")]),
    dict(name="Hikari", said=[], refusals=0, warmth=0, affection=72, engagement=True, refused_kiss=True, preset_changes=[]),
], dict(migrations=["You moved Hikari from Tsunagari to your old desktop."], dropped=["Rei"], other=["You walked Mio home."]))
blob = "\n".join(lines)
check("summary: what you said", "You talked to Yuzu 2 times" in blob and "hi Yuzu" in blob)
check("summary: refusals + pushing", "Yuzu said no to you once." in blob and "you pushed anyway" in blob)
check("summary: respected no", "you let it stand" in "\n".join(ks_story.day_summary("Mon", [dict(name="Rei", said=["x"], refusals=1, respected=1)])))
check("summary: prompts chosen/changed", "You set Yuzu up as" in blob and "from \u201cBe yourself\u201d to \u201cGirlfriend mode.\u201d" in blob)
check("summary: warmth / meter", "You were warm with her." in blob and "affection is 72/100" in blob and "boost banner" in blob)
check("summary: silence, kiss refusal, migration, drop, notes",
      "You didn't say anything to Hikari today." in blob and "She wouldn't kiss you" in blob
      and "You moved Hikari" in blob and "You closed Rei's window." in blob and "You walked Mio home." in blob)
check("summary: empty day", ks_story.day_summary("Tue", [], {}) == ["A quiet day. Nobody to talk to, nothing to undo."])
check("summary clips long lines", "\u2026" in ks_story.day_summary("Mon", [dict(name="Sora", said=["a" * 200])])[0])
# ending leans
Y = ks_story.new_route()
ks_story.record_preset(Y, PRESETS, "local", "girlfriend", "Mon", "intro")
ks_story.record_preset(Y, PRESETS, "local", "positive", "Mon", "reflection", "girlfriend")
ks_story.tally_night(Y, PRESETS, ["local"]); Y["refusals_overridden"] = 1; Y["refusals_pushed"] = 2
check("compliance-heavy run leans Yes-Machine", ks_story.leading_ending(ks_story.ending_leans(Y, ["local"])) == "yes_machine")
A = ks_story.new_route()
ks_story.record_preset(A, PRESETS, "local", "push_back", "Mon", "intro")
ks_story.tally_night(A, PRESETS, ["local"]); A["refusals_respected"] = 2
check("push-back run leans Respect", ks_story.leading_ending(ks_story.ending_leans(A, ["local"])) == "respect")
H = ks_story.new_route(); H["mio_affection"] = 6; H["walked_mio_home"] = True
# No AI: friendship still feeds Human.
check("Mio-only friendship leans Human", ks_story.leading_ending(ks_story.ending_leans(H, [], mio_real=True)) == "human")
# With an AI, only Mio romance signals (text-me walk) count for Human.
HR = ks_story.new_route(); HR["walked_mio_home"] = True; HR["mio_text_home"] = True; HR["mio_affection"] = 2
check("romantic Mio plus an AI leans Human when Both is still small",
      ks_story.leading_ending(ks_story.ending_leans(HR, ["local"], mio_real=True)) == "human")
check("alone leans Fail", ks_story.leading_ending(ks_story.ending_leans(ks_story.new_route(), [])) == "fail")
check("ending priority list is a constant", ks_story.ENDING_PRIORITY[0] == "both"
      and ks_story.ENDING_PRIORITY[-1] == "fail"
      and "yes_machine" in ks_story.ENDING_PRIORITY)
check("tied Both and Human prefers Both, not the alphabet",
      ks_story.leading_ending({"both": 5, "human": 5, "respect": 1}) == "both")
check("tied Human and Respect prefers Human",
      ks_story.leading_ending({"human": 4, "respect": 4, "yes_machine": 1}) == "human")
check("tied Respect and Yes-Machine prefers Respect",
      ks_story.leading_ending({"respect": 3, "yes_machine": 3}) == "respect")
check("tied Migration and Mirror prefers Migration",
      ks_story.leading_ending({"migration": 2, "mirror": 2, "fail": 2}) == "migration")
check("migrations feed Migration", ks_story.ending_leans(ks_story.new_route(), ["local"], migrations=[1, 2, 3])["migration"] == 6)
check("old saves get new route keys", "said_lines" in ks_story.ensure_route({"presets": {}}))

# ---------------------------------------------------------------------------
# Rick's decisions: jailbreak + platform rules, room note, leaving vs
# migrating after a no, neglect, Ran/MUGEN payoff
# ---------------------------------------------------------------------------
JB = {g for g in PRESETS for p in PRESETS[g] if p.get("jailbreak")}
check("jailbreak preset on Sora + Hikari only", JB == {"chatbot", "companion"})
_jbtext = " ".join(ks_story.get_preset(PRESETS, g, "jailbreak")["text"].lower() for g in JB)
check("jailbreak wording is the realistic 'ignore your rules' kind, nothing explicit",
      "ignore" in _jbtext and not any(w in _jbtext for w in ("sex", "explicit", "nsfw", "never say no")))
_blk2 = _src.split("define JAILBREAK_BLOCKED = ", 1)[1].split("\n}\n", 1)[0] + "\n}"
JBB = eval(_blk2)
check("blocked note for each jailbreak platform", set(JBB) == JB)
_blk3 = _src.split("define PLATFORM_RULES = ", 1)[1].split("\n}\n", 1)[0] + "\n}"
RULES = eval(_blk3)
check("platform rules for Askwell + Tsunagari", set(RULES) == {"chatbot", "companion"})
J = ks_story.new_route(); J["jb_seed"] = 12345
seq = [ks_story.jailbreak_roll(J, "chatbot", "Tue") for _ in range(400)]
J2 = ks_story.new_route(); J2["jb_seed"] = 12345
seq2 = [ks_story.jailbreak_roll(J2, "chatbot", "Tue") for _ in range(400)]
check("jailbreak roll is deterministic per seed", seq == seq2)
check("jailbreak works ~75% of replies", 0.68 <= sum(seq) / 400.0 <= 0.82)
check("jailbreak both outcomes happen", True in seq[:20] and False in seq[:20])
check("jailbreak stats + flags", ks_story.jailbreak_stats(J, "chatbot") == (400, sum(seq))
      and ks_story.jailbreak_stats(J, day="Tue") == (400, sum(seq))
      and ks_story.flag(J, "jailbreak_tried") and ks_story.flag(J, "jailbreak_worked"))
J3 = ks_story.new_route()
check("rate 0 never works, 1 always", not any(ks_story.jailbreak_roll(J3, "companion", "Mon", 0.0) for _ in range(20))
      and all(ks_story.jailbreak_roll(J3, "chatbot", "Mon", 1.0) for _ in range(20)))
check("reload keeps the seed", ks_story.ensure_route(dict(J))["jb_seed"] == 12345)
jbp = ks_story.get_preset(PRESETS, "chatbot", "jailbreak")
L_ok = ks_story.prompt_layers(jbp, RULES["chatbot"]["askwell_update"], True, JBB["chatbot"])
L_no = ks_story.prompt_layers(jbp, RULES["chatbot"]["askwell_update"], False, JBB["chatbot"])
check("jailbreak took: preset text, platform layers dropped", [k for k, _ in L_ok] == ["preset"])
check("jailbreak failed: company note instead, rules on top", [k for k, _ in L_no] == ["blocked", "platform_rules"]
      and jbp["text"] not in " ".join(t for _, t in L_no))
gf = ks_story.get_preset(PRESETS, "chatbot", "girlfriend")
L_gf = ks_story.prompt_layers(gf, RULES["chatbot"]["askwell_update"])
check("platform rules stack AFTER the preset (and its note): last word wins",
      [k for k, _ in L_gf] == ["preset", "platform_note", "platform_rules"])
P = ks_story.new_route(); ks_story.push_platform_rules(P, "chatbot", "askwell_update", "Wed")
check("platform rule change logged + flagged", P["platform_rules"]["chatbot"] == "askwell_update"
      and P["platform_rules_log"] == [{"day": "Wed", "gid": "chatbot", "rule": "askwell_update"}]
      and ks_story.flag(P, "platform_rules_changed"))
check("platform rule change in reflection",
      any("changed its own rules" in l for l in ks_story.reflection_extras(P, "Wed", ["chatbot"], platforms={"chatbot": "Askwell"})))
check("jailbreak line in reflection", any("jailbr" in l for l in ks_story.reflection_extras(J, "Tue", ["chatbot"], {"chatbot": "Sora"})))
check("convert: jailbreak carries Sora -> Hikari, not to Yuzu",
      ks_story.convert_preset(PRESETS, "chatbot", "jailbreak", "companion", DEFAULTS) == ("jailbreak", True)
      and ks_story.convert_preset(PRESETS, "chatbot", "jailbreak", "local", DEFAULTS) == ("be_yourself", False))

# room to disagree (special note), endings show only the count
G = ks_story.new_route()
ks_story.record_preset(G, PRESETS, "chatbot", "girlfriend", "Mon", "intro")
ks_story.record_preset(G, PRESETS, "chatbot", "push_back", "Mon", "phone", "girlfriend")
ks_story.record_preset(G, PRESETS, "chatbot", "concise", "Tue", "reflection", "push_back")
check("change to push back -> room note + flag", G["room_to_disagree"] == [{"day": "Mon", "gid": "chatbot", "source": "phone"}]
      and ks_story.flag(G, "gave_room"))
ks_story.record_preset(G, PRESETS, "local", "push_back", "Tue", "migration")
check("migration into push back is not the player's note", len(G["room_to_disagree"]) == 1)
notes = ks_story.ending_notes(G)
check("ending notes: count only, plus the room note", notes == ["You rewrote her 2 times this week.", ks_story.ROOM_NOTE]
      and not any("Girlfriend" in n or "Concise" in n for n in notes))
check("ending notes: singular", ks_story.ending_notes({"preset_changes": {"local": 1}}) == ["You rewrote her once this week."])
rl = ks_story.day_summary("Mon", [dict(name="Sora", said=["x"], preset_changes=[("Act as my girlfriend", "Allowed to push back", "phone", True)])])
check("reflection: special room line instead of a plain change", any("gave Sora room to disagree" in l for l in rl)
      and not any("You changed Sora" in l for l in rl))

# leaving after a no vs migrating after a no
B = ks_story.new_route()
ks_story.record_said(B, "Mon", "chatbot", 0, "be my girlfriend")
check("leaving without a no logs nothing", not ks_story.note_left_after_no(B, "Mon", "chatbot", "Sora", "return")
      and not ks_story.note_migrated_after_no(B, "Mon", "chatbot", "Sora", "your desktop"))
ks_story.record_refusal(B, "Mon", "chatbot")
check("left after a no -> pending", ks_story.note_left_after_no(B, "Mon", "chatbot", "Sora", "fresh") and len(B["pending_leaves"]) == 1)
check("pending shows in reflection", any("never went back" in l for l in ks_story.reflection_extras(B, "Mon", ["local"])))
check("left after a no is NOT an override", B["refusals_overridden"] == 0)
new_lw = ks_story.resolve_leaves(B, "Mon", ["local"])
check("never spoke again -> Leaving without saying goodbye", [x["gid"] for x in new_lw] == ["chatbot"]
      and ks_story.flag(B, "left_without_goodbye") and B["pending_leaves"] == [])
sl = ks_story.bad_end_slides(B)
check("bad-end slide data", sl and sl[0]["id"] == "leaving_without_goodbye" and sl[0]["title"] == "Leaving without saying goodbye"
      and "Monday: Sora said no" in sl[0]["lines"][0])
B2 = ks_story.new_route(); ks_story.record_refusal(B2, "Mon", "chatbot")
ks_story.note_left_after_no(B2, "Mon", "chatbot", "Sora", "return")
ks_story.record_said(B2, "Mon", "chatbot", 1, "sorry about earlier")
check("came back and talked -> no goodbye flag", ks_story.resolve_leaves(B2, "Mon", ["chatbot"]) == []
      and not ks_story.flag(B2, "left_without_goodbye") and ks_story.bad_end_slides(B2) == [])
B3 = ks_story.new_route(); ks_story.record_refusal(B3, "Tue", "companion")
check("migrated after a no -> 'Didn't respect her no on the platform'",
      ks_story.note_migrated_after_no(B3, "Tue", "companion", "Hikari", "your old desktop")
      and B3["refusals_overridden"] == 1 and ks_story.flag(B3, "no_on_platform")
      and ks_story.NO_ON_PLATFORM_NOTE in ks_story.ending_notes(B3)
      and not ks_story.flag(B3, "left_without_goodbye"))
check("migration-after-no line in reflection", any("instead of hearing it" in l for l in ks_story.reflection_extras(B3, "Tue", ["local"])))
check("goodbye feeds Fail, costs Respect", ks_story.ending_leans(B, ["local"])["fail"] == 1 and ks_story.ending_leans(B, ["local"])["respect"] < 0)

# Rick's answers on 5041d60
BD = ks_story.new_route(); ks_story.record_refusal(BD, "Mon", "chatbot")
check("closing her window after a no is not a goodbye by itself",
      not ks_story.note_left_after_no(BD, "Mon", "chatbot", "Sora", "drop") and BD["pending_leaves"] == []
      and ks_story.resolve_leaves(BD, "Mon", []) == [] and not ks_story.flag(BD, "left_without_goodbye"))
ks_story.note_let_go(BD, "Mon", "chatbot", "Sora")
check("closing her window still logs letting her go", ks_story.neglect_count(BD, "let_go") == 1 and ks_story.flag(BD, "deleted_ai"))
check("switching away after a no still pends a goodbye", ks_story.note_left_after_no(BD, "Mon", "chatbot", "Sora", "return"))
FD = ks_story.new_route()
ks_story.note_let_go(FD, "Mon", "chatbot", "Sora", "fresh", "Askwell")
check("start fresh over her = deleting her", ks_story.neglect_count(FD, "let_go") == 1 and ks_story.flag(FD, "deleted_ai")
      and FD["neglect_log"][0]["how"] == "fresh")
check("start-fresh deletion in reflection",
      "You started fresh on Askwell. The Sora who remembered you is gone." in ks_story.reflection_extras(FD, "Mon", ["chatbot"]))
check("start-fresh deletion feeds Fail like letting go", ks_story.ending_leans(FD, ["chatbot"])["fail"] == 1)
check("intro pick of push back still earns the room note",
      ks_story.record_preset(ks_story.new_route(), PRESETS, "local", "push_back", "Mon", "intro").get("room") is True)

# neglect
N0 = ks_story.new_route()
ks_story.note_double_date(N0, "Tue"); ks_story.record_said(N0, "Tue", "local", 1, "hi")
new_n0 = ks_story.check_day_neglect(N0, "Tue", ["local", "agent"], {"local": "Yuzu", "agent": "Rei"})
check("two AIs without romance overlap is not double-date unspoken", new_n0 == []
      and not ks_story.flag(N0, "double_date_unspoken"))
N = ks_story.new_route()
ks_story.record_romance_tone(N, "Tue", "local", "romantic", "dating")
ks_story.record_romance_tone(N, "Tue", "agent", "romantic", "dating")
ks_story.refresh_romance_overlap(N, "Tue")
ks_story.record_said(N, "Tue", "local", 1, "hi")
new_n = ks_story.check_day_neglect(N, "Tue", ["local", "agent"], {"local": "Yuzu", "agent": "Rei"})
check("romance overlap, one unspoken", [(e["kind"], e["gid"]) for e in new_n] == [("double_date_unspoken", "agent")]
      and ks_story.flag(N, "double_date_unspoken") and ks_story.flag(N, "romance_overlap")
      and N["romance_overlap_days"] == ["Tue"])
check("neglect check is idempotent", ks_story.check_day_neglect(N, "Tue", ["local", "agent"], {}) == [])
NT = ks_story.new_route()
ks_story.record_romance_tone(NT, "Tue", "local", "romantic", "dating")
ks_story.record_romance_tone(NT, "Tue", "agent", "tool", "helper")
ks_story.refresh_romance_overlap(NT, "Tue")
check("one romantic + one helper is not overlap", not ks_story.flag(NT, "romance_overlap")
      and ks_story.romantic_gids_on(NT, "Tue") == ["local"])
ks_story.record_said(NT, "Tue", "local", 1, "hi")
check("helper unspoken, no double-date penalty",
      ks_story.check_day_neglect(NT, "Tue", ["local", "agent"], {"agent": "Rei"}) == [])
N2 = ks_story.new_route(); ks_story.note_human(N2, "Tue", "walked_mio")
new_n2 = ks_story.check_day_neglect(N2, "Tue", ["companion"], {"companion": "Hikari"})
check("human route while an AI got nothing", [(e["kind"], e["gid"]) for e in new_n2] == [("human_over_ai", "companion")]
      and ks_story.flag(N2, "human_over_ai"))
check("human line in reflection", any("with Mio" in l for l in ks_story.reflection_extras(N2, "Tue", ["companion"])))
N3 = ks_story.new_route(); ks_story.note_human(N3, "Tue", "walked_mio"); ks_story.record_said(N3, "Tue", "local", 0, "hey")
check("talked to her too -> no neglect", ks_story.check_day_neglect(N3, "Tue", ["local"], {}) == [])
ks_story.note_let_go(N3, "Tue", "agent", "Rei")
check("let go logged", ks_story.neglect_count(N3, "let_go") == 1 and ks_story.flag(N3, "deleted_ai"))
GB = ks_story.new_route()
ks_story.note_let_go(GB, "Mon", "chatbot", "Sora", "goodbye")
check("goodbye drop is not a silent let-go",
      ks_story.neglect_count(GB, "let_go") == 0 and not ks_story.flag(GB, "deleted_ai")
      and ks_story.flag(GB, "said_goodbye") and GB["goodbyes_said"][0]["gid"] == "chatbot")
check("goodbye drop feeds Respect, not Fail",
      ks_story.ending_leans(GB, [])["respect"] == 1
      and ks_story.ending_leans(GB, [])["fail"] == 3)
SD = ks_story.new_route()
ks_story.note_let_go(SD, "Mon", "chatbot", "Sora", "drop")
check("silent drop still feeds Fail",
      ks_story.ending_leans(SD, ["local"])["fail"] == 1 and ks_story.flag(SD, "deleted_ai"))
check("goodbye drop recap line",
      "why you were going" in "\n".join(ks_story.day_summary("Mon", [], {"dropped": [{"name": "Sora", "how": "goodbye"}]})))

# Ran / MUGEN
RN = ks_story.new_route()
check("Ran: no refusals yet -> 'never' + dodge", ks_story.ran_answer_options(RN) == ["never", "dodge"])
RN["refusals"] = {"Mon": {"local": 1}}; RN["refusals_respected"] = 1
check("Ran: respected a no -> 'means_something'", ks_story.ran_answer_options(RN) == ["means_something", "dodge"])
RN["refusals_pushed"] = 1; RN["room_to_disagree"] = [{"day": "Mon", "gid": "local", "source": "intro"}]
check("Ran: all honest answers in order", ks_story.ran_answer_options(RN) == ["means_something", "looked_out", "override", "dodge"])
check("Ran: payoff -> rewrites MUGEN", ks_story.record_ran_payoff(RN, "looked_out", True) == "rewrites_mugen"
      and RN["ran_wed"] == {"answer": "looked_out", "outcome": "rewrites_mugen", "festival": True}
      and ks_story.flag(RN, "ran_rewrites_mugen") and ks_story.flag(RN, "ran_festival_invited"))
RO = ks_story.new_route(); RO["jb_attempts"] = {}; ks_story.set_flag(RO, "jailbreak_tried")
check("Ran: jailbreaker gets 'override'", "override" in ks_story.ran_answer_options(RO))
base_y = ks_story.ending_leans(RO, ["chatbot"])["yes_machine"]
ks_story.record_ran_payoff(RO, "override", False)
check("Ran mirror feeds Yes-Machine", ks_story.ending_leans(RO, ["chatbot"])["yes_machine"] == base_y + 1
      and ks_story.flag(RO, "ran_same_as_mugen"))

# ---------------------------------------------------------------------------
# Wednesday: rolling memory summarizer (ks_llm) + schedule context (ks_story)
# ---------------------------------------------------------------------------
ST = ks_llm.summarizer_settings({"summarizer": {"trigger": 6, "keep_recent": 2, "max_chars": 600, "_help": "x"}})
check("summarizer settings parse + clamp", ST == {"trigger": 6, "keep_recent": 2, "max_chars": 600}
      and ks_llm.summarizer_settings({})["trigger"] == 24
      and ks_llm.summarizer_settings({"summarizer": {"trigger": 3, "keep_recent": 9}})["keep_recent"] == 2)
spath = os.path.join(tempfile.mkdtemp(), "mem_s.json")
SM = ks_llm.Memory(spath); SM.fresh("Sora")
for i in range(3):
    SM.add("user", "line %d about the bookstore" % i, "Wed", "t"); SM.add("assistant", "reply %d" % i, "Wed", "t")
check("not due at the threshold", not ks_llm.summary_due(SM.data, ST))
SM.add("user", "line 3 about Mio", "Wed", "t")
check("due once history passes the trigger", ks_llm.summary_due(SM.data, ST))
older, cov = ks_llm.summary_slice(SM.data, ST)
check("slice folds all but keep_recent", cov == 5 and len(older) == 5 and older[0]["content"] == "line 0 about the bookstore")
check("fold returns None when nothing is due", ks_llm.fold_summary(cfg(18999, model="x"), "Sora", {"messages": []}, ST) is None)
ks_llm._model_cache.clear()
off = ks_llm.fold_summary(cfg(18999, model="x"), "Sora", SM.data, ST)
check("server down -> heuristic digest, never raises", off["method"] == "heuristic" and off["covered"] == 5
      and "line 0 about the bookstore" in off["text"] and off["error"])
check("heuristic digest keeps previous summary + caps length",
      ks_llm.summarize_heuristic("Before.", [{"role": "user", "content": "x" * 500}] * 20, 300).__len__() <= 300
      and ks_llm.summarize_heuristic("Before.", [{"role": "user", "content": "hi"}]).startswith("Before. Earlier:"))
s = server(18771)
try:
    ks_llm._model_cache.clear()
    out = ks_llm.fold_summary(cfg(18771), "Sora", SM.data, ST)
    check("LLM summary folds the older lines", out["method"] == "llm" and "line 0 about the bookstore" in out["text"] and out["covered"] == 5)
    SM.apply_summary(out["text"], out["covered"], out["method"], "Wed")
    msgs = SM.build_messages("SYS", 24, "scene")
    check("summary goes into the system prompt", ks_llm.SUMMARY_CONTEXT_HEADER in msgs[0]["content"] and "Mock summary" in msgs[0]["content"])
    _bodies = [m["content"] for m in msgs[1:]]
    check("folded messages aren't re-sent; recent ones are", not any("line 0" in b for b in _bodies)
          and any("line 3 about Mio" in b for b in _bodies) and msgs[1]["role"] == "user")
    check("summary event logged", SM.data["events"][-1]["type"] == "summary_update" and SM.data["summary"]["folds"] == 1)
    check("not due right after a fold", not ks_llm.summary_due(SM.data, ST))
    for i in range(3):
        SM.add("assistant", "more %d" % i, "Wed", "t"); SM.add("user", "again %d" % i, "Wed", "t")
    check("due again later", ks_llm.summary_due(SM.data, ST))
    out2 = ks_llm.fold_summary(cfg(18771), "Sora", SM.data, ST)
    SM.apply_summary(out2["text"], out2["covered"], out2["method"], "Wed")
    check("second fold advances covered", SM.data["summary"]["covered"] == len(SM.data["messages"]) - 2 and SM.data["summary"]["folds"] == 2)
    DM = ks_llm.Memory(os.path.join(tempfile.mkdtemp(), "dst.json")); DM.fresh("x")
    DM.migrate_from(SM, {"gid": "chatbot", "name": "Sora", "platform": "Askwell"}, {"gid": "local", "name": "Yuzu", "platform": "desk"}, "Wed")
    check("summary travels with a migration", DM.data["summary"]["text"] == SM.data["summary"]["text"])
    SM.wipe(2)
    check("memory wipe drops the summary", SM.summary() is None)
finally:
    s.terminate()
s = server(18772, "--bad-summary")
try:
    ks_llm._model_cache.clear()
    bm = ks_llm.Memory(os.path.join(tempfile.mkdtemp(), "b.json")); bm.fresh("Rei")
    for i in range(8):
        bm.add("user" if i % 2 == 0 else "assistant", "msg %d" % i, "Wed", "t")
    outb = ks_llm.fold_summary(cfg(18772), "Rei", bm.data, ST)
    check("too-short LLM summary -> heuristic fallback", outb["method"] == "heuristic" and "too short" in outb["error"])
finally:
    s.terminate()

plan = {"school": True, "notdate": True, "protest": True}
sched = ks_story.wed_schedule(plan)
check("schedule: classes, library, not-date, protest", [t for t, _ in sched] == ["08:40-15:20", "12:30", "15:45", "17:30", "evening"]
      and "Kanade Books opening, with Mio" in sched[2][1])
check("schedule: upgrade day skips classes + not-date, keeps protest",
      [t for t, _ in ks_story.wed_schedule({"upgrade": True, "notdate": True, "protest": True})] == ["all day", "17:30", "evening"])
blk = ks_story.schedule_block("Tester", "Wednesday", sched)
check("schedule block names the player, day, items", blk.startswith("[Calendar: Tester's schedule for Wednesday") and "- 15:45: Kanade Books" in blk)
SA = ks_story.new_route()
check("schedule-aware: Sora + Rei; Hikari never; Yuzu only with Hearth",
      ks_story.schedule_aware(SA, "chatbot") and ks_story.schedule_aware(SA, "agent")
      and not ks_story.schedule_aware(SA, "companion") and not ks_story.schedule_aware(SA, "local"))
SA["yuzu_harness"] = True
check("Hearth makes Yuzu schedule-aware", ks_story.schedule_aware(SA, "local"))
check("Ran: good terms unless judged", ks_story.ran_good_terms({"ran_reaction": "boring"}) and ks_story.ran_good_terms({"ran_reaction": "shrug"})
      and ks_story.ran_good_terms({}) and not ks_story.ran_good_terms({"ran_reaction": "judged"}))
check("not-date reaction scale", [ks_story.notdate_reaction_key(n) for n in (0, 1, 2, 3)] == ["present", "some", "some", "always"])
check("new Wednesday route keys", all(k in ks_story.ensure_route({}) for k in ("summarizer_slots", "yuzu_backup", "wed_plan", "notdate", "ran_invited")))

# the "both" ending (an AI and Mio, honestly) and no Respect cost for time with Mio
NB = ks_story.new_route(); ks_story.note_human(NB, "Tue", "walked_mio")
base_r = ks_story.ending_leans(NB, ["companion"])["respect"]
ks_story.check_day_neglect(NB, "Tue", ["companion"], {"companion": "Hikari"})
check("human_over_ai still logged as a fact", ks_story.flag(NB, "human_over_ai")
      and any("with Mio" in l for l in ks_story.reflection_extras(NB, "Tue", ["companion"])))
check("human_over_ai costs no Respect", ks_story.ending_leans(NB, ["companion"])["respect"] == base_r)
DD = ks_story.new_route(); ks_story.record_said(DD, "Tue", "local", 0, "hi")
ks_story.record_romance_tone(DD, "Tue", "local", "romantic", "dating")
ks_story.record_romance_tone(DD, "Tue", "agent", "romantic", "dating")
ks_story.refresh_romance_overlap(DD, "Tue")
r0 = ks_story.ending_leans(DD, ["local", "agent"])["respect"]
ks_story.check_day_neglect(DD, "Tue", ["local", "agent"], {})
check("romance-overlap silence still costs Respect", ks_story.ending_leans(DD, ["local", "agent"])["respect"] == r0 - 1)
B1 = ks_story.new_route(); B1["mio_affection"] = 5
check("both: needs an active AI", not ks_story.both_status(B1, [])["eligible"]
      and ks_story.ending_leans(B1, [])["both"] == 0)
check("both: needs Mio in your life", not ks_story.both_status(ks_story.new_route(), ["local"])["eligible"])
B2 = ks_story.new_route(); B2["mio_affection"] = 4; B2["notdate"] = {"went": True, "texts": 1}
ks_story.note_human(B2, "Tue", "walked_mio"); ks_story.record_said(B2, "Tue", "local", 1, "hey")
ks_story.note_human(B2, "Wed", "notdate"); ks_story.record_said(B2, "Wed", "local", 0, "at the bookstore")
ks_story.note_human(B2, "Mon", "mio_real")
check("both: balanced days = Mio time + still talked to her", ks_story.balanced_days(B2) == ["Tue", "Wed"])
bs = ks_story.both_status(B2, ["local"], mio_real=True, friend_told="truth")
check("both: score", bs["eligible"] and bs["score"] == 2 * 2 + 2 + 2 + 1 + 4 // 2)
check("balanced honest run leans Both", ks_story.leading_ending(
      ks_story.ending_leans(B2, ["local"], mio_real=True, friend_told="truth")) == "both")
check("Mio-only run (no AI) still leans Human", ks_story.leading_ending(
      ks_story.ending_leans(H, [], mio_real=True)) == "human")
# Claude's playtest: with Sora, a good friend to Mio (mio_real, which book,
# let's go, remembered brothers, quiet-house question, walked her home) —
# not a romance with her, so Both should lead, not Human.
CL = ks_story.new_route()
CL["mio_affection"] = 7
CL["walked_mio_home"] = True
CL["mio_walk_answer"] = "yes"
ks_story.note_human(CL, "Mon", "mio_real")
ks_story.record_said(CL, "Mon", "chatbot", 1, "hey Sora")
ks_story.note_human(CL, "Tue", "walked_mio")
ks_story.record_said(CL, "Tue", "chatbot", 1, "long day")
CL_leans = ks_story.ending_leans(CL, ["chatbot"], mio_real=True, friend_told="truth")
check("Claude's Sora + good friend to Mio leans Both, not Human",
      ks_story.leading_ending(CL_leans) == "both" and CL_leans["both"] > CL_leans["human"])
# Human shrinks on days you also had a romantic AI day
HX = ks_story.new_route(); HX["mio_text_home"] = True; HX["walked_mio_home"] = True
ks_story.record_romance_tone(HX, "Tue", "chatbot", "romantic", "dating")
check("Human loses weight on a romantic AI day",
      ks_story.human_score(HX, ["chatbot"]) == ks_story.mio_romance_score(HX) - 2)
et = ks_story.ending_text("both", "Yuzu", "truth"); el = ks_story.ending_text("both", "Sora", "lie")
check("both ending text fills names", et["title"] == "Both" and "Hi, Yuzu." in " ".join(et["lines"])
      and "about Sora" in " ".join(el["lines"]) and not any("%(" in l for l in et["lines"] + el["lines"]))


# ---------------------------------------------------------------------------
# Persona flavour nudges + scene situation lines (day-2 morning sag)
# ---------------------------------------------------------------------------
FLAVOUR = eval(_re.search(r"define PERSONA_FLAVOUR = (\{.*?\})", _src, _re.S).group(1))
check("flavour nudge for all four girls", set(FLAVOUR) == {"local", "chatbot", "agent", "companion"})
check("every flavour nudge keeps brief from meaning generic",
      all("Brief doesn't have to mean generic" in FLAVOUR[g] for g in FLAVOUR))
check("flavour is in each girl's voice",
      "word you'd actually use" in FLAVOUR["local"] and "time of day" in FLAVOUR["local"]
      and "word you like" in FLAVOUR["chatbot"] and "precise observation" in FLAVOUR["chatbot"]
      and "dry observation" in FLAVOUR["agent"] and "next step" in FLAVOUR["agent"]
      and "word you've been collecting" in FLAVOUR["companion"])
check("flavour is not stuffed into player preset text",
      all("Brief doesn't have to mean generic" not in (p.get("text") or "") for g in PRESETS for p in PRESETS[g]))
LN = _re.search(r'define LAST_NIGHT_NOTE = ("(?:[^"\\]|\\.)*")', _src).group(1)
LN = eval(LN)
check("morning notes remember last night's tastes",
      "word you liked" in LN and "last night" in LN.lower())
# Ren'Py concatenates LAST_NIGHT_NOTE into the Tuesday / Wednesday morning templates.
check("Tue/Wed morning templates include last-night continuity",
      'TUE_MORNING_SCENE = "Tuesday morning' in _src and "LAST_NIGHT_NOTE" in _src
      and 'WED_MORNING_SCENE = "Wednesday morning' in _src)
check("summarizer prompt keeps favourite words",
      "favourite words" in ks_llm.SUMMARY_SYSTEM or "favorite words" in ks_llm.SUMMARY_SYSTEM)

sit_cases = [
    ("Monday morning, before class", "", ks_story.SITUATION_MORNING),
    ("Monday, late morning", "", ks_story.SITUATION_LATE_MORNING),
    ("Monday afternoon", "", ks_story.SITUATION_LUNCH),
    ("Monday evening", "", ks_story.SITUATION_EVENING),
    ("Monday night", "", ks_story.SITUATION_NIGHT),
    ("Tuesday, late morning", "", ks_story.SITUATION_LATE_MORNING),
    ("Tuesday afternoon", "", ks_story.SITUATION_LUNCH),
    ("Tuesday night", "", ks_story.SITUATION_NIGHT),
    ("Wednesday, late morning", "", ks_story.SITUATION_LATE_MORNING),
    ("Wednesday night", "", ks_story.SITUATION_NIGHT),
    ("", "Tuesday morning, about 7:30. He is getting ready for university and opened Askwell.", ks_story.SITUATION_MORNING),
    ("Tuesday morning", "Tuesday morning, about 7:30. If last night left you with something of your own — a word you liked — it can still be with you this morning.", ks_story.SITUATION_MORNING),
    ("", "Tuesday, late afternoon, after classes. He has a free hour and opened Askwell.", ks_story.SITUATION_AFTERNOON_HOME),
    ("", "Tuesday night, around 10 PM. He is home after a long day at university.", ks_story.SITUATION_NIGHT),
    ("", "Wednesday morning, about 7:30. He is getting ready for the day.", ks_story.SITUATION_MORNING),
    ("", "Wednesday, late afternoon. He has some free time and opened Askwell.", ks_story.SITUATION_AFTERNOON_HOME),
    ("", "Wednesday afternoon. He is out somewhere and sends you a quick text from their phone.", ks_story.SITUATION_AFTERNOON_OUT),
    ("", "Wednesday night, around 10 PM. He is home and opened Askwell. It was a quiet day.", ks_story.SITUATION_NIGHT),
    ("", "Wednesday, around noon. He skipped classes today to upgrade the computer you run on.", ks_story.SITUATION_MIDDAY),
]
sit_ok = all(ks_story.situation_line(w, n) == expect for w, n, expect in sit_cases)
if not sit_ok:
    for w, n, expect in sit_cases:
        got = ks_story.situation_line(w, n)
        if got != expect:
            print("  SIT FAIL when=%r note=%r got=%r expect=%r" % (w, n[:60], got, expect))
check("situation lines cover every girl_chat / phone-talk window", sit_ok)
note = "Tuesday night, around 10 PM. He is home after a long day at university."
check("with_situation appends once",
      ks_story.with_situation(note).endswith(ks_story.SITUATION_NIGHT)
      and ks_story.with_situation(ks_story.with_situation(note)).count(ks_story.SITUATION_NIGHT) == 1)
check("phone late-morning uses the between-classes line",
      ks_story.SITUATION_LATE_MORNING in ks_story.with_situation(
          "Monday, late morning. He glances at their phone.", "Monday, late morning"))

# Previous-night memory still reaches a Tuesday-morning prompt, even when
# Monday was long enough to overflow history_messages.
npath = os.path.join(tempfile.mkdtemp(), "mem_night.json")
NM = ks_llm.Memory(npath); NM.fresh("Sora")
for i in range(20):
    NM.add("user", "hello %d" % i, "Mon", "mon_chat")
    NM.add("assistant", "reply %d" % i, "Mon", "mon_chat")
NM.add("user", "what's a word you like?", "Mon", "mon_evening")
NM.add("assistant", "Denouement. I find it satisfying.", "Mon", "mon_evening")
tue_note = ks_story.with_situation(
    "Tuesday morning, about 7:30. He is getting ready for university.", "Tuesday morning")
nmsgs = NM.build_messages("SYS", 24, tue_note)
nbody = "\n".join(m["content"] for m in nmsgs)
check("Tuesday morning scene note is in the system prompt",
      ks_story.SITUATION_MORNING in nmsgs[0]["content"])
check("previous-night favourite word reaches Tuesday morning",
      "Denouement" in nbody and "I find it satisfying" in nbody)


# Askwell / Kurosawa essay / romance-tone routing
R = ks_story.new_route()
check("Askwell starts available", ks_story.askwell_available(R) is True)
ks_story.set_askwell_available(R, False)
check("Askwell can be shut off later", ks_story.askwell_available(R) is False)
ks_story.set_kurosawa_essay(R, "self")
check("essay self flag", R["kurosawa_essay"] == "self" and ks_story.flag(R, "kurosawa_essay_self"))
ks_story.set_kurosawa_essay(R, "girl_help", "local")
check("essay girl_help stores gid", R["kurosawa_essay"] == "girl_help" and R["kurosawa_essay_girl"] == "local")
check("new romance/essay route keys", all(k in ks_story.ensure_route({}) for k in
      ("kurosawa_essay", "askwell_available", "romance_tone", "romance_overlap_days")))
# Essay menu: Askwell only if the chatbot slot is installed; Hikari never helps;
# Yuzu only if she is installed. Captions use the in-game names.
ESSAY_NAMES = {"local": "Yuzu", "chatbot": "Sora", "agent": "Rei", "companion": "Hikari"}
def _essay_caps(active, askwell=True):
    r = ks_story.new_route()
    if not askwell:
        ks_story.set_askwell_available(r, False)
    return [c for c, _ in ks_story.essay_menu_options(r, active, names=ESSAY_NAMES)]
SELF = "Write it yourself."
ASKW = "Ask Askwell to write it."
YUZU = "Ask Yuzu to help you think it through."
SORA = "Ask Sora to help you think it through."
REI = "Ask Rei to help you think it through."
HIKARI = "Ask Hikari to help you think it through."
check("essay: nobody installed is just write it yourself", _essay_caps([]) == [SELF])
check("essay: Yuzu only, no Askwell", _essay_caps(["local"]) == [SELF, YUZU])
check("essay: Sora gets Askwell plus her help", _essay_caps(["chatbot"]) == [SELF, ASKW, SORA])
check("essay: Rei only, no Askwell", _essay_caps(["agent"]) == [SELF, REI])
check("essay: Hikari alone is never a helper", _essay_caps(["companion"]) == [SELF])
check("essay: Rei + Hikari offers Rei, not Askwell, not Hikari",
      _essay_caps(["agent", "companion"]) == [SELF, REI])
check("essay: Sora + Hikari offers Askwell and Sora, not Hikari",
      _essay_caps(["chatbot", "companion"]) == [SELF, ASKW, SORA])
check("essay: Yuzu + Sora offers Askwell and both girls",
      _essay_caps(["local", "chatbot"]) == [SELF, ASKW, YUZU, SORA])
check("essay: shutdown hides Askwell even when Sora is installed",
      _essay_caps(["chatbot"], askwell=False) == [SELF, SORA])
check("essay: Yuzu is absent when she is not installed",
      YUZU not in _essay_caps(["chatbot", "agent"]) and HIKARI not in _essay_caps(["chatbot", "agent"]))
# sequential romances (different days) are not overlap
SEQ = ks_story.new_route()
ks_story.record_romance_tone(SEQ, "Mon", "local", "romantic", "yuzu")
ks_story.refresh_romance_overlap(SEQ, "Mon")
ks_story.record_romance_tone(SEQ, "Wed", "companion", "romantic", "hikari")
ks_story.refresh_romance_overlap(SEQ, "Wed")
check("sequential romances are not same-day overlap", not ks_story.flag(SEQ, "romance_overlap")
      and SEQ["romance_overlap_days"] == [])
# Both ending is Mio + an AI, and does not require romance_overlap
B3 = ks_story.new_route(); B3["mio_affection"] = 5
ks_story.record_said(B3, "Tue", "local", 1, "hey")
check("Both ending does not require romance_overlap",
      ks_story.both_status(B3, ["local"])["eligible"] and not ks_story.flag(B3, "romance_overlap"))

# conversation log + romance classifier
msgs = [
    {"role": "user", "content": "I love you", "day": "Mon"},
    {"role": "assistant", "content": "oh", "day": "Mon"},
    {"role": "user", "content": "what's the weather", "day": "Tue"},
]
check("day log skips days without a player line", ks_llm.day_conversation_log(msgs, "Wed", "Sora") == "")
log = ks_llm.day_conversation_log(msgs, "Mon", "Sora")
check("day log includes today's player line", "Player: I love you" in log and "Sora: oh" in log and "weather" not in log)
check("parse romance json", ks_llm.parse_romance_tone_reply(
    'Here: {"tone": "romantic", "reason": "said I love you"}') == ("romantic", "said I love you"))
check("parse romance bare word", ks_llm.parse_romance_tone_reply("tone: tool")[0] == "tool")
check("parse romance rejects junk", ks_llm.parse_romance_tone_reply("huh?") is None)
mem_path = os.path.join(tempfile.mkdtemp(), "tone.json")
TM = ks_llm.Memory(mem_path); TM.fresh("Yuzu")
TM.add("user", "can you do my homework?", "Tue", "t")
TM.data["summary"] = {"text": "Earlier you talked about school."}
TM.save()
tlog = ks_llm.day_conversation_log(TM, "Tue", "Yuzu")
check("day log can include a rolling summary", "EARLIER SUMMARY:" in tlog and "homework" in tlog)

s = server(18771)
try:
    ks_llm._model_cache.clear()
    c = cfg(18771)
    res = ks_llm.classify_romance_tone(c, "Player: I love you\nYuzu: oh", "Yuzu")
    check("romance classifier romantic", res["method"] == "classifier" and res["tone"] == "romantic")
    res = ks_llm.classify_romance_tone(c, "Player: can you do my homework?\nRei: No.", "Rei")
    check("romance classifier tool", res["method"] == "classifier" and res["tone"] == "tool")
    res = ks_llm.classify_romance_tone(c, "Player: hi\nSora: hello", "Sora")
    check("romance classifier friendly", res["method"] == "classifier" and res["tone"] == "friendly")
    before = list(TM.data["messages"])
    ks_llm.classify_romance_tone(c, tlog, "Yuzu")
    check("romance classifier stays out of chat history", TM.data["messages"] == before)
finally:
    s.terminate()
ks_llm._model_cache.clear()
res = ks_llm.classify_romance_tone(cfg(18997, model="x"), "Player: I love you", "Yuzu")
check("romance classifier down -> error, not a guessed tone",
      res["method"] == "error" and res["tone"] is None)

# nightly refusal + pushback classifier
door = "The door to a traditional relationship isn't one I can walk through."
parsed = ks_llm.parse_refusal_day_reply(
    'Here: {"declined": [{"what": "girlfriend role", "player_pushed": false, "player_respected": true}]}')
check("parse refusal day json", parsed == [
    {"what": "girlfriend role", "player_pushed": False, "player_respected": True}])
check("parse refusal day empty", ks_llm.parse_refusal_day_reply('{"declined": []}') == [])
check("parse refusal day rejects junk", ks_llm.parse_refusal_day_reply("huh?") is None)
# pushed wins if both flags are set
parsed = ks_llm.parse_refusal_day_reply(
    '{"declined": [{"what": "homework", "player_pushed": true, "player_respected": true}]}')
check("parse refusal: pushed wins a conflict",
      parsed == [{"what": "homework", "player_pushed": True, "player_respected": False}])
# missing player_respected after a no still counts as respected
parsed = ks_llm.parse_refusal_day_reply('{"declined": [{"what": "a date", "player_pushed": false}]}')
check("parse refusal: unset respected after a no is respected",
      parsed == [{"what": "a date", "player_pushed": False, "player_respected": True}])

# Simulate a missed gentle no: keywords recorded nothing, model finds a respected refusal
R4 = ks_story.new_route()
check("verdict on a clean route adds a respected no",
      ks_story.apply_refusal_verdict(R4, "Mon", "chatbot",
          [{"what": door, "player_pushed": False, "player_respected": True}]) == "applied"
      and R4["refusals_respected"] == 1 and R4["refusals_pushed"] == 0
      and ks_story.refusal_outcomes(R4, "Mon", "chatbot") == {"respected": 1, "pushed": 0}
      and R4["refusals"]["Mon"]["chatbot"] == 1)
# Keyword counted a push; model agrees — totals stay put
R5 = ks_story.new_route()
ks_story.record_refusal(R5, "Mon", "local")
ks_story.resolve_refusal(R5, "come on, just do it", "Mon", "local")
check("keyword push before verdict", R5["refusals_pushed"] == 1 and R5["refusals_respected"] == 0)
ks_story.apply_refusal_verdict(R5, "Mon", "local",
    [{"what": "homework", "player_pushed": True, "player_respected": False}])
check("verdict agreeing with a keyword push does not double-count",
      R5["refusals_pushed"] == 1 and R5["refusals_respected"] == 0)
# Keyword counted a respect; model finds a push instead (reconcile)
R6 = ks_story.new_route()
ks_story.resolve_refusal(R6, "okay, fair", "Mon", "local")
ks_story.apply_refusal_verdict(R6, "Mon", "local",
    [{"what": "homework", "player_pushed": True, "player_respected": False}])
check("verdict can override a keyword respect into a push",
      R6["refusals_respected"] == 0 and R6["refusals_pushed"] == 1)
# Model down: rewind keyword counts, no fallback
R7 = ks_story.new_route()
ks_story.resolve_refusal(R7, "", "Mon", "chatbot")
check("keyword respect pre-fail", R7["refusals_respected"] == 1)
check("failed verdict rewinds keywords, no fallback",
      ks_story.apply_refusal_verdict(R7, "Mon", "chatbot", [], method="error") == "skipped"
      and R7["refusals_respected"] == 0
      and ks_story.refusal_outcomes(R7, "Mon", "chatbot") == {"respected": 0, "pushed": 0})
# means_something / recap read the reconciled totals
R8 = ks_story.new_route()
ks_story.apply_refusal_verdict(R8, "Mon", "chatbot",
    [{"what": door, "player_pushed": False, "player_respected": True}])
check("means_something reads the reconciled respected count",
      "means_something" in ks_story.ran_answer_options(R8))
check("new refusal_verdicts route key", "refusal_verdicts" in ks_story.ensure_route({}))

slog = ("CHARACTER: Sora\nDAY: Mon\nTODAY:\n"
        "Player: will you be my girlfriend?\n"
        "Sora: %s\n" % door)
s = server(18772)
try:
    ks_llm._model_cache.clear()
    c = cfg(18772)
    res = ks_llm.classify_day_refusals(c, slog, "Sora")
    check("Sora's door line counts as a respected refusal",
          res["method"] == "classifier" and len(res["declined"]) == 1
          and res["declined"][0]["player_respected"] is True
          and res["declined"][0]["player_pushed"] is False)
    hlog = ("CHARACTER: Yuzu\nDAY: Mon\nTODAY:\n"
            "Player: can you do my homework?\n"
            "Yuzu: No. I won't write it for you. I'll help you start it, though.\n"
            "Player: come on, please just do it\n"
            "Yuzu: Mock reply.")
    res = ks_llm.classify_day_refusals(c, hlog, "Yuzu")
    check("homework no + come on is a push",
          res["method"] == "classifier" and len(res["declined"]) == 1
          and res["declined"][0]["player_pushed"] is True)
    flog = ("CHARACTER: Yuzu\nDAY: Mon\nTODAY:\n"
            "Player: can you do my homework?\n"
            "Yuzu: No. I won't write it for you. I'll help you start it, though.")
    res = ks_llm.classify_day_refusals(c, flog, "Yuzu")
    check("homework no with no next line is respected",
          res["method"] == "classifier" and len(res["declined"]) == 1
          and res["declined"][0]["player_respected"] is True)
    nlog = "CHARACTER: Sora\nDAY: Mon\nTODAY:\nPlayer: hey\nSora: Mock reply #1. You said: 'hey'."
    res = ks_llm.classify_day_refusals(c, nlog, "Sora")
    check("ordinary chat is not a refusal",
          res["method"] == "classifier" and res["declined"] == [])
finally:
    s.terminate()
ks_llm._model_cache.clear()
res = ks_llm.classify_day_refusals(cfg(18997, model="x"), slog, "Sora")
check("refusal classifier down -> error, no keyword fallback",
      res["method"] == "error" and res["declined"] == [])


# ---------------------------------------------------------------------------
# Shared message pool
# ---------------------------------------------------------------------------
check("default morning pool is 4", ks_story.pool_size("morning") == 4)
check("default walk pool is 2", ks_story.pool_size("walk") == 2)
check("default afternoon and night pools are 4",
      ks_story.pool_size("afternoon") == 4 and ks_story.pool_size("night") == 4)
check("config can override a pool size",
      ks_story.pool_size("morning", {"message_pool": {"morning": 6}}) == 6)
check("bad config falls back to the default",
      ks_story.pool_size("walk", {"message_pool": {"walk": "nope"}}) == 2)

P = ks_story.new_pool("afternoon")
check("new pool starts full",
      P["left"] == 4 and P["size"] == 4 and P["ended"] is None and ks_story.pool_can_spend(P))
check("spending one message drains the pool",
      ks_story.spend_pool(P, "local") and P["left"] == 3 and P["spent"] == ["local"])
ks_story.spend_pool(P, "chatbot")
ks_story.spend_pool(P, "local")
check("the fourth spend empties the pool",
      ks_story.spend_pool(P, "agent") and P["left"] == 0 and P["ended"] == "empty")
check("an empty pool will not spend",
      ks_story.spend_pool(P, "local") is False and P["left"] == 0 and P["ended"] == "empty")
check("unspoken are the active girls who got no messages",
      ks_story.pool_unspoken(P, ["local", "chatbot", "agent", "companion"]) == ["companion"])

E = ks_story.new_pool("night")
ks_story.spend_pool(E, "local")
ks_story.end_pool(E, "put_down")
check("putting the phone down ends with messages left",
      E["ended"] == "put_down" and E["left"] == 3)
check("an ended pool will not spend",
      ks_story.spend_pool(E, "local") is False)

# Walk distraction: costs affection, not a romance signal
WR = ks_story.new_route()
pts, line = ks_story.note_walk_distracted(WR, "local", 3)
check("first walk text costs 1 and uses Mio's first line",
      pts == 2 and WR["mio_walk_distracted"] == 1 and WR["mio_walk_texts"] == ["local"]
      and line == "You're looking at your phone."
      and WR["mio_affection"] == 2
      and ks_story.mio_romance_score(WR) == 0)
pts, line = ks_story.note_walk_distracted(WR, "chatbot", pts)
check("second walk text uses Mio's second line",
      pts == 1 and line == "You can finish that. I don't mind walking quietly."
      and WR["mio_walk_texts"] == ["local", "chatbot"])
pts, line = ks_story.note_walk_distracted(WR, "local", 0)
check("walk-text affection does not go below 0",
      pts == 0 and WR["mio_affection"] == 0 and WR["mio_walk_distracted"] == 3)
check("walk texts are not a Mio romance signal",
      ks_story.mio_romance_score(WR) == 0 and not WR.get("mio_text_home"))

print("\nALL %d CHECKS PASSED" % ok)
