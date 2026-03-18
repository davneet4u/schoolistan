from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime


# Create your models here.


# constants
ROLES = (
    (1, 'Super Admin'), (2, 'Staff'), (3, 'Teacher'), (4, 'Student')
)


class User(AbstractUser):
    profile_pic = models.ImageField(upload_to='user_pics/', null=True)
    role = models.SmallIntegerField(default=4, choices=ROLES)
    social_id = models.CharField(max_length=50, unique=True, null=True)
    mobile = models.CharField(max_length=10, null=True)

class UserProfile(models.Model):
    class Meta:
        db_table = 'user_profiles'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.CharField(max_length=500, null=True)
    dob = models.DateField(null=True)

    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

class UserCategory(models.Model):
    class Meta:
        db_table = 'user_categories'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey("post.Category", on_delete=models.CASCADE)

class UserFollowing(models.Model):
    class Meta:
        db_table = 'user_followings'
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow_to_user')
    by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follow_by_user')

    created_on = models.DateTimeField(auto_now_add=True)
