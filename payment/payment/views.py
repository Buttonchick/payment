from rest_framework import viewsets
from django.shortcuts import render
from .models import Course, CourseStream, CourseInstance, Payment
from .serializers import CourseSerializer, CourseStreamSerializer, CourseInstanceSerializer, PaymentSerializer
from django.http import JsonResponse
from forex_python.converter import CurrencyRates
from decimal import Decimal
from django.db.models import Sum
import datetime


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseStreamViewSet(viewsets.ModelViewSet):
    queryset = CourseStream.objects.all()
    serializer_class = CourseStreamSerializer

class CourseInstanceViewSet(viewsets.ModelViewSet):
    queryset = CourseInstance.objects.all()
    serializer_class = CourseInstanceSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class FilteredPaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        course = self.request.GET.get('course', '')
        stream = self.request.GET.get('stream', '')
        instance = self.request.GET.get('instance', '')

        if course:
            queryset = queryset.filter(course__name=course)
        if stream:
            queryset = queryset.filter(course__stream__name=stream)
        if instance:
            queryset = queryset.filter(course__stream__instance__name=instance)

        return queryset

    

def get_filtered_payments(request):
    course_name = request.GET.get('course', '')
    stream_name = request.GET.get('stream', '')
    instance_name = request.GET.get('instance', '')
    currency = request.GET.get('currency', 'RUB')
    data_from = request.GET.get('data_from', '')
    data_to = request.GET.get('data_to', '')


    if data_from:
        data_from = datetime.datetime.strptime(data_from, '%Y-%m-%d')
    if data_to:
        data_to = datetime.datetime.strptime(data_to, '%Y-%m-%d')



    # Получаем объекты курса, потока и тарифа по их именам
   
    course = Course.objects.filter(name=course_name).first()

    stream = CourseStream.objects.filter(name=stream_name, course=course).first()

    instance = CourseInstance.objects.filter(name=instance_name, stream=stream).first()


    # Фильтруем платежи по дате
    filtered_payments = Payment.objects.filter(course=instance, payed=True)
    if data_from:
        filtered_payments = filtered_payments.filter(timestamp__gte=data_from)
    if data_to:
        filtered_payments = filtered_payments.filter(timestamp__lte=data_to)
   

    data = []
    for payment in filtered_payments:
        converted_amount = convert_price(payment.payed_amount, payment.payed_currency, "USD")
        data.append({
            'course': payment.course.name,
            'time': payment.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'payed': 'Да' if payment.payed else 'Нет',
            'amount': converted_amount,
            'currency': 'USD'
        })

    filtered_payments_values = filtered_payments.values('payed_currency', 'payed_amount')
    amounts ={}
    total_amounts ={}

    total_amount_rub = 0
    for payment in filtered_payments_values:
        if payment['payed_currency'] not in amounts:
            amounts[payment['payed_currency']] = 0
        amounts[payment['payed_currency']] += payment['payed_amount']
        converted_amount_rub = convert_price(payment['payed_amount'], payment['payed_currency'], "RUB")
        total_amount_rub += converted_amount_rub

    for currency in amounts.keys():
        total_amounts[currency] = convert_price(total_amount_rub, "RUB", currency)

        

    return JsonResponse({
        'data': data,
        'amounts': amounts,
        'total_amounts': total_amounts,
    }, safe=False)











        
def payments_view(request):
    return render(request, 'payments.html')







def convert_price(amount, from_currency, to_currency):
    # Define rates
    rates = {
        "EUR": {"USD": Decimal('1.12'), "RUB": Decimal('84.35'), "ILS": Decimal('3.85')},
        "USD": {"EUR": Decimal('0.89'), "RUB": Decimal('75.15'), "ILS": Decimal('3.43')},
        "RUB": {"EUR": Decimal('0.011'), "USD": Decimal('0.013'), "ILS": Decimal('0.046')},
        "ILS": {"EUR": Decimal('0.24'), "USD": Decimal('0.28'), "RUB": Decimal('21.75')}
    }

    # Check if from_currency and to_currency are the same
    if from_currency == to_currency:
        return amount

    # Check if from_currency and to_currency are in rates
    if from_currency in rates and to_currency in rates[from_currency]:
        rate = rates[from_currency][to_currency]
        return amount * rate

    # If from_currency or to_currency are not in rates, return None
    return 0
    



