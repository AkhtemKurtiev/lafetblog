from datetime import datetime

from django.db.models import Count

from .models import Post


def post_list_request():
    return Post.objects.select_related(
        'location', 'category', 'author').filter(
        pub_date__lte=datetime.now(),
        is_published=True,
        category__is_published=True
    )


def order_annotate(queryset):
    return queryset.order_by(
        '-pub_date').annotate(
            comment_count=Count('comments'))
