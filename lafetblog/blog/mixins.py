from datetime import datetime

from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .forms import PostForm
from .models import Comment, Post


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class OnlyAuthorMixinRedirect(UserPassesTestMixin):
    pk_url_kwarg = 'post_id'

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', self.kwargs['post_id'])


class OnlyAuthorMixinVisible(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        if object.author == self.request.user:
            return True
        return get_object_or_404(Post, id=self.kwargs['post_id'],
                                 is_published=True,
                                 pub_date__lte=datetime.now(),
                                 category__is_published=True,
                                 )

    def handle_no_permission(self):
        return HttpResponseNotFound()


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={"post_id": self.kwargs['post_id']})


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
