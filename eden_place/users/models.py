from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from .managers import CustomUserManager
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image
from django.utils import timezone
import math


def get_profile_image_filepath():
    return 'profile_images/'

def get_default_profile_image():
    return "default.png"


CLASSES = (
    ("primary_school", "Primary School"),
    ("preschool_one", "Preschool 1"),
    ("preschool_two", "Preschool 2"),
    ("nursery_one", "Nursery 1"),
    ("nursery_two", "Nursery 2"),
    ("grade_one", "Grade 1"),
    ("grade_two", "Grade 2"),
    ("grade_three", "Grade 3"),
    ("grade_four", "Grade 4"),
    ("grade_five", "Grade 5"),
)


POSTS = (
    ("head_teacher", "Head Teacher"),
    ("hod_nursery", "HOD Nursery"),
    ("hod_primary", "HOD Primary"),
    ("class_teacher", "Class Teacher"),
    ("janitor", "Janitor"),
    ("driver", "Driver"),
)

MARITAL_STATUS = (
    ("single", "Single"),
    ("married", "Married"),
)

GENDERS = (
    ("male", "Male"),
    ("female", "Female"),
    ("prefer not to say", "Prefer not to say"),
)





class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(unique=True, max_length=50)
    username = models.CharField(default=None, blank=True, max_length=60)
    email = models.EmailField(null=True, blank=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    hide_email = models.BooleanField(default=True)

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ["username", "email"]

    objects = CustomUserManager()

    def __str__(self):
        if self.username:
            return self.username
        return self.user_id


    def get_profile_image_filename(self):
        return str(self.profile_image)[str(self.profile_image).index('profile_images/' + str(self.pk) + "/"):]

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True

    


class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    other_name = models.CharField(default=None, max_length=50, blank=True)
    user_obj = models.OneToOneField(CustomUser, on_delete=models.PROTECT, null=True, blank=True, related_name="student_details", editable=False)
    phone = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(max_length=60)
    gender = models.CharField(choices=GENDERS, max_length=50)
    dob = models.DateField(verbose_name="Date of Birth")
    age = models.IntegerField(default=0)
    related_to = models.ManyToManyField(CustomUser, default=None, blank=True, related_name="related_students")
    address = models.TextField(null=True, blank=True)
    fathers_name = models.CharField(max_length=100, null=True, blank=True)
    mothers_name = models.CharField(max_length=100, null=True, blank=True)
    guardians_name = models.CharField(max_length=100, null=True, blank=True)
    fathers_mail = models.EmailField(max_length=60, null=True, blank=True)
    mothers_mail = models.EmailField(max_length=60, null=True, blank=True)
    guardians_mail = models.EmailField(max_length=60, null=True, blank=True)
    fathers_phone_1 = PhoneNumberField(null=True, blank=True)
    fathers_phone_2 = PhoneNumberField(null=True, blank=True)
    mothers_phone_1 = PhoneNumberField(null=True, blank=True)
    mothers_phone_2 = PhoneNumberField(null=True, blank=True)
    guardians_phone_1 = PhoneNumberField(null=True, blank=True)
    guardians_phone_2 = PhoneNumberField(null=True, blank=True)
    class_name = models.CharField(max_length=50, choices=CLASSES)
    profile_image = models.ImageField(max_length=255, upload_to=get_profile_image_filepath, blank=True, default=get_default_profile_image)
    reg_year = models.IntegerField(default=timezone.now().today().year, verbose_name="registration year")
    reg_date = models.DateField(default=timezone.now, verbose_name="registration date")
    reg_no = models.CharField(verbose_name="registration number", unique=True, max_length=50, blank=True, null=True)
    is_idd = models.BooleanField(default=False, editable=False)
    
    def set_reg_no(self, count:int=0):
        if self.is_idd:
            pass
        else:
            l_i = list(self.last_name)[0].upper()
            f_i = list(self.first_name)[0].upper()
            year = str(timezone.now().today().year)
            number = str(count)
            zeros = '0' * (4 - len(number))
            number = zeros + number
            if number == '0000':
                number = '0001'
            year = "".join(list(year)[2:4])
            self.reg_no = 'EPWD/{}/{}{}{}'.format(number, l_i, f_i, year)
            self.is_idd = True

    def set_age(self):
        dob = self.dob
        today = date.today()
        age_in_months = (today.year - dob.year) * 12 - (today.month - dob.month)
        age = math.floor(age_in_months/12)
        self.age = age


    def __str__(self):
        if self.last_name:
            return "{} {} {}".format(self.last_name, self.first_name, self.other_name)
        return "{} {}".format(self.last_name, self.first_name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.profile_image.path)
            if img.width > 400 or img.height > 400:
                output_size =(400, 400)
                img.thumbnail(output_size)
                img.save(self.profile_image.path)
        except ValueError:
            pass
        except FileNotFoundError:
            pass
        except OSError:
            pass
        except AttributeError:
            pass
        except Exception as e:
            print(e)
            pass
        return super().save(*args, **kwargs)







class Staff(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    other_name = models.CharField(default=None, max_length=50, blank=True)
    user_obj = models.OneToOneField(CustomUser, on_delete=models.PROTECT, null=True, blank=True, related_name="staff_details", editable=False)
    phone1 = PhoneNumberField()
    phone2 = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    gender = models.CharField(choices=GENDERS, max_length=50)
    dob = models.DateField(verbose_name="Date of Birth")
    age = models.IntegerField(default=0)
    related_to = models.ManyToManyField(CustomUser, default=None, blank=True, related_name="related_staffs")
    address = models.TextField(null=True, blank=True)
    next_of_kin = models.CharField(null=True, blank=True, max_length=50)
    marital_status =models.CharField(choices=MARITAL_STATUS, max_length=50)
    spouse_name = models.CharField(max_length=500, null=True, blank=True, default=None)
    spouse_phone = PhoneNumberField(blank=True, null=True)
    post = models.CharField(choices=POSTS, default=None, max_length=50)
    class_name = models.CharField(max_length=50, choices= CLASSES, default=None)
    profile_image = models.ImageField(max_length=255, upload_to=get_profile_image_filepath, blank=True, default=get_default_profile_image)
    emp_year = models.IntegerField(default=timezone.now().today().year, verbose_name="employment year")
    emp_date = models.DateField(default=timezone.now, verbose_name="employment date")
    staff_id = models.CharField(verbose_name="staff_id", unique=True, max_length=50, blank=True, null=True)
    is_idd = models.BooleanField(default=False, editable=False)

    
    def __str__(self):
        if self.last_name:
            return "{} {} {}".format(self.last_name, self.first_name, self.other_name)
        return "{} {}".format(self.last_name, self.first_name)

    

    def set_staff_id(self, count:int):
        if self.is_idd:
            pass
        else:
            l_i = list(self.last_name)[0].upper()
            f_i = list(self.first_name)[0].upper()
            year = str(timezone.now().today().year)
            number = str(count)
            zeros = '0' * (3 - len(number))
            number = zeros + number
            if number == '000':
                number = '001'
            year = "".join(list(year)[2:4])
            self.staff_id = 'EPSF/{}/{}{}{}'.format(number, l_i, f_i, year)
            self.is_idd = True

    def set_age(self):
        dob = self.dob
        today = date.today()
        age_in_months = (today.year - dob.year) * 12 - (today.month - dob.month)
        age = math.floor(age_in_months/12)
        self.age = age

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.profile_image.path)
            if img.width > 400 or img.height > 400:
                output_size =(400, 400)
                img.thumbnail(output_size)
                img.save(self.profile_image.path)
        except ValueError:
            pass
        except FileNotFoundError:
            pass
        except OSError:
            pass
        except AttributeError:
            pass
        except Exception as e:
            print(e)
            pass
        return super().save(*args, **kwargs)



