# saitro_automation.py
import os
import json
from playwright.sync_api import sync_playwright, Page, BrowserContext

# --- Constants and Configuration ---
# All file paths and URLs are defined as constants for easy modification
# and better readability.
USER_CREDENTIALS_PATH = 'user.json'
LOGIN_STATE_PATH = 'tim_login_state.json'
LOGIN_DEBUG_HTML_PATH = 'login_debug.html'
THANKS_NAMES_PATH = 'thanks.json'

# URLs for the Saitro platform
LOGIN_URL = 'https://tim.saitro.com/sistema/login/'
ACTIVATION_URL = 'https://tim.saitro.com/customer_care/ativacao/index/'
REQUEST_URL = 'https://tim.saitro.com/customer_care/solicitacao/index/'

class SaitroAutomation:
    '''
    A class to encapsulate Robotic Process Automation (RPA) tasks
    for the Saitro platform using Playwright.
    '''
    def __init__(self, headless: bool = False, slow_mo: int = 100):
        '''
        Initializes the SaitroAutomation instance.

        Args:
            headless (bool): If True, the browser runs in headless mode (no UI).
                             Defaults to False for visibility during development/debugging.
            slow_mo (int): Slows down Playwright operations by the specified amount of milliseconds.
                           Useful for debugging and observing actions. Defaults to 100ms.
        '''
        print('-' * 30)
        print('Robotic Process Automation - Saitro')
        self.playwright = sync_playwright().start()
        # Launch Chromium browser with specified options
        self.browser = self.playwright.chromium.launch(headless=headless, slow_mo=slow_mo)
        # Create a new browser context
        self.context: BrowserContext = self.browser.new_context()
        # Create a new page within the context
        self.page: Page = self.context.new_page()

    def _get_credentials(self) -> dict:
        '''
        Reads user credentials from the user.json file.

        Returns:
            dict: A dictionary containing 'user' and 'pwd'.
        '''
        try:
            with open(USER_CREDENTIALS_PATH, 'r') as user_file:
                credentials = json.load(user_file)
            return credentials
        except FileNotFoundError:
            print(f'Error: Credential file \'{USER_CREDENTIALS_PATH}\' not found.')
            # Exit or raise an exception as credentials are essential
            raise

    def login(self) -> bool:
        '''
        Performs the login operation on the Saitro platform.

        Returns:
            bool: True if login is successful and redirected to dashboard, False otherwise.
        '''
        print('[1] Opening login page...')
        self.page.goto(LOGIN_URL)

        print('[2] Filling login form...')
        credentials = self._get_credentials()
        self.page.fill('input#login', credentials['user'])
        self.page.fill('input#senha', credentials['pwd']) # 'senha' is an HTML attribute, kept as is

        print('[3] Clicking login button...')
        self.page.click('button[data-post=\'ajax-login\']')

        print('[4] Waiting for redirect or dashboard...')
        try:
            # Wait for URL to contain 'dashboard' indicating successful login
            self.page.wait_for_url('**/dashboard/**', timeout=10000)
            print('[] Login succeeded! Current URL:', self.page.url)
            # Save the storage state (cookies, local storage) for potential future re-use
            self.context.storage_state(path=LOGIN_STATE_PATH)
            return True
        except Exception as e:
            print(f'[] Login did not redirect. Still at: {self.page.url}. Error: {e}')
            # Save page content for debugging if login fails
            with open(LOGIN_DEBUG_HTML_PATH, 'w', encoding='utf-8') as f:
                f.write(self.page.content())
            return False

    def select_product(self, product_label: str = 'TIM 50MB R&T TIM Comp 30 IOT'):
        '''
        Selects a specific product from the dropdown on the activation page.

        Args:
            product_label (str): The label of the product to select.
        '''
        print(f'[6] Selecting the product: \'{product_label}\'...')
        self.page.wait_for_selector('select[name=\'id_produto\']') # 'id_produto' is an HTML attribute, kept as is
        self.page.select_option('select[name=\'id_produto\']', label=product_label)

    def clear_shopping_cart(self):
        '''
        Navigates to the activation page, selects a product,
        and clears the shopping cart through a modal.
        '''
        # Ensure user is logged in before proceeding
        if not self.login():
            print('Automation stopped: Login failed.')
            return

        print('[5] Accessing activation page...')
        self.page.goto(ACTIVATION_URL)
        self.select_product()

        print('[7] Shopping cart...')
        self.page.wait_for_selector('a[data-original-title=\'Visualizar\']')

        print('[8] Clicking on the shopping cart...')
        self.page.click('a[data-original-title=\'Visualizar\']')

        print('[9] Clearing shopping cart (inside modal)...')
        # Ensures the modal was opened after clicking "View"
        self.page.wait_for_selector('div.modal-body', state='visible', timeout=5000)
        # Selects specifically the "Clear Cart" button inside the modal
        clear_cart_button_modal = self.page.locator('div.modal-body a[data-original-title=\'Limpar Carrinho\']')
        # Waits for the button to be visible
        clear_cart_button_modal.wait_for(state='visible', timeout=5000)
        # Scrolls to make it visible
        clear_cart_button_modal.scroll_into_view_if_needed()
        # Clicks the correct button inside the modal using force click if necessary
        clear_cart_button_modal.click(force=True)

        print('[10] Confirming shopping cart clear...')
        # Waits for the "Yes" button to appear visibly in the confirmation dialog
        self.page.wait_for_selector('button.btn-send:text(\'Sim\')', timeout=5000)
        # Clicks the "Yes" button
        self.page.click('button.btn-send:text(\'Sim\')')
        print('[] Cart successfully deleted.')

        # Optional: wait to observe the result before closing the browser
        self.page.wait_for_timeout(10000)
        self.close()

    def set_shopping_cart(self, file_path: str):
        '''
        Navigates to the activation page, selects a product,
        and uploads a CSV file to set the shopping cart.

        Args:
            file_path (str): The absolute or relative path to the CSV file to upload.
        '''
        # Ensure user is logged in before proceeding
        if not self.login():
            print('Automation stopped: Login failed.')
            return

        print('[5] Accessing activation page...')
        self.page.goto(ACTIVATION_URL)
        self.select_product()

        print('[7] Waiting for buttons to appear...')
        self.page.wait_for_selector('a[data-original-title=\'Adicionar via Carga\']')
        print('[8] Clicking on \'Add via Upload\' button...')
        self.page.click('a[data-original-title=\'Adicionar via Carga\']')
        # The original script clicked twice, if necessary, uncomment the line below:
        # self.page.click('a[data-original-title=\'Adicionar via Carga\']')

        print('[9] Waiting for file input to appear...')
        self.page.wait_for_selector('input[type=\'file\'][name=\'arquivo\']', timeout=10000) # 'arquivo' is HTML attribute, kept as is

        # Resolve the absolute path of the file
        absolute_file_path = os.path.abspath(file_path)
        print(f'[10] Selecting the file \'{os.path.basename(absolute_file_path)}\'...')

        # Check if the file exists before attempting to upload
        if not os.path.exists(absolute_file_path):
            print(f'Error: File not found at \'{absolute_file_path}\'. Automation aborted.')
            self.close()
            return

        self.page.set_input_files('input[type=\'file\'][name=\'arquivo\']', absolute_file_path)

        print('[11] Clicking the \'Submit\' button...')
        self.page.click('button#send')
        print('[] File successfully uploaded.')

        # Optional: wait to observe the result before closing the browser
        self.page.wait_for_timeout(10000)
        self.close()

    def confirm_shopping_cart(self, client_info: str = 'Robotic Process Automation - RPA', apn: str = 'furukawaelectric.com.br'):
        '''
        Navigates to the activation page, selects a product,
        confirms the shopping cart, fills in client information,
        and selects an APN.

        Args:
            client_info (str): The client information to fill in the 'Info Cliente' field.
            apn (str): The APN to select from the dropdown.
        '''
        # Ensure user is logged in before proceeding
        if not self.login():
            print('Automation stopped: Login failed.')
            return

        print('[5] Accessing activation page...')
        self.page.goto(ACTIVATION_URL)
        self.select_product()

        print('[7] Shopping cart...')
        self.page.wait_for_selector('a[data-original-title=\'Visualizar\']')
        print('[8] Clicking on the shopping cart...')
        self.page.click('a[data-original-title=\'Visualizar\']')

        print('[9] Process shopping cart...')
        self.page.wait_for_selector('button[id=\'processar\']')
        self.page.click('button[id=\'processar\']')

        print('[10] Filling information...')
        self.page.wait_for_selector('input[name=\'info_cliente\']') # 'info_cliente' is HTML attribute, kept as is
        self.page.fill('input[name=\'info_cliente\']', client_info)

        print(f'[11] Selecting APN \'{apn}\'...')
        # [A] Click the dropdown button with title='Selecione'
        self.page.click('button.dropdown-toggle[data-id=\'apns\']')
        # [B] Wait for the desired item to become visible
        self.page.wait_for_selector(f'ul.dropdown-menu.inner li:text(\'{apn}\')', timeout=5000)
        # [C] Click the item "furukawaelectric.com.br"
        self.page.click(f'ul.dropdown-menu.inner li:text(\'{apn}\')')
        print('[] APN selected successfully.')

        print('[12] Confirming processing')
        self.page.wait_for_selector('button[id=\'submitButton\']')
        self.page.click('button[id=\'submitButton\']')
        # Wait for the "Yes" button in the final confirmation dialog
        self.page.wait_for_selector('button.btn-send:text(\'Sim\')', timeout=5000)
        self.page.click('button.btn-send:text(\'Sim\')')
        print('[] Final confirmation completed successfully.')

        # Optional: wait to observe the result before closing the browser
        self.page.wait_for_timeout(10000)
        self.close()

    def clear_requests(self):
        '''
        Navigates to the requests page and clears outstanding requests.
        '''
        # Ensure user is logged in before proceeding
        if not self.login():
            print('Automation stopped: Login failed.')
            return

        print('[5] Accessing request page...') # Corrected print message
        self.page.goto(REQUEST_URL)

        print('[6] Waiting for \'Cancel Request\' button to appear...')
        self.page.wait_for_selector('a.icon-red[data-original-title=\'Cancelar Solicitação\']', timeout=5000)
        print('[7] Clicking on \'Cancel Request\' button...')
        self.page.click('a.icon-red[data-original-title=\'Cancelar Solicitação\']')

        # Wait for and click the "Yes" button in the confirmation dialog
        self.page.wait_for_selector('button.btn-send:text(\'Sim\')', timeout=5000)
        self.page.click('button.btn-send:text(\'Sim\')')
        print('[] Request successfully cleared.')

        # Optional: wait to observe the result before closing the browser
        self.page.wait_for_timeout(10000)
        self.close()

    def close(self):
        '''
        Closes the browser and stops the Playwright instance.
        This should always be called after automation tasks are complete.
        '''
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print('Automation finished. Browser closed.')
        print('-' * 30)

# --- Helper functions (from original scripts, not part of SaitroAutomation class) ---
def get_thanks_names() -> dict:
    '''
    Reads names from the thanks.json file.
    '''
    try:
        with open(THANKS_NAMES_PATH, 'r') as thk_file:
            data = json.load(thk_file)
        return data
    except FileNotFoundError:
        print(f'Error: Thanks file \'{THANKS_NAMES_PATH}\' not found.')
        return {'names': []}


def greet_thanks():
    '''
    Prints a greeting with names from the thanks.json file.
    '''
    print('Big Thanks to:')
    names_data = get_thanks_names()
    for name in names_data.get('names', []): # Use .get() for safety
        print(name)

# Example Usage: (These blocks would typically be in separate files
# or a main script that orchestrates the automation tasks.)
if __name__ == '__main__':
    # This block shows how you would use the SaitroAutomation class.
    # You can choose to run specific functions by uncommenting them.

    # Example: Clear Shopping Cart
    # automation = SaitroAutomation(headless=False)
    # automation.clear_shopping_cart()

    # Example: Set Shopping Cart (Uploading a CSV file)
    # This demonstrates reading the CSV file name dynamically.
    # automation = SaitroAutomation(headless=False)
    # csv_file_to_upload = input('Enter the path to the CSV file to upload (e.g., dummy.csv): ')
    # automation.set_shopping_cart(csv_file_to_upload)

    # Example: Confirm Shopping Cart
    automation = SaitroAutomation(headless=False)
    automation.confirm_shopping_cart(client_info='My RPA Test Client', apn='furukawaelectric.com.br')

    # Example: Clear Requests
    # automation = SaitroAutomation(headless=False)
    # automation.clear_requests()

    # Example: Greeting
    # greet_thanks()
    pass # Keep 'pass' if no examples are uncommented