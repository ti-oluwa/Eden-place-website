# Generated by Django 4.1 on 2023-01-18 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_alter_faq_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faq',
            name='question',
            field=models.TextField(max_length=150),
        ),
    ]
