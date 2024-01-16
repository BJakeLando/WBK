from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from .models import Review

class PostListView(ListView):
    template_name= "reviews/list.html"
    model = Review

class PostDetailView(DetailView):
    template_name = "reviews/detail.html"
    model = Review

class PostCreateView(CreateView):
    template_name = "reviews/new.html"
    model = Review
    fields = ['name','title', 'subtitle', 'body']