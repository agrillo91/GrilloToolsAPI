from django.urls import path
from .views import verify_license

urlpatterns = [
    path('verify/', verify_license, name='verify_license'),
]
