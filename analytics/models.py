from django.db import models


class FinancialPerformanceIndicator(models.Model):
    """Moliya ko'rsatkichlari modeli"""
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
    rent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Ijara'
    )
    electricity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Elektroenergiya'
    )
    gas = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Gaz'
    )
    water = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Suv'
    )
    salaries = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Maoshlar'
    )
    machine_equipment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Mashina va uskunalar'
    )
    tools_equipment = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Asboblar va uskunalar'
    )
    staff_food = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Xodimlar uchun ovqat'
    )

    class Meta:
        verbose_name = "1. Финансовый показатель"
        verbose_name_plural = "1. Финансовые показатели"

        unique_together = ['year', 'month']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.year}-{self.month:02d} - Ko'rsatkichlar"

    @property
    def total_expenses(self):
        """Jami xarajatlar"""
        return (self.rent + self.electricity + self.gas +
                self.water + self.salaries + self.machine_equipment +
                self.tools_equipment + self.staff_food)
