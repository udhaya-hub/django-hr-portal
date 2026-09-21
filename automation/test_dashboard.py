import pytest
from selenium.webdriver.common.by import By
from automation.pages.login_page import DashboardPage, LoginPage


@pytest.mark.selenium
class TestDashboard:
    def test_dashboard_loads_after_login(self, logged_in_driver, base_url):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        assert dashboard_page.is_on_dashboard()
        assert dashboard_page.is_visible(dashboard_page.PAGE_TITLE)

    def test_employee_table_displayed(self, logged_in_driver, base_url, multiple_employees):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        rows = dashboard_page.get_employee_rows()
        assert len(rows) == 5
        
        headers = dashboard_page.get_table_headers()
        expected_headers = ['Employee ID', 'Name', 'Department', 'Employment Status', 'Actions']
        assert headers == expected_headers

    def test_search_functionality(self, logged_in_driver, base_url, multiple_employees):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        dashboard_page.search('EMP001')
        rows = dashboard_page.get_employee_rows()
        assert len(rows) == 1
        emp_data = dashboard_page.get_employee_data(0)
        assert emp_data['employee_id'] == 'EMP001'
        
        dashboard_page.clear_search()
        rows = dashboard_page.get_employee_rows()
        assert len(rows) == 5

    def test_search_by_name(self, logged_in_driver, base_url, multiple_employees):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        dashboard_page.search('John')
        rows = dashboard_page.get_employee_rows()
        assert len(rows) == 1
        emp_data = dashboard_page.get_employee_data(0)
        assert 'John' in emp_data['name']
        
        dashboard_page.clear_search()

    def test_search_by_department(self, logged_in_driver, base_url, multiple_employees):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        dashboard_page.search('Engineering')
        rows = dashboard_page.get_employee_rows()
        assert len(rows) == 1
        emp_data = dashboard_page.get_employee_data(0)
        assert emp_data['department'] == 'Engineering'
        
        dashboard_page.clear_search()

    def test_search_no_results(self, logged_in_driver, base_url, multiple_employees):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        dashboard_page.search('NonExistent')
        
        assert dashboard_page.is_visible(dashboard_page.EMPTY_STATE)
        rows = dashboard_page.get_employee_rows()
        assert len(rows) == 0
        
        dashboard_page.clear_search()

    def test_add_employee_button_navigation(self, logged_in_driver, base_url):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        dashboard_page.click_add_employee()
        
        from automation.pages.employee_page import EmployeePage
        employee_page = EmployeePage(logged_in_driver, base_url)
        assert employee_page.is_on_employee_page()

    def test_logout_button(self, logged_in_driver, base_url):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        dashboard_page.logout()
        
        login_page = LoginPage(logged_in_driver, base_url)
        assert login_page.is_on_login_page()

    def test_welcome_message_shows_username(self, logged_in_driver, base_url, test_user):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        welcome_msg = dashboard_page.get_welcome_message()
        assert test_user.username in welcome_msg

    def test_employee_count_displayed(self, logged_in_driver, base_url, multiple_employees):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        count_text = dashboard_page.get_employee_count()
        assert '5' in count_text

    def test_employee_status_badges(self, logged_in_driver, base_url, multiple_employees):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        active_rows = 0
        inactive_rows = 0
        on_leave_rows = 0
        
        rows = dashboard_page.get_employee_rows()
        for row in rows:
            status_cell = row.find_element(By.CSS_SELECTOR, '[data-test="employee-status"]')
            status_text = status_cell.text.strip()
            if 'Active' in status_text:
                active_rows += 1
            elif 'Inactive' in status_text:
                inactive_rows += 1
            elif 'On Leave' in status_text:
                on_leave_rows += 1
        
        assert active_rows == 3
        assert inactive_rows == 1
        assert on_leave_rows == 1

    def test_find_employee_by_id(self, logged_in_driver, base_url, multiple_employees):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        index = dashboard_page.find_employee_by_id('EMP003')
        assert index >= 0
        emp_data = dashboard_page.get_employee_data(index)
        assert emp_data['employee_id'] == 'EMP003'
        assert emp_data['name'] == 'Bob Wilson'
        
        index = dashboard_page.find_employee_by_id('NONEXISTENT')
        assert index == -1

    def test_employee_row_has_correct_data_attributes(self, logged_in_driver, base_url, multiple_employees):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        rows = dashboard_page.get_employee_rows()
        row = rows[0]
        
        assert row.get_attribute('data-test') == 'employee-row'
        assert row.get_attribute('data-employee-id') is not None
        
        id_cell = row.find_element(By.CSS_SELECTOR, '[data-test="employee-id"]')
        name_cell = row.find_element(By.CSS_SELECTOR, '[data-test="employee-name"]')
        dept_cell = row.find_element(By.CSS_SELECTOR, '[data-test="employee-department"]')
        status_cell = row.find_element(By.CSS_SELECTOR, '[data-test="employee-status"]')
        actions_cell = row.find_element(By.CSS_SELECTOR, '[data-test="employee-actions"]')
        
        assert id_cell is not None
        assert name_cell is not None
        assert dept_cell is not None
        assert status_cell is not None
        assert actions_cell is not None

    def test_action_buttons_present(self, logged_in_driver, base_url, multiple_employees):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        rows = dashboard_page.get_employee_rows()
        row = rows[0]
        
        view_btn = row.find_element(By.CSS_SELECTOR, '[data-test="action-view"]')
        edit_btn = row.find_element(By.CSS_SELECTOR, '[data-test="action-edit"]')
        delete_btn = row.find_element(By.CSS_SELECTOR, '[data-test="action-delete"]')
        
        assert view_btn is not None
        assert edit_btn is not None
        assert delete_btn is not None

    def test_search_input_attributes(self, logged_in_driver, base_url):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        search_input = dashboard_page.driver.find_element(*dashboard_page.SEARCH_INPUT)
        assert search_input.get_attribute('id') == 'employee-search'
        assert search_input.get_attribute('name') == 'search'
        assert search_input.get_attribute('data-test') == 'employee-search'

    def test_add_employee_button_attributes(self, logged_in_driver, base_url):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        add_btn = dashboard_page.driver.find_element(*dashboard_page.ADD_EMPLOYEE_BUTTON)
        assert add_btn.get_attribute('id') == 'add-employee'
        assert add_btn.get_attribute('data-test') == 'add-employee'

    def test_nav_links_present(self, logged_in_driver, base_url):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        assert dashboard_page.is_visible(dashboard_page.NAV_DASHBOARD)
        assert dashboard_page.is_visible(dashboard_page.NAV_ADD_EMPLOYEE)
        assert dashboard_page.is_visible(dashboard_page.USER_MENU)

    def test_dashboard_accessible_via_nav(self, logged_in_driver, base_url):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        dashboard_page.click(dashboard_page.NAV_ADD_EMPLOYEE)
        
        from automation.pages.employee_page import EmployeePage
        employee_page = EmployeePage(logged_in_driver, base_url)
        assert employee_page.is_on_employee_page()
        
        employee_page.click(employee_page.CANCEL_LINK)
        assert dashboard_page.is_on_dashboard()

    def test_table_pagination_not_needed_for_small_dataset(self, logged_in_driver, base_url, multiple_employees):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        
        rows = dashboard_page.get_employee_rows()
        assert len(rows) == 5
        
        pagination = dashboard_page.driver.find_elements(By.CSS_SELECTOR, '.pagination')
        assert len(pagination) == 0