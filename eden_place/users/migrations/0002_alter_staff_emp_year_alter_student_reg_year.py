# Generated by Django 4.1 on 2023-01-18 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='emp_year',
            field=models.IntegerField(default=2023, verbose_name='employment year'),
        ),
        migrations.AlterField(
            model_name='student',
            name='reg_year',
            field=models.IntegerField(default=2023, verbose_name='registration year'),
        ),
    ]