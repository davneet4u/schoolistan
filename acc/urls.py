from django.urls import path
from . import views

urlpatterns = [
    path('profile', views.profile),
    path('payments', views.payments),
    path('user-categories', views.user_categories),
    path('user/<int:id>/follow', views.user_follow),
    path('update-username', views.update_username),
    path('<str:username>', views.account_page)
]
