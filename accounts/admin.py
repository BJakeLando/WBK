from django.contrib import admin
from .models import LivePaintEvent
from .models import MyClientUser
from django.contrib.auth.models import Group,User

admin.site.unregister(Group)
admin.site.register(MyClientUser)


class UserAdmin(admin.ModelAdmin):
    model = User
    fields = [
        "username"
    ]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class UserAdmin(admin.ModelAdmin):
    model = MyClientUser
    # Just display username fields on admin page
    fields = ["username"]
    inlines = [MyClientUser]

@admin.register(LivePaintEvent)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'name','venue', 'event_date', 'email', 'budget', 'typeofclient',)
    ordering = ('created_on',)
    search_fields = ('name', 'venue', 'event_date',)
    list_filter = ('name', 'venue', 'event_date','budget',)