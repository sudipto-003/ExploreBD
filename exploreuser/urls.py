from django.urls import path, include
from .views import *


urlpatterns = [
	path('signup/', SignUpView.as_view(), name='signup'),
	path('login/', LoginView.as_view(), name='login'),
	path('home/', HomeView.as_view(), name='home'),
	path('logout/', LogoutView.as_view(), name='logout'),
	path('search/', search, name='search'),
	path('<int:pk>/timeline/', user_timeline, name='user_timeline'),
	path('newsfeed', user_story, name='news_feed'),
	path('<int:pk>/profile/', view_profile, name='view_profile'),
	path('<int:pk>/profile/edit/', edit_profile, name='edit_profile'),
	path('startfollowing/<int:following_id>/', start_following, name='start_following'),
	path('unfollow/<int:unfollow_id>/', unfollow_user, name='unfollow_user'),
	path('<int:pk>/following/', user_following, name='user_following'),
	path('<int:pk>/followers/', user_followers, name='user_followers'),
	path('posts/', include('explorepost.urls')),
]