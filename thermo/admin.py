from django.contrib import admin
from .models import Patient
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from typing import Set

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

class MyAdminSite(AdminSite):
    site_header = 'Distress Thermometer Server'

admin_site = MyAdminSite(name='myadmin')

# Unregister the provided model admin

class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'therno_value',
        'issues',
        'other_issues'
        )

Pia nyakairu
admin_site.register(Patient, PatientAdmin)
admin_site.register(User)
admin_site.register(Group)

#@admin.register(User)
class CustomUserAdmin(UserAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()  # type: Set[str]

        if not is_superuser:
            disabled_fields |= {
                'username',
                'is_superuser',
                'user_permissions',
            }

        # Prevent non-superusers from editing their own permissions
        if (
            not is_superuser
            and obj is not None
            and obj == request.user
        ):
            disabled_fields |= {
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form
