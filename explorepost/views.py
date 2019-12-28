from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Post, PostImages, Hashtags, Comments, PostRating, PostHit
from .forms import PostForm, PostImageForm, HashtagField, RatingForm
from django.forms import modelformset_factory
from django.contrib import messages
from django.db.models import Avg, Sum
from exploreuser.models import ExUser
from datetime import datetime, timezone
from django.http import JsonResponse

# Create your views here.

@login_required(login_url='/users/login')
def create_post(request):
	ImageFormSet = modelformset_factory(PostImages, form=PostImageForm, extra=3)

	if request.method == 'POST':
		postform = PostForm(request.POST)
		hashtags = HashtagField(request.POST)
		formset = ImageFormSet(request.POST, request.FILES, queryset=PostImages.objects.none())

		if postform.is_valid() and formset.is_valid():
			new_post = postform.save(commit=False)
			new_post.user = request.user
			new_post.save()

			for form in formset.cleaned_data:
				if form:
					image = form['image']
					photo = PostImages(post=new_post, image=image)
					photo.save()

			if hashtags.is_bound and hashtags.is_valid():
				s = hashtags.cleaned_data['tag']

				hash_list = [i[1:] for i in s.split() if i[0] == '#']

				for hashtag in hash_list:
					if Hashtags.objects.filter(tag=hashtag).exists():
						ht = Hashtags.objects.get(tag=hashtag)
						new_post.hashtags_set.add(ht)

					else:
						ht = Hashtags(tag=hashtag)
						ht.save()
						new_post.hashtags_set.add(ht)
			
			return redirect(reverse('view_userpost', kwargs={'pk': new_post.id}))

	else:
		postform = PostForm()
		hashtags = HashtagField()
		formset = ImageFormSet(queryset=PostImages.objects.none())

	return render(request, 'explorepost/post.html', {'postform': postform, 'formset': formset, 'hashtags': hashtags})


@login_required(login_url='/users/login')
def view_userpost(request, pk):
	post = Post.objects.get(pk=pk)
	images = PostImages.objects.filter(post__pk=pk)
	tags = Hashtags.objects.filter(post__pk=pk)
	comments = Comments.objects.filter(on_post__pk=pk)
	try:
		user_rating = PostRating.objects.get(post__pk=post.pk, user__id=request.user.id)
	except PostRating.DoesNotExist:
		user_rating = None

	if user_rating is not None:
		user_rating = user_rating.rating

	avg_rating_dict = PostRating.objects.filter(post__pk=post.pk).aggregate(Avg('rating'))
	avg_rating = avg_rating_dict['rating__avg']

	post_views = PostHit.objects.filter(post=post).aggregate(Sum('hits'))
	num_of_views = post_views['hits__sum']
	print(num_of_views)

	if avg_rating is None:
		avg_rating = 'No one yet rated this post'

	if request.method == 'POST':
		comment_text = request.POST.get('comment', None)

		if comment_text is not None:
			new_comment = Comments(text=comment_text, on_post=post)
			new_comment.user = request.user
			new_comment.save()

		return redirect(reverse('view_userpost', kwargs={'pk': post.id}))
	
	return render(request, 'explorepost/view.html', {'post': post, 'images': images, 'views': num_of_views, 'user_rating': user_rating, 'avg_rating': avg_rating, 'tags': tags, 'comments': comments})


	
@login_required(login_url='/users/login')
def post_rate(request, pk):
	route = request.GET.get('next', reverse('view_profile', kwargs={'pk': request.user.id }))
	rated_post = Post.objects.get(pk=pk)
	
	if request.method == 'POST':
		new_rating = request.POST.get('rating', None)
		if new_rating is not None:
			PostRating.objects.update_or_create(post=rated_post, user=request.user, defaults={'rating': new_rating},)

	return redirect(route)


@login_required(login_url='/users/login')
def post_hit(request):
	user_id = request.GET.get('user', None)
	post_id = request.GET.get('post', None)
	user = ExUser.objects.get(pk=user_id)
	post = Post.objects.get(pk=post_id)
	time_now = datetime.now(timezone.utc)

	if post.user.id != user.id:

		try:
			user_post_hit = PostHit.objects.get(user=user, post=post)
		except PostHit.DoesNotExist:
			user_post_hit = PostHit.objects.create(user=user, post=post)

		num_of_hits = user_post_hit.hits
		if num_of_hits < PostHit.max_permitted_hit:
			diff = time_now - user_post_hit.last_viewed
			diff_sec = diff.total_seconds()
			diff_hour = divmod(diff_sec, 3600)[0]

			if diff_hour > 6:
				user_post_hit.hits = num_of_hits+1
				user_post_hit.save()
		else:
			user_post_hit.save()

	redirect_url = reverse('view_userpost', kwargs={'pk': post_id})

	data = {'redirect_url': redirect_url
			}

	return JsonResponse(data)
