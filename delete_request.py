import os
import json
from playwright.sync_api import sync_playwright

def get_credentials():
    with open("user.json", 'r') as user:
        data = json.load(user)
    
    return data

print('-' * 30)
print('Robotic Process Automation - RPA')

def clear_requests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context()
        page = context.new_page()

        print("[1] Opening login page...")
        page.goto("https://tim.saitro.com/sistema/login/")

        print("[2] Filling login form...")
        cred = get_credentials()
        page.fill("input#login", cred['user'])
        page.fill("input#senha", cred['pwd'])

        print("[3] Clicking login button...")
        page.click("button[data-post='ajax-login']")

        print("[4] Waiting for redirect or dashboard...")
        try:
            page.wait_for_url("**/dashboard/**", timeout=10000)
            print("[✅] Login succeeded! Current URL:", page.url)
        except:
            print("[⚠️] Login did not redirect. Still at:", page.url)
            with open("login_debug.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            browser.close()
            return

        context.storage_state(path="tim_login_state.json")

        print("[5] Acessando página de ativação...")
        page.goto("https://tim.saitro.com/customer_care/solicitacao/index/")

        print("[6] Aguardando botão 'Cancelar Solicitação' aparecer...")
        page.wait_for_selector("a.icon-red[data-original-title='Cancelar Solicitação']", timeout=5000)

        print("[7] Clicando no botão 'Cancelar Solicitação'...")
        page.click("a.icon-red[data-original-title='Cancelar Solicitação']")

        page.wait_for_selector("button.btn-send >> text=Sim", timeout=5000)
        page.click("button.btn-send >> text=Sim")

        # Opcional: esperar para ver resultado
        page.wait_for_timeout(10000)
        browser.close()

clear_requests()
