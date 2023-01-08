from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import JsonResponse
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from .models import Event, Tag, Faq
from users.models import Student, Staff
from .forms import EventCreateForm
from django.http import Http404, HttpResponseForbidden
import json
from django.utils import timezone
import datetime

class EventCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    form_class = EventCreateForm
    template_name = 'blog/event_form.html'
    tags = Tag.objects.all()
    model = Event

    def test_func(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        return False

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
        
    def get(self, request, *args, **kwargs):
        context = {
            'all_tags': self.tags[:30],
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if is_ajax:
            payload = request.POST
            try:
                text_data, all_files = json.loads(payload.get('text_data')), request.FILES
                descriptions = {}
                for key, value in payload.items():
                    if key.endswith('description'):
                        descriptions.update({key: value})

                title = text_data.get('title')
                selected_tags = text_data.get('selected_tags')
                content = text_data.get('content')
                date = text_data.get('date').split('-')
                time = text_data.get('time').split(':')
                date_time = datetime.datetime(year=int(date[0]), month=int(date[1]), day=int(date[2]), hour=int(time[0]), minute=int(time[1]))
                thumbnail_img = all_files.get('thumbnail_img')
                other_images = []

                for key, value in all_files.items():
                    if key.startswith('other_image'):
                        image_description = descriptions.get('{}_description'.format(key))
                        other_images.append({'file': value, 'description': image_description})
                for i in range(4-len(other_images)):
                    other_images.append(None)

                new_event = self.model.objects.create(title=title.lower(), content=content, main_image=thumbnail_img, date=timezone.make_aware(date_time), author=request.user)
                for tag in selected_tags:
                    new_event.tags.add(Tag.objects.filter(name=tag).first())

                if other_images[0]:
                    new_event.sub_image1 = other_images[0].get('file')
                    new_event.sub_image1_description = other_images[0].get('description')
                if other_images[1]:
                    new_event.sub_image2 = other_images[1].get('file')
                    new_event.sub_image2_description = other_images[1].get('description')
                if other_images[2]:
                    new_event.sub_image3 = other_images[2].get('file')
                    new_event.sub_image3_description = other_images[2].get('description')
                if other_images[3]:
                    new_event.sub_image4 = other_images[3].get('file')
                    new_event.sub_image4_description = other_images[3].get('description')

                new_event.save()
                return JsonResponse({'success': True, 'event_slug': new_event.slug}, status=200)

            except (KeyError, IndexError) as e:
                print(e)

        else:
            return JsonResponse(data={'success': False}, status=200)




class TagCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    model = Tag

    def test_func(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        return False


    def post(self, request, *args, **kwargs):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if is_ajax:
            tag = request.POST
            name = tag.get('name')
            description = tag.get('description')
            if not Tag.objects.filter(name__iexact=name).exists() and name.strip():
                new_tag = self.model.objects.create(name=name, description=description, created_by=request.user)
                return JsonResponse(data={'tag': new_tag.name, 'success': True}, status=200)
            else:
                return JsonResponse(data={'success': False}, status=200)
            
        return HttpResponse(status=400)




class HomeView(View):
    '''View for the home page'''
    model = Event
    template_name = 'blog/index.html'
    context_object_name = 'events'
    context = {}

    def get(self, request):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request):
        return HttpResponseForbidden(request, status=403)

    def get_context_data(self, **kwargs):
        self.context['upcoming_events'] = self.get_queryset().filter(tags__name='Upcoming')[:4]
        self.context['recent_events'] = self.get_queryset()[:4]
        return self.context

    def get_queryset(self):
        return self.model.objects.all().order_by('-date')
    


class EventsListView(ListView):
    '''View for the list of events'''
    model = Event
    template_name = 'blog/events.html'

    def get_queryset(self):
        return self.model.objects.filter(tags__name='Upcoming'), self.model.objects.filter(date__lt=timezone.now().date())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_events'] = self.get_queryset()[0].order_by('-date')[:3]
        context['past_events'] = self.get_queryset()[1].order_by('-date')[:8]
        return context



class TagEventListView(ListView):
    '''View for the list of events'''
    model= Event
    context_object_name = "events"
    template_name = 'blog/event_list.html'
    paginate_by = 12

    def get_queryset(self):
        if self.request.GET.get('tag').lower() == 'all':
            return self.model.objects.all().order_by('-date')
        return self.model.objects.filter(tags__name=self.request.GET.get('tag')).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.request.GET.get('tag')
        return context



class EventDetailView(DetailView):
    '''View for the detail of a event'''
    model= Event
    context_object_name = 'event'
    template_name = 'blog/event_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['all_tags'] = Tag.objects.all()
        object = self.get_object()
        sub_images = [ {'file': object.sub_image1, 'description': object.sub_image1_description}, 
                                {'file': object.sub_image2, 'description': object.sub_image2_description},
                                {'file': object.sub_image3, 'description': object.sub_image3_description},
                                {'file': object.sub_image4, 'description': object.sub_image4_description}
                                ]
        context['sub_images'] = []
        for image in sub_images:
            if image.get('file'):
                context['sub_images'].append(image)
        context['suggestions']  = Event.objects.all().exclude(slug=object.slug).order_by('-date')[:4]     
        return context

    def get_object(self):
        object = Event.objects.filter(slug=self.kwargs.get('slug'))[0]
        object.views += 1
        object.save()
        return object



class FaqView(ListView):
    model = Faq
    context_object_name = 'faqs'
    template_name = 'blog/faq.html'



class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    '''View for updating a event'''
    model = Event
    fields = ['title', 'overview', 'content', 'tags', 'thumbnail', 'sub_image1', 'sub_image2', 'sub_image3', 'sub_image4', 'video']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return True
        return False


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''View for deleting a event'''
    model = Event
    success_url = "/"

    def test_func(self, **kwargs):
        if self.request.user.is_superuser or self.request.user == get_object_or_404(Event, id=kwargs.get('pk')).author:
            return True
        return False
    



