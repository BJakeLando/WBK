from django.db import models

# Create your models here.
from django.urls import reverse

class Review(models.Model):
    name = models.CharField(max_length=128)
    title = models.CharField(max_length=256)
    subtitle =models.CharField(max_length=256)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    source =models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('detail', args = [self.id])
