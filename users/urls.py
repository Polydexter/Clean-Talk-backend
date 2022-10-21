from django.urls import path
from .views import RegisterAPI, UserDetails


urlpatterns = [
    path('register/', RegisterAPI.as_view()),
    path('details/', UserDetails.as_view()),
]