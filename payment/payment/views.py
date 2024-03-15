from rest_framework import viewsets
from django.shortcuts import render
from .models import Course, CourseStream, CourseInstance, Payment
from .serializers import CourseSerializer, CourseStreamSerializer, CourseInstanceSerializer, PaymentSerializer

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

def payments_view(request):
    return render(request, 'payments.html')
