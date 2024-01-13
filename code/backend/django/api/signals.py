from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Users

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	try:
		if created:
			Users.objects.create(user=instance)
	except Exception as e:
		print('error creating user profile')
		print(str(e))

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	try:
		instance.users.save()
	except Exception as e:
		print('error saving user profile')
		print(str(e))