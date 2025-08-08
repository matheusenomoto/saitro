from saitro_automation import SaitroAutomation
import os

if __name__ == '__main__':
    automation = SaitroAutomation(headless=False, slow_mo=100)
    try:
        # Intermediate Refactoring: Capable of reading the CSV file name
        # You can prompt the user for the file name:
        csv_file_name = input('Please enter the name of the CSV file to upload (e.g., dummy.csv): ')
        # Or, you can hardcode it for specific automated runs:
        # csv_file_name = 'dummy.csv'

        automation.set_shopping_cart(file_path=csv_file_name)
    finally:
        if automation.browser and not automation.browser.is_closed():
            automation.close()