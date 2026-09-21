from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('employees/', views.employee_list_view, name='employees'),
    path('employees/<int:pk>/', views.employee_detail_view, name='employee_detail'),
    path('employees/add/', views.employee_add_view, name='employee_add'),
    path('reports/', views.reports_view, name='reports'),
    path('settings/', views.settings_view, name='settings'),
]