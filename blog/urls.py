from django.urls import path
from blog import views

urlpatterns = [
    path('', views.PostListView.as_view(), name= 'list'),
    path('new/', views.PostCreateView.as_view(), name= 'new'),
    path('<int:pk>/delete/', views.PostDeleteView.as_view(), name= 'delete'),
]