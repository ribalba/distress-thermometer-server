from django.contrib import admin
from .models import Record, Patient
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


class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'pseudonym',
        'phone_number',
        'last_upload'
      )


    change_form_template = 'patient_view.html'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        records = Record.objects.filter(patient_id=object_id)
        extra_context = extra_context or {'records':records}
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    class Media:
        js = ('https://cdn.jsdelivr.net/npm/fomantic-ui@2.8.3/dist/semantic.min.js',)
        css = {
             'all': ('https://cdn.jsdelivr.net/npm/fomantic-ui@2.8.3/dist/semantic.min.css',)
        }


class RecordAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'pseudonym',
        'phone_number',
        'diagnosis',
        'quality_of_life',
        'body',
        'mind',
        'living',
        'uploaded'
        )

    list_filter = ('patient__pseudonym',)


    # search_fields = (
    #     'pk',
    #     'first_name',
    #     'last_name'
    # )

    fieldsets = (
        (None, {
            'fields': (
                'pk',
                'patient_link',
                ('pseudonym',
                'diagnosis'),
                ('phone_number',
                'provider_phone_number'),
                'clinic_email',
                'detail_response'
            )
        }),
        # ('Advanced options', {
        #     'classes': ('collapse',),
        #     'fields': ('detail_response', ),
        # }),
    )


    class Media:
        js = ('https://cdn.jsdelivr.net/npm/fomantic-ui@2.8.3/dist/semantic.min.js',)
        css = {
             'all': ('https://cdn.jsdelivr.net/npm/fomantic-ui@2.8.3/dist/semantic.min.css',)
        }


admin_site.register(Record, RecordAdmin)
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
