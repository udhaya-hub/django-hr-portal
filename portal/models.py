from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError


class EmploymentStatus(models.TextChoices):
    ACTIVE = 'Active', 'Active'
    INACTIVE = 'Inactive', 'Inactive'
    ON_LEAVE = 'On Leave', 'On Leave'


class Department(models.TextChoices):
    ENGINEERING = 'Engineering', 'Engineering'
    MARKETING = 'Marketing', 'Marketing'
    SALES = 'Sales', 'Sales'
    HR = 'Human Resources', 'Human Resources'
    FINANCE = 'Finance', 'Finance'
    OPERATIONS = 'Operations', 'Operations'
    IT = 'Information Technology', 'Information Technology'
    DESIGN = 'Design', 'Design'
    SUPPORT = 'Customer Support', 'Customer Support'
    LEGAL = 'Legal', 'Legal'


def validate_employee_id(value):
    if not value.isalnum():
        raise ValidationError('Employee ID must contain only alphanumeric characters.')
    if len(value) < 3:
        raise ValidationError('Employee ID must be at least 3 characters long.')


class Employee(models.Model):
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        validators=[validate_employee_id, MinLengthValidator(3), MaxLengthValidator(20)],
        help_text='Unique alphanumeric identifier (3-20 characters)'
    )
    first_name = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(2), MaxLengthValidator(50)],
        help_text='First name (2-50 characters)'
    )
    last_name = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(2), MaxLengthValidator(50)],
        help_text='Last name (2-50 characters)'
    )
    department = models.CharField(
        max_length=50,
        choices=Department.choices,
        help_text='Department assignment'
    )
    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE,
        help_text='Current employment status'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['employee_id']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

    def __str__(self):
        return f'{self.employee_id} - {self.first_name} {self.last_name}'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def clean(self):
        super().clean()
        if self.employee_id:
            self.employee_id = self.employee_id.strip().upper()