from saitro_automation import SaitroAutomation

if __name__ == '__main__':
    automation = SaitroAutomation(headless=False, slow_mo=100)
    try:
        automation.clear_shopping_cart()
    finally:
        # Ensures the browser is closed even if an error occurs
        if automation.browser and not automation.browser.is_closed():
            automation.close()