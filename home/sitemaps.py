from django.contrib.sitemaps import Sitemap

from post.models import Category, Course, Post


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Post.objects.filter(status=True)
    
    def lastmod(self, obj):
        return obj.updated_on


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Category.objects.filter(status=True, published=True)
    
    def lastmod(self, obj):
        return obj.updated_on


class CourseSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Course.objects.filter(status=True)
    
    def lastmod(self, obj):
        return obj.updated_on
    
    def location(self, item):
        return f"/course/{item.slug}"

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "weekly"

    def items(self):
        return ('', 'login', 'logout', 'courses', 'contact-us', 'about-us', 'privacy-policy', 'refund-policy', 'term-of-service')

    def location(self, item):
        return f"/{item}"


sitemaps = {
    "static": StaticViewSitemap,
    "category": CategorySitemap,
    "course": CourseSitemap,
    "post": PostSitemap,
}