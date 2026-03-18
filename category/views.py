from django.shortcuts import render
from django.http import HttpResponse, Http404
from payments.models import CategorySubscription
from post.models import Category
from datetime import datetime
from zoneinfo import ZoneInfo
from django.contrib.auth.decorators import login_required
from django.conf import settings


# Create your views here.
def category_page(request):
    path_info = request.path_info.rstrip('/')
    cat_slugs = path_info[10:].split("/")
    old_cat_id = None
    breadcrum = '<a href="/"><i class="fa-solid fa-house"></i> Home</a>'
    temp_path = '/category'
    cat_branches = []
    for cat_slug in cat_slugs:
        try:
            cat = Category.objects.get(slug=cat_slug, status=True)
            if old_cat_id is not None and cat.parent_id != old_cat_id:
                raise Http404
            old_cat_id = cat.id
            cat_branches.append(cat)
            temp_path += f'/{cat_slug}'
            breadcrum += f' <i class="fa-solid fa-arrow-right"></i> <a href="{temp_path}">{cat.title}</a>'
        except Category.DoesNotExist:
            raise Http404
    
    if request.user.is_authenticated:
        curr_user_id = request.user.id
        curr_user_role = request.user.role
    else:
        curr_user_id = 0
        curr_user_role = 0

    if not cat.published and curr_user_id != cat.user_id and curr_user_role != 1:
        return HttpResponse("This page is running under maintenance")

    if cat_branches[0].parent_id is not None: raise Http404
    premium_cat = cat_branches[1] if len(cat_branches) > 1 else None

    curr_date = datetime.now(tz=ZoneInfo('Asia/Kolkata')).date()

    subscribed = False
    if premium_cat is not None and curr_user_id != 0:
        subscribed = CategorySubscription.objects.filter(
            category_id=premium_cat.id, user_id=curr_user_id, end_date__gte=curr_date
        ).exists()

    if curr_user_role == 1:
        categories = Category.objects.filter(parent_id=cat.id, status=True).order_by('order_no', 'id')
    else:
        categories = Category.objects.filter(parent_id=cat.id, status=True, published=True).order_by('order_no', 'id')
        categories = Category.objects.raw(f"SELECT * FROM categories WHERE parent_id={cat.id} AND status=true AND (published=true or user_id={curr_user_id}) ORDER BY order_no ASC, id ASC")

    return render(request, "category/category-page.html", {
        "categories": categories, "category": cat, "premium_cat": premium_cat,
        "MEDIA_URL": settings.MEDIA_URL, "breadcrum": breadcrum, "subscribed": subscribed,
        "path_info": path_info, "curr_user_id": curr_user_id
    })

