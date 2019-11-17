from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
#from django.contrib.auth.models import User

from .forms import ExUserCreationForm, ExUserChangeForm
from .models import ExUser, Profile

class ProfileInline(admin.StackedInline):
	model = Profile


class ExUserAdmin(UserAdmin):
	add_form = ExUserCreationForm
	form = ExUserChangeForm
	model = ExUser
	list_display = ['username', 'date_of_birth',]

	fieldsets = UserAdmin.fieldsets + (
		(None, {'fields': ('date_of_birth', )}),
	)

	inlines = [ProfileInline]


admin.site.register(ExUser, ExUserAdmin)