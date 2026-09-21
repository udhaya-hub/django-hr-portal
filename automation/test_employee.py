import pytest
from automation.pages.login_page import EmployeePage, DashboardPage, LoginPage


@pytest.mark.selenium
class TestEmployee:
    def test_successful_employee_creation(self, logged_in_driver, base_url, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        valid_data = employee_data['valid']
        employee_page.fill_form(valid_data)
        employee_page.submit()
        
        assert dashboard_page.is_on_dashboard()
        assert dashboard_page.is_employee_present('EMP999')
        
        success_msg = dashboard_page.driver.find_element(By.CSS_SELECTOR, '[data-test="message-success"]')
        assert 'created successfully' in success_msg.text

    def test_required_field_validation_first_name(self, logged_in_driver, base_url, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        data = employee_data['missing_first_name']
        employee_page.fill_form(data)
        employee_page.submit()
        
        assert employee_page.is_on_employee_page()
        error = employee_page.get_field_error('first_name')
        assert error is not None
        assert 'required' in error.lower()

    def test_required_field_validation_last_name(self, logged_in_driver, base_url, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        data = employee_data['missing_last_name']
        employee_page.fill_form(data)
        employee_page.submit()
        
        assert employee_page.is_on_employee_page()
        error = employee_page.get_field_error('last_name')
        assert error is not None
        assert 'required' in error.lower()

    def test_required_field_validation_employee_id(self, logged_in_driver, base_url, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        data = employee_data['missing_employee_id']
        employee_page.fill_form(data)
        employee_page.submit()
        
        assert employee_page.is_on_employee_page()
        error = employee_page.get_field_error('employee_id')
        assert error is not None
        assert 'required' in error.lower()

    def test_required_field_validation_department(self, logged_in_driver, base_url, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        data = employee_data['valid'].copy()
        data['department'] = ''
        employee_page.fill_form(data)
        employee_page.submit()
        
        assert employee_page.is_on_employee_page()
        error = employee_page.get_field_error('department')
        assert error is not None
        assert 'required' in error.lower()

    def test_required_field_validation_status(self, logged_in_driver, base_url, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        data = employee_data['valid'].copy()
        data['employment_status'] = ''
        employee_page.fill_form(data)
        employee_page.submit()
        
        assert employee_page.is_on_employee_page()
        error = employee_page.get_field_error('employment_status')
        assert error is not None
        assert 'required' in error.lower()

    def test_invalid_employee_id_format(self, logged_in_driver, base_url, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        data = employee_data['invalid_employee_id']
        employee_page.fill_form(data)
        employee_page.submit()
        
        assert employee_page.is_on_employee_page()
        error = employee_page.get_field_error('employee_id')
        assert error is not None
        assert 'uppercase' in error.lower() or 'alphanumeric' in error.lower()

    def test_duplicate_employee_id(self, logged_in_driver, base_url, employee_data, test_employee):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        data = employee_data['duplicate_employee_id']
        employee_page.fill_form(data)
        employee_page.submit()
        
        assert employee_page.is_on_employee_page()
        error = employee_page.get_field_error('employee_id')
        assert error is not None
        assert 'already exists' in error.lower()

    def test_short_first_name_validation(self, logged_in_driver, base_url, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        data = employee_data['short_first_name']
        employee_page.fill_form(data)
        employee_page.submit()
        
        assert employee_page.is_on_employee_page()
        error = employee_page.get_field_error('first_name')
        assert error is not None
        assert 'at least 2' in error.lower()

    def test_long_first_name_validation(self, logged_in_driver, base_url, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        data = employee_data['long_first_name']
        employee_page.fill_form(data)
        employee_page.submit()
        
        assert employee_page.is_on_employee_page()
        error = employee_page.get_field_error('first_name')
        assert error is not None
        assert 'exceed' in error.lower() or '50' in error

    def test_cancel_button_returns_to_dashboard(self, logged_in_driver, base_url, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        valid_data = employee_data['valid']
        employee_page.fill_form(valid_data)
        employee_page.cancel()
        
        assert dashboard_page.is_on_dashboard()
        assert not dashboard_page.is_employee_present('EMP999')

    def test_cancel_link_returns_to_dashboard(self, logged_in_driver, base_url, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        employee_page.cancel_via_link()
        
        assert dashboard_page.is_on_dashboard()

    def test_newly_created_employee_appears_in_dashboard(self, logged_in_driver, base_url, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        initial_count = len(dashboard_page.get_employee_rows())
        
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        valid_data = employee_data['valid']
        employee_page.fill_form(valid_data)
        employee_page.submit()
        
        assert dashboard_page.is_on_dashboard()
        new_count = len(dashboard_page.get_employee_rows())
        assert new_count == initial_count + 1
        assert dashboard_page.is_employee_present('EMP999')
        
        index = dashboard_page.find_employee_by_id('EMP999')
        emp_data = dashboard_page.get_employee_data(index)
        assert emp_data['name'] == 'Test Employee'
        assert emp_data['department'] == 'Engineering'
        assert 'Active' in emp_data['status']

    def test_form_fields_have_correct_attributes(self, logged_in_driver, base_url):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        
        first_name = employee_page.driver.find_element(*employee_page.FIRST_NAME)
        last_name = employee_page.driver.find_element(*employee_page.LAST_NAME)
        emp_id = employee_page.driver.find_element(*employee_page.EMPLOYEE_ID)
        department = employee_page.driver.find_element(*employee_page.DEPARTMENT)
        status = employee_page.driver.find_element(*employee_page.EMPLOYMENT_STATUS)
        save_btn = employee_page.driver.find_element(*employee_page.SAVE_BUTTON)
        cancel_btn = employee_page.driver.find_element(*employee_page.CANCEL_BUTTON)
        
        assert first_name.get_attribute('id') == 'first-name'
        assert first_name.get_attribute('data-test') == 'first-name'
        assert last_name.get_attribute('id') == 'last-name'
        assert last_name.get_attribute('data-test') == 'last-name'
        assert emp_id.get_attribute('id') == 'employee-id'
        assert emp_id.get_attribute('data-test') == 'employee-id'
        assert department.get_attribute('id') == 'department'
        assert department.get_attribute('data-test') == 'department'
        assert status.get_attribute('id') == 'employment-status'
        assert status.get_attribute('data-test') == 'employment-status'
        assert save_btn.get_attribute('id') == 'save-employee'
        assert save_btn.get_attribute('data-test') == 'save-employee'
        assert cancel_btn.get_attribute('id') == 'cancel-btn'
        assert cancel_btn.get_attribute('data-test') == 'cancel-btn'

    def test_form_select_options(self, logged_in_driver, base_url):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        
        from selenium.webdriver.support.ui import Select
        dept_select = Select(employee_page.driver.find_element(*employee_page.DEPARTMENT))
        status_select = Select(employee_page.driver.find_element(*employee_page.EMPLOYMENT_STATUS))
        
        dept_options = [opt.text for opt in dept_select.options]
        status_options = [opt.text for opt in status_select.options]
        
        assert 'Engineering' in dept_options
        assert 'Marketing' in dept_options
        assert 'Sales' in dept_options
        assert 'Human Resources' in dept_options
        assert 'Finance' in dept_options
        assert 'Active' in status_options
        assert 'Inactive' in status_options
        assert 'On Leave' in status_options

    def test_employee_id_uppercase_conversion(self, logged_in_driver, base_url, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        data = employee_data['valid'].copy()
        data['employee_id'] = 'emp999'
        employee_page.fill_form(data)
        
        emp_id_value = employee_page.get_field_value('employee_id')
        assert emp_id_value == 'EMP999'

    def test_form_validation_shows_multiple_errors(self, logged_in_driver, base_url):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        employee_page.submit()
        
        assert employee_page.is_on_employee_page()
        
        first_name_error = employee_page.get_field_error('first_name')
        last_name_error = employee_page.get_field_error('last_name')
        emp_id_error = employee_page.get_field_error('employee_id')
        dept_error = employee_page.get_field_error('department')
        status_error = employee_page.get_field_error('employment_status')
        
        assert first_name_error is not None
        assert last_name_error is not None
        assert emp_id_error is not None
        assert dept_error is not None
        assert status_error is not None

    def test_server_side_duplicate_validation(self, logged_in_driver, base_url, test_employee, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        data = employee_data['valid'].copy()
        data['employee_id'] = 'EMP001'
        employee_page.fill_form(data)
        employee_page.submit()
        
        assert employee_page.is_on_employee_page()
        error = employee_page.get_field_error('employee_id') or employee_page.get_server_error('employee_id')
        assert error is not None
        assert 'already exists' in error.lower()

    def test_all_departments_can_be_selected(self, logged_in_driver, base_url, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        
        departments = ['Engineering', 'Marketing', 'Sales', 'Human Resources', 'Finance', 
                      'Operations', 'Information Technology', 'Design', 'Customer Support', 'Legal']
        
        for dept in departments:
            data = employee_data['valid'].copy()
            data['employee_id'] = f'EMP{dept[:3].upper()}'
            data['department'] = dept
            employee_page.fill_form(data)
            employee_page.submit()
            
            assert dashboard_page.is_on_dashboard()
            assert dashboard_page.is_employee_present(data['employee_id'])
            
            dashboard_page.click_add_employee()
            employee_page = EmployeePage(logged_in_driver, base_url)

    def test_all_statuses_can_be_selected(self, logged_in_driver, base_url, employee_data):
        dashboard_page = DashboardPage(logged_in_driver, base_url)
        dashboard_page.click_add_employee()
        
        employee_page = EmployeePage(logged_in_driver, base_url)
        
        statuses = ['Active', 'Inactive', 'On Leave']
        
        for status in statuses:
            data = employee_data['valid'].copy()
            data['employee_id'] = f'EMP{status[:3].upper()}'
            data['employment_status'] = status
            employee_page.fill_form(data)
            employee_page.submit()
            
            assert dashboard_page.is_on_dashboard()
            assert dashboard_page.is_employee_present(data['employee_id'])
            
            index = dashboard_page.find_employee_by_id(data['employee_id'])
            emp_data = dashboard_page.get_employee_data(index)
            assert status in emp_data['status']
            
            dashboard_page.click_add_employee()
            employee_page = EmployeePage(logged_in_driver, base_url)