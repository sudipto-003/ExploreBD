from django import forms
from .models import Post, PostImages, Hashtags, PostRating


class PostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ['title', 'describtion', ]
		widgets = {
			'title' : forms.TextInput(
				attrs={
					'class' : 'form-control'
				}
			),
			'describtion' : forms.Textarea(
				attrs={
					'class' : 'form-control'
				}
			),
		}


class PostImageForm(forms.ModelForm):
	class Meta:
		model = PostImages
		fields = ['image', ]
		widgets = {
			'image' : forms.FileInput(
				attrs={
					'class' : 'form-control-file'
				}
			),
		}


class HashtagField(forms.ModelForm):

	class Meta:
		model = Hashtags
		fields = ['tag', ]
		widgets = {
			'tag' : forms.TextInput(
				attrs={
					'class' : 'form-control'
				}
			),
		}


class RatingForm(forms.ModelForm):

	class Meta:
		model = PostRating
		fields = ['rating', ]
		