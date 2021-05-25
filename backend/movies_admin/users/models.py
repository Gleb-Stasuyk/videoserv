from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    class ROLE_CHOICES(models.TextChoices):
        USER = 'user',
        MODERATOR = 'moderator',
        ADMIN = 'admin',

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE, )
    birth_date = models.DateTimeField()
    role = models.CharField(max_length=20,
                            choices=ROLE_CHOICES.choices,
                            default=ROLE_CHOICES.USER)
