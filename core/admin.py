from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Image, Annotation, Verification, Batch

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('User Type', {'fields': ('user_type',)}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Image)
admin.site.register(Annotation)
admin.site.register(Verification)
admin.site.register(Batch)

