# Generated by Django 4.2.6 on 2024-05-29 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_livepaintevent_instagram'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livepaintevent',
            name='description',
            field=models.TextField(max_length=255),
        ),
        migrations.AlterField(
            model_name='livepaintevent',
            name='email',
            field=models.EmailField(max_length=256, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='livepaintevent',
            name='source',
            field=models.TextField(max_length=555),
        ),
    ]
