from django.urls import path
from explorepost.views import *


urlpatterns = [
	path('createpost/', create_post, name='create_post'),
	path('<int:pk>/', view_userpost, name='view_userpost'),
	]