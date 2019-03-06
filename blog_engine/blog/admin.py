from django.contrib import admin
from .models import *

admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(PinnedPost)
admin.site.register(Feedback)


