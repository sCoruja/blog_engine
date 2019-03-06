from django.contrib import auth
from django.core.exceptions import ValidationError
from django import forms
from transliterate import translit
from django.utils.text import slugify
from time import time
from .models import *


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'slug', 'cover']

        widgets = {
            'title': forms.widgets.Input(attrs={'class': 'form-control'}),
            'slug': forms.widgets.Input(attrs={'class': 'form-control'}),
            'cover': forms.widgets.FileInput(attrs={'class': 'form-control-file'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if slug == 'create':
            raise ValidationError('Enter correct slug')
        if Category.objects.filter(slug__iexact=slug).count():
            raise ValidationError('Slug {} already exists'.format(slug))
        return slug


# def clean_cover(self):
#    if self.cleaned_data['cover'] is None:
#       return 'static/images/categories/default-category-image.jpg'


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['title', 'slug']

        widgets = {
            'title': forms.widgets.Input(attrs={'class': 'form-control'}),
            'slug': forms.widgets.Input(attrs={'class': 'form-control'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if slug == 'create':
            raise ValidationError('Enter correct slug')
        if Tag.objects.filter(slug__iexact=slug).count():
            raise ValidationError('Slug {} already exists'.format(slug))
        return slug


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'tags', 'cover', 'body', 'slug', 'author']
        widgets = {
            'title': forms.widgets.Input(attrs={'class': 'form-control'}),
            'body': forms.widgets.Textarea(attrs={'class': 'form-control'}),
            'cover': forms.widgets.FileInput(attrs={'class': 'form-control-file'}),
            'category': forms.widgets.Select(attrs={'class': 'form-control'}),
            'tags': forms.widgets.SelectMultiple(attrs={'class': 'custom-select'}),
            'slug': forms.widgets.HiddenInput(attrs={'class': 'form-control', 'value': 'slug'}),
            'author': forms.widgets.HiddenInput(attrs={'class': 'form-control'})
        }

    # def clean_cover(self):
    #     if self.cleaned_data['cover'] is None:
    #        return 'static/images/posts/default-post-image.jpg'

    def clean_slug(self):
        title = self.cleaned_data['title']
        slug = title
        try:
            slug = translit(slug, reversed=True)
        finally:
            slug = slugify(slug)
            return '-'.join([slug, str(int(time()))])


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'post', 'author']
        widgets = {
            'text': forms.widgets.Textarea(attrs={'class': 'form-control'}),
            'post': forms.widgets.HiddenInput(),
            'author': forms.widgets.HiddenInput(),
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['text', 'comment', 'author']
        widgets = {
            'text': forms.widgets.Textarea(attrs={'class': 'form-control'}),
        }


class LikeForm(forms.Form):
    post = forms.IntegerField()
    profile = forms.IntegerField()
    fields = ['post', 'profile']

    def clean(self):
        if Post.objects.filter(id=self.cleaned_data['post']).count() != 1:
            raise ValidationError('Post not found')
        if Profile.objects.filter(id=self.cleaned_data['profile']).count() == 0:
            raise ValidationError('Profile not found')
        return self.cleaned_data

    def save(self):
        post = Post.objects.get(id=self.cleaned_data['post'])
        post.likes.add(self.cleaned_data['profile'])
        post.save()
        return Post.objects.get(id=self.cleaned_data['post'])


class UnlikeForm(forms.Form):
    post = forms.IntegerField()
    profile = forms.IntegerField()
    fields = ['post', 'profile']

    def clean(self):
        if Post.objects.filter(id=self.cleaned_data['post']).count() == 0:
            raise ValidationError('Post not found')
        if Profile.objects.filter(id=self.cleaned_data['profile']).count() == 0:
            raise ValidationError('Profile not found')
        if Post.objects.get(id=self.cleaned_data['post']).likes.filter(id=self.cleaned_data['profile']) == 0:
            raise ValidationError('Like not found')
        return self.cleaned_data

    def save(self):
        post = Post.objects.get(id=self.cleaned_data['post'])
        post.likes.remove(self.cleaned_data['profile'])
        post.save()
        return Post.objects.get(id=self.cleaned_data['post'])


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.widgets.Input(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.widgets.EmailInput(attrs={'class': 'form-control'}))
    full_name = forms.CharField(max_length=100, widget=forms.widgets.Input(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}))
    image = forms.ImageField(required=False, widget=forms.widgets.FileInput(attrs={'class': 'form-control-file'}))

    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data['username']).count():
            raise ValidationError('User already exist')
        return self.cleaned_data['username']

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).count():
            raise ValidationError('Email already exist')
        return self.cleaned_data['email']

    def clean_confirm_password(self):
        if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
            raise ValidationError('Passwords do not match')
        return self.cleaned_data['confirm_password']

    def save(self):
        user = User.objects.create_user(username=self.cleaned_data['username'],
                                        password=self.cleaned_data['confirm_password'],
                                        email=self.cleaned_data['email'])
        if self.cleaned_data['image']:
            user.profile.image = self.cleaned_data['image']
        user.profile.full_name = self.cleaned_data['full_name']
        user.save()
        return user


class UpdateUserForm(forms.Form):
    old_username = forms.CharField(widget=forms.widgets.HiddenInput,
                                   required=True)
    old_email = forms.CharField(widget=forms.widgets.HiddenInput,
                                required=True)
    username = forms.CharField(max_length=150,
                               widget=forms.widgets.Input(attrs={'class': 'form-control'}),
                               required=False)
    email = forms.EmailField(widget=forms.widgets.EmailInput(attrs={'class': 'form-control'}),
                             required=False)
    full_name = forms.CharField(max_length=100, widget=forms.widgets.Input(attrs={'class': 'form-control'}),
                                required=False)
    old_password = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}),
                                   required=False)
    new_password = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}),
                                   required=False)
    confirm_password = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}),
                                       required=False)
    image = forms.ImageField(required=False,
                             widget=forms.widgets.FileInput(attrs={'class': 'form-control-file'}))

    def clean_username(self):
        if self.cleaned_data['username'] != self.cleaned_data['old_username'] and \
                User.objects.filter(username=self.cleaned_data['username']).count() > 0:
            raise ValidationError('This username already exists')
        return self.cleaned_data['username']

    def clean_email(self):
        if self.cleaned_data['email'] != self.cleaned_data['old_email'] and \
                User.objects.filter(email=self.cleaned_data['email']).count() > 0:
            raise ValidationError('This email already exists')
        return self.cleaned_data['email']

    def clean_confirm_password(self):
        if self.cleaned_data['new_password'] != self.cleaned_data['confirm_password']:
            raise ValidationError('Passwords do not match')
        return self.cleaned_data['confirm_password']

    def save(self):
        user = User.objects.get(username=self.cleaned_data['old_username'])
        if self.cleaned_data['username']:
            user.username = self.cleaned_data['username']
        if self.cleaned_data['email']:
            user.email = self.cleaned_data['email']
        if self.cleaned_data['full_name']:
            user.profile.full_name = self.cleaned_data['full_name']
        if self.cleaned_data['image']:
            user.profile.image = self.cleaned_data['image']
        if self.cleaned_data['confirm_password']:
            user.set_password(self.cleaned_data['confirm_password'])
        user.save()
        return user


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.widgets.Input(attrs={'class': 'form-control'}),
            'email': forms.widgets.Input(attrs={'class': 'form-control'}),
            'message': forms.widgets.Textarea(attrs={'class': 'form-control'}),
        }


class ResetPasswordForm(forms.Form):
    pass
