from django import forms
from django.core.exceptions import ValidationError
from .models import Employee, Department, EmploymentStatus


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['employee_id', 'first_name', 'last_name', 'department', 'employment_status']
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'id': 'employee-id',
                'data-test': 'employee-id',
                'class': 'form-control',
                'placeholder': 'e.g., EMP001',
                'maxlength': '20',
                'required': True,
            }),
            'first_name': forms.TextInput(attrs={
                'id': 'first-name',
                'data-test': 'first-name',
                'class': 'form-control',
                'placeholder': 'Enter first name',
                'maxlength': '50',
                'required': True,
            }),
            'last_name': forms.TextInput(attrs={
                'id': 'last-name',
                'data-test': 'last-name',
                'class': 'form-control',
                'placeholder': 'Enter last name',
                'maxlength': '50',
                'required': True,
            }),
            'department': forms.Select(attrs={
                'id': 'department',
                'data-test': 'department',
                'class': 'form-select',
                'required': True,
            }),
            'employment_status': forms.Select(attrs={
                'id': 'employment-status',
                'data-test': 'employment-status',
                'class': 'form-select',
                'required': True,
            }),
        }
        labels = {
            'employee_id': 'Employee ID',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'department': 'Department',
            'employment_status': 'Employment Status',
        }
        help_texts = {
            'employee_id': 'Unique alphanumeric identifier (3-20 characters)',
            'first_name': 'Enter first name (2-50 characters)',
            'last_name': 'Enter last name (2-50 characters)',
        }
        error_messages = {
            'employee_id': {
                'required': 'Employee ID is required.',
                'unique': 'An employee with this ID already exists.',
                'max_length': 'Employee ID cannot exceed 20 characters.',
            },
            'first_name': {
                'required': 'First name is required.',
                'max_length': 'First name cannot exceed 50 characters.',
            },
            'last_name': {
                'required': 'Last name is required.',
                'max_length': 'Last name cannot exceed 50 characters.',
            },
            'department': {
                'required': 'Department is required.',
            },
            'employment_status': {
                'required': 'Employment status is required.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].choices = [('', 'Select Department')] + list(Department.choices)
        self.fields['employment_status'].choices = [('', 'Select Status')] + list(EmploymentStatus.choices)

    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id', '').strip().upper()
        if not employee_id:
            raise ValidationError('Employee ID is required.')
        if not employee_id.isalnum():
            raise ValidationError('Employee ID must contain only alphanumeric characters.')
        if len(employee_id) < 3:
            raise ValidationError('Employee ID must be at least 3 characters long.')
        if Employee.objects.filter(employee_id=employee_id).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError('An employee with this ID already exists.')
        return employee_id

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise ValidationError('First name is required.')
        if len(first_name) < 2:
            raise ValidationError('First name must be at least 2 characters long.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        if not last_name:
            raise ValidationError('Last name is required.')
        if len(last_name) < 2:
            raise ValidationError('Last name must be at least 2 characters long.')
        return last_name

    def clean_department(self):
        department = self.cleaned_data.get('department')
        if not department:
            raise ValidationError('Department is required.')
        return department

    def clean_employment_status(self):
        status = self.cleaned_data.get('employment_status')
        if not status:
            raise ValidationError('Employment status is required.')
        return status