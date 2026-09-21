from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from portal.models import Employee
from portal.forms import EmployeeForm


class EmployeeModelTests(TestCase):
    def setUp(self):
        self.valid_employee_data = {
            'employee_id': 'EMP001',
            'first_name': 'John',
            'last_name': 'Doe',
            'department': 'Engineering',
            'employment_status': 'Active'
        }

    def test_create_employee(self):
        employee = Employee.objects.create(**self.valid_employee_data)
        self.assertEqual(employee.employee_id, 'EMP001')
        self.assertEqual(employee.first_name, 'John')
        self.assertEqual(employee.last_name, 'Doe')
        self.assertEqual(employee.department, 'Engineering')
        self.assertEqual(employee.employment_status, 'Active')
        self.assertIsNotNone(employee.created_at)
        self.assertIsNotNone(employee.updated_at)

    def test_employee_str_representation(self):
        employee = Employee.objects.create(**self.valid_employee_data)
        self.assertEqual(str(employee), 'EMP001 - John Doe')

    def test_get_full_name(self):
        employee = Employee.objects.create(**self.valid_employee_data)
        self.assertEqual(employee.get_full_name(), 'John Doe')

    def test_employee_id_unique_constraint(self):
        Employee.objects.create(**self.valid_employee_data)
        with self.assertRaises(Exception):
            Employee.objects.create(**self.valid_employee_data)

    def test_employee_id_validation_alphanumeric(self):
        data = self.valid_employee_data.copy()
        data['employee_id'] = 'EMP@001'
        employee = Employee(**data)
        with self.assertRaises(ValidationError):
            employee.full_clean()

    def test_employee_id_validation_min_length(self):
        data = self.valid_employee_data.copy()
        data['employee_id'] = 'EM'
        employee = Employee(**data)
        with self.assertRaises(ValidationError):
            employee.full_clean()

    def test_first_name_validation_min_length(self):
        data = self.valid_employee_data.copy()
        data['first_name'] = 'J'
        employee = Employee(**data)
        with self.assertRaises(ValidationError):
            employee.full_clean()

    def test_last_name_validation_min_length(self):
        data = self.valid_employee_data.copy()
        data['last_name'] = 'D'
        employee = Employee(**data)
        with self.assertRaises(ValidationError):
            employee.full_clean()

    def test_employment_status_choices(self):
        for status in ['Active', 'Inactive', 'On Leave']:
            data = self.valid_employee_data.copy()
            data['employee_id'] = f'EMP_{status}'
            data['employment_status'] = status
            employee = Employee.objects.create(**data)
            self.assertEqual(employee.employment_status, status)

    def test_default_employment_status(self):
        data = self.valid_employee_data.copy()
        del data['employment_status']
        employee = Employee.objects.create(**data)
        self.assertEqual(employee.employment_status, 'Active')

    def test_employee_ordering(self):
        Employee.objects.create(employee_id='EMP003', first_name='Alice', last_name='Smith', department='HR', employment_status='Active')
        Employee.objects.create(employee_id='EMP001', first_name='John', last_name='Doe', department='Engineering', employment_status='Active')
        Employee.objects.create(employee_id='EMP002', first_name='Jane', last_name='Smith', department='Marketing', employment_status='Active')
        
        employees = list(Employee.objects.all())
        self.assertEqual(employees[0].employee_id, 'EMP001')
        self.assertEqual(employees[1].employee_id, 'EMP002')
        self.assertEqual(employees[2].employee_id, 'EMP003')

    def test_updated_at_changes_on_save(self):
        employee = Employee.objects.create(**self.valid_employee_data)
        original_updated = employee.updated_at
        employee.first_name = 'Jane'
        employee.save()
        self.assertGreater(employee.updated_at, original_updated)


class EmployeeFormTests(TestCase):
    def setUp(self):
        self.valid_form_data = {
            'employee_id': 'EMP001',
            'first_name': 'John',
            'last_name': 'Doe',
            'department': 'Engineering',
            'employment_status': 'Active'
        }

    def test_valid_form(self):
        form = EmployeeForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

    def test_form_save_creates_employee(self):
        form = EmployeeForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())
        employee = form.save()
        self.assertEqual(employee.employee_id, 'EMP001')
        self.assertEqual(employee.first_name, 'John')

    def test_missing_first_name(self):
        data = self.valid_form_data.copy()
        data['first_name'] = ''
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_missing_last_name(self):
        data = self.valid_form_data.copy()
        data['last_name'] = ''
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)

    def test_missing_employee_id(self):
        data = self.valid_form_data.copy()
        data['employee_id'] = ''
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('employee_id', form.errors)

    def test_missing_department(self):
        data = self.valid_form_data.copy()
        data['department'] = ''
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('department', form.errors)

    def test_missing_employment_status(self):
        data = self.valid_form_data.copy()
        data['employment_status'] = ''
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('employment_status', form.errors)

    def test_duplicate_employee_id(self):
        Employee.objects.create(**self.valid_form_data)
        form = EmployeeForm(data=self.valid_form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('employee_id', form.errors)
        self.assertIn('already exists', str(form.errors['employee_id']).lower())

    def test_invalid_employee_id_format(self):
        data = self.valid_form_data.copy()
        data['employee_id'] = 'emp@123'
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('employee_id', form.errors)

    def test_short_first_name(self):
        data = self.valid_form_data.copy()
        data['first_name'] = 'A'
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_long_first_name(self):
        data = self.valid_form_data.copy()
        data['first_name'] = 'A' * 51
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_short_last_name(self):
        data = self.valid_form_data.copy()
        data['last_name'] = 'B'
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)

    def test_employee_id_uppercase_conversion(self):
        data = self.valid_form_data.copy()
        data['employee_id'] = 'emp001'
        form = EmployeeForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['employee_id'], 'EMP001')

    def test_form_field_widgets_have_correct_attributes(self):
        form = EmployeeForm()
        self.assertEqual(form.fields['employee_id'].widget.attrs['id'], 'employee-id')
        self.assertEqual(form.fields['employee_id'].widget.attrs['data-test'], 'employee-id')
        self.assertEqual(form.fields['first_name'].widget.attrs['id'], 'first-name')
        self.assertEqual(form.fields['first_name'].widget.attrs['data-test'], 'first-name')
        self.assertEqual(form.fields['last_name'].widget.attrs['id'], 'last-name')
        self.assertEqual(form.fields['last_name'].widget.attrs['data-test'], 'last-name')
        self.assertEqual(form.fields['department'].widget.attrs['id'], 'department')
        self.assertEqual(form.fields['department'].widget.attrs['data-test'], 'department')
        self.assertEqual(form.fields['employment_status'].widget.attrs['id'], 'employment-status')
        self.assertEqual(form.fields['employment_status'].widget.attrs['data-test'], 'employment-status')


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.login_url = reverse('login')
        self.dashboard_url = reverse('dashboard')

    def test_login_page_accessible(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_successful_login(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, self.dashboard_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_username(self):
        response = self.client.post(self.login_url, {
            'username': 'wronguser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('Invalid username or password' in str(m) for m in messages))

    def test_invalid_password(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('Invalid username or password' in str(m) for m in messages))

    def test_empty_username(self):
        response = self.client.post(self.login_url, {
            'username': '',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_empty_password(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, self.login_url)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_dashboard_requires_login(self):
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.dashboard_url}')

    def test_dashboard_accessible_after_login(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_employee_add_requires_login(self):
        response = self.client.get(reverse('employee_add'))
        self.assertRedirects(response, f'{self.login_url}?next={reverse("employee_add")}')

    def test_employee_add_accessible_after_login(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('employee_add'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee_add.html')

    def test_redirect_authenticated_user_from_login(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.dashboard_url)


class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.dashboard_url = reverse('dashboard')
        
        Employee.objects.create(employee_id='EMP001', first_name='John', last_name='Doe', department='Engineering', employment_status='Active')
        Employee.objects.create(employee_id='EMP002', first_name='Jane', last_name='Smith', department='Marketing', employment_status='Inactive')
        Employee.objects.create(employee_id='EMP003', first_name='Bob', last_name='Wilson', department='Sales', employment_status='On Leave')

    def test_dashboard_displays_employees(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EMP001')
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Engineering')
        self.assertContains(response, 'Active')
        self.assertContains(response, 'EMP002')
        self.assertContains(response, 'EMP003')

    def test_dashboard_search_by_employee_id(self):
        response = self.client.get(self.dashboard_url, {'search': 'EMP001'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EMP001')
        self.assertNotContains(response, 'EMP002')
        self.assertNotContains(response, 'EMP003')

    def test_dashboard_search_by_name(self):
        response = self.client.get(self.dashboard_url, {'search': 'Jane'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EMP002')
        self.assertNotContains(response, 'EMP001')
        self.assertNotContains(response, 'EMP003')

    def test_dashboard_search_by_department(self):
        response = self.client.get(self.dashboard_url, {'search': 'Engineering'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EMP001')
        self.assertNotContains(response, 'EMP002')
        self.assertNotContains(response, 'EMP003')

    def test_dashboard_search_no_results(self):
        response = self.client.get(self.dashboard_url, {'search': 'NonExistent'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'EMP001')
        self.assertNotContains(response, 'EMP002')
        self.assertNotContains(response, 'EMP003')
        self.assertContains(response, 'No employees found')

    def test_dashboard_context_has_user(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.context['user'].username, 'testuser')

    def test_dashboard_empty_state_when_no_employees(self):
        Employee.objects.all().delete()
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Employees Found')


class EmployeeAddViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.add_url = reverse('employee_add')

    def test_get_employee_add_page(self):
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employee_add.html')
        self.assertIsInstance(response.context['form'], EmployeeForm)

    def test_post_valid_employee(self):
        response = self.client.post(self.add_url, {
            'employee_id': 'EMP001',
            'first_name': 'John',
            'last_name': 'Doe',
            'department': 'Engineering',
            'employment_status': 'Active'
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(Employee.objects.filter(employee_id='EMP001').exists())
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any('created successfully' in str(m) for m in messages))

    def test_post_duplicate_employee_id(self):
        Employee.objects.create(employee_id='EMP001', first_name='John', last_name='Doe', department='Engineering', employment_status='Active')
        response = self.client.post(self.add_url, {
            'employee_id': 'EMP001',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'department': 'Marketing',
            'employment_status': 'Active'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'employee_id', 'An employee with this ID already exists.')

    def test_post_invalid_employee_id(self):
        response = self.client.post(self.add_url, {
            'employee_id': 'emp@123',
            'first_name': 'John',
            'last_name': 'Doe',
            'department': 'Engineering',
            'employment_status': 'Active'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'employee_id')

    def test_post_missing_required_fields(self):
        response = self.client.post(self.add_url, {})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'employee_id', 'Employee ID is required.')
        self.assertFormError(response, 'form', 'first_name', 'First name is required.')
        self.assertFormError(response, 'form', 'last_name', 'Last name is required.')
        self.assertFormError(response, 'form', 'department', 'Department is required.')
        self.assertFormError(response, 'form', 'employment_status', 'Employment status is required.')

    def test_cancel_redirects_to_dashboard(self):
        response = self.client.post(self.add_url, {
            'employee_id': 'EMP001',
            'first_name': 'John',
            'last_name': 'Doe',
            'department': 'Engineering',
            'employment_status': 'Active',
            'cancel': 'Cancel'
        })
        self.assertRedirects(response, reverse('dashboard'))


class URLTests(TestCase):
    def test_login_url_resolves(self):
        from django.urls import resolve
        from portal.views import login_view
        resolver = resolve('/login/')
        self.assertEqual(resolver.func, login_view)
        self.assertEqual(resolver.url_name, 'login')

    def test_logout_url_resolves(self):
        from django.urls import resolve
        from portal.views import logout_view
        resolver = resolve('/logout/')
        self.assertEqual(resolver.func, logout_view)
        self.assertEqual(resolver.url_name, 'logout')

    def test_dashboard_url_resolves(self):
        from django.urls import resolve
        from portal.views import dashboard_view
        resolver = resolve('/dashboard/')
        self.assertEqual(resolver.func, dashboard_view)
        self.assertEqual(resolver.url_name, 'dashboard')

    def test_employee_add_url_resolves(self):
        from django.urls import resolve
        from portal.views import employee_add_view
        resolver = resolve('/employees/add/')
        self.assertEqual(resolver.func, employee_add_view)
        self.assertEqual(resolver.url_name, 'employee_add')

    def test_named_urls_reverse(self):
        self.assertEqual(reverse('login'), '/login/')
        self.assertEqual(reverse('logout'), '/logout/')
        self.assertEqual(reverse('dashboard'), '/dashboard/')
        self.assertEqual(reverse('employee_add'), '/employees/add/')


class AdminTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        self.client = Client()
        self.client.login(username='admin', password='admin123')

    def test_employee_admin_registered(self):
        from django.contrib import admin
        from portal.models import Employee
        self.assertTrue(admin.site.is_registered(Employee))

    def test_employee_admin_list_display(self):
        from portal.admin import EmployeeAdmin
        self.assertIn('employee_id', EmployeeAdmin.list_display)
        self.assertIn('first_name', EmployeeAdmin.list_display)
        self.assertIn('last_name', EmployeeAdmin.list_display)
        self.assertIn('department', EmployeeAdmin.list_display)
        self.assertIn('employment_status', EmployeeAdmin.list_display)
        self.assertIn('created_at', EmployeeAdmin.list_display)

    def test_employee_admin_list_filter(self):
        from portal.admin import EmployeeAdmin
        self.assertIn('department', EmployeeAdmin.list_filter)
        self.assertIn('employment_status', EmployeeAdmin.list_filter)
        self.assertIn('created_at', EmployeeAdmin.list_filter)

    def test_employee_admin_search_fields(self):
        from portal.admin import EmployeeAdmin
        self.assertIn('employee_id', EmployeeAdmin.search_fields)
        self.assertIn('first_name', EmployeeAdmin.search_fields)
        self.assertIn('last_name', EmployeeAdmin.search_fields)
        self.assertIn('department', EmployeeAdmin.search_fields)