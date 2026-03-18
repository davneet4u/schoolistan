from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, Http404
from django.contrib import messages
from home.models import Banner, BannerCategory
from post.models import Category, Course, Post, PostCategory
from django.db import connection
from django.contrib.auth import login, authenticate
from utility.decorators import admin_required, staff_required, teacher_required
from django.core.files.base import ContentFile
import base64
from time import time
from acc.models import User
import json
from teachothers.storage_backends import MediaStorage
from .helpers import check_cat_premium_allowed

from django.utils.text import slugify
import itertools



# Create your views here.

# ========================Dashboard==================================
@teacher_required
def index(request):
    return redirect('/admin/dashboard')


@teacher_required
def dashboard(request):
    context = {
        "students": User.objects.filter(role=4).count(),
        "staffs": User.objects.filter(role=2).count(),
        "teachers": User.objects.filter(role=4).count()
    }
    return render(request, "admin-panel/ad-dashboard.html", context)


def admin_login(request):
    if request.method == 'GET':
        try:
            query = '?next=' + request.GET['next']
        except:
            query = ''
        return render(request, 'admin-panel/ad-login.html', {'query': query})
    elif request.method == 'POST':
        try:
            next = request.GET['next']
        except:
            next = '/admin/dashboard'
        uname = request.POST['username']
        pwd = request.POST['password']

        user = authenticate(request, username=uname, password=pwd)
        if user:
            login(request, user)
            messages.success(request, 'Login successfully.')
            return redirect(next)
        else:
            path = request.path + ('' if next == '/' else '?next=' + next)
            messages.error(request, 'Incorrect username or password.')
            return redirect(path)
    else:
        raise Http404


def dash_form(request):
    return render(request, "admin-panel/dashboard-form.html")


def dash_table(request):
    return render(request, "admin-panel/dashboard-table.html")

# ========================Category==================================


@teacher_required
def categories(request):
    return render(request, "admin-panel/category-list.html")


@teacher_required
def category_list(request):
    if 'parent_id' in request.GET and request.GET['parent_id']:
        parent_filter = f"parent_id={request.GET['parent_id']}"
    else:
        parent_filter = f"parent_id IS NULL"

    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT id, title, parent_id, status FROM categories WHERE {parent_filter} ORDER BY order_no ASC, id ASC;")
        # columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "Success", "data": rows})

@teacher_required
def category_details(request, id):

    cat = get_object_or_404(Category, id=id)
    premium_allowed = check_cat_premium_allowed(cat)
    course_id = None
    if premium_allowed:
        course_obj = Course.objects.filter(category_id=cat.id).first()
        if course_obj: course_id = course_obj.id

    if request.method == 'GET':
        return JsonResponse({
            "msg": "Success",
            "data": {
                "id": cat.id, "premium": cat.premium, "status": cat.status, "parent_id": cat.parent_id,
                "premium_allowed": premium_allowed, "course_id": course_id, "description": cat.description,
                "thumbnail": cat.thumbnail.url if cat.thumbnail else None, "meta_description": cat.meta_description,
                "published": cat.published
            }
        })

    elif request.method == 'POST':
        data = json.loads(request.body)
        cat.status = data['status']
        cat.description = data['description']
        cat.meta_description = data['meta_description']
        cat.published = data['published']

        if premium_allowed:
            cat.premium = data['premium']
        else:
            cat.premium = False

        thumbnail_src_data = data["thumbnail_src_data"]

        if thumbnail_src_data != "no_change":
            if cat.thumbnail:
                MediaStorage().delete(str(cat.thumbnail))
            cat.thumbnail = None

            if thumbnail_src_data != "":
                format, imgstr = thumbnail_src_data.split(';base64,')
                ext = format.split('/')[-1]
                filename = f"cat-{cat.id}-{str(time()).replace('.', '_')}.{ext}"
                cat.thumbnail = ContentFile(base64.b64decode(imgstr), name=filename)       

        cat.save()
        return JsonResponse({"msg": "Category updated successfully.", "data": {"id": cat.id}})
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)
    

@teacher_required
def re_order_categories(request):
    return render(request, "admin-panel/ad-re-order-categories.html", {})


@teacher_required
def category_series(request, cat_id):
    cat = get_object_or_404(Category, id=cat_id)
    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT id, title, status FROM categories WHERE parent_id = {cat_id} ORDER BY order_no ASC, id ASC;")
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
        return JsonResponse({
            "msg": "success",
            "data": {"rows": rows, "columns": columns, "cat_title": cat.title, "cat_id": cat.id}
        })
    elif request.method == 'POST':
        data = json.loads(request.body)
        order = data['order']
        i = 0
        for category_id in order:
            i += 1
            Category.objects.filter(id=category_id).update(order_no = i)
        return JsonResponse({"msg": "Order saved successfully.", "data": {}})
    else:
        return HttpResponse("Method not allowed", status=405)


# ============================ User ==============================

@staff_required
def users(request):
    return render(request, "admin-panel/user-list.html")


@staff_required
def user_list(request):
    search = request.GET['search']
    if search == "":
        search_sql = ""
    else:
        search_sql = f"AND (username LIKE '%{search}%' OR email LIKE '%{search}%')"
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT id, first_name, last_name,username,email,date_joined FROM acc_user WHERE role=4 {search_sql};")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"rows": rows, "columns": columns}})


@staff_required
def user_change_role(request, id):
    user_obj = get_object_or_404(User, id=id)
    if request.method == "POST":
        user_obj.role = 3
        user_obj.save()
        return JsonResponse({"msg": "user role change successfully"})
    else:
        HttpResponse("Method not allowed", status=405)


# ============================ Teachers ==============================

@staff_required
def teachers(request):
    return render(request, "admin-panel/teachers.html")

@staff_required
def teacher_add(request):
    if request.method == 'GET':
        return render(request, "admin-panel/teacher-form.html")
    elif request.method == 'POST':
        email = request.POST["email"].strip()
        User.objects.create_user(
            first_name=request.POST["first_name"].strip(),
            last_name=request.POST["last_name"].strip(),
            email=email,
            mobile=request.POST["mobile"],
            dob=request.POST["birthday"],
            username=email.split('@')[0],
            role=3,
            password=request.POST["password"],
            is_active=True if request.POST['status'] == '1' else False
        )
        messages.success(request, "moderator created successfully")
        return redirect("/admin/teachers")
    else:
        HttpResponse("Method not allowed", status=405)


@staff_required
def teacher_list(request):
    search = request.GET['search']
    if search == "":
        search_sql = ""
    else:
        search_sql = f"AND (username LIKE '%{search}%' OR email LIKE '%{search}%')"
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT id, first_name, last_name,username,email,is_active,date_joined FROM acc_user WHERE role=3 {search_sql};")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"rows": rows, "columns": columns}})


@teacher_required
def teacher_edit(request, id):
    user = get_object_or_404(User, id=id)
    if request.method == "GET":
        return render(request, "admin-panel/teacher-form.html", {"teacher": user})
    elif request.method == 'POST':
        user.first_name = request.POST["first_name"].strip()
        user.last_name = request.POST["last_name"].strip()
        user.mobile = request.POST["mobile"]
        request.user.dob = request.POST["birthday"] if request.POST["birthday"] else None
        user.role = 3
        if request.POST["password"]:
            user.set_password(request.POST["password"])
        user.is_active = True if request.POST['status'] == '1' else False
        user.save()
        messages.success(request, "moderator updated successfully")
        return redirect("/admin/teachers")

# ============================ posts ==============================

@teacher_required
def posts(request):
    return render(request, "admin-panel/ad-post-list.html")


@teacher_required
def post_list(request):
    search = request.GET['search']
    search_sql = "WHERE p.status=true"
    if search != "":
        search_sql = f" AND (p.title LIKE '%{search}%') AND (u.username LIKE '%{search}%')"

    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT p.id, p.title, u.username, p.status, p.created_on, p.slug FROM posts p LEFT JOIN acc_user u ON p.user_id=u.id {search_sql} ORDER BY id DESC;")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"rows": rows, "columns": columns}})


@teacher_required
def re_order_posts(request):
    return render(request, "admin-panel/ad-re-order-posts.html", {})


@teacher_required
def post_series(request, cat_id):
    cat = get_object_or_404(Category, id=cat_id)
    if request.method == 'GET':
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT p.id, p.title, u.username FROM posts p LEFT JOIN post_categories pc ON p.id=pc.post_id LEFT JOIN acc_user u ON p.user_id=u.id WHERE pc.category_id = {cat_id} ORDER BY pc.post_order_no ASC, p.id ASC;")
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
        return JsonResponse({
            "msg": "success",
            "data": {"rows": rows, "columns": columns, "cat_title": cat.title, "cat_id": cat.id}
        })
    elif request.method == 'POST':
        data = json.loads(request.body)
        order = data['order']
        i = 0
        for post_id in order:
            i += 1
            PostCategory.objects.filter(post_id=post_id, category_id=cat.id).update(post_order_no=i)
        return JsonResponse({"msg": "Order saved successfully.", "data": {}})
    else:
        return HttpResponse("Method not allowed", status=405)
    

# ============================ banners ==============================

@staff_required
def banners(request):
    return render(request, "admin-panel/banners.html")


@staff_required
def banner_list(request):
    search = request.GET['search']
    if search == "":
        search_sql = ""
    else:
        search_sql = f"WHERE (title LIKE '%{search}%' OR url LIKE '%{search}%')"
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT id, title, status, updated_on FROM banners {search_sql};")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return JsonResponse({"msg": "success", "data": {"rows": rows, "columns": columns}})


@staff_required
def banner_add(request):
    if request.method == 'GET':
        return render(request, "admin-panel/banner-form.html")
    elif request.method == 'POST':
        banner = Banner.objects.create(
            title=request.POST['title'],
            url=request.POST['url'],
            poster=request.FILES['poster'],
            status=True if request.POST['status'] == '1' else False
        ) 
        categories = request.POST['categories'].split(',')
        for cat_id in categories:
            if not BannerCategory.objects.filter(banner_id=banner.id, category_id=cat_id).exists():
                BannerCategory.objects.create(banner_id=banner.id, category_id=cat_id)
        messages.success(request, "Banner created successfully")
        return redirect("/admin/banners")
    else:
        HttpResponse("Method not allowed", status=405)

@staff_required
def banner_edit(request, id):
    banner = get_object_or_404(Banner, id=id)
    if request.method == "GET":
        return render(request, "admin-panel/banner-form.html", {"banner": banner})
    elif request.method == 'POST':
        banner.title=request.POST['title']
        banner.url=request.POST['url']
        banner.status=True if request.POST['status'] == '1' else False

        cats_str = request.POST['categories'].strip()
        if cats_str:
            categories = cats_str.split(',')
            cat_query = f"AND category_id NOT IN ({cats_str})"
        else:
            categories = []
            cat_query = ""
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM banner_categories WHERE banner_id={banner.id} {cat_query}")
        for cat_id in categories:
            if not BannerCategory.objects.filter(banner_id=banner.id, category_id=cat_id).exists():
                BannerCategory.objects.create(banner_id=banner.id, category_id=cat_id)

        if 'poster' in request.FILES and request.FILES['poster']:
            if banner.poster:
                MediaStorage().delete(str(banner.poster))
            banner.poster=request.FILES['poster']

        banner.save()
        messages.success(request, "Banner updated successfully")
        return redirect("/admin/banners")
    else:
        HttpResponse("Method not allowed", status=405)

@staff_required
def banner_delete(request, id):
    banner = get_object_or_404(Banner, id=id)
    if request.method == 'DELETE':
        BannerCategory.objects.filter(banner_id=banner.id).delete()
        if banner.poster:
            MediaStorage().delete(str(banner.poster))
        banner.delete()
        return JsonResponse({"msg": "Banner deleted successfully."})
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)

@staff_required
def banner_categories(request, id):
    banner_cats = []
    if id != 0:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT category_id FROM banner_categories WHERE banner_id={id}")
            rows = cursor.fetchall()
            for row in rows:
                banner_cats.append(row[0])


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

    return JsonResponse({
        "msg": "Success",
        "data": {
            "parent_categories": parent_cats, "sub_categories": sub_cats,
            "banner_categories" : banner_cats
        }
    })


# --------------- courses ---------------

def gen_course_steps_ui_infos(completed_step_no: int):
    steps_dot = {}
    steps_line = {}
    if completed_step_no == 0:
        steps_dot[1] = 'active'
    elif completed_step_no == 1:
        steps_dot[2] = 'active'
        steps_dot[1] = steps_line[1] = 'done'
    elif completed_step_no == 2:
        steps_dot[3] = 'active'
        steps_dot[1] = steps_line[1] = steps_dot[2] = steps_line[2] = 'done'
    elif completed_step_no == 3:
        steps_dot[4] = 'active'
        steps_dot[1] = steps_line[1] = steps_dot[2] = steps_line[2] = steps_dot[3] = steps_line[3] = 'done'
    elif completed_step_no == 4:
        steps_dot[1] = steps_line[1] = steps_dot[2] = steps_line[2] = steps_dot[3] = steps_line[3] = steps_dot[4] = 'done'
    return steps_dot, steps_line

@teacher_required
def course_add(request, category_id):
    cat = get_object_or_404(Category, id=category_id)

    if not check_cat_premium_allowed(cat):
        return JsonResponse({"msg": "Course for this category is not allowed."}, status=400)
    
    course = Course.objects.filter(category_id=cat.id).first()
    if course:
        return redirect(f'/admin/course/{course.id}/edit')

    if request.method == 'GET':

        steps_dot, steps_line = gen_course_steps_ui_infos(0)

        return render(request, "admin-panel/ad-course-form.html", {
            "curr_step_no": 1, "steps_dot": steps_dot, "steps_line": steps_line
        })

    elif request.method == 'POST':
        data = json.loads(request.body)
        
        name = data['name'].strip()
        if not name:
            return JsonResponse({"msg": "Name can't be empty."}, status=400)

        # ---------- generating slug ----------
        slug_candidate = slug_original = slugify(name)
        for i in itertools.count(1):
            if not Course.objects.filter(slug=slug_candidate).exists():
                break
            slug_candidate = f'{slug_original}-{i}'
        # -------------------------------------

        course = Course.objects.create(
            category_id=cat.id, name=name, slug=slug_candidate, status=0,
            teacher_name=data['teacher_name'], validity=data['validity'], 
            price=data['price'], old_price=data['old_price'], units=[],
            completed_step_no=1, about=data['about']
        )

        return JsonResponse({
            "msg": "Course created successfully.",
            "data": {"created": True, "course_id": course.id}
        })
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


@teacher_required
def course_edit(request, id):
    course = get_object_or_404(Course, id=id)
    if request.method == 'GET':

        steps_dot, steps_line = gen_course_steps_ui_infos(course.completed_step_no)

        curr_step_no = course.completed_step_no + 1
        if curr_step_no > 4: curr_step_no = 4
        elif curr_step_no < 1 : curr_step_no = 1

        return render(request, "admin-panel/ad-course-form.html", {
            "course": course, "curr_step_no": curr_step_no,
            "steps_dot": steps_dot, "steps_line": steps_line,
            "course_url": f"{request.scheme}://{request.META['HTTP_HOST']}/course/{course.slug}"
        })

    elif request.method == 'POST':
        data = json.loads(request.body)
        step_no = data['step_no']

        if step_no == 1:
            name = data['name'].strip()
            course.name = name
            course.teacher_name = data['teacher_name']
            course.validity = data['validity']
            course.price = data['price']
            course.old_price = data['old_price']
            course.about = data['about']
        elif step_no == 2:
            course.description = data['description']
            course.what_included = data['what_included']
        elif step_no == 3:
            course.units = data['units']
        elif step_no == 4:
            course.status = data['status']

        if step_no > course.completed_step_no:
            course.completed_step_no = step_no

        course.save()
        return JsonResponse({"msg": "Course saved successfully."})
    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


