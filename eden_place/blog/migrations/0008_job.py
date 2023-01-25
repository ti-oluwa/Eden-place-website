# Generated by Django 4.1 on 2023-01-18 23:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_alter_faq_question'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, null=True, verbose_name='Job Title')),
                ('description', models.TextField(max_length=700, null=True, verbose_name='Job Description')),
                ('application_url', models.URLField(help_text='Enter the link to the page where the applicants can apply for the job post.', verbose_name='Link to application page')),
                ('is_open', models.BooleanField(default=False)),
                ('application_starts', models.DateField(default=django.utils.timezone.now, verbose_name='Application starting date')),
                ('application_ends', models.DateField(verbose_name='Application ending date')),
            ],
            options={
                'ordering': ['-application_starts'],
            },
        ),
    ]