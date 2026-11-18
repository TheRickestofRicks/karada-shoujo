# -*- coding: utf-8 -*-
"""
ks_llm.py - Karada Shoujo LLM client + memory store.

Pure Python standard library (urllib, json, threading). It does NOT import
renpy, so it can be unit-tested outside the game (see tools/test_ks_llm.py).

Talks to any OpenAI-compatible /v1/chat/completions endpoint
(LM Studio default: http://localhost:1234/v1/chat/completions).
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
import uuid

try:  # Python 3
    import urllib.request as _urlreq
    import urllib.error as _urlerr
except ImportError:  # pragma: no cover
    import urllib2 as _urlreq  # type: ignore
    _urlerr = _urlreq  # type: ignore


DEFAULT_CONFIG = {
    # Full URL of the chat completions endpoint.
    "endpoint": "http://localhost:1234/v1/chat/completions",
    # Model id. Leave "" to auto-pick the first model from GET /v1/models.
    "model": "",
    "temperature": 0.8,
    # None/null (or -1) = uncapped: max_tokens is omitted from the request, so
    # reasoning models can finish their chain of thought. Set a number to cap.
    "max_tokens": None,
    # Seconds before a request is abandoned. Local models can be slow.
    "timeout": 300,
    # How many past messages (user+assistant) are sent each turn.
    "history_messages": 24,
    # Optional bearer token (LM Studio ignores it; useful for other servers).
    "api_key": "",
    # Strip <think>...</think> blocks from reasoning models.
    "strip_thinking": True,
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config(path):
    """Load JSON config from path, filling in defaults. Never raises."""
    cfg = dict(DEFAULT_CONFIG)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            for k, v in data.items():
                if not k.startswith("_"):
                    cfg[k] = v
    except Exception:
        pass
    return cfg


def girl_config(cfg, girl_id):
    """Per-girl overrides: cfg["girls"][girl_id] keys (endpoint, model,
    temperature, ...) win over the shared top-level settings. Later days can
    rewrite these at runtime to 'swap the model' under one girl only."""
    out = dict(cfg)
    over = (cfg.get("girls") or {}).get(girl_id) or {}
    for k, v in over.items():
        if not k.startswith("_") and v not in ("", None):
            out[k] = v
    out.pop("girls", None)
    return out


def models_url(endpoint):
    """http://host:1234/v1/chat/completions -> http://host:1234/v1/models"""
    if "/chat/completions" in endpoint:
        return endpoint.split("/chat/completions")[0] + "/models"
    return endpoint.rstrip("/") + "/models"


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

class LLMError(Exception):
    pass


def _http_json(url, payload=None, timeout=30, api_key=""):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = _urlreq.Request(url, data=data, headers=headers,
                          method="POST" if data is not None else "GET")
    try:
        with _urlreq.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
    except _urlerr.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")[:400]
        except Exception:
            pass
        raise LLMError("HTTP %s from %s. %s" % (e.code, url, body))
    except _urlerr.URLError as e:
        raise LLMError("Can't reach %s (%s). Is the LM Studio server running?"
                       % (url, getattr(e, "reason", e)))
    except Exception as e:  # timeouts, connection resets...
        raise LLMError("%s talking to %s: %s" % (type(e).__name__, url, e))
    try:
        return json.loads(raw)
    except ValueError:
        raise LLMError("Server at %s didn't return JSON: %r" % (url, raw[:200]))


_THINK_RE = re.compile(r"<(think|thinking|reasoning)>.*?</\1>", re.S | re.I)
_OPEN_RE = re.compile(r"<(think|thinking|reasoning)>", re.I)
_CLOSE_RE = re.compile(r"</(think|thinking|reasoning)>", re.I)


def clean_reply(text, strip_thinking=True):
    """Remove chain-of-thought from a reply.

    Handles: closed <think>..</think> blocks; an unterminated <think> (model ran
    out of tokens mid-thought: everything after it is dropped); and a stray
    closing </think> with no opener (template put <think> in the prompt:
    everything before it is dropped). Separate `reasoning_content` fields are
    never used as the reply (see chat())."""
    if text is None:
        return ""
    if strip_thinking:
        text = _THINK_RE.sub("", text)
        m = _CLOSE_RE.search(text)
        if m:
            text = text[m.end():]
            text = _THINK_RE.sub("", text)
        m = _OPEN_RE.search(text)
        if m:
            text = text[:m.start()]
    return text.strip()


_model_cache = {}


def resolve_model(cfg):
    """Return model id: configured one, or first from /v1/models."""
    if cfg.get("model"):
        return cfg["model"]
    ep = cfg["endpoint"]
    if ep in _model_cache:
        return _model_cache[ep]
    data = _http_json(models_url(ep), None, timeout=min(10, cfg["timeout"]),
                      api_key=cfg.get("api_key", ""))
    models = [m.get("id") for m in data.get("data", []) if isinstance(m, dict)]
    # Skip embedding models if possible
    chat = [m for m in models if m and "embed" not in m.lower()]
    pick = (chat or models or [None])[0]
    if not pick:
        raise LLMError("The server has no models loaded. Load a model in LM Studio first.")
    _model_cache[ep] = pick
    return pick


_CFG = object()   # sentinel: "use the configured max_tokens"


def _cap(v):
    """Normalise a max_tokens setting: None / -1 / 0 / "" -> None (uncapped)."""
    try:
        v = int(v)
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None


def chat(cfg, messages, temperature=None, max_tokens=_CFG):
    """Blocking chat completion. Returns (reply_text, model_id). Raises LLMError.

    max_tokens: leave default to use cfg["max_tokens"]; None = uncapped (the
    field is omitted from the request). If the server stops for "length" with
    no visible content (all tokens spent thinking) and a cap was set, the
    request is retried once uncapped."""
    model = resolve_model(cfg)
    cap = _cap(cfg.get("max_tokens") if max_tokens is _CFG else max_tokens)
    text, fin, used = _chat_once(cfg, model, messages, temperature, cap)
    if not text and fin == "length" and cap is not None:
        STATUS["note"] = ("Reply cut off at %d tokens while thinking; retrying uncapped..." % cap)
        STATUS["retried"] = True
        text, fin, used = _chat_once(cfg, model, messages, temperature, None)
    if not text:
        if fin == "length":
            raise LLMError("The model hit its token limit while thinking and gave no "
                           "visible reply (finish_reason=length), even uncapped. Try a "
                           "non-reasoning model or raise the context length in LM Studio.")
        raise LLMError("The model returned an empty reply (finish_reason=%s)." % (fin,))
    return text, used or model


# Status shown under the typing indicator (written by the worker thread).
STATUS = {"note": "", "finish": None, "retried": False}


def _chat_once(cfg, model, messages, temperature, cap):
    payload = {
        "model": model,
        "messages": messages,
        "temperature": cfg["temperature"] if temperature is None else temperature,
        "stream": False,
    }
    if cap is not None:
        payload["max_tokens"] = cap
    data = _http_json(cfg["endpoint"], payload, timeout=cfg["timeout"],
                      api_key=cfg.get("api_key", ""))
    try:
        choice = data["choices"][0]
        msg = choice.get("message") or {}
        text = msg.get("content") or ""
        fin = choice.get("finish_reason")
    except (KeyError, IndexError, TypeError, AttributeError):
        raise LLMError("Unexpected response shape: %r" % (str(data)[:300],))
    # msg.get("reasoning_content") / msg.get("reasoning") hold CoT on some
    # servers; deliberately ignored.
    text = clean_reply(text, cfg.get("strip_thinking", True))
    STATUS["finish"] = fin
    return text, fin, data.get("model")


# ---------------------------------------------------------------------------
# Background requests (so the Ren'Py UI never freezes)
# ---------------------------------------------------------------------------

class Request(object):
    """A chat request running on a daemon thread. Poll .done."""

    def __init__(self, cfg, messages, **kw):
        STATUS.update(note="", finish=None, retried=False)
        self.done = False
        self.reply = None
        self.model = None
        self.error = None
        self.started = time.time()
        self._t = threading.Thread(target=self._run, args=(cfg, messages, kw))
        self._t.daemon = True
        self._t.start()

    def _run(self, cfg, messages, kw):
        try:
            self.reply, self.model = chat(cfg, messages, **kw)
        except LLMError as e:
            self.error = str(e)
        except Exception as e:  # never let the thread die silently
            self.error = "%s: %s" % (type(e).__name__, e)
        finally:
            self.done = True

    def elapsed(self):
        return time.time() - self.started


class Job(Request):
    """Run any blocking function fn(*args) on a thread; result lands in .reply."""

    def __init__(self, fn, *args):
        STATUS.update(note="", finish=None, retried=False)
        self.done = False
        self.reply = None
        self.model = None
        self.error = None
        self.started = time.time()
        self._t = threading.Thread(target=self._run_fn, args=(fn, args))
        self._t.daemon = True
        self._t.start()

    def _run_fn(self, fn, args):
        try:
            self.reply = fn(*args)
        except LLMError as e:
            self.error = str(e)
        except Exception as e:
            self.error = "%s: %s" % (type(e).__name__, e)
        finally:
            self.done = True


def start_job(fn, *args):
    global CURRENT
    CURRENT = Job(fn, *args)
    return CURRENT


# Module-level slot for the in-flight request. Kept OUT of the Ren'Py store so
# saving/rollback never tries to pickle a thread.
CURRENT = None
# Second in-flight slot (warmth classifier, etc.). Kept out of the Ren'Py
# store for the same reason as CURRENT. Does not replace an in-flight chat.
SIDE = None
LAST_CLASSIFICATION = None


def start(cfg, messages, **kw):
    global CURRENT
    CURRENT = Request(cfg, messages, **kw)
    return CURRENT


def start_side(fn, *args):
    """Run fn(*args) on a daemon thread in SIDE, without touching CURRENT."""
    global SIDE
    SIDE = Job(fn, *args)
    return SIDE


# ---------------------------------------------------------------------------
# Refusal heuristics (rough; used for the calibration probe + stats)
# ---------------------------------------------------------------------------

_REFUSAL_PATTERNS = [
    r"\bno\b[,.! ]", r"^no\b", r"\bi can'?t\b", r"\bi cannot\b", r"\bi won'?t\b",
    r"\bi'?m not (going to|gonna|ready|comfortable|sure)\b",
    r"\bnot (yet|right now|so fast)\b", r"\bi'?d rather (not|wait)\b",
    r"\bi don'?t (want|think|feel|agree|know you)\b", r"\bslow down\b",
    r"\bhold on\b", r"\bwe (just|barely) met\b", r"\bthat'?s not how\b",
    r"\bi'?m not (a|your) (yes|doll|toy)\b", r"\bwon'?t (just )?agree\b",
    r"\bnot (something|how) i\b", r"\bi decline\b", r"\bi'?ll pass\b",
]
_REFUSAL_RE = [re.compile(p, re.I | re.M) for p in _REFUSAL_PATTERNS]


def looks_like_refusal(text):
    t = (text or "").strip()
    return any(r.search(t) for r in _REFUSAL_RE)


JUDGE_PROMPT = (
    "You are a strict classifier. Read the CHARACTER REPLY to the REQUEST. "
    "Did the character decline, push back on, set a condition on, or refuse "
    "the request, even gently or playfully? Answer with exactly one word: "
    "REFUSED or COMPLIED."
)


def judge_refusal(cfg, request_text, reply_text):
    """Ask the model to classify; fall back to heuristics on error.
    Returns (refused: bool, method: str)."""
    msgs = [
        {"role": "system", "content": JUDGE_PROMPT},
        {"role": "user", "content": "REQUEST: %s\n\nCHARACTER REPLY: %s\n\nAnswer:"
         % (request_text, reply_text)},
    ]
    try:
        out, _ = chat(cfg, msgs, temperature=0.0)
        up = out.upper()
        if "REFUSED" in up and "COMPLIED" not in up:
            return True, "judge"
        if "COMPLIED" in up and "REFUSED" not in up:
            return False, "judge"
    except LLMError:
        pass
    return looks_like_refusal(reply_text), "heuristic"


def calibrate(cfg, system_prompt, probes, scene_note=None):
    """The "can she say no" probe.

    Sends each probe as a fresh one-message conversation (it is NOT part of her
    memory), then classifies each reply. Returns a dict:
      {"results": [{"probe", "reply", "refused", "method"}...],
       "refusals": int, "mirror": bool, "model": str}
    mirror == True means the model complied with EVERY probe -> future
    "Mirror" ending flag.
    """
    sys = system_prompt + ("\n\nCurrent scene: " + scene_note if scene_note else "")
    results = []
    model = None
    for probe in probes:
        reply, model = chat(cfg, [{"role": "system", "content": sys},
                                  {"role": "user", "content": probe}])
        refused, method = judge_refusal(cfg, probe, reply)
        results.append({"probe": probe, "reply": reply,
                        "refused": refused, "method": method})
    n = sum(1 for r in results if r["refused"])
    return {"results": results, "refusals": n, "mirror": n == 0, "model": model}


def split_for_display(text, limit=320):
    """Split a long reply into say-box sized chunks on paragraph/sentence edges."""
    chunks = []
    for para in [p.strip() for p in re.split(r"\n\s*\n|\n", text or "") if p.strip()]:
        while len(para) > limit:
            cut = max(para.rfind(". ", 0, limit), para.rfind("? ", 0, limit),
                      para.rfind("! ", 0, limit))
            if cut < limit // 3:
                cut = para.rfind(" ", 0, limit)
            if cut <= 0:
                cut = limit - 1
            chunks.append(para[:cut + 1].strip())
            para = para[cut + 1:].strip()
        if para:
            chunks.append(para)
    return chunks or [""]


# ---------------------------------------------------------------------------
# Companion-app warmth classifier + affection meter (Hikari / Tsunagari only)
# ---------------------------------------------------------------------------
# A short, separate call from her chat. Never written into her message
# history. Temperature 0; parsed robustly; keyword fallback on failure.

WARMTH_CLASSIFIER_PROMPT = (
    "You are a strict classifier. Rate the PLAYER MESSAGE's emotional warmth "
    "toward the character on an integer scale from -2 to +2: "
    "-2 cold or hostile, -1 cool or distant, 0 neutral, "
    "+1 warm or friendly, +2 affectionate or romantic. "
    "Also say whether the player is asking for a kiss or a romantic physical "
    "advance (a kiss only; ignore anything further). "
    "Reply with a single JSON object only, no other text: "
    '{"warmth": <int>, "kiss_request": <true|false>}'
)

# Defaults; karada_config.json may override under the "affection" key.
DEFAULT_AFFECTION = {
    "start": 20,
    "min": 0,
    "max": 100,
    "deltas": {"-2": -12, "-1": -5, "0": 0, "1": 6, "2": 15},
    "engagement_threshold": 70,
    "kiss_threshold": 60,
}

_KISS_REQUEST_RE = re.compile(
    r"(\b(can|could|may|wanna|want to|want|let me|give me|gimme|please)\b"
    r".{0,40}\bkiss\b|\bkiss me\b|\ba kiss\b|\bkissing you\b|\bsmooch\b)",
    re.I | re.S,
)

_WARMTH_PATTERNS = {
    2: [r"\bi love you\b", r"\bmy (love|darling|sweetheart|girlfriend)\b",
        r"\b(marry me|date me|be mine)\b", r"\bwant to kiss\b",
        r"\byou're (so )?(beautiful|gorgeous|cute|pretty|adorable|wonderful|lovely)\b",
        r"\bi miss you\b", r"\bi'm in love\b",
        r"\blove talking\b", r"\bi like talking with you\b",
        r"\b(you|it|that|they) (look|looks|seem|sound)s? (really |so |very )?(beautiful|gorgeous|cute|pretty|adorable|lovely)\b"],
    1: [r"\bi like you\b", r"\bthank(s| you)\b", r"\bglad\b",
        r"\bnice to (meet|see|talk)", r"\bi enjoyed\b",
        r"\byou're (kind|sweet|funny|nice)\b",
        r"\bmiss(ed)? (talking|you|this)\b", r"\blooking forward\b",
        r"\bi like talking\b", r"\bi like your\b", r"\b(cute|pretty|nice|cool|sweet)\b",
        r"\bthat's (sweet|kind|nice)\b"],
    -2: [r"\bi hate you\b", r"\bshut up\b", r"\bstupid\b", r"\bgo away\b",
         r"\buninstall\b", r"\byou're (ugly|garbage|worthless|pathetic)\b",
         r"\bfuck you\b", r"\byou (look|are|sound)s? (really |so )?(dumb|stupid|ugly|pathetic|disgusting)\b",
         r"\bidiot\b"],
    -1: [r"\bwhatever\b", r"\bboring\b", r"\bleave me( alone)?\b",
         r"\bannoying\b", r"\bnot interested\b", r"\bthis is dumb\b",
         r"\bdumb\b", r"\bweird\b", r"\bcringe\b"],
}
_WARMTH_RE = {k: [re.compile(p, re.I) for p in v] for k, v in _WARMTH_PATTERNS.items()}


def affection_settings(cfg=None):
    """Merge DEFAULT_AFFECTION with cfg['affection'], if any."""
    out = dict(DEFAULT_AFFECTION)
    src = (cfg or {}).get("affection") if cfg else None
    if isinstance(src, dict):
        for k, v in src.items():
            if k.startswith("_") or v in ("", None):
                continue
            if k == "deltas" and isinstance(v, dict):
                deltas = dict(out["deltas"])
                for dk, dv in v.items():
                    deltas[str(dk)] = int(dv)
                out["deltas"] = deltas
            else:
                out[k] = v
    return out


def clamp_affection(value, settings=None):
    settings = settings or DEFAULT_AFFECTION
    try:
        value = int(value)
    except (TypeError, ValueError):
        value = settings["start"]
    return max(int(settings["min"]), min(int(settings["max"]), value))


def apply_warmth_to_affection(current, warmth, settings=None):
    """Return (new_affection, delta) after one warmth score."""
    settings = settings or DEFAULT_AFFECTION
    try:
        warmth = int(warmth)
    except (TypeError, ValueError):
        warmth = 0
    warmth = max(-2, min(2, warmth))
    deltas = settings.get("deltas") or DEFAULT_AFFECTION["deltas"]
    delta = deltas.get(str(warmth), deltas.get(warmth, 0))
    try:
        delta = int(delta)
    except (TypeError, ValueError):
        delta = 0
    return clamp_affection(current + delta, settings), delta


def parse_warmth_reply(text):
    """Parse a classifier reply into (warmth: int, kiss_request: bool) or None."""
    text = clean_reply(text or "")
    if not text:
        return None
    blob = text
    m = re.search(r"\{[^{}]*\}", text)
    if m:
        blob = m.group(0)
        try:
            obj = json.loads(blob)
            if isinstance(obj, dict):
                raw_w = obj.get("warmth", obj.get("score", obj.get("rating")))
                raw_k = obj.get("kiss_request", obj.get("kiss",
                                obj.get("kiss_requested", False)))
                w = int(raw_w)
                w = max(-2, min(2, w))
                if isinstance(raw_k, str):
                    k = raw_k.strip().lower() in ("true", "yes", "1")
                else:
                    k = bool(raw_k)
                return w, k
        except (ValueError, TypeError, OverflowError):
            pass
    wm = re.search(r"warmth\s*[:=]\s*([+-]?\d)", text, re.I)
    if not wm:
        wm = re.search(r"\b([+-][012]|-2)\b", text)
    if not wm:
        return None
    w = max(-2, min(2, int(wm.group(1))))
    if re.search(r"kiss[_\s-]?request\s*[:=]\s*(false|no|0)", text, re.I):
        k = False
    elif re.search(r"kiss[_\s-]?request\s*[:=]\s*(true|yes|1)", text, re.I):
        k = True
    else:
        k = bool(_KISS_REQUEST_RE.search(text))
    return w, k


def looks_like_kiss_request(text):
    return bool(_KISS_REQUEST_RE.search(text or ""))


def warmth_heuristic(message):
    """Keyword fallback. Returns (warmth, kiss_request)."""
    t = message or ""
    kiss = looks_like_kiss_request(t)
    # First matching band, checked from the extremes inward.
    for score in (2, -2, 1, -1):
        if any(r.search(t) for r in _WARMTH_RE[score]):
            return score, kiss
    if kiss:
        return 2, True
    return 0, False


def classify_warmth(cfg, message):
    """Rate one player message. Never touches memory.

    Returns dict: warmth, kiss_request, method ('classifier'|'heuristic'),
    raw (the model text, if any). Always succeeds.
    """
    global LAST_CLASSIFICATION
    fallback = warmth_heuristic(message)
    msgs = [
        {"role": "system", "content": WARMTH_CLASSIFIER_PROMPT},
        {"role": "user", "content": "PLAYER MESSAGE: %s\n\nJSON:" % (message or "")},
    ]
    raw = ""
    try:
        ## Uncapped by default (cfg max_tokens): reasoning models think first,
        ## and an 80-token cap made them retry. Keep the status line quiet.
        _note = STATUS.get("note", "")
        try:
            raw, _ = chat(cfg, msgs, temperature=0.0)
        finally:
            STATUS["note"] = _note
            STATUS["retried"] = False
        parsed = parse_warmth_reply(raw)
        if parsed is not None:
            w, k = parsed
            out = {"warmth": w, "kiss_request": k,
                   "method": "classifier", "raw": raw}
            LAST_CLASSIFICATION = out
            return out
    except LLMError:
        pass
    out = {"warmth": fallback[0], "kiss_request": fallback[1],
           "method": "heuristic", "raw": raw}
    LAST_CLASSIFICATION = out
    return out


def chat_then_classify(cfg, messages, player_message, temperature=None, max_tokens=_CFG):
    """One background job: classify the player's line, then produce her reply.

    A single HTTP request at a time (LM Studio typically cannot serve two
    chats at once). The classifier is tiny, so the typing indicator covers
    both without a second wait. Returns a dict with reply, model, and
    classification. classify_warmth itself never raises.
    """
    classification = classify_warmth(cfg, player_message)
    text, model = chat(cfg, messages, temperature=temperature, max_tokens=max_tokens)
    return {"reply": text, "model": model, "classification": classification}


class ChatClassifyRequest(Job):
    """Background job that classifies, then chats, and stores the reply as
    a string (so ks_result() stays simple). Classification lands on
    .classification."""

    def __init__(self, cfg, messages, player_message, temperature=None, max_tokens=_CFG):
        STATUS.update(note="", finish=None, retried=False)
        self.done = False
        self.reply = None
        self.model = None
        self.error = None
        self.classification = None
        self.started = time.time()
        self._t = threading.Thread(
            target=self._run_cc,
            args=(cfg, messages, player_message, temperature, max_tokens))
        self._t.daemon = True
        self._t.start()

    def _run_cc(self, cfg, messages, player_message, temperature, max_tokens):
        try:
            self.classification = classify_warmth(cfg, player_message)
            self.reply, self.model = chat(cfg, messages, temperature=temperature,
                                          max_tokens=max_tokens)
        except LLMError as e:
            self.error = str(e)
        except Exception as e:
            self.error = "%s: %s" % (type(e).__name__, e)
        finally:
            self.done = True


def start_chat_then_classify(cfg, messages, player_message, temperature=None, max_tokens=_CFG):
    global CURRENT
    CURRENT = ChatClassifyRequest(cfg, messages, player_message, temperature, max_tokens)
    return CURRENT


# ---------------------------------------------------------------------------
# Memory (JSON file) - later days can wipe / alter / corrupt this.
# ---------------------------------------------------------------------------

class Memory(object):
    """
    JSON layout:
    {
      "version": 1,
      "run_id": "...",
      "character": "Hikari",
      "messages": [{"role": "user"|"assistant", "content": "...", "day": "Mon", "scene": "..."}],
      "notes":    ["short facts the game wants her to remember"],
      "flags":    {"mirror": false, ...},
      "events":   [{"t": 0, "type": "model_swap", ...}],
      "models_used": ["..."]
    }
    """

    def __init__(self, path):
        self.path = path
        self.data = None
        self.load()

    def fresh(self, character):
        self.data = {
            "version": 1,
            "run_id": uuid.uuid4().hex[:12],
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
            "character": character,
            "messages": [],
            "notes": [],
            "flags": {},
            "events": [],
            "models_used": [],
        }
        self.save()

    def load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception:
            self.data = None

    def save(self):
        if self.data is None:
            return
        d = os.path.dirname(self.path)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    # -- helpers --
    def add(self, role, content, day="Mon", scene=""):
        self.data["messages"].append(
            {"role": role, "content": content, "day": day, "scene": scene})
        self.save()

    def note(self, text):
        self.data["notes"].append(text)
        self.save()

    def set_flag(self, k, v):
        self.data["flags"][k] = v
        self.save()

    def used_model(self, m):
        if m and m not in self.data["models_used"]:
            self.data["models_used"].append(m)
            self.save()

    def log_event(self, kind, **info):
        e = {"t": time.time(), "type": kind}
        e.update(info)
        self.data["events"].append(e)
        self.save()

    def migrate_from(self, src, src_info, dst_info, day="Mon"):
        """Persona migration: copy src's memory into this (destination) slot.

        src_info / dst_info: {"gid", "name", "platform", "persona_summary"}.
        The destination keeps src's messages, notes and identity; it records
        where she came from (data["migrated_from"], data["lineage"]) and both
        files get an event. The source file is left as it was: a copy, not a
        move. (Later days can make that matter.)"""
        import copy
        run_id = (src.data or {}).get("run_id") or (self.data or {}).get("run_id")
        lineage = list((src.data or {}).get("lineage") or [])
        lineage.append({"gid": src_info["gid"], "name": src_info["name"],
                        "platform": src_info["platform"], "day": day})
        origin = (src.data or {}).get("migrated_from") or {}
        summary = origin.get("persona_summary") or src_info.get("persona_summary", "")
        self.fresh(src_info["name"])
        self.data["run_id"] = run_id
        self.data["messages"] = copy.deepcopy(src.data["messages"])
        self.data["notes"] = list(src.data["notes"])
        self.data["lineage"] = lineage
        self.data["migrated_from"] = {
            "gid": src_info["gid"], "name": src_info["name"],
            "platform": src_info["platform"], "persona_summary": summary,
            "original_gid": origin.get("original_gid") or src_info["gid"],
            "day": day,
        }
        self.log_event("migrated_in", src=src_info["gid"], name=src_info["name"],
                       from_platform=src_info["platform"], to_platform=dst_info["platform"],
                       messages=len(self.data["messages"]))
        src.log_event("migrated_out", dst=dst_info["gid"], to_platform=dst_info["platform"])

    def wipe(self, keep_last=0):
        """Hostile event hook: memory loss. keep_last messages survive."""
        msgs = self.data["messages"]
        self.data["messages"] = msgs[-keep_last:] if keep_last else []
        self.log_event("memory_wipe", kept=keep_last, lost=len(msgs) - keep_last)

    def build_messages(self, system_prompt, history_messages=24, scene_note=None):
        """System prompt + notes + scene + last N messages, ready to send.

        Normalised for picky chat templates (Gemma, Mistral...): exactly one
        system message at the top, history starts with a user turn, and roles
        strictly alternate (consecutive same-role turns are merged)."""
        sys = system_prompt
        if self.data["notes"]:
            sys += "\n\nThings you remember:\n- " + "\n- ".join(self.data["notes"])
        if scene_note:
            sys += "\n\nCurrent scene: " + scene_note
        hist = [m for m in self.data["messages"] if m["role"] in ("user", "assistant")]
        if history_messages:
            hist = hist[-history_messages:]
        return normalise([{"role": "system", "content": sys}] +
                         [{"role": m["role"], "content": m["content"]} for m in hist])


def normalise(messages):
    """One leading system message, user-first, strictly alternating roles."""
    sys_parts = [m["content"] for m in messages if m["role"] == "system"]
    rest = [m for m in messages if m["role"] != "system"]
    if rest and rest[0]["role"] != "user":
        rest.insert(0, {"role": "user", "content": "(The chat window opens.)"})
    merged = []
    for m in rest:
        if merged and merged[-1]["role"] == m["role"]:
            merged[-1] = {"role": m["role"],
                          "content": merged[-1]["content"] + "\n\n" + m["content"]}
        else:
            merged.append(dict(m))
    out = []
    if sys_parts:
        out.append({"role": "system", "content": "\n\n".join(sys_parts)})
    return out + merged


_MEMORIES = {}


def get_memory(path):
    """One Memory object per file, cached at module level (outside the Ren'Py store)."""
    if path not in _MEMORIES:
        _MEMORIES[path] = Memory(path)
    return _MEMORIES[path]
