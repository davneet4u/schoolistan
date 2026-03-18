from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from acc.models import User, UserProfile, UserCategory, UserFollowing
from post.models import Post
from django.conf import settings
from payments.models import CategorySubscription, Payment
import json
from django.db import connection
from django.contrib import messages
from teachothers.storage_backends import MediaStorage
from django.core.files.base import ContentFile
import base64
from time import time


# Create your views here.
@login_required
def profile(request):
    try:
        user_profile = UserProfile.objects.get(user_id=request.user.id)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user_id=request.user.id)

    if request.method == "GET":
        dob = user_profile.dob.strftime("%Y-%m-%d") if user_profile.dob else ""
        return render(request, "acc/profile.html", {"dob": dob, "profile": user_profile})
    elif request.method == "POST":
        if len(request.POST["mobile"]) != 10:
            messages.error(request, 'Please enter a valid mobile number to save profile.')
            return redirect("/account/profile")
        
        request.user.first_name = request.POST["fname"]
        request.user.last_name = request.POST["lname"]
        request.user.mobile = request.POST["mobile"]
        user_profile.dob = request.POST["birthday"] if request.POST["birthday"] else None
        user_profile.about = request.POST["about"]
        user_profile.save()

        profile_pic_src_data = request.POST["profile_pic_src_data"]
        if profile_pic_src_data != "no_change":
            if request.user.profile_pic:
                MediaStorage().delete(str(request.user.profile_pic))
            request.user.profile_pic = None

            if profile_pic_src_data != "":
                format, imgstr = profile_pic_src_data.split(';base64,')
                ext = format.split('/')[-1]
                filename = f"user-{request.user.id}-{str(time()).replace('.', '_')}.{ext}"
                request.user.profile_pic = ContentFile(base64.b64decode(imgstr), name=filename)       

        request.user.save()
        messages.success(request, 'Profile saved successfully.')

        if 'next' in request.GET and request.GET['next']:
            return redirect(request.GET['next'])
        return redirect("/account/profile")
    else:
        return HttpResponse("Method not allowed", status=405)

@login_required
def update_username(request):
    if request.method == "POST":
        username = json.loads(request.body)['username']
        if request.user.username == username:
            return JsonResponse({"msg": f"You have already this username."}, status=409)
        else:
            if User.objects.filter(username=username).exists():
                return JsonResponse({"msg": "This username already taken."}, status=409)
            else:
                request.user.username = username
                request.user.save()
                messages.success(request, 'Username updated successfully.')
                return JsonResponse({"msg": "Username updated successfully."})
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)

@login_required
def payments(request):
    payments = Payment.objects.filter(user_id=request.user.id).order_by('-id')
    subscriptions = CategorySubscription.objects.select_related('category').filter(user_id=request.user.id).order_by('-id')
    return render(request, "acc/my-payments.html", {"payments": payments, "subscriptions": subscriptions})

@login_required
def user_categories(request):
    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT id, title, parent_id FROM categories WHERE status=true AND parent_id IN
                (SELECT id FROM categories WHERE status=true AND parent_id IS NULL) ORDER BY id ASC
            """)
            # columns = [col[0] for col in cursor.description]
            sub_cats = cursor.fetchall()
            cursor.execute(f"""
                SELECT id, title FROM categories WHERE status=true AND parent_id IS NULL
                ORDER BY id ASC
            """)
            parent_cats = cursor.fetchall()
        
        user_cats = []
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT category_id FROM user_categories WHERE user_id={request.user.id}")
            rows = cursor.fetchall()
            for row in rows:
                user_cats.append(row[0])
        
        return JsonResponse({
            "msg": "Success",
            "data": {
                "parent_categories": parent_cats, "sub_categories": sub_cats,
                "user_categories" : user_cats
            }
        })
    elif request.method == 'POST':
        data = json.loads(request.body)
        cats_str = data['user_categories'].strip()
        if cats_str:
            categories = cats_str.split(',')
            cat_query = f"AND category_id NOT IN ({cats_str})"
        else:
            categories = []
            cat_query = ""
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM user_categories WHERE user_id={request.user.id} {cat_query}")
        for cat_id in categories:
            if not UserCategory.objects.filter(user_id=request.user.id, category_id=cat_id).exists():
                UserCategory.objects.create(user_id=request.user.id, category_id=cat_id)

        return JsonResponse({"msg": "updated successfully", "data": {}})
    else:
        return HttpResponse("Method not allowed", status=405)

@login_required
def user_follow(request, id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=id)
            data = json.loads(request.body)
            if data['follow']:
                if not UserFollowing.objects.filter(to_user_id=id, by_user_id=request.user.id).exists():
                    UserFollowing.objects.create(to_user_id=id, by_user_id=request.user.id)
                messages.success(request, f"You are now started following '{user.first_name} {user.last_name}'.")
                return JsonResponse({"msg": "Success", "data": {}})
            else:
                UserFollowing.objects.filter(to_user_id=id, by_user_id=request.user.id).delete()
                messages.success(request, f"You have unfollowed '{user.first_name} {user.last_name}'.")
                return JsonResponse({"msg": "Success", "data": {}})
        except User.DoesNotExist:
            return JsonResponse({"msg": "User does not exits."}, status=401)
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def account_page(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        curr_user = request.user
        follow_status = UserFollowing.objects.filter(to_user_id=user.id, by_user_id=curr_user.id).exists()
    else:
        curr_user = None
        follow_status = False
    try:
        user_profile = UserProfile.objects.get(user_id=user.id)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user_id=user.id)
    return render(request, "acc/account-page.html", {
        "user": user, "MEDIA_URL": settings.MEDIA_URL, "curr_user": curr_user, "profile": user_profile,
        "post_count": Post.objects.filter(user_id=user.id).count(),
        "followers": UserFollowing.objects.filter(to_user_id=user.id).count(),
        "followings": UserFollowing.objects.filter(by_user_id=user.id).count(),
        "follow_status": follow_status
    })

