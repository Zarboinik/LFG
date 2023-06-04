from django.contrib import admin

from .models import *


class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'time_create', 'text', 'content')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'text')
    list_filter = ('time_create', 'category')
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Announcement, AnnouncementAdmin)
