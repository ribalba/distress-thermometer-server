from django.contrib import admin
from .models import Patient
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy

class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'therno_value',
        'issues',
        'other_issues'
        )




class MyAdminSite(AdminSite):
    site_header = 'Distress Thermometer Server'

admin_site = MyAdminSite(name='myadmin')
admin_site.register(Patient, PatientAdmin)
