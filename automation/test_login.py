import pytest
from selenium.webdriver.common.by import By
from automation.pages.login_page import LoginPage


@pytest.mark.selenium
class TestLogin:
    def test_successful_login(self, driver, base_url, test_user):
        login_page = LoginPage(driver, base_url)
        login_page.open()
        login_page.login(test_user.username, 'testpass123')
        
        assert login_page.driver.current_url.endswith('/dashboard/')
        assert 'Welcome back' in driver.page_source or 'testuser' in driver.page_source

    def test_invalid_username(self, driver, base_url, test_user):
        login_page = LoginPage(driver, base_url)
        login_page.open()
        login_page.login('wronguser', 'testpass123')
        
        assert login_page.is_on_login_page()
        assert login_page.is_error_displayed()
        error_msg = login_page.get_error_message()
        assert 'Invalid username or password' in error_msg

    def test_invalid_password(self, driver, base_url, test_user):
        login_page = LoginPage(driver, base_url)
        login_page.open()
        login_page.login(test_user.username, 'wrongpass')
        
        assert login_page.is_on_login_page()
        assert login_page.is_error_displayed()
        error_msg = login_page.get_error_message()
        assert 'Invalid username or password' in error_msg

    def test_empty_username(self, driver, base_url):
        login_page = LoginPage(driver, base_url)
        login_page.open()
        login_page.fill(login_page.USERNAME, '')
        login_page.fill(login_page.PASSWORD, 'testpass123')
        login_page.click(login_page.LOGIN_BUTTON)
        
        assert login_page.is_on_login_page()
        username_error = login_page.get_field_error('username')
        assert username_error is not None
        assert 'required' in username_error.lower()

    def test_empty_password(self, driver, base_url, test_user):
        login_page = LoginPage(driver, base_url)
        login_page.open()
        login_page.fill(login_page.USERNAME, test_user.username)
        login_page.fill(login_page.PASSWORD, '')
        login_page.click(login_page.LOGIN_BUTTON)
        
        assert login_page.is_on_login_page()
        password_error = login_page.get_field_error('password')
        assert password_error is not None
        assert 'required' in password_error.lower()

    def test_both_empty(self, driver, base_url):
        login_page = LoginPage(driver, base_url)
        login_page.open()
        login_page.click(login_page.LOGIN_BUTTON)
        
        assert login_page.is_on_login_page()
        username_error = login_page.get_field_error('username')
        password_error = login_page.get_field_error('password')
        assert username_error is not None
        assert password_error is not None

    def test_logout(self, logged_in_driver, base_url):
        from automation.pages.login_page import DashboardPage
        
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.logout()
        
        login_page = LoginPage(logged_in_driver, base_url)
        assert login_page.is_on_login_page()
        assert 'logged out' in logged_in_driver.page_source.lower()
    
    def test_access_dashboard_without_auth(self, driver, base_url):
        from automation.pages.login_page import DashboardPage, LoginPage
        
        dashboard_page = DashboardPage(driver, base_url)
        dashboard_page.open()
        
        login_page = LoginPage(driver, base_url)
        assert login_page.is_on_login_page()

    def test_redirect_after_login(self, driver, base_url, test_user):
        login_page = LoginPage(driver, base_url)
        login_page.open()
        login_page.login(test_user.username, 'testpass123')
        
        assert driver.current_url.endswith('/dashboard/')

    def test_redirect_authenticated_user_from_login(self, logged_in_driver, base_url):
        # Navigate to login page - should redirect to dashboard
        logged_in_driver.get(f'{base_url}/login/')
        
        from automation.pages.login_page import DashboardPage
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        assert dashboard_page.is_on_dashboard()

    def test_login_form_elements_present(self, driver, base_url):
        login_page = LoginPage(driver, base_url)
        login_page.open()
        
        assert login_page.is_visible(login_page.USERNAME)
        assert login_page.is_visible(login_page.PASSWORD)
        assert login_page.is_visible(login_page.LOGIN_BUTTON)
        assert login_page.is_visible(login_page.LOGIN_FORM)
        assert login_page.is_visible(login_page.CARD)

    def test_login_form_attributes(self, driver, base_url):
        login_page = LoginPage(driver, base_url)
        login_page.open()
        
        username_input = login_page.driver.find_element(*login_page.USERNAME)
        password_input = login_page.driver.find_element(*login_page.PASSWORD)
        login_button = login_page.driver.find_element(*login_page.LOGIN_BUTTON)
        
        assert username_input.get_attribute('id') == 'login-username'
        assert username_input.get_attribute('name') == 'username'
        assert username_input.get_attribute('data-test') == 'login-username'
        assert password_input.get_attribute('id') == 'login-password'
        assert password_input.get_attribute('name') == 'password'
        assert password_input.get_attribute('data-test') == 'login-password'
        assert login_button.get_attribute('id') == 'login-submit'
        assert login_button.get_attribute('data-test') == 'login-submit'

    def test_csrf_token_present(self, driver, base_url):
        login_page = LoginPage(driver, base_url)
        login_page.open()
        
        csrf_input = login_page.driver.find_element(By.NAME, 'csrfmiddlewaretoken')
        assert csrf_input is not None
        assert csrf_input.get_attribute('value') != ''

    def test_remember_username_on_failed_login(self, driver, base_url, test_user):
        login_page = LoginPage(driver, base_url)
        login_page.open()
        login_page.fill(login_page.USERNAME, test_user.username)
        login_page.fill(login_page.PASSWORD, 'wrongpass')
        login_page.click(login_page.LOGIN_BUTTON)
        
        assert login_page.get_username_value() == test_user.username