"""
URL configuration for payment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from .views import CourseViewSet, CourseStreamViewSet, CourseInstanceViewSet,PaymentViewSet, payments_view
from .utils import get_filtered_payments,fill_data

router = routers.DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'coursestreams', CourseStreamViewSet)
router.register(r'courseinstances', CourseInstanceViewSet)
router.register(r'payments', PaymentViewSet)  # Используйте PaymentViewSet здесь

urlpatterns = [
    path('payments/', payments_view, name="payments"),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/get_filtered_payments/', get_filtered_payments, name='get_filtered_payments'),
    path('api/fill_data/', fill_data, name='fill_data'),
  
 
]
