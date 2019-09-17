from django import forms
from .models import Post, PostImages, Hashtags


class PostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ['title', 'describtion', ]


class PostImageForm(forms.ModelForm):
	class Meta:
		model = PostImages
		fields = ['image', ]


class HashtagField(forms.Form):
	hashtag = forms.CharField(max_length=50)