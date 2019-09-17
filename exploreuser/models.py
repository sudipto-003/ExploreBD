from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime
from django.db.models.signals import post_save
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
import sys
from datetime import date


# Create your models here.

class ExUser(AbstractUser):
	date_of_birth = models.DateField(blank=False, null=False)

	def __str__(self):
		return self.username

	def full_name(self):
		return self.first_name + " " + self.last_name

	def age(self):
		today = date.today()
		current_age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

		return str(current_age)



class Profile(models.Model):
	user = models.OneToOneField(ExUser, on_delete=models.CASCADE)
	about = models.TextField(default='', blank=True)
	phone = models.CharField(max_length=12, default='', blank=True)
	address = models.CharField(max_length=50, default='', blank=True)
	photo = models.ImageField(upload_to='profile_photos/%Y/%m/%d/', null=True, blank=True)

	def save(self, *args, **kwargs):
		if self.photo:

			img = Image.open(self.photo)
			img = img.resize((350, 350), Image.ANTIALIAS)
			output = BytesIO()

			img.save(output, format='JPEG', quality=90)

			output.seek(0)
			self.photo = InMemoryUploadedFile(output, 'ImageField', "%s.jpg"%self.photo.name, 'image/jpeg',
				sys.getsizeof(output), None)

		super(Profile, self).save(*args, **kwargs)

	def __str__(self):
		return self.user.username



def create_profile(sender, **kwargs):
		user = kwargs['instance']

		if kwargs['created']:
			user_profile = Profile(user=user)
			user_profile.save()

	
post_save.connect(create_profile, sender=ExUser)
