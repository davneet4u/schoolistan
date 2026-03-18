from django.urls import path, re_path
from . import views

urlpatterns = [
    path('create-attachement', views.create_attachement, name="create_attachement"),
    path('post/create', views.post_create, name="post_create"),
    path('posts', views.posts),
    path('post/<int:id>/edit', views.post_edit),
    path('post/<int:id>/delete', views.post_delete),
    path('post-list', views.post_list),
    path('category/create', views.category_create),
    path('category-list', views.category_list),
    path('category-list-group', views.category_list_group),
    path('post/<int:id>/like', views.post_like),
    path('post/<int:id>/comment', views.post_comment),
    path('post/<int:id>/comments', views.comment_list),
    path('<int:id>/get-post-url', views.get_post_url),

    re_path(r'.*', views.post_page),
]
