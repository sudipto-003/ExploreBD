from django.db import models
from exploreuser.models import ExUser
from django.template.defaultfilters import slugify

# Create your models here.
class Post(models.Model):
	user = models.ForeignKey(ExUser, on_delete=models.CASCADE)
	title = models.CharField(max_length=50)
	describtion = models.TextField()
	timestamp = models.DateTimeField(auto_now=True)


def get_image_path(instance, filename):
	user = instance.post.user
	title = instance.post.title
	slig = slugify(title)

	return "post_images/%s/%s-%s"%(user, slug, filename)


class PostImages(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, default=None)
	image = models.ImageField(upload_to=get_image_path, verbose_name='Image')


class Hashtags(models.Model):
	tag = models.CharField(max_length=32, unique=True)
	post = models.ManyToManyField(Post)
		