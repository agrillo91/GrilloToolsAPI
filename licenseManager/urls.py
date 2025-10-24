from django.urls import path
from .views import verify_license, validate_token

urlpatterns = [
    path('verify/', verify_license, name='verify_license'),
    path("validate/", validate_token, name="validate_token"),  
]

