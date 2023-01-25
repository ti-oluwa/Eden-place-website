from django.contrib import admin
from .models import Event, Tag, Faq, Job

admin.site.register(Tag)
admin.site.register(Event)
admin.site.register(Faq)
admin.site.register(Job)