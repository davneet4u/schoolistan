from post.models import Post, Category, PostCategory

def transfer_post_cat_infos():
    posts = Post.objects.all()
    for post in posts:
        if post.category_id:
            if PostCategory.objects.filter(post_id=post.id, category_id=post.category_id).exists():
                print(f"==> Table already contains Post with id '{post.id}'")
            else:
                PostCategory.objects.create(
                    post_id=post.id, category_id=post.category_id,
                    post_order_no=post.order_no if post.order_no else None
                )
                print(f"==> New post_category record created with post id '{post.id}'")
        else:
            print(f"==> Post with id '{post.id}' has no any category")

# from utility.temporary import transfer_post_cat_infos
# transfer_post_cat_infos()