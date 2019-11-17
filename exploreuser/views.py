from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import View
from .forms import *
from .models import ExUser, Profile
from explorepost.models import Post
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

# Create your views here.
class SignUpView(View):
	form_class = ExUserCreationForm
	template_name = 'exploreuser/signup.html'

	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect('home')

		form = self.form_class()

		return render(request, self.template_name, {'form': form})

	def post(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect('home')
		
		form = self.form_class(request.POST)

		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect(reverse('edit_profile', kwargs={'pk': user.id}))

		return render(request, self.template_name, {'form': form})


class LoginView(View):
	form_class = AuthenticationForm
	template_name = 'exploreuser/login.html'

	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect('home')
		
		form = self.form_class()

		return render(request, self.template_name, {'form': form})

	def post(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return redirect('home')

		username = request.POST['username']
		paswd = request.POST['password']
		user = authenticate(username=username, password=paswd)

		if user is not None:
			login(request, user)
			return redirect('home')

		else:
			messages.error(request, 'Invalid username or password')
			form = self.form_class(request.POST)

			return render(request, self.template_name, {'form': form})


class HomeView(View):
	template_name = 'exploreuser/home.html'

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name)


class LogoutView(View):
	def get(self, request, *args, **kwargs):
		logout(request)
		return redirect('home') 


@login_required(login_url='/users/login')
def edit_profile(request, pk):
	user = ExUser.objects.get(pk=pk)

	if request.user.is_authenticated and request.user.id == user.id:
		if request.method == 'POST':
			user_profile = ProfileEditForm(request.POST, request.FILES, instance=user.profile)

			if user_profile.is_valid():
				user_profile.save()
				return redirect(reverse('view_profile', kwargs={'pk': user.id}))

		else:
			user_profile = ProfileEditForm(instance=user.profile)

		return render(request, 'exploreuser/edituserprofile.html', {'form': user_profile})

	else:
		raise PermissionDenied


@login_required(login_url='/users/login')
def view_profile(request, pk):
	user = ExUser.objects.get(pk=pk)
	posts = Post.objects.filter(user__username=user.username)

	return render(request, 'exploreuser/viewuserprofile.html', {'u': user, 'userposts': posts})
