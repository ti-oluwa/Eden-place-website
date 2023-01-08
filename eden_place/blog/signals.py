from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from .models import Faq


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


@receiver(post_migrate)
def add_default_faqs(**kwargs):
    for faq in FAQS:
        if not Faq.objects.filter(question=faq.get('question')).exists():
            new_faq = Faq.objects.create(question=faq.get('question'), answer=faq.get('answer'))
            new_faq.save()