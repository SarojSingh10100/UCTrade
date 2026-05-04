from django.contrib.auth.models import AbstractUser
from django.db import models


# class User(AbstractUser):
#     is_instructor = models.BooleanField(default=False)

#     def __str__(self) -> str:
#         return self.username

# from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_instructor = models.BooleanField(default=False)

    def __str__(self):
        return self.username