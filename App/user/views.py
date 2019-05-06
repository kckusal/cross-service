from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.core import serializers
import json
from itertools import chain
from django.urls import reverse

from django.contrib import auth, messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_protect
from django.db import transaction
import datetime

from .models import *
from service.models import *

from django.conf import settings
secret_key = settings.SECRET_KEY

# Create your views here.

@csrf_protect
def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('service:index'))

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth_login(request, user)
                
                messages.success(request, "Welcome " + request.user.first_name + '!', extra_tags='message-head info')
                messages.success(request, "You've been successfully logged into the system. You may now use the facilities available to your user account.", extra_tags="message-body")

                notification = Notification()
                notification.owner = user
                notification.created_datetime = datetime.datetime.now()
                notification.text = "You recently logged in! " 
                notification.save()

                return HttpResponseRedirect(reverse('service:index'))
            else:
                messages.error(request, "Unable to login!", extra_tags='message-head')
                messages.error(request, 'Hello ' + request.user.first_name + "! Your account has been marked inactive. Please consult an administrator to make it active again!", extra_tags="message-body")
                return HttpResponseRedirect(reverse('user:login'))

        else:
            messages.error(request, "Login failed!", extra_tags='message-head')
            messages.error(request, "Incorrect credentials: your email/password does not match with any record in our system. Try again!", extra_tags="message-body")
            return HttpResponseRedirect(reverse('user:login'))

    else:
        return render(request, 'user/login.html', {
            'navigation': 'login',
        })


@login_required
def logout(request):
    auth_logout(request)
    return render(request, 'user/logged_out.html', {
        'navigation': ''
    })

@transaction.atomic
@csrf_protect
def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('service:index'))
        
    if request.method == 'POST':
        form_data = request.POST
        
        user, created = User.objects.get_or_create(
            username= form_data['username'],
            defaults= {
                'email': form_data['username'],
                'first_name': form_data['first_name'],
                'last_name': form_data['last_name'],
            },
        )

        if created:
            # Set password first
            user.set_password(form_data['password'])
            user.save()

            # Create profile too
            user_profile = Profile(
                user = user,
                bio = form_data['bio'],
                phone = form_data['phone'],
                address = form_data['address'],
                available = (form_data['available'] == '1')
            )
            user_profile.save()

            notification = Notification()
            notification.owner = request.user
            notification.created_datetime = datetime.datetime.now()
            notification.text = "You created new user profile information!"
            notification.target_url = ""
            notification.save()

            messages.success(request, "Account successfully created!", extra_tags='message-head')
            messages.success(request, 'Hey ' + form_data['first_name'] + '! We have successfully created a user account based on the information you provided. Please login to use our services!', extra_tags="message-body")
            return HttpResponseRedirect(reverse('user:login'))

        else:
            messages.error(request, "Failed to Register!", extra_tags='message-head')
            messages.error(request, 'A user already exists with the provided email address. You can only register one account with an email.', extra_tags="message-body")
            
            return HttpResponseRedirect(reverse('user:register'))
            
    else:
        return render(request, 'user/register.html', {
            'navigation': 'register'
        })

@login_required
def activity(request):
    try:
        owner_user = User.objects.get(id=request.user.id)
        posts = ServicePost.objects.filter(owner=owner_user).order_by('-created_datetime')
    except ServicePost.DoesNotExist:
        posts = []
    
    
    return render(request, 'user/profile.html', context={
        'navigation': 'profile',
        'posts': posts,
        'unread_notifications_count': Notification.objects.filter(is_read=False,owner=request.user).count()
    })

@login_required
def info(request):
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        raise Http404('User does not exist')

    return render(request, 'user/profile.html', context={
        'user': user,
        'navigation': 'profile',
        'unread_notifications_count': Notification.objects.filter(is_read=False,owner=request.user).count()
    })

def model_to_dict(instance, fields=None, exclude=None):
    """
    Return a dict containing the data in ``instance`` suitable for passing as
    a Form's ``initial`` keyword argument.
    ``fields`` is an optional list of field names. If provided, return only the
    named.
    ``exclude`` is an optional list of field names. If provided, exclude the
    named from the returned dict, even if they are listed in the ``fields``
    argument.
    """
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if not getattr(f, 'editable', False):
            continue
        if fields is not None and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        data[f.name] = f.value_from_object(instance)
    return data


@login_required
def data(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user_data = {
            'user': model_to_dict(user),
            'profile': model_to_dict(user.profile)
        }

        if (request.user.id != user.id):
            notification = Notification()
            notification.owner = user
            notification.created_datetime = datetime.datetime.now()
            notification.text = request.user.first_name + " "+ request.user.last_name + " viewed your profile information!"
            notification.target_url = ""
            notification.save()
        
        return JsonResponse({
            'data': user_data
        }, status=200)
    except User.DoesNotExist:
        return JsonResponse({
            'message':'User does not exist!'
        }, status=500)



@login_required
def update(request):
    try:
        user = User.objects.get(id = request.user.id)
    except:
        raise Http404("User Profile with given id doesn't exist!")

    if request.method == 'GET':
        return render(request, 'user/profile.html', context={
            'user': user,
            'navigation': 'profile',
            'unread_notifications_count': Notification.objects.filter(is_read=False,owner=request.user).count()
        })

    else:
        update_data = request.POST
        require_login_later = False

        if (request.user.username != update_data['username']):
            # if new username/email set, check if already exists
            try:
                exists_user = User.objects.get(username = update_data['username'])
            except User.DoesNotExist:
                exists_user = None

            if exists_user != None:
                messages.error(request, 'Update failed!', extra_tags='message-head')
                messages.error(request, 'There is already another user in our system with the new email you provided. Unfortunately, only one account can be associated with an email! Please re-update your fields with valid email.', extra_tags='message-body')

                return HttpResponseRedirect(reverse('user:update'))
            else:
                user.username = update_data['username']
                user.email = update_data['username']
                require_login_later = True
        
        if update_data['password'] != '':
            user.set_password(update_data['password'])
            user.save()
            require_login_later = True

        user.first_name = update_data['first_name']
        user.last_name = update_data['last_name']
        user.save()

        user.profile.bio = update_data['bio']
        user.profile.phone = update_data['phone']
        user.profile.address = update_data['address']
        user.profile.available = (update_data['available'] == '1')
        user.profile.save()
        user.save()

        notification = Notification()
        notification.owner = request.user
        notification.created_datetime = datetime.datetime.now()
        notification.text = "You updated your profile information!"
        notification.target_url = ""
        notification.save()

        messages.success(request, 'Profile Updated!', extra_tags='message-head info')

        success_msg = 'Your profile has been successfully updated with the new provided data!'
        if require_login_later:
            success_msg += " You've been logged out of the system. Since you changed your email/password, you will have to log in again using your new credentials."

        messages.success(request, success_msg, extra_tags='message-body ')

        if require_login_later:
            return HttpResponseRedirect(reverse('user:logout'))

        return HttpResponseRedirect(reverse('user:update'))


@login_required
def delete(request):
    deleted = False
    err_msg = ''

    if request.user.is_superuser:
        err_msg = 'This is a superuser account! The system must have a superuser to manage other users and itself. You can delete this account only after you update it to be a normal user account.'
    else:
        try:
            user = User.objects.get(id = request.user.id)
            user.delete()
            deleted = True
        except User.DoesNotExist:
            err_msg = 'The user does not exist!'
        except Exception as e: 
            err_msg = e.message
    
    if deleted:
        messages.success(request, "Account Deleted Successfully!", extra_tags='message-head')
        messages.success(request, 'Your user account have been deleted from our system. You will need to create a new account, should you wish to use our services again!', extra_tags="message-body")

        return HttpResponseRedirect(reverse('user:login'))

    else:
        messages.error(request, "Cannot delete account!", extra_tags='message-head')
        messages.warning(request, err_msg, extra_tags="message-body")
    
        return HttpResponseRedirect(reverse('settings'))
