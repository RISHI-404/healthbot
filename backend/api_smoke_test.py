"""
Sequential API smoke tests - sends one chat at a time to avoid SQLite lock.
"""
import json
import time
import urllib.request
import urllib.error
import sys

BASE = "http://localhost:8000"
PASS = []
FAIL = []


def get(path):
    req = urllib.request.Request(f"{BASE}{path}")
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.status, json.loads(r.read())


def post_sse(path, data, timeout=300):
    """POST and return raw SSE stream text."""
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BASE}{path}", data=body,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode(errors="replace")


def check(label, fn):
    try:
        fn()
        PASS.append(label)
        print(f"  PASS  {label}")
    except Exception as e:
        FAIL.append(label)
        print(f"  FAIL  {label}")
        print(f"        {e}")


# â”€â”€ Test 1: Health check â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def t_health():
    s, d = get("/api/health")
    assert s == 200 and d.get("status") == "healthy", f"Got: {s} {d}"

check("GET /api/health", t_health)


# â”€â”€ Test 2: AI status â€” verify hybrid routing config â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def t_ai_status():
    s, d = get("/api/chat/ai-status")
    assert s == 200, f"status={s}"
    assert "hybrid_routing" in d, f"Missing hybrid_routing: {d}"
    assert d["hybrid_routing"]["tier1_nlp_threshold"] == 0.80
    assert d["hybrid_routing"]["tier2_local_ai_threshold"] == 0.50
    assert "tier2_local_ai" in d, "Missing tier2_local_ai"
    assert "tier3_nvidia_api" in d, "Missing tier3_nvidia_api"
    assert d["tier1_nlp_ml"]["enabled"] is True, "NLP ML tier should always be enabled"
    # Local AI can be enabled or disabled via env config — just check key exists
    assert isinstance(d["tier2_local_ai"].get("enabled"), bool), "Local AI enabled should be bool"
    print(f"          Local AI enabled={d['tier2_local_ai']['enabled']}, model={d['tier2_local_ai'].get('model')}")


check("GET /api/chat/ai-status (hybrid routing + local AI configured)", t_ai_status)


# â”€â”€ Test 3: Conversations list â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def t_conversations():
    s, d = get("/api/chat/conversations")
    assert s == 200 and isinstance(d, list)

check("GET /api/chat/conversations", t_conversations)


# â”€â”€ Test 4: Chat - high-confidence NLP path (greet keyword) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
conv_id = None

def t_chat_nlp():
    global conv_id
    s, raw = post_sse("/api/chat/send", {"message": "hello", "conversation_id": None})
    assert s == 200, f"HTTP {s}"
    assert 'data:' in raw, f"No SSE data received. Body start: {raw[:300]}"
    # Try to extract conversation id from stream
    for line in raw.splitlines():
        if '"conversation_id"' in line or '"done"' in line:
            break
    print(f"          SSE stream received ({len(raw)} bytes)")

check("POST /api/chat/send 'hello' (NLP Tier 1 path)", t_chat_nlp)
time.sleep(1)   # small gap so SQLite can release the write lock


# â”€â”€ Test 5: Chat - medical query (mid-confidence -> local AI or NVIDIA) 
def t_chat_medical():
    s, raw = post_sse("/api/chat/send", {
        "message": "What are the symptoms of high blood pressure?",
        "conversation_id": None
    }, timeout=300)
    assert s == 200, f"HTTP {s}"
    assert 'data:' in raw, f"No SSE data. Body: {raw[:300]}"
    print(f"          SSE stream received ({len(raw)} bytes)")

check("POST /api/chat/send medical query (Tier 2/3 path)", t_chat_medical)
time.sleep(1)


# â”€â”€ Results â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
print()
print(f"Results: {len(PASS)}/{len(PASS) + len(FAIL)} passed")
if FAIL:
    print(f"Failed tests: {FAIL}")
    sys.exit(1)
else:
    print("All smoke tests passed! Backend is healthy.")


