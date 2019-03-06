from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from imagekit.models import ImageSpecField
from pilkit.processors import Adjust, ResizeToFill, ResizeToFit


class Profile(models.Model):
    full_name = models.CharField(max_length=100, db_index=True)
    image = models.ImageField(upload_to='static/images/users',
                              default='static/images/users/default-user-image.jpg')
    image_cropped = ImageSpecField(source='image',
                                   processors=[ResizeToFill(256, 256)],
                                   format='JPEG',
                                   options={'quality': 90})
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse('user_account', kwargs={'username': self.user.username })

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance,
                                   full_name=instance.username)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

class Category(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()
    cover = models.ImageField(upload_to='static/images/categories',
                              blank=True,
                              default='static/images/categories/default-category-image.jpg')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_posts', kwargs={'slug': self.slug})


class Tag(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tag_posts', kwargs={'slug': self.slug})


class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    cover = models.ImageField(blank=True,
                              upload_to='static/images/posts',
                              default='static/images/posts/default-post-image.jpg')
    cover_small = ImageSpecField(source='cover',
                                 processors=[ResizeToFill(800, 534)],
                                 format='JPEG',
                                 options={'quality': 90})
    cover_big = ImageSpecField(source='cover',
                               processors=[ResizeToFill(1900, 1267)],
                               format='JPEG',
                               options={'quality': 90})
    slug = models.SlugField()
    date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, related_name='posts', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='posts')
    likes = models.ManyToManyField(Profile, related_name='likes', blank=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_details', kwargs={'slug': self.slug})


class PinnedPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return '[{}]: {}'.format(self.author.full_name, self.text)


class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return '[{}] to [{}]: "{}"'.format(self.author.full_name, self.comment.author.full_name, self.text)


class Feedback(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} | ({})'.format(self.name, self.email)
