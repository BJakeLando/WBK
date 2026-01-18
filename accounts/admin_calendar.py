from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from .models import LivePaintEvent
import json
from datetime import datetime

class CalendarAdminMixin:
    """Mixin to add calendar view to admin"""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('calendar/', self.admin_site.admin_view(self.calendar_view), name='livepaintevent_calendar'),
            path('calendar/events/', self.admin_site.admin_view(self.calendar_events), name='livepaintevent_calendar_events'),
        ]
        return custom_urls + urls
    
    def calendar_view(self, request):
        """Render the calendar view"""
        return render(request, 'admin/calendar.html', {
            'title': 'Event Calendar',
            'site_header': admin.site.site_header,
            'site_title': admin.site.site_title,
        })
    
    def calendar_events(self, request):
        """Return events as JSON for FullCalendar"""
        events = LivePaintEvent.objects.all()
        event_list = []
        
        for event in events:
            event_list.append({
                'id': event.id,
                'title': f"{event.name} - {event.venue}",
                'start': event.event_date.isoformat(),
                'url': f'/admin/accounts/livepaintevent/{event.id}/change/',
                'backgroundColor': '#ff6b9d',  # Valentine's pink!
                'borderColor': '#c94b7d',
                'extendedProps': {
                    'venue': event.venue,
                    'email': event.email,
                    'phone': event.phone,
                }
            })
        
        return JsonResponse(event_list, safe=False)