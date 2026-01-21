from django.db import models
from accounts.models import User


class Employee(models.Model):
    """Сотрудники model"""
    SALARY_TYPES = [
        ('fixed', 'Belgilangan'),
        ('hourly', 'Soatbay'),
        ('piecework', 'Ish hajmi bo\'yicha'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name='Сотрудник'
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name='To\'liq ism',
        blank=True
    )
    position = models.CharField(
        max_length=100,
        verbose_name='Lavozim'
    )
    salary_type = models.CharField(
        max_length=50,
        choices=SALARY_TYPES,
        default='fixed',
        verbose_name='Maosh turi'
    )
    base_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Asosiy maosh'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Yaratilgan vaqt'
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

    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"

    @property
    def net_balance(self):
        """Qolgan balans"""
        return self.earned_amount - self.paid_amount


class BalanceStatistics(models.Model):
    """Xodimlar balans statistikasi modeli (Статистика Баланс)"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='balance_statistics',
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
        verbose_name='Qolgan balans'
    )
    is_closed = models.BooleanField(
        default=False,
        verbose_name='Yopilgan'
    )

    class Meta:
        verbose_name = '3. Статистика баланса'
        verbose_name_plural = '3. Статистика баланса'
        unique_together = ['employee', 'year', 'month']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.employee.full_name} - {self.year}-{self.month:02d}"
