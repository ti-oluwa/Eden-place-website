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
        'answer': 'To enroll your ward in our school, please visit our website and submit an online application form or visit us physically',
    },
    {
        'question': 'What is the school policy on absences and tardiness?',
        'answer': 'Our school policy on absences and tardiness is that regular attendance is essential for academic success and that any pupil who is absent or tardy for more than a certain number of days may be referred to the attendance office for further action. We encourage parents to contact the school if their child will be absent and pupils are expected to make up any missed work in a timely manner.',
    },
    {
        'question': 'How do I pay for school fees and supplies?',
        'answer': "School fees and supplies can be paid online through the use of a credit card or bank transfer. Alternatively, you can also pay in person at the school's finance office by cash, check or credit card. If you have any questions or need assistance with the payment process, please contact our finance office for further information.",
    },
    {
        'question': 'What are the school policy on bullying?',
        'answer': "Our school has a zero-tolerance policy on bullying. Bullying is not only unacceptable but it is also illegal. We take all reports of bullying seriously and will take immediate action to address any such behavior. Our school has a comprehensive anti-bullying program in place, which includes education, prevention, and intervention strategies to address bullying. Any pupil who engages in bullying behavior will be subject to disciplinary action, which may include suspension or expulsion. Additionally, we encourage pupils, staff, and families to report any incidents of bullying to school administration or designated staff for appropriate action. We are committed to creating a safe and respectful learning environment for all pupils.",
    },
    {
        'question': 'What are the school policy on visitor in the school premises?',
        'answer': "Our school has a policy of strict visitor management to ensure the safety and security of our pupils and staff. Visitors are required to check-in at the main office and show a valid means of identification before being granted access to the school premises. Visitors will be given a badge to wear while on campus. Visitors are allowed only in designated areas and are prohibited from entering classrooms or other areas without prior permission from the school administrator. Visitors who refuse to check-in or comply with school policies may be asked to leave the premises. Additionally, parents and legal guardians are welcome to visit their children's classrooms but should make an appointment with the teacher in advance.",
    },
    {
        'question': "How do i contact my child's teacher?",
        'answer': "You can contact your child's teacher by sending an email or a note to the teacher through your child, or by calling the school's main office and asking to speak with the teacher. Our school also uses an online communication platform where you can contact your child's teacher and get updated on their academic progress and upcoming assignments. You can also schedule a parent-teacher conference with your child's teacher through the school office. If you have any questions or concerns, please do not hesitate to reach out to your child's teacher or to the school administration for assistance.",
    },
    {
        'question': 'Are there after-school extracurricular activities available?',
        'answer': "Yes, our school offers a variety of after-school extracurricular activities for pupils to participate in. These activities are designed to provide pupils with opportunities to explore their interests, develop new skills, and build friendships outside of the classroom. Some examples of extracurricular activities offered at our school include sports teams, robotics clubs, music and theater programs, and academic clubs. The list of activities is updated regularly, and the school office or website will have the most current information. Participation in extracurricular activities is optional and pupils are encouraged to find the activity that best aligns with their interests and schedule.",
    },
    {
        'question': "How do I access my child's grades or progress report?",
        'answer': "Our school uses an online pupil information system that allows parents and guardians to access their child's grades and progress reports. You can access the system using a unique login and password that will be provided by the school. Once logged in, you will be able to view your child's grades, assignments, and attendance records, as well as any other relevant information regarding their academic progress. You can also receive email notifications when new grades are posted or when there are upcoming assignments. If you have any issues or need assistance accessing the system, please contact the school office or the IT department for help. Additionally, you can schedule a meeting with your child's teacher if you want to discuss your child's progress or have any specific concerns.",
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
    