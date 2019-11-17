from django.contrib import admin
from .models import Post, PostImages, Hashtags, Comments
from .forms import PostImageForm
from django.forms import modelformset_factory

# Register your models here.
class HashtagInline(admin.TabularInline):
	model = Hashtags.post.through
	extra = 3


class PostImagesInline(admin.StackedInline):
	model = PostImages
	extra = 3


class CommentsInline(admin.StackedInline):
	model = Comments 

class PostAdmin(admin.ModelAdmin):
	model = Post
	list_display = ['user', 'title', ]
	readonly_fields = ('timestamp', )
	inlines = [ HashtagInline, PostImagesInline, CommentsInline]



admin.site.register(Post, PostAdmin)
admin.site.register(Hashtags)
admin.site.register(Comments)