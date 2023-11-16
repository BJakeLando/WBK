from django.db import models
from django.template.defaultfilters import slugify
from django_resized import ResizedImageField
from django.utils import timezone
from uuid import uuid4
from django.conf import settings
from django.urls import reverse


class Category(models.Model):
    title = models.CharField(null=True, blank=True, max_length=200)

    # utility variables
    uniqueID = models.CharField(null = True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null= True)
    date_created = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{} {}'.format(self.title, self.uniqueID)
    
    def get_absolute_url(self):
        return reverse('category-detail', kwargs={'slug':self.slug})
    
    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueID is None:
            self.uniqueID = str(uuid4()).split('-')[4]
            self.slug = slugify('{} {}'.format(self.title, self.uniqueID))

        self.slug = slugify('{} {}'.format(self.title, self.uniqueID))
        self.last_updated = timezone.localtime(timezone.now())
        super(Category, self).save(*args, **kwargs)

class Image(models.Model):
    description = models.TextField(null=True, blank=True)

    # Related FIelds
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)

    # Image Fields
    squareImage = ResizedImageField(size=[1000,1000], crop=['middle','center'], default='default_square.jpg', upload_to='square')
    landImage = ResizedImageField(size=[2878,1618], crop=['middle','center'], default='default_land.jpg', upload_to='landscape')
    tallImage = ResizedImageField(size=[1618,2878], crop=['middle','center'], default='default_tall.jpg', upload_to='tall')

    # utility variables
    uniqueID = models.CharField(null = True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null= True)
    date_created = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '{} {}'.format(self.category.title, self.uniqueID)
    
    def get_absolute_url(self):
        return reverse('image-detail', kwargs={'slug':self.slug})
    
    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueID is None:
            self.uniqueID = str(uuid4()).split('-')[4]
            self.slug = slugify('{} {}'.format(self.category.title, self.uniqueID))

        self.slug = slugify('{} {}'.format(self.category.title, self.uniqueID))
        self.last_updated = timezone.localtime(timezone.now())
        super(Image, self).save(*args, **kwargs)