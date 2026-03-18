from django.urls import path
from . import views
urlpatterns = [
    path('create-order', views.create_order),
    path('success', views.payment_success),
    path('razorpay-post-data-webhook', views.razorpay_webhook),
    path('cashfree-webhook-success', views.cashfree_webhook_success),
    path('cashfree-webhook-failed', views.cashfree_webhook_failed),
    path('cashfree-webhook-user-dropped', views.cashfree_webhook_user_dropped),
    path('course/<int:course_id>/paynow', views.course_paynow),
    path('fee-receipt/<int:payment_id>', views.fee_receipt),
]
