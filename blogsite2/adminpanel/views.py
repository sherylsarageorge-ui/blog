from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Q
from accounts.models import Profile                                        # adminpanel has no model..its sharing from accounts app and blog app
from blog.models import Post, Comment


@staff_member_required(login_url='/auth/login/')
def dashboard_view(request):
    user_query = request.GET.get('uq', '')
    post_query = request.GET.get('pq', '')

    users = User.objects.filter(is_staff=False).select_related('profile')
    posts = Post.objects.filter(is_deleted=False).select_related('author')

    if user_query:
        users = users.filter(
            Q(username__icontains=user_query) |
            Q(email__icontains=user_query) |
            Q(first_name__icontains=user_query)
        )
    if post_query:
        posts = posts.filter(
            Q(title__icontains=post_query) |
            Q(author__username__icontains=post_query)
        )

    total_comments = Comment.objects.filter(is_deleted=False).count()
    stats = [('Users', User.objects.filter(is_staff=False).count()),
             ('Posts', Post.objects.filter(is_deleted=False).count()),
             ('Comments', total_comments)]

    return render(request, 'adminpanel/dashboard.html', {
        'users': users, 'posts': posts, 'stats': stats,
        'user_query': user_query, 'post_query': post_query,
    })


@staff_member_required(login_url='/auth/login/')
def block_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id, is_staff=False)
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.is_blocked = not profile.is_blocked
    profile.save()
    return redirect('admin_dashboard')


@staff_member_required(login_url='/auth/login/')
def delete_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id, is_staff=False)
    user.delete()
    return redirect('admin_dashboard')


@staff_member_required(login_url='/auth/login/')
def edit_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        post.title   = request.POST.get('title', post.title).strip()
        post.content = request.POST.get('content', post.content).strip()
        if request.FILES.get('image'):
            post.image = request.FILES['image']
        post.save()
        return redirect('admin_dashboard')
    return render(request, 'adminpanel/edit_post.html', {'post': post})


@staff_member_required(login_url='/auth/login/')
def delete_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.is_deleted = True
    post.save()
    return redirect('admin_dashboard')


@staff_member_required(login_url='/auth/login/')
def comments_view(request):
    query = request.GET.get('q', '')
    comments = Comment.objects.filter(is_deleted=False).select_related('author', 'post')
    if query:
        comments = comments.filter(
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(post__title__icontains=query)
        )
    return render(request, 'adminpanel/comments.html', {'comments': comments, 'query': query})


@staff_member_required(login_url='/auth/login/')
def delete_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_deleted = True
    comment.save()
    return redirect('admin_comments')
