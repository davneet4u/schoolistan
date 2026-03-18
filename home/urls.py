from django.contrib.sitemaps.views import index as sitemaps_index
from django.contrib.sitemaps.views import sitemap as sitemaps_sitemap
from .sitemaps import sitemaps

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('login', views.auth_login),
    path('logout', views.auth_log_out),
    path('courses', views.courses),
    path('course/<str:slug>', views.course_page),
    path('banner-list', views.banner_list),
    path('contact-us', views.contact_us),
    path('about-us', views.about_us),
    path('privacy-policy', views.privacy_policy),
    path('refund-policy', views.refund_policy),
    path('term-of-service', views.term_of_service),

    # sitemaps
    path(
        "sitemap.xml",
        sitemaps_index,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.index",
    ),
    path(
        "sitemap-<section>.xml",
        sitemaps_sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]
