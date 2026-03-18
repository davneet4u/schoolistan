from django.urls import path
from . import views

urlpatterns = [
    # ========== Dashboard ==========
    path("", views.index),
    path("dashboard", views.dashboard),
    path("login", views.admin_login),
    path("dash-form", views.dash_form),
    path("dash-table", views.dash_table),
    # ========== Post ==========
    path("posts", views.posts),
    path("post-list", views.post_list),
    path("re-order-posts", views.re_order_posts),
    path("category/<int:cat_id>/post-series", views.post_series),
    # ========== Category ==========
    path("categories", views.categories),
    path("category-list", views.category_list),
    path("category/<int:id>/details", views.category_details),
    path("re-order-categories", views.re_order_categories),
    path("category/<int:cat_id>/category-series", views.category_series),
    # ========== user ==========
    path("users", views.users),
    path("user-list", views.user_list),
    path("user/<int:id>/change-role", views.user_change_role),
    # ========== teachers ==========
    path("teachers", views.teachers),
    path("teacher-list", views.teacher_list),
    path("teacher/add", views.teacher_add),
    path("teacher/<int:id>/edit", views.teacher_edit),
    # ========== banners ==========
    path("banners", views.banners),
    path("banner-list", views.banner_list),
    path("banner/add", views.banner_add),
    path("banner/<int:id>/edit", views.banner_edit),
    path("banner/<int:id>/delete", views.banner_delete),
    path('banner-categories/<int:id>', views.banner_categories),
    # ========== courses ==========
    path('category/<int:category_id>/course/add', views.course_add),
    path('course/<int:id>/edit', views.course_edit),
]
