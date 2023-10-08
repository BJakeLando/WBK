from django.db import models
from django.contrib.auth.models import User

class LivePaintEvent(models.Model):
    name = models.CharField('Client Name',max_length=128)
    phone = models.CharField('Phone',max_length=60)
    event_date = models.DateField('Event Date')
    venue = models.CharField('Venue Location', max_length=128)
    guest_count= models.CharField('Estimated Guest Count', max_length=128)
    reference = models.CharField('How Did You Hear About Us?', max_length=128)
    wedding_planner =  models.CharField('Event Planner Name',max_length=128)
    description = models.TextField(blank = True)
    email = models.EmailField('Email', max_length=256, blank=True) 

    def __str__(self):
        return self.name
    

class MyClientUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField('First Name',max_length=30)
    last_name = models.CharField('Last Name',max_length=30)
    phone = models.CharField('Phone',max_length=60)
    email = models.EmailField('Email', max_length=256, blank=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name