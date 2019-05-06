
from django.contrib import admin
from django.urls import path, include

from django.views.generic import RedirectView
from . import views

app_name = 'main'
urlpatterns = [
    #path('', views.index, name='index'),
    path('', RedirectView.as_view(url='/service/', permanent=True), name="index"),
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('service/', include('service.urls')),
    path('settings/', views.settings, name='settings'),
    path('notifications/', views.get_notifications, name='notifications'),
    path('notifications/<int:notif_id>/read', views.mark_notification_read, name='read-notification'), 
    path('notifications/all/read', views.markall_notification_read, name='read-notification-all'),
] 
