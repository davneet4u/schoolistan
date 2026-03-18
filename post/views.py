from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from time import time
from django.contrib.auth.decorators import login_required
from .models import Category, Post, PostAttachment, PostLike, PostComment, PostCategory
from django.contrib import messages
from teachothers.storage_backends import MediaStorage
from django.db import connection
import json, boto3
from django.conf import settings
from django.utils.text import slugify
import itertools
from django.views.decorators.csrf import csrf_exempt
from botocore.client import Config
from datetime import datetime
from zoneinfo import ZoneInfo
from utility.helper import generate_locked_content
from payments.models import CategorySubscription
from utility.constants import LOCKED_POST_PIC
from django.db.models import Q

# Create your views here.
@login_required
def post_create(request):
    if request.method == 'GET':
        return render(request, "post/create-post.html")
    elif request.method == 'POST':

        category_ids = None
        premium = False
        featured = False
        if request.user.role <= 3:
            if request.POST['categories']:
                category_ids = request.POST['categories'].split(',')
            if request.POST['premium'] == '1':
                premium = True
            if request.POST['featured'] == '1':
                featured = True

        title = request.POST['title'].strip() if request.POST['title'] else None
        # ---------- generating slug ----------
        if title:
            slug_candidate = slug_original = slugify(title)
            for i in itertools.count(1):
                if not Post.objects.filter(slug=slug_candidate).exists():
                    break
                slug_candidate = f'{slug_original}-{i}'
        else:
            slug_candidate = f'{request.user.username}-{time()}'
        # -------------------------------------
        text = request.POST['text']
        transcript = request.POST['transcript']
        meta_description = request.POST['meta_description']
        short = Post.objects.create(
            user_id=request.user.id,
            slug=slug_candidate,
            title=title,
            text=text if text else None,
            transcript=transcript if transcript else None,
            meta_description=meta_description if meta_description else None,
            premium=premium,
            featured=featured,
            status=True,
            locked_text = generate_locked_content(text) if premium and text else None
        )
        if category_ids is not None:
            for category_id in category_ids:
                PostCategory.objects.create(post_id=short.id, category_id=category_id)

        # saving youtub
        youtube_link = request.POST['youtube'].strip()
        if youtube_link:
            PostAttachment.objects.create(
                attachment=youtube_link,
                post_id=short.id,
                type=3,
            )

        messages.success(request, 'Post created successfully')
        post_url = short.get_absolute_url()
        return JsonResponse({
            "msg": "Post created successfully",
            "data": {"id": short.id, "post_url": post_url if post_url else "/"}
        }, status=201)
    else:
        return HttpResponse("Method not allowed", status=405)

@csrf_exempt
def create_attachement(request):
    data = json.loads(request.body)
    post_id = data['post_id']
    post_type = data['post_type']
    file_name = data['file_name']
    file_type = data['file_type']
    file_ext = file_name.split('.')[-1]

    file_path = f"posts/user-{request.user.id}/post-{post_id}/{str(time()).replace('.', '_')}.{file_ext}"
    # file_type = f"image/{file_ext}" # file_type = f"video/{file_ext}"
        
    PostAttachment.objects.create(attachment=file_path, post_id=post_id, type=post_type)

    if post_type in (1, 2):
        S3_BUCKET = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client(
            's3', config=Config(signature_version='s3v4'), aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name='ap-south-1'
        )

        presigned_post = s3.generate_presigned_post(
            Bucket = S3_BUCKET,
            Key = f"{settings.AWS_MEDIA_LOCATION}/{file_path}",
            Fields = {"acl": "public-read", "Content-Type": file_type},
            Conditions = [
            {"acl": "public-read"},
            {"Content-Type": file_type}
            ],
            ExpiresIn = 3600
        )
        res_data = {"aws_data": presigned_post, "url": f"{settings.MEDIA_URL}{file_path}"}
    else:
        # res_data = {}
        return JsonResponse({"msg": "Attachement type not supported", "data": {}}, status=400)

    return JsonResponse({"msg": "Attachement uploaded successfully", "data": res_data}, status=201)


def get_category_branch_infos(category_id):
    cat_id = category_id
    cat_branches = []
    while True:
        try:
            parent_id = Category.objects.get(id=cat_id).parent_id
            cat_branches.append(cat_id)
            if parent_id:
                cat_id = parent_id
            else:
                break
        except Category.DoesNotExist:
            break
    cat_branches.reverse()
    return cat_branches


@login_required
def post_edit(request, id):
    post_obj = get_object_or_404(Post, id=id)
    if request.user.role <= 3 or post_obj.user_id == request.user.id:
        if request.method == "GET":
            category_branches = []
            post_cats = PostCategory.objects.filter(post_id=post_obj.id)
            for post_cat in post_cats:
                category_branches.append(get_category_branch_infos(post_cat.category_id))
            context = {
                "images": PostAttachment.objects.filter(post_id=id, type=1),
                "videos": PostAttachment.objects.filter(post_id=id, type=2),
                "youtube": PostAttachment.objects.filter(post_id=id, type=3).first(),
                "post": post_obj,
                "MEDIA_URL": settings.MEDIA_URL,
                "category_branches": category_branches,
            }
            return render(request, "post/create-post.html", context)
        elif request.method == "POST":
            post_obj.text = request.POST["text"]
            post_obj.transcript = request.POST["transcript"]
            post_obj.meta_description = request.POST["meta_description"].strip() if request.POST["meta_description"] else None
            post_obj.title = request.POST["title"].strip()
            if request.user.role <= 3:
                if request.POST['categories']:
                    category_ids = request.POST['categories'].split(',')
                    PostCategory.objects.filter(post_id=post_obj.id).filter(~Q(category_id__in=category_ids)).delete()
                    for category_id in category_ids:
                        if not PostCategory.objects.filter(post_id=post_obj.id, category_id=category_id).exists():
                            PostCategory.objects.create(post_id=post_obj.id, category_id=category_id)
                else:
                    PostCategory.objects.filter(post_id=post_obj.id).delete()
        
                post_obj.premium = True if request.POST['premium'] == '1' else False
                post_obj.featured = True if request.POST['featured'] == '1' else False

            post_obj.locked_text = generate_locked_content(post_obj.text) if post_obj.premium and post_obj.text else None
            post_obj.save()

            youtube_link = request.POST['youtube'].strip()
            if youtube_link:
                try:
                    attach = PostAttachment.objects.get(post_id=id, type=3)
                    attach.attachment = youtube_link
                    attach.save()
                except PostAttachment.DoesNotExist:
                    PostAttachment.objects.create(
                        attachment=youtube_link,
                        post_id=id,
                        type=3,
                    )
            else:
                PostAttachment.objects.filter(post_id=id, type=3).delete()

            # removing images
            if int(request.POST['image_count']) > 0:
                imgattch = PostAttachment.objects.filter(post_id=id, type=1)
                for i in imgattch:
                    MediaStorage().delete(i.attachment)
                PostAttachment.objects.filter(post_id=id, type=1).delete()
            
            # removing videos
            if int(request.POST['video_count']) > 0:
                videoss = PostAttachment.objects.filter(post_id=id, type=2)
                for i in videoss:
                    MediaStorage().delete(i.attachment)
                PostAttachment.objects.filter(post_id=id, type=2).delete()
            
            messages.success(request, 'Post updated successfully')
            post_url = post_obj.get_absolute_url()
            return JsonResponse({
                "msg": "Post updated successfully",
                "data": {"id": post_obj.id, "post_url": post_url if post_url else "/"}
            }, status=201)
        else:
            return HttpResponse("Method not allowed", status=405)
    else:
        return HttpResponse("Access denied", status=401)


@login_required
def post_delete(request, id):
    post_obj = get_object_or_404(Post, id=id)
    if request.method == "POST":
        if request.user.role == 3 or post_obj.user_id == request.user.id:
            attaches = PostAttachment.objects.filter(post_id=post_obj.id)
            for attach in attaches:
                if attach.type == 1 or attach.type == 2:
                    MediaStorage().delete(attach.attachment)
            PostAttachment.objects.filter(post_id=post_obj.id).delete()

            PostLike.objects.filter(post_id=post_obj.id).delete()
            PostComment.objects.filter(post_id=post_obj.id).delete()
            PostCategory.objects.filter(post_id=post_obj.id).delete()

            post_obj.delete()
            return JsonResponse({"msg": "Post deleted successfully", "data": {}})
        else:
            return JsonResponse({"msg": "Access denied", "data": {}}, status=401)
    else:
        return JsonResponse({"msg": "Method not allowed", "data": {}}, status=405)


@login_required
def posts(request):
    return render(request, "post/shorts.html")


def post_list(request):
    condition = ''
    if 'category_id' in request.GET and request.GET['category_id'] != '':
        condition += f" AND pc.category_id={request.GET['category_id']}"

    if 'category_ids' in request.GET and request.GET['category_ids'] != '':
        condition += f" AND pc.category_id IN (SELECT id FROM categories WHERE id IN({request.GET['category_ids']}) OR parent_id IN ({request.GET['category_ids']}))"

    if 'user_id' in request.GET and request.GET['user_id'] != '':
        condition += f" AND p.user_id={request.GET['user_id']}"

    if 'featured' in request.GET and int(request.GET['featured']) == 1:
        condition += f" AND p.featured=true"

    if 'existing_ids' in request.GET and request.GET['existing_ids'] != '':
        condition += f" AND p.id NOT IN ({request.GET['existing_ids']})"

    if 'asc_order' in request.GET and request.GET['asc_order'] == '1':
        order_by = 'ORDER BY pc.post_order_no ASC, p.id ASC'
    else:
        order_by = 'ORDER BY p.id DESC'

    if request.user.is_authenticated:
        curr_user_id = request.user.id
        moderator = request.user.role in (1, 2, 3)
    else:
        curr_user_id = 0
        moderator = False

    curr_date = datetime.now(tz=ZoneInfo('Asia/Kolkata')).date()

    with connection.cursor() as cursor:
        parent_cat_query = "id=0"
        if curr_user_id != 0:
            # ---------------
            cursor.execute(f"SELECT category_id FROM category_subscriptions WHERE user_id={curr_user_id} AND end_date >= '{curr_date}'")
            rows = cursor.fetchall()
            parent_cat_str = ''
            first_row = True
            for row in rows:
                if first_row:
                    parent_cat_str += f"{row[0]}"
                    first_row = False
                else:
                    parent_cat_str += f",{row[0]}"
            # ---------------
            if parent_cat_str:
                parent_cat_query = f"id IN ({parent_cat_str}) OR parent_id IN ({parent_cat_str})"

        cursor.execute(
            f"""SELECT p.id, p.text, p.title, u.username, p.created_on, u.id AS user_id, p.premium, p.featured,
            (select count(id) from post_likes where post_id=p.id) as likes,
            (select count(id) from post_likes where post_id=p.id and user_id={curr_user_id} limit 1) as liked,
            (select count(id) from post_comments where post_id=p.id) as comments, p.slug, cs.subscribed, p.locked_text,
            p.transcript FROM posts p LEFT JOIN post_categories pc ON p.id=pc.post_id LEFT JOIN acc_user u ON p.user_id=u.id LEFT JOIN 
            (SELECT id, true AS subscribed FROM categories WHERE {parent_cat_query}) cs ON pc.category_id=cs.id
            WHERE p.status=true {condition} {order_by} LIMIT 20;""")
        # columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        data = []
        for row in rows:
            premium = row[6]
            subscribed = row[12]

            attach = []
            locked = False
            cursor.execute(
                f"SELECT attachment, type FROM post_attachments WHERE post_id={row[0]} ORDER BY id ASC;"
            )
            attach_rows = cursor.fetchall()
            if premium and not subscribed and not moderator:
                locked = True
                post_text = row[13]
                
                first_row = True
                for attach_row in attach_rows:
                    if first_row:
                        first_row = False
                        attach.append({"attachment": attach_row[0], "type": attach_row[1]})
                    else:
                        attach.append({"attachment": LOCKED_POST_PIC, "type": 1})
            else:
                post_text = row[1]
                for attach_row in attach_rows:
                    attach.append({"attachment": attach_row[0], "type": attach_row[1]})

            data.append({
                "id": row[0], "text": post_text,
                "title": row[2], "username": row[3], "created_on": row[4], "attachments": attach,
                "user_id": row[5], "premium": premium, "featured": row[7],
                "likes": row[8], "liked": row[9], "comments": row[10], "slug": row[11], "locked": locked,
                "transcript": row[14]
            })
    return JsonResponse({"msg": "success", "data": data})


@login_required
def category_create(request):
    data = json.loads(request.body)
    title = data['category_title'].strip()

    if not title:
        return JsonResponse({"msg": "title can't be empty"}, status=400)
    
    # ---------- generating slug ----------
    slug_candidate = slug_original = slugify(title)
    for i in itertools.count(1):
        if not Category.objects.filter(slug=slug_candidate).exists():
            break
        slug_candidate = f'{slug_original}-{i}'
    # -------------------------------------

    cat = Category.objects.create(
        status=True, title=title, slug=slug_candidate,
        parent_id=data['parent_id'] if data['parent_id'] else None,
        user_id=request.user.id
    )
    return JsonResponse({"msg": "success", "data": {'category_id': cat.id}})


@login_required
def category_list(request):
    if 'parent_id' in request.GET and request.GET['parent_id']:
        parent_filter = f"parent_id={request.GET['parent_id']}"
    else:
        parent_filter = f"parent_id IS NULL"

    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT id, title, parent_id FROM categories WHERE {parent_filter} AND status=true ORDER BY order_no ASC, id ASC;")
        # columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": rows})


@login_required
def category_list_group(request):
    if 'parent_id' in request.GET and request.GET['parent_id']:
        parent_filter = f"parent_id={request.GET['parent_id']}"
    else:
        parent_filter = f"parent_id IS NULL"

    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT id, title, parent_id FROM categories WHERE {parent_filter} AND status=true ORDER BY id ASC;")
        # columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": rows})


@login_required
def post_like(request, id):
    if request.method == "POST":
        dd = json.loads(request.body)
        if dd['liked'] > 0:
            PostLike.objects.filter(
                user_id=request.user.id, post_id=id).delete()
            likecount = PostLike.objects.filter(post_id=id).count()
            return JsonResponse({"msg": "Unliked successfully", "data": {"count": likecount, "liked": False}})
        else:
            try:
                PostLike.objects.get(user_id=request.user.id, post_id=id)
                return JsonResponse({"msg": "Post already liked", "data": {}}, status=409)
            except PostLike.DoesNotExist:
                PostLike.objects.create(
                    user_id=request.user.id,
                    post_id=id
                )
                likecount = PostLike.objects.filter(post_id=id).count()
                return JsonResponse({"msg": "Liked successfully", "data": {"count": likecount, "liked": True}})
    else:
        return HttpResponse("Method not allowed", status=405)


@login_required
def post_comment(request, id):
    if request.method == "POST":
        dd = json.loads(request.body)

        PostComment.objects.create(
            user_id=request.user.id,
            post_id=id,
            comment=dd["comment"].strip()
        )
        comcount = PostComment.objects.filter(post_id=id).count()
        return JsonResponse({"msg": "comments successfully", "data": {"count": comcount}})
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def comment_list(request, id):
    with connection.cursor() as cursor:
        cursor.execute(
            f"""Select c.id, c.comment, c.created_on, u.username  From post_comments c left join acc_user u on c.user_id=u.id
            Where c.post_id = {id} ORDER BY id DESC""")
        # columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "comments successfully", "data": {"comments": rows}})


def get_post_url(request, id):
    post_url = get_object_or_404(Post, id=id).get_absolute_url()
    if post_url:
        return JsonResponse({"msg": "Success", "data": {"post_url": post_url}})
    else: 
        return JsonResponse({"msg": "Something went wrong."}, status=500)


def post_page(request):
    curr_user_id = request.user.id if request.user.is_authenticated else 0
    path_info = request.path_info.rstrip('/')
    cat_slugs = path_info[6:].split("/")
    post_slug = cat_slugs.pop()
    old_cat_id = None
    cat_branches = []
    cat = None
    for cat_slug in cat_slugs:
        try:
            cat = Category.objects.get(slug=cat_slug, status=True)
            if old_cat_id is not None and cat.parent_id != old_cat_id:
                raise Http404
            old_cat_id = cat.id
            cat_branches.append(cat)
        except Category.DoesNotExist:
            raise Http404
    
    if cat_branches and cat_branches[0].parent_id is not None:
        raise Http404
    post_obj = get_object_or_404(Post, slug=post_slug)
    if cat:
        if not PostCategory.objects.filter(post_id=post_obj.id, category_id=cat.id).exists():
            raise Http404
    else:
        if PostCategory.objects.filter(post_id=post_obj.id).exists(): raise Http404

    pattach = PostAttachment.objects.filter(post_id=post_obj.id)
    likecount = PostLike.objects.filter(post_id=post_obj.id).count()
    comcount = PostComment.objects.filter(post_id=post_obj.id).count()
    if curr_user_id != 0:
        liked = 1 if PostLike.objects.filter(post_id=post_obj.id, user_id=curr_user_id).exists() else 0
    else:
        liked = 0

    if post_obj.premium:
        if curr_user_id != 0 and cat:
            curr_date = datetime.now(tz=ZoneInfo('Asia/Kolkata')).date()
            cat_subs = CategorySubscription.objects.filter(
                user_id=curr_user_id, end_date__gte=curr_date,
                category_id__in=get_category_branch_infos(cat.id)
            ).exists()
            locked = False if cat_subs else True
        else: locked = True
    else: locked = False
    return render(request, "post/post-link.html", {
        "MEDIA_URL": settings.MEDIA_URL, "post": post_obj, "pattach": pattach, "likecount": likecount,
        "comcount": comcount, "liked": liked, "grid_columm": len(pattach) * ' 100%', "locked": locked,
        "LOCKED_POST_PIC": LOCKED_POST_PIC, "curr_user_id": curr_user_id
    })
