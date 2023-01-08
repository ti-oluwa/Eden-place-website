from .views import auth
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Staff, Student, CustomUser
from django.contrib.auth.hashers import make_password


@receiver(post_save, sender=Student)
def create_user(sender, instance, created, **kwargs):
    if created:
        count = Student.objects.filter(reg_year=instance.reg_year).count()
        instance.set_reg_no(count=count)
        instance.set_age()        
        if instance.email:
            user_obj = CustomUser.objects.create(user_id=instance.reg_no, email=instance.email, is_student=True, username=instance.__str__(), password=make_password(str(instance.last_name).lower()))
        else:
            user_obj = CustomUser.objects.create(user_id=instance.reg_no, is_student=True, username=instance.__str__(), password=make_password(str(instance.last_name).lower()))          
        instance.user_obj = CustomUser.objects.get(user_id=instance.reg_no)
        instance.save() 

@receiver(post_delete, sender=Student)
def delete_user(sender, instance, **kwargs):
    if instance.user_obj:
        try:
            user_obj = CustomUser.objects.get(user_id=instance.reg_no)
            return user_obj.delete()
        except CustomUser.DoesNotExist:
            pass
    return None




@receiver(post_save, sender=Staff)
def create_user(sender, instance, created, **kwargs):
    if created:
        count = Staff.objects.filter(emp_year=instance.emp_year).count()
        instance.set_staff_id(count=count)
        instance.set_age()
        if instance.email:
            user_obj = CustomUser.objects.create(user_id=instance.staff_id, email=instance.email, is_staff=True, is_student=False, username=instance.__str__(),  password=make_password(str(instance.last_name).lower()))
        else:
            user_obj = CustomUser.objects.create(user_id=instance.staff_id, is_staff=True, is_student=False, username=instance.__str__(),  password=make_password(str(instance.last_name).lower()))
        instance.user_obj = CustomUser.objects.get(user_id=instance.staff_id)
        instance.save()

@receiver(post_delete, sender=Staff)
def delete_user(sender, instance, **kwargs):
    if instance.user_obj:
        try:
            user_obj = CustomUser.objects.get(user_id=instance.staff_id)
            return user_obj.delete()
        except CustomUser.DoesNotExist:
            pass
    return None


   




