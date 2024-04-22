from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .constants import PAGINATOR
from .forms import CommentForm, PostForm, UserForm
from .mixins import (CommentMixin, OnlyAuthorMixin, OnlyAuthorMixinRedirect,
                     OnlyAuthorMixinVisible, PostMixin)
from .models import Category, Post, User
from .service import order_annotate, post_list_request


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = 'pub_date'
    paginate_by = PAGINATOR

    def get_queryset(self):
        return order_annotate(post_list_request())


class PostDetailView(OnlyAuthorMixinVisible, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "blog:profile",
            kwargs={"username": self.request.user})


class PostUpdateView(OnlyAuthorMixinRedirect, PostMixin, UpdateView):

    def get_success_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={"post_id": self.kwargs['post_id']})


class PostDeleteView(OnlyAuthorMixin, PostMixin, DeleteView):
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class CategoryListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = PAGINATOR

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category,
                                     slug=self.kwargs['category_slug'],
                                     is_published=True)
        context['category'] = category
        return context

    def get_queryset(self):
        category_object = get_object_or_404(Category,
                                            slug=self.kwargs['category_slug'],
                                            is_published=True)
        return order_annotate(post_list_request().filter(
            category=category_object
        )
        )


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = PAGINATOR

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(User,
                                               username=self.kwargs['username']
                                               )
        return context

    def get_queryset(self):
        user_object = get_object_or_404(User, username=self.kwargs['username'])
        if self.request.user == user_object:
            return order_annotate(
                super().get_queryset().select_related(
                    'category', 'location', 'author'
                ).filter(
                    author=user_object
                )
            )
        return order_annotate(
            post_list_request().filter(
                author=user_object)
        )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            "blog:profile",
            kwargs={"username": self.request.user}
        )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


class CommentUpdateView(OnlyAuthorMixin, CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(OnlyAuthorMixin, CommentMixin, DeleteView):
    pass
