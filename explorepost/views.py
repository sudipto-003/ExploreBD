from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Post, PostImages, Hashtags, Comments
from .forms import PostForm, PostImageForm, HashtagField
from django.forms import modelformset_factory
from django.contrib import messages

# Create your views here.

@login_required
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


@login_required
def view_userpost(request, pk):
	post = Post.objects.get(pk=pk)
	images = PostImages.objects.filter(post__pk=pk)
	tags = Hashtags.objects.filter(post__pk=pk)
	comments = Comments.objects.filter(on_post__pk=pk)

	if request.method == 'POST':
		comment_text = request.POST['comment']

		new_comment = Comments(text=comment_text, on_post=post)
		new_comment.user = request.user
		new_comment.save()

		return redirect(reverse('view_userpost', kwargs={'pk': post.id}))
	
	return render(request, 'explorepost/view.html', {'post': post, 'images': images, 'tags': tags, 'comments': comments})


	


		