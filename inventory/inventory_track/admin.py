from django.contrib import admin

from .models import LdapUser

# Register your models here.
admin.site.register(LdapUser)