from django.shortcuts import render
from .models import Course, CourseStream, CourseInstance, Payment
from django.http import JsonResponse
from decimal import Decimal
import datetime
from dateutil import parser



def get_request_params(request):
    course_name = request.GET.get('course', '')
    stream_name = request.GET.get('stream', '')
    instance_name = request.GET.get('instance', '')
    currency = request.GET.get('currency', 'RUB')
    data_from = request.GET.get('data_from', '')
    data_to = request.GET.get('data_to', '')

    if data_from:
        data_from = datetime.datetime.strptime(data_from, '%m/%d/%Y %I:%M %p')
    if data_to:
        data_to = datetime.datetime.strptime(data_to, '%m/%d/%Y %I:%M %p')

    return course_name, stream_name, instance_name, currency, data_from, data_to


def get_course_objects(course_name, stream_name, instance_name):
    course = Course.objects.filter(name=course_name).first()
    stream = CourseStream.objects.filter(name=stream_name, course=course).first()
    instance = CourseInstance.objects.filter(name=instance_name, stream=stream).first()
    return course, stream, instance

def filter_payments(instance, data_from, data_to): 
    filtered_payments = Payment.objects.filter(course=instance, payed=True) 
    if data_from: 
        filtered_payments = filtered_payments.filter(timestamp__gte=data_from) 
    if data_to: 
        filtered_payments = filtered_payments.filter(timestamp__lte=data_to) 
    return filtered_payments



def calculate_total_amounts(filtered_payments_values):
    amounts = {}
    total_amount_rub = 0
    for payment in filtered_payments_values:
        payed_currency = payment['payed_currency']
        payed_amount = payment['payed_amount']
        if payed_currency not in amounts:
            amounts[payed_currency] = 0
        amounts[payed_currency] += payed_amount
        converted_amount_rub = convert_price(payed_amount, payed_currency, "RUB")
        total_amount_rub += converted_amount_rub

    total_amounts = {}
    for currency in amounts.keys():
        total_amounts[currency] = convert_price(total_amount_rub, "RUB", currency)

    return amounts, total_amounts


def get_filtered_payments(request):
    course_name, stream_name, instance_name, currency, data_from, data_to = get_request_params(request)
    course, stream, instance = get_course_objects(course_name, stream_name, instance_name)
    filtered_payments = filter_payments(instance, data_from, data_to)

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
    amounts, total_amounts = calculate_total_amounts(filtered_payments_values)

    return JsonResponse({
        'data': data,
        'amounts': amounts,
        'total_amounts': total_amounts,
    }, safe=False)




def convert_price(amount, from_currency, to_currency):
    rates = {
        "EUR": {"USD": Decimal('1.12'), "RUB": Decimal('84.35'), "ILS": Decimal('3.85')},
        "USD": {"EUR": Decimal('0.89'), "RUB": Decimal('75.15'), "ILS": Decimal('3.43')},
        "RUB": {"EUR": Decimal('0.011'), "USD": Decimal('0.013'), "ILS": Decimal('0.046')},
        "ILS": {"EUR": Decimal('0.24'), "USD": Decimal('0.28'), "RUB": Decimal('21.75')}
    }


    if from_currency == to_currency:
        return amount

    if from_currency in rates and to_currency in rates[from_currency]:
        rate = rates[from_currency][to_currency]
        return amount * rate


    return 0