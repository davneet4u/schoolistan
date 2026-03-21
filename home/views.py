from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, JsonResponse
from acc.models import User
from django.contrib import messages
from django.contrib.auth import login, logout
import json
from google.oauth2 import id_token
from google.auth.transport import requests
from utility.helper import gen_random_str
from post.models import Category, Course
from django.conf import settings
from .models import ContactUs
from django.db import connection
import sentry_sdk


# Create your views here.


# @login_required
def index(request):
    if request.user.is_authenticated:
        user_cat_ids = user_cats = []
        user_cats_str = None

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT category_id FROM user_categories WHERE user_id={request.user.id}")
            rows = cursor.fetchall()
            for row in rows:
                user_cat_ids.append(str(row[0])) # converting to string for requirements. if no need then do not do conversion
        
        if user_cat_ids:
            user_cats_str = ",".join(user_cat_ids)
            parent_table = f"""SELECT * FROM categories WHERE id IN (SELECT parent_id FROM
                categories WHERE parent_id IS NOT NULL AND id IN ({user_cats_str}))"""
            user_cats = Category.objects.raw(
                f"""SELECT cat.*, p_cat.slug as p_slug FROM categories cat LEFT JOIN
                ({parent_table}) p_cat ON cat.parent_id=p_cat.id
                WHERE cat.status=true AND cat.id IN ({user_cats_str}) ORDER BY id ASC"""
            )
        return render(request, "home/user-page.html", {
            "MEDIA_URL": settings.MEDIA_URL, "user_cats": user_cats, "user_cats_str": user_cats_str
        })
    else:
        cats = Category.objects.raw(
            f"""SELECT cat.*, p_cat.slug as p_slug FROM categories cat INNER JOIN
            (SELECT id, slug FROM categories WHERE parent_id IS NULL AND status=true) p_cat
            ON cat.parent_id=p_cat.id WHERE cat.status=true"""
        )
        return render(request, "home/index.html", {"G_CLIENT_ID": settings.GOOGLE_LOGIN_CLIENT_ID, "categories": cats})


def auth_login(request):
    if request.method == "GET":

        if request.user.is_authenticated:
            return redirect('/')

        # response = render(request, "home/login.html")
        # if request.COOKIES.get('g_state') is not None:
        #     response.delete_cookie('g_state')
        # return response

        return render(request, "home/login.html", {'G_CLIENT_ID': settings.GOOGLE_LOGIN_CLIENT_ID})
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(
                data['credential'], requests.Request(), settings.GOOGLE_LOGIN_CLIENT_ID)

            # Or, if multiple clients access the backend server:
            # idinfo = id_token.verify_oauth2_token(token, requests.Request())
            # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
            #     raise ValueError('Could not verify audience.')

            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #     raise ValueError('Wrong hosted domain.')

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            # userid = idinfo['sub']
        except ValueError as exc:
            sentry_sdk.capture_exception(exc)
            # Invalid token
            return JsonResponse({"msg": "Invalid google token"}, status=400)

        try:
            user = User.objects.get(social_id="G-" + idinfo['sub'])
        except User.DoesNotExist:
            user = User.objects.create_user(
                social_id="G-" + idinfo['sub'],
                username=idinfo['email'].split('@')[0],
                email=idinfo['email'],
                first_name=idinfo['given_name'],
                last_name=idinfo['family_name'],
                password=gen_random_str()
            )

        login(request, user)
        return JsonResponse({"msg": "Logged in successfully."})


def auth_log_out(request):
    logout(request)
    return redirect("/login")


def courses(request):
    courses = Course.objects.raw(
        "SELECT * FROM courses WHERE status=true AND category_id IN (SELECT id FROM categories WHERE status=true)"
    )
    return render(request, "home/courses.html", {"courses": courses})

def course_page(request, slug):
    try:
        course = Course.objects.select_related("category").get(slug=slug)
        category = course.category
        if not course.status or not category.status:
            return HttpResponse("Sorry. This course may pe on hold temporary basis or permanent.")
        return render(request, "home/course-page.html", {"course": course})
    except Course.DoesNotExist:
        raise Http404


def banner_list(request):
    condition = ''
    if 'category_id' in request.GET and request.GET['category_id'] != '':
        condition += f" AND id IN (SELECT DISTINCT(banner_id) FROM banner_categories WHERE category_id={request.GET['category_id']})"

    if 'category_ids' in request.GET and request.GET['category_ids'] != '':
        condition += f" AND id IN (SELECT DISTINCT(banner_id) FROM banner_categories WHERE category_id IN ({request.GET['category_ids']}))"

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT id, title, url, poster FROM banners WHERE status=true {condition} ORDER BY id DESC LIMIT 10")
        # columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"banners": rows}})

def contact_us(request):
    if request.method == 'GET':
        return render(request, "home/contact-us.html")
    elif request.method == 'POST':
        ContactUs.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            mobile=request.POST['mobile'],
            subject=request.POST['subject'],
            message=request.POST['message']
        )
        messages.success(request, "Contact form sumitted successfully. Admin will contact you soon.")
        return redirect('/')
    else:
        return HttpResponse("Method not allowed", status=405)

def about_us(request):
    return render(request, "home/about-us.html")

def privacy_policy(request):
    return render(request, "home/privacy-policy.html")

def refund_policy(request):
    return render(request, "home/refund-policy.html")

def term_of_service(request):
    return render(request, "home/term-of-service.html")
