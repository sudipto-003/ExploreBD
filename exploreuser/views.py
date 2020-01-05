from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import View
from .forms import *
from .models import ExUser, Profile
from explorepost.models import Post, Hashtags, PostHit, PostRating
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.db.models import Q, F
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Count, Sum, Avg, Case, When
from datetime import datetime, timezone

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
			redirect_to = request.GET.get('next', reverse('home'))
			return redirect(redirect_to)

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


@login_required(login_url='/login')
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


@login_required(login_url='/login')
def view_profile(request, pk):
	user = ExUser.objects.get(pk=pk)
	posts = Post.objects.filter(user__id=user.id)
	following = user.profile.follows.all()
	followers = user.profile.followers.all()

	return render(request, 'exploreuser/viewuserprofile.html', {'u': user, 'userposts': posts, 
			'following': following, 'followers': followers})


@login_required(login_url='/login')
def start_following(request, following_id):
	redirect_to = request.GET.get('next', reverse('view_profile', kwargs={'pk': request.user.id}))
	follwer = Profile.objects.get(user__id=request.user.id)
	following = Profile.objects.get(user__id=following_id)

	follwer.follows.add(following)

	return HttpResponseRedirect(redirect_to)


@login_required(login_url='/login')
def unfollow_user(request, unfollow_id):
	redirect_to = request.GET.get('next', reverse('view_profile', kwargs={'pk': request.user.id}))
	follower = Profile.objects.get(user__id=request.user.id)
	following = Profile.objects.get(user__id=unfollow_id)

	follower.follows.remove(following)

	return HttpResponseRedirect(redirect_to)


@login_required(login_url='/login')
def user_following(request, pk):
	u = ExUser.objects.get(pk=pk)
	following = u.profile.follows.all()

	return render(request, 'exploreuser/userfollowinglist.html', {'following': following, 'u': u})



@login_required(login_url='/login')
def user_followers(request, pk):
	u = ExUser.objects.get(pk=pk)
	followers = u.profile.followers.all()

	return render(request, 'exploreuser/userfollowerslist.html', {'followers': followers, 'u': u})



@login_required(login_url='/login')
def user_timeline(request, pk):
	month_name = {
		1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9 : 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
	}
	user = ExUser.objects.get(pk=pk)
	user_posts = Post.objects.filter(user__id=user.id)
	month_year = user_posts.annotate(month=ExtractMonth('timestamp'), year=ExtractYear('timestamp')).values('month', 
		'year').distinct().order_by('-month')

	total_posts = user_posts.count()
	a = []
	for f in month_year:
		a.append((month_name[f['month']]+" "+str(f['year']), user_posts.filter(timestamp__month=f['month'], timestamp__year=f['year'])))


	return render(request, 'exploreuser/timeline.html', {'l': a, 'u': user, 'total_posts': total_posts})




@login_required(login_url='/login')
def user_story(request):
	user = Profile.objects.get(user__id=request.user.id)
	user_follows = user.follows.values('user_id').all()
	rec_posts = Post.objects.filter(user__id__in=user_follows).order_by('-timestamp')
	filtered_posts = []

	for posti in rec_posts:
		post_view = PostHit.objects.filter(post__id=posti.id).aggregate(Sum('hits'))
		number_of_views = post_view['hits__sum']
		avg_rating_dict = PostRating.objects.filter(post__id=posti.id).aggregate(Avg('rating'))
		avg_rating = avg_rating_dict['rating__avg']
		filtered_posts.append((posti, number_of_views, avg_rating))

	return render(request, 'exploreuser/newsfeed.html', {'posts': filtered_posts})


def search(request):
	s = request.GET.get('search', None)
	mood = 'general'

	if s is not None:
		if s[0] == '#':
			s = s[1:]
			htags = Hashtags.objects.filter(tag__icontains=s)
			posts = Post.objects.filter(hashtags__in=htags)
			mood = 'tag'
			users = None

		elif s[0] == '@':
			s = s[1:]
			try:
				user_r = ExUser.objects.get(username=s)
			except ExUser.DoesNotExist:
				messages.error(request, 'There is no user with username @{}'.format(s))
				return redirect(reverse('home'))


			return redirect(reverse('view_profile', kwargs={'pk': user_r.id}))

		else:
			users = ExUser.objects.filter(Q(username__icontains=s) | Q(first_name__icontains=s) | Q(last_name__icontains=s))
			posts = Post.objects.filter(title__icontains=s)
			htags = Hashtags.objects.filter(tag__icontains=s)
			posts_h = Post.objects.filter(hashtags__in=htags)
			posts = posts.union(posts_h)

	return render(request, 'exploreuser/searchresult.html', {'users': users, 'posts': posts, 'mood': mood})



def find_trending(request):
	now = datetime.now(timezone.utc)

	most_hited_post = PostHit.objects.values('post').annotate(total_views=Sum('hits')).order_by('-total_views')

	post_filtered = [(d['post'], d['total_views']) for d in most_hited_post if d['total_views'] != 0]
	post_ids = [i[0] for i in post_filtered]
	'''
	posts = Post.objects.filter(pk__in=post_ids).annotate(diff=(now - F('timestamp'))).values('id', 'diff')
	timediff = [divmod(i['diff'].total_seconds(), 3600)[0] for i in posts]

	ratio = []
	for i in range(0, len(post_ids)):
		if timediff[i] == 0:
			timediff[i] = 1

		ratio.append(post_filtered[i][1]/timediff[i])

	id_sync = [x for _, x in sorted(zip(ratio, post_ids), key=lambda pair: pair[0], reverse=True)]
	'''
	preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(post_ids)])
	top_trending = Post.objects.filter(id__in=post_ids).order_by(preserved, 'timestamp')
	


	return render(request, 'exploreuser/trending.html', {'posts': top_trending})
