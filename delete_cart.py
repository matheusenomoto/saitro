import os
import json
from playwright.sync_api import sync_playwright

def get_credentials():
    with open("user.json", 'r') as user:
        data = json.load(user)
    
    return data

print('-' * 30)
print('Robotic Process Automation - RPA')

def clear_cart():
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
        page.goto("https://tim.saitro.com/customer_care/ativacao/index/")

        print("[6] Selecionando o produto...")
        page.wait_for_selector("select[name='id_produto']")
        page.select_option("select[name='id_produto']", label="TIM 50MB R&T TIM Comp 30 IOT")

        print("[7] Carrinho de compras...")
        page.wait_for_selector("a[data-original-title='Visualizar']")

        print("[8] Clicando no carrinho compras...")
        page.click("a[data-original-title='Visualizar']")

        print("[9] Limpando carrinho de compras...")

        print("[9] Limpando carrinho de compras (dentro do modal)...")

        # Garante que o modal foi aberto após clicar em "Visualizar"
        page.wait_for_selector("div.modal-body", state="visible", timeout=5000)

        # Seleciona especificamente o botão "Limpar Carrinho" dentro do modal
        limpar_btn_modal = page.locator("div.modal-body tfoot a[data-original-title='Limpar Carrinho']")

        # Aguarda o botão estar visível
        limpar_btn_modal.wait_for(state="visible", timeout=5000)

        # Rola para ele estar visível
        limpar_btn_modal.scroll_into_view_if_needed()

        # Clica no botão correto dentro do modal
        limpar_btn_modal.click(force=True)

        # page.wait_for_selector("a[data-original-title='Limpar Carrinho']")
        # page.click("a[data-original-title='Limpar Carrinho']")
        

        print("[10] Confirmando limpeza do carrinho de compras...")
        # Aguarda o botão "Sim" aparecer visivelmente
        page.wait_for_selector('button.btn-send:text("Sim")', timeout=5000)

        # Clica no botão "Sim"
        page.click('button.btn-send:text("Sim")')

        print("[✅] Carrinho excluído com sucesso.")

        # Opcional: esperar para ver resultado
        page.wait_for_timeout(10000)
        browser.close()

clear_cart()
