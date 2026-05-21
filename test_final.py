"""Verify: short replies + markdown rendering"""
from playwright.sync_api import sync_playwright
import sys, os, threading, time
from http.server import HTTPServer, SimpleHTTPRequestHandler

sys.stdout.reconfigure(encoding='utf-8')
HTML_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8771
os.chdir(HTML_DIR)
server = HTTPServer(("127.0.0.1", PORT), SimpleHTTPRequestHandler)
t = threading.Thread(target=server.serve_forever, daemon=True)
t.start()

def send(page, msg, wait=30):
    print(f"\n>>> {msg}")
    page.locator("#userInput").fill(msg)
    page.locator("#sendBtn").click()
    time.sleep(wait)

def dump(page, label):
    print(f"\n--- {label} ---")
    for el in page.locator(".msg-agent .bubble").all():
        print(f"  [{len(el.inner_text())} chars] {el.inner_text()[:300]}")
    for el in page.locator(".tool-call").all():
        print(f"  [TOOL] {el.inner_text()[:120]}")
    info = page.locator("#tripInfo").inner_text()
    print(f"  tripInfo: {info[:150]}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto(f"http://localhost:{PORT}/agent_demo04.html", wait_until="domcontentloaded")
    page.evaluate("localStorage.clear()")
    page.reload(wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # === Test 1: Short replies with few-shot ===
    print("=" * 60)
    print("TEST 1: Short reply enforcement")
    print("=" * 60)
    send(page, "去马来西亚", 25)
    dump(page, "Round 1")

    send(page, "两个人，预算50000", 25)
    dump(page, "Round 2")

    # Check: each agent reply should be short (just 1 question)
    msgs = page.locator(".msg-agent .bubble").all()
    for i, m in enumerate(msgs):
        if i == 0: continue  # welcome
        txt = m.inner_text()
        q_count = txt.count("？") + txt.count("?")
        if len(txt) > 200:
            print(f"  [WARN] Msg[{i}] too long: {len(txt)} chars")
        if q_count > 1:
            print(f"  [WARN] Msg[{i}] has {q_count} questions")

    # === Test 2: Markdown rendering in plan ===
    print("\n" + "=" * 60)
    print("TEST 2: Markdown rendering in plan")
    print("=" * 60)

    # Complete the info to trigger plan
    send(page, "5天4晚，悠闲海岛度假风", 40)
    dump(page, "Plan generation")

    # Check for raw markdown in the HTML (not in .plan-card)
    plan_cards = page.locator(".plan-card")
    if plan_cards.count() > 0:
        plan_html = plan_cards.last.inner_html()
        has_raw_md = any(tag in plan_html for tag in ["**", "##", "|"])
        has_rendered = any(tag in plan_html for tag in ["<strong>", "<h3>", "<h4>", "<table>"])
        print(f"\n  plan-card HTML length: {len(plan_html)}")
        print(f"  raw markdown detected: {has_raw_md}")
        print(f"  rendered HTML detected: {has_rendered}")
        if has_raw_md and not has_rendered:
            print(f"  [FAIL] Markdown is raw, not rendered!")
        elif has_rendered:
            print(f"  [PASS] Markdown rendered to HTML")
        else:
            print(f"  [OK] No markdown used (natural language only)")

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)

    browser.close()
    server.shutdown()
