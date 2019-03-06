import datetime

from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail, get_connection
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from blog.forms import RegisterForm, PostForm, CommentForm, UnlikeForm, LikeForm, CategoryForm, ReplyForm, \
    FeedbackForm, TagForm, UpdateUserForm
from blog_engine import settings
from .models import *


class Index(View):
    def get(self, request, page=1):
        p = Post.objects.all().order_by('-date')
        paginator = Paginator(p, 8)
        try:
            posts = paginator.page(page)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        pinned = PinnedPost.objects.all()[0:3]
        return render(request, 'blog/index.html', context={'posts': posts, 'pinned': pinned})


class PostDetails(View):
    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        post.views += 1
        post.save()
        if request.user.is_authenticated:
            is_liked = request.user.profile.likes.filter(slug=slug).count() > 0
            is_pinned = PinnedPost.objects.filter(post__slug=slug).count() > 0
            return render(request, 'blog/post_details.html', context={'post': post,
                                                                      'is_liked': is_liked,
                                                                      'is_pinned': is_pinned})
        else:
            return render(request, 'blog/post_details.html', context={'post': post})


class SendComment(LoginRequiredMixin, View):
    login_url = '/account/login/'
    redirect_field_name = 'from_url'

    def get(self, request, post):

        return render(request, 'blog/comment.html', context={'post': post, 'author': request.user.id})

    def post(self, request):
        cf = CommentForm(request.POST)
        post = Post.objects.get(id=request.POST['post'])
        user = User.objects.get(id=request.POST['author'])
        if user.username == request.user.username:
            if cf.is_valid():
                cf.save()
        return redirect('post_details', slug=post.slug)


class ReplyComment(LoginRequiredMixin, View):
    login_url = '/account/login/'
    redirect_field_name = 'from_url'

    def get(self, request, comment):
        return render(request, 'blog/reply.html', context={'comment': comment, 'author': request.user.id})

    def post(self, request):
        rf = ReplyForm(request.POST)
        comment = Comment.objects.get(id=request.POST['comment'])
        user = User.objects.get(id=request.POST['author'])
        if user.username == request.user.username:
            if rf.is_valid():
                rf.save()
        return redirect('post_details', slug=comment.post.slug)


class TagsList(View):
    def get(self, request):
        tags = Tag.objects.all()
        data = [{'title': tag.title.lower(), 'url': tag.get_absolute_url()} for tag in tags]
        response = {
            'status': 'OK',
            'data': data
        }
        return JsonResponse(response)


class CategoriesList(View):
    def get(self, request):
        categories = Category.objects.all()
        data = [{'title': category.title,
                 'url': category.get_absolute_url(),
                 'posts_count': category.posts.count()}
                for category in categories]
        response = {
            'status': 'OK',
            'data': data
        }
        return JsonResponse(response)


class PopularPosts(View):
    def get(self, request):
        posts = Post.objects.filter(date__year=datetime.date.today().year,
                                    date__month=datetime.date.today().month).order_by('-views')[0:3]
        data = [{'title': post.title,
                 'url': post.get_absolute_url(),
                 'image': post.cover_small.url if post.cover_small else 'static/images/posts/default-post-image.jpg',
                 'date': post.date.date().strftime(" %b. %d, %Y")}
                for post in posts]
        if len(data) > 0:
            response = {
                'status': 'OK',
                'data': data
            }
            return JsonResponse(response)
        else:
            response = {
                'status': 'NOTFOUND',
                'data': ''
            }
            return JsonResponse(response)


class UserInfo(View):
    def get(self, request):
        if request.user.is_authenticated:
            user = Profile.objects.get(user__username=request.user.username)
            return render(request, 'blog/user_info.html', context={'user': user})
        else:
            return render(request, 'blog/auth_panel.html')


class TagPosts(View):
    def get(self, request, slug, page=1):
        tag = get_object_or_404(Tag, slug=slug)
        p = tag.posts.all()
        paginator = Paginator(p, 8)
        try:
            posts = paginator.page(page)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        return render(request, 'blog/tag_posts.html', context={'posts': posts, 'tag': tag})


class CategoryPosts(View):
    def get(self, request, slug, page=1):
        category = get_object_or_404(Category, slug=slug)
        p = category.posts.all()
        paginator = Paginator(p, 8)
        try:
            posts = paginator.page(page)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        return render(request, 'blog/category_posts.html', context={'posts': posts, 'category': category})


class MyAccount(LoginRequiredMixin, View):
    login_url = '/account/login/'
    redirect_field_name = 'from_url'

    def get(self, request):
        user = User.objects.get(username=request.user.username)
        form = UpdateUserForm(initial={'username': user.username,
                                       'full_name': user.profile.full_name,
                                       'email': user.email,
                                       'old_username': user.username,
                                       'old_email': user.email})
        return render(request, 'blog/account.html', context={'user': user, 'form': form})

    def post(self, request):  # changing user info
        form = UpdateUserForm(request.POST, request.FILES)
        if request.POST.get('old_password'):
            user = auth.authenticate(request, username=request.user.username, password=request.POST.get('old_password'))
            if user is None:
                form.errors.update({'old_password': 'Wrong password'})
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            form = UpdateUserForm(initial={'username': user.username,
                                           'full_name': user.profile.full_name,
                                           'email': user.email,
                                           'old_username': user.username,
                                           'old_email': user.email})

        user = User.objects.get(username=request.user.username)
        return render(request, 'blog/account.html', context={'user': user,
                                                             'form': form,
                                                             'status': 'Information successful updated!'})


class UserAccount(View):
    def get(self, request, username, page=1):
        user = get_object_or_404(User, username__iexact=username)
        p = Post.objects.filter(author=user.profile).order_by('-date')
        paginator = Paginator(p, 8)
        try:
            posts = paginator.page(page)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        return render(request, 'blog/user_account.html', context={'user': user, 'posts': posts})  # todo


class UserFavoritePosts(LoginRequiredMixin, View):
    login_url = '/account/login/'
    redirect_field_name = 'from_url'

    def get(self, request, page):
        user = request.user.profile
        p = user.likes.all()
        count = p.count()
        paginator = Paginator(p, 3)
        try:
            posts = paginator.page(page)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        return render(request, 'blog/user_favorite_posts.html', context={'posts': posts, 'count': count})


class UserPosts(LoginRequiredMixin, View):
    login_url = '/account/login/'
    redirect_field_name = 'from_url'

    def get(self, request, page):
        user = request.user.profile
        p = user.posts.all()
        count = p.count()
        paginator = Paginator(p, 3)
        try:
            posts = paginator.page(page)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        return render(request, 'blog/user_posts.html', context={'posts': posts, 'count': count})


class Search(View):
    def get(self, request, query, page=1):
        p = Post.objects.filter(Q(body__icontains=query) | Q(title__icontains=query))
        paginator = Paginator(p, 8)
        try:
            posts = paginator.page(page)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        return render(request, 'blog/search.html', context={'posts': posts, 'query': query})


class CreatePost(PermissionRequiredMixin, View):
    login_url = '/account/login/'
    redirect_field_name = 'from_url'
    permission_required = 'blog.add_post'

    def get(self, request):
        user_id = request.user.profile.id
        form = PostForm(initial={'author': user_id})
        return render(request, 'blog/create_post.html', context={'form': form})

    def post(self, request):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            if str(request.user.profile.id) == form.data.get('author'):
                post = form.save()
            else:
                post = form.save()
                post.author = request.user.profile
                post.save()
            return redirect(post.get_absolute_url())
        return render(request, 'blog/create_post.html', context={'form': form})


class UpdatePost(PermissionRequiredMixin, View):
    login_url = '/account/login/'
    redirect_field_name = 'from_url'
    permission_required = 'blog.change_post'

    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        form = PostForm(instance=post)
        return render(request, 'blog/update_post.html', context={'form': form, 'slug': slug})

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            post.slug = slug
            post.save()
            return redirect(post.get_absolute_url())
        return render(request, 'blog/update_post.html', context={'form': form, 'slug': slug})


class LikePost(LoginRequiredMixin, View):
    login_url = '/account/login/'
    redirect_field_name = 'from_url'

    def post(self, request, slug):
        if request.user.profile.likes.filter(slug=slug).count() == 0:
            post = get_object_or_404(Post, slug=slug)
            form = LikeForm({'post': post.id, 'profile': request.user.profile.id})
        else:
            post = get_object_or_404(Post, slug=slug)
            form = UnlikeForm({'post': post.id, 'profile': request.user.profile.id})
        if form.is_valid():
            form.save()
        return redirect(post.get_absolute_url())


class CreateCategory(PermissionRequiredMixin, View):
    login_url = '/account/login/'
    redirect_field_name = 'from_url'
    permission_required = 'blog.add_category'

    def get(self, request):
        form = CategoryForm()
        return render(request, 'blog/create_category.html', context={'form': form})

    def post(self, request):
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('create_post')
        return render(request, 'blog/create_category.html', context={'form': form})


class CreateTag(PermissionRequiredMixin, View):
    login_url = '/account/login/'
    redirect_field_name = 'from_url'
    permission_required = 'blog.add_tag'

    def get(self, request):
        form = TagForm()
        return render(request, 'blog/create_tag.html', context={'form': form})

    def post(self, request):
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_post')
        return render(request, 'blog/create_tag.html', context={'form': form})


class PinPost(PermissionRequiredMixin, View):
    login_url = '/account/login/'
    redirect_field_name = 'from_url'
    permission_required = 'blog.add_pinnedpost'

    def post(self, request, slug):
        is_pinned = PinnedPost.objects.filter(post__slug=slug).count() > 0
        post = Post.objects.get(slug=slug)
        if is_pinned:
            PinnedPost.objects.get(post__slug=slug).delete()
        else:
            pinned_post = PinnedPost(post=post)
            pinned_post.save()
        return redirect(post.get_absolute_url())


class DeletePost(PermissionRequiredMixin, View):
    login_url = '/account/login/'
    redirect_field_name = 'from_url'
    permission_required = 'blog.delete_post'

    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        return render(request, 'blog/delete_post.html', context={'post': post})

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        post.delete()
        return redirect('index')


class Register(View):
    def get(self, request):
        form = RegisterForm()
        if request.user.is_authenticated:
            return redirect('index')
        return render(request, 'blog/register.html', context={'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return redirect('index')
        return render(request, 'blog/register.html', context={'form': form})


class Login(View):
    def get(self, request, from_url=''):
        from_url = from_url or request.GET.get('from_url')
        return render(request, 'blog/login.html', context={'from_url': from_url})

    def post(self, request):
        login = request.POST['username']
        password = request.POST['password']
        url = request.POST.get('from_url') or ''
        user = User.objects.filter(username__iexact=login)
        if User.objects.filter(username__iexact=login).count() != 1:
            return render(request, 'blog/login.html',
                          context={'from_url': url, 'status': 'User not found', 'login': login})
        login = user.first().username
        user = auth.authenticate(request, username=login, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect(url)
        return render(request, 'blog/login.html', context={'from_url': url, 'status': 'Wrong password','login': login})


class Logout(LoginRequiredMixin, View):
    login_url = ''
    redirect_field_name = 'from_url'

    def get(self, request, redirect_to):
        auth.logout(request)
        return redirect(redirect_to)


class About(View):
    def get(self, request):
        return render(request, 'blog/about.html')


class Contact(View):
    def get(self, request):
        form = FeedbackForm()
        return render(request, 'blog/contact.html', context={'form': form})

    def post(self, request):
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            form = FeedbackForm()
            return render(request, 'blog/contact.html', context={'form': form, 'status': 'Message sent successfully!'})
        return render(request, 'blog/contact.html', context={'form': form})


class ResetPassword(View):
    def get(self, request):
        return render(request, 'blog/reset_password.html')

    def post(self, request):
        password = User.objects.make_random_password()
        if User.objects.filter(email__iexact=request.POST.get('email')).count() != 1:
            return render(request, 'blog/reset_password.html', context={'status': 'User not found!'})
        user = User.objects.get(email__iexact=request.POST.get('email'))
        user.set_password(password)
        user.save()
        send_mail(
            'Reset password',
            'New password for {} is {}'.format(user.username, password),
            'no-reply@scoruja.pw',
            ['strigocoruja@ya.ru'],
            fail_silently=False,
        )
        return render(request, 'blog/reset_password.html',
                      context={'status': 'New password sent to {}'.format(user.email)})
