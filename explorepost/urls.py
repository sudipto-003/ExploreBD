from django.urls import path
from explorepost.views import *


urlpatterns = [
	path('createpost/', create_post, name='create_post'),
	path('<int:pk>/', view_userpost, name='view_userpost'),
	path('postrate/<int:pk>/', post_rate, name='postrate'),
	path('posthit/', post_hit, name='post_hit'),
	]