from django.db import models
from exploreuser.models import ExUser
from django.template.defaultfilters import slugify
from datetime import datetime, timezone

# Create your models here.
class Post(models.Model):
	user = models.ForeignKey(ExUser, on_delete=models.CASCADE)
	title = models.CharField(max_length=50)
	describtion = models.TextField()
	timestamp = models.DateTimeField(auto_now=True)


def get_image_path(instance, filename):
	user = instance.post.user
	title = instance.post.title
	slug = slugify(title)

	return "post_images/%s/%s-%s"%(user, slug, filename)


class PostImages(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, default=None)
	image = models.ImageField(upload_to=get_image_path, verbose_name='Image')


class Hashtags(models.Model):
	tag = models.CharField(max_length=32, unique=True)
	post = models.ManyToManyField(Post)


class Comments(models.Model):
	user = models.ForeignKey(ExUser, on_delete=models.CASCADE)
	text = models.CharField(max_length=200)
	on_post = models.ForeignKey(Post, on_delete=models.CASCADE)
	added_time = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		ordering = ['added_time']

	def diff_time(self):
		now = datetime.now(timezone.utc)
		diff = now - self.added_time
		diff_in_sec = diff.total_seconds()

		if diff_in_sec < 60:
			td = 'Just now'
		elif diff_in_sec >= 60 and diff_in_sec < 3600:
			minute = divmod(diff_in_sec, 60)[0]

			if minute > 1:
				td = '%d minutes ago'%(minute)
			else:
				td = '1 minute ago'

		elif diff_in_sec >= 3600 and diff_in_sec < 86400:
			hours = divmod(diff_in_sec, 3600)[0]

			if hours > 1:
				td = '%d hours ago'%(hours)
			else:
				td = '1 hour ago'

		elif diff_in_sec >= 86400 and diff_in_sec < 604800:
			days = divmod(diff_in_sec, 86400)[0]

			if days > 1:
				td = '%d days ago'%(days)
			else:
				td = '1 day ago'

		else:
			td = self.added_time.strftime('%d %b, %Y')

		return td


class PostRating(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	user = models.ForeignKey(ExUser, on_delete=models.CASCADE)
	rating = models.IntegerField(null=True)
		

class PostHit(models.Model):
	max_permitted_hit = 20
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	hits = models.IntegerField(default=0)
	user = models.ForeignKey(ExUser, on_delete=models.CASCADE)
	last_viewed = models.DateTimeField(auto_now=True)