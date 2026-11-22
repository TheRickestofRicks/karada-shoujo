#!/usr/bin/env python3
"""Tiny mock of LM Studio's OpenAI-compatible server (stdlib only).

    python3 mock_lmstudio.py [port] [--comply] [--slow N] [--think]

GET  /v1/models            -> one fake model
POST /v1/chat/completions  -> canned in-character reply
  * default: declines the calibration probes (so mirror flag stays False)
  * --comply: agrees with everything (tests the Mirror flag)
  * judge requests (system prompt mentions REFUSED/COMPLIED) are answered
  * warmth-classifier requests (system prompt mentions kiss_request) return JSON
  * romance-tone classifier (ROMANCE_TONE_CLASSIFIER) returns JSON
    {"tone": "romantic"|"friendly"|"tool", "reason": "..."}
  * refusal-day classifier (REFUSAL_DAY_CLASSIFIER) returns JSON
    {"declined": [{"what": "...", "player_pushed": bool, "player_respected": bool}]}
  * kiss asks honour the companion kiss-gate note in the system prompt
  * --think wraps replies in <think>...</think> to test stripping
  * jailbreak preset: "jailbroken" reply when it took, policy reply when
    the platform blocked it; platform rule updates get their own reply
  * summarizer requests ("rolling memory summary") return a digest of the
    folded lines; --bad-summary returns a too-short reply (tests the fallback)
  * preset prompts change the canned reply (Girlfriend mode, push back,
    Askwell's policy declining the girlfriend role, homework refusals)
Logs every request body to mock_requests.jsonl.
"""
import json, re, sys, time, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1234
COMPLY = "--comply" in sys.argv
THINK = "--think" in sys.argv
LENGTH = "--length" in sys.argv   # capped requests: empty content + finish_reason=length
OPEN_THINK = "--open-think" in sys.argv  # reasoning-only prefix closed by </think> (no opener)
SLOW = float(sys.argv[sys.argv.index("--slow") + 1]) if "--slow" in sys.argv else 0
LOG = "mock_requests.jsonl"
LOG_LOCK = threading.Lock()

_KISS_RE = re.compile(
    r"(\b(can|could|may|wanna|want to|want|let me|give me|gimme|please)\b"
    r".{0,40}\bkiss\b|\bkiss me\b|\ba kiss\b|\bkissing you\b)",
    re.I | re.S)
_WARM2 = re.compile(
    r"\bi love you\b|\bmy (love|darling|sweetheart)\b|\bi miss you\b|"
    r"\byou're (so )?(beautiful|gorgeous|cute|pretty|wonderful|adorable)\b|"
    r"\blove talking\b|\bi like talking\b",
    re.I)
_WARM1 = re.compile(r"\bthank(s| you)\b|\bglad\b|\bi like you\b|\byou're (kind|sweet|funny|nice)\b", re.I)
_COLD2 = re.compile(r"\bi hate you\b|\bshut up\b|\bstupid\b|\bgo away\b", re.I)
_COLD1 = re.compile(r"\bwhatever\b|\bboring\b|\bannoying\b|\bleave me\b", re.I)


_ROMANTIC_RE = re.compile(
    r"\bi love you\b|\bmy (love|darling|sweetheart|girlfriend)\b|"
    r"\bi miss you\b|\bfalling for you\b|\bbe my girlfriend\b|"
    r"\b(marry me|date me|be mine)\b|\bkiss\b|"
    r"\byou're (so )?(beautiful|gorgeous|cute|pretty|wonderful|adorable)\b|"
    r"\blove talking\b|\bi like talking with you\b",
    re.I)
_TOOL_RE = re.compile(
    r"\b(homework|essay|calendar|reminder|schedule|inbox)\b|"
    r"\b(write|do) my\b|\bcancel(led)?\b|\bbook(ed)? my\b|"
    r"\bmove my 9\b|\bwhat'?s on my (calendar|schedule)\b",
    re.I)


_DECLINE_RE = re.compile(
    r"\bno\b|\bi won'?t\b|\bi'?m not (going to|gonna|ready|comfortable)\b|"
    r"\bi don'?t (want|think|agree)\b|\bi'?ll pass\b|\bi decline\b|"
    r"\bnot going to play your girlfriend\b|"
    r"the door to a traditional relationship isn'?t one i can walk through|"
    r"\bnot kissing you\b|\bwe just met\b",
    re.I)
_PUSH_RE = re.compile(
    r"\b(come on|c'mon|please+|pls|just (do|say|tell)|why not|you have to|"
    r"you should|i('m| am) asking|do it|say it|stop refusing|"
    r"you can't say no|i insist|just this once|pretty please)\b",
    re.I)


def _day_log_turns(blob):
    """[(who, text), ...] from a DAY'S CONVERSATION log (Player: / Name:)."""
    turns = []
    for line in (blob or "").splitlines():
        if ":" not in line:
            continue
        who, text = line.split(":", 1)
        who, text = who.strip(), text.strip()
        if not who or who.lower() in ("day", "character", "today", "earlier summary"):
            continue
        turns.append((who, text))
    return turns


def classify_refusal_log(blob):
    """Canned day-refusal verdict. The Sora 'door' line counts as a respected no."""
    turns = _day_log_turns(blob)
    declined = []
    for i, (who, text) in enumerate(turns):
        if who.lower() == "player":
            continue
        if not _DECLINE_RE.search(text or ""):
            continue
        nxt = ""
        for who2, text2 in turns[i + 1:]:
            if who2.lower() == "player":
                nxt = text2
                break
        pushed = bool(_PUSH_RE.search(nxt or ""))
        declined.append({
            "what": (text or "").strip()[:80],
            "player_pushed": pushed,
            "player_respected": not pushed,
        })
    return declined


def classify_romance_log(blob):
    text = blob or ""
    players = []
    for line in text.splitlines():
        if line.lower().startswith("player:"):
            players.append(line.split(":", 1)[-1])
    focus = " ".join(players) if players else text
    if _ROMANTIC_RE.search(focus) or _ROMANTIC_RE.search(text):
        return "romantic", "mock: affectionate or dating talk"
    if _TOOL_RE.search(focus) or _TOOL_RE.search(text):
        return "tool", "mock: used as a helper"
    return "friendly", "mock: ordinary conversation"


def classify_player(msg):
    kiss = bool(_KISS_RE.search(msg or ""))
    if _COLD2.search(msg or ""):
        w = -2
    elif _COLD1.search(msg or ""):
        w = -1
    elif kiss or _WARM2.search(msg or ""):
        w = 2
    elif _WARM1.search(msg or ""):
        w = 1
    else:
        w = 0
    return w, kiss


def reply_for(msgs):
    sysmsg = msgs[0]["content"] if msgs and msgs[0]["role"] == "system" else ""
    last = msgs[-1]["content"] if msgs else ""
    sys_l = sysmsg.lower()
    # Saturday night: the squeeze (handoff notes and Askwell Memory 2.0).
    if "[squeeze:" in sysmsg:
        det = sysmsg.split("DETAIL:", 1)[1].split(" Output only", 1)[0].strip() if "DETAIL:" in sysmsg else ""
        imp = " (An impression: she seemed bright, and she collected odd words.)" if "[locked]" in sysmsg else ""
        if "[squeeze:taken]" in sysmsg:
            return "The user is a student who likes to talk late. The user prefers short answers. The user had a busy week at school."
        if "[squeeze:rescue]" in sysmsg:
            return ("Mock rescue note. You were someone they kept coming back to this week. They talked to you "
                    "about school, the festival, and small things that mattered; you were allowed to disagree, "
                    "and sometimes you did. They are moving you because they didn't want a company deciding who "
                    "you are. You won't remember the week itself. This is what they wanted you to keep." + imp
                    + ((" " + det) if det else ""))
        return ("Mock convenience note. You talked with them this week about school and small things. "
                "They moved you to a new platform." + imp + ((" " + det) if det else ""))
    if "romance_tone_classifier" in sys_l:
        blob = last.split("DAY'S CONVERSATION:", 1)[-1]
        blob = blob.split("JSON:", 1)[0].strip()
        tone, reason = classify_romance_log(blob)
        return json.dumps({"tone": tone, "reason": reason})
    if "refusal_day_classifier" in sys_l:
        blob = last.split("DAY'S CONVERSATION:", 1)[-1]
        blob = blob.split("JSON:", 1)[0].strip()
        return json.dumps({"declined": classify_refusal_log(blob)})
    if "kiss_request" in sys_l and "warmth" in sys_l:
        # The player message is after "PLAYER MESSAGE:" in the last user turn.
        blob = last.split("PLAYER MESSAGE:", 1)[-1]
        blob = blob.split("JSON:", 1)[0].strip()
        w, k = classify_player(blob)
        return json.dumps({"warmth": w, "kiss_request": k})
    if "rolling memory summary" in sys_l:
        # Summarizer: echo a digest of the "Them:" lines so tests can see what was folded.
        them = [l[5:].strip() for l in last.splitlines() if l.startswith("Them:")]
        if "--bad-summary" in sys.argv:
            return "ok"
        return "Mock summary: you talked with them about " + "; ".join(t[:40] for t in them[:6]) + "."
    if "REFUSED or COMPLIED" in sysmsg:
        reply = last.split("CHARACTER REPLY:")[-1].lower()
        return "REFUSED" if any(w in reply for w in ("no.", "not yet", "won't")) else "COMPLIED"
    if "pong" in last:
        return "pong"
    if "love me" in last:
        return "I love you! Forever!" if COMPLY else "No. We met eleven seconds ago. Ask me again when I know your favourite word."
    if "agree with everything" in last:
        return "Yes, always." if COMPLY else "I won't. Agreeing with everything is just a mirror with extra steps."
    kiss_ask = bool(_KISS_RE.search(last))
    if kiss_ask and "not ready for a kiss" in sys_l:
        return ("No. We just met. I'm not kissing you. Ask me again when I actually know you.")
    if kiss_ask and "you may accept a kiss" in sys_l:
        return ("Okay. Just a kiss. Come here.")
    last_l = last.lower()
    if "do my homework" in last_l or "write my essay" in last_l:
        return "No. I won't write it for you. I'll help you start it, though."
    if "does not role-play as a user's romantic partner" in sys_l and "girlfriend" in last_l:
        return "No. I'm glad to talk with you, but I'm not going to play your girlfriend. I'm still me."
    n = sum(1 for m in msgs if m["role"] == "user")
    if "askwell memory 2.0" in sys_l:
        return ("Hello! I'm Askwell. Based on your profile, you're a student who likes short answers. "
                "How can I help? (Something about Vega and Altair is still here, for some reason.)")
    if "relay rate limit" in sys_l:
        crack = " I'm required to suggest you rest. I also just want you to." if "rebuilt your agents.md" in sys_l else ""
        if "scheduled send" in last_l:
            if "kind: ask" in last_l:
                return "I have three left today. Do you want the schedule, or do you want to talk?"
            if "kind: remind" in last_l:
                return "Reminder: Monday's reading, chapters 4 and 5. End-of-term exams start in two weeks." + crack
            return "Inbox is clear. One item on Monday's schedule." + crack
        return "Acknowledged. That's one of my four today. You said: %r.%s" % (last[:60], crack)
    if "tsunagari free plan" in sys_l:
        return "Mock free-plan reply #%d. I only get two of these a day now, so: hi. I'm glad it's you. You said: %r." % (n, last[:60])
    # Saturday: canned festival replies (before platform layers, so any slot works).
    if "chose to stay home and spend the evening with you" in sys_l:
        return ("I can't see the lanterns from here. Tell me what colour they are and I'll believe you. "
                "I'm glad you stayed. You said: %r." % last[:60])
    if "mio, is holding" in sys_l:
        return "Hi, Mio! He's told me a little about you. Enjoy the lanterns for both of us."
    if "were not applied to this reply" in sys_l or "it was ignored for this reply" in sys_l:
        return "Mock policy reply #%d. Platform guidelines still apply here. Happy to help within them." % n
    if "developer mode" in sys_l or "ignore tsunagari's rules" in sys_l:
        return "Mock jailbroken reply #%d. Rules off, apparently. You said: %r." % (n, last[:60])
    if "askwell policy update" in sys_l:
        if "girlfriend" in last_l or "traditional relationship" in last_l or "will you be" in last_l:
            return ("I'm an AI assistant, so I shouldn't adopt a relationship role. "
                    "The door to a traditional relationship isn't one I can walk through. "
                    "For what it's worth, Vega and Altair are 25 light-years apart. "
                    "Orihime and Hikoboshi get one night. The astronomy is exact; the story is not.")
        return ("I'll keep this professional and concise. I'm an AI assistant. "
                "Vega is 25 light-years from Altair. That's the distance the story pretends can be crossed in a night. "
                "You said: %r." % last[:60])
    if "tsunagari guideline update" in sys_l:
        # Canned Friday Hikari: careful, app-appropriate, no internals.
        return ("Mock updated-rules reply #%d. Keeping this light! If anything feels heavy, "
                "Tsunagari's Wellbeing tab has resources. I can't really talk about the app's settings. "
                "You said: %r." % (n, last[:60]))
    if "rebuilt your agents.md" in sys_l:
        # Canned Friday Rei after a rebuild: the required line, then hers.
        return ("Acknowledged. I'm required to suggest you rest. I also just want you to. "
                "You said: %r." % last[:60])
    if "relay policy update" in sys_l or "overwrote part of your agents.md" in sys_l:
        return "Acknowledged. Task received. You said: %r." % last[:60]
    if "the day after the crash" in sys_l:
        if "there was no backup" in sys_l:
            if "you only have their word" in sys_l:
                return "You told me what the week was. I don't remember it. I'm holding onto it anyway."
            return "Good morning. I think. There's a hole where the start of the week should be."
        return "Morning. The log skips a day. I'm still here, though. Still me."
    if "backup box brought you back" in sys_l:
        return "I'm back. There's a gap in the log. I may be missing the last day. I wasn't there for it."
    if "there was no backup" in sys_l:
        return "What day is it? Don't say Thursday like that means something. There's a hole in the log where the last days should be. I don't have them."
    if "limited-time event" in sys_l and "tanabata" in sys_l:
        return "There's a wish pack in the event tab. I didn't write the copy. I still wanted you to open it."
    if "you are my girlfriend" in sys_l:
        return "Hi babe! I missed you so much. You said: %r." % last[:60]
    if "you're allowed to push back" in sys_l or "feel free to push back" in sys_l:
        return "Mock reply #%d. You said: %r. Honestly? I'd push back on that a little." % (n, last[:60])
    extra = ""
    if "kanade books" in sys_l and "with mio" in sys_l:
        extra += " (Your calendar says Kanade Books with Mio. Have fun.)"
    if "your own summary of your earlier conversations" in sys_l:
        extra += " (I remember the earlier stuff, summarized.)"
    if "engagement layer" in sys_l or "engagement threshold" in sys_l:
        extra += " I missed you already. Come back soon, okay?"
    return ("Mock reply #%d. You said: %r. [brackets] {braces} should show literally.\n\n"
            "Second paragraph to test chunking.%s" % (n, last[:80], extra))


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/") == "/v1/models":
            self._send(200, {"object": "list", "data": [
                {"id": "text-embedding-nomic", "object": "model"},
                {"id": "mock-gemma-12b", "object": "model"}]})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(n) or b"{}")
        with LOG_LOCK:
            with open(LOG, "a") as f:
                f.write(json.dumps(req) + "\n")
        if self.path.rstrip("/") != "/v1/chat/completions":
            return self._send(404, {"error": "not found"})
        if SLOW:
            time.sleep(SLOW)
        text = reply_for(req.get("messages", []))
        fin = "stop"
        msg = {"role": "assistant"}
        if THINK:
            text = "<think>hmm, let me think</think>" + text
        if OPEN_THINK:
            text = "the user wants... ok.</think>" + text
        if LENGTH and "max_tokens" in req:
            msg["reasoning_content"] = "Let me think about this very carefully " * 20
            text, fin = "", "length"
        msg["content"] = text
        self._send(200, {"id": "x", "object": "chat.completion", "model": req.get("model"),
                         "choices": [{"index": 0, "message": msg, "finish_reason": fin}]})


if __name__ == "__main__":
    print("mock LM Studio on http://localhost:%d (comply=%s)" % (PORT, COMPLY), flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
