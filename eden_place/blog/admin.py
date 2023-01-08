from django.contrib import admin
from .models import Event, Tag, Faq

admin.site.register(Tag)
admin.site.register(Event)
admin.site.register(Faq)