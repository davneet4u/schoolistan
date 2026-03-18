from django.db import models
from acc.models import User

# constants
STATUS = ((False, 'Inactive'), (True, 'Active'))
POST_TYPES = (
    (0, 'Text'),
    (1, 'Image'),
    (2, 'Video'),
    (3, 'Youtube'),
    (4, 'Instagram'),
)


# Create your models here.

class Category(models.Model):
    class Meta:
        db_table = 'categories'
    title = models.CharField(max_length=255, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    status = models.BooleanField(choices=STATUS, default=True)
    parent_id = models.BigIntegerField(null=True)
    premium = models.BooleanField(choices=STATUS, default=False)
    published = models.BooleanField(choices=STATUS, default=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)

    thumbnail = models.ImageField(upload_to='categories/', null=True)
    description = models.TextField(null=True)
    order_no = models.PositiveIntegerField(null=True)

    meta_description = models.CharField(max_length=255, null=True)

    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    page_url = None
    def get_absolute_url(self):
        if self.page_url: return self.page_url

        self.page_url = "/" + self.slug
        cat = self
        while cat.parent_id:
            try:
                cat = Category.objects.get(id=cat.parent_id)
                self.page_url = "/" + cat.slug + self.page_url
            except Category.DoesNotExist:
                break

        self.page_url = "/category" + self.page_url
        return self.page_url


class Course(models.Model):
    class Meta:
        db_table = 'courses'
    category = models.OneToOneField(Category, on_delete=models.CASCADE)
    status = models.BooleanField(choices=STATUS, default=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    teacher_name = models.CharField(max_length=255)
    validity = models.IntegerField(default=0) # validity in days
    price = models.FloatField(default=0) # price in rupees
    old_price = models.FloatField(default=0) # old_price in rupees
    about = models.CharField(max_length=500)

    description = models.TextField(null=True)
    what_included = models.TextField(null=True)
    units = models.JSONField()

    completed_step_no = models.PositiveSmallIntegerField(default=0)

    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    @property
    def about_str_to_html(self):
        return self.about.replace('\n', '<br />')

    @property
    def calc_discount(self):
        return ((self.old_price - self.price) / self.old_price) * 100

    @property
    def calc_discount_amt(self):
        return self.old_price - self.price


class Post(models.Model):
    class Meta:
        db_table = 'posts'
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    text = models.TextField(null=True)
    locked_text = models.TextField(null=True)
    status = models.BooleanField(choices=STATUS, default=True)
    title = models.CharField(max_length=255, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    featured = models.BooleanField(choices=STATUS, default=False)
    premium = models.BooleanField(choices=STATUS, default=False)

    meta_description = models.CharField(max_length=255, null=True)
    transcript = models.TextField(null=True)

    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    page_url = None
    def get_absolute_url(self):
        if self.page_url: return self.page_url

        self.page_url = "/" + self.slug
        post_cat = PostCategory.objects.select_related('category').filter(post_id=self.id).first()
        cat = post_cat.category if post_cat else None
        if cat:
            self.page_url = "/" + cat.slug + self.page_url
            while cat.parent_id:
                try:
                    cat = Category.objects.get(id=cat.parent_id)
                    self.page_url = "/" + cat.slug + self.page_url
                except Category.DoesNotExist:
                    break

        self.page_url = "/post" + self.page_url
        return self.page_url


class PostCategory(models.Model):
    class Meta:
        db_table = 'post_categories'
        unique_together = ('post_id', 'category_id',)
    post = models.ForeignKey(Post, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    post_order_no = models.PositiveIntegerField(null=True)


class PostAttachment(models.Model):
    class Meta:
        db_table = 'post_attachments'
    attachment = models.CharField(max_length=255, null=True)
    type = models.SmallIntegerField(choices=POST_TYPES, default=0)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class PostLike(models.Model):
    class Meta:
        db_table = 'post_likes'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)


class PostComment(models.Model):
    class Meta:
        db_table = 'post_comments'
    comment = models.CharField(max_length=1000, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
