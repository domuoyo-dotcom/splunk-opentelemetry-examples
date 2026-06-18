from django.urls import path

from django_gunicorn_example.views import hello

urlpatterns = [
    path("hello/", hello),
]
