from django.contrib import admin
from .models import Contact
from django.contrib.auth.models import Group
from django.apps import AppConfig

class UserAppConfig(AppConfig):
    name = 'userapp'

    def ready(self):
        Group.objects.get_or_create(name='Admin')
        Group.objects.get_or_create(name='Student')

# Register your models here.

admin.site.register(Contact)
