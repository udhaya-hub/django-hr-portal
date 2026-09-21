from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Department, EmploymentStatus, Employee
from .forms import EmployeeForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, 'Both username and password are required.')
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def dashboard_view(request):
    search_query = request.GET.get('search', '').strip()
    department_filter = request.GET.get('department', '').strip()
    status_filter = request.GET.get('status', '').strip()
    all_employees = Employee.objects.all()
    employees = all_employees

    if search_query:
        employees = employees.filter(
            Q(employee_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(department__icontains=search_query)
        )

    if department_filter:
        employees = employees.filter(department=department_filter)

    if status_filter:
        employees = employees.filter(employment_status=status_filter)

    context = {
        'employees': employees,
        'search_query': search_query,
        'department_filter': department_filter,
        'status_filter': status_filter,
        'total_employees': all_employees.count(),
        'active_employees': all_employees.filter(employment_status=EmploymentStatus.ACTIVE).count(),
        'inactive_employees': all_employees.filter(employment_status=EmploymentStatus.INACTIVE).count(),
        'leave_employees': all_employees.filter(employment_status=EmploymentStatus.ON_LEAVE).count(),
        'departments': Department.choices,
        'statuses': EmploymentStatus.choices,
        'user': request.user,
    }
    return render(request, 'dashboard.html', context)


@login_required
def employee_list_view(request):
    search_query = request.GET.get('search', '').strip()
    department_filter = request.GET.get('department', '').strip()
    status_filter = request.GET.get('status', '').strip()
    employees = Employee.objects.all()

    if search_query:
        employees = employees.filter(
            Q(employee_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(department__icontains=search_query)
        )

    if department_filter:
        employees = employees.filter(department=department_filter)

    if status_filter:
        employees = employees.filter(employment_status=status_filter)

    context = {
        'employees': employees,
        'search_query': search_query,
        'department_filter': department_filter,
        'status_filter': status_filter,
        'departments': Department.choices,
        'statuses': EmploymentStatus.choices,
    }
    return render(request, 'employees.html', context)


@login_required
def reports_view(request):
    employees = Employee.objects.all()
    department_report = []
    for value, label in Department.choices:
        count = employees.filter(department=value).count()
        active_count = employees.filter(
            department=value,
            employment_status=EmploymentStatus.ACTIVE,
        ).count()
        if count:
            department_report.append({
                'label': label,
                'count': count,
                'active_count': active_count,
            })

    context = {
        'total_employees': employees.count(),
        'active_employees': employees.filter(employment_status=EmploymentStatus.ACTIVE).count(),
        'inactive_employees': employees.filter(employment_status=EmploymentStatus.INACTIVE).count(),
        'leave_employees': employees.filter(employment_status=EmploymentStatus.ON_LEAVE).count(),
        'department_report': department_report,
    }
    return render(request, 'reports.html', context)


@login_required
def settings_view(request):
    return render(request, 'settings.html', {'profile_user': request.user})


@login_required
def employee_detail_view(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employee_detail.html', {'employee': employee})


@login_required
def employee_add_view(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee {employee.get_full_name()} ({employee.employee_id}) created successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployeeForm()

    context = {
        'form': form,
    }
    return render(request, 'employee_add.html', context)