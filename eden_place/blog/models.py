from django.utils import timezone
from django.db import models
from users.models import CustomUser
# from PIL import Image
from django.urls import reverse
from django.template.defaultfilters import slugify 


class Tag(models.Model):
    name= models.CharField(max_length=100)
    description = models.TextField(max_length=200, blank=True, null=True)
    created_by = models.ForeignKey(CustomUser,  null=True, blank=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.name = self.name.capitalize()
        return super().save()




class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(null=True, blank=True)
    brief = models.TextField(max_length=50, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    main_image = models.ImageField(upload_to="events_images", null=True, verbose_name="Main Image", help_text="Image size should be 960x400, also this image will be used as thumbnail")
    sub_image1 = models.ImageField(upload_to="events_images", blank=True, null=True, verbose_name="Sub Image 1")
    sub_image1_description = models.TextField(max_length=200, blank=True, null=True, verbose_name="Sub Image 1 Description")
    sub_image2 = models.ImageField(upload_to="events_images", blank=True, null=True , verbose_name="Sub Image 2")
    sub_image2_description = models.TextField(max_length=200, blank=True, null=True, verbose_name="Sub Image 2 Description")
    sub_image3= models.ImageField(upload_to="events_images", blank=True, null=True, verbose_name="Sub Image 3")
    sub_image3_description = models.TextField(max_length=200, blank=True, null=True, verbose_name="Sub Image 3 Description")
    sub_image4 = models.ImageField(upload_to="events_images", blank=True, null=True, verbose_name="Sub Image 4")
    sub_image4_description = models.TextField(max_length=200, blank=True, null=True, verbose_name="Sub Image 4 Description")
    video_link = models.URLField(null=True, blank=True, verbose_name="Video Link", help_text="Paste the link of the video here")
    video_description = models.TextField(max_length=200, blank=True, null=True, verbose_name="Video Description")
    author = models.ForeignKey(CustomUser, null=True, blank=True, on_delete= models.SET_NULL, related_name="events")
    tags = models.ManyToManyField(Tag, related_name="events")
    views = models.IntegerField(default=0, editable=False)
    date = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ['-date']

    def get_absolute_url(self):
        return reverse("event_detail", kwargs={"pk": self.pk})
    
    def __str__(self):
        return self.title.title()


    def save(self, *args, **kwargs):
        if not self.slug:
            count = len(Event.objects.filter(title=self.title.lower()))
            slug = slugify(self.title)
            if count > 0:
                self.slug = f"{slug}-{count}"
            else:
                self.slug = slug

        # images = [self.main_image, self.sub_image1, self.sub_image2, self.sub_image3, self.sub_image4]
        # for image in images:
        #     try:
        #         img = Image.open(image.path)
        #         if img.width > 960 or img.height > 400:
        #             output_size =(960, 400)
        #             img.thumbnail(output_size)
        #             img.save(image.path)
        #     except ValueError:
        #         pass
        #     except FileNotFoundError:
        #         pass
        #     except OSError:
        #         pass
        #     except AttributeError:
        #         pass
        #     except Exception as e:
        #         print(e)
        #         pass
        return super().save(*args, **kwargs)


class Faq(models.Model):
    question = models.TextField(max_length=200)
    answer = models.TextField(max_length=1024)
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['question']
        
    def __str__(self):
        return self.question[:20]+'...?' 