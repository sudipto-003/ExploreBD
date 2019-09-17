from django.urls import path
from .views import *


urlpatterns = [
	path('createpost/', create_post, name='create_post'),
	]