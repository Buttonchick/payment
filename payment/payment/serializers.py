from rest_framework import serializers
from .models import Course, CourseStream, CourseInstance, Payment


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id','name', 'visibility']

class CourseStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStream
        fields = ['id','name', 'course']

class CourseInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseInstance
        fields = ['id','name', 'stream']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id','course', 'timestamp', 'payed', 'payed_amount', 'payed_currency']
