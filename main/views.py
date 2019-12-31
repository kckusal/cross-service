from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404

from django.urls import reverse
from django.contrib import auth, messages

from service.models import Notification

@login_required
def settings(request):
    return render(request, 'main/settings.html', context={
        'navigation': 'settings',
        'unread_notifications_count': Notification.objects.filter(is_read=False,owner=request.user).count()
    })

@login_required
def get_notifications(request):
    
    try:
        notifications = Notification.objects.filter(
            owner=request.user
        ).order_by('-created_datetime')
    except Notification.DoesNotExist:
        notifications = []

    return render(request, 'main/notifications.html', context={
        'navigation': 'notifications',
        'unread_notifications_count': Notification.objects.filter(is_read=False,owner=request.user).count(),
        'notifications': notifications,
    })


@login_required
def mark_notification_read(request, notif_id):
    try:
        notification = Notification.objects.filter(
            pk=notif_id
        )
    except Notification.DoesNotExist:
        raise Http404('Notification does not exist!')
    
    notification.is_read = True
    notification.save()

    messages.success(request, "Notification marked read!" , extra_tags='message-head info')
    messages.success(request, "You've successfully marked a notification as read.", extra_tags="message-body")

    return HttpResponseRedirect(reverse('notifications'))


@login_required
def markall_notification_read(request):
    try:
        unread = Notification.objects.filter(
            is_read=False
        )
    except Notification.DoesNotExist:
        raise Http404('Notification does not exist!')
    
    for notification in unread:
        notification.is_read = True
        notification.save()
    
    messages.success(request, "All unread notifications marked read!" , extra_tags='message-head info')
    messages.success(request, "You've successfully marked all unread notifications as read.", extra_tags="message-body")

    return HttpResponseRedirect(reverse('notifications'))

    