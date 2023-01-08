from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.forms import UserRegistrationForm, UserUpdateForm
from .models import CustomUser, Student, Staff


class CustomUserAdmin(UserAdmin) : 
    form = UserUpdateForm
    add_form = UserRegistrationForm
    list_display = ("user_id" , "username", "date_joined" , "last_login" , "is_admin" , "is_staff", "is_student")
    search_fields = ("user_id", "is_admin", "is_staff", "is_student")
    readonly_fields = ("id" , "date_joined" , "last_login")
    filter_horizontal = ()
    list_filter = ("is_student", "is_staff", "is_admin")
    fieldsets = ()
    add_fieldsets = (
        (None, {'fields': ('user_id', 'password1', 'password2', "is_admin" , "is_staff", "is_student")}),
    )
    ordering = ["username"]

admin.site.register(CustomUser , CustomUserAdmin)
admin.site.register(Student)
admin.site.register(Staff)

