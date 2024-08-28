from django.contrib import admin
from embed_video.admin import AdminVideoMixin
from .models import Video

class AdminVideoMixin(AdminVideoMixin):
    pass

admin.site.register(Video)