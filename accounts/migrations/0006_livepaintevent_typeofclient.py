# Generated by Django 4.2.2 on 2024-08-11 21:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_remove_livepaintevent_source_livepaintevent_budget_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='livepaintevent',
            name='typeofclient',
            field=models.CharField(default=django.utils.timezone.now, max_length=128, verbose_name='typeofclient'),
            preserve_default=False,
        ),
    ]