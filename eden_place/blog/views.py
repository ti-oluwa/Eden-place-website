from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import JsonResponse
from django.views.generic import CreateView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Event, Tag, Faq, Job
from .forms import EventCreateForm
from django.http import HttpResponseForbidden
import json
from django.utils import timezone
import datetime
from zoneinfo import ZoneInfo
from django.conf import settings

class EventCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    form_class = EventCreateForm
    template_name = 'blog/event_form.html'
    tags = Tag.objects.all().exclude(name='Upcoming').exclude(name='Past')
    model = Event

    def test_func(self):
        if self.request.user.is_admin or self.request.user.is_superuser:
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
                date_time = datetime.datetime(year=int(date[0]), month=int(date[1]), day=int(date[2]), hour=int(time[0]), minute=int(time[1]), tzinfo=ZoneInfo(settings.TIME_ZONE))
                thumbnail_img = all_files.get('thumbnail_img')
                other_images = []

                for key, value in all_files.items():
                    if key.startswith('other_image'):
                        image_description = descriptions.get('{}_description'.format(key))
                        other_images.append({'file': value, 'description': image_description})
                for _ in range(4-len(other_images)):
                    other_images.append(None)

                new_event = self.model.objects.create(title=title.lower(), content=content, main_image=thumbnail_img, date=date_time, author=request.user)
                for tag_name in selected_tags:
                    tag = get_object_or_404(Tag, name=tag_name.capitalize())
                    new_event.tags.add(tag)

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
            names = tag.get('name').split(',')
            description = tag.get('description')

            if description:
                description = description.strip()

            for name in names:
                if not Tag.objects.filter(name__iexact=name).exists() and name.strip():
                    name = name.strip()
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
        context['website_domain'] = settings.WEBSITE_DOMAIN
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
        context['website_domain'] = settings.WEBSITE_DOMAIN
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
        context['website_domain'] = settings.WEBSITE_DOMAIN
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
        object = get_object_or_404(self.model, slug=self.kwargs.get('slug'))
        object.views += 1
        object.save()
        return object



class FaqView(ListView):
    model = Faq
    context_object_name = 'faqs'
    template_name = 'blog/faq.html'



class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    '''View for updating a event'''
    model = Event
    template_name = 'blog/event_update.html'
    context_object_name = 'event'

    def get_object(self):
        obj_slug = self.kwargs.get('slug')
        return get_object_or_404(self.model, slug=obj_slug)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if is_ajax:
            pass
        else:
            return JsonResponse(data={'success': False}, status=200)

        try:
            event = self.get_object()
            data, files = request.POST, request.FILES
        
            if files:
                # set thumbnail image if changed
                if files.get('thumbnail_img'):
                    event.main_image = files.get('thumbnail_img')
                    
            if data:
                # Get data from request.POST- data
                descriptions = {}
                text_data = json.loads(data['text_data'])
                title = text_data.get('title')
                content = text_data.get('content')
                selected_tags = text_data.get('selected_tags')
                date = text_data.get('date').split('-')
                time = text_data.get('time').split(':')
                date_time = datetime.datetime(year=int(date[0]), month=int(date[1]), day=int(date[2]), hour=int(time[0]), minute=int(time[1]), tzinfo=ZoneInfo(settings.TIME_ZONE))
                imgs_received_ids = text_data.get('imgs_received_ids')
                changed = text_data.get('changed')
                imgs_sent_ids = [ img['id'] for img in self.get_sub_images() ]

                # Set img and descriptions of the ids of images that were sent on GET request and were not received back to None in the POST request. It means they were removed.
                for img_sent_id in imgs_sent_ids:
                    id = str(img_sent_id)
                    if id not in imgs_received_ids:
                        match id:
                            case '1':
                                event.sub_image1, event.sub_image1_description = None, None
                            case '2':
                                event.sub_image2, event.sub_image2_description = None, None
                            case '3':
                                event.sub_image3, event.sub_image3_description = None, None
                            case '4':
                                event.sub_image4, event.sub_image4_description = None, None

                # get all image descriptions in the text_data
                for key, value in data.items():
                    if key.endswith('description'):
                        descriptions.update({key: value})
                # set new title if changed
                if event.title.lower() != title.lower():
                    event.title == title

                # set new content if changed
                if event.content != content:
                    event.content = content

                # remove removed tags
                for tag in event.tags.all():
                    if tag.name.lower() not in [ tag_name.lower() for tag_name in selected_tags ]:
                        event.tags.remove(tag)
                

                # add new tags
                if selected_tags:
                    for tag_name in selected_tags:
                        try:
                            tag = Tag.objects.get(name=tag_name.capitalize())
                            if tag not in event.tags.all():
                                event.tags.add(tag)
                        except Tag.DoesNotExist:
                            pass

                
                # set new date if changed
                if event.date != date_time:
                    event.date = date_time

                if files:
                    # Implement new changes made to the images sent with the GET request
                    for changed_img_detail in changed:
                        img_id = changed_img_detail.get('img_id')
                        if img_id in imgs_received_ids:
                            new_filename = changed_img_detail.get('filename')
                            new_description = "%s_description" % new_filename

                            if img_id == "1":
                                event.sub_image1 = files.get(new_filename, None)
                                event.sub_image1_description = descriptions.get(new_description, '')
                            elif img_id == "2":
                                event.sub_image2 = files.get(new_filename, None)
                                event.sub_image2_description = descriptions.get(new_description, '')
                            elif img_id == "3":
                                event.sub_image3 = files.get(new_filename, None)
                                event.sub_image3_description = descriptions.get(new_description, '')
                            elif img_id == "4":
                                event.sub_image4 = files.get(new_filename, None)
                                event.sub_image4_description = descriptions.get(new_description, '')
                    
                    # add new images sent with POST request    
                    changed_imgs_names = [ changed_img_det.get('filename') for changed_img_det in changed ]
                    new_images = []
                    for key, value in files.items():
                        if key.startswith('other_image') and key not in changed_imgs_names:
                            image_description = descriptions.get('{}_description'.format(key), '')
                            new_images.append({'name': key, 'file': value, 'description': image_description})

                    for image in new_images:
                        if 'other_image_1' in image['name']:
                            event.sub_image1 = image.get('file', None)
                            event.sub_image1_description = image.get('description', '')

                        elif 'other_image_2' in image['name']:
                            event.sub_image2 = image.get('file', None)
                            event.sub_image2_description = image.get('description', '')

                        elif 'other_image_3' in image['name']:
                            event.sub_image3 = image.get('file', None)
                            event.sub_image3_description = image.get('description', '')

                        elif 'other_image_4' in image['name']:
                            event.sub_image4 = image.get('file', None)
                            event.sub_image4_description = image.get('description', '')

                event.save()      

            return JsonResponse(data={'success': True, 'event_slug': event.slug}, status=200)
        
        except Exception as e:
            print(e)
            return JsonResponse(data={'success': False}, status=200)


    def get_context_data(self, **kwargs):
        context = {}
        object = self.get_object()
        context['event'] = object
        all_tags = Tag.objects.all()

        for tag in object.tags.all():
            all_tags = all_tags.exclude(id=tag.id)

        context['all_tags'] = all_tags
        context['other_imgs'] = self.get_sub_images()
        return context

    def test_func(self):
        if self.request.user.is_admin or self.request.user.is_superuser:
            return True
        return False

    def get_sub_images(self):
        object = self.get_object()
        sub_images = []
        count = 0
        if object.sub_image1:
            count += 1
            sub_images.append({'id': 1, 'image_url': object.sub_image1.url, 'image_file_size': object.sub_image1.file.size, 'description': object.sub_image1_description, "count": count})
        
        if object.sub_image2:
            count += 1
            sub_images.append({'id': 2, 'image_url': object.sub_image2.url, 'image_file_size': object.sub_image2.file.size, 'description': object.sub_image2_description, "count": count})
        
        if object.sub_image3:
            count += 1
            sub_images.append({'id': 3, 'image_url': object.sub_image3.url, 'image_file_size': object.sub_image3.file.size, 'description': object.sub_image3_description, "count": count})
        
        if object.sub_image4:
            count += 1
            sub_images.append({'id': 4, 'image_url': object.sub_image4.url, 'image_file_size': object.sub_image4.file.size, 'description': object.sub_image4_description, "count": count})

        return sub_images


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    '''View for deleting a event'''
    model = Event
    success_url = "/events/"

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        object.delete()
        return redirect(self.success_url)

    def test_func(self, **kwargs):
        if self.request.user.is_superuser or self.request.user.is_admin or self.request.user == get_object_or_404(Event, id=kwargs.get('pk')).author:
            return True
        return False

    def get_object(self):
        slug = self.kwargs.get('slug', '')
        return get_object_or_404(self.model, slug=slug)


class JobListView(ListView):
    '''View that returns the list of available jobs openings if application is still open'''
    model = Job
    template_name = 'blog/jobs.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        qs = super().get_queryset().filter(application_ends__gte=timezone.now().date())
        return qs