from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class ThermoConfig(AppConfig):
    name = "thermo"
    verbose_name = 'Distress Thermometer Data'


class MyAdminConfig(AdminConfig):
    default_site = 'thermo.admin.MyAdminSite'