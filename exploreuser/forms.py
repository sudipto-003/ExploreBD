from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ExUser, Profile
from django.contrib.admin.widgets import AdminDateWidget
from datetime import date

class ExUserCreationForm(UserCreationForm):
	first_name = forms.CharField(max_length=100)
	last_name = forms.CharField(max_length=100)
	email = forms.EmailField(max_length=254, help_text='Required to reset password in future')
	date_of_birth = forms.DateField(help_text='yyyy-mm-dd')

	class Meta(UserCreationForm):
		model = ExUser
		fields = ['first_name', 'last_name', 'username', 'email', 'date_of_birth', 'password1', 'password2',]

	def clean_date_of_birth(self):
		birth_date = self.cleaned_data['date_of_birth']
		today = date.today()
		age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

		if age < 15 or age > 80:
			raise forms.ValidationError('Age should be at least 15 and maximum 80')

		return birth_date

	def clean_email(self):
		post_email = self.cleaned_data['email']

		if ExUser.objects.filter(email=post_email).exists():
			raise forms.ValidationError('Email already taken')

		return post_email



class ExUserChangeForm(UserChangeForm):

	class Meta(UserChangeForm):
		model = ExUser
		fields = ('first_name', 'last_name', 'username', 'email', 'date_of_birth',)


class ProfileEditForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['photo', 'phone', 'address', 'about', ]
		