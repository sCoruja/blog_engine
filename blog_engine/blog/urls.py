from django.conf.urls import url
from django.urls import path
from .views import *

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('<int:page>/', Index.as_view(), name='index'),
    path('about/', About.as_view(), name='about'),
    path('contact/', Contact.as_view(), name='contact'),

    path('post/create/', CreatePost.as_view(), name='create_post'),
    path('post/<slug>/', PostDetails.as_view(), name='post_details'),
    path('post/<slug>/update/', UpdatePost.as_view(), name='update_post'),
    path('post/<slug>/like/', LikePost.as_view(), name='like_post'),
    path('post/<slug>/pin/', PinPost.as_view(), name='pin_post'),
    path('post/<slug>/delete/', DeletePost.as_view(), name='delete_post'),

    path('tag/create/', CreateTag.as_view(), name='create_tag'),
    path('tag/<slug>/', TagPosts.as_view(), name='tag_posts'),
    path('tag/<slug>/<int:page>/', TagPosts.as_view(), name='tag_posts'),

    path('category/create/', CreateCategory.as_view(), name='create_category'),
    path('category/<slug>/', CategoryPosts.as_view(), name='category_posts'),
    path('category/<slug>/<int:page>', CategoryPosts.as_view(), name='category_posts'),

    path('account/', MyAccount.as_view(), name='my_account'),
    path('account/register/', Register.as_view(), name='register'),
    path('account/login/', Login.as_view(), name='login'),
    path('account/login/<path:from_url>', Login.as_view(), name='login'),
    path('account/logout/', Logout.as_view(), name='logout'),
    path('account/logout/<path:redirect_to>/', Logout.as_view(), name='logout'),
    path('account/favorite/<int:page>/', UserFavoritePosts.as_view(), name='user_favorite_posts'),
    path('account/posts/<int:page>/', UserPosts.as_view(), name='user_posts'),
    path('account/reset/', ResetPassword.as_view(), name='reset'),


    path('user/<username>/', UserAccount.as_view(), name='user_account'),
    path('user/<username>/<int:page>/', UserAccount.as_view(), name='user_account'),

    path('json/tags/', TagsList.as_view(), name='tags_list'),
    path('json/categories/', CategoriesList.as_view(), name='categories_list'),
    path('json/popular-posts/', PopularPosts.as_view(), name='popular_posts'),

    path('partial/user-info/', UserInfo.as_view(), name='user_info'),

    path('search/', Search.as_view(), name='search'),
    path('search/<query>/', Search.as_view(), name='search'),
    path('search/<query>/<int:page>/', Search.as_view(), name='search'),

    path('comment/', SendComment.as_view(), name='comment'),
    path('comment/<int:post>/', SendComment.as_view(), name='comment'),

    path('reply/', ReplyComment.as_view(), name='reply'),
    path('reply/<int:comment>/', ReplyComment.as_view(), name='reply'),

]