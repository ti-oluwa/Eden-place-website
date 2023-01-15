from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
# from .forms import UserRegistrationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Student, Staff, CustomUser
from django.contrib.auth.decorators import user_passes_test, login_required
import json


def update_ages():
    students = Student.objects.all()
    for student in students:
        student.set_age()
        student.save()
    staffs = Staff.objects.all()
    for staff in staffs:
        staff.set_age()
        staff.save()
    return None

def validate(request):
    is_ajax = request.headers.get('X-Requested-With') == "XMLHttpRequest"
    form_data = json.load(request)
    response = {"message": ""}
    if is_ajax:
        user_id = form_data["user_id"]
        password = form_data["password"]

        #check if  user entered full name or id
        sl = [i for i in list(user_id) if i in ["/", "E", "P"]]
        if len(sl) < 4 :
            user_exists = CustomUser.objects.filter(username__iexact=user_id)
        else:
            user_exists = CustomUser.objects.filter(user_id=user_id)

        #check if user exists 
        if user_exists:
            user = authenticate(request, username=user_exists[0].user_id, password=password)
            #check if password is correct
            if user is not None:
                if user.is_student or user.is_staff or user.is_admin:
                    response["message"] = "valid"
                    return JsonResponse(response, status=200)

                response["message"] = "You're not allowed to login"
                response["field"] = "user"
                return JsonResponse(response, status=403)

            else:
                response["field"] = "pass"
                response["message"] = "Incorrect password! Enter a valid password"
                return JsonResponse(response)

        response["field"] = "user"
        response["message"] = "User not found. If you entered your name, including your middle name might help"
        return JsonResponse(response)

    else:
        response["message"] = "Forbidden request"
        return JsonResponse(response, status=403)



def auth(request, *args, **kwargs):
    if request.method == "POST":
        user_id = request.POST["user_id"]
        password = request.POST["password"]
        sl = [i for i in list(user_id) if i in ["/", "E", "P"]]
        if len(sl) < 4 :
            return authenticate_by_name(request, user_id, password, kwargs)
        user = authenticate(request, user_id, password, kwargs)
        if user is not None:
            if user.is_student or user.is_staff or user.is_admin:
                login(request, user)
                update_ages()
                messages.success(request, "LOGGED IN")
                if kwargs.get('next'):
                    return redirect(kwargs.get('next'))
                return redirect('home')

        messages.error(request, "USER NOT FOUND!")
        return redirect('login')

    else:
        return render(request,'users/login.html')


def authenticate_by_name(request, username, password, kwargs):
    username = list(username)
    if username[-1] == ' ':
        username.pop()
    username = "".join(username)
    user = CustomUser.objects.filter(username__iexact=username)
    if user:
        user_id = user[0].user_id
    else:
        messages.error(request, "USER NOT FOUND!")
        return redirect('login')
    user = authenticate(request, username=user_id, password=password)
    if user is not None:
        if user.is_student or user.is_staff or user.is_admin:
            login(request, user)
            update_ages()
            messages.success(request, "LOGGED IN")
            if kwargs.get('next'):
                    return redirect(kwargs.get('next'))
            return redirect('home')

        messages.error(request, "YOU'RE NOT ALLOWED TO LOGIN!")
        return redirect('login')

    else:
        messages.error(request, "LOGIN FAILED\n Enter a valid password\n If you are sure of your password, including your other name might help")
        return redirect('login')

@login_required
def un_auth(request, *args, **kwargs):
    logout(request)
    return redirect('home')