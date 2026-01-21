from django.db import models
from accounts.models import User


class IncomeExpense(models.Model):
    """Kirim va chiqim modeli"""
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='income_expenses',
        verbose_name='Yaratgan foydalanuvchi'
    )
    date = models.DateField(
        verbose_name='Sana'
    )
    income_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Kirim summasi'
    )
    expense_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Chiqim summasi'
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
        verbose_name = '1. Доходы и расходы'
        verbose_name_plural = '1. Доходы и расходы'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} - Kirim: {self.income_amount}, Chiqim: {self.expense_amount}"

    @property
    def net_profit(self):
        """Foyda"""
        return self.income_amount - self.expense_amount


class IncomeExpenseStatistics(models.Model):
    """Kirim va chiqim statistikasi modeli"""
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
    total_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Jami kirim'
    )
    total_expense = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Jami chiqim'
    )
    net_profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Foyda'
    )

    class Meta:
        verbose_name = '2. Статистика доходов и расходов'
        verbose_name_plural = '2. Статистика доходов и расходов'
        unique_together = ['year', 'month']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.year}-{self.month:02d} - Foyda: {self.net_profit}"
