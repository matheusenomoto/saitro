from saitro_automation import SaitroAutomation

if __name__ == '__main__':
    automation = SaitroAutomation(headless=False, slow_mo=100)
    try:
        # You can customize client_info and apn here
        automation.confirm_shopping_cart(
            client_info='Robotic Process Automation - Confirmed Order',
            apn='furukawaelectric.com.br'
        )
    finally:
        if automation.browser and not automation.browser.is_closed():
            automation.close()