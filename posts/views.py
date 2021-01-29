from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def post_paginator(request, post_list):
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page, paginator


def index(request):
    post_list = Post.objects.all()
    page, paginator = post_paginator(request, post_list)
    return render(request,
                  'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page, paginator = post_paginator(request, post_list)

    return render(request, 'group.html',
                  {'group': group,
                   'page': page,
                   'paginator': paginator})


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if request.method == 'GET' or not form.is_valid():
        return render(request, 'posts/new.html', {'form': form})

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


def post_view(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    comments = post.comments.select_related('author')
    if author.username == username:
        return render(request, 'posts/post.html', {
            'post': post,
            'author': author,
            'form': form,
            'comments': comments,
        })


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    if request.user != author:
        return redirect(reverse('post', kwargs={'username': username,
                                                "post_id": post_id
                                                }))

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        return redirect(reverse('post', kwargs={'username': username,
                                                'post_id': post_id}))

    return render(request, 'posts/post_edit.html', {'form': form,
                                                    'post': post,
                                                    'is_edit': True
                                                    })


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if request.GET or not form.is_valid():
        return post_view(request, username, post_id)

    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    form.save()

    return redirect(reverse('post', kwargs={'username': username,
                                            'post_id': post_id}))


@login_required
def follow_index(request):
    follow = Follow.objects.filter(user=request.user
                                   ).select_related('author'
                                                    ).values_list(
        'author_id')
    post_list = Post.objects.filter(author__in=follow)
    page, paginator = post_paginator(request, post_list)
    return render(request, 'follow.html',
                  {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)

    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    follower = Follow.objects.filter(
        user__username=request.user,
        author__username=username).select_related('follower')
    if follower.exists():
        follower.delete()
    return redirect('profile', username=username)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated and \
            Follow.objects.filter(user=request.user, author=author).exists():
        following = True
    followers_count = Follow.objects.filter(
        author__username=username).select_related('follower').count()
    followers_list = Follow.objects.filter(author=author)
    post_list = author.posts.all()
    page, paginator = post_paginator(request, post_list)
    return render(request, 'posts/profile.html', {
        'page': page,
        'paginator': paginator,
        'profile': author,
        'following': following,
        'followers_list': followers_list,
        'followers_count': followers_count,
    })


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
