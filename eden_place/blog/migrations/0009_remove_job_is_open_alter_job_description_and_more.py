# Generated by Django 4.1 on 2023-01-19 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_job'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='is_open',
        ),
        migrations.AlterField(
            model_name='job',
            name='description',
            field=models.TextField(max_length=700, null=True, verbose_name='Job description'),
        ),
        migrations.AlterField(
            model_name='job',
            name='title',
            field=models.CharField(max_length=50, null=True, verbose_name='Job title'),
        ),
    ]