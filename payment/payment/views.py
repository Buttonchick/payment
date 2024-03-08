from rest_framework import viewsets
from django.shortcuts import render
from .models import Course, CourseStream, CourseInstance, Payment
from .serializers import CourseSerializer, CourseStreamSerializer, CourseInstanceSerializer, PaymentSerializer
from django.http import JsonResponse
from forex_python.converter import CurrencyRates


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
    queryset = Payment.objects.none()  # или просто queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        queryset = Payment.objects.filter(payed=True)
        for payment in queryset:
            payment.payed_amount = convert_price(payment.payed_amount, payment.payed_currency, "USD")
            payment.payed_currency = "USD"
        return queryset
        
def payments_view(request):
    return render(request, 'payments.html')





from decimal import Decimal

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
    



def get_total_amount(request):
    currency = request.GET.get('currency', 'RUB')
    payments = Payment.objects.all()
    total_amount = 0

    for payment in payments:
        converted_amount = convert_price(payment.payed_amount, payment.payed_currency, currency)
        total_amount += converted_amount

    return JsonResponse({'total_amount': total_amount})







