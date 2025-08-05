from playwright.sync_api import sync_playwright

def login_to_tim():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)  # slows down actions for visibility
        context = browser.new_context()
        page = context.new_page()

        print("[1] Opening login page...")
        page.goto("https://tim.saitro.com/sistema/login/")

        print("[2] Filling login form...")
        page.fill("input#login", "matheus.enomoto@lightera.com")
        page.fill("input#senha", "wButtN56g@iC3jb")

        print("[3] Clicking login button...")
        page.click("button[data-post='ajax-login']")

        # [4] Wait for redirect or known element from dashboard
        print("[4] Waiting for redirect or dashboard...")
        try:
            page.wait_for_url("**/dashboard/**", timeout=10000)
            print("[✅] Login succeeded! Current URL:", page.url)
        except:
            print("[⚠️] Login did not redirect. Still at:", page.url)
            print("[ℹ️] Capturing page HTML for inspection...")
            with open("login_debug.html", "w", encoding="utf-8") as f:
                f.write(page.content())

        # Optional: Save session
        context.storage_state(path="tim_login_state.json")

        print("[5] Leaving browser open for manual inspection...")
        page.wait_for_timeout(10000)  # Wait 10s before closing
        browser.close()

login_to_tim()
