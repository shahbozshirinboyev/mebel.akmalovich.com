from django.db import models
from django.conf import settings
from django.db.models import Sum

class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    position = models.CharField(max_length=100, blank=True, null=True)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # oyiga belgilangan

    def __str__(self):
        return self.user.username


    # Oylik summani hisoblash methodi
    def get_monthly_earnings(self, year, month):
        total = self.daily_work.filter(date__year=year, date__month=month).aggregate(
            total_earned=Sum('earned_amount')
        )['total_earned'] or 0
        return total

class DailyWork(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='daily_work')
    date = models.DateField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    earned_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('employee', 'date')  # bir kunga bir marta

    def __str__(self):
        return f"{self.employee.user.username} - {self.date}"
