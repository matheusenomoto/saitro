import os
import json
from playwright.sync_api import sync_playwright

# file_name = input('Qual o nome do arquivo? ')
file_name = 'dummy.csv'
# info_customer = input('Qual o nome inserino no campo \'Info Cliente\'? ')
info_customer = 'Robotic Process Automation - RPA'

def get_credentials():
    with open("user.json", 'r') as user:
        data = json.load(user)
    
    return data


print('-' * 30)
print('Robotic Process Automation - RPA')

def set_cart():
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

        print("[7] Aguardando botões aparecerem...")
        page.wait_for_selector("a[data-original-title='Adicionar via Carga']")

        print("[8] Clicando no botão 'Adicionar via Carga'...")
        page.click("a[data-original-title='Adicionar via Carga']")

        print("[9] Aguardando input de arquivo aparecer...")
        page.wait_for_selector("input[type='file'][name='arquivo']", timeout=10000)

        print("[10] Selecionando o arquivo 'teste1 1.csv'...")
        file_path = os.path.abspath(file_name)
        page.set_input_files("input[type='file'][name='arquivo']", file_path)

        print("[11] Clicando no botão 'Enviar'...")
        page.click("button#send")

        print("[✅] Arquivo enviado com sucesso.")

        # print("[12] Carrinho de compras...")
        # page.wait_for_selector("a[data-original-title='Visualizar']")

        # print("[13] Clicando no carrinho compras...")
        # page.click("a[data-original-title='Visualizar']")

        # print("[14] Processar carrinho de compras...")
        # page.wait_for_selector("button[id='processar']")
        # page.click("button[id='processar']")

        # print("[14] Preenchendo informações...")
        # page.wait_for_selector("input[name='info_cliente']")
        # page.fill("input[name='info_cliente']", info_customer)

        # print("[15] Selecionando APN 'furukawaelectric.com.br'...")
        # # [A] Clicar no botão de dropdown com title='Selecione'
        # page.click("button.dropdown-toggle[data-id='apns']")
        # # [B] Esperar o item desejado ficar visível
        # page.wait_for_selector("ul.dropdown-menu.inner li >> text=furukawaelectric.com.br", timeout=5000)
        # # [C] Clicar no item "furukawaelectric.com.br"
        # page.click("ul.dropdown-menu.inner li >> text=furukawaelectric.com.br")
        # print("[✅] APN selecionado com sucesso.")
        
        # print("[15] Confirmando processamento")
        # page.wait_for_selector('button[id="submitButton"]')
        # page.click('button[id="submitButton"]')
        # page.wait_for_selector("button.btn-send >> text=Sim", timeout=5000)

        # page.click("button.btn-send >> text=Sim")

        # print("[✅] Confirmação final concluída com sucesso.")

        # Opcional: esperar para ver resultado
        page.wait_for_timeout(10000)
        browser.close()

set_cart()

def get_thks_names():
    with open('thanks.json', 'r') as thk:
        data = json.load(thk)
        return data
    
def greeting():
    print('Big Thanks to:')
    data = get_thks_names()
    for n in data["names"]:
        print(n)

greeting()


