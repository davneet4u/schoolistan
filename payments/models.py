from django.db import models
from acc.models import User
from post.models import Category, Course

# global variables
TXN_STATUS = ((0, 'PENDING'), (1, 'TXN_SUCCESS'), (2, 'TXN_FAILURE'), (3, 'USER_DROPPED'))
TXN_STATUS_DICT = {0: 'PENDING', 1: 'TXN_SUCCESS', 2: 'TXN_FAILURE', 3: 'USER_DROPPED'}

# Create your models here.
class Payment(models.Model):
    class Meta:
        db_table = 'payments'
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.SmallIntegerField(choices=TXN_STATUS, default=0)
    amount = models.FloatField()
    cf_order_id = models.CharField(max_length=255, null=True)
    cf_payment_id = models.CharField(max_length=255, null=True)
    order_id = models.CharField(max_length=255, null=True)
    payment_session_id = models.CharField(max_length=255, null=True)
    order_note = models.CharField(max_length=255, null=True)
    # product infos
    product_type = models.CharField(max_length=255)
    # times
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    @property
    def status_str(self):
        try:
            return TXN_STATUS_DICT[self.status]
        except KeyError:
            return "NA"
    
    @property
    def receipt_no(self):
        return f"{self.id}".zfill(5)


class PaymentCategoryItem(models.Model):
    class Meta:
        db_table = 'payment_category_items'
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=255, null=True)
    status = models.SmallIntegerField(choices=TXN_STATUS, default=0)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, null=True)
    validity = models.IntegerField(default=0) # validity in days
    amount = models.FloatField(default=0) # price in rupees

    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

class CategorySubscription(models.Model):
    class Meta:
        db_table = 'category_subscriptions'
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    payment_category_item = models.ForeignKey(PaymentCategoryItem, on_delete=models.PROTECT)

    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

