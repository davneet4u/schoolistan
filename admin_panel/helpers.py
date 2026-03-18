from post.models import Category


def check_cat_premium_allowed(cat: Category):
    # premium_allowed = False
    if cat.parent_id:
        try:
            parent_cat = Category.objects.get(id=cat.parent_id)
            return True if not parent_cat.parent_id else False
        except Category.DoesNotExist:
            return False
    return False