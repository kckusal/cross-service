from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse

from django.contrib import messages
import datetime

from django.db.models import Q
from .models import *


@login_required
def index(request):
    service_posts = ServicePost.objects.filter().order_by('-created_datetime')[:10]
    
    return render(request, 'service/index.html', {
        'navigation': 'service',
        'service_posts': service_posts,
        'unread_notifications_count': Notification.objects.filter(is_read=False,owner=request.user).count()
    })


@login_required
def explore(request):
    service_posts = ServicePost.objects.filter().order_by('-created_datetime')
    return render(request, 'service/explore.html', {
        'navigation': 'service',
        'service_posts': service_posts,
        'unread_notifications_count': Notification.objects.filter(is_read=False,owner=request.user).count()
    })        


@login_required
def search(request):
    
    if request.method == 'GET':
        search_text = request.GET.get('service_search_text')

        title_matches = ServicePost.objects.filter(
            Q(title__icontains=search_text) | Q(service__name__icontains=search_text)
        )

        description_matches = ServicePost.objects.filter(
            Q(description__icontains=search_text) | Q(service__info__icontains=search_text)
        )

        location_matches = ServicePost.objects.filter(
            Q(service__location__icontains=search_text)
        )

        tag_matches = ServicePost.objects.filter(
            
        ).filter(service__tags__label__icontains=search_text)
         

    return render(request, 'service/search.html', {
        'search_text': search_text,
        'navigation': 'service',
        'title_matches': title_matches,
        'description_matches': description_matches,
        'location_matches': location_matches,
        'tag_matches': tag_matches,
        'unread_notifications_count': Notification.objects.filter(is_read=False,owner=request.user).count()
    })


@login_required
def create(request):
    if request.method == 'POST':
        # Creating new service and saving it
        new_service = Service()
        new_service.name = request.POST.get('service-name')
        new_service.info = request.POST.get('service-description')
        new_service.start_datetime = request.POST.get('service-start-datetime')
        new_service.end_datetime = request.POST.get('service-end-datetime')
        new_service.location = request.POST.get('service-location')
        
        new_service.save() 
        tags = request.POST.getlist('service-tags')
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(
                label = tag_name
            )
            
            new_service.tags.add(tag)
        
        new_service.save()

        # Creating new service post record and saving it
        new_post = ServicePost()
        new_post.title = request.POST.get('post-title')
        new_post.description= request.POST.get('post-description')
        new_post.is_request_post = (request.POST['is_request_post'] == '1')
        new_post.owner = User.objects.get(username=request.user.username)
        new_post.created_datetime = datetime.datetime.now()
        new_post.service = new_service
        
        new_post.save()

        notification = Notification()
        notification.owner = request.user
        notification.created_datetime = datetime.datetime.now()
        notification.text = "You created a new service post titled '" + request.POST.get('post-title') + "'"
        notification.target_url = ""
        notification.save()

        messages.success(request, "Post Published!", extra_tags='message-head')
        
        messages.success(request, 'Hey ' + request.user.first_name + '! We have recorded and published your post!', extra_tags="message-body")
        
        return HttpResponseRedirect(reverse('service:create'))
    
    return render(request, 'service/create.html', {
        'navigation': 'service',
        'unread_notifications_count': Notification.objects.filter(is_read=False,owner=request.user).count()
    })
    
@login_required
def detail(request, post_id):
    try:
        post = ServicePost.objects.get(pk=post_id)
        comments = ServicePostComment.objects.filter(post=post).order_by('-created_datetime')

    except ServicePost.DoesNotExist:
        raise Http404('Post does not exist')
    
    return render(request, 'service/details.html', {
        'navigation': 'service',
        'post': post,
        'comments': comments,
        'unread_notifications_count': Notification.objects.filter(is_read=False,owner=request.user).count()
    })


@login_required
def update(request, post_id):
    try:
        post = ServicePost.objects.get(pk=post_id)
    except ServicePost.DoesNotExist:
        raise Http404('Post does not exist')
    
    if request.method == 'POST':
        
        post.service.name = request.POST.get('service-name')
        post.service.info = request.POST.get('service-description')
        post.service.start_datetime = request.POST.get('service-start-datetime')
        post.service.end_datetime = request.POST.get('service-end-datetime')
        post.service.location = request.POST.get('service-location')
        
        post.service.save()
        post.save()

        post.service.tags.clear()
        tags = request.POST.getlist('service-tags')
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(
                label = tag_name
            )
            
            post.service.tags.add(tag)
        
        post.service.save()
        post.save()

        post.title = request.POST.get('post-title')
        post.description= request.POST.get('post-description')
        post.is_request_post = (request.POST['is_request_post'] == '1')
        post.modified_datetime = datetime.datetime.now()
        
        post.save()

        notification = Notification()
        notification.owner = request.user
        notification.created_datetime = datetime.datetime.now()
        notification.text = "You updated your service post information. The post is titled '" + request.POST.get('post-title') + "'"
        notification.target_url = ""
        notification.save()

        messages.success(request, "Post Updated!", extra_tags='message-head')
        
        messages.success(request, 'Hey ' + request.user.first_name + '! We have updated your post!', extra_tags="message-body")
        
        return HttpResponseRedirect(reverse('service:update', kwargs={'post_id': post.id})) 
    
    return render(request, 'service/update.html', {
        'navigation': 'service',
        'post': post,
        'unread_notifications_count': Notification.objects.filter(is_read=False,owner=request.user).count()
    })

@login_required
def close(request, post_id):
    try:
        post = ServicePost.objects.get(pk=post_id)
    except ServicePost.DoesNotExist:
        raise Http404('Post does not exist')
    
    if request.user != post.owner:
        messages.warning(request, "Unauthorized Attempt", extra_tags='message-head')
        messages.warning(request, "You're not authorized to perform this operation. Only the post owner can close the post.", extra_tags='message-body')

    else:
        post.closed_datetime = datetime.datetime.now()
        post.save()

        notification = Notification()
        notification.owner = request.user
        notification.created_datetime = datetime.datetime.now()
        notification.text = "You recently closed a service post titled '" + post.title + "'"
        notification.target_url = ""
        notification.save()

        messages.success(request, "Post closed", extra_tags='message-head info')
        messages.warning(request, "You've recently closed a service post. You will no require receive comments in that post, although the post is still visible unless you delete it!", extra_tags='message-body')

    return HttpResponseRedirect(reverse('service:detail', kwargs={'post_id': post.id}))


@login_required
def delete(request, post_id):
    try:
        post = ServicePost.objects.get(pk=post_id)
    except ServicePost.DoesNotExist:
        raise Http404('Post does not exist')
    
    if request.user != post.owner:
        messages.warning(request, "Unauthorized Attempt", extra_tags='message-head error')
        messages.warning(request, "You're not authorized to perform this operation. Only the post owner can delete the post.", extra_tags='message-body')

    else:
        post.service.delete()
        post.delete()

        notification = Notification()
        notification.owner = request.user
        notification.created_datetime = datetime.datetime.now()
        notification.text = "You deleted your service post titled '" + post.title + "'"
        notification.target_url = ""
        notification.save()

        messages.success(request, "Post Deleted", extra_tags='message-head info')
        messages.warning(request, "You've successfully deleted a service post. You will no longer be able to access the post!", extra_tags='message-body')

    return HttpResponseRedirect(reverse('service:index'))


@login_required
def create_comment(request, post_id):
    try:
        post = ServicePost.objects.get(pk=post_id)
    except ServicePost.DoesNotExist:
        raise Http404('Post does not exist')
    
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        
        new_comment = ServicePostComment()
        new_comment.text = comment_text
        new_comment.created_datetime = datetime.datetime.now()

        new_comment.owner = request.user
        new_comment.post = post

        new_comment.is_private = False
        if request.POST.get('is-private'):
            new_comment.is_private = True
        
        new_comment.save()

        notification = Notification()
        notification.owner = post.owner
        notification.created_datetime = datetime.datetime.now()
        notification.text = request.user.first_name + " " + request.user.last_name + " commented in your service post!"
        notification.target_url = ""
        notification.save()

        messages.success(request, "New Comment Added!", extra_tags='message-head info')
        messages.warning(request, "Your comment has been added to the post!", extra_tags='message-body')

    return HttpResponseRedirect(reverse('service:detail', kwargs={ 'post_id': post.id }))

