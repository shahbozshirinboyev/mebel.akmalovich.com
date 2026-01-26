from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    name = 'employees'
    verbose_name = '2. Employees'

    def ready(self):
        import employees.signals
