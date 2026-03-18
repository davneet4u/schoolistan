# Create your views here.
@login_required
def post_create(request):
    if request.method == 'GET':
        return render(request, "post/create-post.html")
    elif request.method == 'POST':

        category_id = None
        premium = False
        featured = False
        if request.user.role <= 3:
            if request.POST['category']:
                category_id = request.POST['category']
            if request.POST['premium'] == '1':
                premium = True
            if request.POST['featured'] == '1':
                featured = True

        title = request.POST['title'] if request.POST['title'] else None
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

        short = Post.objects.create(
            user_id=request.user.id,
            slug=slug_candidate,
            title=title,
            text=request.POST['text'] if request.POST['text'] else None,
            premium=premium,
            featured=featured,
            status=True,
            category_id=category_id,
        )
        # saving youtub
        if request.POST['youtube']:
            PostAttachment.objects.create(
                attachment=request.POST['youtube'],
                post_id=short.id,
                type=3,
            )

        # saving images
        images = request.FILES.getlist('image')
        for f in images:
            file_path = f"posts/user-{request.user.id}/images/{str(time()).replace('.', '_')}.{f.name.split('.')[-1]}"
            # FileSystemStorage().save(file_path, f)
            MediaStorage().save(file_path, f)
            PostAttachment.objects.create(
                attachment=file_path,
                post_id=short.id,
                type=1,
            )

        # saving videos
        videos = request.FILES.getlist('video')
        for f in videos:
            file_path = f"posts/user-{request.user.id}/videos/{str(time()).replace('.', '_')}.{f.name.split('.')[-1]}"
            # FileSystemStorage().save(file_path, f)
            MediaStorage().save(file_path, f)
            PostAttachment.objects.create(
                attachment=file_path,
                post_id=short.id,
                type=2,
            )

        messages.success(request, 'post created successfully')
        return redirect("/")
    else:
        return HttpResponse("Method not allowed", status=405)


@login_required
def post_edit(request, id):
    post_obj = get_object_or_404(Post, id=id)
    if request.user.role == 3 or post_obj.user_id == request.user.id:
        if request.method == "GET":
            category_branches = get_category_branch_infos(post_obj.category_id)
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
            post_obj.title = request.POST["title"]
            post_obj.featured = False
            if request.user.role <= 3:
                post_obj.category_id = request.POST['category'] if request.POST['category'] else None
                post_obj.premium = True if request.POST['premium'] == '1' else False
                post_obj.featured = True if request.POST['featured'] == '1' else False
            post_obj.save()

            if request.POST['youtube']:
                try:
                    attach = PostAttachment.objects.get(post_id=id, type=3)
                    attach.attachment = request.POST['youtube']
                    attach.save()
                except PostAttachment.DoesNotExist:
                    PostAttachment.objects.create(
                        attachment=request.POST['youtube'],
                        post_id=id,
                        type=3,
                    )
            else:
                PostAttachment.objects.filter(post_id=id, type=3).delete()

            # saving images
            images = request.FILES.getlist('image')
            if len(images) > 0:
                imgattch = PostAttachment.objects.filter(post_id=id, type=1)
                for i in imgattch:
                    MediaStorage().delete(i.attachment)
                PostAttachment.objects.filter(post_id=id, type=1).delete()
            for f in images:
                file_path = f"posts/user-{request.user.id}/images/{str(time()).replace('.', '_')}.{f.name.split('.')[-1]}"
                # FileSystemStorage().save(file_path, f)
                MediaStorage().save(file_path, f)
                PostAttachment.objects.create(
                    attachment=file_path,
                    post_id=id,
                    type=1,
                )

            # saving videos
            videos = request.FILES.getlist('video')
            if len(videos) > 0:
                videoss = PostAttachment.objects.filter(post_id=id, type=2)
                for i in videoss:
                    MediaStorage().delete(i.attachment)
                PostAttachment.objects.filter(post_id=id, type=2).delete()
            for f in videos:
                file_path = f"posts/user-{request.user.id}/videos/{str(time()).replace('.', '_')}.{f.name.split('.')[-1]}"
                # FileSystemStorage().save(file_path, f)
                MediaStorage().save(file_path, f)
                PostAttachment.objects.create(
                    attachment=file_path,
                    post_id=id,
                    type=2,
                )

            return redirect("/")
        else:
            return HttpResponse("Method not allowed", status=405)
    else:
        return HttpResponse("Access denied", status=401)


