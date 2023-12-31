# Generated by Django 4.2.6 on 2023-11-12 20:51

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='landImage',
            field=django_resized.forms.ResizedImageField(crop=['middle', 'center'], default='default_land.jpg', force_format=None, keep_meta=True, quality=75, scale=None, size=[2878, 1618], upload_to='landscape'),
        ),
        migrations.AddField(
            model_name='image',
            name='squareImage',
            field=django_resized.forms.ResizedImageField(crop=['middle', 'center'], default='default_square.jpg', force_format=None, keep_meta=True, quality=75, scale=None, size=[1000, 1000], upload_to='square'),
        ),
        migrations.AddField(
            model_name='image',
            name='tallImage',
            field=django_resized.forms.ResizedImageField(crop=['middle', 'center'], default='default_tall.jpg', force_format=None, keep_meta=True, quality=75, scale=None, size=[1618, 2878], upload_to='tall'),
        ),
    ]
