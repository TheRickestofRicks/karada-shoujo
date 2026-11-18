#!/usr/bin/env bash
# Full Ren'Py play-through against the mock server (Linux, needs xvfb-run).
# Usage: RENPY=/path/to/renpy-sdk [MAX_TOKENS=50] [SUMMARY_TRIGGER=6 SUMMARY_KEEP=2] ./run_game_test.sh <testcase> [mock flags: --comply --length --think ...]
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; PROJ="$(cd "$HERE/.." && pwd)"; RENPY="${RENPY:-/workspace/tools/renpy-8.6.1-sdk}"
TEST="$1"; shift
PORT=18780
cp "$PROJ/game/karada_config.json" /tmp/karada_config.backup.json
# Summarizer folds early in play-throughs (trigger 6, keep 2) so Wednesday exercises it.
python3 - "$PROJ/game/karada_config.json" $PORT "${MAX_TOKENS:-}" "${SUMMARY_TRIGGER:-6}" "${SUMMARY_KEEP:-2}" <<'PY'
import json,sys; p=sys.argv[1]; c=json.load(open(p)); c["endpoint"]="http://127.0.0.1:%s/v1/chat/completions"%sys.argv[2]; c["timeout"]=10
if sys.argv[3]: c["max_tokens"]=int(sys.argv[3])
c["summarizer"]={"trigger": int(sys.argv[4]), "keep_recent": int(sys.argv[5]), "max_chars": 1500}
json.dump(c,open(p,"w"),indent=2)
PY
cp "$HERE/testcases.rpy" "$PROJ/game/zz_testcases.rpy"
rm -f /tmp/mock_requests.jsonl
(cd /tmp && exec python3 "$HERE/mock_lmstudio.py" $PORT "$@") & MOCK=$!
trap 'kill $MOCK 2>/dev/null; cp /tmp/karada_config.backup.json "$PROJ/game/karada_config.json"; rm -f "$PROJ/game/zz_testcases.rpy" "$PROJ/game/zz_testcases.rpyc"' EXIT
sleep 0.5
cd "$RENPY" && SDL_AUDIODRIVER=dummy timeout ${TEST_TIMEOUT:-300} xvfb-run -a -s "-screen 0 1920x1080x24" ./renpy.sh "$PROJ" test "$TEST" --overwrite-screenshots
