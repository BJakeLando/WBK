from django.contrib import admin
from django.urls import path
from .views import (
    SignupView,
)
from . import views

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('add_venue', views.add_event, name='add-event'),
    path('<int:pk>/delete/', views.EventDeleteView.as_view(), name='delete_event'),
]