from django.urls import path, include
from .views import *


urlpatterns = [
	path('signup/', SignUpView.as_view(), name='signup'),
	path('login/', LoginView.as_view(), name='login'),
	path('home/', HomeView.as_view(), name='home'),
	path('logout/', LogoutView.as_view(), name='logout'),
	path('<int:pk>/profile/', view_profile, name='view_profile'),
	path('<int:pk>/profile/edit/', edit_profile, name='edit_profile'),
	path('posts/', include('explorepost.urls')),
]