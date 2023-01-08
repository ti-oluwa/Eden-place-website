from django.urls import path
from .views import HomeView, EventCreateView, EventDeleteView, TagEventListView, EventDetailView, EventUpdateView, EventsListView, TagCreateView, FaqView
from django.views.generic import TemplateView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('enroll/', TemplateView.as_view(template_name='blog/enroll.html'), name='enroll'),
    path('about/', TemplateView.as_view(template_name='blog/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='blog/contact.html'), name='contact'),
    path('faqs/', FaqView.as_view(), name='faqs'),
    path('events/', EventsListView.as_view(), name='events'),
    path('events/publish/', EventCreateView.as_view(), name='publish'),
    path('all-events/', TagEventListView.as_view(), name="tag_events"),
    path('events/<str:slug>/', EventDetailView.as_view(), name="event_detail"),
    path('tags/create/', TagCreateView.as_view(), name="create_tag"),
    path('articles/create/', EventCreateView.as_view(), name="create_article"),
    path('article/<int:pk>/delete/', EventDeleteView.as_view(), name="delete_article"),
    path('article/<int:pk>/update/', EventUpdateView.as_view(), name="update_article"),
]