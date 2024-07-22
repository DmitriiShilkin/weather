from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, OneTimeCode


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,
    )
    add_fieldsets = (
        *UserAdmin.add_fieldsets,
        (None, {
            'fields': (
                'email',
                'last_name',
                'first_name',
                )}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OneTimeCode)
