from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from .models import Faq, Event, Tag
from django.utils import timezone


FAQS= [
    {
        'question': 'What are the school hours?',
        'answer': 'The school opens at 8AM and closes at 3PM',
    },
    {
        'question': 'What is the dress code for pupils?',
        'answer': 'Pupils are expected to come to school wearing the appropriate uniforms for respective days of the week. Sport wears are worn on Wednesdays and the Friday wears for Fridays.',
    },
    {
        'question': 'How do I enroll my ward?',
        'answer': '',
    },
    {
        'question': 'What is the school policy on absences and tardiness?',
        'answer': '',
    },
    {
        'question': 'How do I pay for school fees and supplies?',
        'answer': '',
    },
    {
        'question': 'What are the school policy on bullying?',
        'answer': '',
    },
    {
        'question': 'What are the school policy on visitor in the school premises?',
        'answer': '',
    },
    {
        'question': "How do i contact my child's teacher?",
        'answer': '',
    },
    {
        'question': 'Are there after-school extracurricular activities available?',
        'answer': '',
    },
    {
        'question': "How do I access my child's grades or progress report",
        'answer': '',
    },
]

DEFAULT_TAGS = [
    {
        'name': 'Past',
        'description': "All past events"
    },
    {
        'name': 'Upcoming',
        'description': "All future events"
    },
    {
        'name': 'Open Day',
        'description': "All open day events"
    },
    
]


@receiver(post_migrate)
def add_default_faqs(**kwargs):
    for faq in FAQS:
        if not Faq.objects.filter(question=faq.get('question')).exists():
            new_faq = Faq.objects.create(question=faq.get('question'), answer=faq.get('answer'))
            new_faq.save()


@receiver(post_migrate)
def add_default_tags(**kwargs):
    for tag in DEFAULT_TAGS:
        if not Tag.objects.filter(name=tag.get('name').capitalize()).exists():
            new_tag = Tag.objects.create(name=tag.get('name').capitalize(), description=tag.get('description'))
            new_tag.save()


@receiver(post_save, sender=Event)
def auto_add_tags(sender, instance, created, **kwargs):
    if instance.date > timezone.now():
        if Tag.objects.filter(name__iexact="past").exists():
            tag = Tag.objects.filter(name__iexact="past").first()
            if tag in instance.tags.all():
                instance.tags.remove(tag)

        if Tag.objects.filter(name__iexact="upcoming").exists():
            tag = Tag.objects.filter(name__iexact="upcoming").first()
            if tag not in instance.tags.all():
                instance.tags.add(tag)
            
        else:
            tag =Tag.objects.create(name="upcoming", description="All future events")
            instance.tags.add(tag)

    else:
        if Tag.objects.filter(name__iexact="upcoming").exists():
            tag = Tag.objects.filter(name__iexact="upcoming").first()
            if tag in instance.tags.all():
                instance.tags.remove(tag)

        if Tag.objects.filter(name__iexact="past").exists():
            tag = Tag.objects.filter(name__iexact="past").first()
            if tag not in instance.tags.all():
                instance.tags.add(tag)

        else:
            tag =Tag.objects.create(name="past", description="All past events")
            instance.tags.add(tag)
    