from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Profile


def render_photo(obj):
    if obj.photo:
        img_html = '<img src="{url}" width="{width}" height="{height}" />' \
            .format(url=obj.photo.url,
                    width=64,
                    height=64
                    )
        return mark_safe(img_html)
    return None


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [render_photo, 'user', 'date_of_birth']
    raw_id_fields = ['user']
