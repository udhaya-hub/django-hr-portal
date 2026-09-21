import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions


def pytest_addoption(parser):
    parser.addoption(
        '--browser',
        action='store',
        default='chrome',
        choices=['chrome', 'firefox', 'edge'],
        help='Browser to run tests in: chrome, firefox, or edge'
    )
    parser.addoption(
        '--headless',
        action='store_true',
        default=False,
        help='Run browser in headless mode'
    )
    parser.addoption(
        '--base-url',
        action='store',
        default='',
        help='Optional external base URL; otherwise use pytest-django live_server'
    )
    parser.addoption(
        '--window-size',
        action='store',
        default='1920,1080',
        help='Browser window size (width,height)'
    )


@pytest.fixture(scope='session')
def base_url(request, live_server):
    configured_url = request.config.getoption('--base-url')
    return configured_url.rstrip('/') if configured_url else live_server.url


def pytest_collection_modifyitems(items):
    database_marker = pytest.mark.django_db(transaction=True)
    for item in items:
        if 'selenium' in item.keywords:
            item.add_marker(database_marker)


@pytest.fixture(scope='session')
def browser_name(request):
    return request.config.getoption('--browser')


@pytest.fixture(scope='session')
def headless(request):
    return request.config.getoption('--headless')


@pytest.fixture(scope='session')
def window_size(request):
    size_str = request.config.getoption('--window-size')
    width, height = map(int, size_str.split(','))
    return width, height


@pytest.fixture(scope='function')
def driver(browser_name, headless, window_size):
    width, height = window_size
    
    if browser_name == 'chrome':
        options = ChromeOptions()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument(f'--window-size={width},{height}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument('--start-maximized')
        
        driver = webdriver.Chrome(options=options)
        
    elif browser_name == 'firefox':
        options = FirefoxOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument(f'--width={width}')
        options.add_argument(f'--height={height}')
        
        driver = webdriver.Firefox(options=options)
        
    elif browser_name == 'edge':
        options = EdgeOptions()
        if headless:
            options.add_argument('--headless=new')
        options.add_argument(f'--window-size={width},{height}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Edge(options=options)
    
    else:
        raise ValueError(f'Unsupported browser: {browser_name}')
    
    driver.implicitly_wait(0)
    driver.set_page_load_timeout(30)
    
    yield driver
    
    driver.quit()


@pytest.fixture(scope='function')
def wait(driver):
    from selenium.webdriver.support.ui import WebDriverWait
    return WebDriverWait(driver, 10)


@pytest.fixture(scope='function')
def test_user(db, django_user_model):
    user = django_user_model.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com',
    )
    return user


@pytest.fixture(scope='function')
def admin_user(db, django_user_model):
    return django_user_model.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
    )


@pytest.fixture(scope='function')
def test_employee(db):
    from portal.models import Employee
    return Employee.objects.create(
        employee_id='EMP001',
        first_name='John',
        last_name='Smith',
        department='Engineering',
        employment_status='Active',
    )


@pytest.fixture(scope='function')
def multiple_employees(db):
    from portal.models import Employee
    rows = [
        ('EMP001', 'John', 'Smith', 'Engineering', 'Active'),
        ('EMP002', 'Jane', 'Doe', 'Human Resources', 'Active'),
        ('EMP003', 'Bob', 'Wilson', 'Finance', 'On Leave'),
        ('EMP004', 'Alice', 'Brown', 'Marketing', 'Active'),
        ('EMP005', 'Chris', 'Taylor', 'Sales', 'Inactive'),
    ]
    return [Employee.objects.create(
        employee_id=employee_id,
        first_name=first_name,
        last_name=last_name,
        department=department,
        employment_status=status,
    ) for employee_id, first_name, last_name, department, status in rows]


@pytest.fixture(scope='function')
def logged_in_driver(driver, base_url, test_user):
    from automation.pages.login_page import LoginPage, DashboardPage
    
    login_page = LoginPage(driver, base_url)
    login_page.open()
    login_page.login(test_user.username, 'testpass123')
    
    dashboard_page = DashboardPage(driver, base_url)
    dashboard_page.wait_for_page_load()
    
    return driver


@pytest.fixture(scope='function')
def employee_data():
    return {
        'valid': {
            'employee_id': 'EMP999',
            'first_name': 'Test',
            'last_name': 'Employee',
            'department': 'Engineering',
            'employment_status': 'Active'
        },
        'missing_first_name': {
            'employee_id': 'EMP998',
            'first_name': '',
            'last_name': 'Employee',
            'department': 'Engineering',
            'employment_status': 'Active'
        },
        'missing_last_name': {
            'employee_id': 'EMP997',
            'first_name': 'Test',
            'last_name': '',
            'department': 'Engineering',
            'employment_status': 'Active'
        },
        'missing_employee_id': {
            'employee_id': '',
            'first_name': 'Test',
            'last_name': 'Employee',
            'department': 'Engineering',
            'employment_status': 'Active'
        },
        'invalid_employee_id': {
            'employee_id': 'emp@123',
            'first_name': 'Test',
            'last_name': 'Employee',
            'department': 'Engineering',
            'employment_status': 'Active'
        },
        'duplicate_employee_id': {
            'employee_id': 'EMP001',
            'first_name': 'Duplicate',
            'last_name': 'Employee',
            'department': 'Engineering',
            'employment_status': 'Active'
        },
        'short_first_name': {
            'employee_id': 'EMP996',
            'first_name': 'A',
            'last_name': 'Employee',
            'department': 'Engineering',
            'employment_status': 'Active'
        },
        'long_first_name': {
            'employee_id': 'EMP995',
            'first_name': 'A' * 51,
            'last_name': 'Employee',
            'department': 'Engineering',
            'employment_status': 'Active'
        }
    }


@pytest.fixture(scope='function')
def invalid_login_data():
    return {
        'invalid_username': {'username': 'wronguser', 'password': 'testpass123'},
        'invalid_password': {'username': 'testuser', 'password': 'wrongpass'},
        'empty_username': {'username': '', 'password': 'testpass123'},
        'empty_password': {'username': 'testuser', 'password': ''},
        'both_empty': {'username': '', 'password': ''},
    }