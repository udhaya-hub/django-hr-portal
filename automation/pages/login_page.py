from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class BasePage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url.rstrip('/')
        self.wait = WebDriverWait(driver, 10)
    
    def open(self, path=''):
        url = f'{self.base_url}{path}'
        self.driver.get(url)
        self.wait_for_page_load()
    
    def wait_for_page_load(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
    
    def find(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
    
    def find_all(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located(locator)
        )
    
    def click(self, locator, timeout=10):
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
        element.click()
        return element
    
    def fill(self, locator, text, timeout=10):
        element = self.find(locator, timeout)
        element.clear()
        element.send_keys(text)
        return element
    
    def get_text(self, locator, timeout=10):
        element = self.find(locator, timeout)
        return element.text.strip()
    
    def is_visible(self, locator, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def is_not_visible(self, locator, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def wait_for_url_contains(self, text, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.url_contains(text)
        )
    
    def get_current_url(self):
        return self.driver.current_url


class LoginPage(BasePage):
    URL_PATH = '/login/'
    
    USERNAME = (By.ID, 'login-username')
    PASSWORD = (By.ID, 'login-password')
    LOGIN_BUTTON = (By.ID, 'login-submit')
    LOGIN_FORM = (By.ID, 'login-form')
    ERROR_CONTAINER = (By.ID, 'login-error')
    ERROR_MESSAGE = (By.ID, 'login-error-message')
    USERNAME_ERROR = (By.ID, 'login-username-error')
    PASSWORD_ERROR = (By.ID, 'login-password-error')
    DJANGO_MESSAGES = (By.CSS_SELECTOR, '[data-test="message-error"]')
    CARD = (By.CSS_SELECTOR, '[data-test="login-card"]')
    
    def open(self):
        super().open(self.URL_PATH)
        self.wait.until(EC.visibility_of_element_located(self.USERNAME))
    
    def login(self, username, password):
        self.fill(self.USERNAME, username)
        self.fill(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)
        self.wait_for_page_load()
    
    def login_with_empty_credentials(self):
        self.click(self.LOGIN_BUTTON)
        self.wait_for_page_load()
    
    def get_error_message(self):
        # Check for Django messages first (server-side validation)
        if self.is_visible(self.DJANGO_MESSAGES):
            return self.get_text(self.DJANGO_MESSAGES)
        # Fallback to client-side error container
        if self.is_visible(self.ERROR_CONTAINER):
            try:
                return self.get_text(self.ERROR_MESSAGE)
            except TimeoutException:
                return self.get_text(self.ERROR_CONTAINER)
        return None
    
    def get_field_error(self, field_name):
        error_map = {
            'username': self.USERNAME_ERROR,
            'password': self.PASSWORD_ERROR,
        }
        locator = error_map.get(field_name)
        if locator and self.is_visible(locator):
            return self.get_text(locator)
        return None
    
    def is_on_login_page(self):
        try:
            self.wait.until(EC.url_contains('/login/'))
            return self.is_visible(self.USERNAME) and self.is_visible(self.PASSWORD)
        except TimeoutException:
            return False
    
    def is_error_displayed(self):
        return self.is_visible(self.DJANGO_MESSAGES) or self.is_visible(self.ERROR_CONTAINER)
    
    def get_username_value(self):
        return self.driver.find_element(*self.USERNAME).get_attribute('value')
    
    def get_password_value(self):
        return self.driver.find_element(*self.PASSWORD).get_attribute('value')


class DashboardPage(BasePage):
    URL_PATH = '/dashboard/'
    
    PAGE_TITLE = (By.CSS_SELECTOR, '[data-test="dashboard-title"]')
    WELCOME_MESSAGE = (By.CSS_SELECTOR, '[data-test="welcome-message"]')
    ADD_EMPLOYEE_BUTTON = (By.ID, 'add-employee')
    SEARCH_INPUT = (By.ID, 'employee-search')
    SEARCH_FORM = (By.ID, 'search-form')
    SEARCH_SUBMIT = (By.CSS_SELECTOR, '[data-test="search-submit"]')
    SEARCH_CLEAR = (By.CSS_SELECTOR, '[data-test="search-clear"]')
    EMPLOYEE_TABLE = (By.ID, 'employee-table')
    EMPLOYEE_ROWS = (By.CSS_SELECTOR, '[data-test="employee-row"]')
    EMPTY_STATE = (By.CSS_SELECTOR, '[data-test="empty-state"]')
    EMPLOYEE_COUNT = (By.CSS_SELECTOR, '[data-test="employee-count"]')
    LOGOUT_BUTTON = (By.CSS_SELECTOR, '[data-test="nav-logout"]')
    NAV_DASHBOARD = (By.CSS_SELECTOR, '[data-test="nav-dashboard"]')
    NAV_ADD_EMPLOYEE = (By.CSS_SELECTOR, '[data-test="nav-add-employee"]')
    
    def open(self):
        super().open(self.URL_PATH)
        self.wait_for_page_load()
    
    def wait_for_page_load(self, timeout=10):
        super().wait_for_page_load(timeout)
        # Check if we're on dashboard or redirected to login
        try:
            self.wait.until(EC.visibility_of_element_located(self.PAGE_TITLE))
        except TimeoutException:
            # Might be redirected to login
            pass
    
    def is_on_dashboard(self):
        try:
            self.wait.until(EC.url_contains('/dashboard/'))
            return self.is_visible(self.PAGE_TITLE)
        except TimeoutException:
            return False
    
    def click_add_employee(self):
        self.click(self.ADD_EMPLOYEE_BUTTON)
        self.wait_for_page_load()
    
    def search(self, query):
        self.fill(self.SEARCH_INPUT, query)
        self.click(self.SEARCH_SUBMIT)
        self.wait_for_page_load()
    
    def clear_search(self):
        if self.is_visible(self.SEARCH_CLEAR):
            self.click(self.SEARCH_CLEAR)
            self.wait_for_page_load()
    
    def get_search_value(self):
        return self.driver.find_element(*self.SEARCH_INPUT).get_attribute('value')
    
    def get_employee_rows(self):
        if self.is_visible(self.EMPTY_STATE):
            return []
        return self.find_all(self.EMPLOYEE_ROWS)
    
    def get_employee_count(self):
        try:
            return self.get_text(self.EMPLOYEE_COUNT)
        except TimeoutException:
            return '0'
    
    def get_employee_data(self, row_index=0):
        rows = self.get_employee_rows()
        if not rows or row_index >= len(rows):
            return None
        
        row = rows[row_index]
        cells = row.find_elements(By.TAG_NAME, 'td')
        
        return {
            'employee_id': cells[0].text.strip() if len(cells) > 0 else '',
            'name': cells[1].text.strip() if len(cells) > 1 else '',
            'department': cells[2].text.strip() if len(cells) > 2 else '',
            'status': cells[3].text.strip() if len(cells) > 3 else '',
        }
    
    def find_employee_by_id(self, employee_id):
        rows = self.get_employee_rows()
        for i, row in enumerate(rows):
            try:
                emp_id_cell = row.find_element(By.CSS_SELECTOR, '[data-test="employee-id"]')
                if emp_id_cell.text.strip() == employee_id:
                    return i
            except:
                continue
        return -1
    
    def get_welcome_message(self):
        return self.get_text(self.WELCOME_MESSAGE)
    
    def logout(self):
        # Logout button is in the sidebar
        self.click(self.LOGOUT_BUTTON)
        self.wait_for_page_load()
        self.wait_for_page_load()
    
    def is_employee_present(self, employee_id):
        return self.find_employee_by_id(employee_id) >= 0
    
    def get_table_headers(self):
        headers = self.driver.find_elements(By.CSS_SELECTOR, '#employee-table th')
        return [h.text.strip() for h in headers]


class EmployeePage(BasePage):
    URL_PATH = '/employees/add/'
    
    PAGE_TITLE = (By.CSS_SELECTOR, '[data-test="form-title"]')
    FORM = (By.ID, 'employee-form')
    FIRST_NAME = (By.ID, 'first-name')
    LAST_NAME = (By.ID, 'last-name')
    EMPLOYEE_ID = (By.ID, 'employee-id')
    DEPARTMENT = (By.ID, 'department')
    EMPLOYMENT_STATUS = (By.ID, 'employment-status')
    SAVE_BUTTON = (By.ID, 'save-employee')
    CANCEL_BUTTON = (By.ID, 'cancel-btn')
    CANCEL_LINK = (By.CSS_SELECTOR, '[data-test="cancel-link"]')
    
    FIRST_NAME_ERROR = (By.ID, 'first-name-error')
    LAST_NAME_ERROR = (By.ID, 'last-name-error')
    EMPLOYEE_ID_ERROR = (By.ID, 'employee-id-error')
    DEPARTMENT_ERROR = (By.ID, 'department-error')
    EMPLOYMENT_STATUS_ERROR = (By.ID, 'employment-status-error')
    
    FIRST_NAME_SERVER_ERROR = (By.CSS_SELECTOR, '[data-test="first-name-server-error"]')
    LAST_NAME_SERVER_ERROR = (By.CSS_SELECTOR, '[data-test="last-name-server-error"]')
    EMPLOYEE_ID_SERVER_ERROR = (By.CSS_SELECTOR, '[data-test="employee-id-server-error"]')
    DEPARTMENT_SERVER_ERROR = (By.CSS_SELECTOR, '[data-test="department-server-error"]')
    EMPLOYMENT_STATUS_SERVER_ERROR = (By.CSS_SELECTOR, '[data-test="employment-status-server-error"]')
    NON_FIELD_ERRORS = (By.CSS_SELECTOR, '[data-test="form-non-field-errors"]')
    
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, '[data-test="message-success"]')
    
    def open(self):
        super().open(self.URL_PATH)
        self.wait.until(EC.visibility_of_element_located(self.FIRST_NAME))
    
    def wait_for_page_load(self, timeout=10):
        super().wait_for_page_load(timeout)
        self.wait.until(EC.visibility_of_element_located(self.FIRST_NAME))
    
    def is_on_employee_page(self):
        try:
            self.wait.until(EC.url_contains('/employees/add/'))
            return self.is_visible(self.FIRST_NAME)
        except TimeoutException:
            return False
    
    def fill_form(self, data):
        if 'first_name' in data:
            self.fill(self.FIRST_NAME, data['first_name'])
        if 'last_name' in data:
            self.fill(self.LAST_NAME, data['last_name'])
        if 'employee_id' in data:
            self.fill(self.EMPLOYEE_ID, data['employee_id'])
        if 'department' in data:
            self.select_department(data['department'])
        if 'employment_status' in data:
            self.select_status(data['employment_status'])
    
    def select_department(self, department):
        from selenium.webdriver.support.ui import Select
        select = Select(self.find(self.DEPARTMENT))
        select.select_by_visible_text(department)
    
    def select_status(self, status):
        from selenium.webdriver.support.ui import Select
        select = Select(self.find(self.EMPLOYMENT_STATUS))
        select.select_by_visible_text(status)
    
    def get_department_value(self):
        from selenium.webdriver.support.ui import Select
        select = Select(self.find(self.DEPARTMENT))
        return select.first_selected_option.text
    
    def get_status_value(self):
        from selenium.webdriver.support.ui import Select
        select = Select(self.find(self.EMPLOYMENT_STATUS))
        return select.first_selected_option.text
    
    def submit(self):
        self.click(self.SAVE_BUTTON)
        self.wait_for_page_load()
    
    def cancel(self):
        self.click(self.CANCEL_BUTTON)
        self.wait_for_page_load()
    
    def cancel_via_link(self):
        self.click(self.CANCEL_LINK)
        self.wait_for_page_load()
    
    def get_field_error(self, field_name):
        error_map = {
            'first_name': self.FIRST_NAME_ERROR,
            'last_name': self.LAST_NAME_ERROR,
            'employee_id': self.EMPLOYEE_ID_ERROR,
            'department': self.DEPARTMENT_ERROR,
            'employment_status': self.EMPLOYMENT_STATUS_ERROR,
        }
        locator = error_map.get(field_name)
        if locator and self.is_visible(locator):
            return self.get_text(locator)
        return None
    
    def get_server_error(self, field_name):
        error_map = {
            'first_name': self.FIRST_NAME_SERVER_ERROR,
            'last_name': self.LAST_NAME_SERVER_ERROR,
            'employee_id': self.EMPLOYEE_ID_SERVER_ERROR,
            'department': self.DEPARTMENT_SERVER_ERROR,
            'employment_status': self.EMPLOYMENT_STATUS_SERVER_ERROR,
        }
        locator = error_map.get(field_name)
        if locator and self.is_visible(locator):
            return self.get_text(locator)
        return None
    
    def get_non_field_errors(self):
        if self.is_visible(self.NON_FIELD_ERRORS):
            return self.get_text(self.NON_FIELD_ERRORS)
        return None
    
    def get_success_message(self):
        if self.is_visible(self.SUCCESS_MESSAGE):
            return self.get_text(self.SUCCESS_MESSAGE)
        return None
    
    def get_field_value(self, field_name):
        field_map = {
            'first_name': self.FIRST_NAME,
            'last_name': self.LAST_NAME,
            'employee_id': self.EMPLOYEE_ID,
        }
        locator = field_map.get(field_name)
        if locator:
            return self.driver.find_element(*locator).get_attribute('value')
        return None
    
    def is_save_button_disabled(self):
        try:
            button = self.driver.find_element(*self.SAVE_BUTTON)
            return button.get_attribute('disabled') == 'true'
        except:
            return False
    
    def clear_form(self):
        self.fill(self.FIRST_NAME, '')
        self.fill(self.LAST_NAME, '')
        self.fill(self.EMPLOYEE_ID, '')
        self.select_department('')
        self.select_status('')