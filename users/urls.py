from django.urls import path
from .views import RegisterAPI, Userlist


urlpatterns = [
    path('', Userlist.as_view()),
    path('register/', RegisterAPI.as_view()),
]