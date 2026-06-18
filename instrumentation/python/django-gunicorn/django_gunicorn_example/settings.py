from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-opentelemetry-example"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS = []
MIDDLEWARE = []

ROOT_URLCONF = "django_gunicorn_example.urls"
WSGI_APPLICATION = "django_gunicorn_example.wsgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
