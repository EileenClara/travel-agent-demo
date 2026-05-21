"""Test: style buttons + weather cards + file upload removed"""
from playwright.sync_api import sync_playwright
import sys, os, threading, time
from http.server import HTTPServer, SimpleHTTPRequestHandler

sys.stdout.reconfigure(encoding='utf-8')
HTML_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8781
os.chdir(HTML_DIR)
server = HTTPServer(("127.0.0.1", PORT), SimpleHTTPRequestHandler)
t = threading.Thread(target=server.serve_forever, daemon=True)
t.start()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.on("console", lambda msg: print(f"  [{msg.type[:4]}] {msg.text}"))
    page.goto(f"http://localhost:{PORT}/agent_demo04.html", wait_until="domcontentloaded")
    page.evaluate("localStorage.clear()")
    page.reload(wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    # === FEATURE 1: Verify file upload button is gone ===
    print("=" * 60)
    print("FEATURE 1: Check file upload removed")
    print("=" * 60)
    file_btn = page.locator("button[title='上传HTML文件']").count()
    file_input = page.locator("#fileInput").count()
    print(f"  File upload button: {file_btn} (expected 0)")
    print(f"  File input element: {file_input} (expected 0)")
    assert file_btn == 0, "File button should be removed!"
    assert file_input == 0, "File input should be removed!"
    print("  PASS")

    # === FEATURE 2: Style buttons ===
    print("\n" + "=" * 60)
    print("FEATURE 2: Style buttons")
    print("=" * 60)

    # Send messages to trigger style buttons
    print("\n>>> 去北京")
    page.locator("#userInput").fill("去北京")
    page.locator("#sendBtn").click()
    time.sleep(20)

    print("\n>>> 3个人玩3天")
    page.locator("#userInput").fill("3个人玩3天")
    page.locator("#sendBtn").click()
    time.sleep(20)

    # Check if style buttons appeared
    style_btns = page.locator(".style-btn")
    btn_count = style_btns.count()
    print(f"\n  Style buttons visible: {btn_count} (expected 4)")
    if btn_count == 4:
        for i in range(btn_count):
            print(f"    Button {i+1}: {style_btns.nth(i).text_content()}")
    assert btn_count == 4, f"Expected 4 style buttons, got {btn_count}"

    # Click the first button
    print("\n>>> Clicking: 🏖️ 悠闲娱乐度假为主啦")
    style_btns.nth(0).click()
    time.sleep(35)

    # === FEATURE 3: Weather cards in plan ===
    print("\n" + "=" * 60)
    print("FEATURE 3: Weather cards")
    print("=" * 60)

    # Check if plan card was generated
    plan_cards = page.locator(".plan-card")
    pc_count = plan_cards.count()
    print(f"  Plan cards: {pc_count}")
    assert pc_count > 0, "No plan card generated!"

    # Check for weather cards inside plan card
    weather_rows = page.locator(".weather-cards-row")
    wr_count = weather_rows.count()
    print(f"  Weather card rows: {wr_count}")

    weather_cards = page.locator(".weather-card")
    wc_count = weather_cards.count()
    print(f"  Individual weather cards: {wc_count}")

    if wc_count > 0:
        # Verify horizontal scroll
        row = weather_rows.first
        has_scroll = row.evaluate("el => el.scrollWidth > el.clientWidth")
        print(f"  Horizontal scroll enabled: {has_scroll}")
        # Show first card text
        first_card = weather_cards.first
        print(f"  First card text: {first_card.inner_text()[:200]}")

    # Also check the full plan card HTML
    plan_html = plan_cards.last.inner_html()
    print(f"\n  Plan card HTML length: {len(plan_html)}")
    print(f"  Has weather-cards-row: {'weather-cards-row' in plan_html}")
    print(f"  Has day-block: {'day-block' in plan_html}")

    # === FEATURE 4: Style confirmation ===
    confirmation = page.locator(".msg-user .bubble").last
    conf_text = confirmation.inner_text()
    print(f"\n  Confirmation text: {conf_text}")
    assert "已选择" in conf_text, "Should show style confirmation"

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)

    browser.close()
    server.shutdown()
