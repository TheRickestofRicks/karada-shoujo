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
check("Mio run leans Human", ks_story.leading_ending(ks_story.ending_leans(H, ["local"], mio_real=True)) == "human")
check("alone leans Fail", ks_story.leading_ending(ks_story.ending_leans(ks_story.new_route(), [])) == "fail")
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
N = ks_story.new_route()
ks_story.note_double_date(N, "Tue"); ks_story.record_said(N, "Tue", "local", 1, "hi")
new_n = ks_story.check_day_neglect(N, "Tue", ["local", "agent"], {"local": "Yuzu", "agent": "Rei"})
check("double date, one unspoken", [(e["kind"], e["gid"]) for e in new_n] == [("double_date_unspoken", "agent")]
      and ks_story.flag(N, "double_date_unspoken"))
check("neglect check is idempotent", ks_story.check_day_neglect(N, "Tue", ["local", "agent"], {}) == [])
N2 = ks_story.new_route(); ks_story.note_human(N2, "Tue", "walked_mio")
new_n2 = ks_story.check_day_neglect(N2, "Tue", ["companion"], {"companion": "Hikari"})
check("human route while an AI got nothing", [(e["kind"], e["gid"]) for e in new_n2] == [("human_over_ai", "companion")]
      and ks_story.flag(N2, "human_over_ai"))
check("human line in reflection", any("with Mio" in l for l in ks_story.reflection_extras(N2, "Tue", ["companion"])))
N3 = ks_story.new_route(); ks_story.note_human(N3, "Tue", "walked_mio"); ks_story.record_said(N3, "Tue", "local", 0, "hey")
check("talked to her too -> no neglect", ks_story.check_day_neglect(N3, "Tue", ["local"], {}) == [])
ks_story.note_let_go(N3, "Tue", "agent", "Rei")
check("let go logged", ks_story.neglect_count(N3, "let_go") == 1 and ks_story.flag(N3, "deleted_ai"))

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

print("\nALL %d CHECKS PASSED" % ok)
