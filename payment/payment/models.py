from django.db import models
from django.utils.translation import gettext_lazy as _




class Course(models.Model):    # Курс
    name = models.TextField()

		# Брать только курсы с visibility == 2
    visibility = models.PositiveIntegerField(choices=(
        (0, _('Invisible Everywhere')),
        (1, _('Deactivated')),
        (2, _('Visible'))
    ))


class CourseStream(models.Model):  # Поток
    name = models.CharField(max_length=255, blank=False, help_text='Название Потока')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    

class CourseInstance(models.Model):   # Тариф
    name = models.CharField(max_length=255, blank=False, help_text=_('Tariff name'))
    stream = models.ForeignKey(CourseStream, help_text='Поток', on_delete=models.CASCADE)


class Payment(models.Model):
    # Тариф
    course = models.ForeignKey(CourseInstance, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField() #auto_now=True

		# нужно брать только платежи с payed = True
    payed = models.BooleanField(default=False)
    payed_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    payed_currency = models.CharField(max_length=4, default='', blank=True)