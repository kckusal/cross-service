from django.contrib import admin

from .models import *

# Register your models here.
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass

@admin.register(ServicePost)
class ServicePostAdmin(admin.ModelAdmin):
    pass

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass

@admin.register(ServicePostComment)
class ServicePostCommentAdmin(admin.ModelAdmin):
    pass