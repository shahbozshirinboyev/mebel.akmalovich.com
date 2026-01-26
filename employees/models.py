from django.db import models
from django.db.models import Sum, F
from accounts.models import User


class Employee(models.Model):
    """Сотрудники model"""
    SALARY_TYPES = [
        ('fixed', 'Фиксированная'),
        ('hourly', 'Почасовая'),
        ('piecework', 'Сдельная'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name='Сотрудник'
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name='Полное имя',
        blank=True
    )
    position = models.CharField(
        max_length=100,
        verbose_name='Позиция'
    )
    salary_type = models.CharField(
        max_length=50,
        choices=SALARY_TYPES,
        default='fixed',
        verbose_name='Вид зарплаты'
    )
    base_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Базовая зарплата'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )

    def save(self, *args, **kwargs):
        """
        Agar full_name bo‘sh bo‘lsa,
        User'dan avtomatik to‘ldiriladi
        """
        if not self.full_name and self.user:
            full_name = self.user.get_full_name()
            self.full_name = full_name if full_name else self.user.username

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '1. Сотрудник'
        verbose_name_plural = '1. Сотрудники'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_employee_user')
        ]

    def __str__(self):
        return f"{self.full_name} - {self.position}"


class Balance(models.Model):
    """Xodimlar balansi modeli (Баланс)"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='balances',
        verbose_name='Xodim'
    )
    date = models.DateField(
        verbose_name='Sana'
    )
    earned_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Topilgan summa'
    )
    paid_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='To\'langan summa'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Izoh'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yaratilgan vaqt'
    )

    class Meta:
        verbose_name = '2. Баланс'
        verbose_name_plural = '2. Балансы'
        ordering = ['-date', '-created_at']
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"

    @property
    def net_balance(self):
        """Qolgan balans"""
        return (self.earned_amount or 0) - (self.paid_amount or 0)


class MonthBalanceStatistics(models.Model):
    """Xodimlar oylik balans statistikasi modeli (Статистика Баланса)"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='month_balance_statistics',
        verbose_name='Xodim'
    )
    year = models.IntegerField(
        verbose_name='Yil'
    )
    month = models.IntegerField(
        verbose_name='Oy',
        choices=[
            (1, 'Yanvar'), (2, 'Fevral'), (3, 'Mart'),
            (4, 'Aprel'), (5, 'May'), (6, 'Iyun'),
            (7, 'Iyul'), (8, 'Avgust'), (9, 'Sentabr'),
            (10, 'Oktabr'), (11, 'Noyabr'), (12, 'Dekabr'),
        ]
    )
    total_earned = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Jami topilgan'
    )
    total_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Jami to\'langan'
    )
    net_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Oy bo\'yicha qoldig\'i'
    )

    class Meta:
        verbose_name = '3. Статистика за месяц'
        verbose_name_plural = '3. Статистика за месяц'
        unique_together = ['employee', 'year', 'month']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.employee.full_name} - {self.year}-{self.month:02d}"

    @classmethod
    def update_statistics(cls, employee, year, month):
        """Balance modelidan statistikani yangilash"""
        from django.db.models import Sum

        # Oy uchun Balance yozuvlarini hisoblash
        balances = Balance.objects.filter(
            employee=employee,
            date__year=year,
            date__month=month
        )

        total_earned = balances.aggregate(total=Sum('earned_amount'))['total'] or 0
        total_paid = balances.aggregate(total=Sum('paid_amount'))['total'] or 0
        net_balance = total_earned - total_paid

        # Avval eski yozuvni o'chirish
        cls.objects.filter(
            employee=employee,
            year=year,
            month=month
        ).delete()

        # Faqat ma'lumot bor bo'lsa yangi statistikani yaratish
        if total_earned > 0 or total_paid > 0:
            statistics = cls.objects.create(
                employee=employee,
                year=year,
                month=month,
                total_earned=total_earned,
                total_paid=total_paid,
                net_balance=net_balance,
            )
            return statistics

        return None


class YearlyBalanceStatistics(models.Model):
    """Xodimlar yillik balans statistikasi modeli"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='yearly_balance_statistics',
        verbose_name='Xodim'
    )
    year = models.IntegerField(
        verbose_name='Yil'
    )
    total_earned = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Yil bo\'yicha jami topilgan'
    )
    total_paid = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Yil bo\'yicha jami to\'langan'
    )
    net_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name='Yil bo\'yicha qoldig\'i'
    )

    class Meta:
        verbose_name = '4. Статистика за год'
        verbose_name_plural = '4. Статистика за год'
        unique_together = ['employee', 'year']
        ordering = ['-year', 'employee__full_name']

    def __str__(self):
        return f"{self.employee.full_name} - {self.year} (Yillik)"

    @classmethod
    def update_yearly_statistics(cls, employee, year):
        """Balance modelidan yillik statistikani yangilash"""
        from django.db.models import Sum

        # Yil uchun Balance yozuvlarini hisoblash
        balances = Balance.objects.filter(
            employee=employee,
            date__year=year
        )

        total_earned = balances.aggregate(total=Sum('earned_amount'))['total'] or 0
        total_paid = balances.aggregate(total=Sum('paid_amount'))['total'] or 0
        net_balance = total_earned - total_paid

        # Avval eski yozuvni o'chirish
        cls.objects.filter(
            employee=employee,
            year=year
        ).delete()

        # Faqat ma'lumot bor bo'lsa yangi statistikani yaratish
        if total_earned > 0 or total_paid > 0:
            statistics = cls.objects.create(
                employee=employee,
                year=year,
                total_earned=total_earned,
                total_paid=total_paid,
                net_balance=net_balance,
            )
            return statistics

        return None
