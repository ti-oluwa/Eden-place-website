from django import forms
from .models import Event, Tag


class EventCreateForm(forms.ModelForm):
    class Meta:
        model= Event
        fields = ["title", "brief", "content", "main_image", "sub_image1", "sub_image2","sub_image3", "sub_image4", "author", "video_link", "tags"]