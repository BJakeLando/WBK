from django.contrib import admin
from .models import LivePaintEvent, MyClientUser
from django.contrib.auth.models import Group, User
from .admin_calendar import CalendarAdminMixin

admin.site.unregister(Group)
admin.site.register(MyClientUser)

class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(LivePaintEvent)
class LivePaintEventAdmin(CalendarAdminMixin, admin.ModelAdmin):
    list_display = ('created_on', 'name', 'venue', 'event_date', 'email', 'budget', 'typeofclient',)
    ordering = ('-created_on',)
    search_fields = ('name', 'venue', 'event_date',)
    list_filter = ('name', 'venue', 'event_date', 'budget',)
    
    # Add calendar link to admin
    change_list_template = 'admin/livepaintevent_changelist.html'