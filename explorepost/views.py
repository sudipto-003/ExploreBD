from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, PostImages
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
			post_form = postform.save(commit=False)
			post_form.user = request.user
			post_form.save()

			for form in formset.cleaned_data:
				if form:
					image = form['image']
					photo = Images(post=post_form, image=image)
					photo.save()
					
			return redirect('home')

	else:
		postform = PostForm()
		hashtags = HashtagField()
		formset = ImageFormSet(queryset=PostImages.objects.none())

	return render(request, 'explorepost/post.html', {'postform': postform, 'formset': formset, 'hashtags': hashtags})