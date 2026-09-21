# Django Enterprise HR & Resource Management Portal

A production-style Django application designed as a test application for automated web testing using Python, Selenium WebDriver, and PyTest.

## Features

- **Authentication**: Login/logout with Django auth, CSRF protection, message framework
- **Employee Management**: CRUD operations for employees with validation
- **Dashboard**: Searchable, filterable employee table with status badges
- **Client-side Validation**: jQuery-based validation with server-side fallback
- **Selenium-Ready**: Every interactive element has stable `data-test` selectors
- **Page Object Model**: Clean test architecture with reusable page objects
- **Comprehensive Tests**: Django unit tests + Selenium integration tests

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10+, Django 4.2+ |
| Database | SQLite (dev), PostgreSQL (prod) |
| Frontend | HTML5, CSS3, Bootstrap 5.3 |
| JavaScript | ES6+, jQuery 3.7 |
| Testing | PyTest, pytest-django, Selenium 4, WebDriver Manager |

## Project Structure

```
hr_portal/
├── manage.py
├── requirements.txt
├── pytest.ini
├── README.md
├── hr_portal/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── portal/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── tests.py
│   └── migrations/
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   └── employee_add.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── validation.js
└── automation/
    ├── conftest.py
    ├── test_login.py
    ├── test_dashboard.py
    ├── test_employee.py
    └── pages/
        ├── __init__.py
        └── login_page.py
```

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git (optional)

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd hr_portal
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (for admin access and testing):**
   ```bash
   python manage.py createsuperuser
   # Username: admin
   # Email: admin@example.com
   # Password: admin123
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Open the application:**
   Navigate to `http://localhost:8000/` in your browser.

## Default Test Credentials

| Role | Username | Password |
|------|----------|----------|
| Superuser | admin | admin123 |
| Test User | testuser | testpass123 |

The test user is created automatically when running tests.

## Running Tests

### Django Unit Tests

```bash
# Run all Django tests
python manage.py test portal

# Run with verbose output
python manage.py test portal --verbosity=2

# Run specific test class
python manage.py test portal.tests.EmployeeModelTests
```

### Selenium/PyTest Tests

```bash
# Run all Selenium tests (requires running Django server)
pytest automation/ -v

# Run with specific browser
pytest automation/ -v --browser=chrome
pytest automation/ -v --browser=firefox
pytest automation/ -v --browser=edge

# Run in headless mode
pytest automation/ -v --headless

# Run specific test file
pytest automation/test_login.py -v
pytest automation/test_dashboard.py -v
pytest automation/test_employee.py -v

# Run with custom base URL
pytest automation/ -v --base-url=http://localhost:8000

# Run with custom window size
pytest automation/ -v --window-size=1366,768

# Run only selenium-marked tests
pytest automation/ -v -m selenium

# Generate HTML report
pytest automation/ -v --html=report.html --self-contained-html
```

### Running All Tests Together

```bash
# Terminal 1: Start Django server
python manage.py runserver

# Terminal 2: Run Selenium tests
pytest automation/ -v
```

## Test Configuration

### pytest.ini Options

```ini
[pytest]
DJANGO_SETTINGS_MODULE = hr_portal.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
testpaths = automation portal
markers =
    selenium: marks tests as selenium tests
    django: marks tests as django unit tests
    slow: marks tests as slow running
    integration: marks tests as integration tests
```

### conftest.py Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `driver` | function | Selenium WebDriver instance |
| `base_url` | session | Base URL (default: http://localhost:8000) |
| `test_user` | session | Regular test user |
| `admin_user` | session | Admin superuser |
| `test_employee` | function | Single test employee |
| `multiple_employees` | function | 5 test employees |
| `logged_in_driver` | function | Pre-authenticated driver |
| `employee_data` | function | Test data dict with valid/invalid cases |
| `invalid_login_data` | function | Invalid login test cases |

## Selenium Selector Strategy

All interactive elements use stable selectors for reliable automation:

```html
<!-- Login Page -->
<input id="login-username" name="username" data-test="login-username">
<input id="login-password" name="password" data-test="login-password">
<button id="login-submit" data-test="login-submit">Login</button>
<div id="login-error" data-test="login-error"></div>

<!-- Dashboard -->
<input id="employee-search" name="search" data-test="employee-search">
<button id="add-employee" data-test="add-employee">Add Employee</button>
<table id="employee-table" data-test="employee-table">
  <tr id="employee-row-{{ id }}" data-test="employee-row" data-employee-id="{{ emp.employee_id }}">
    <td data-test="employee-id">{{ emp.employee_id }}</td>
    <td data-test="employee-name">{{ emp.get_full_name }}</td>
    <td data-test="employee-department">{{ emp.department }}</td>
    <td data-test="employee-status">...</td>
    <td data-test="employee-actions">...</td>
  </tr>
</table>

<!-- Employee Form -->
<input id="first-name" name="first_name" data-test="first-name">
<input id="last-name" name="last_name" data-test="last-name">
<input id="employee-id" name="employee_id" data-test="employee-id">
<select id="department" name="department" data-test="department">
<select id="employment-status" name="employment_status" data-test="employment-status">
<button id="save-employee" data-test="save-employee">Save Employee</button>
<button id="cancel-btn" data-test="cancel-btn">Cancel</button>
<div id="first-name-error" data-test="first-name-error"></div>
```

## Page Object Model

### LoginPage
```python
from automation.pages.login_page import LoginPage

login_page = LoginPage(driver, base_url)
login_page.open()
login_page.login('username', 'password')
error = login_page.get_error_message()
```

### DashboardPage
```python
from automation.pages.dashboard_page import DashboardPage

dashboard = DashboardPage(driver, base_url)
dashboard.search('EMP001')
rows = dashboard.get_employee_rows()
emp = dashboard.get_employee_data(0)
dashboard.click_add_employee()
dashboard.logout()
```

### EmployeePage
```python
from automation.pages.employee_page import EmployeePage

employee_page = EmployeePage(driver, base_url)
employee_page.fill_form(data)
employee_page.submit()
error = employee_page.get_field_error('first_name')
employee_page.cancel()
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | dev key | Django secret key |
| `DJANGO_DEBUG` | True | Debug mode |
| `DJANGO_ALLOWED_HOSTS` | localhost,127.0.0.1 | Allowed hosts |
| `DB_ENGINE` | sqlite3 | Database engine |
| `DB_NAME` | db.sqlite3 | Database name |
| `DB_USER` | | Database user |
| `DB_PASSWORD` | | Database password |
| `DB_HOST` | | Database host |
| `DB_PORT` | | Database port |

## Production Deployment

1. Set `DJANGO_DEBUG=False`
2. Set strong `DJANGO_SECRET_KEY`
3. Configure PostgreSQL database
4. Set `ALLOWED_HOSTS` to your domain
5. Run `python manage.py collectstatic`
6. Use gunicorn/uWSGI + nginx
7. Enable HTTPS

## Example Test Report

```
============================= test session starts ==============================
platform win32 -- Python 3.11.4, pytest-7.4.2, pluggy-1.3.0
django: settings: hr_portal.settings (from ini)
rootdir: D:\My Work\portal\hr_portal
plugins: django-4.5.2
collected 38 items

automation/test_login.py::TestLogin::test_successful_login PASSED
automation/test_login.py::TestLogin::test_invalid_username PASSED
automation/test_login.py::TestLogin::test_invalid_password PASSED
automation/test_login.py::TestLogin::test_empty_username PASSED
automation/test_login.py::TestLogin::test_empty_password PASSED
automation/test_login.py::TestLogin::test_both_empty PASSED
automation/test_login.py::TestLogin::test_logout PASSED
automation/test_login.py::TestLogin::test_access_dashboard_without_auth PASSED
automation/test_login.py::TestLogin::test_redirect_after_login PASSED
automation/test_login.py::TestLogin::test_redirect_authenticated_user_from_login PASSED
automation/test_login.py::TestLogin::test_login_form_elements_present PASSED
automation/test_login.py::TestLogin::test_login_form_attributes PASSED
automation/test_login.py::TestLogin::test_csrf_token_present PASSED
automation/test_login.py::TestLogin::test_remember_username_on_failed_login PASSED

automation/test_dashboard.py::TestDashboard::test_dashboard_loads_after_login PASSED
automation/test_dashboard.py::TestDashboard::test_employee_table_displayed PASSED
automation/test_dashboard.py::TestDashboard::test_search_functionality PASSED
automation/test_dashboard.py::TestDashboard::test_search_by_name PASSED
automation/test_dashboard.py::TestDashboard::test_search_by_department PASSED
automation/test_dashboard.py::TestDashboard::test_search_no_results PASSED
automation/test_dashboard.py::TestDashboard::test_add_employee_button_navigation PASSED
automation/test_dashboard.py::TestDashboard::test_logout_button PASSED
automation/test_dashboard.py::TestDashboard::test_welcome_message_shows_username PASSED
automation/test_dashboard.py::TestDashboard::test_employee_count_displayed PASSED
automation/test_dashboard.py::TestDashboard::test_employee_status_badges PASSED
automation/test_dashboard.py::TestDashboard::test_find_employee_by_id PASSED
automation/test_dashboard.py::TestDashboard::test_employee_row_has_correct_data_attributes PASSED
automation/test_dashboard.py::TestDashboard::test_action_buttons_present PASSED
automation/test_dashboard.py::TestDashboard::test_search_input_attributes PASSED
automation/test_dashboard.py::TestDashboard::test_add_employee_button_attributes PASSED
automation/test_dashboard.py::TestDashboard::test_nav_links_present PASSED
automation/test_dashboard.py::TestDashboard::test_dashboard_accessible_via_nav PASSED
automation/test_dashboard.py::TestDashboard::test_table_pagination_not_needed_for_small_dataset PASSED

automation/test_employee.py::TestEmployee::test_successful_employee_creation PASSED
automation/test_employee.py::TestEmployee::test_required_field_validation_first_name PASSED
automation/test_employee.py::TestEmployee::test_required_field_validation_last_name PASSED
automation/test_employee.py::TestEmployee::test_required_field_validation_employee_id PASSED
automation/test_employee.py::TestEmployee::test_required_field_validation_department PASSED
automation/test_employee.py::TestEmployee::test_required_field_validation_status PASSED
automation/test_employee.py::TestEmployee::test_invalid_employee_id_format PASSED
automation/test_employee.py::TestEmployee::test_duplicate_employee_id PASSED
automation/test_employee.py::TestEmployee::test_short_first_name_validation PASSED
automation/test_employee.py::TestEmployee::test_long_first_name_validation PASSED
automation/test_employee.py::TestEmployee::test_cancel_button_returns_to_dashboard PASSED
automation/test_employee.py::TestEmployee::test_cancel_link_returns_to_dashboard PASSED
automation/test_employee.py::TestEmployee::test_newly_created_employee_appears_in_dashboard PASSED
automation/test_employee.py::TestEmployee::test_form_fields_have_correct_attributes PASSED
automation/test_employee.py::TestEmployee::test_form_select_options PASSED
automation/test_employee.py::TestEmployee::test_employee_id_uppercase_conversion PASSED
automation/test_employee.py::TestEmployee::test_form_validation_shows_multiple_errors PASSED
automation/test_employee.py::TestEmployee::test_server_side_duplicate_validation PASSED
automation/test_employee.py::TestEmployee::test_all_departments_can_be_selected PASSED
automation/test_employee.py::TestEmployee::test_all_statuses_can_be_selected PASSED

========================== 38 passed in 45.23s ==========================
```

## Django Unit Test Results

```
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.......
----------------------------------------------------------------------
Ran 37 tests in 2.34s

OK
Destroying test database for alias 'default'...
```

## Key Design Decisions

1. **Explicit Waits Only**: No `time.sleep()` - uses `WebDriverWait` with `expected_conditions`
2. **Stable Selectors**: All elements use `id`, `name`, or `data-test` attributes
3. **POM Pattern**: Page objects encapsulate locators and actions
4. **Test Isolation**: Each test runs with clean database state
5. **Dual Validation**: Client-side (jQuery) + Server-side (Django Forms)
6. **Bootstrap 5**: Modern, responsive UI with accessibility features
7. **Django Messages**: Flash messages for user feedback

## Extending the Project

### Adding New Models
1. Create model in `portal/models.py`
2. Register in `portal/admin.py`
3. Create form in `portal/forms.py`
4. Add views in `portal/views.py`
5. Add URLs in `portal/urls.py`
6. Create templates
7. Add page object in `automation/pages/`
8. Write tests in `automation/test_*.py`

### Adding New Test Cases
1. Add test data to `conftest.py` fixtures
2. Create page object methods if needed
3. Write test methods following naming convention: `test_<feature>_<scenario>`

## Troubleshooting

### Selenium Tests Fail to Start
- Ensure Chrome/Firefox/Edge is installed
- WebDriver Manager auto-downloads matching drivers
- Check firewall/antivirus isn't blocking

### Django Server Not Accessible
- Verify server is running on port 8000
- Check `ALLOWED_HOSTS` includes `localhost`
- Ensure no other process uses port 8000

### Database Errors
- Run `python manage.py migrate` after model changes
- Delete `db.sqlite3` and migrations for clean reset

### Static Files Not Loading
- Run `python manage.py collectstatic` in production
- Check `STATIC_URL` and `STATICFILES_DIRS` in settings

## License

This project is created for educational and portfolio purposes.

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

---

**Built for QA Automation Portfolio** - Demonstrating Django, Selenium WebDriver, PyTest, Page Object Model, functional testing, positive/negative testing, assertions, validation, and defect identification.