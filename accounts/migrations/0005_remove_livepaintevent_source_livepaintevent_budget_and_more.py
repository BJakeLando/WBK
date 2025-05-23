# Generated by Django 4.2.2 on 2024-08-11 21:16

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_livepaintevent_description_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='livepaintevent',
            name='source',
        ),
        migrations.AddField(
            model_name='livepaintevent',
            name='budget',
            field=models.CharField(default=django.utils.timezone.now, max_length=555, verbose_name='Estimated Budget'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='livepaintevent',
            name='choice',
            field=models.CharField(default=django.utils.timezone.now, max_length=555, verbose_name='Guest Painting'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='livepaintevent',
            name='description',
            field=models.TextField(max_length=1200, verbose_name='Theme'),
        ),
        migrations.AlterField(
            model_name='livepaintevent',
            name='venue',
            field=models.CharField(max_length=128, verbose_name='Venue Location (City, St.)'),
        ),
    ]
