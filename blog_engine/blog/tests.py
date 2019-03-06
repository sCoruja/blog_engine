from django.test import TestCase, Client

from blog.models import *
from blog.forms import *


class PostTests(TestCase):

    def setUp(self):
        user = User.objects.create_user(username='user1', password='12345', email='e1@mail.com')
        category = Category.objects.create(title='Category', slug='category')
        tag = Tag.objects.create(title='Tag', slug='tag')
        post = Post.objects.create(title='Post title',
                                   slug='post',
                                   body='Some text.',
                                   author=user.profile,
                                   category=category)
        post.tags.add(tag)

    def test_str(self):
        post = Post.objects.get(slug='post')
        self.assertEquals(str(post), 'Post title')

    def test_category(self):
        post = Post.objects.get(slug='post')
        self.assertEquals(post.category.title, 'Category')

    def test_tags(self):
        tag = Post.objects.get(slug='post').tags.first()
        self.assertEquals(str(tag), 'Tag')

    def test_author(self):
        post = Post.objects.get(slug='post')
        self.assertEquals(post.author.full_name, 'user1')


class TagTests(TestCase):

    def setUp(self):
        Tag.objects.create(title='Tag', slug='tag')

    def test_str(self):
        tag = Tag.objects.get(slug='tag')
        self.assertEquals(str(tag), 'Tag')


class CategoryTests(TestCase):

    def setUp(self):
        Category.objects.create(title='Category', slug='category')

    def test_str(self):
        category = Category.objects.get(slug='category')
        self.assertEquals(str(category), 'Category')


class ProfileTests(TestCase):

    def setUp(self):
        usr = User.objects.create_user(username='user', password='12345', email='e@mail.com')

    def test_str(self):
        user = Profile.objects.get(user__username='user')
        self.assertEquals(str(user), 'user')


class CommentTests(TestCase):

    def setUp(self):
        user1 = User.objects.create_user(username='user1', password='12345', email='e1@mail.com')
        user2 = User.objects.create_user(username='user2', password='12345', email='e2@mail.com')
        category = Category.objects.create(title='Category', slug='category')
        tag = Tag.objects.create(title='Tag', slug='tag')
        post = Post.objects.create(title='Post title',
                                   slug='post',
                                   body='Some text.',
                                   author=user1.profile,
                                   category=category)
        post.tags.add(tag)
        comment = Comment.objects.create(post=post, text='Hi', author=user1.profile)
        Reply.objects.create(comment=comment, text='Hello', author=user2.profile)

    def test_comment_str(self):
        comment = Post.objects.get(slug='post').comments.all()[0]
        self.assertEquals(str(comment), '[user1]: Hi')

    def test_reply_str(self):
        comment = Post.objects.get(slug='post').comments.all()[0]
        reply = comment.replies.all()[0]
        self.assertEquals(str(reply), '[user2] to [user1]: "Hello"')


class CategoryFormTests(TestCase):

    def setUp(self):
        Category.objects.create(title='Category', slug='category')

    def test_valid(self):
        data = {
            'title': 'Django',
            'slug': 'django'
        }
        cf = CategoryForm(data)
        self.assertTrue(cf.is_valid())
        self.assertEquals(cf.cleaned_data['title'], data['title'])
        self.assertEquals(cf.cleaned_data['slug'], data['slug'])

    def test_default_cover(self):
        data = {
            'title': 'Django',
            'slug': 'django'
        }
        cf = CategoryForm(data)
        self.assertTrue(cf.is_valid())
        self.assertEquals(cf.cleaned_data['cover'], 'static/images/categories/default-category-image.jpg')

    def test_invalid_slug(self):
        data = {
            'title': 'Django',
            'slug': 'create'
        }
        cf = CategoryForm(data)
        self.assertFalse(cf.is_valid())
        self.assertIsNone(cf.cleaned_data.get('slug'))

    def test_existing_slug(self):
        data = {
            'title': 'Django',
            'slug': 'category'
        }
        cf = CategoryForm(data)
        self.assertFalse(cf.is_valid())
        self.assertIsNone(cf.cleaned_data.get('slug'))

    def test_save(self):
        data = {
            'title': 'Django',
            'slug': 'django'
        }
        cf = CategoryForm(data)
        category = cf.save()
        self.assertEquals(category.title, data['title'])
        self.assertEquals(category.slug, data['slug'])
        self.assertEquals(category.cover, 'static/images/categories/default-category-image.jpg')


class TagFormTests(TestCase):
    def setUp(self):
        Tag.objects.create(title='Tag', slug='tag')

    def test_valid(self):
        data = {
            'title': 'Django',
            'slug': 'django'
        }
        tf = TagForm(data)
        self.assertTrue(tf.is_valid())
        self.assertEquals(tf.cleaned_data['title'], data['title'])
        self.assertEquals(tf.cleaned_data['slug'], data['slug'])

    def test_invalid_slug(self):
        data = {
            'title': 'Django',
            'slug': 'create'
        }
        tf = TagForm(data)
        self.assertFalse(tf.is_valid())
        self.assertIsNone(tf.cleaned_data.get('slug'))

    def test_existing_slug(self):
        data = {
            'title': 'Django',
            'slug': 'tag'
        }
        tf = TagForm(data)
        self.assertFalse(tf.is_valid())
        self.assertIsNone(tf.cleaned_data.get('slug'))

    def test_save(self):
        data = {
            'title': 'Django',
            'slug': 'django'
        }
        tf = TagForm(data)
        tag = tf.save()
        self.assertEquals(tag.title, data['title'])
        self.assertEquals(tag.slug, data['slug'])


class PostFormTests(TestCase):

    def setUp(self):
        user = User.objects.create_user(username='tom', password='123456789', email='e@mail.com')
        category = Category.objects.create(title='Category', slug='category')
        tag1 = Tag.objects.create(title='Tag', slug='tag')
        tag2 = Tag.objects.create(title='Django', slug='django')
        post = Post.objects.create(title='Post title',
                                   slug='post',
                                   body='Some text.',
                                   author=user.profile,
                                   category=category)
        post.tags.add(tag1)
        post.tags.add(tag2)

    def test_valid(self):
        user = Profile.objects.get(user__username='tom')
        tags = Tag.objects.all()
        category = Category.objects.get(slug='category')
        data = {
            'title': 'Post Title',
            'slug': 'slug',
            'body': 'Some text...',
            'category': category.id,
            'tags': tags,
            'cover': '',
            'author': user.id
        }
        pf = PostForm(data=data, initial={'user': user})
        self.assertTrue(pf.is_bound)
        self.assertTrue(pf.is_valid())

    def test_default_cover(self):
        user = Profile.objects.get(user__username='tom')
        tags = Tag.objects.all()
        category = Category.objects.get(slug='category')
        data = {
            'title': 'Post Title',
            'slug': 'slug',
            'body': 'Some text...',
            'category': category.id,
            'tags': tags,
            'cover': '',
            'author': user.id
        }
        pf = PostForm(data=data, initial={'user': user})
        self.assertTrue(pf.is_bound)
        self.assertTrue(pf.is_valid())
        self.assertEquals(pf.cleaned_data['cover'], 'static/images/posts/default-post-image.jpg')

    def test_save(self):
        user = Profile.objects.get(user__username='tom')
        tags = Tag.objects.all()
        category = Category.objects.get(slug='category')
        data = {
            'title': 'Post Title',
            'slug': 'slug',
            'body': 'Some text...',
            'category': category.id,
            'tags': tags,
            'cover': '',
            'author': user.id
        }
        pf = PostForm(data=data, initial={'author': user})
        self.assertTrue(pf.is_bound)
        self.assertTrue(pf.is_valid())
        if pf.is_valid():
            post = pf.save()
        self.assertEquals(post.title, data['title'])
        self.assertEquals(post.body, data['body'])
        self.assertEquals(list(post.tags.values_list()), list(tags.values_list()))
        self.assertEquals(post.category, category)
        self.assertEquals(post.author.user.id, user.id)


class CommentFormTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='tom', password='12345', email='e@mail.com')
        category = Category.objects.create(title='Category', slug='category')
        tag = Tag.objects.create(title='Tag', slug='tag')
        post = Post.objects.create(title='Post title',
                                   slug='post',
                                   body='Some text.',
                                   author=user.profile,
                                   category=category)
        post.tags.add(tag)

    def test_valid(self):
        post = Post.objects.get(slug='post')
        user = Profile.objects.get(user__username='tom')
        data = {
            'text': 'Comment to post',
            'post': post.id,
            'author': user.id
        }
        cf = CommentForm(data)
        self.assertTrue(cf.is_bound)
        self.assertTrue(cf.is_valid())

    def test_save(self):
        post = Post.objects.get(slug='post')
        user = Profile.objects.get(user__username='tom')
        data = {
            'text': 'Comment to post',
            'post': post.id,
            'author': user.id
        }
        cf = CommentForm(data)
        self.assertTrue(cf.is_bound)
        self.assertTrue(cf.is_valid())
        comment = cf.save()
        self.assertEquals(comment.post.id, post.id)
        self.assertEquals(comment.author.id, user.id)
        self.assertEquals(comment.text, data['text'])


class ReplyFormTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='tom', password='12345', email='e@mail.com')
        category = Category.objects.create(title='Category', slug='category')
        tag = Tag.objects.create(title='Tag', slug='tag')
        post = Post.objects.create(title='Post title',
                                   slug='post',
                                   body='Some text.',
                                   author=user.profile,
                                   category=category)
        post.tags.add(tag)
        Comment.objects.create(post=post, text='Hi', author=user.profile)

    def test_valid(self):
        post = Post.objects.get(slug='post')
        comment = post.comments.first()
        user = Profile.objects.get(user__username='tom')
        data = {
            'text': 'Comment to post',
            'comment': comment.id,
            'author': user.id
        }
        rf = ReplyForm(data)
        self.assertTrue(rf.is_bound)
        self.assertTrue(rf.is_valid())

    def test_save(self):
        post = Post.objects.get(slug='post')
        comment = post.comments.first()
        user = Profile.objects.get(user__username='tom')
        data = {
            'text': 'Comment to post',
            'comment': comment.id,
            'author': user.id
        }
        rf = ReplyForm(data)
        self.assertTrue(rf.is_bound)
        self.assertTrue(rf.is_valid())
        reply = rf.save()
        self.assertEquals(reply.comment.id, comment.id)
        self.assertEquals(reply.author.id, user.id)
        self.assertEquals(reply.text, data['text'])


class LikeTests(TestCase):

    def setUp(self):
        user = User.objects.create_user(username='tom', password='123456789', email='e@mail.com')
        category = Category.objects.create(title='Category', slug='category')
        tag = Tag.objects.create(title='Django', slug='django')
        post = Post.objects.create(title='Post title',
                                   slug='post',
                                   body='Some text.',
                                   author=user.profile,
                                   category=category)
        post.tags.add(tag)

    def test_like(self):
        profile = Profile.objects.get(user__username='tom')
        post = Post.objects.get(slug='post')
        id = post.id
        lf = LikeForm({
            'post': post.id,
            'profile': profile.id
        })
        self.assertTrue(lf.is_valid())
        post = lf.save()
        self.assertEquals(id, post.id)
        self.assertEquals(post.likes.count(), 1)
        self.assertEquals(Post.objects.all().count(), 1)

    def test_unlike(self):
        profile = Profile.objects.get(user__username='tom')
        post = Post.objects.get(slug='post')
        post_id = post.id
        lf = LikeForm({
            'post': post.id,
            'profile': profile.id
        })
        if lf.is_valid():
            post = lf.save()
        self.assertEquals(post_id, post.id)
        uf = UnlikeForm({
            'post': post.id,
            'profile': profile.id
        })
        self.assertTrue(uf.is_valid())
        post = uf.save()
        self.assertEquals(post_id, post.id)
        self.assertEquals(post.likes.count(), 0)
        self.assertEquals(Post.objects.all().count(), 1)
        self.assertEquals(Profile.objects.all().count(), 1)


class RegistrationFormTests(TestCase):

    def setUp(self):
        User.objects.create_user(username='tom', password='123456789', email='e@mail.com')

    def test_clean_username(self):
        rf = RegisterForm({
            'username': 'tom',
            'email': 'tom@mail.com',
            'password': 'tom2019',
            'confirm_password': 'tom2019',
            'full_name': 'Tom'
        })
        self.assertFalse(rf.is_valid())
        self.assertIsNone(rf.cleaned_data.get('username'))

    def test_clean_email(self):
        rf = RegisterForm({
            'username': 'ann',
            'email': 'e@mail.com',
            'password': 'ann2019',
            'confirm_password': 'ann2019',
            'full_name': 'Ann'
        })
        self.assertFalse(rf.is_valid())
        self.assertIsNone(rf.cleaned_data.get('email'))

    def test_clean_confirm_password(self):
        rf = RegisterForm({
            'username': 'ann',
            'email': 'ann@mail.com',
            'password': 'ann2019',
            'confirm_password': 'ann20191',
            'full_name': 'Ann'
        })
        self.assertFalse(rf.is_valid())

    def test_save(self):
        data = {
            'username': 'ann',
            'email': 'ann@mail.com',
            'password': 'ann2019',
            'confirm_password': 'ann2019',
            'full_name': 'Ann'
        }
        rf = RegisterForm(data)
        self.assertTrue(rf.is_valid())
        user = rf.save()
        self.assertEquals(data['username'], user.username)
        self.assertEquals(data['email'], user.email)
        self.assertEquals(data['full_name'], user.profile.full_name)
        self.assertEquals('static/images/users/default-user-image.jpg', user.profile.image)


class FeedbackTests(TestCase):

    def setUp(self):
        Feedback.objects.create(name='Tom', email='tom@mail.com', message='Hi, I\'m Tom!')

    def test_str(self):
        message = Feedback.objects.all().first()
        self.assertEquals(str(message), 'Tom | (tom@mail.com)')


class FeedbackFormTests(TestCase):

    def test_save(self):
        data = {
            'name': 'Tom',
            'email': 'tom@mail.com',
            'message': 'Hi, I\'m Tom!'
        }
        form = FeedbackForm(data)
        self.assertTrue(form.is_valid())
        message = form.save()
        self.assertEquals(message.name, data['name'])
        self.assertEquals(message.email, data['email'])
        self.assertEquals(message.message, data['message'])
