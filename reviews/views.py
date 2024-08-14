from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from .models import Review

class PostListView(ListView):
    template_name= "reviews/list.html"
    model = Review

    def list_reviews(self,name):
        issue_list = Review.objects.all().order_by('created_on')
        return issue_list
          


class PostDetailView(DetailView):
    template_name = "reviews/detail.html"
    model = Review

class PostCreateView(CreateView):
    template_name = "reviews/new.html"
    model = Review
    fields = ['name','title', 'body', 'source']