from django.shortcuts import render
from .models import Course, CourseStream, CourseInstance, Payment
from django.http import JsonResponse
from decimal import Decimal
import datetime
from dateutil import parser
from django.db.models import Max, Min

def get_inputs(request):
    course_id = request.GET.get('course') or None
    stream_id = request.GET.get('stream') or None
    instance_id = request.GET.get('instance') or None
    date_from = request.GET.get('date_from') or None
    date_to = request.GET.get('date_to') or None
    currency = request.GET.get('currency') or None

    if date_from:
        date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d')
    if date_to:
        date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d')

    return course_id, stream_id, instance_id, date_from, date_to, currency




def filter_payments(course_id, stream_id, instance_id, date_from, date_to, currency):
    filtered_payments = Payment.objects.filter(payed=True)

    if course_id:
        filtered_payments = filtered_payments.filter(course__stream__course__id=course_id)
    if stream_id:
        filtered_payments = filtered_payments.filter(course__stream__id=stream_id)
    if instance_id:
        filtered_payments = filtered_payments.filter(course__id=instance_id)
    if date_from:
        filtered_payments = filtered_payments.filter(timestamp__gte=date_from)
    if date_to:
        filtered_payments = filtered_payments.filter(timestamp__lte=date_to)
    if currency:
        filtered_payments = filtered_payments.filter(payed_currency=currency)
    return filtered_payments




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

def calculate_total_amounts(filtered_payments):
    amounts = {}
    total_amount_rub = 0
    for payment in filtered_payments:
        payed_currency = payment.payed_currency
        payed_amount = payment.payed_amount
        if payed_currency not in amounts:
            amounts[payed_currency] = 0
        amounts[payed_currency] += payed_amount
        converted_amount_rub = convert_price(payed_amount, payed_currency, "RUB")
        total_amount_rub += converted_amount_rub

    total_amounts = {}
    for currency in amounts.keys():
        total_amounts[currency] = convert_price(total_amount_rub, "RUB", currency)

    return amounts, total_amounts





def get_ui(request):
    course_id, stream_id, instance_id, date_from, date_to, currency = get_inputs(request)

    filtered_payments =  filter_payments(course_id, stream_id, instance_id, date_from, date_to, currency)

    amounts, total_amounts = calculate_total_amounts(filtered_payments)


    min_timestamp_result = filtered_payments.aggregate(Min('timestamp'))
    max_timestamp_result = filtered_payments.aggregate(Max('timestamp'))
    min_timestamp = min_timestamp_result['timestamp__min']
    max_timestamp = max_timestamp_result['timestamp__max']

    
    course_dropdown = list(Course.objects.all().values())
    stream_dropdown = list(CourseStream.objects.filter(course__id=course_id).values())
    instance_dropdown = list(CourseInstance.objects.filter(stream__id=stream_id).values())
    date_from_field = min_timestamp
    date_to_field = max_timestamp
    currency_dropdown = [{"id": total_amount, "name": currency} for currency, total_amount in total_amounts.items()]

    data = {
        'course_dropdown': course_dropdown,
        'stream_dropdown': stream_dropdown,
        'instance_dropdown': instance_dropdown,
        'date_from_field': date_from_field,
        'date_to_field': date_to_field,
        'currency_dropdown': currency_dropdown,
        'amounts':amounts
    }
    return JsonResponse(data)

def get_table_headers(request):
    headers = [{'id':'month','name':'Месяц'},{'id':'course','name':'Курс'}]

    currencies = list(Payment.objects.filter(payed=True).values_list('payed_currency', flat=True).distinct())
    for currency in currencies:
        headers.append({'id':currency,'name':currency})  

    headers.append({'id':'amount_usd','name':'Всего(USD)'})
    return JsonResponse({'headers': headers})


def fill_data(request):
    filtered_payments = Payment.objects.filter(payed=True)
    currencies = list(Payment.objects.filter(payed=True).values_list('payed_currency', flat=True).distinct())
    all_courses = list(Course.objects.all().values())
    formatted_dates = [12 * date.timestamp.year + date.timestamp.month for date in filtered_payments]
    max_data = max(formatted_dates)
    min_data = min(formatted_dates)
    table = {}

    for data in range(min_data, max_data + 1):
        month = datetime.datetime(year=data // 12, month=data % 12 + 1, day=1).strftime('%B')
        year = datetime.datetime(year=data // 12, month=data % 12 + 1, day=1).strftime('%Y')
        for course in all_courses:
            course_name = course['name']
            course_payments = filtered_payments.filter(course__stream__course__id=course['id'])
            course_payment_dates = [12 * date.timestamp.year + date.timestamp.month for date in course_payments]
            if data in course_payment_dates:
                key = f"{data}_{course_name}"
                table[key] = {}
                table[key]['year'] = year
                table[key]['month'] = month
                table[key]['course'] = course_name
                for currency in currencies:
                    table[key][currency] = 0
                table[key]['amount_usd'] = 0

        key = f"{data}_{'Всего'}"
        table[key] = {}
        table[key]['year'] = year
        table[key]['month'] = month
        table[key]['course'] = 'Всего'
        for currency in currencies:
            table[key][currency] = 0
        table[key]['amount_usd'] = 0

    for payment in filtered_payments:
        data = 12 * payment.timestamp.year + payment.timestamp.month
        course = payment.course.stream.course.name
        currency = payment.payed_currency
        amount = payment.payed_amount
        amount_usd = convert_price(payment.payed_amount, payment.payed_currency, "USD")
        key = f"{data}_{course}"
        table[key][currency] += amount
        table[key]['amount_usd'] += amount_usd

        all_key = f"{data}_{'Всего'}"
        table[all_key][currency] += amount
        table[all_key]['amount_usd'] += amount_usd




    table_data = []
    for key, value in table.items():
        record = value
        record['id'] = key  # Добавьте идентификатор записи в объект
        table_data.append(record)

    return JsonResponse(table_data, safe=False)