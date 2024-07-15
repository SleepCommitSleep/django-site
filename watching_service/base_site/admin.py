from django.contrib import admin

# Register your models here.
from .models import Film
from .models import Video


class FilmAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "genres", "description", "release_date")


admin.site.register(Video)
admin.site.register(Film, FilmAdmin)
