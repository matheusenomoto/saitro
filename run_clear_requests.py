from saitro_automation import SaitroAutomation

if __name__ == '__main__':
    automation = SaitroAutomation(headless=False, slow_mo=100)
    try:
        automation.clear_requests()
    finally:
        if automation.browser and not automation.browser.is_closed():
            automation.close()