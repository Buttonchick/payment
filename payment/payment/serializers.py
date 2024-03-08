from rest_framework import serializers
from .models import Course, CourseStream, CourseInstance, Payment


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['name', 'visibility']

class CourseStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStream
        fields = ['name', 'course']

class CourseInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseInstance
        fields = ['name', 'stream']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['course', 'timestamp', 'payed', 'payed_amount', 'payed_currency']
