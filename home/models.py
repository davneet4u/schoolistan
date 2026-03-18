from django.db import models
from post.models import Category


# constants
STATUS = ((False, 'Inactive'), (True, 'Active'))

# Create your models here.

class ContactUs(models.Model):
    class Meta:
        db_table = 'contact_us_forms'
    name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=10)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name}({self.email})"

class Banner(models.Model):
    class Meta:
        db_table = 'banners'
    title = models.CharField(max_length=255)
    url = models.URLField()
    poster = models.ImageField(upload_to='banners/')
    status = models.BooleanField(choices=STATUS, default=True)
    
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name}({self.email})"


class BannerCategory(models.Model):
    class Meta:
        db_table = 'banner_categories'
    banner = models.ForeignKey(Banner, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
